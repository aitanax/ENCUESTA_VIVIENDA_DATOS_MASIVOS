from pathlib import Path
import pandas as pd

# Carpeta donde tienes los CSV (ajusta si hace falta)
INPUT_DIR = Path("data/vivienda/datos_filtrados_1")          # o la carpeta que tengas
OUTPUT_DIR = Path("data/vivienda/datos_filtrados_11")

# Columnas que quieres conservar (en este orden)
KEEP_COLS = [
    "municipality",
    "precio",
    "banos",
    "habitaciones",
    "propertyCode",
    "url",
]


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(INPUT_DIR.glob("*.csv"))
if not csv_files:
    raise SystemExit(f"No encuentro CSVs en: {INPUT_DIR.resolve()}")

for csv_path in csv_files:
    df = pd.read_csv(csv_path)

    # Nos quedamos solo con las columnas que existan en ese archivo
    cols_presentes = [c for c in KEEP_COLS if c in df.columns]
    df2 = df[cols_presentes].copy()

    # (Opcional) renombrar a español
    rename_map = {
        "municipality": "municipio",
        "precio": "precio",
        "banos": "banos",
        "habitaciones": "habitaciones",
        "propertyCode": "propertyCode",
        "url": "url",
    }
    df2 = df2.rename(columns=rename_map)

    out_path = OUTPUT_DIR / csv_path.name
    df2.to_csv(out_path, index=False)

print(f"✅ Listo. CSV filtrados en: {OUTPUT_DIR.resolve()}")
