"""Series de RESULTADO desde BCRPData (replican INEI): empleo Lima Metro e IPC.
Uso: python3 resultados_bcrp.py <out.json>   (solo stdlib)"""
import json, sys, urllib.request, time
BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
SERIES = {
    "PN38063GM": "Tasa de desempleo Lima Metro (%, trimestre móvil)",
    "PN38051GM": "PEA ocupada Lima Metro (miles, trimestre móvil)",
    "PN38070GM": "Ingreso promedio mensual Lima Metro (S/, trimestre móvil)",
    "PN01273PM": "IPC Lima Metro var% 12 meses",
    "PN01313PM": "IPC Alimentos y Bebidas Lima Metro var% mensual",
    "PN01440PM": "Índice real de precio de Gas Doméstico (GLP) 2010=100",
    "PN01728AM": "PBI var% interanual (INEI, mensual)",
}
def get(url):
    err = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = e; time.sleep(2)
    raise RuntimeError(f"{url}: {err}")
out = {}
for code, name in SERIES.items():
    d = get(f"{BASE}/{code}/json/2020-1/2026-12")
    serie = []
    for p in d["periods"]:
        v = p["values"][0]
        try: serie.append([p["name"], round(float(v), 3)])
        except ValueError: pass  # 'n.d.'
    out[code] = {"nombre": name, "bcrp_nombre": d["config"]["series"][0]["name"], "serie": serie}
    print(code, len(serie), serie[-1])
# Inflación de alimentos 12 meses: compuesto de 12 variaciones mensuales
m = out["PN01313PM"]["serie"]
a12 = []
for i in range(11, len(m)):
    f = 1.0
    for _, v in m[i-11:i+1]: f *= 1 + v/100
    a12.append([m[i][0], round((f-1)*100, 2)])
out["ALIM12"] = {"nombre": "IPC Alimentos y Bebidas Lima Metro var% 12 meses (compuesto de PN01313PM)", "serie": a12}
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
