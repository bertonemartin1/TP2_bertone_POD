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


def leer_seleccion(
    mensaje: str,
    opciones_validas: list[str],
    tipo: str,
    *,
    opcion_volver: str | None = None,
) -> str | None:
    if not opciones_validas:
        raise ValueError(f"No hay opciones de {tipo} disponibles para seleccionar.")

    opciones_por_nombre = {
        opcion.casefold(): opcion for opcion in opciones_validas
    }
    while True:
        entrada = leer_texto(mensaje)
        if (
            opcion_volver is not None
            and entrada.casefold() == opcion_volver.casefold()
        ):
            return None

        opcion = opciones_por_nombre.get(entrada.casefold())
        if opcion is not None:
            return opcion

        disponibles = ", ".join(opciones_validas)
        print(
            f"Error: {tipo} '{entrada}' no válido. "
            f"Opciones disponibles: {disponibles}."
        )


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
            carreras = obtener_carreras_disponibles()
            print("\nCarreras disponibles:")
            for carrera_disponible in carreras:
                print(f"- {carrera_disponible}")
            carrera = leer_seleccion("Ingrese la carrera: ", carreras, "carrera")
            if carrera is None:
                continue
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
            carreras = obtener_carreras_disponibles()
            print("\nCarreras disponibles:")
            for carrera_disponible in carreras:
                print(f"- {carrera_disponible}")
            carrera = leer_seleccion("Ingrese la carrera: ", carreras, "carrera")
            if carrera is None:
                continue
            comparar_pilotos_por_carrera(carrera)
        elif opcion == 3:
            pilotos = obtener_nombres_pilotos()
            print("\nPilotos disponibles:")
            for nombre in pilotos:
                print(f"- {nombre}")
            piloto = leer_seleccion(
                "Ingrese el nombre del piloto: ",
                pilotos,
                "piloto",
            )
            if piloto is None:
                continue
            comparar_piloto_temporada(piloto)


def menu_h2h():
    while True:
        equipos = obtener_equipos_disponibles()
        print("\nEquipos disponibles:")
        for equipo_disponible in equipos:
            print(f"- {equipo_disponible}")
        equipo = leer_seleccion(
            "\nIngrese el equipo para la comparacion h2h "
            "(o 0 para volver): ",
            equipos,
            "equipo",
            opcion_volver="0",
        )
        if equipo is None:
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
