import os, csv, re, base64, time
from pathlib import Path
import requests

# ==== Config ====
TOKEN_URL = "https://api.idealista.com/oauth/token"
SEARCH_URL = "https://api.idealista.com/3.5/es/search"

CLIENT_ID = os.getenv("IDEALISTA_CLIENT_ID")
CLIENT_SECRET = os.getenv("IDEALISTA_CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Faltan IDEALISTA_CLIENT_ID / IDEALISTA_CLIENT_SECRET")

MUNICIPIOS_CSV = "external_data/municipios_madrid.csv"
OUTPUT_DIR = Path("csv_municipios")

OPERATION = "buy"
PROPERTY_TYPE = "homes"
DISTANCE_METROS = 2000
MAX_ITEMS = 20
MAX_PAGINAS = 2

# Espera normal entre peticiones (cuando todo va bien)
SLEEP_OK = 1.0

# Progreso (para reanudar)
PROGRESO_FILE = Path("progreso_idealista.txt")

def slugify(s: str) -> str:
    s = s.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_\-ÁÉÍÓÚáéíóúÑñ]", "", s)

def get_access_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "scope": "read"}
    r = requests.post(TOKEN_URL, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def cargar_municipios():
    out = []
    with open(MUNICIPIOS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            m = row["Municipio"]
            lat = float(row["Latitud"].replace(",", "."))
            lon = float(row["Longitud"].replace(",", "."))
            out.append((m, lat, lon))
    return out

def abrir_csv(path: Path, fieldnames):
    existe = path.is_file()
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fieldnames)
    if not existe:
        w.writeheader()
        f.flush()
        os.fsync(f.fileno())
    return f, w

def guardar_progreso(i: int):
    PROGRESO_FILE.write_text(str(i), encoding="utf-8")

def leer_progreso() -> int:
    if PROGRESO_FILE.exists():
        try:
            return int(PROGRESO_FILE.read_text(encoding="utf-8").strip())
        except:
            return 0
    return 0

class RateLimited(Exception):
    def __init__(self, retry_after=None, text=None):
        self.retry_after = retry_after
        self.text = text
        super().__init__("Rate limited (429)")

def buscar_pagina(token, lat, lon, page):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "country": "es",
        "operation": OPERATION,
        "propertyType": PROPERTY_TYPE,
        "center": f"{lat},{lon}",
        "distance": DISTANCE_METROS,
        "numPage": page,
        "maxItems": MAX_ITEMS
    }
    r = requests.post(SEARCH_URL, headers=headers, data=data, timeout=30)

    if r.status_code == 429:
        retry_after = r.headers.get("Retry-After")
        raise RateLimited(retry_after=retry_after, text=r.text)

    r.raise_for_status()
    return r.json()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    start_idx = leer_progreso()
    municipios = cargar_municipios()

    print(f"Reanudando desde índice {start_idx} de {len(municipios)} municipios.")
    token = get_access_token()

    fieldnames = ["municipio", "propertyCode", "precio", "banos", "habitaciones",
                  "tamano_m2", "direccion", "barrio", "url"]

    for i in range(start_idx, len(municipios)):
        municipio, lat, lon = municipios[i]
        slug = slugify(municipio)
        csv_path = OUTPUT_DIR / f"{slug}.csv"

        # Guardamos progreso ANTES de empezar este municipio
        guardar_progreso(i)

        print(f"\n=== {municipio} === -> {csv_path}")

        f, w = abrir_csv(csv_path, fieldnames)
        try:
            for page in range(1, MAX_PAGINAS + 1):
                try:
                    data = buscar_pagina(token, lat, lon, page)
                except RateLimited as rl:
                    # Aquí paramos todo, para no quemar cuota
                    msg = f"\n[STOP] 429 Rate Limit. Idealista te está limitando o has agotado cuota."
                    if rl.retry_after:
                        msg += f" Retry-After={rl.retry_after} (segundos)."
                    print(msg)
                    print("Guardado progreso. Cuando tengas cuota, vuelve a ejecutar el script y seguirá donde lo dejó.")
                    return

                elems = data.get("elementList", [])
                total = data.get("total", 0)
                print(f"  Página {page}: {len(elems)} (total API: {total})")

                if not elems:
                    break

                for e in elems:
                    row = {
                        "municipio": municipio,
                        "propertyCode": e.get("propertyCode", ""),
                        "precio": e.get("price", ""),
                        "banos": e.get("bathrooms", ""),
                        "habitaciones": e.get("rooms", e.get("bedrooms", "")),
                        "tamano_m2": e.get("size", ""),
                        "direccion": e.get("address", ""),
                        "barrio": e.get("neighborhood", ""),
                        "url": e.get("url", ""),
                    }
                    w.writerow(row)
                    f.flush()
                    os.fsync(f.fileno())

                if len(elems) < MAX_ITEMS:
                    break

                time.sleep(SLEEP_OK)

        finally:
            f.close()

    # Si acabó todo, ponemos progreso al final
    guardar_progreso(len(municipios))
    print("\n✅ Terminado. Todos los municipios procesados.")

if __name__ == "__main__":
    main()
