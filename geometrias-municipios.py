import geopandas as gpd

# Ruta al shapefile
shp_path = "data/muni2024/muni2024.shp"

# Cargar shapefile
gdf = gpd.read_file(shp_path)

# Verifica qué columnas tiene
print(gdf.columns)

# Asegúrate de que haya una columna tipo "codigo" o "cod_mun"
# Si se llama distinto, renómbrala
gdf = gdf.rename(columns={"CODIGO": "codigo"})  # ajusta si se llama distinto

# Exportar a GeoJSON
gdf.to_file("static/municipios_madrid.geojson", driver="GeoJSON")
