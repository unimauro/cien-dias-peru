"""Macro de los primeros 100 días (García 2006, Humala 2011, PPK 2016, Toledo 2001) desde BCRPData.
Solo stdlib. Uso: python3 historico_bcrp.py <salida.json>
Códigos verificados contra el catálogo https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata (7-nov-2026):
  PD04638PD  TC Interbancario (S/ por US$) - Venta   (PD04640PD es TC Sistema bancario SBS - Venta, NO interbancario)
  PD04709XD  Spread - EMBIG Perú (pbs)
  PD38026MD  Índice General Bursátil BVL (índice)   (desde 2006-01-02; no cubre 2001)
  PD12301MD  Tasa de Referencia de la Política Monetaria (desde 2003-09-05; no cubre 2001)
"""
import json, sys, time, urllib.request
from datetime import date, datetime

BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
CODES = ["PD04638PD", "PD04709XD", "PD38026MD", "PD12301MD"]
GOBIERNOS = {
    "toledo_2001": "2001-07-28",
    "garcia_2006": "2006-07-28",
    "humala_2011": "2011-07-28",
    "ppk_2016": "2016-07-28",
}
MES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7,
       "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def get(url):
    err = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa
            err = e
            time.sleep(2)
    return {"error": str(err)}


def parse_fecha(s):  # "28.Jul.06"
    d, m, y = s.split(".")
    return date(2000 + int(y), MES[m[:3]], int(d))


def serie(code, a, b):
    js = get(f"{BASE}/{code}/json/{a}/{b}")
    if "error" in js:
        return None, [], js["error"]
    nombre = js.get("config", {}).get("series", [{}])[0].get("name", "")
    out = []
    for p in js.get("periods", []):
        v = p["values"][0]
        try:
            out.append([parse_fecha(p["name"]).isoformat(), float(v)])
        except (ValueError, KeyError):
            continue  # "n.d."
    return nombre, out, None


def nearest(s, target, forward):
    """Primer dato con fecha >= target (forward) o último <= target."""
    t = target.isoformat()
    if forward:
        c = [x for x in s if x[0] >= t]
        return c[0] if c else None
    c = [x for x in s if x[0] <= t]
    return c[-1] if c else None


res = {}
for gob, d0s in GOBIERNOS.items():
    d0 = datetime.strptime(d0s, "%Y-%m-%d").date()
    y = d0.year
    d100 = date(y, 11, 5)  # 28-jul + 100 días = 5-nov
    a, b = f"{y}-07-01", f"{y}-11-30"
    lst = []
    for c in CODES:
        nombre, s, err = serie(c, a, b)
        if err or not s:
            lst.append({"codigo": c, "nombre": nombre, "error": err or "sin datos en la ventana"})
            continue
        # Día 0: último dato hábil <= 28-jul (28-jul es feriado nacional) ; día 100: último dato <= 5-nov
        p0 = nearest(s, d0, forward=False)
        p100 = nearest(s, d100, forward=False)
        var = round((p100[1] / p0[1] - 1) * 100, 2) if p0 and p100 and p0[1] else None
        win = [x for x in s if (date(y, 7, 20).isoformat() <= x[0] <= date(y, 11, 10).isoformat())]
        lst.append({
            "codigo": c, "nombre": nombre,
            "d0": p0[1] if p0 else None, "d0_fecha": p0[0] if p0 else None,
            "d100": p100[1] if p100 else None, "d100_fecha": p100[0] if p100 else None,
            "var_pct": var,
            "fuente_url": f"{BASE}/{c}/json/{a}/{b}",
            "serie": win,
        })
        print(gob, c, nombre, p0, p100, var)
    res[gob] = lst

json.dump(res, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
