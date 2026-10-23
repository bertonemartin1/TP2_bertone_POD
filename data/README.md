# Datos CSV

Este directorio contiene los tres archivos CSV de resultados de Fórmula 1 de
la temporada 2025 usados por la aplicación:

- `f1_2025_race_results.csv`: una fila por piloto y Gran Premio.

- `f1_2025_drivers_standings.csv`: clasificación final de pilotos, con
  posición, nombre/código del piloto, nacionalidad, constructor y puntos.

- `f1_2025_teams_standings.csv`: clasificación final de constructores, con
  posición, nombre del constructor y puntos.

## Procedencia y fecha de consulta

Los archivos proceden del conjunto
[F1 2025 Season Results: Races, Drivers, Teams](https://www.kaggle.com/datasets/jamieeeee/f1-2025-season-results-races-drivers-teams),
publicado en Kaggle por Jamie J (`jamieeeee`). La ficha reconoce como fuente
al [sitio oficial de Fórmula 1](https://www.formula1.com/). La ficha y su
atribución se consultaron el 23/10/2026; la versión 1 muestra como fecha de
última modificación el 28/01/2026. No se dispone de una fecha verificable de
descarga local de los archivos.

La licencia indicada por el conjunto es
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

## Variables y significado

Las unidades son las declaradas o representadas en los archivos originales;
no se convierten a otras unidades.

### `f1_2025_race_results.csv` y `.json`

Cada observación representa el resultado de un piloto en un Gran Premio.

| Variable | Significado y unidad |
|---|---|
| `race` | Nombre del Gran Premio; categoría, sin unidad. |
| `position` | Posición de llegada, como entero ordinal. `NC` indica no clasificado y `DQ`, descalificado; estos estados no son posiciones numéricas. |
| `driver_number` | Número identificador del piloto durante la temporada; no es una magnitud. |
| `driver` | Nombre del piloto concatenado con su código identificador de tres letras; texto. La transformación elimina ese sufijo para mostrar el nombre. |
| `team` | Nombre del constructor/equipo; categoría, sin unidad. |
| `laps` | Vueltas completadas; conteo entero de vueltas. Puede estar vacío en el dato original cuando no se informa. |
| `time` | Tiempo o diferencia respecto del ganador, tal como lo publica la fuente. El ganador aparece con tiempo total y otros pilotos con una diferencia que puede llevar el sufijo `s` (segundos); la aplicación conserva este texto y no calcula ni normaliza tiempos. |
| `points` | Puntos obtenidos en el Gran Premio; puntos de campeonato. |

### Clasificaciones finales

En `f1_2025_drivers_standings.csv`, cada fila representa un piloto; en
`f1_2025_teams_standings.csv`, cada fila representa un constructor.

| Variable | Significado y unidad |
|---|---|
| `position` | Puesto final en la clasificación; entero ordinal, sin unidad física. |
| `driver` | En la clasificación de pilotos, nombre concatenado con el código identificador de tres letras. |
| `nationality` | En la clasificación de pilotos, código de nacionalidad de tres letras. |
| `team` | Constructor/equipo asociado al piloto o clasificado en la tabla de constructores; texto. |
| `points` | Puntos finales de campeonato acumulados; puntos de campeonato. |

Los archivos se mantienen como fuente original. `src/transformaciones.py` los
carga y transforma en memoria; por ejemplo, normaliza los nombres de pilotos
quitando su sufijo de tres letras y, por defecto, elimina la columna `driver`
de los resultados por carrera. Los análisis individuales pueden solicitar que
esa columna se conserve.

Además, `f1_2025_race_results.json` es la representación JSON equivalente a
`f1_2025_race_results.csv`: contiene una lista de objetos con las mismas claves,
valores y orden de filas. `src/fuentes.py` carga CSV y JSON como DataFrames, y
`src/transformaciones.py` aplica las mismas transformaciones a ambos formatos.
La aplicación utiliza este JSON para los resultados por carrera y conserva los
CSV de clasificaciones de pilotos y constructores.

Antes de analizarse, cada archivo se valida con el esquema correspondiente.
Los errores estructurales (por ejemplo, columnas obligatorias ausentes o un
archivo que no se puede interpretar) detienen la operación. Los errores
localizados se informan en consola con el número de registro desde 1 (en CSV
no se cuenta el encabezado; en JSON se usa el orden de los objetos de la lista)
y su motivo. Las filas con campos obligatorios vacíos, puntos o valores enteros
inválidos, posiciones de carrera no admitidas, vueltas inválidas o claves
duplicadas se excluyen; para claves duplicadas se conserva la primera fila
válida. El detalle también queda disponible en
`DataFrame.attrs["rechazos"]` durante la ejecución. No se modifica ningún CSV o
JSON ni se escribe un archivo de rechazos.
