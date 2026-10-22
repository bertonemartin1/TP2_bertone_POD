"""Fuentes de datos tabulares compatibles con los análisis de la aplicación."""

import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class FuenteDatos(ABC):
    """Interfaz común para cargar registros como un DataFrame."""

    @abstractmethod
    def cargar(self, ruta: str | Path) -> pd.DataFrame:
        """Carga registros desde la ruta indicada."""


class FuenteCSV(FuenteDatos):
    """Carga registros tabulares desde archivos CSV."""

    def cargar(self, ruta: str | Path) -> pd.DataFrame:
        return pd.read_csv(ruta)


class FuenteJSON(FuenteDatos):
    """Carga una lista JSON de objetos con campos tabulares."""

    def cargar(self, ruta: str | Path) -> pd.DataFrame:
        ruta_json = Path(ruta)
        try:
            with ruta_json.open(encoding="utf-8") as archivo:
                registros = json.load(archivo)
        except json.JSONDecodeError as error:
            raise ValueError(f"JSON inválido en {ruta_json}: {error}") from error

        if not isinstance(registros, list):
            raise ValueError(
                f"El JSON debe contener una lista de objetos: {ruta_json}"
            )
        if any(not isinstance(registro, dict) for registro in registros):
            raise ValueError(
                f"Cada elemento del JSON debe ser un objeto: {ruta_json}"
            )

        if registros:
            columnas = set(registros[0])
            if any(set(registro) != columnas for registro in registros[1:]):
                raise ValueError(
                    f"Todos los objetos del JSON deben tener las mismas "
                    f"columnas: {ruta_json}"
                )

        return pd.DataFrame.from_records(registros)


def obtener_fuente(ruta: str | Path) -> FuenteDatos:
    """Selecciona una fuente de datos según la extensión de la ruta."""
    extension = Path(ruta).suffix.casefold()
    if extension == ".csv":
        return FuenteCSV()
    if extension == ".json":
        return FuenteJSON()
    raise ValueError(
        f"Formato de archivo no soportado: {extension or 'sin extensión'}. "
        "Formatos disponibles: .csv, .json"
    )
