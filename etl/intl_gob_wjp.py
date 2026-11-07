"""WJP Rule of Law Index: lee el archivo histórico oficial y extrae Perú.
Fuente: https://worldjusticeproject.org/rule-of-law-index/downloads/2025_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx
Uso: ~/.venvs/cien-dias/bin/python -I intl_gob_wjp.py ARCHIVO.xlsx"""
import sys, warnings, openpyxl
warnings.filterwarnings("ignore")
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    print("##", ws.title, len(rows), rows[0][:6] if rows else None)
    hdr = rows[0] if rows else []
    for r in rows:
        if r and r[0] == "Peru" or (r and "Peru" in [c for c in r[:3]]):
            print({h: v for h, v in zip(hdr, r) if h and ("Overall" in str(h) or "Rank" in str(h) or "Year" in str(h) or "Country" in str(h))})

# Hojas por año (traspuestas): columna Perú, filas "Overall Score" y rango global
for ws in wb.worksheets:
    if "Scores" not in ws.title: continue
    rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Country")
    col = list(rows[hi]).index("Peru") if "Peru" in rows[hi] else None
    if col is None: print(ws.title, "sin Perú"); continue
    sel = {str(r[0]).strip(): r[col] for r in rows[hi:] if r and r[0] and ("Overall" in str(r[0]) or "Rank" in str(r[0]))}
    n = sum(1 for c in rows[hi][1:] if c)
    print(ws.title, sel, "paises:", n)

# Rango global calculado (posición del puntaje de Perú entre todos los países de la hoja)
import json
out = {}
for ws in wb.worksheets:
    if "Scores" not in ws.title: continue
    rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Country")
    orow = next(r for r in rows[hi:] if r and r[0] and "Overall Score" in str(r[0]))
    scores = {c: v for c, v in zip(rows[hi][1:], orow[1:]) if c and isinstance(v, (int, float))}
    p = scores["Peru"]
    rank = 1 + sum(1 for v in scores.values() if round(v, 2) > round(p, 2))
    yr = ws.title.replace("WJP ROL Index ", "").replace(" Scores", "")
    out[yr] = {"score": round(p, 4), "rank_calc": rank, "n_paises": len(scores)}
    print(yr, out[yr])
json.dump(out, open("wjp_per.json", "w"), indent=1)
