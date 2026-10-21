from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ESTADOS_SIN_POSICION = {"NC", "DQ"}

ESQUEMAS = {
    "f1_2025_drivers_standings.csv": {
        "columnas": ("position", "driver", "nationality", "team", "points"),
        "columnas_texto": ("driver", "nationality", "team"),
        "columnas_enteras": ("position", "points"),
        "columnas_positivas": ("position",),
        "clave_unica": ("driver",),
    },
    "f1_2025_race_results.csv": {
        "columnas": (
            "race",
            "position",
            "driver_number",
            "driver",
            "team",
            "laps",
            "time",
            "points",
        ),
        "columnas_texto": ("race", "position", "driver", "team", "time"),
        "columnas_enteras": ("driver_number", "points"),
        "columnas_positivas": ("driver_number",),
        "clave_unica": ("race", "driver_number"),
    },
    "f1_2025_teams_standings.csv": {
        "columnas": ("position", "team", "points"),
        "columnas_texto": ("team",),
        "columnas_enteras": ("position", "points"),
        "columnas_positivas": ("position",),
        "clave_unica": ("team",),
    },
}


def validar_archivo(ruta_csv: Path, datos: pd.DataFrame) -> None:
    """Valida las columnas y los valores requeridos de los CSV del proyecto."""
    esquema = ESQUEMAS.get(ruta_csv.name)
    if esquema is None:
        raise ValueError(f"Archivo CSV no esperado: {ruta_csv.name}")
    if datos.empty:
        raise ValueError(f"El archivo no contiene registros: {ruta_csv.name}")

    columnas_esperadas = esquema["columnas"]
    columnas_faltantes = set(columnas_esperadas).difference(datos.columns)
    if columnas_faltantes:
        faltantes = ", ".join(sorted(columnas_faltantes))
        raise ValueError(
            f"Faltan columnas en {ruta_csv.name}: {faltantes}"
        )

    for columna in columnas_esperadas:
        if columna == "laps" and ruta_csv.name == "f1_2025_race_results.csv":
            continue
        if datos[columna].isna().any():
            raise ValueError(
                f"Hay valores vacíos en {columna} de {ruta_csv.name}"
            )

    for columna in esquema["columnas_texto"]:
        valores = datos[columna].astype("string").str.strip()
        if valores.eq("").any():
            raise ValueError(
                f"Hay valores vacíos en {columna} de {ruta_csv.name}"
            )

    for columna in esquema["columnas_enteras"]:
        valores = pd.to_numeric(datos[columna], errors="coerce")
        if valores.isna().any() or valores.lt(0).any():
            raise ValueError(
                f"La columna {columna} debe contener enteros no negativos "
                f"en {ruta_csv.name}"
            )
        if columna in esquema["columnas_positivas"] and valores.lt(1).any():
            raise ValueError(
                f"La columna {columna} debe contener enteros positivos "
                f"en {ruta_csv.name}"
            )
        if (valores % 1 != 0).any():
            raise ValueError(
                f"La columna {columna} debe contener enteros "
                f"en {ruta_csv.name}"
            )

    if ruta_csv.name == "f1_2025_race_results.csv":
        posiciones = datos["position"].astype("string").str.strip()
        posiciones_validas = posiciones.str.fullmatch(r"\d+|NC|DQ")
        if not posiciones_validas.all():
            raise ValueError(
                f"La columna position debe contener posiciones numéricas "
                f"o estados {', '.join(sorted(ESTADOS_SIN_POSICION))} "
                f"en {ruta_csv.name}"
            )
        posiciones_numericas = pd.to_numeric(
            posiciones[~posiciones.isin(ESTADOS_SIN_POSICION)],
            errors="coerce",
        )
        if posiciones_numericas.lt(1).any():
            raise ValueError(
                f"Las posiciones numéricas deben ser positivas "
                f"en {ruta_csv.name}"
            )
        vueltas = pd.to_numeric(datos["laps"], errors="coerce")
        vueltas_invalidas = datos["laps"].notna() & (
            vueltas.isna() | vueltas.lt(0) | (vueltas % 1 != 0)
        )
        if vueltas_invalidas.any():
            raise ValueError(
                f"La columna laps debe contener enteros no negativos "
                f"o valores vacíos en {ruta_csv.name}"
            )

    clave_unica = esquema["clave_unica"]
    if datos.duplicated(subset=list(clave_unica)).any():
        columnas_clave = ", ".join(clave_unica)
        raise ValueError(
            f"Hay registros duplicados según {columnas_clave} "
            f"en {ruta_csv.name}"
        )


def inspeccionar_archivos() -> None:
    """Valida los CSV del proyecto y muestra un resumen y sus primeras filas."""
    archivos_faltantes = [
        nombre for nombre in ESQUEMAS if not (DATA_DIR / nombre).is_file()
    ]
    if archivos_faltantes:
        faltantes = ", ".join(archivos_faltantes)
        raise FileNotFoundError(
            f"No se encontraron los archivos requeridos en {DATA_DIR}: {faltantes}"
        )

    conjuntos: dict[str, pd.DataFrame] = {}

    for nombre_archivo in ESQUEMAS:
        ruta_csv = DATA_DIR / nombre_archivo
        datos = pd.read_csv(ruta_csv)
        validar_archivo(ruta_csv, datos)
        conjuntos[ruta_csv.name] = datos

        print(f"\n{'=' * 80}")
        print(f"ARCHIVO: {ruta_csv.name}")
        print(f"Dimensiones: {datos.shape[0]} filas x {datos.shape[1]} columnas")

        print("\nInformación general:")
        datos.info()

        print("\nTipos de datos:")
        print(datos.dtypes.to_string())

        valores_nulos = datos.isna().sum()
        resumen_nulos = pd.DataFrame(
            {
                "valores_nulos": valores_nulos,
                "porcentaje_nulos": (valores_nulos / len(datos) * 100).round(2),
            }
        )
        print("\nValores nulos por columna:")
        print(resumen_nulos.to_string())

        print(f"\nFilas duplicadas: {datos.duplicated().sum()}")

    print(f"\n{'=' * 80}")
    print("PRIMERAS FILAS DE CADA ARCHIVO (head)")
    for nombre, datos in conjuntos.items():
        print(f"\n--- {nombre} ---")
        print(datos.head().to_string(index=False))


if __name__ == "__main__":
    inspeccionar_archivos()