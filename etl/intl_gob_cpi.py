"""CPI de Transparency International para Perú.
- 2012-2025 (escala 0-100): hoja «CPI Historical» del XLSX oficial
  https://images.transparencycdn.org/images/CPI2025_Results.xlsx (formato OOXML strict; openpyxl no lo lee, por eso se parsea el XML).
- 2005-2011 (escala 0-10): CSV del archivo histórico de transparency.org/en/cpi/{año}.
Uso: python3 -I intl_gob_cpi.py DIR  (DIR contiene cpi2025.xlsx y cpiold_*.csv) -> DIR/cpi_per.json"""
import csv, glob, json, os, re, sys, zipfile, xml.etree.ElementTree as ET
NS = "http://purl.oclc.org/ooxml/spreadsheetml/main"
OLD = {2005: "CPI-2005_200602_104136.csv", 2006: "CPI-2006-new_200602_095933.csv", 2007: "CPI-2007-new_200602_092501.csv",
       2008: "CPI-Archive-2008-2.csv", 2009: "CPI-2009-new_200601_120052.csv", 2010: "CPI-2010-new_200601_105629.csv",
       2011: "CPI-2011-new_200601_104308.csv"}

def sheet_rows(path, name):
    z = zipfile.ZipFile(path)
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % NS)) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("{%s}si" % NS)]
    names = [s.get("name") for s in ET.fromstring(z.read("xl/workbook.xml")).find("{%s}sheets" % NS)]
    i = names.index(name) + 1
    for r in ET.fromstring(z.read(f"xl/worksheets/sheet{i}.xml")).iter("{%s}row" % NS):
        out = {}
        for c in r.findall("{%s}c" % NS):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("{%s}v" % NS)
            out[col] = None if v is None else (ss[int(v.text)] if c.get("t") == "s" else v.text)
        yield out

def peru(d):
    res = {}
    rows = list(sheet_rows(os.path.join(d, "cpi2025.xlsx"), "CPI Historical"))
    hdr = next(r for r in rows if r.get("A") == "Country / Territory")
    col = {v: k for k, v in hdr.items()}
    for r in rows:
        if r.get(col["ISO3"]) and r.get(col["Year"], "").isdigit():
            y = int(r[col["Year"]])
            res.setdefault(y, {"n_paises": 0})["n_paises"] += 1
            if r[col["ISO3"]] == "PER":
                res[y].update(score=int(float(r[col["CPI score"]])), rank=int(r[col["Rank"]]), escala="0-100")
    for y, f in OLD.items():
        rows = list(csv.DictReader(open(os.path.join(d, "cpiold_" + f), encoding="utf-8-sig", errors="ignore")))
        p = next(x for x in rows if x["iso"] == "PER")
        res[y] = {"score": float(p["score"]), "rank": int(p["rank"]), "n_paises": len(rows), "escala": "0-10",
                  "fuente": "https://images.transparencycdn.org/images/" + f}
    return dict(sorted(res.items()))

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    out = peru(d)
    for y, v in out.items(): print(y, v)
    json.dump(out, open(os.path.join(d, "cpi_per.json"), "w"), indent=1)
