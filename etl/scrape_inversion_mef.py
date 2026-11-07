"""Ejecución de inversión pública por mes (Consulta Amigable del MEF).
Fuente: https://apps5.mineco.gob.pe/transparencia/Navegador/  (la API CKAN
datastore_search_sql respondía 404 'Recurso no encontrado' el 7-nov-2026).

Para cada año: 'Sólo Proyectos' -> TOTAL y por Nivel de Gobierno (E/M/R) -> Mes.
Además: 'Actividades/Proyectos' -> Genérica 2.6 -> Mes (total).
Uso: python scrape_inversion_mef.py OUT.json 2021 2026
"""
import sys, re, json, time, requests
from bs4 import BeautifulSoup
BASE = "https://apps5.mineco.gob.pe/transparencia/Navegador/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def fields(soup):
    d = {}
    for inp in soup.select("input"):
        n = inp.get("name"); t = (inp.get("type") or "text").lower()
        if not n or t in ("submit", "button", "image", "reset"): continue
        if t in ("radio", "checkbox"):
            if inp.has_attr("checked"): d[n] = inp.get("value", "on")
        else: d[n] = inp.get("value", "")
    for sel in soup.select("select"):
        o = sel.select_one("option[selected]") or sel.select_one("option")
        if sel.get("name"): d[sel["name"]] = o.get("value", "") if o else ""
    return d

def num(c):
    try: return float(c.replace(",", ""))
    except ValueError: return None

def rows(soup):
    out = []
    for tr in soup.find_all("tr"):
        tds = [t.get_text(" ", strip=True) for t in tr.find_all("td")]
        radio = tr.select_one("input[name=grp1]")
        if len(tds) < 9 or not tds[1]: continue
        v = [num(c) if c else None for c in tds[2:10]]
        if v[1] is None and v[5] is None: continue  # filas de cabecera
        out.append({"label": tds[1], "grp1": radio.get("value") if radio else None,
                    "pia": v[0], "pim": v[1], "certificacion": v[2], "compromiso_anual": v[3],
                    "atencion_mensual": v[4], "devengado": v[5], "girado": v[6], "avance_pct": v[7]})
    return out

class Nav:
    def __init__(self, year, ap):
        self.s = requests.Session(); self.s.headers["User-Agent"] = UA
        self.s.get(BASE + "default.aspx", timeout=40)
        self.s.get(f"{BASE}default.aspx?y={year}&ap={ap}", timeout=40)
        self.ref = f"{BASE}Navegar.aspx?y={year}&ap={ap}"
        self.soup = BeautifulSoup(self.s.get(self.ref, timeout=40).text, "lxml")
        sel = self.soup.select_one("#ctl00_CPH1_DrpYear option[selected]")
        assert sel and sel.get_text(strip=True) == str(year), f"año no fijado: {sel}"
    def click(self, btn, grp1=None):
        d = fields(self.soup)
        if grp1 is not None: d["grp1"] = grp1
        d[f"ctl00$CPH1${btn}"] = "x"
        action = self.soup.find("form").get("action")
        html = self.s.post(BASE + action, data=d, headers={"Referer": self.ref}, timeout=90).text
        self.soup = BeautifulSoup(html, "lxml"); time.sleep(2)
        return rows(self.soup)

def scope(year, ap, steps):
    """steps: lista de (boton, prefijo_de_fila_a_seleccionar_o_None)."""
    for attempt in range(3):
        try:
            n = Nav(year, ap); r = rows(n.soup); grp = r[0]["grp1"] if r else None
            for btn, pick in steps:
                r = n.click(btn, grp)
                if pick:
                    m = [x for x in r if x["label"].startswith(pick)]
                    assert m, f"no hallé fila {pick}"
                    grp = m[0]["grp1"]
            return r
        except Exception as e:
            print("  reintento", year, steps, repr(e)[:120], flush=True); time.sleep(6)
    return None

out = {}
for y in sys.argv[2:]:
    y = int(y); res = {}
    res["proyectos_por_nivel"] = scope(y, "Proyecto", [("BtnTipoGobierno", None)])
    res["proyectos_total_por_mes"] = scope(y, "Proyecto", [("BtnMes", None)])
    for code, name in (("E", "gobierno_nacional"), ("M", "gobiernos_locales"), ("R", "gobiernos_regionales")):
        res[f"proyectos_{name}_por_mes"] = scope(y, "Proyecto", [("BtnTipoGobierno", code + ":"), ("BtnMes", None)])
    res["generica_por_generica"] = scope(y, "ActProy", [("BtnGenerica", None)])
    res["generica_26_por_mes"] = scope(y, "ActProy", [("BtnGenerica", "6-26:"), ("BtnMes", None)])
    out[y] = res
    print(y, {k: (len(v) if v else None) for k, v in res.items()}, flush=True)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
