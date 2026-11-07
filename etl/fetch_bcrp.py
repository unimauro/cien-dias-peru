"""Descarga series BCRPData para las dos ventanas (V1 2021, V2 2026). Solo stdlib."""
import json, sys, urllib.request, time
BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
CODES = sys.argv[2:] if len(sys.argv) > 2 else []
OUT = sys.argv[1]
RANGES = {
    "D": {"v1": ("2021-07-01", "2021-11-30"), "v2": ("2026-07-01", "2026-11-07")},
    "M": {"v1": ("2021-4", "2021-12"), "v2": ("2026-4", "2026-11")},
}
def get(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = e; time.sleep(2)
    return {"error": str(err)}
res = {}
for c in CODES:
    freq = "M" if c.endswith("M") and not c.endswith("MD") and not c.endswith("PD") else "D"
    if c[-1] == "D": freq = "D"
    r = {"meta": get(f"{BASE}/{c}/json")}
    for w, (a, b) in RANGES[freq].items():
        r[w] = get(f"{BASE}/{c}/json/{a}/{b}")
    r["freq"] = freq
    res[c] = r
    print(c, freq, json.dumps(r["meta"].get("config", r["meta"]), ensure_ascii=False)[:250])
json.dump(res, open(OUT, "w"), ensure_ascii=False)
