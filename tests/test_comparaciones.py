import contextlib
import io
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

comparaciones = importlib.import_module("comparaciones")
modelos = importlib.import_module("modelos")
transformaciones = importlib.import_module("transformaciones")
validaciones = importlib.import_module("validaciones")
CampeonatoF1 = modelos.CampeonatoF1
TipoCampeonato = modelos.TipoCampeonato


class ComparacionesTests(unittest.TestCase):
    def test_campeonatos_equivalentes_csv_json_conservan_tablas_y_acumulados(self):
        resultados = [
            {
                "race": "Australia",
                "position": "1",
                "driver_number": 4,
                "driver": "LandoNorrisNOR",
                "team": "McLaren",
                "laps": 57,
                "time": "1:42:06.304",
                "points": 25,
            },
            {
                "race": "Australia",
                "position": "2",
                "driver_number": 16,
                "driver": "CharlesLeclercLEC",
                "team": "Ferrari",
                "laps": 57,
                "time": "+1.0s",
                "points": 18,
            },
            {
                "race": "China",
                "position": "2",
                "driver_number": 4,
                "driver": "LandoNorrisNOR",
                "team": "McLaren",
                "laps": 56,
                "time": "+1.0s",
                "points": 18,
            },
        ]
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            resultados_df = pd.DataFrame(resultados)
            resultados_df.to_csv(
                ruta / "f1_2025_race_results.csv",
                index=False,
            )
            (ruta / "f1_2025_race_results.json").write_text(
                json.dumps(resultados),
                encoding="utf-8",
            )
            pd.DataFrame(
                {
                    "position": [1, 2],
                    "team": ["McLaren", "Ferrari"],
                    "points": [43, 18],
                }
            ).to_csv(
                ruta / "f1_2025_teams_standings.csv",
                index=False,
            )
            pd.DataFrame(
                {
                    "position": [1, 2],
                    "driver": ["LandoNorrisNOR", "CharlesLeclercLEC"],
                    "nationality": ["GBR", "MON"],
                    "team": ["McLaren", "Ferrari"],
                    "points": [43, 18],
                }
            ).to_csv(
                ruta / "f1_2025_drivers_standings.csv",
                index=False,
            )

            acumulados_por_formato = {}
            clasificaciones_por_formato = {}
            temporadas_por_formato = {}
            with patch.object(transformaciones, "DATA_DIR", ruta):
                for extension in ("csv", "json"):
                    with self.subTest(extension=extension):
                        with patch.object(
                            comparaciones,
                            "ARCHIVO_CARRERAS",
                            f"f1_2025_race_results.{extension}",
                        ):
                            with patch.object(
                                comparaciones,
                                "graficar_evolucion_puntos_constructores",
                            ) as grafico_constructores:
                                with contextlib.redirect_stdout(
                                    io.StringIO()
                                ):
                                    clasificacion_constructores = (
                                        comparaciones
                                        .comparar_campeonato_constructores()
                                    )
                            with patch.object(
                                comparaciones,
                                "graficar_evolucion_puntos_pilotos",
                            ) as grafico_pilotos:
                                with contextlib.redirect_stdout(
                                    io.StringIO()
                                ):
                                    clasificacion_pilotos = (
                                        comparaciones.comparar_campeonato_pilotos()
                                    )
                            with patch.object(
                                comparaciones,
                                "graficar_evolucion_puntos_piloto",
                            ):
                                with contextlib.redirect_stdout(
                                    io.StringIO()
                                ):
                                    temporada_piloto = (
                                        comparaciones.comparar_piloto_temporada(
                                            "CharlesLeclerc"
                                        )
                                    )
                        clasificaciones_por_formato[extension] = (
                            clasificacion_constructores,
                            clasificacion_pilotos,
                        )
                        temporadas_por_formato[extension] = temporada_piloto
                        acumulados_por_formato[extension] = (
                            grafico_constructores.call_args.args[0],
                            grafico_pilotos.call_args.args[0],
                        )

        for tabla_csv, tabla_json in zip(
            clasificaciones_por_formato["csv"],
            clasificaciones_por_formato["json"],
        ):
            pd.testing.assert_frame_equal(tabla_csv, tabla_json)
        pd.testing.assert_frame_equal(
            temporadas_por_formato["csv"],
            temporadas_por_formato["json"],
        )
        for acumulado_csv, acumulado_json in zip(
            acumulados_por_formato["csv"],
            acumulados_por_formato["json"],
        ):
            pd.testing.assert_frame_equal(acumulado_csv, acumulado_json)
        self.assertEqual(
            acumulados_por_formato["json"][0].index.tolist(),
            ["Australia", "China"],
        )
        self.assertEqual(
            acumulados_por_formato["json"][0].loc["China", "Ferrari"],
            18,
        )
        self.assertEqual(
            acumulados_por_formato["json"][1].loc["China", "CharlesLeclerc"],
            18,
        )
        self.assertEqual(
            temporadas_por_formato["json"].loc["China", "Posición"],
            "Sin participación",
        )
        self.assertEqual(
            temporadas_por_formato["json"].loc["China", "Puntos"],
            0,
        )

    def test_comparacion_excluye_fila_rechazada_y_muestra_motivo(self):
        registros = [
            {
                "race": "Australia",
                "position": "1",
                "driver_number": 4,
                "driver": "LandoNorrisNOR",
                "team": "McLaren",
                "laps": 57,
                "time": "1:42:06.304",
                "points": 25,
            },
            {
                "race": "Australia",
                "position": "2",
                "driver_number": 1,
                "driver": "MaxVerstappenVER",
                "team": "Red Bull Racing",
                "laps": 57,
                "time": "+0.895s",
                "points": -1,
            },
        ]
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "f1_2025_race_results.json"
            ruta.write_text(json.dumps(registros), encoding="utf-8")
            with patch.object(transformaciones, "DATA_DIR", Path(directorio)):
                with patch.object(
                    comparaciones,
                    "ARCHIVO_CARRERAS",
                    ruta.name,
                ):
                    with patch.object(
                        comparaciones,
                        "graficar_puntos_pilotos_carrera",
                    ):
                        with contextlib.redirect_stdout(io.StringIO()) as salida:
                            tabla = comparaciones.comparar_pilotos_por_carrera(
                                "Australia"
                            )

        self.assertEqual(tabla["driver"].tolist(), ["LandoNorris"])
        self.assertIn("points: no puede ser negativo", salida.getvalue())
        self.assertEqual(
            tabla.attrs["rechazos"]["fila"].tolist(),
            [2],
        )
        self.assertEqual(tabla["points"].tolist(), [25])

    def test_comparacion_no_genera_resultado_si_todas_las_filas_son_invalidas(self):
        registro = {
            "race": "Australia",
            "position": "1",
            "driver_number": 4,
            "driver": "LandoNorrisNOR",
            "team": "McLaren",
            "laps": 57,
            "time": "1:42:06.304",
            "points": -1,
        }
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "f1_2025_race_results.json"
            ruta.write_text(json.dumps([registro]), encoding="utf-8")
            with patch.object(transformaciones, "DATA_DIR", Path(directorio)):
                with patch.object(
                    comparaciones,
                    "ARCHIVO_CARRERAS",
                    ruta.name,
                ):
                    with patch.object(
                        comparaciones,
                        "graficar_puntos_pilotos_carrera",
                    ) as graficar:
                        with self.assertRaises(
                            validaciones.DatosSinRegistrosValidosError
                        ):
                            comparaciones.comparar_pilotos_por_carrera(
                                "Australia"
                            )

        graficar.assert_not_called()

    def test_comparacion_de_carrera_da_el_mismo_resultado_con_csv_y_json(self):
        registros = [
            {
                "race": "Australia",
                "position": "2",
                "driver_number": 4,
                "driver": "LandoNorrisNOR",
                "team": "McLaren",
                "laps": 57,
                "time": "+1.0s",
                "points": 18,
            },
            {
                "race": "Australia",
                "position": "1",
                "driver_number": 1,
                "driver": "MaxVerstappenVER",
                "team": "Red Bull Racing",
                "laps": 58,
                "time": "1:42:06.304",
                "points": 25,
            },
        ]
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            datos = pd.DataFrame(registros)
            datos.to_csv(ruta / "f1_2025_race_results.csv", index=False)
            (ruta / "f1_2025_race_results.json").write_text(
                json.dumps(registros),
                encoding="utf-8",
            )
            with patch.object(transformaciones, "DATA_DIR", ruta):
                with patch.object(
                    comparaciones,
                    "graficar_puntos_pilotos_carrera",
                ):
                    with patch.object(
                        comparaciones,
                        "ARCHIVO_CARRERAS",
                        "f1_2025_race_results.json",
                    ):
                        resultado_json = (
                            comparaciones.comparar_pilotos_por_carrera(
                                "Australia"
                            )
                        )
                    with patch.object(
                        comparaciones,
                        "ARCHIVO_CARRERAS",
                        "f1_2025_race_results.csv",
                    ):
                        resultado_csv = (
                            comparaciones.comparar_pilotos_por_carrera(
                                "Australia"
                            )
                        )

        pd.testing.assert_frame_equal(resultado_json, resultado_csv)
        self.assertEqual(
            resultado_csv["driver"].tolist(),
            ["MaxVerstappen", "LandoNorris"],
        )

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
                "position": ["1", "2", "3"],
                "team": ["McLaren", "Ferrari", "McLaren"],
                "points": [5, 7, 3],
            }
        )

        tipos_inicializados = []

        def crear_campeonato(
            tipo: TipoCampeonato,
            datos_clasificacion: pd.DataFrame,
            resultados_carreras: pd.DataFrame,
        ) -> CampeonatoF1:
            tipos_inicializados.append(tipo)
            return CampeonatoF1(tipo, datos_clasificacion, resultados_carreras)

        with patch.object(
            comparaciones,
            "_leer_csv_puntuaciones",
            side_effect=[clasificacion, carreras],
        ):
            with patch.object(comparaciones, "CampeonatoF1", crear_campeonato):
                with patch.object(
                    comparaciones,
                    "graficar_evolucion_puntos_constructores",
                ) as graficar:
                    resultado = comparaciones.comparar_campeonato_constructores()

        self.assertEqual(resultado["team"].tolist(), ["Ferrari", "McLaren"])
        self.assertEqual(tipos_inicializados, ["constructores"])
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
            side_effect=[
                clasificacion,
                pd.DataFrame(
                    {
                        "race": ["Australia"],
                        "position": ["1"],
                        "team": ["McLaren"],
                        "points": [5],
                    }
                ),
            ],
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
                "position": ["1", "2", "3"],
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
                    {
                        "race": ["Australia"],
                        "position": ["1"],
                        "driver": ["Piloto A"],
                        "points": [5],
                    }
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
