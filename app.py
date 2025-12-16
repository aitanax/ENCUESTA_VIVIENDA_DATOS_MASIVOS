from flask import Flask, render_template, request
import pandas as pd
import os
import json
import plotly.graph_objs as go
import plotly.express as px
import plotly
import re
import unicodedata
import geopandas as gpd

# Rutas
CSV_PATH = os.path.join("data_interfaz", "valores.csv")
GEOJSON_PATH = os.path.join("static", "municipios_madrid_4326.geojson")

gdf = gpd.read_file("static/municipios_madrid.geojson")
# Transformar a WGS84
gdf = gdf.to_crs(epsg=4326)
# Guardar nuevo GeoJSON proyectado
gdf.to_file("static/municipios_madrid_4326.geojson", driver="GeoJSON")

# Inicializar Flask
app = Flask(__name__)

# Cargar datos
df = pd.read_csv(CSV_PATH)
with open(GEOJSON_PATH, encoding="utf-8") as f:
    geojson_data = json.load(f)

# Función de normalización
def normalizar(nombre):
    if not isinstance(nombre, str):
        return ""
    nombre = nombre.lower().strip()
    nombre = unicodedata.normalize("NFD", nombre)
    nombre = "".join(c for c in nombre if unicodedata.category(c) != "Mn")
    match = re.search(r"\((el|la|los|las)\)$", nombre)
    if match:
        articulo = match.group(1)
        nombre = re.sub(r"\s*\((el|la|los|las)\)$", "", nombre)
        nombre = f"{articulo} {nombre}"
    nombre = re.sub(r"\s+", " ", nombre)
    return nombre

# Añadir campo ETIQUETA_NORM al GeoJSON
for f in geojson_data["features"]:
    f["properties"]["ETIQUETA_NORM"] = normalizar(f["properties"]["ETIQUETA"])

# Verificación de nombres
df_verificacion = df.copy()
df_verificacion["nombre_norm"] = df_verificacion["Nombre"].apply(normalizar)

geojson_nombres = set(
    f["properties"]["ETIQUETA_NORM"] for f in geojson_data["features"]
)

df_verificacion["coincide_con_geojson"] = df_verificacion["nombre_norm"].apply(
    lambda x: "✅ SÍ" if x in geojson_nombres else "❌ NO"
)

df_verificacion[["Nombre", "nombre_norm", "coincide_con_geojson"]].to_csv(
    "external_data/verificacion_nombres.csv", index=False
)

# Etiquetas para clústeres
CLUSTER_LABELS = {"1.0": "Poca población", "2.0": "Media población", "3.0": "Mucha población"}

# ---------------------- RUTAS -------------------------

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/estudio_cluster", methods=["GET", "POST"])
def estudio_cluster():
    if request.method == "GET":
        clusters = sorted(df["grupo"].dropna().unique())
        cluster_labels = [(c, CLUSTER_LABELS.get(str(c), str(c))) for c in clusters]
        return render_template("estudio_cluster.html", clusters=cluster_labels)

    # -------------------------
    # 1️⃣ POST: cluster elegido
    # -------------------------
    cluster = request.form.get("cluster")

    df_cluster = df[df["grupo"].astype(str) == cluster].copy()

    # -------------------------
    # 2️⃣ Normalizar nombres CSV
    # -------------------------
    df_cluster["nombre_norm"] = df_cluster["Nombre"].apply(normalizar)

    print("\n🧾 EJEMPLOS CSV normalizados:")
    print(df_cluster[["Nombre", "nombre_norm"]].head(10))

    # -------------------------
    # 3️⃣ Nombres GeoJSON
    # -------------------------
    geojson_nombres = set(
        f["properties"]["ETIQUETA_NORM"] for f in geojson_data["features"]
    )

    df_cluster_filtrado = df_cluster[
        df_cluster["nombre_norm"].isin(geojson_nombres)
    ]

    print("COINCIDENCIAS CSV ↔ GEOJSON:", len(df_cluster_filtrado))

    if df_cluster_filtrado.empty:
        print(" NO HAY COINCIDENCIAS — se usará fallback (SIN MAPA REAL)")
        df_cluster_filtrado = df_cluster
    else:
        print("PRIMERAS COINCIDENCIAS:")
        print(df_cluster_filtrado[["Nombre", "nombre_norm", "mean_per_row"]].head())



    fig = px.choropleth_mapbox(
        df_cluster_filtrado,
        geojson=geojson_data,
        locations="nombre_norm",
        featureidkey="properties.ETIQUETA_NORM",
        color="mean_per_row",
        center={"lat": 40.4168, "lon": -3.7038},
        mapbox_style="carto-positron",
        zoom=8,
        opacity=0.6,
        labels={"mean_per_row": "Índice medio"}
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


    grafico_json = fig.to_json()

    return render_template(
        "resultado_cluster.html",
        cluster=CLUSTER_LABELS.get(cluster, cluster),
        datos=df_cluster.to_dict(orient="records"),
        grafico=grafico_json
    )

DATA_PATH = os.path.join("data_interfaz", "valores.csv")
df = pd.read_csv(DATA_PATH)

def crear_boxplot_municipio(df, datos):
    dimensiones = ["educacion", "salud", "transporte", "economia", "housing"]
    fig = go.Figure()

    for dim in dimensiones:
        # Boxplot del conjunto
        fig.add_trace(go.Box(
            y=df[dim],
            name=dim.capitalize(),
            boxpoints=False,
            marker_color="lightgray"
        ))

        # Punto del municipio seleccionado
        fig.add_trace(go.Scatter(
            x=[dim.capitalize()],
            y=[datos[dim]],
            mode="markers",
            marker=dict(color="red", size=10),
            name=datos["Nombre"],
            showlegend=False
        ))

    fig.update_layout(
        title="📦 Valor de atractividad del municipio para los diferentes bloques",
        yaxis_title="Valor normalizado",
        xaxis_title="Dimensión",
        height=500
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_resultados(resultados):
    nombres = [r["Nombre"] for r in resultados]
    dimensiones = ["educacion", "salud", "transporte", "economia", "housing"]
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    data = []
    for i, dim in enumerate(dimensiones):
        data.append(go.Bar(
            name=dim.capitalize(),
            x=nombres,
            y=[r[dim] for r in resultados],
            marker=dict(color=colores[i])
        ))

    layout = go.Layout(
        barmode="group",
        title="Comparativa por dimensión",
        yaxis=dict(title="Valor normalizado"),
        xaxis=dict(title="Municipios")
    )

    fig = go.Figure(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.route("/recomendador", methods=["GET", "POST"])
def recomendador():
    if request.method == "GET":
        return render_template("recomendador.html")

    # 1. Recoger respuestas del usuario
    educacion = int(request.form.get("educacion", 3))
    salud = int(request.form.get("salud", 3))
    transporte = int(request.form.get("transporte", 3))
    economia = int(request.form.get("economia", 3))
    housing = int(request.form.get("housing", 3))
    ocio = int(request.form.get("ocio", 3))
    entorno = request.form.get("entorno", "mixto")
    cluster = request.form.get("cluster", "2")

    # 2. Ajustar según ocio y entorno
    transporte += ocio // 2
    economia += ocio // 2

    if entorno == "urbano":
        cluster = "3"
    elif entorno == "natural":
        cluster = "1"

    # 3. Crear diccionario de preferencias
    preferencias = {
        "educacion": educacion,
        "salud": salud,
        "transporte": transporte,
        "economia": economia,
        "housing": housing,
    }

    # 4. Filtrar municipios por grupo
    df_local = df.copy()
    df_local = df[df["grupo"].astype(float) == float(cluster)]

    print(f"👉 Cluster seleccionado: {cluster}")
    print(f"📊 Municipios disponibles: {len(df_local)}")


    if df_local.empty:
        df_local = df.copy()

    # 5. Normalizar y calcular índice personalizado
    for dim in preferencias:
        min_val = df_local[dim].min()
        max_val = df_local[dim].max()
        if max_val != min_val:
            df_local[dim + "_norm"] = (df_local[dim] - min_val) / (max_val - min_val)
        else:
            df_local[dim + "_norm"] = 0.0

    total = sum(preferencias.values()) or 1.0
    df_local["indice_personalizado"] = sum(
        (preferencias[dim] / total) * df_local[dim + "_norm"] for dim in preferencias
    )

    # 6. Escoger un municipio por dimensión destacada (ordenando según preferencia)
    orden_bloques = sorted(preferencias.items(), key=lambda x: x[1], reverse=True)

    municipios_recomendados = []
    ya_elegidos = set()

    for bloque, _ in orden_bloques:
        mejor = df_local.sort_values(by=bloque, ascending=False)
        mejor = mejor[~mejor["Nombre"].isin(ya_elegidos)]
        if not mejor.empty:
            municipio = mejor.iloc[0].to_dict()
            municipio["destaca_en"] = bloque
            municipios_recomendados.append(municipio)
            ya_elegidos.add(municipio["Nombre"])
        if len(municipios_recomendados) == 3:
            break

    # ✅ Aquí estaba el error:
    grafico = crear_grafico_resultados(municipios_recomendados)
    return render_template("resultados.html", resultados=municipios_recomendados, grafico=grafico)


@app.route("/estudio_municipio", methods=["GET", "POST"])
def estudio_municipio():
    if request.method == "GET":
        nombres = sorted(df["Nombre"].dropna().unique())
        return render_template("estudio_municipio.html", municipios=nombres)

    municipio = request.form.get("municipio")
    datos = df[df["Nombre"] == municipio].iloc[0].to_dict()

    # Radar
    labels = ["educacion", "salud", "transporte", "economia", "housing"]
    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=[datos[l] for l in labels],
        theta=[l.capitalize() for l in labels],
        fill="toself"
    ))
    radar.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1])),
        title="Perfil del municipio"
    )

    radar_json = json.dumps(radar, cls=plotly.utils.PlotlyJSONEncoder)

    # Boxplot comparativo
    boxplot_json = crear_boxplot_municipio(df, datos)

    return render_template(
        "resultado_municipio.html",
        datos=datos,
        radar=radar_json,
        boxplot=boxplot_json
    )

if __name__ == "__main__":
    app.run(debug=True, port=5049)
