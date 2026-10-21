# Modulo para transformar los CSV de F1 en memoria, eliminando columnas innecesarias.

from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ARCHIVOS_CSV = (
    "f1_2025_drivers_standings.csv",
    "f1_2025_race_results.csv",
    "f1_2025_teams_standings.csv",
)
COLUMNAS_A_ELIMINAR = {
    "f1_2025_race_results.csv": ("driver",),
}


def normalizar_nombres_pilotos(nombres: pd.Series) -> pd.Series:
    """Elimina el sufijo de tres letras de los códigos de piloto."""
    nombres_limpios = nombres.astype("string").str.strip()
    if nombres_limpios.isna().any() or nombres_limpios.str.len().le(3).any():
        raise ValueError("Los nombres de pilotos deben tener más de tres letras.")
    return nombres_limpios.str[:-3]


def transformar_archivo(
    archivo: str | Path,
    *,
    conservar_driver: bool = False,
) -> pd.DataFrame:
    """Carga y transforma un CSV en memoria, sin modificar el archivo original.

    ``archivo`` debe ser el nombre de uno de los CSV almacenados en ``data``.
    En resultados de carrera, ``conservar_driver`` permite mantener el piloto
    normalizado para los análisis que necesitan puntos individuales.
    """
    nombre_archivo = Path(archivo).name
    if nombre_archivo not in ARCHIVOS_CSV:
        raise ValueError(
            f"Archivo no soportado: {nombre_archivo}. "
            f"Archivos disponibles: {', '.join(ARCHIVOS_CSV)}"
        )
    if conservar_driver and nombre_archivo != "f1_2025_race_results.csv":
        raise ValueError(
            "La opción conservar_driver solo se admite para "
            "f1_2025_race_results.csv."
        )

    ruta_csv = DATA_DIR / nombre_archivo
    if not ruta_csv.is_file():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    datos = pd.read_csv(ruta_csv)
    columnas = COLUMNAS_A_ELIMINAR.get(nombre_archivo, ())
    if conservar_driver and nombre_archivo == "f1_2025_race_results.csv":
        columnas = ()
    datos = datos.drop(columns=list(columnas))

    if nombre_archivo in {
        "f1_2025_drivers_standings.csv",
        "f1_2025_race_results.csv",
    } and "driver" in datos.columns:
        datos["driver"] = normalizar_nombres_pilotos(datos["driver"])

    return datos
