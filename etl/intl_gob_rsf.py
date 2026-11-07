"""RSF Clasificación Mundial de la Libertad de Prensa: descarga CSV oficiales y extrae Perú.
Uso: for y in 2013..2026: curl -sLo OUTDIR/rsf_$y.csv https://rsf.org/sites/default/files/import_classement/$y.csv
     python3 -I intl_gob_rsf.py OUTDIR"""
import csv, io, json, os, sys, urllib.request
outdir = sys.argv[1] if len(sys.argv) > 1 else "."
res = {}
for y in range(2013, 2027):
    # Fuente: https://rsf.org/sites/default/files/import_classement/{y}.csv (descargado con curl a OUTDIR/rsf_{y}.csv)
    f = os.path.join(outdir, f"rsf_{y}.csv")
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        print(y, "sin archivo"); continue
    raw = open(f, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            txt = raw.decode(enc)
            if ";" in txt[:200]: break
        except Exception:
            continue
    rd = csv.DictReader(io.StringIO(txt), delimiter=";")
    for r in rd:
        r = {(k or "").strip().lstrip("﻿"): v for k, v in r.items()}
        if r.get("ISO", "").strip() == "PER":
            score_key = next(k for k in r if k.lower().startswith("score") and "n-1" not in k.lower() and "evolution" not in k.lower() and "exaction" not in k.lower())
            rank_key = "Rank" if "Rank" in r else "Rank N"
            n = sum(1 for _ in csv.DictReader(io.StringIO(txt), delimiter=";"))
            res[y] = {"score": float(r[score_key].replace(",", ".")), "rank": int(r[rank_key]), "n_paises": n, "metodologia": "nueva (0-100, alto=mejor)" if y >= 2022 else "antigua 2013-2021 (RSF la publica en sus CSV como 0-100 alto=mejor; no comparable con 2022+)"}
            print(y, res[y], flush=True)
json.dump(res, open(os.path.join(outdir, "rsf_per.json"), "w"), indent=1)
