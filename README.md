# Análisis de Fórmula 1: temporada 2025

**Autor:** `bertonemartin1`

Aplicación de consola para explorar y comparar los resultados de los Grandes
Premios de Fórmula 1 de la temporada 2025.

## Problema, usuario y solución

Los resultados de una temporada se distribuyen entre clasificaciones y datos
por carrera, lo que dificulta comparar rápidamente el desempeño de pilotos y
constructores. La aplicación está dirigida a personas interesadas en consultar
esos resultados sin procesar manualmente los archivos CSV.

La solución carga los datos locales, los valida y transforma en memoria, y
presenta tablas y gráficos mediante un menú interactivo.

## Funcionalidades

- Consultar la clasificación final del campeonato de constructores y la
  evolución de sus puntos por Gran Premio.
- Comparar los puntos y las posiciones promedio de los constructores en una
  carrera.
- Consultar la clasificación final del campeonato de pilotos y la evolución
  de sus puntos por Gran Premio.
- Comparar los resultados de los pilotos en una carrera.
- Consultar la evolución carrera a carrera de un piloto, incluidos los casos
  en que no participó.
- Comparar entre sí a los pilotos de un equipo durante la temporada (H2H),
  incluyendo cambios de piloto y carreras sin participación.
- Mostrar carreras, pilotos y equipos disponibles antes de solicitar una
  selección. Las entradas se validan y los errores se informan al usuario.

## Datos y unidad de análisis

Los CSV incluidos en `data/` provienen del conjunto
[F1 2025 Season Results: Races, Drivers, Teams](https://www.kaggle.com/datasets/jamieeeee/f1-2025-season-results-races-drivers-teams).
La licencia indicada para ese conjunto de datos es
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
Esta licencia corresponde a los datos citados; el repositorio no declara una
licencia independiente para el código.

Archivos utilizados:

- `f1_2025_race_results.csv`: resultados de pilotos por carrera.
- `f1_2025_drivers_standings.csv`: clasificación final de pilotos.
- `f1_2025_teams_standings.csv`: clasificación final de constructores.

La unidad de análisis elemental de los resultados es el resultado de un piloto
en un Gran Premio. Las comparaciones agregan esos registros por carrera,
piloto o constructor. Las clasificaciones finales se toman de los archivos de
standings incluidos en el conjunto de datos.

## Instalación

Se requiere Python 3.10 o superior. Desde PowerShell, ubicado en la raíz del
repositorio:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si se usa otra versión instalada de Python 3.10 o superior, se puede crear el
entorno con `python -m venv .venv` en lugar de `py -3.10 -m venv .venv`.

## Uso

Desde la raíz del repositorio y con el entorno virtual activado:

```powershell
python src\main.py
```

En el menú principal, selecciona `1` para comparaciones de constructores, `2`
para comparaciones de pilotos, `3` para H2H por equipo o `0` para salir. En los
submenús, selecciona el análisis deseado y escribe la carrera, el piloto o el
equipo solicitado. Los nombres admiten diferencias entre mayúsculas y
minúsculas; el programa muestra las opciones disponibles para facilitar la
selección.

## Pruebas

Las pruebas automatizadas se ejecutan desde la raíz del repositorio, con las
dependencias instaladas:

```powershell
python -m unittest discover -s tests -v
```

La suite comprueba la transformación de resultados y la normalización de
nombres de pilotos.

## Organización del código

```text
.
├── data/
│   ├── README.md
│   ├── f1_2025_drivers_standings.csv
│   ├── f1_2025_race_results.csv
│   └── f1_2025_teams_standings.csv
├── src/
│   ├── comparaciones.py
│   ├── graficos.py
│   ├── main.py
│   ├── menus.py
│   └── transformaciones.py
├── tests/
│   └── test_transformaciones.py
├── .gitignore
├── README.md
└── requirements.txt
```

- `main.py` inicia la aplicación.
- `menus.py` presenta los menús y recoge las entradas.
- `comparaciones.py` valida y procesa datos para las comparaciones.
- `graficos.py` construye los gráficos.
- `transformaciones.py` carga y limpia los CSV en memoria.
- `tests/` contiene las pruebas automatizadas.
- `.gitignore` excluye cachés, entornos virtuales y archivos locales de
  desarrollo; los CSV de `data/` no se excluyen y forman parte del proyecto.

## Ejemplo de resultado

La consulta de campeonato de constructores presenta una tabla como la
siguiente, basada en `f1_2025_teams_standings.csv`:

| Posición | Constructor | Puntos |
|---:|---|---:|
| 1 | McLaren | 833 |
| 2 | Mercedes | 469 |
| 3 | Red Bull Racing | 451 |

Además de la tabla, la aplicación abre un gráfico con la evolución de puntos
acumulados por carrera.

## Decisiones de limpieza

- Los archivos originales no se modifican: las transformaciones se realizan
  en memoria.
- Se eliminan espacios al inicio y al final de los campos de texto y se
  comprueba que los campos requeridos no estén vacíos.
- Los nombres de pilotos se normalizan quitando sus tres letras finales, que
  corresponden al sufijo de identificación del conjunto de datos.
- Por defecto, la transformación de resultados de carrera elimina la columna
  `driver`; los análisis individuales la solicitan explícitamente y conservan
  el nombre normalizado.
- Los puntos se convierten a números y se rechazan si están vacíos, no son
  numéricos o son negativos. Las posiciones se convierten a números cuando el
  análisis las necesita; las posiciones no numéricas no se consideran para
  promedios ni ordenamientos numéricos.

## Interpretación y limitaciones

- Las tablas de campeonatos reproducen las clasificaciones finales incluidas
  en el conjunto; las curvas acumuladas se calculan sumando los puntos de los
  resultados por carrera.
- El conjunto y las comparaciones descritas corresponden a Grandes Premios.
  No se calculan resultados de Sprint.
- Una posición promedio se calcula solo con posiciones numéricas. Si un
  constructor o piloto no tiene ninguna, se informa que no hay posición
  numérica y no se le asigna un valor estimado.
- El H2H compara los pilotos que aparecen asociados al equipo en los datos de
  la temporada. Los cambios de piloto se muestran como ausencia de
  participación en las carreras en las que ese piloto no figura.
- La cobertura, exactitud y granularidad del análisis dependen de los CSV
  incluidos; la aplicación no consulta datos externos ni actualiza la
  temporada automáticamente.
