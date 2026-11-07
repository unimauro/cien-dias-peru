"""BTI (Bertelsmann Transformation Index): extrae Perú del archivo oficial.
Fuente: https://bti-project.org/fileadmin/api/content/en/downloads/data/BTI_2006-2026_Scores.xlsx
Uso: ~/.venvs/cien-dias/bin/python -I intl_gob_bti.py ARCHIVO.xlsx"""
import sys, json, warnings, openpyxl
warnings.filterwarnings("ignore")
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
out = {}
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    if not rows: continue
    hi = next((i for i, r in enumerate(rows[:10]) if r and any(isinstance(c, str) and "Status Index" in c for c in r)), None)
    if hi is None: print("##", ws.title, "sin cabecera"); continue
    hdr = [str(c).strip() if c else "" for c in rows[hi]]
    for r in rows[hi + 1:]:
        if r and isinstance(r[0], str) and r[0].strip().startswith("Peru"):
            d = {h: v for h, v in zip(hdr, r) if h and any(k in h for k in ("Status Index", "Democracy Status", "Governance Index", "Category", "Prosecution of office abuse", "Anti-corruption policy", "Rank"))}
            out[ws.title] = d; print(ws.title, d)
json.dump(out, open("bti_per.json", "w"), indent=1, default=str)
