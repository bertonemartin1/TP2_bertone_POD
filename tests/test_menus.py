import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

leer_seleccion = importlib.import_module("menus").leer_seleccion


class LeerSeleccionTests(unittest.TestCase):
    def test_nombre_invalido_informa_y_vuelve_a_pedir(self):
        with patch("builtins.input", side_effect=["Mclaren incorrecto", "mClArEn"]):
            with patch("builtins.print") as imprimir:
                equipo = leer_seleccion(
                    "Equipo: ",
                    ["McLaren", "Mercedes"],
                    "equipo",
                )

        self.assertEqual(equipo, "McLaren")
        imprimir.assert_called_once_with(
            "Error: equipo 'Mclaren incorrecto' no válido. "
            "Opciones disponibles: McLaren, Mercedes."
        )

    def test_cadena_vacia_informa_y_vuelve_a_pedir(self):
        with patch("builtins.input", side_effect=["  ", "Australia"]):
            with patch("builtins.print") as imprimir:
                carrera = leer_seleccion(
                    "Carrera: ",
                    ["Australia"],
                    "carrera",
                )

        self.assertEqual(carrera, "Australia")
        imprimir.assert_called_once_with("Error: este campo no puede estar vacio.")

    def test_opcion_volver_no_se_compara_como_equipo(self):
        with patch("builtins.input", return_value="0"):
            equipo = leer_seleccion(
                "Equipo: ",
                ["McLaren"],
                "equipo",
                opcion_volver="0",
            )

        self.assertIsNone(equipo)

    def test_sin_opciones_disponibles_informa_error(self):
        with self.assertRaisesRegex(ValueError, "No hay opciones de carrera"):
            leer_seleccion("Carrera: ", [], "carrera")


if __name__ == "__main__":
    unittest.main()
