"""Descarga WGI (Banco Mundial, source=3) para Perú. Uso: python3 intl_gob_wgi.py OUT.json"""
import json, sys, urllib.request
DIMS = ["CC", "GE", "RL", "RQ", "VA", "PV"]
out = {}
for d in DIMS:
    for suf in ["EST", "SC"]:
        code = f"GOV_WGI_{d}.{suf}"
        url = f"https://api.worldbank.org/v2/country/PER/indicator/{code}?format=json&per_page=100&source=3"
        with urllib.request.urlopen(url, timeout=90) as r:
            js = json.load(r)
        rows = js[1] if len(js) > 1 and js[1] else []
        out[code] = {x["date"]: x["value"] for x in rows if x["value"] is not None}
        print(code, {k: out[code][k] for k in sorted(out[code]) if k >= "2004"}, flush=True)
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "wgi_per.json", "w"), indent=1)
