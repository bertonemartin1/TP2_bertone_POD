"""Modelos del dominio para los campeonatos de Fórmula 1."""

from typing import Literal

import pandas as pd


TipoCampeonato = Literal["pilotos", "constructores"]


class CampeonatoF1:
    """Reúne y analiza la clasificación y los resultados de un campeonato."""

    _COLUMNAS_POR_TIPO = {
        "pilotos": "driver",
        "constructores": "team",
    }

    def __init__(
        self,
        tipo: TipoCampeonato,
        clasificacion: pd.DataFrame,
        resultados: pd.DataFrame,
    ) -> None:
        if not isinstance(tipo, str) or tipo not in self._COLUMNAS_POR_TIPO:
            tipos_disponibles = ", ".join(self._COLUMNAS_POR_TIPO)
            raise ValueError(
                f"Tipo de campeonato no válido: {tipo}. "
                f"Tipos disponibles: {tipos_disponibles}."
            )

        self.tipo = tipo
        self._columna_entidad = self._COLUMNAS_POR_TIPO[tipo]
        self.clasificacion = clasificacion.copy(deep=True)
        self.resultados = resultados.copy(deep=True)
        self._validar_datos()
        self.calendario = self.resultados["race"].drop_duplicates().tolist()

    def _validar_datos(self) -> None:
        columnas_clasificacion = {
            "position",
            "points",
            self._columna_entidad,
        }
        columnas_resultados = {
            "race",
            "position",
            "points",
            self._columna_entidad,
        }
        self._validar_columnas(
            self.clasificacion,
            columnas_clasificacion,
            "clasificación",
        )
        self._validar_columnas(
            self.resultados,
            columnas_resultados,
            "resultados",
        )

        for tabla, nombre in (
            (self.clasificacion, "clasificación"),
            (self.resultados, "resultados"),
        ):
            if tabla.empty:
                raise ValueError(f"No hay filas en la tabla de {nombre}.")

        for tabla, columnas, nombre in (
            (
                self.clasificacion,
                ("position", self._columna_entidad),
                "clasificación",
            ),
            (
                self.resultados,
                ("race", "position", self._columna_entidad),
                "resultados",
            ),
        ):
            for columna in columnas:
                valores = tabla[columna].astype("string").str.strip()
                if valores.isna().any() or valores.eq("").any():
                    raise ValueError(
                        f"La columna {columna} contiene valores vacíos "
                        f"en la tabla de {nombre}."
                    )
                tabla[columna] = valores

        posiciones = pd.to_numeric(
            self.clasificacion["position"],
            errors="coerce",
        )
        if posiciones.isna().any() or posiciones.lt(1).any():
            raise ValueError(
                "La clasificación contiene posiciones inválidas o no positivas."
            )
        self.clasificacion["position"] = posiciones

        for tabla, nombre in (
            (self.clasificacion, "clasificación"),
            (self.resultados, "resultados"),
        ):
            puntos = pd.to_numeric(tabla["points"], errors="coerce")
            if puntos.isna().any() or puntos.lt(0).any():
                raise ValueError(
                    f"La tabla de {nombre} contiene puntos no numéricos "
                    "o negativos."
                )
            tabla["points"] = puntos

    @staticmethod
    def _validar_columnas(
        tabla: pd.DataFrame,
        columnas_requeridas: set[str],
        nombre: str,
    ) -> None:
        faltantes = columnas_requeridas.difference(tabla.columns)
        if faltantes:
            columnas = ", ".join(sorted(faltantes))
            raise ValueError(
                f"Faltan columnas requeridas en la tabla de {nombre}: {columnas}."
            )

    def obtener_clasificacion(self) -> pd.DataFrame:
        """Devuelve una copia de la clasificación ordenada por posición."""
        return self.clasificacion.sort_values(
            "position",
            kind="stable",
        ).reset_index(drop=True)

    def calcular_puntos_acumulados(self) -> pd.DataFrame:
        """Acumula por carrera los puntos de los pilotos o constructores."""
        entidades = self.obtener_clasificacion()[self._columna_entidad].tolist()
        puntos_por_carrera = (
            self.resultados.groupby(
                ["race", self._columna_entidad],
                sort=False,
            )["points"]
            .sum()
            .unstack(fill_value=0)
            .reindex(
                index=pd.Index(self.calendario, name="race"),
                columns=pd.Index(
                    entidades,
                    name=self._columna_entidad,
                ),
                fill_value=0,
            )
            .fillna(0)
        )
        return puntos_por_carrera.cumsum()

    def resultados_de_carrera(self, carrera: str) -> pd.DataFrame:
        """Devuelve los resultados de una carrera ordenados por posición."""
        carrera_normalizada = carrera.strip().casefold()
        resultados = self.resultados.loc[
            self.resultados["race"].str.casefold() == carrera_normalizada
        ].copy()
        if resultados.empty:
            disponibles = ", ".join(self.calendario)
            raise ValueError(
                f"No se encontró la carrera '{carrera}'. "
                f"Carreras disponibles: {disponibles or 'ninguna'}"
            )

        resultados["_posicion_numerica"] = pd.to_numeric(
            resultados["position"],
            errors="coerce",
        )
        resultados["_orden_original"] = range(len(resultados))
        return (
            resultados.sort_values(
                ["_posicion_numerica", "_orden_original"],
                ascending=True,
                na_position="last",
                kind="stable",
            )
            .drop(columns=["_posicion_numerica", "_orden_original"])
            .reset_index(drop=True)
        )
