# 📊 Visor de Atractividad Territorial – Pipeline de Procesamiento y Visualización

## Descripción general del proyecto

Este proyecto implementa un pipeline completo de procesamiento, análisis y visualización de indicadores territoriales orientado al estudio de la atractividad de los municipios de la Comunidad de Madrid.

El sistema parte de datos estadísticos abiertos organizados en bloques temáticos (educación, economía, salud, vivienda y transporte). Cada bloque se procesa de forma independiente mediante notebooks de Jupyter, generando indicadores parciales que posteriormente se unifican y normalizan por clúster poblacional.

Los resultados finales se exponen a través de una aplicación web interactiva desarrollada con Flask, que permite el análisis comparativo entre municipios, el estudio por clústeres poblacionales y la recomendación de municipios en función de preferencias.

El proyecto está diseñado como una prueba de concepto reproducible, donde todo el flujo de ejecución puede lanzarse automáticamente mediante un único script Bash.

---

## Arquitectura del pipeline

El pipeline se estructura en las siguientes fases:

1. Cálculo de indicadores temáticos mediante notebooks independientes.  
2. Unificación de los resultados parciales en un único dataset.  
3. Normalización final de las variables por clúster poblacional.  
4. Generación de geometrías municipales en formato GeoJSON.  
5. Visualización interactiva mediante una aplicación web Flask.  

---

## Requisitos del sistema

- Python 3.9 o superior  
- pip  
- Jupyter Notebook y nbconvert  
- Sistema operativo Linux o macOS (o WSL en Windows)  

Principales librerías utilizadas:

- pandas  
- numpy  
- geopandas  
- shapely  
- flask  
- matplotlib  
- seaborn  
- scikit-learn  

---

## Estructura del proyecto

    ├── notebooks/
    │   ├── economy_final.ipynb
    │   ├── education_final.ipynb
    │   ├── health_final.ipynb
    │   ├── housing_final.ipynb
    │   ├── transport_final.ipynb
    │   └── normalizacion_final_2024.ipynb
    │
    ├── data/
    │   ├── external_data/
    │   ├── processed/
    │   └── data_interfaz/
    │
    ├── join.py
    ├── geometrias-municipios.py
    ├── app.py
    ├── run_pipeline.sh
    └── README.md

---

## Ejecución del proyecto

La ejecución completa del proyecto se realiza mediante el script `run_pipeline.sh`, que automatiza todas las fases del pipeline, desde el cálculo de indicadores hasta el lanzamiento de la interfaz web.

Antes de ejecutar el script es necesario conceder permisos de ejecución:

    chmod +x run_pipeline.sh

---

## Proceso de ejecución automatizado

### Generación de dependencias

El pipeline comienza generando automáticamente un fichero `requirements.txt` que contiene todas las dependencias del entorno de ejecución:

    pip freeze > requirements.txt

Este fichero permite reproducir exactamente el entorno en otros sistemas.

---

### Ejecución de notebooks temáticos

Se ejecutan de forma secuencial los notebooks correspondientes a los bloques temáticos:

- economy_final.ipynb  
- education_final.ipynb  
- health_final.ipynb  
- housing_final.ipynb  
- transport_final.ipynb  

Cada notebook realiza las siguientes tareas:

- Carga de los datos de entrada  
- Cálculo de los indicadores del bloque temático  
- Exportación de los resultados intermedios  

Ejecución automática:

    jupyter nbconvert --to notebook --execute notebook.ipynb --output notebook_out.ipynb

Si alguno de los notebooks produce un error, el pipeline se detiene automáticamente.

---

### Unificación de datasets

Una vez calculados todos los bloques temáticos, se ejecuta el script `join.py`, encargado de:

- Unificar los resultados de todos los bloques  
- Eliminar columnas auxiliares o duplicadas  
- Generar un dataset consolidado  

Ejecución:

    python3 join.py

---

### Normalización final

Tras la unificación, se ejecuta el notebook de normalización final correspondiente al año 2024:

    jupyter nbconvert --to notebook --execute normalizacion_final_2024.ipynb --output normalizacion_final_2024_out.ipynb

Este paso genera el dataset definitivo que será consumido por la interfaz web.

---

### Generación de geometrías municipales

Se generan los ficheros GeoJSON de los municipios mediante el script `geometrias-municipios.py`, utilizando el sistema de referencia EPSG:4326, adecuado para su uso en mapas web:

    python3 geometrias-municipios.py

---

### Lanzamiento de la interfaz web

Finalmente, se lanza la aplicación web desarrollada con Flask:

    python3 app.py

La aplicación queda disponible en el navegador en la dirección:

    http://127.0.0.1:5000

---

## Ejecución completa en un único comando

Para ejecutar todo el pipeline de principio a fin (cálculo, normalización, geometrías y visualización):

    ./run_pipeline.sh

---

## Consideraciones finales

- Pipeline completamente automatizado y reproducible  
- Arquitectura modular y fácilmente extensible  
- Separación clara entre cálculo de indicadores y visualización  
- Preparado para futuras extensiones RDF, DCAT y GeoDCAT  
