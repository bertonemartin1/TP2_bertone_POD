import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import comparaciones


class ComparacionesTests(unittest.TestCase):
    def test_comparacion_de_carrera_da_el_mismo_resultado_con_csv_y_json(self):
        with patch.object(
            comparaciones,
            "ARCHIVO_CARRERAS",
            "f1_2025_race_results.json",
        ):
            with patch.object(comparaciones, "graficar_puntos_pilotos_carrera"):
                resultado_json = comparaciones.comparar_pilotos_por_carrera(
                    "Australia"
                )

        with patch.object(
            comparaciones,
            "ARCHIVO_CARRERAS",
            "f1_2025_race_results.csv",
        ):
            with patch.object(comparaciones, "graficar_puntos_pilotos_carrera"):
                resultado_csv = comparaciones.comparar_pilotos_por_carrera(
                    "Australia"
                )

        pd.testing.assert_frame_equal(resultado_json, resultado_csv)

    def test_leer_csv_limpia_texto_y_convierte_puntos(self):
        datos = pd.DataFrame(
            {"team": ["  McLaren  "], "points": ["12.5"]}
        )

        with patch.object(comparaciones, "transformar_archivo", return_value=datos):
            resultados = comparaciones._leer_csv_puntuaciones(
                "equipos.csv",
                ("team", "points"),
            )

        self.assertEqual(resultados.loc[0, "team"], "McLaren")
        self.assertEqual(resultados.loc[0, "points"], 12.5)

    def test_leer_csv_rechaza_columnas_faltantes(self):
        datos = pd.DataFrame({"team": ["McLaren"]})

        with patch.object(comparaciones, "transformar_archivo", return_value=datos):
            with self.assertRaisesRegex(ValueError, "Faltan columnas requeridas"):
                comparaciones._leer_csv_puntuaciones(
                    "equipos.csv",
                    ("team", "points"),
                )

    def test_leer_csv_rechaza_texto_vacio(self):
        datos = pd.DataFrame({"team": ["  "], "points": [10]})

        with patch.object(comparaciones, "transformar_archivo", return_value=datos):
            with self.assertRaisesRegex(ValueError, "valores vacíos"):
                comparaciones._leer_csv_puntuaciones(
                    "equipos.csv",
                    ("team", "points"),
                )

    def test_leer_csv_rechaza_puntos_invalidos_o_negativos(self):
        for puntos in ("no-numérico", -1):
            with self.subTest(puntos=puntos):
                datos = pd.DataFrame({"team": ["McLaren"], "points": [puntos]})

                with patch.object(
                    comparaciones,
                    "transformar_archivo",
                    return_value=datos,
                ):
                    with self.assertRaisesRegex(ValueError, "puntos vacíos"):
                        comparaciones._leer_csv_puntuaciones(
                            "equipos.csv",
                            ("team", "points"),
                        )

    def test_calcular_puntos_acumulados_por_carrera_y_equipo(self):
        resultados = pd.DataFrame(
            {
                "race": ["Australia", "Australia", "China"],
                "team": ["McLaren", "Ferrari", "McLaren"],
                "points": [10, 5, 3],
            }
        )

        acumulados = comparaciones._calcular_puntos_acumulados(resultados)

        self.assertEqual(acumulados.loc["Australia", "McLaren"], 10)
        self.assertEqual(acumulados.loc["China", "McLaren"], 13)
        self.assertEqual(acumulados.loc["China", "Ferrari"], 5)

    def test_calcular_puntos_acumulados_rechaza_resultados_vacios(self):
        resultados = pd.DataFrame(columns=["race", "team", "points"])

        with self.assertRaisesRegex(ValueError, "No hay resultados"):
            comparaciones._calcular_puntos_acumulados(resultados)

    def test_filtrar_carrera_no_distingue_mayusculas_ni_espacios(self):
        resultados = pd.DataFrame(
            {"race": ["Australia", "China"], "points": [10, 5]}
        )

        filtrados = comparaciones._filtrar_por_carrera(resultados, "  aUsTrAlIa ")

        self.assertEqual(filtrados["points"].tolist(), [10])

    def test_filtrar_carrera_informa_carreras_disponibles(self):
        resultados = pd.DataFrame({"race": ["Australia"], "points": [10]})

        with self.assertRaisesRegex(ValueError, "Carreras disponibles: Australia"):
            comparaciones._filtrar_por_carrera(resultados, "China")

    def test_buscar_nombre_no_distingue_mayusculas_ni_espacios(self):
        nombre = comparaciones._buscar_nombre_disponible(
            "  mClArEn ",
            ["McLaren", "Ferrari"],
            "el equipo",
            "Equipos",
        )

        self.assertEqual(nombre, "McLaren")

    def test_buscar_nombre_inexistente_informa_opciones(self):
        with self.assertRaisesRegex(ValueError, "Equipos disponibles: McLaren"):
            comparaciones._buscar_nombre_disponible(
                "Williams",
                ["McLaren"],
                "el equipo",
                "Equipos",
            )

    def test_comparar_campeonato_constructores_ordena_y_grafica(self):
        clasificacion = pd.DataFrame(
            {
                "position": [2, 1],
                "team": ["McLaren", "Ferrari"],
                "points": [8, 10],
            }
        )
        carreras = pd.DataFrame(
            {
                "race": ["Australia", "Australia", "China"],
                "team": ["McLaren", "Ferrari", "McLaren"],
                "points": [5, 7, 3],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[clasificacion, carreras],
        ):
            with patch.object(
                comparaciones,
                "graficar_evolucion_puntos_constructores",
            ) as graficar:
                resultado = comparaciones.comparar_campeonato_constructores()

        self.assertEqual(resultado["team"].tolist(), ["Ferrari", "McLaren"])
        self.assertEqual(
            graficar.call_args.args[0].loc["China", "McLaren"],
            8,
        )

    def test_comparar_campeonato_constructores_rechaza_posicion_invalida(self):
        clasificacion = pd.DataFrame(
            {"position": ["primero"], "team": ["McLaren"], "points": [10]}
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=clasificacion,
        ):
            with self.assertRaisesRegex(ValueError, "posiciones inválidas"):
                comparaciones.comparar_campeonato_constructores()

    def test_comparar_campeonato_pilotos_ordena_y_grafica(self):
        clasificacion = pd.DataFrame(
            {
                "position": [2, 1],
                "driver": ["Piloto B", "Piloto A"],
                "team": ["Ferrari", "McLaren"],
                "points": [8, 10],
            }
        )
        carreras = pd.DataFrame(
            {
                "race": ["Australia", "Australia", "China"],
                "driver": ["Piloto A", "Piloto B", "Piloto A"],
                "points": [5, 7, 3],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[clasificacion, carreras],
        ):
            with patch.object(
                comparaciones,
                "graficar_evolucion_puntos_pilotos",
            ) as graficar:
                resultado = comparaciones.comparar_campeonato_pilotos()

        self.assertEqual(resultado["driver"].tolist(), ["Piloto A", "Piloto B"])
        self.assertEqual(
            graficar.call_args.args[0].loc["China", "Piloto A"],
            8,
        )

    def test_comparar_campeonato_pilotos_rechaza_pilotos_duplicados(self):
        clasificacion = pd.DataFrame(
            {
                "position": [1, 2],
                "driver": ["Piloto A", "Piloto A"],
                "team": ["McLaren", "Ferrari"],
                "points": [10, 8],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[
                clasificacion,
                pd.DataFrame(
                    {"race": ["Australia"], "driver": ["Piloto A"], "points": [5]}
                ),
            ],
        ):
            with self.assertRaisesRegex(ValueError, "nombres de pilotos no son únicos"):
                comparaciones.comparar_campeonato_pilotos()

    def test_comparar_constructores_por_carrera_ordena_y_grafica(self):
        resultados = pd.DataFrame(
            {
                "race": ["Australia", "Australia", "Australia"],
                "position": ["2", "1", "DNF"],
                "team": ["McLaren", "Ferrari", "Williams"],
                "points": [5, 7, 0],
            }
        )

        with patch.object(
            comparaciones,
            "transformar_archivo",
            return_value=resultados,
        ):
            with patch.object(
                comparaciones,
                "graficar_puntos_constructores_carrera",
            ) as graficar:
                tabla = comparaciones.comparar_constructores_por_carrera(
                    " australia "
                )

        self.assertEqual(tabla["team"].tolist(), ["Ferrari", "McLaren", "Williams"])
        self.assertEqual(tabla["puntos"].tolist(), [7, 5, 0])
        graficar.assert_called_once()

    def test_comparar_constructores_por_carrera_rechaza_carrera_inexistente(self):
        with patch.object(
            comparaciones,
            "transformar_archivo",
            return_value=pd.DataFrame(
                {"race": ["Australia"], "position": ["1"], "team": ["McLaren"], "points": [5]}
            ),
        ):
            with self.assertRaisesRegex(ValueError, "No se encontró la carrera"):
                comparaciones.comparar_constructores_por_carrera("China")

    def test_comparar_h2h_incluye_carreras_sin_participacion(self):
        equipos = pd.DataFrame({"team": ["McLaren"], "points": [10]})
        carreras = pd.DataFrame(
            {
                "race": ["Australia", "Australia", "China"],
                "position": ["1", "2", "3"],
                "driver": ["Piloto A", "Piloto B", "Piloto A"],
                "team": ["McLaren", "McLaren", "McLaren"],
                "points": [10, 8, 6],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[equipos, carreras],
        ):
            tabla = comparaciones.comparar_h2h_equipo("mClArEn")

        self.assertEqual(tabla.loc[("China", "Piloto B"), "Posición"], "Sin participación")
        self.assertEqual(tabla.loc[("China", "Piloto B"), "Puntos"], 0)

    def test_comparar_h2h_rechaza_equipo_inexistente(self):
        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=pd.DataFrame({"team": ["McLaren"], "points": [10]}),
        ):
            with self.assertRaisesRegex(ValueError, "No se encontró el equipo"):
                comparaciones.comparar_h2h_equipo("Williams")

    def test_comparar_piloto_temporada_incluye_carrera_sin_participacion(self):
        clasificacion = pd.DataFrame(
            {"driver": ["Piloto A"], "team": ["McLaren"], "points": [10]}
        )
        carreras = pd.DataFrame(
            {
                "race": ["Australia", "China"],
                "position": ["1", "2"],
                "driver": ["Piloto A", "Piloto B"],
                "points": [10, 8],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[clasificacion, carreras],
        ):
            with patch.object(comparaciones, "graficar_evolucion_puntos_piloto"):
                tabla = comparaciones.comparar_piloto_temporada(" piloto a ")

        self.assertEqual(tabla.loc["China", "Posición"], "Sin participación")
        self.assertEqual(tabla.loc["China", "Puntos"], 0)

    def test_comparar_piloto_temporada_rechaza_piloto_inexistente(self):
        clasificacion = pd.DataFrame(
            {"driver": ["Piloto A"], "team": ["McLaren"], "points": [10]}
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=clasificacion,
        ):
            with self.assertRaisesRegex(ValueError, "No se encontró el piloto"):
                comparaciones.comparar_piloto_temporada("Piloto B")

    def test_comparar_pilotos_por_carrera_ordena_y_grafica(self):
        resultados = pd.DataFrame(
            {
                "race": ["Australia", "Australia"],
                "position": ["2", "1"],
                "driver_number": [4, 1],
                "driver": ["Piloto B", "Piloto A"],
                "team": ["Ferrari", "McLaren"],
                "points": [8, 10],
            }
        )

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=resultados,
        ):
            with patch.object(
                comparaciones,
                "graficar_puntos_pilotos_carrera",
            ) as graficar:
                tabla = comparaciones.comparar_pilotos_por_carrera("Australia")

        self.assertEqual(tabla["driver"].tolist(), ["Piloto A", "Piloto B"])
        graficar.assert_called_once()

    def test_listados_disponibles_devuelven_nombres_unicos(self):
        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[
                pd.DataFrame({"team": ["McLaren", "McLaren"], "points": [10, 10]}),
                pd.DataFrame({"driver": ["Piloto A", "Piloto A"], "points": [10, 10]}),
            ],
        ):
            equipos = comparaciones.obtener_equipos_disponibles()
            pilotos = comparaciones.obtener_nombres_pilotos()

        self.assertEqual(equipos, ["McLaren"])
        self.assertEqual(pilotos, ["Piloto A"])

    def test_listados_disponibles_rechazan_clasificaciones_vacias(self):
        vacia = pd.DataFrame(columns=["team", "points"])

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=vacia,
        ):
            with self.assertRaisesRegex(ValueError, "No hay equipos disponibles"):
                comparaciones.obtener_equipos_disponibles()

        vacia_pilotos = pd.DataFrame(columns=["driver", "points"])
        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            return_value=vacia_pilotos,
        ):
            with self.assertRaisesRegex(ValueError, "No hay pilotos disponibles"):
                comparaciones.obtener_nombres_pilotos()

    def test_obtener_carreras_disponibles(self):
        resultados = pd.DataFrame({"race": ["Australia", "China"]})

        with patch.object(
            comparaciones,
            "transformar_archivo",
            return_value=resultados,
        ):
            carreras = comparaciones.obtener_carreras_disponibles()

        self.assertEqual(carreras, ["Australia", "China"])


if __name__ == "__main__":
    unittest.main()
