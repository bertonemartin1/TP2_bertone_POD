# Definicion de menus y funciones de entrada de datos.

from comparaciones import (
    comparar_campeonato_constructores,
    comparar_campeonato_pilotos,
    comparar_constructores_por_carrera,
    comparar_h2h_equipo,
    comparar_piloto_temporada,
    comparar_pilotos_por_carrera,
    obtener_carreras_disponibles,
    obtener_equipos_disponibles,
    obtener_nombres_pilotos,
)


def leer_opcion(mensaje: str, opciones_validas: tuple[int, ...]) -> int:
    while True:
        entrada = input(mensaje).strip()
        try:
            opcion = int(entrada)
        except ValueError:
            print("Error: debe ingresar un numero entero.")
            continue

        if opcion not in opciones_validas:
            opciones = ", ".join(str(opcion) for opcion in opciones_validas)
            print(f"Error: opcion no valida. Ingrese una de estas opciones: {opciones}.")
            continue
        return opcion


def leer_texto(mensaje: str) -> str:
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("Error: este campo no puede estar vacio.")


def menu_constructores():
    while True:
        print("\n--- Constructores ---")
        print("1. Campeonato")
        print("2. Carrera")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", (0, 1, 2))

        if opcion == 0:
            return
        if opcion == 1:
            comparar_campeonato_constructores()
        elif opcion == 2:
            print("\nCarreras disponibles:")
            for carrera_disponible in obtener_carreras_disponibles():
                print(f"- {carrera_disponible}")
            carrera = leer_texto("Ingrese la carrera: ")
            comparar_constructores_por_carrera(carrera)


def menu_pilotos():
    while True:
        print("\n--- Pilotos ---")
        print("1. Campeonato")
        print("2. Carrera")
        print("3. Piloto")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", (0, 1, 2, 3))

        if opcion == 0:
            return
        if opcion == 1:
            comparar_campeonato_pilotos()
        elif opcion == 2:
            print("\nCarreras disponibles:")
            for carrera_disponible in obtener_carreras_disponibles():
                print(f"- {carrera_disponible}")
            carrera = leer_texto("Ingrese la carrera: ")
            comparar_pilotos_por_carrera(carrera)
        elif opcion == 3:
            print("\nPilotos disponibles:")
            for nombre in obtener_nombres_pilotos():
                print(f"- {nombre}")
            piloto = leer_texto("Ingrese el nombre del piloto: ")
            comparar_piloto_temporada(piloto)


def menu_h2h():
    while True:
        print("\nEquipos disponibles:")
        for equipo_disponible in obtener_equipos_disponibles():
            print(f"- {equipo_disponible}")
        equipo = leer_texto(
            "\nIngrese el equipo para la comparacion h2h "
            "(o 0 para volver): "
        )
        if equipo == "0":
            return
        comparar_h2h_equipo(equipo)


def menu_principal():
    while True:
        print("\n=== Menu principal ===")
        print("1. Constructores")
        print("2. Pilotos")
        print("3. h2h")
        print("0. Salir")
        opcion = leer_opcion("Seleccione una opcion: ", (0, 1, 2, 3))

        if opcion == 0:
            print("Programa finalizado.")
            return
        if opcion == 1:
            menu_constructores()
        elif opcion == 2:
            menu_pilotos()
        elif opcion == 3:
            menu_h2h()
