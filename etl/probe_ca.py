"""Sonda de la Consulta Amigable (MEF): guarda HTML de un drill-down para inspección."""
import sys, requests
from bs4 import BeautifulSoup
BASE = "https://apps5.mineco.gob.pe/transparencia/Navegador/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
year, ap, btn, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = requests.Session(); s.headers["User-Agent"] = UA
s.get(BASE + "default.aspx", timeout=40)
s.get(f"{BASE}default.aspx?y={year}&ap={ap}", timeout=40)
html = s.get(f"{BASE}Navegar.aspx?y={year}&ap={ap}", timeout=40).text
open(out + ".0.html", "w").write(html)
soup = BeautifulSoup(html, "lxml")
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
g = soup.select_one("input[name=grp1]")
if g: d["grp1"] = g.get("value")
d[f"ctl00$CPH1${btn}"] = "x"
action = soup.find("form").get("action")
r = s.post(BASE + action, data=d, headers={"Referer": f"{BASE}Navegar.aspx?y={year}&ap={ap}"}, timeout=60).text
open(out + ".1.html", "w").write(r)
print(len(html), len(r), action)
