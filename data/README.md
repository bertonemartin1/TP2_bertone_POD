# Datos CSV

Este directorio contiene los tres archivos CSV de resultados de Fórmula 1 de
la temporada 2025 usados por la aplicación:

- `f1_2025_race_results.csv`: una fila por piloto y Gran Premio, con carrera,
  posición, número y código del piloto, constructor, vueltas, tiempo y puntos.

- `f1_2025_drivers_standings.csv`: clasificación final de pilotos, con
  posición, nombre/código del piloto, nacionalidad, constructor y puntos.

- `f1_2025_teams_standings.csv`: clasificación final de constructores, con
  posición, nombre del constructor y puntos.

Los archivos se mantienen como fuente original. `src/transformaciones.py` los
carga y transforma en memoria; por ejemplo, normaliza los nombres de pilotos
quitando su sufijo de tres letras y, por defecto, elimina la columna `driver`
de los resultados por carrera. Los análisis individuales pueden solicitar que
esa columna se conserve.
