import pandas as pd
import glob
import os
from collections import defaultdict

def combinar_csvs_por_anio(base_folder, output_prefix):
    # Buscar todos los archivos CSV recursivamente
    csv_files = glob.glob(os.path.join(base_folder, "**", "*.csv"), recursive=True)

    if not csv_files:
        print(f"No se encontraron CSVs en {base_folder}")
        return

    print(f"🧩 Encontrados {len(csv_files)} archivos CSV en total")

    # Agrupar los archivos por año detectado en la ruta
    archivos_por_anio = defaultdict(list)
    for file in csv_files:
        # Detectar año en la ruta (ej: .../2024/Precio.csv → año = 2024)
        partes = file.replace("\\", "/").split("/")
        anio = next((p for p in partes if p in ["2023", "2024", "2025"]), None)
        if anio:
            archivos_por_anio[anio].append(file)

    # Procesar por año
    for anio, archivos in archivos_por_anio.items():
        print(f"\n📁 Procesando año {anio} con {len(archivos)} archivos...")

        dataframes = []
        for file in archivos:
            try:
                df = pd.read_csv(file)
                dataframes.append(df)
            except Exception as e:
                print(f"⚠️ Error leyendo {file}: {e}")

        if not dataframes:
            print(f"⚠️ No se pudieron cargar CSVs para el año {anio}")
            continue

        # Merge por "Nombre"
        df_final = dataframes[0]
        for df in dataframes[1:]:
            df_final = pd.merge(df_final, df, on="Nombre", how="outer")

        # Guardar resultado
        output_file = f"{output_prefix}_{anio}.csv"
        df_final.to_csv(output_file, index=False)
        print(f"✅ Archivo combinado para {anio} guardado en: {output_file}")

# USO
combinar_csvs_por_anio(
    base_folder="data_interfaz",
    output_prefix="data_interfaz/clusterAtractividadJuntos"
)
