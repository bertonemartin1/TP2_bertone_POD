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

fuentes = importlib.import_module("fuentes")
FuenteCSV = fuentes.FuenteCSV
FuenteDatos = fuentes.FuenteDatos
FuenteJSON = fuentes.FuenteJSON
obtener_fuente = fuentes.obtener_fuente


class FuentesTests(unittest.TestCase):
    def test_fuentes_csv_y_json_implementan_la_misma_interfaz(self):
        self.assertTrue(issubclass(FuenteCSV, FuenteDatos))
        self.assertTrue(issubclass(FuenteJSON, FuenteDatos))

    def test_fuentes_cargan_registros_en_el_mismo_formato(self):
        registros = [
            {"race": "Australia", "points": 25},
            {"race": "China", "points": 18},
        ]

        with tempfile.TemporaryDirectory() as directorio:
            ruta_csv = Path(directorio) / "resultados.csv"
            ruta_json = Path(directorio) / "resultados.json"
            pd.DataFrame(registros).to_csv(ruta_csv, index=False)
            ruta_json.write_text(
                json.dumps(registros),
                encoding="utf-8",
            )

            datos_csv = obtener_fuente(ruta_csv).cargar(ruta_csv)
            datos_json = obtener_fuente(ruta_json).cargar(ruta_json)

        pd.testing.assert_frame_equal(datos_json, datos_csv)

    def test_obtener_fuente_rechaza_extension_no_soportada(self):
        with self.assertRaisesRegex(ValueError, "Formatos disponibles"):
            obtener_fuente("resultados.tsv")

    def test_fuente_json_rechaza_json_mal_formado(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.json"
            ruta.write_text("{inválido", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                FuenteJSON().cargar(ruta)

    def test_fuente_json_rechaza_raiz_que_no_es_una_lista(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.json"
            ruta.write_text('{"race": "Australia"}', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "lista de objetos"):
                FuenteJSON().cargar(ruta)

    def test_fuente_json_rechaza_elementos_que_no_son_objetos(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.json"
            ruta.write_text('[{"race": "Australia"}, 1]', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Cada elemento"):
                FuenteJSON().cargar(ruta)

    def test_fuente_json_rechaza_columnas_inconsistentes(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.json"
            ruta.write_text(
                '[{"race": "Australia"}, {"points": 25}]',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "mismas columnas"):
                FuenteJSON().cargar(ruta)

    def test_fuente_csv_rechaza_estructura_mal_formada(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.csv"
            with patch.object(
                pd,
                "read_csv",
                side_effect=pd.errors.ParserError("estructura inválida"),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "No se pudo interpretar el CSV",
                ):
                    FuenteCSV().cargar(ruta)

    def test_fuente_csv_informa_archivo_inexistente(self):
        ruta = Path("no_existe") / "resultados.csv"

        with self.assertRaises(FileNotFoundError):
            FuenteCSV().cargar(ruta)

    def test_fuente_json_rechaza_codificacion_invalida_con_ruta(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "resultados.json"
            ruta.write_bytes(b"\xff")

            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                FuenteJSON().cargar(ruta)


if __name__ == "__main__":
    unittest.main()
