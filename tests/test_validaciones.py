import importlib
import sys
import unittest
from pathlib import Path

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

validar_archivo = importlib.import_module("validaciones").validar_archivo


def crear_resultados_carrera() -> pd.DataFrame:
    return pd.DataFrame(
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
                "driver_number": 4,
                "driver": "OtroPilotoXXX",
                "team": "Ferrari",
                "laps": 57,
                "time": "+1.0s",
                "points": 18,
            },
            {
                "race": "China",
                "position": "0",
                "driver_number": 0,
                "driver": "",
                "team": " ",
                "laps": -1,
                "time": "",
                "points": -2,
            },
        ]
    )


class ValidacionesTests(unittest.TestCase):
    def test_separar_filas_validas_y_rechazos_con_numero_y_motivo(self):
        resultado = validar_archivo(
            "f1_2025_race_results.csv",
            crear_resultados_carrera(),
        )

        self.assertEqual(len(resultado.datos_validos), 1)
        self.assertEqual(resultado.datos_validos.iloc[0]["driver_number"], 4)
        self.assertEqual(resultado.rechazos["fila"].tolist(), [2, 3])
        self.assertIn("clave duplicada", resultado.rechazos.iloc[0]["motivo"])
        motivo_fila_invalida = resultado.rechazos.iloc[1]["motivo"]
        for motivo in (
            "position: las posiciones numéricas deben ser positivas",
            "driver_number: debe ser positivo",
            "driver: valor vacío",
            "team: valor vacío",
            "laps: debe ser un entero no negativo",
            "time: valor vacío",
            "points: no puede ser negativo",
        ):
            self.assertIn(motivo, motivo_fila_invalida)

    def test_acepta_nc_dq_y_vueltas_vacias(self):
        resultados = crear_resultados_carrera().iloc[[0]].copy()
        resultados.loc[resultados.index[0], "position"] = "NC"
        resultados.loc[resultados.index[0], "laps"] = None
        segunda_fila = resultados.iloc[0].copy()
        segunda_fila["position"] = "DQ"
        segunda_fila["driver_number"] = 5
        segunda_fila["driver"] = "OscarPiastriPIA"
        segunda_fila["team"] = "McLaren"
        resultados = pd.concat(
            [resultados, pd.DataFrame([segunda_fila])],
            ignore_index=True,
        )

        validacion = validar_archivo(
            "f1_2025_race_results.json",
            resultados,
        )

        self.assertEqual(len(validacion.datos_validos), 2)
        self.assertTrue(validacion.rechazos.empty)

    def test_posicion_decimal_se_rechaza_igual_que_el_esquema_original(self):
        resultados = crear_resultados_carrera().iloc[[0]].copy()
        resultados.loc[resultados.index[0], "position"] = "1.0"

        validacion = validar_archivo(
            "f1_2025_race_results.csv",
            resultados,
        )

        self.assertTrue(validacion.datos_validos.empty)
        self.assertIn(
            "position: debe contener dígitos enteros o NC/DQ",
            validacion.rechazos.iloc[0]["motivo"],
        )

    def test_rechaza_campo_nulo_y_campo_textual_vacio_con_fila(self):
        resultados = crear_resultados_carrera().iloc[[0, 2]].copy()
        resultados.iloc[0, resultados.columns.get_loc("time")] = None

        validacion = validar_archivo(
            "f1_2025_race_results.csv",
            resultados,
        )

        self.assertEqual(validacion.rechazos["fila"].tolist(), [1, 2])
        self.assertIn("time: valor nulo", validacion.rechazos.iloc[0]["motivo"])
        self.assertIn("driver: valor vacío", validacion.rechazos.iloc[1]["motivo"])

    def test_rechaza_vueltas_no_numericas_y_fraccionarias(self):
        resultados = crear_resultados_carrera().iloc[[0, 0]].copy()
        resultados["driver_number"] = [4, 5]
        resultados["driver"] = ["LandoNorrisNOR", "OscarPiastriPIA"]
        resultados["laps"] = ["sin dato", 57.5]

        validacion = validar_archivo(
            "f1_2025_race_results.csv",
            resultados,
        )

        self.assertTrue(validacion.datos_validos.empty)
        self.assertEqual(validacion.rechazos["fila"].tolist(), [1, 2])
        for motivo in validacion.rechazos["motivo"]:
            self.assertIn(
                "laps: debe ser un entero no negativo o estar vacío",
                motivo,
            )

    def test_columnas_faltantes_son_error_estructural(self):
        datos = crear_resultados_carrera().drop(columns="points")

        with self.assertRaisesRegex(ValueError, "Faltan columnas.*points"):
            validar_archivo("f1_2025_race_results.csv", datos)

    def test_archivo_sin_registros_es_error_estructural(self):
        with self.assertRaisesRegex(ValueError, "no contiene registros"):
            validar_archivo(
                "f1_2025_teams_standings.csv",
                pd.DataFrame(columns=["position", "team", "points"]),
            )

    def test_schema_admite_csv_y_json_para_el_mismo_dataset(self):
        datos = crear_resultados_carrera().iloc[[0]].copy()

        csv = validar_archivo("f1_2025_race_results.csv", datos)
        json = validar_archivo("f1_2025_race_results.json", datos)

        pd.testing.assert_frame_equal(csv.datos_validos, json.datos_validos)
        pd.testing.assert_frame_equal(csv.rechazos, json.rechazos)

    def test_columnas_de_clasificacion_validan_valores_y_duplicados(self):
        clasificacion = pd.DataFrame(
            {
                "position": [1, 2, 3],
                "team": ["McLaren", "McLaren", "Ferrari"],
                "points": [100, 80, "inválido"],
            }
        )

        resultado = validar_archivo(
            "f1_2025_teams_standings.csv",
            clasificacion,
        )

        self.assertEqual(resultado.datos_validos["team"].tolist(), ["McLaren"])
        self.assertEqual(resultado.rechazos["fila"].tolist(), [2, 3])
        self.assertIn("clave duplicada", resultado.rechazos.iloc[0]["motivo"])
        self.assertIn("points: debe ser un entero", resultado.rechazos.iloc[1]["motivo"])


if __name__ == "__main__":
    unittest.main()
