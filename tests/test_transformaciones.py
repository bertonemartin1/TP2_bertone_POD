import contextlib
import io
import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

transformaciones = importlib.import_module("transformaciones")
normalizar_nombres_pilotos = transformaciones.normalizar_nombres_pilotos
transformar_archivo = transformaciones.transformar_archivo
DatosSinRegistrosValidosError = importlib.import_module(
    "validaciones"
).DatosSinRegistrosValidosError


def crear_archivos_resultados(directorio: Path) -> None:
    registros = pd.DataFrame(
        [
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
                "points": 18,
            },
        ]
    )
    registros.to_csv(
        directorio / "f1_2025_race_results.csv",
        index=False,
    )
    (directorio / "f1_2025_race_results.json").write_text(
        registros.to_json(orient="records"),
        encoding="utf-8",
    )


class TransformacionesTests(unittest.TestCase):
    def test_resultados_json_equivalen_a_csv(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            crear_archivos_resultados(ruta)
            with patch.object(transformaciones, "DATA_DIR", ruta):
                resultados_csv = transformar_archivo(
                    "f1_2025_race_results.csv"
                )
                resultados_json = transformar_archivo(
                    "f1_2025_race_results.json"
                )

        pd.testing.assert_frame_equal(resultados_json, resultados_csv)

    def test_resultados_json_conservan_piloto_normalizado_si_se_solicita(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            crear_archivos_resultados(ruta)
            with patch.object(transformaciones, "DATA_DIR", ruta):
                resultados = transformar_archivo(
                    "f1_2025_race_results.json",
                    conservar_driver=True,
                )

        self.assertIn("driver", resultados.columns)
        self.assertEqual(resultados.loc[0, "driver"], "LandoNorris")

    def test_resultados_eliminan_piloto_por_defecto(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            crear_archivos_resultados(ruta)
            with patch.object(transformaciones, "DATA_DIR", ruta):
                resultados = transformar_archivo(
                    "f1_2025_race_results.csv"
                )

        self.assertNotIn("driver", resultados.columns)

    def test_resultados_conservan_piloto_normalizado_si_se_solicita(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            crear_archivos_resultados(ruta)
            with patch.object(transformaciones, "DATA_DIR", ruta):
                resultados = transformar_archivo(
                    "f1_2025_race_results.csv",
                    conservar_driver=True,
                )

        self.assertIn("driver", resultados.columns)
        self.assertEqual(resultados.loc[0, "driver"], "LandoNorris")

    def test_nombres_de_pilotos_quitan_el_sufijo(self):
        nombres = normalizar_nombres_pilotos(
            pd.Series(["LandoNorrisNOR", "MaxVerstappenVER"])
        )

        self.assertEqual(nombres.tolist(), ["LandoNorris", "MaxVerstappen"])

    def test_transformar_archivo_rechaza_extension_no_soportada(self):
        with self.assertRaisesRegex(ValueError, "Formato de archivo no soportado"):
            transformar_archivo("f1_2025_race_results.tsv")

    def test_conservar_driver_solo_se_admite_para_resultados_de_carrera(self):
        with self.assertRaisesRegex(ValueError, "solo se admite"):
            transformar_archivo(
                "f1_2025_teams_standings.csv",
                conservar_driver=True,
            )

    def test_transformaciones_csv_y_json_excluyen_las_mismas_filas(self):
        registros = pd.DataFrame(
            [
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
        )
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            registros.to_csv(
                ruta / "f1_2025_race_results.csv",
                index=False,
            )
            (ruta / "f1_2025_race_results.json").write_text(
                registros.to_json(orient="records"),
                encoding="utf-8",
            )

            with patch("transformaciones.DATA_DIR", ruta):
                with contextlib.redirect_stdout(io.StringIO()) as salida_csv:
                    datos_csv = transformar_archivo(
                        "f1_2025_race_results.csv",
                        conservar_driver=True,
                    )
                with contextlib.redirect_stdout(io.StringIO()) as salida_json:
                    datos_json = transformar_archivo(
                        "f1_2025_race_results.json",
                        conservar_driver=True,
                    )

        pd.testing.assert_frame_equal(datos_json, datos_csv)
        pd.testing.assert_frame_equal(
            datos_json.attrs["rechazos"],
            datos_csv.attrs["rechazos"],
        )
        self.assertEqual(datos_csv.attrs["rechazos"]["fila"].tolist(), [2])
        self.assertIn("points: no puede ser negativo", salida_csv.getvalue())
        self.assertEqual(
            salida_csv.getvalue().replace(".csv", ".json"),
            salida_json.getvalue(),
        )

    def test_transformacion_sin_filas_validas_expone_detalle_de_rechazos(self):
        registros = pd.DataFrame(
            [
                {
                    "race": "Australia",
                    "position": "1",
                    "driver_number": 4,
                    "driver": "LandoNorrisNOR",
                    "team": "McLaren",
                    "laps": 57,
                    "time": "1:42:06.304",
                    "points": -1,
                }
            ]
        )
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            registros.to_json(
                ruta / "f1_2025_race_results.json",
                orient="records",
            )
            with patch("transformaciones.DATA_DIR", ruta):
                with contextlib.redirect_stdout(io.StringIO()) as salida:
                    with self.assertRaises(
                        DatosSinRegistrosValidosError
                    ) as contexto:
                        transformar_archivo("f1_2025_race_results.json")

        self.assertEqual(contexto.exception.rechazos["fila"].tolist(), [1])
        self.assertIn("points: no puede ser negativo", str(contexto.exception))
        self.assertIn("se excluyeron 1 fila(s)", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
