import unittest

import pandas as pd


from src.modelos import CampeonatoF1


def crear_clasificacion() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "position": [2, 1],
            "team": ["Ferrari", "McLaren"],
            "points": [5, 13],
        }
    )


def crear_resultados() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "race": ["China", "Australia", "Australia"],
            "position": ["2", "1", "2"],
            "team": ["McLaren", "McLaren", "Ferrari"],
            "points": [3, 10, 5],
        }
    )


class CampeonatoF1Tests(unittest.TestCase):
    def test_clasificacion_se_ordena_por_posicion(self):
        campeonato = CampeonatoF1(
            "constructores",
            crear_clasificacion(),
            crear_resultados(),
        )

        ordenada = campeonato.obtener_clasificacion()

        self.assertEqual(ordenada["team"].tolist(), ["McLaren", "Ferrari"])

    def test_puntos_acumulados_respetan_calendario_y_ausencias(self):
        campeonato = CampeonatoF1(
            "constructores",
            crear_clasificacion(),
            crear_resultados(),
        )

        acumulados = campeonato.calcular_puntos_acumulados()

        self.assertEqual(acumulados.index.tolist(), ["China", "Australia"])
        self.assertEqual(acumulados.loc["China", "McLaren"], 3)
        self.assertEqual(acumulados.loc["China", "Ferrari"], 0)
        self.assertEqual(acumulados.loc["Australia", "McLaren"], 13)
        self.assertEqual(acumulados.loc["Australia", "Ferrari"], 5)

    def test_resultados_de_carrera_ordenan_por_posicion(self):
        campeonato = CampeonatoF1(
            "constructores",
            crear_clasificacion(),
            crear_resultados(),
        )

        resultados = campeonato.resultados_de_carrera(" australia ")

        self.assertEqual(resultados["team"].tolist(), ["McLaren", "Ferrari"])

    def test_resultados_de_carrera_inexistente_informan_disponibles(self):
        campeonato = CampeonatoF1(
            "constructores",
            crear_clasificacion(),
            crear_resultados(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Carreras disponibles: China, Australia",
        ):
            campeonato.resultados_de_carrera("Monaco")

    def test_rechaza_tipo_de_campeonato_invalido(self):
        with self.assertRaisesRegex(ValueError, "Tipo de campeonato no válido"):
            CampeonatoF1("sprints", crear_clasificacion(), crear_resultados())

    def test_rechaza_columnas_requeridas_ausentes(self):
        resultados = crear_resultados().drop(columns="position")

        with self.assertRaisesRegex(
            ValueError,
            "Faltan columnas requeridas en la tabla de resultados: position",
        ):
            CampeonatoF1("constructores", crear_clasificacion(), resultados)

    def test_rechaza_puntos_negativos_o_no_numericos(self):
        for punto in (-1, "inválido"):
            with self.subTest(punto=punto):
                resultados = crear_resultados()
                resultados["points"] = resultados["points"].astype(object)
                resultados.loc[0, "points"] = punto

                with self.assertRaisesRegex(ValueError, "puntos no numéricos"):
                    CampeonatoF1(
                        "constructores",
                        crear_clasificacion(),
                        resultados,
                    )

    def test_admite_campeonato_de_pilotos(self):
        clasificacion = pd.DataFrame(
            {
                "position": [1],
                "driver": ["Piloto A"],
                "points": [10],
            }
        )
        resultados = pd.DataFrame(
            {
                "race": ["Australia"],
                "position": ["1"],
                "driver": ["Piloto A"],
                "points": [10],
            }
        )

        campeonato = CampeonatoF1("pilotos", clasificacion, resultados)

        self.assertEqual(
            campeonato.calcular_puntos_acumulados().loc[
                "Australia",
                "Piloto A",
            ],
            10,
        )


if __name__ == "__main__":
    unittest.main()
