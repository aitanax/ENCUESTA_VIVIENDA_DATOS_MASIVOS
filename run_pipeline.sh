#!/bin/bash

echo "=========================================="
echo "INICIO DEL PIPELINE DE EJECUCIÓN"
echo "=========================================="

# =========================
# CREAR ENTORNO VIRTUAL
# =========================
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
else
    echo "Entorno virtual ya existente."
fi

# =========================
# ACTIVAR ENTORNO
# =========================
echo "Activando entorno virtual..."
source venv/bin/activate

# =========================
# INSTALAR DEPENDENCIAS
# =========================
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install jupyter

# =========================
# EJECUTAR NOTEBOOKS
# =========================
echo "Ejecutando notebooks de bloques temáticos..."

notebooks=(
    "economy_final.ipynb"
    "education_final.ipynb"
    "health_final.ipynb"
    "housing_final.ipynb"
    "transport_final.ipynb"
)

for nb in "${notebooks[@]}"; do
    echo "Ejecutando $nb"
    jupyter nbconvert --to notebook --execute "$nb" --output "${nb%.ipynb}_out.ipynb"
    if [ $? -ne 0 ]; then
        echo "Error en $nb. Abortando."
        deactivate
        exit 1
    fi
done

# =========================
# JOIN DE DATASETS
# =========================
echo "Unificando datasets con join.py..."
python join.py
if [ $? -ne 0 ]; then
    echo "Error al ejecutar join.py"
    deactivate
    exit 1
fi

# =========================
# NORMALIZACIÓN FINAL
# =========================
echo "Ejecutando normalización final..."
jupyter nbconvert --to notebook --execute "normalizacion_final_2024.ipynb" \
    --output "normalizacion_final_2024_out.ipynb"

if [ $? -ne 0 ]; then
    echo "Error en normalizacion_final_2024.ipynb"
    deactivate
    exit 1
fi

# =========================
# GENERAR GEOMETRÍAS
# =========================
echo "Generando geometrías de municipios (EPSG:4326)..."
python geometrias-municipios.py
if [ $? -ne 0 ]; then
    echo "Error al generar geometrías"
    deactivate
    exit 1
fi

# =========================
# LANZAR FLASK
# =========================
echo "Lanzando la interfaz web..."
python app.py

# =========================
# LIMPIEZA
# =========================
deactivate
