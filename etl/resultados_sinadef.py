"""Homicidios SINADEF (MINSA) por mes y por ventana de 100 días.
La descarga oficial (files.minsa.gob.pe / datosabiertos.gob.pe) está detrás de
Cloudflare/WAF y no se deja bajar desde script; se usa el espejo diario público
github.com/JudithCristina/sinadef-automatizado, que baja el CSV oficial y filtra
MUERTE_VIOLENTA == 'HOMICIDIO' con necropsia realizada, ANIO >= 2017.
Uso: python3 -I resultados_sinadef.py <out.json>   (solo stdlib)"""
import csv, io, json, sys, urllib.request, collections
from datetime import date, timedelta
URL = "https://raw.githubusercontent.com/JudithCristina/sinadef-automatizado/main/data/processed/BASE_FINAL_GENERAL.csv"
raw = urllib.request.urlopen(URL, timeout=180).read().decode("utf-8-sig")
rows = list(csv.DictReader(io.StringIO(raw)))
fechas = [date.fromisoformat(r["FECHA"][:10]) for r in rows if r["FECHA"][:4].isdigit()]
corte = max(fechas)
porm = collections.Counter(f.strftime("%Y-%m") for f in fechas)
def rango(a, b):
    return sum(1 for f in fechas if a <= f <= b)
ventanas = {}
for y in (2021, 2026):
    ini, fin = date(y, 7, 28), date(y, 11, 5)
    pre_ini, pre_fin = ini - timedelta(days=100), ini - timedelta(days=1)
    ventanas[str(y)] = {
        "100_dias_previos": [str(pre_ini), str(pre_fin), rango(pre_ini, pre_fin)],
        "100_dias_gobierno": [str(ini), str(fin), rango(ini, fin)],
    }
out = {"fuente": URL, "corte_datos": str(corte), "fecha_descarga": rows[-1].get("FECHA_DESCARGA"),
       "mensual": sorted(porm.items()), "ventanas": ventanas,
       "anual": sorted(collections.Counter(f.year for f in fechas).items())}
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(json.dumps(ventanas, indent=1), out["corte_datos"])
