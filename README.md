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
El conjunto fue publicado en Kaggle por Jamie J (`jamieeeee`), quien reconoce
como fuente al sitio oficial de Fórmula 1. La ficha del conjunto se consultó el
23/10/2026; la versión publicada allí indica como última modificación el
28/01/2026.
La licencia indicada para ese conjunto de datos es
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
Esta licencia corresponde a los datos citados; el repositorio no declara una
licencia independiente para el código.

Archivos utilizados:

- `f1_2025_race_results.csv`: resultados de pilotos por carrera en CSV.
- `f1_2025_race_results.json`: los mismos resultados de carrera en JSON; la
  aplicación usa esta representación para demostrar la carga JSON.
- `f1_2025_drivers_standings.csv`: clasificación final de pilotos.
- `f1_2025_teams_standings.csv`: clasificación final de constructores.

La unidad de análisis elemental de los resultados es el resultado de un piloto
en un Gran Premio. Las comparaciones agregan esos registros por carrera,
piloto o constructor. Las clasificaciones finales se toman de los archivos de
standings incluidos en el conjunto de datos. El JSON de resultados contiene una
lista de objetos con las mismas columnas, filas y orden que su CSV equivalente.
La capa de fuentes carga ambos formatos como tablas, por lo que las
transformaciones y comparaciones no dependen de la extensión del archivo.
Las variables, su significado y las unidades disponibles se detallan en
[`data/README.md`](data/README.md).

En los resultados por carrera, `position` acepta una posición expresada con
dígitos o los estados `NC` (no clasificado) y `DQ` (descalificado). El validador
aplica `fullmatch(r"\d+|NC|DQ")` al texto sin espacios externos: `\d+` significa
uno o más dígitos, mientras que `NC` y `DQ` son alternativas literales en
mayúsculas. `fullmatch` exige que toda la cadena coincida, por lo que valores
como `P1`, `1.5`, `NC extra` o una cadena vacía se rechazan. Después, para las
coincidencias numéricas se convierte el valor a número y se exige que sea mayor
que cero; `NC` y `DQ` se conservan como estados y no participan como posiciones
numéricas en promedios u ordenamientos.

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

La aplicación valida cada fuente antes de usarla. Para ejecutar por separado el
validador e inspeccionar los CSV incluidos, ejecuta desde la raíz:

```powershell
python src\validaciones.py
```

## Pruebas

Las pruebas automatizadas se ejecutan desde la raíz del repositorio, con las
dependencias instaladas:

```powershell
python -m unittest discover -s tests -v
```

La suite usa datos sintéticos, archivos temporales y mocks para probar por
separado las fuentes, el validador, las transformaciones, el modelo y las
comparaciones, sin depender de los datos distribuidos en `data/`. Comprueba la
lectura y transformación equivalente de CSV/JSON, los errores estructurales,
los rechazos con fila y motivo, el manejo de entradas inválidas y que las
comparaciones produzcan las mismas tablas, orden y puntos acumulados con ambos
formatos. También cubre filas excluidas y carreras sin participación.
La validación descarta filas defectuosas identificando el número de registro
(desde 1; en CSV no se cuenta la fila de encabezado) y el motivo; muestra el
detalle en consola y lo conserva en
`DataFrame.attrs["rechazos"]`. Si todas las filas son rechazadas, la carga
lanza `DatosSinRegistrosValidosError` con el mismo detalle. Los errores de
esquema o lectura bloquean la operación.

## Organización del código

```text
.
├── data/
│   ├── README.md
│   ├── f1_2025_drivers_standings.csv
│   ├── f1_2025_race_results.csv
│   ├── f1_2025_race_results.json
│   └── f1_2025_teams_standings.csv
├── src/
│   ├── comparaciones.py
│   ├── fuentes.py
│   ├── graficos.py
│   ├── main.py
│   ├── modelos.py
│   ├── menus.py
│   ├── transformaciones.py
│   └── validaciones.py
├── tests/
│   ├── test_comparaciones.py
│   ├── test_fuentes.py
│   ├── test_menus.py
│   ├── test_modelos.py
│   ├── test_validaciones.py
│   └── test_transformaciones.py
├── .gitignore
├── README.md
└── requirements.txt
```

- `main.py` inicia la aplicación.
- `menus.py` presenta los menús y recoge las entradas.
- `comparaciones.py` valida y procesa datos para las comparaciones.
- `modelos.py` define `CampeonatoF1`, que representa una temporada de
  constructores o pilotos. Recibe la clasificación y los resultados ya
  transformados; ordena la clasificación, conserva el calendario, selecciona
  resultados de una carrera y calcula puntos acumulados completando con cero
  las ausencias. Centraliza el contexto de temporada compartido para que las
  comparaciones de campeonato no repitan esos cálculos sobre DataFrames sueltos.
- `fuentes.py` proporciona una interfaz de carga común para archivos CSV y
  JSON.
- `graficos.py` construye los gráficos.
- `transformaciones.py` carga CSV o JSON y aplica las limpiezas en memoria.
- `validaciones.py` comparte las reglas de validación entre CSV y JSON y
  distingue errores estructurales de errores por fila.
  Columnas requeridas ausentes, fuentes sin registros y archivos que no se
  pueden interpretar bloquean el análisis. Los registros con campos
  obligatorios vacíos, valores fuera de rango o claves duplicadas se excluyen
  con su fila (numerada desde 1, sin contar el encabezado CSV) y motivo; ante
  claves repetidas se conserva la primera fila válida.
- `tests/` contiene pruebas para las comparaciones, el modelo, la entrada de
  menús y las transformaciones.
- `.gitignore` excluye cachés, entornos virtuales y archivos locales de
  desarrollo; los archivos de datos de `data/` forman parte del proyecto.

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
