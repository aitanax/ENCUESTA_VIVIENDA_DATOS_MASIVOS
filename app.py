from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = os.path.join("data", "municipios_integrado.csv")
df = pd.read_csv(DATA_PATH)

DIMENSIONS = ["economia", "educacion", "sanidad", "transporte", "vivienda"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recomendador", methods=["GET", "POST"])
def recomendador():
    # --- PETICION GET: mostrar formulario con lista de clusters ---
    if request.method == "GET":
        # OJO: el nombre de la columna debe ser EXACTAMENTE "cluster_poblacion"
        if "cluster_poblacion" in df.columns:
            clusters = sorted(df["cluster_poblacion"].dropna().unique())
        else:
            # fallback por si acaso
            clusters = []
        return render_template("recomendador.html", clusters=clusters)

    # --- PETICION POST: procesar encuesta ---
    try:
        w_econ = float(request.form.get("economia", 1))
        w_edu = float(request.form.get("educacion", 1))
        w_san = float(request.form.get("sanidad", 1))
        w_tra = float(request.form.get("transporte", 1))
        w_viv = float(request.form.get("vivienda", 1))
    except ValueError:
        w_econ = w_edu = w_san = w_tra = w_viv = 1.0

    cluster_preferido = request.form.get("cluster", "cualquiera")

    pesos = {
        "economia": w_econ,
        "educacion": w_edu,
        "sanidad": w_san,
        "transporte": w_tra,
        "vivienda": w_viv,
    }

    df_local = df.copy()

    # Filtrado por cluster si el usuario ha elegido uno
    if cluster_preferido != "cualquiera" and "cluster_poblacion" in df_local.columns:
        df_local = df_local[df_local["cluster_poblacion"] == cluster_preferido]

    if df_local.empty:
        df_local = df.copy()

    # Normalizacion 0-1
    for dim in DIMENSIONS:
        if dim not in df_local.columns:
            raise ValueError(f"Falta la columna '{dim}' en el CSV integrado")
        min_val = df_local[dim].min()
        max_val = df_local[dim].max()
        if max_val != min_val:
            df_local[dim + "_norm"] = (df_local[dim] - min_val) / (max_val - min_val)
        else:
            df_local[dim + "_norm"] = 0.0

    total_pesos = sum(pesos.values()) or 1.0
    indice_personalizado = 0
    for dim in DIMENSIONS:
        w = pesos[dim] / total_pesos
        indice_personalizado += w * df_local[dim + "_norm"]

    df_local["indice_personalizado"] = indice_personalizado
    df_ordenado = df_local.sort_values(by="indice_personalizado", ascending=False)
    top_n = df_ordenado.head(10)
    resultados = top_n.to_dict(orient="records")

    # volvemos a mandar la lista completa de clusters por si quieres volver al formulario
    if "cluster_poblacion" in df.columns:
        clusters = sorted(df["cluster_poblacion"].dropna().unique())
    else:
        clusters = []

    return render_template(
        "resultados.html",
        resultados=resultados,
        pesos=pesos,
        cluster_preferido=cluster_preferido,
        clusters=clusters,
    )


if __name__ == "__main__":
    app.run(debug=True)
