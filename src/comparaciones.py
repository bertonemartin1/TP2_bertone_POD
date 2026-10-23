
import pandas as pd

from graficos import (
    graficar_evolucion_puntos_constructores,
    graficar_evolucion_puntos_piloto,
    graficar_evolucion_puntos_pilotos,
    graficar_puntos_constructores_carrera,
    graficar_puntos_pilotos_carrera,
)
from modelos import CampeonatoF1
from transformaciones import transformar_archivo


ARCHIVO_CARRERAS = "f1_2025_race_results.json"
ARCHIVO_CAMPEONATO_CONSTRUCTORES = "f1_2025_teams_standings.csv"
ARCHIVO_CAMPEONATO_PILOTOS = "f1_2025_drivers_standings.csv"


def _leer_csv_puntuaciones(
    nombre_archivo: str,
    columnas_requeridas: tuple[str, ...],
    *,
    conservar_driver: bool = False,
) -> pd.DataFrame:
    resultados = transformar_archivo(
        nombre_archivo,
        conservar_driver=conservar_driver,
    )
    columnas_faltantes = set(columnas_requeridas).difference(resultados.columns)
    if columnas_faltantes:
        faltantes = ", ".join(sorted(columnas_faltantes))
        raise ValueError(
            f"Faltan columnas requeridas en {nombre_archivo}: {faltantes}"
        )

    resultados = resultados.loc[:, columnas_requeridas].copy()
    for columna in columnas_requeridas:
        if columna == "points":
            continue
        resultados[columna] = resultados[columna].astype("string").str.strip()
        if resultados[columna].isna().any() or resultados[columna].eq("").any():
            raise ValueError(
                f"Hay valores vacíos en la columna {columna} "
                f"de {nombre_archivo}"
            )

    resultados["points"] = pd.to_numeric(resultados["points"], errors="coerce")
    if resultados["points"].isna().any() or resultados["points"].lt(0).any():
        raise ValueError(
            f"Hay puntos vacíos, no numéricos o negativos en {nombre_archivo}"
        )
    return resultados


def _filtrar_por_carrera(resultados: pd.DataFrame, carrera: str) -> pd.DataFrame:
    carrera_normalizada = carrera.strip().casefold()
    nombres_carreras = (
        resultados["race"]
        .dropna()
        .astype("string")
        .str.strip()
        .drop_duplicates()
        .tolist()
    )
    filtrados = resultados.loc[
        resultados["race"].astype("string").str.strip().str.casefold()
        == carrera_normalizada
    ].copy()
    if filtrados.empty:
        disponibles = ", ".join(nombres_carreras)
        raise ValueError(
            f"No se encontró la carrera '{carrera}'. "
            f"Carreras disponibles: {disponibles or 'ninguna'}"
        )
    return filtrados


def _buscar_nombre_disponible(
    nombre: str,
    nombres_disponibles: list[str],
    tipo: str,
    etiqueta_disponibles: str,
) -> str:
    nombres_por_clave = {
        nombre_disponible.casefold(): nombre_disponible
        for nombre_disponible in nombres_disponibles
    }
    nombre_encontrado = nombres_por_clave.get(nombre.strip().casefold())
    if nombre_encontrado is None:
        disponibles = ", ".join(nombres_disponibles)
        raise ValueError(
            f"No se encontró {tipo} '{nombre}'. "
            f"{etiqueta_disponibles} disponibles: {disponibles}"
        )
    return nombre_encontrado


def comparar_campeonato_constructores() -> pd.DataFrame:
    """Muestra la clasificación final del campeonato de constructores."""
    datos_clasificacion = _leer_csv_puntuaciones(
        ARCHIVO_CAMPEONATO_CONSTRUCTORES,
        ("position", "team", "points"),
    )
    resultados_carreras = _leer_csv_puntuaciones(
        ARCHIVO_CARRERAS,
        ("race", "position", "team", "points"),
    )
    campeonato = CampeonatoF1(
        "constructores",
        datos_clasificacion,
        resultados_carreras,
    )
    clasificacion = campeonato.obtener_clasificacion()
    puntos_acumulados = campeonato.calcular_puntos_acumulados()

    print("\nCampeonato de constructores:")
    print(clasificacion.to_string(index=False))

    graficar_evolucion_puntos_constructores(
        puntos_acumulados,
        clasificacion["team"].tolist(),
    )

    return clasificacion


def comparar_campeonato_pilotos() -> pd.DataFrame:
    """Muestra la clasificación final del campeonato de pilotos."""
    datos_clasificacion = _leer_csv_puntuaciones(
        ARCHIVO_CAMPEONATO_PILOTOS,
        ("position", "driver", "team", "points"),
    )
    resultados_carreras = _leer_csv_puntuaciones(
        ARCHIVO_CARRERAS,
        ("race", "position", "driver", "points"),
        conservar_driver=True,
    )
    if datos_clasificacion["driver"].duplicated().any():
        raise ValueError(
            "Los nombres de pilotos no son únicos después de eliminar el sufijo."
        )
    pilotos = datos_clasificacion["driver"].tolist()
    pilotos_en_resultados = set(resultados_carreras["driver"].unique())
    pilotos_sin_resultados = set(pilotos).difference(pilotos_en_resultados)
    if pilotos_sin_resultados:
        faltantes = ", ".join(sorted(pilotos_sin_resultados))
        raise ValueError(
            "No hay resultados de carrera para estos pilotos de la "
            f"clasificación: {faltantes}"
        )
    campeonato = CampeonatoF1(
        "pilotos",
        datos_clasificacion,
        resultados_carreras,
    )
    clasificacion = campeonato.obtener_clasificacion()
    pilotos = clasificacion["driver"].tolist()
    puntos_acumulados = campeonato.calcular_puntos_acumulados()

    print("\nCampeonato de pilotos:")
    print(clasificacion.to_string(index=False))

    graficar_evolucion_puntos_pilotos(puntos_acumulados, pilotos)

    return clasificacion


def comparar_constructores_por_carrera(carrera: str) -> pd.DataFrame:
    """Muestra los resultados de los constructores en una carrera."""
    datos = transformar_archivo(ARCHIVO_CARRERAS)
    datos = _filtrar_por_carrera(datos, carrera)

    datos["position_num"] = pd.to_numeric(datos["position"], errors="coerce")
    por_constructor = (
        datos.groupby("team", as_index=False)
        .agg(
            puntos=("points", "sum"),
            posicion_promedio=("position_num", "mean"),
        )
        .sort_values(["puntos", "posicion_promedio"], ascending=[False, True], kind="stable")
        .reset_index(drop=True)
    )

    sin_puntos = por_constructor[por_constructor["puntos"] == 0].copy()
    con_puntos = por_constructor[por_constructor["puntos"] > 0].copy()
    final = pd.concat(
        [
            con_puntos.sort_values(
                ["puntos", "posicion_promedio"],
                ascending=[False, True],
                kind="stable",
            ),
            sin_puntos.sort_values(
                ["posicion_promedio", "team"],
                ascending=[True, True],
                na_position="last",
                kind="stable",
            ),
        ],
        ignore_index=True,
    )
    final.index = range(1, len(final) + 1)
    final.index.name = "Posición"

    print(f"\nResultados de constructores en la carrera: {carrera}")
    vista_final = final.copy()
    vista_final["posicion_promedio"] = vista_final["posicion_promedio"].map(
        lambda posicion: (
            "Sin posición numérica" if pd.isna(posicion) else posicion
        )
    )
    print(vista_final.to_string())

    graficar_puntos_constructores_carrera(final, carrera)

    return final


def comparar_h2h_equipo(equipo: str) -> pd.DataFrame:
    """Compara carrera a carrera y en total a los pilotos de un equipo."""
    equipos_disponibles = obtener_equipos_disponibles()
    nombre_equipo = _buscar_nombre_disponible(
        equipo,
        equipos_disponibles,
        "el equipo",
        "Equipos",
    )
    equipo_ingresado = nombre_equipo.casefold()

    resultados = _leer_csv_puntuaciones(
        ARCHIVO_CARRERAS,
        ("race", "position", "driver", "team", "points"),
        conservar_driver=True,
    )
    resultados_equipo = resultados.loc[
        resultados["team"].str.casefold() == equipo_ingresado
    ].copy()
    if resultados_equipo.empty:
        raise ValueError(f"No hay resultados disponibles para {nombre_equipo}.")

    calendario = resultados["race"].drop_duplicates().tolist()
    pilotos = resultados_equipo["driver"].drop_duplicates().tolist()
    if resultados_equipo.duplicated(subset=["race", "driver"]).any():
        raise ValueError(
            f"Hay más de un resultado por carrera para un piloto de {nombre_equipo}."
        )

    resultados_equipo["position_numeric"] = pd.to_numeric(
        resultados_equipo["position"], errors="coerce"
    )
    indices = pd.MultiIndex.from_product(
        [calendario, pilotos],
        names=["Carrera", "Piloto"],
    )
    tabla = (
        resultados_equipo.set_index(["race", "driver"])[
            ["position", "points", "position_numeric"]
        ]
        .reindex(indices)
        .rename(
            columns={
                "position": "Posición",
                "points": "Puntos",
                "position_numeric": "Posición numérica",
            }
        )
    )
    tabla["Posición"] = tabla["Posición"].fillna("Sin participación")
    tabla["Puntos"] = tabla["Puntos"].fillna(0).astype(int)
    tabla = tabla.drop(columns="Posición numérica")

    resumen = (
        resultados_equipo.groupby("driver", sort=False)
        .agg(
            Puntos_totales=("points", "sum"),
            Posición_promedio=("position_numeric", "mean"),
        )
        .rename_axis("Piloto")
        .reset_index()
        .sort_values(
            ["Puntos_totales", "Posición_promedio", "Piloto"],
            ascending=[False, True, True],
            na_position="last",
            kind="stable",
        )
        .reset_index(drop=True)
    )
    resumen["Posición_promedio"] = resumen["Posición_promedio"].map(
        lambda posicion: (
            "Sin posición numérica" if pd.isna(posicion) else posicion
        )
    )

    print(f"\nComparación h2h para {nombre_equipo} (resultados de carreras):")
    print(tabla.to_string())
    print(f"\nResumen de {nombre_equipo}:")
    print(resumen.to_string(index=False))

    return tabla


def comparar_piloto_temporada(piloto: str) -> pd.DataFrame:
    """Muestra la evolución de un piloto durante la temporada."""
    clasificacion = _leer_csv_puntuaciones(
        ARCHIVO_CAMPEONATO_PILOTOS,
        ("driver", "team", "points"),
    )
    nombres = clasificacion["driver"].tolist()
    nombre_piloto = _buscar_nombre_disponible(
        piloto,
        nombres,
        "el piloto",
        "Pilotos",
    )

    resultados_temporada = _leer_csv_puntuaciones(
        ARCHIVO_CARRERAS,
        ("race", "position", "driver", "points"),
        conservar_driver=True,
    )
    calendario = resultados_temporada["race"].drop_duplicates().tolist()
    resultados_piloto = resultados_temporada.loc[
        resultados_temporada["driver"] == nombre_piloto
    ].copy()
    if resultados_piloto.empty:
        raise ValueError(
            f"No hay resultados de carrera para el piloto {nombre_piloto}."
        )

    posiciones_duplicadas = resultados_piloto["race"].duplicated()
    if posiciones_duplicadas.any():
        carreras_duplicadas = ", ".join(
            resultados_piloto.loc[posiciones_duplicadas, "race"].tolist()
        )
        raise ValueError(
            f"Hay más de un resultado para {nombre_piloto} en: "
            f"{carreras_duplicadas}"
        )

    resultados = resultados_piloto.set_index("race").reindex(calendario)
    tabla = resultados[["position", "points"]].rename(
        columns={"position": "Posición", "points": "Puntos"}
    )
    tabla.index.name = "Carrera"
    tabla["Posición"] = tabla["Posición"].fillna("Sin participación")
    tabla["Puntos"] = tabla["Puntos"].fillna(0).astype(int)

    print(f"\nEvolución de {nombre_piloto} durante la temporada:")
    print(tabla.to_string())

    puntos_acumulados = tabla["Puntos"].cumsum()
    graficar_evolucion_puntos_piloto(puntos_acumulados, nombre_piloto)

    return tabla


def comparar_pilotos_por_carrera(carrera: str) -> pd.DataFrame:
    """Muestra los resultados de los pilotos en una carrera."""
    resultados = _leer_csv_puntuaciones(
        ARCHIVO_CARRERAS,
        ("race", "position", "driver_number", "driver", "team", "points"),
        conservar_driver=True,
    )
    resultados = _filtrar_por_carrera(resultados, carrera)

    resultados["posicion_numerica"] = pd.to_numeric(
        resultados["position"], errors="coerce"
    )
    resultados["orden_original"] = range(len(resultados))
    resultados = resultados.sort_values(
        ["posicion_numerica", "orden_original"],
        ascending=True,
        na_position="last",
        kind="stable",
    ).reset_index(drop=True)

    tabla = resultados[
        ["position", "driver", "team", "points"]
    ].copy()
    tabla.index = range(1, len(tabla) + 1)
    tabla.index.name = "Posición"

    print(f"\nResultados de pilotos en la carrera: {carrera}")
    print(tabla.to_string())

    graficar_puntos_pilotos_carrera(tabla, carrera)

    return tabla


def obtener_carreras_disponibles() -> list[str]:
    """Devuelve las carreras disponibles en los resultados transformados."""
    resultados = transformar_archivo(ARCHIVO_CARRERAS)
    return resultados["race"].drop_duplicates().tolist()


def obtener_equipos_disponibles() -> list[str]:
    """Devuelve los nombres de equipos de la clasificación de constructores."""
    clasificacion = _leer_csv_puntuaciones(
        ARCHIVO_CAMPEONATO_CONSTRUCTORES,
        ("team", "points"),
    )
    equipos = clasificacion["team"].drop_duplicates().tolist()
    if not equipos:
        raise ValueError("No hay equipos disponibles en la clasificación.")
    return equipos


def obtener_nombres_pilotos() -> list[str]:
    """Devuelve los nombres limpios de los pilotos en el campeonato."""
    clasificacion = _leer_csv_puntuaciones(
        ARCHIVO_CAMPEONATO_PILOTOS,
        ("driver", "points"),
    )
    nombres = clasificacion["driver"].drop_duplicates().tolist()
    if not nombres:
        raise ValueError("No hay pilotos disponibles en la clasificación.")
    return nombres
