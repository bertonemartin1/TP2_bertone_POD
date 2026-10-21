"""Funciones para crear los gráficos de las comparaciones de F1."""

import matplotlib.pyplot as plt
import pandas as pd


def graficar_evolucion_puntos_constructores(
    puntos_acumulados: pd.DataFrame,
    constructores: list[str],
) -> None:
    """Grafica la evolución de puntos acumulados de los constructores."""
    figura, eje = plt.subplots(figsize=(12, 7))
    for constructor in constructores:
        if constructor not in puntos_acumulados.columns:
            continue
        eje.plot(
            puntos_acumulados.index,
            puntos_acumulados[constructor],
            marker="o",
            label=constructor,
        )
    eje.set_title("Evolución de puntos por carrera (sin sprints)")
    eje.set_xlabel("Gran Premio")
    eje.set_ylabel("Puntos acumulados en carreras")
    eje.grid(True, linestyle="--", alpha=0.5)
    eje.legend(title="Constructor", bbox_to_anchor=(1.02, 1), loc="upper left")
    figura.autofmt_xdate(rotation=45)
    figura.tight_layout()
    plt.show()


def graficar_puntos_constructores_carrera(
    resultados: pd.DataFrame,
    carrera: str,
) -> None:
    """Grafica los puntos obtenidos por cada constructor en una carrera."""
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.bar(resultados["team"], resultados["puntos"], color="steelblue")
    eje.set_title(f"Puntos por constructor en {carrera}")
    eje.set_xlabel("Constructor")
    eje.set_ylabel("Puntos")
    eje.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=45, ha="right")
    figura.tight_layout()
    plt.show()


def graficar_evolucion_puntos_pilotos(
    puntos_acumulados: pd.DataFrame,
    pilotos: list[str],
) -> None:
    """Grafica la evolución de puntos acumulados de los pilotos."""
    figura, eje = plt.subplots(figsize=(14, 8))
    for piloto in pilotos:
        eje.plot(
            puntos_acumulados.index,
            puntos_acumulados[piloto],
            marker="o",
            label=piloto,
        )
    eje.set_title("Evolución de puntos de pilotos por carrera (sin sprints)")
    eje.set_xlabel("Gran Premio")
    eje.set_ylabel("Puntos acumulados en carreras")
    eje.grid(True, linestyle="--", alpha=0.5)
    eje.legend(title="Piloto", bbox_to_anchor=(1.02, 1), loc="upper left")
    figura.autofmt_xdate(rotation=45)
    figura.tight_layout()
    plt.show()


def graficar_puntos_pilotos_carrera(
    resultados: pd.DataFrame,
    carrera: str,
) -> None:
    """Grafica los puntos obtenidos por cada piloto en una carrera."""
    figura, eje = plt.subplots(figsize=(12, 7))
    eje.bar(resultados["driver"], resultados["points"], color="steelblue")
    eje.set_title(f"Puntos por piloto en {carrera}")
    eje.set_xlabel("Piloto")
    eje.set_ylabel("Puntos")
    eje.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=60, ha="right")
    figura.tight_layout()
    plt.show()


def graficar_evolucion_puntos_piloto(
    puntos_acumulados: pd.Series,
    nombre_piloto: str,
) -> None:
    """Grafica los puntos acumulados de un piloto a lo largo de la temporada."""
    figura, eje = plt.subplots(figsize=(12, 7))
    eje.plot(
        puntos_acumulados.index,
        puntos_acumulados,
        marker="o",
        label=nombre_piloto,
    )
    eje.set_title(f"Evolución de puntos de {nombre_piloto} por carrera")
    eje.set_xlabel("Gran Premio")
    eje.set_ylabel("Puntos acumulados en carreras")
    eje.grid(True, linestyle="--", alpha=0.5)
    figura.autofmt_xdate(rotation=45)
    figura.tight_layout()
    plt.show()
