#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ejecución presupuestal del Gobierno Nacional por SECTOR al cierre de octubre.

Fuente: Consulta Amigable del MEF (Consulta de Ejecución del Gasto),
https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx
(la API CKAN datastore_search_sql de datosabiertos.mef.gob.pe respondía 404 el 7-nov-2026).

Drill-down: Año -> (ActProy | Proyecto) -> Nivel de Gobierno = E (Gobierno Nacional)
            -> Sector -> [cada sector] -> Mes.
- PIM: el PIM que muestra la consulta (año cerrado = PIM final al 31-dic;
  año en curso = PIM vigente a la fecha de consulta). La consulta NO da PIM por mes.
- Devengado ene-oct = suma de la columna Devengado de los meses 1..10.
- Devengado ago-oct = meses 8..10 (aprox. los primeros 100 días desde el 28-jul).
Columnas mensuales: Certificación, Compromiso anual, Atención compromiso mensual, Devengado, Girado.

Cache reanudable en etl/cache/mef_sector_<año>_<ap>.json
Uso: ~/.venvs/cien-dias/bin/python etl/performance_mef_sectores.py [años...]
"""
import json, os, re, sys, time
import requests
from bs4 import BeautifulSoup

BASE = "https://apps5.mineco.gob.pe/transparencia/Navegador/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
YEARS = [int(a) for a in sys.argv[1:]] or [2026, 2021, 2016, 2011, 2006]
APS = ["ActProy", "Proyecto"]


def sess():
    s = requests.Session(); s.headers["User-Agent"] = UA
    s.get(BASE + "default.aspx", timeout=40)
    return s


def start(s, y, ap):
    s.get(f"{BASE}default.aspx?y={y}&ap={ap}", timeout=40)
    soup = BeautifulSoup(s.get(f"{BASE}Navegar.aspx?y={y}&ap={ap}", timeout=40).text, "lxml")
    sel = soup.select_one("#ctl00_CPH1_DrpYear option[selected]")
    if not sel or sel.get_text(strip=True) != str(y):
        raise RuntimeError("año no fijado")
    return soup


def fields(soup):
    d = {}
    for inp in soup.select("input"):
        n = inp.get("name"); t = (inp.get("type") or "text").lower()
        if n and t not in ("submit", "button", "image", "reset", "radio", "checkbox"):
            d[n] = inp.get("value", "")
    for sel in soup.select("select"):
        n = sel.get("name"); o = sel.select_one("option[selected]") or sel.select_one("option")
        if n:
            d[n] = o.get("value", "") if o else ""
    return d


def rows(soup):
    out = []
    for tr in soup.find_all("tr"):
        r = tr.find("input", {"type": "radio"})
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if not r or len(tds) < 5:
            continue
        lab = next((t for t in tds if t and not re.match(r"^[\d,\.\-]+$", t)), "")
        nums = [float(t.replace(",", "")) for t in tds if re.match(r"^-?[\d,]+(\.\d+)?$", t)]
        out.append({"grp": r.get("name"), "val": r.get("value"), "label": lab, "nums": nums})
    return out


def click(s, soup, btn, select=None):
    d = fields(soup)
    d[btn] = next(i.get("value") for i in soup.select("input[type=submit]") if i.get("name") == btn)
    if select:
        d.update(select)
    action = soup.find("form").get("action")
    for k in range(4):
        try:
            h = s.post(BASE + action, data=d, headers={"Referer": BASE + action}, timeout=120).text
            time.sleep(1.0)
            return BeautifulSoup(h, "lxml")
        except Exception:
            time.sleep(6)
    raise RuntimeError("POST falló")


def sector_list(s, y, ap):
    p = start(s, y, ap)
    p = click(s, p, "ctl00$CPH1$BtnTipoGobierno")
    gn = [r for r in rows(p) if r["label"].startswith("E:")]
    if not gn:
        raise RuntimeError("sin Gobierno Nacional")
    gn = gn[0]
    ps = click(s, p, "ctl00$CPH1$BtnSector", {gn["grp"]: gn["val"]})
    return gn, ps


def scrape(y, ap):
    path = os.path.join(CACHE, f"mef_sector_{y}_{ap}.json")
    data = json.load(open(path)) if os.path.exists(path) else {"anio": y, "ap": ap, "sectores": {}}
    s = sess()
    gn, ps = sector_list(s, y, ap)
    # GN: PIA, PIM, Cert, CompAnual, AtencMens, Devengado, Girado, Avance%
    data["gn_total"] = {"label": gn["label"], "pia": gn["nums"][0], "pim": gn["nums"][1],
                        "devengado_anual_o_a_la_fecha": gn["nums"][-3]}
    secs = rows(ps)
    print(f"{y} {ap}: {len(secs)} sectores", flush=True)
    for sec in secs:
        if sec["label"] in data["sectores"]:
            continue
        for att in range(3):
            try:
                pm = click(s, ps, "ctl00$CPH1$BtnMes", {sec["grp"]: sec["val"]})
                meses = {}
                for r in rows(pm):
                    m = re.match(r"^(\d+):", r["label"])
                    if m and len(r["nums"]) >= 2:
                        meses[int(m.group(1))] = r["nums"][-2]  # Devengado (penúltima: Devengado, Girado)
                break
            except Exception as e:
                print("  retry", sec["label"], repr(e)[:60], flush=True)
                time.sleep(8); s = sess(); gn, ps = sector_list(s, y, ap)
                sec = next(r for r in rows(ps) if r["label"] == sec["label"])
        n = sec["nums"]
        data["sectores"][sec["label"]] = {
            "pia": n[0], "pim": n[1], "devengado_total": n[-3],
            "dev_mes": meses,
            "dev_ene_oct": round(sum(v for k, v in meses.items() if k <= 10), 2),
            "dev_ago_oct": round(sum(v for k, v in meses.items() if 8 <= k <= 10), 2),
        }
        json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        print(f"  {sec['label'][:40]:40s} PIM {n[1]/1e6:10.1f}M  dev ene-oct {data['sectores'][sec['label']]['dev_ene_oct']/1e6:10.1f}M", flush=True)
    data["consultado"] = time.strftime("%Y-%m-%d %H:%M")
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    for y in YEARS:
        for ap in APS:
            try:
                scrape(y, ap)
            except Exception as e:
                print("FALLO", y, ap, repr(e)[:100], flush=True)
