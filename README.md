# ETL_process_manager

Gestor de procesos ETL para extraer entidades nombradas de noticias.

## Uso
./run.sh ruta/al/archivo.csv

## Proceso

### Extract
Lee un CSV con las columnas:
- fecha
- medio
- reportero
- noticia

### Transform
- Limpieza del texto
- Extracción de entidades nombradas
- Resumen (summary) generado con un LLM

### Load
Guarda en la BD:
- fecha
- medio
- texto
- summary
- entidades nombradas
