import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from fuentes import FuenteCSV, FuenteDatos, FuenteJSON, obtener_fuente


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


if __name__ == "__main__":
    unittest.main()
