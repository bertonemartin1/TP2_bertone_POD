import sys
import unittest
from pathlib import Path

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from transformaciones import normalizar_nombres_pilotos, transformar_archivo


class TransformacionesTests(unittest.TestCase):
    def test_resultados_eliminan_piloto_por_defecto(self):
        resultados = transformar_archivo("f1_2025_race_results.csv")

        self.assertNotIn("driver", resultados.columns)

    def test_resultados_conservan_piloto_normalizado_si_se_solicita(self):
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


if __name__ == "__main__":
    unittest.main()
