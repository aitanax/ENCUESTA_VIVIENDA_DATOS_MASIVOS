#!/bin/bash

echo "=========================================="
echo "🚀 INICIO DEL PIPELINE DE EJECUCIÓN"
echo "=========================================="

# Crear requirements.txt (opcional, se puede mover al final)
pip freeze > requirements.txt

# Paso 1: Ejecutar notebooks de bloques temáticos
echo "📚 Ejecutando notebooks de bloques temáticos..."

notebooks=(
    "economy_final.ipynb"
    "education_final.ipynb"
    "health_final.ipynb"
    "housing_final.ipynb"
    "transport_final.ipynb"
)

for nb in "${notebooks[@]}"; do
    echo "🧠 Ejecutando $nb"
    jupyter nbconvert --to notebook --execute "$nb" --output "${nb%.ipynb}_out.ipynb"
    if [ $? -ne 0 ]; then
        echo "❌ Error en $nb. Abortando."
        exit 1
    fi
done

# Paso 2: Ejecutar join.py
echo "🧩 Unificando datasets con join.py..."
python3 join.py
if [ $? -ne 0 ]; then
    echo "❌ Error al ejecutar join.py"
    exit 1
fi

# Paso 3: Ejecutar normalización
echo "📊 Ejecutando normalización final..."
jupyter nbconvert --to notebook --execute "normalizacion_final_2024.ipynb" --output "normalizacion_final_2024_out.ipynb"
if [ $? -ne 0 ]; then
    echo "❌ Error en normalizacion_final_2024.ipynb"
    exit 1
fi

# Paso 4: Generar geometrías GeoJSON en EPSG:4326
echo "🗺️ Generando geometrías de municipios (EPSG:4326)..."
python3 geometrias-municipios.py
if [ $? -ne 0 ]; then
    echo "❌ Error al generar geometrías"
    exit 1
fi

# Paso 5: Lanzar interfaz web Flask
echo "🌐 Lanzando la interfaz web..."
python3 app.py
