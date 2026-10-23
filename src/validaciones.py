"""Validación estructural y por registro de los datos de temporada."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ESTADOS_SIN_POSICION = {"NC", "DQ"}

ESQUEMAS = {
    "f1_2025_drivers_standings": {
        "columnas": ("position", "driver", "nationality", "team", "points"),
        "columnas_texto": ("driver", "nationality", "team"),
        "columnas_enteras": ("position", "points"),
        "columnas_positivas": ("position",),
        "clave_unica": ("driver",),
    },
    "f1_2025_race_results": {
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
    "f1_2025_teams_standings": {
        "columnas": ("position", "team", "points"),
        "columnas_texto": ("team",),
        "columnas_enteras": ("position", "points"),
        "columnas_positivas": ("position",),
        "clave_unica": ("team",),
    },
}


@dataclass
class ResultadoValidacion:
    """Datos utilizables y detalle de los registros rechazados."""

    datos_validos: pd.DataFrame
    rechazos: pd.DataFrame


class DatosSinRegistrosValidosError(ValueError):
    """Indica que el conjunto no contiene ningún registro válido para analizar."""

    def __init__(self, nombre_archivo: str, rechazos: pd.DataFrame) -> None:
        self.nombre_archivo = nombre_archivo
        self.rechazos = rechazos.copy(deep=True)
        detalle = rechazos.to_string(index=False)
        super().__init__(
            f"No quedan registros válidos en {nombre_archivo}. "
            f"Filas rechazadas ({len(rechazos)}):\n{detalle}"
        )


def validar_archivo(
    ruta_archivo: str | Path,
    datos: pd.DataFrame,
) -> ResultadoValidacion:
    """Separa registros válidos de filas inválidas según el esquema del archivo.

    La falta de esquema, columnas o registros es un error estructural y bloquea
    la operación. Los errores localizados se devuelven por fila para que esas
    filas puedan excluirse sin descartar las restantes.
    """
    ruta = Path(ruta_archivo)
    if ruta.suffix.casefold() not in {".csv", ".json"}:
        raise ValueError(
            f"Formato de archivo no soportado: {ruta.suffix or 'sin extensión'}."
        )
    esquema = ESQUEMAS.get(ruta.stem)
    if esquema is None:
        raise ValueError(f"Archivo de datos no esperado: {ruta.name}")
    if datos.empty:
        raise ValueError(f"El archivo no contiene registros: {ruta.name}")

    columnas_faltantes = set(esquema["columnas"]).difference(datos.columns)
    if columnas_faltantes:
        faltantes = ", ".join(sorted(columnas_faltantes))
        raise ValueError(f"Faltan columnas en {ruta.name}: {faltantes}")

    datos_copia = datos.loc[:, esquema["columnas"]].copy(deep=True)
    errores_por_fila: dict[int, list[str]] = {
        posicion: [] for posicion in range(len(datos_copia))
    }

    for columna in esquema["columnas"]:
        if columna == "laps" and ruta.stem == "f1_2025_race_results":
            continue
        for posicion, faltante in enumerate(datos_copia[columna].isna().tolist()):
            if faltante:
                errores_por_fila[posicion].append(f"{columna}: valor nulo")

    for columna in esquema["columnas_texto"]:
        valores = datos_copia[columna].astype("string").str.strip()
        vacios = valores.eq("").fillna(False)
        for posicion in range(len(datos_copia)):
            if vacios.iloc[posicion]:
                errores_por_fila[posicion].append(
                    f"{columna}: valor vacío"
                )
        datos_copia[columna] = valores
        if columna == "driver":
            nombres_demasiado_cortos = valores.str.len().le(3).fillna(False)
            for posicion, invalido in enumerate(
                nombres_demasiado_cortos.tolist()
            ):
                if invalido:
                    errores_por_fila[posicion].append(
                        "driver: debe tener más de tres caracteres"
                    )

    for columna in esquema["columnas_enteras"]:
        valores = pd.to_numeric(datos_copia[columna], errors="coerce")
        for posicion, valor in enumerate(valores.tolist()):
            if pd.isna(valor):
                errores_por_fila[posicion].append(
                    f"{columna}: debe ser un entero no negativo"
                )
            elif valor < 0:
                errores_por_fila[posicion].append(
                    f"{columna}: no puede ser negativo"
                )
            elif valor % 1 != 0:
                errores_por_fila[posicion].append(
                    f"{columna}: debe ser un número entero"
                )
            elif (
                columna in esquema["columnas_positivas"]
                and valor < 1
            ):
                errores_por_fila[posicion].append(
                    f"{columna}: debe ser positivo"
                )

    if ruta.stem == "f1_2025_race_results":
        posiciones = datos_copia["position"].astype("string").str.strip()
        posiciones_validas = posiciones.str.fullmatch(r"\d+|NC|DQ").fillna(False)
        for posicion, valor in enumerate(posiciones.tolist()):
            if not posiciones_validas.iloc[posicion]:
                errores_por_fila[posicion].append(
                    "position: debe contener dígitos enteros o NC/DQ"
                )
            elif valor not in ESTADOS_SIN_POSICION:
                numero = pd.to_numeric(valor, errors="coerce")
                if pd.isna(numero) or numero < 1:
                    errores_por_fila[posicion].append(
                        "position: las posiciones numéricas deben ser positivas"
                    )

        vueltas = pd.to_numeric(datos_copia["laps"], errors="coerce")
        for posicion, valor_original in enumerate(datos_copia["laps"].tolist()):
            if pd.isna(valor_original):
                continue
            valor = vueltas.iloc[posicion]
            if pd.isna(valor) or valor < 0 or valor % 1 != 0:
                errores_por_fila[posicion].append(
                    "laps: debe ser un entero no negativo o estar vacío"
                )

    validas_antes_de_unicidad = [
        posicion
        for posicion, errores in errores_por_fila.items()
        if not errores
    ]
    vistos: set[tuple[object, ...]] = set()
    for posicion in validas_antes_de_unicidad:
        clave = tuple(
            datos_copia.iloc[posicion][columna]
            for columna in esquema["clave_unica"]
        )
        if clave in vistos:
            etiqueta = ", ".join(esquema["clave_unica"])
            errores_por_fila[posicion].append(
                f"{etiqueta}: clave duplicada (se conserva la primera fila válida)"
            )
        else:
            vistos.add(clave)

    filas_rechazadas = [
        {
            "fila": posicion + 1,
            "motivo": "; ".join(errores),
        }
        for posicion, errores in errores_por_fila.items()
        if errores
    ]
    tabla_rechazos = pd.DataFrame(
        filas_rechazadas,
        columns=["fila", "motivo"],
    )
    posiciones_validas = [
        posicion
        for posicion, errores in errores_por_fila.items()
        if not errores
    ]
    datos_validos = datos_copia.iloc[posiciones_validas].reset_index(drop=True)
    return ResultadoValidacion(datos_validos, tabla_rechazos)


def informar_rechazos(nombre_archivo: str, rechazos: pd.DataFrame) -> None:
    """Muestra las filas excluidas y sus motivos en la consola."""
    if rechazos.empty:
        return
    print(
        f"\nValidación de {nombre_archivo}: "
        f"se excluyeron {len(rechazos)} fila(s)."
    )
    print(rechazos.to_string(index=False))


def inspeccionar_archivos() -> None:
    """Valida los CSV locales e informa registros válidos y rechazados."""
    for nombre_archivo in ESQUEMAS:
        ruta_csv = DATA_DIR / f"{nombre_archivo}.csv"
        if not ruta_csv.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

        datos = pd.read_csv(ruta_csv)
        resultado = validar_archivo(ruta_csv, datos)
        print(f"\nARCHIVO: {ruta_csv.name}")
        print(
            f"Filas válidas: {len(resultado.datos_validos)}; "
            f"filas rechazadas: {len(resultado.rechazos)}."
        )
        if not resultado.rechazos.empty:
            print(resultado.rechazos.to_string(index=False))


if __name__ == "__main__":
    inspeccionar_archivos()
