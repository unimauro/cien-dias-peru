#!/usr/bin/env python3
"""Genera los informes PDF de «100 días bajo la lupa».

Salida (en pdf/):
  comparativo.pdf                      informe completo (8-14 páginas)
  keiko-2026.pdf, castillo-2021.pdf,
  ppk-2016.pdf, humala-2011.pdf,
  garcia-2006.pdf                      un informe por gobierno (3-6 páginas)

Fuentes de datos: research/*.json. La redacción editorial se lee de index.html
(#conclusion) y de app.js (lista de correcciones), para que el PDF no se aparte
de lo publicado en el dashboard.

Uso (siempre dentro de un venv con reportlab y matplotlib):
  ~/.venvs/cien-dias/bin/python etl/build_pdfs.py
Tipografías: Archivo y Source Serif 4 (Google Fonts, TTF). Se buscan en
$CIEN_DIAS_FONTS o en etl/cache/fonts (se descargan ahí si faltan); si no hay
red, se usa Helvetica/Times.
"""
from __future__ import annotations

import html
import io
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT, TA_RIGHT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas as rl_canvas  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "research"
OUT = ROOT / "pdf"
URL = "https://unimauro.github.io/cien-dias-peru/"
URL_SHORT = "unimauro.github.io/cien-dias-peru"
CREDIT = "Elaborado por Carlos Cárdenas, con investigación asistida por IA y verificación de fuentes"

# ---------------------------------------------------------------- tipografías
FONT_FILES = {
    "Archivo": ("Archivo-Regular.ttf", "https://fonts.gstatic.com/s/archivo/v25/k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q82sJaRE-NWIDdgffTTNDNp8A.ttf"),
    "Archivo-SB": ("Archivo-SemiBold.ttf", "https://fonts.gstatic.com/s/archivo/v25/k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q82sJaRE-NWIDdgffTT6jRp8A.ttf"),
    "Archivo-XB": ("Archivo-ExtraBold.ttf", "https://fonts.gstatic.com/s/archivo/v25/k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q82sJaRE-NWIDdgffTTtDRp8A.ttf"),
    "ArchivoC-XB": ("ArchivoCondensed-ExtraBold.ttf", "https://fonts.gstatic.com/s/archivo/v25/k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q9osJaRE-NWIDdgffTTtDRp8A.ttf"),
    "Serif": ("SourceSerif4-Regular.ttf", "https://fonts.gstatic.com/s/sourceserif4/v15/vEFy2_tTDB4M7-auWDN0ahZJW3IX2ih5nk3AucvUPf6OAVIJmeUDygwjihdqrhw.ttf"),
    "Serif-SB": ("SourceSerif4-SemiBold.ttf", "https://fonts.gstatic.com/s/sourceserif4/v15/vEFy2_tTDB4M7-auWDN0ahZJW3IX2ih5nk3AucvUPf6OAVIJmeUDygwjisltrhw.ttf"),
    "Serif-It": ("SourceSerif4-Italic.ttf", "https://fonts.gstatic.com/s/sourceserif4/v15/vEF02_tTDB4M7-auWDN0ahZJW1ge6NmXpVAHV83Bfb_0S2D2QYxoUKIkn98pRl9dCw.ttf"),
}
FALLBACK = {"Archivo": "Helvetica", "Archivo-SB": "Helvetica-Bold", "Archivo-XB": "Helvetica-Bold",
            "ArchivoC-XB": "Helvetica-Bold", "Serif": "Times-Roman", "Serif-SB": "Times-Bold", "Serif-It": "Times-Italic"}
F = dict(FALLBACK)  # nombre lógico -> nombre registrado


def setup_fonts() -> None:
    fdir = Path(os.environ.get("CIEN_DIAS_FONTS") or ROOT / "etl" / "cache" / "fonts")
    fdir.mkdir(parents=True, exist_ok=True)
    ok = True
    for name, (fn, url) in FONT_FILES.items():
        p = fdir / fn
        if not p.exists():
            try:
                urllib.request.urlretrieve(url, p)
            except Exception as e:  # sin red: Helvetica/Times
                print(f"  ! no se pudo descargar {fn}: {e}")
                ok = False
                continue
        try:
            pdfmetrics.registerFont(TTFont(name, str(p)))
            F[name] = name
            font_manager.fontManager.addfont(str(p))
        except Exception as e:
            print(f"  ! no se pudo registrar {fn}: {e}")
            ok = False
    from reportlab.lib.fonts import addMapping
    for fam, n, b, i in (("Serif", F["Serif"], F["Serif-SB"], F["Serif-It"]), ("Archivo", F["Archivo"], F["Archivo-SB"], F["Archivo"])):
        if F["Serif"] == "Serif" or fam == "Archivo" and F["Archivo"] == "Archivo":
            addMapping(fam, 0, 0, n); addMapping(fam, 1, 0, b); addMapping(fam, 0, 1, i); addMapping(fam, 1, 1, b)
    try:
        pdfmetrics.registerFont(TTFont("Sym", str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf")))
        F["Sym"] = "Sym"
    except Exception as e:
        print(f"  ! sin fuente de símbolos: {e}")
    plt.rcParams["font.family"] = "Archivo" if ok else "DejaVu Sans"
    plt.rcParams["font.size"] = 8


SYM_RE = re.compile("([■▲▼◆○●✓✕≈])")


def P(text, style, **kw):
    """Paragraph que dibuja los símbolos que no trae Archivo/Source Serif con DejaVu Sans."""
    if F.get("Sym") == "Sym":
        text = SYM_RE.sub(r'<font name="Sym">\1</font>', str(text))
    return Paragraph(text, style, **kw)


# ---------------------------------------------------------------- paleta
INK = "#161a22"; INK2 = "#3a404c"; MUTED = "#636a77"; RULE = "#dcd9d2"; SUNK = "#f3f1ec"; PAPER = "#ffffff"
SEM = {  # fondo, texto, etiqueta
    "g": ("#1e7e3a", "#ffffff", "Bien"),
    "y": ("#f6c744", INK, "Regular"),
    "o": ("#f08a3c", INK, "Malo"),
    "r": ("#c23a35", "#ffffff", "Crítico"),
    "na": ("#ecebe6", "#555c68", "Sin dato"),
}
GOV = {
    "castillo": dict(name="Pedro Castillo", full="Pedro Castillo Terrones", short="Castillo", year=2021, color="#2a78d6", file="castillo-2021.pdf", idn="castillo_2021", exp=None),
    "keiko": dict(name="Keiko Fujimori", full="Keiko Fujimori Higuchi", short="Keiko", year=2026, color="#e87ba4", file="keiko-2026.pdf", idn="keiko_2026", exp=None),
    "ppk": dict(name="Pedro Pablo Kuczynski", full="Pedro Pablo Kuczynski", short="PPK", year=2016, color="#1baf7a", file="ppk-2016.pdf", idn="ppk_2016", exp="ppk_2016"),
    "humala": dict(name="Ollanta Humala", full="Ollanta Humala Tasso", short="Humala", year=2011, color="#eda100", file="humala-2011.pdf", idn="humala_2011", exp="humala_2011"),
    "garcia": dict(name="Alan García", full="Alan García Pérez", short="García", year=2006, color="#6250d6", file="garcia-2006.pdf", idn="garcia_2006", exp="garcia_2006"),
}
ORDER = ["castillo", "keiko", "ppk", "humala", "garcia"]


def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb2hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02x}" for v in c)


def mix(h1, h2, t):
    a, b = hex2rgb(h1), hex2rgb(h2); return rgb2hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


def lum(h):
    def ch(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in hex2rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b


def on_color(h):  # texto legible sobre el color h
    return INK if lum(h) > 0.22 else "#ffffff"


def ink_of(h):  # versión oscura del color, para texto sobre blanco
    c = h
    while lum(c) > 0.12:
        c = mix(c, "#000000", 0.08)
    return c


C = colors.HexColor

# ---------------------------------------------------------------- formato
def fnum(v, d=1):
    if not isinstance(v, (int, float)):
        return "—"
    s = f"{v:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def fsem(v):
    if not isinstance(v, (int, float)):
        return "—"
    a = abs(v)
    return fnum(v, 2 if a < 1 else 1 if a < 10 else 0)


def comma_dec(s):
    """3.4 -> 3,4 en textos (no toca separadores de miles con coma como S/1,230)."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", str(s))


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=False)


def band(sc):
    if not isinstance(sc, (int, float)):
        return "na"
    return "g" if sc >= 70 else "y" if sc >= 50 else "o" if sc >= 30 else "r"


MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "set", "oct", "nov", "dic"]


def fdate(s):
    m = re.match(r"^(\d{4})-(\d{2})(?:-(\d{2}))?", str(s or ""))
    if not m:
        return str(s or "")
    return f"{int(m.group(3))}-{MES[int(m.group(2)) - 1]}-{m.group(1)}" if m.group(3) else f"{MES[int(m.group(2)) - 1]}-{m.group(1)}"


def short_idx(n):
    """Nombre corto de un índice internacional (sin la nota de escala)."""
    if n.startswith(("WGI", "V-Dem")):
        return re.split(r" \(", n)[0].replace("Índice de ", "")
    return re.split(r" \(| – ", n)[0]


def host(u):
    m = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
    return m.group(1) if m else "fuente"


# ---------------------------------------------------------------- datos
def J(name):
    return json.loads((RES / f"{name}.json").read_text(encoding="utf-8"))


D = {n: J(n) for n in ["indice100", "castillo", "keiko", "expresidentes", "idoneidad", "resultados", "indicadores",
                       "performance", "planes", "noticias", "factcheck", "pp2050_mensaje", "pp2050_cumplimiento",
                       "intl_gobernanza", "intl_social", "videos"]}
I = D["indice100"]


def hist(k):
    e = GOV[k]["exp"]
    return D["expresidentes"].get(e) if e else None


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def parse_index_html():
    """Extrae la redacción validada de #conclusion (index.html)."""
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    sec = src.split('id="conclusion"', 1)[1].split("</section>", 1)[0]
    out = {"lede": strip_tags(re.search(r'<p class="verdict-lede">(.*?)</p>', sec, re.S).group(1))}
    hyps = []
    for row in sec.split('<div class="hyp-row">')[1:]:
        stamp = re.search(r'<span class="stamp ([\w-]+)">.*?</span>(.*?)</span>', row, re.S)
        hyps.append(dict(cls=stamp.group(1), label=strip_tags(stamp.group(2)),
                         title=strip_tags(re.search(r"<h3>(.*?)</h3>", row, re.S).group(1)),
                         text=strip_tags(re.search(r"<p>(.*?)</p>", row, re.S).group(1))))
    out["hyps"] = hyps
    ledger = {}
    for col in re.findall(r'<div class="ledger-col">(.*?)</div>\s*(?=<div class="ledger-col">|</div>)', sec, re.S):
        who = "castillo" if "--castillo" in col else "keiko"
        groups = []
        for h4, ul in re.findall(r"<h4>(.*?)</h4>\s*<ul>(.*?)</ul>", col, re.S):
            groups.append((strip_tags(h4), [strip_tags(li) for li in re.findall(r"<li>(.*?)</li>", ul, re.S)]))
        ledger[who] = groups
    out["ledger"] = ledger
    out["note"] = strip_tags(re.search(r'<p class="note">(.*?)</p>', sec, re.S).group(1))
    sem = src.split('id="semaforo"', 1)[1].split("</section>", 1)[0]
    out["sem_intro"] = strip_tags(re.search(r"<div class=\"sec-head\">.*?<p>(.*?)</p>", sem, re.S).group(1))
    out["intl_note"] = INTL_NOTE
    for fn in ("index.html", "contexto.html"):
        p = ROOT / fn
        m = re.search(r'<p class="note"[^>]*>(Año previo a asumir.*?)</p>', p.read_text(encoding="utf-8"), re.S) if p.exists() else None
        if m:
            out["intl_note"] = strip_tags(m.group(1)); break
    return out


INTL_NOTE = ("Año previo a asumir → primer año de gobierno. Contexto, no evaluación: estos índices son anuales y describen el país que recibió cada gobierno y su primer año, "
             "no los 100 días. Para Keiko solo existe la línea base. Un verde en pobreza no significa que la pobreza sea baja, solo que es menor que en el pasado del Perú.")


def parse_app_fixes():
    src = (ROOT / "app.js").read_text(encoding="utf-8")
    block = re.search(r"const fixes = \[(.*?)\];", src, re.S).group(1)
    return [s.replace("\\'", "'") for s in re.findall(r"'((?:[^'\\]|\\.)*)'", block)]


ED = parse_index_html()
FIXES = parse_app_fixes()


def approvals(k):
    if k == "castillo":
        arr = D["castillo"]["aprobacion"]
    elif k == "keiko":
        arr = D["keiko"]["aprobacion"]
    else:
        arr = hist(k)["aprobacion"]
    arr = [a for a in arr if isnum(a.get("aprueba"))]
    ip = [a for a in arr if re.search(r"ipsos|apoyo", a.get("encuestadora", ""), re.I)]
    use = ip if len(ip) >= 2 else arr
    key = lambda a: str(a.get("fecha") or a.get("campo") or "")
    use = sorted(use, key=key)
    lim = f"{GOV[k]['year']}-11-04"
    inwin = [a for a in use if key(a) <= lim]
    return dict(first=use[0], last=(inwin or use)[-1], all=use, key=key)


def promise_balance(k):
    if k == "castillo":
        e = D["castillo"]["ecdata"]
        return dict(total=e["total"], c=e["cumplidas"], p=e["en_proceso"], n=e["incumplidas"], u=0,
                    src="El Comercio – ECData, nov-2021", url=e["fuente_url"], met=e["metodologia"],
                    labels=("Cumplidas", "En proceso", "No cumplidas", "Otras / no verificables"))
    if k == "keiko":
        kg = next(t for t in D["keiko"]["trackers"] if re.search("keiko gobierna", t["nombre"], re.I))
        c, p, n = kg["cumplidas"] or 0, kg["en_proceso"] or 0, (kg.get("incumplidas") or 0) + (kg.get("sin_avance") or 0)
        return dict(total=kg["total"], c=c, p=p, n=n, u=max(0, kg["total"] - c - p - n), src="Keiko Gobierna (tracker ciudadano)",
                    url=kg["url"], met=kg["metodologia"], detalle=kg.get("en_proceso_detalle"),
                    labels=("Cumplidas", "En proceso (norma parcial)", "Sin avance (sin norma que lo acredite)", "Otras"))
    b = (hist(k) or {}).get("balance_promesas") or {}
    if isnum(b.get("total")):
        c, n, p = b.get("cumplidas") or 0, b.get("incumplidas") or 0, b.get("en_proceso") or 0
        return dict(total=b["total"], c=c, p=p, n=n, u=max(0, b["total"] - c - n - p), src="Convoca.pe (vía América TV)", url=b["fuente_url"],
                    met=b.get("metodologia"), nota=b.get("nota_suma"), labels=("Cumplidas", "En proceso", "No cumplidas", "Otras categorías / no verificables"))
    return dict(total=None, met=b.get("metodologia"), url=b.get("fuente_url"))


LEVELS = ["insumo", "actividad", "producto", "resultado", "impacto"]
LEVEL_DEF = {"insumo": "Leyes, decretos, presupuesto, nombramientos.", "actividad": "Procesos en marcha: mesas, lanzamientos, operativos.",
             "producto": "Bienes o servicios entregados: camas, pensiones, obras.", "resultado": "Cambia la situación de la población.",
             "impacto": "Cambio de largo plazo en bienestar o desarrollo."}


def norm_level(s):
    s = str(s or "").lower()
    for lv in LEVELS:
        if s.startswith(lv) or lv in s:
            return lv
    return None


def is_done(s):
    s = str(s or "").strip().lower()
    return bool(re.match(r"^cumplid", s)) and "parcial" not in s


def promise_items(k):
    arr = D["castillo"]["promesas"] if k == "castillo" else D["keiko"]["promesas"] if k == "keiko" else hist(k)["promesas_emblematicas"]
    out = []
    for p in arr:
        out.append(dict(texto=p["texto"], estado=p.get("estado", ""), lvl=norm_level(p.get("nivel_cadena_valor")), url=p.get("fuente_url"), nota=p.get("nota")))
    return out


def gov_facts(k):
    """Gabinete y gobernabilidad, con la misma estructura para todos."""
    ido = D["idoneidad"]["gabinetes"][GOV[k]["idn"]]
    ag = ido["agregados"]
    d3 = I["gobiernos"][k]["dims"]["D3"]["valor"]
    m = re.search(r"(\d+) de (\d+) ministros del día 1 siguen en el cargo; idoneidad (\d+)/100", d3)
    f = dict(premier=ido["premier"], siguen=f"{m.group(1)} de {m.group(2)}", idoneidad=int(m.group(3)),
             exp_n=round(ag["pct_experiencia_si"] * ag["n_validos_experiencia"] / 100), exp_N=ag["n_validos_experiencia"],
             form_n=round(ag["pct_formacion_si"] * ag["n_validos_formacion"] / 100), form_N=ag["n_validos_formacion"],
             inv=ag["n_investigacion_reportada_si"], urls=[])
    if k == "castillo":
        g = D["castillo"]["gobernabilidad"]
        f["cambios"] = f"{g['ministros_salientes_100_dias']['valor']} cambios de ministro, incluido el premier; 2 gabinetes"
        f["premieres"] = g["premieres"]["detalle"]
        vc = g["votos_de_confianza"]["detalle"]
        f["confianza"] = " · ".join(f"{v['gabinete']} ({fdate(v['fecha'])}): {v['a_favor']}-{v['en_contra']}-{v['abstenciones']}" for v in vc)
        pl = g["proyectos_de_ley_ejecutivo"]
        f["facultades"] = (f"{pl['valor']} proyectos de ley del Ejecutivo ({pl['desglose']['iniciativas_de_politica_sustantivas']} de política sustantiva; el resto, tratados y trámites). "
                           "Pidió facultades tributarias al Congreso el 28-oct-2021; no se aprobaron dentro de la ventana.")
        f["inv_src"] = "prensa"
        f["urls"] = [g["ministros_salientes_100_dias"]["fuente_url"], vc[0]["fuente_url"], pl["fuente_url"]]
    elif k == "keiko":
        K = D["keiko"]; g = K["gobernabilidad"]
        f["cambios"] = "1 ministro reemplazado (Transportes, 18-sep, por salud); el mismo premier los 100 días"
        f["premieres"] = f"{K['gabinete']['premier']}: el mismo premier los 100 días"
        f["confianza"] = "Sin votación: con la reforma bicameral, el gabinete se presentó ante Diputados el 20-ago (confianza media, una sola fuente)"
        f["facultades"] = f"Facultades por 90 días (Ley 32743, 22-oct). {g['decretos_legislativos']['n']} decretos legislativos emitidos al día 100. Censura a Interior rechazada."
        f["inv_src"] = "declaraciones juradas (Ley 31227)"
        f["urls"] = [K["gabinete"]["cambios"][0]["fuentes"][0], K["gabinete"]["voto_de_confianza"]["fuente_url"], g["decretos_legislativos"]["fuentes"][0]]
    else:
        g = hist(k)["gobernabilidad"]
        cm = g.get("cambios_gabinete_100d") or {}
        f["cambios"] = f"{cm.get('n', '—')} cambios de ministro" + (f". {cm['detalle']}" if cm.get("detalle") else "")
        f["premieres"] = g.get("premier_inicial", "—")
        vc = g.get("voto_confianza") or {}
        f["confianza"] = f"{vc['a_favor']} a favor, {vc['en_contra']} en contra, {vc.get('abstenciones', '?')} abstenciones ({vc.get('fecha', '')})" if isnum(vc.get("a_favor")) else (vc.get("nota") or "sin dato")
        fa = g.get("facultades_delegadas_100d") or {}
        f["facultades"] = (f"Sí: {fa.get('ley', '')} ({fa.get('plazo_dias', '?')} días de {fa.get('plazo_pedido_dias', '?')} pedidos)" if fa.get("otorgadas")
                           else (fa.get("detalle") or fa.get("nota") or "No identificadas"))
        f["inv_src"] = "prensa"
        f["urls"] = [u for u in (cm.get("fuente_url"), vc.get("fuente_url"), fa.get("fuente_url")) if u]
    for mi in ido["ministros"][:1]:
        f["urls"] += mi.get("fuentes", [])[:1]
    f["ext"] = [e for e in D["idoneidad"]["evaluaciones_externas"] if e["gabinete"] == GOV[k]["idn"]]
    return f


SERIES = [("tc", "PD04638PD", "Tipo de cambio", "S/ por US$; arriba = sol más débil"),
          ("embig", "PD04709XD", "Riesgo país (EMBIG)", "spread; arriba = más riesgo"),
          ("bvl", "PD38026MD", "Bolsa de Valores de Lima", "índice general"),
          ("cobre", "PD04701XD", "Cobre (control externo)", "no depende del gobierno")]


def eco_series(k):
    """{key: dict(pts=[(dia, indice)], d0, d100, d0f, d100f, var, url, nota)} para la ventana de k."""
    y = GOV[k]["year"]
    from datetime import date
    t0 = date(y, 7, 28)
    out = {}
    if k in ("castillo", "keiko"):
        v = "v1" if k == "castillo" else "v2"
        for key, code, *_ in SERIES:
            s = next((x for x in D["indicadores"]["series"] if x.get("codigo_bcrp") == code), None)
            if not s:
                continue
            w = s[v]
            d0 = w["d0"]["valor"]; d100 = (w.get("d100") or {}).get("valor")
            nota = None; var = w.get("var_pct")
            if d100 is None and w.get("ultimo_disponible"):
                nota = f"serie diaria hasta el {fdate(w['ultimo_disponible']['fecha'])} ({fnum(w.get('var_pct_al_ultimo_disponible'), 1)} %)"
            out[key] = dict(serie=w["serie"], d0=d0, d100=d100, d0f=w["d0"]["fecha"], d100f=(w.get("d100") or {}).get("fecha"), var=var, url=s["fuente_url"], nota=nota)
    else:
        for key, code, *_ in SERIES:
            m = next((x for x in hist(k)["macro"] if x.get("codigo") == code), None)
            if not m:
                continue
            out[key] = dict(serie=m["serie"], d0=m["d0"], d100=m["d100"], d0f=m["d0_fecha"], d100f=m["d100_fecha"], var=m.get("var_pct"), url=m["fuente_url"], nota=None)
    for key, s in out.items():
        pts = []
        for f, val in s["serie"]:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", f):
                continue
            dd = (date(*map(int, f.split("-"))) - t0).days + 1  # 28-jul = día 1
            if f >= s["d0f"] and dd <= 100 and isnum(val):
                pts.append((max(dd, 0), val / s["d0"] * 100))
        s["pts"] = pts
    return out


# ---------------------------------------------------------------- referencias
class Refs:
    def __init__(self):
        self.items: list[tuple[str, str]] = []
        self.idx: dict[str, int] = {}

    def __call__(self, url, label=None):
        if not url or not re.match(r"^https?://", str(url)):
            return ""
        url = str(url).strip()
        if url not in self.idx:
            self.items.append((url, label or host(url)))
            self.idx[url] = len(self.items)
        return f'<font name="{F["Archivo-SB"]}" size="6" color="{MUTED}"><super>[{self.idx[url]}]</super></font>'

    def many(self, urls):
        return "".join(self(u) for u in dict.fromkeys(u for u in urls if u))


# ---------------------------------------------------------------- estilos
def styles(accent):
    acc_ink = ink_of(accent)
    S = {}
    S["body"] = ParagraphStyle("body", fontName=F["Serif"], fontSize=9.2, leading=13.2, textColor=C(INK), spaceAfter=5)
    S["lede"] = ParagraphStyle("lede", parent=S["body"], fontSize=12, leading=17, spaceAfter=10)
    S["small"] = ParagraphStyle("small", parent=S["body"], fontSize=8, leading=11, textColor=C(INK2), spaceAfter=4)
    S["note"] = ParagraphStyle("note", fontName=F["Archivo"], fontSize=7.6, leading=10.6, textColor=C(MUTED), spaceAfter=6)
    S["kicker"] = ParagraphStyle("kicker", fontName=F["Archivo-SB"], fontSize=7.2, leading=9, textColor=C(acc_ink), spaceAfter=2)
    S["h1"] = ParagraphStyle("h1", fontName=F["ArchivoC-XB"], fontSize=18, leading=20, textColor=C(INK), spaceAfter=5, keepWithNext=1)
    S["h2"] = ParagraphStyle("h2", fontName=F["Archivo-SB"], fontSize=10.5, leading=13, textColor=C(INK), spaceBefore=8, spaceAfter=4, keepWithNext=0)
    S["cell"] = ParagraphStyle("cell", fontName=F["Archivo"], fontSize=7.6, leading=9.8, textColor=C(INK))
    S["cellb"] = ParagraphStyle("cellb", parent=S["cell"], fontName=F["Archivo-SB"])
    S["cells"] = ParagraphStyle("cells", parent=S["cell"], fontSize=6.6, leading=8.4, textColor=C(MUTED))
    S["cellsm"] = ParagraphStyle("cellsm", parent=S["cell"], fontSize=7, leading=8.8)
    S["cellr"] = ParagraphStyle("cellr", parent=S["cell"], alignment=TA_RIGHT)
    S["bul"] = ParagraphStyle("bul", parent=S["body"], fontSize=9, leading=12.8, leftIndent=10, bulletIndent=0, spaceAfter=3)
    S["ref"] = ParagraphStyle("ref", fontName=F["Archivo"], fontSize=5.9, leading=7.3, textColor=C(INK2), leftIndent=16, firstLineIndent=-16, spaceAfter=1.6, splitLongWords=1)
    S["acc"] = acc_ink
    return S


class Rule(Flowable):
    def __init__(self, width=None, color=RULE, thick=0.6, space=4):
        super().__init__(); self.w = width; self.c = color; self.t = thick; self.sp = space

    def wrap(self, aw, ah):
        self.aw = self.w or aw; return self.aw, self.sp * 2

    def draw(self):
        self.canv.setStrokeColor(C(self.c)); self.canv.setLineWidth(self.t); self.canv.line(0, self.sp, self.aw, self.sp)


def section(S, kicker, title, refs_txt=""):
    return [CondPageBreak(42 * mm), P(esc(kicker).upper(), S["kicker"]), P(esc(title) + refs_txt, S["h1"]), Rule(color=INK, thick=1.1, space=3), Spacer(1, 4)]


def h2(text, S, need=30 * mm):
    return [CondPageBreak(need), P(text, S["h2"])]


def bullets(items, S, style="bul"):
    return [P(t, S[style], bulletText="•") for t in items]


def img(fig, width_pt, dpi=220):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    ir = ImageReader(buf)
    w, h = ir.getSize()
    buf.seek(0)
    return Image(buf, width=width_pt, height=width_pt * h / w)


def chip_cell(score, main, sub, S, size=11):
    b = band(score)
    bg, fg, lab = SEM[b]
    st = ParagraphStyle("chip", fontName=F["Archivo-XB"], fontSize=size, leading=size + 1.5, textColor=C(fg))
    st2 = ParagraphStyle("chip2", fontName=F["Archivo"], fontSize=6.6, leading=8.2, textColor=C(fg))
    return [P(main, st), P(esc(sub if sub is not None else lab), st2)], bg


# ---------------------------------------------------------------- página
class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__)); self._startPage()

    def save(self):
        n = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st)
            if getattr(self, "_deco", None):
                self._deco(self, n)
            super().showPage()
        super().save()


PW, PH = A4
ML, MR, MT, MB = 21 * mm, 21 * mm, 24 * mm, 22 * mm


def make_doc(path, title, accent, header_right, cover_fn, cover_h=None):
    """cover_h: alto de la portada en la página 1 (None = portada a página completa)."""
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
                          title=title, author="Carlos Cárdenas", subject="100 días bajo la lupa", creator=URL)
    fr = Frame(ML, MB, PW - ML - MR, PH - MT - MB, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    fr1 = Frame(ML, MB, PW - ML - MR, PH - (cover_h or 0) - 8 * mm - MB, id="f1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0) if cover_h else fr

    def deco(c, total):
        pg = c.getPageNumber()
        if pg == 1 and not cover_h:
            return
        c.saveState()
        if pg > 1:
            c.setFillColor(C(accent)); c.rect(ML, PH - 15 * mm, 9, 9, stroke=0, fill=1)
            c.setFont(F["Archivo-SB"], 7); c.setFillColor(C(INK))
            c.drawString(ML + 14, PH - 15 * mm + 1.5, "100 DÍAS BAJO LA LUPA")
            c.setFont(F["Archivo"], 7); c.setFillColor(C(MUTED))
            c.drawRightString(PW - MR, PH - 15 * mm + 1.5, header_right)
            c.setStrokeColor(C(RULE)); c.setLineWidth(0.6); c.line(ML, PH - 17.5 * mm, PW - MR, PH - 17.5 * mm)
        c.setStrokeColor(C(RULE)); c.setLineWidth(0.6)
        c.line(ML, 15.5 * mm, PW - MR, 15.5 * mm)
        c.setFont(F["Archivo-SB"], 7); c.setFillColor(C(INK))
        c.drawString(ML, 11.3 * mm, URL_SHORT)
        c.setFont(F["Archivo"], 6.6); c.setFillColor(C(MUTED))
        c.drawString(ML, 8.2 * mm, CREDIT)
        txt = f"Página {pg} de {total}"
        c.setFont(F["Archivo-SB"], 7.4); c.setFillColor(C(INK))
        c.drawRightString(PW - MR, 10.2 * mm, txt)
        c.restoreState()

    def on_page(c, d):
        c._deco = deco
        if c.getPageNumber() == 1:
            cover_fn(c)

    doc.addPageTemplates([PageTemplate(id="cover", frames=[fr1], onPage=on_page), PageTemplate(id="body", frames=[fr], onPage=on_page)])
    return doc


def build(doc, story):
    doc.build(story, canvasmaker=NumberedCanvas)


# ---------------------------------------------------------------- gráficos
def style_ax(ax, grid_y=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(RULE); ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=MUTED, labelsize=7, length=2)
    if grid_y:
        ax.yaxis.grid(True, color="#ece9e2", lw=0.6); ax.set_axisbelow(True)


def chart_approval(highlight=None, width_in=6.4):
    data = [(k, approvals(k)) for k in ORDER]
    fig, ax = plt.subplots(figsize=(width_in, 0.42 * len(data) + 0.55))
    for i, (k, a) in enumerate(reversed(data)):
        y = i; f, l = a["first"]["aprueba"], a["last"]["aprueba"]
        col = GOV[k]["color"]
        dim = highlight and k != highlight
        c = mix(col, "#ffffff", 0.62) if dim else col
        ax.plot([f, l], [y, y], color=c, lw=3 if not dim else 2, solid_capstyle="round", zorder=2)
        ax.scatter([f], [y], s=46, facecolor="white", edgecolor=c, lw=1.8, zorder=3)
        ax.scatter([l], [y], s=58, color=c, edgecolor="white", lw=1.2, zorder=4)
        right = l >= f
        ax.text(l + (2.2 if right else -2.2), y, f"{fnum(l, 0)} %", va="center", ha="left" if right else "right",
                fontsize=8, fontweight="semibold", color=INK if not dim else MUTED)
        ax.text(f + (-2.2 if right else 2.2), y, fnum(f, 0), va="center", ha="right" if right else "left", fontsize=7, color=MUTED)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([f"{GOV[k]['short']} {GOV[k]['year']}" for k, _ in reversed(data)], fontsize=8, color=INK)
    ax.set_xlim(0, 100); ax.set_ylim(-0.6, len(data) - 0.4)
    ax.axvline(50, color=RULE, lw=0.8, ls=(0, (3, 3)), zorder=1)
    ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels([f"{v} %" for v in (0, 25, 50, 75, 100)])
    style_ax(ax, grid_y=False); ax.xaxis.grid(True, color="#ece9e2", lw=0.6); ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    return fig


def chart_markets_single(k, width_in=3.4):
    S = eco_series(k); col = GOV[k]["color"]
    fig, axes = plt.subplots(2, 2, figsize=(width_in, 2.75))
    for ax, (key, code, title, sub) in zip(axes.flat, SERIES):
        style_ax(ax)
        ax.set_title(title, fontsize=7.5, color=INK, loc="left", fontweight="semibold", pad=10)
        s = S.get(key)
        if not s or not s["pts"]:
            ax.text(0.5, 0.5, "sin dato", transform=ax.transAxes, ha="center", va="center", color=MUTED, fontsize=8)
            ax.set_yticks([]); ax.set_xticks([0, 50, 100]); ax.set_xlim(0, 100)
            ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=5.8, color=MUTED, va="bottom")
            continue
        xs, ys = zip(*s["pts"])
        ax.axhline(100, color=RULE, lw=0.8, ls=(0, (3, 3)))
        ax.plot(xs, ys, color=col, lw=1.6)
        ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["día 1", "50", "100"])
        lo, hi = min(ys + (100,)), max(ys + (100,)); pad = max(1.5, (hi - lo) * 0.18)
        ax.set_ylim(lo - pad, hi + pad)
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=5.8, color=MUTED, va="bottom")
    fig.subplots_adjust(wspace=0.42, hspace=0.95)
    return fig


def chart_markets_all(width_in=6.6):
    S = {k: eco_series(k) for k in ORDER}
    fig, axes = plt.subplots(2, 2, figsize=(width_in, 4.3))
    for ax, (key, code, title, sub) in zip(axes.flat, SERIES):
        style_ax(ax)
        ax.set_title(f"{title}", fontsize=8, color=INK, loc="left", fontweight="semibold", pad=11)
        ax.text(0, 1.015, f"índice: día 1 = 100 · {sub}", transform=ax.transAxes, fontsize=6.2, color=MUTED, va="bottom")
        ax.axhline(100, color=RULE, lw=0.8, ls=(0, (3, 3)))
        for k in ORDER:
            s = S[k].get(key)
            if not s or not s["pts"]:
                continue
            xs, ys = zip(*s["pts"])
            ax.plot(xs, ys, color=GOV[k]["color"], lw=1.9 if k in ("castillo", "keiko") else 1.2, label=f"{GOV[k]['short']} {GOV[k]['year']}")
        ax.set_xlim(0, 100); ax.set_xticks([1, 25, 50, 75, 100]); ax.set_xticklabels(["día 1", "25", "50", "75", "100"])
    h, l = axes.flat[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(hspace=0.55, wspace=0.22, bottom=0.12)
    return fig


def chart_sensitivity(width_in=6.4):
    Sx = I["sensibilidad"]
    rows = [k for k in ORDER if k in Sx]
    fig, ax = plt.subplots(figsize=(width_in, 2.2))
    for x0, x1, b in ((0, 30, "r"), (30, 50, "o"), (50, 70, "y"), (70, 100, "g")):
        ax.axvspan(x0, x1, color=mix(SEM[b][0], "#ffffff", 0.82), lw=0, zorder=0)
        ax.text((x0 + x1) / 2, len(rows) - 0.42, SEM[b][2], ha="center", va="bottom", fontsize=6.8, color=MUTED)
    for i, k in enumerate(reversed(rows)):
        r = Sx[k]; col = GOV[k]["color"]; tot = I["gobiernos"][k]["total"]
        ax.plot([r["p5"], r["p95"]], [i, i], color=col, lw=6, solid_capstyle="round", alpha=0.55, zorder=2)
        ax.scatter([r["p50"]], [i], s=40, color="white", edgecolor=col, lw=1.6, zorder=3)
        ax.scatter([tot], [i], s=60, marker="D", color=col, edgecolor="white", lw=1, zorder=4)
        ax.text(r["p95"] + 1.5, i, f"{fnum(r['p5'], 0)}–{fnum(r['p95'], 0)}", va="center", fontsize=7.4, color=INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{GOV[k]['short']} {GOV[k]['year']}" for k in reversed(rows)], fontsize=8.2)
    ax.set_xlim(0, 100); ax.set_ylim(-0.6, len(rows) - 0.1)
    style_ax(ax, grid_y=False); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Índice de los 100 días (0-100)", fontsize=7.4, color=MUTED)
    return fig


def chart_ck_dims(width_in=6.4):
    dims = [d for d in I["dimensiones"] if d["peso"]]
    fig, ax = plt.subplots(figsize=(width_in, 0.46 * len(dims) + 0.7))
    for x0, x1, b in ((0, 30, "r"), (30, 50, "o"), (50, 70, "y"), (70, 100, "g")):
        ax.axvspan(x0, x1, color=mix(SEM[b][0], "#ffffff", 0.84), lw=0, zorder=0)
    for i, d in enumerate(reversed(dims)):
        a = I["gobiernos"]["castillo"]["dims"][d["id"]]["score"]; b = I["gobiernos"]["keiko"]["dims"][d["id"]]["score"]
        ax.plot([a, b], [i, i], color="#9aa0aa", lw=1.4, zorder=2)
        for v, k in ((a, "castillo"), (b, "keiko")):
            ax.scatter([v], [i], s=62, color=GOV[k]["color"], edgecolor="white", lw=1.1, zorder=3)
        lo, hi = (a, "castillo"), (b, "keiko")
        if a > b:
            lo, hi = hi, lo
        ax.text(lo[0] - 2.4, i, fnum(lo[0], 0), ha="right", va="center", fontsize=7.4, color=ink_of(GOV[lo[1]]["color"]), fontweight="semibold")
        ax.text(hi[0] + 2.4, i, fnum(hi[0], 0), ha="left", va="center", fontsize=7.4, color=ink_of(GOV[hi[1]]["color"]), fontweight="semibold")
    ax.set_yticks(range(len(dims))); ax.set_yticklabels([f"{d['nombre']} ({d['peso']} %)" for d in reversed(dims)], fontsize=7.8)
    ax.set_xlim(0, 100); ax.set_ylim(-0.6, len(dims) - 0.4)
    style_ax(ax, grid_y=False); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=GOV[k]["color"], label=f"{GOV[k]['short']} {GOV[k]['year']}") for k in ("castillo", "keiko")],
              loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=False, fontsize=7.6)
    return fig


# ---------------------------------------------------------------- bloques de tabla
def tbl(data, widths, style_cmds, repeat=1):
    t = Table(data, colWidths=widths, repeatRows=repeat)
    base = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    t.setStyle(TableStyle(base + style_cmds))
    return t


def promise_bar(pb, width, height=14):
    from reportlab.graphics.shapes import Drawing, Rect, String
    d = Drawing(width, height + 12)
    if not pb.get("total"):
        d.add(Rect(0, 12, width, height, fillColor=C(SUNK), strokeColor=None))
        d.add(String(6, 12 + height / 2 - 3, "sin balance cuantitativo independiente", fontName=F["Archivo"], fontSize=7, fillColor=C(MUTED)))
        return d
    segs = [(pb["c"], "#1e7e3a"), (pb["p"], "#f6c744"), (pb["n"], "#b9b5ac"), (pb["u"], "#e2dfd8")]
    x = 0
    for n, col in segs:
        if n:
            w = width * n / pb["total"]
            d.add(Rect(x, 12, w - 1, height, fillColor=C(col), strokeColor=None))
            if w > 14:
                d.add(String(x + 3, 12 + height / 2 - 2.6, str(n), fontName=F["Archivo-SB"], fontSize=7, fillColor=C(on_color(col))))
            x += w
    return d


def legend_promises(S, labels):
    cols = ["#1e7e3a", "#f6c744", "#b9b5ac", "#e2dfd8"]
    return P("  ".join(f'<font color="{c}">■</font> {esc(l)}' for c, l in zip(cols, labels)), S["note"])


# =============================================================== INFORME POR GOBIERNO
def verdict_sentences(k):
    g = I["gobiernos"][k]; Sx = I["sensibilidad"]; name = GOV[k]["short"]
    tot = g.get("total")
    if isnum(tot):
        r = g["rango"]
        s1 = (f"En el índice experimental de los 100 días, {name} obtiene <b>{fnum(tot)} sobre 100</b> ({SEM[band(tot)][2].lower()}). "
              f"Con otros pesos y fórmulas (20 000 simulaciones), su total queda entre {fnum(r['p5'], 0)} y {fnum(r['p95'], 0)}.")
    else:
        s1 = (f"No existe un balance independiente de las promesas de {name} a los 100 días, así que el índice no calcula su total. "
              f"En el núcleo común (gabinete, confianza e inversión), que existe para los cinco gobiernos, obtiene <b>{fnum(g['total_comun'])}</b> "
              f"({SEM[band(g['total_comun'])][2].lower()}). El núcleo común no equivale al total: deja fuera las promesas y la cadena de valor.")
    if k in ("castillo", "keiko"):
        s2 = (f"Castillo y Keiko no se pueden distinguir: sus rangos se superponen ({fnum(Sx['castillo']['p5'], 0)}–{fnum(Sx['castillo']['p95'], 0)} frente a "
              f"{fnum(Sx['keiko']['p5'], 0)}–{fnum(Sx['keiko']['p95'], 0)}) y Castillo queda arriba solo en el {round(Sx['p_castillo_mayor_keiko'] * 100)} % de las simulaciones. "
              f"Lo que sí se sostiene: PPK (2016) queda por encima de ambos en el {round(Sx['p_ppk_primero'] * 100)} % de las simulaciones.")
    elif k == "ppk":
        s2 = (f"Es el único resultado del índice que resiste el análisis de sensibilidad: PPK queda por encima de Castillo y de Keiko en el "
              f"{round(Sx['p_ppk_primero'] * 100)} % de las simulaciones. Ese margen descansa sobre todo en la estabilidad de su gabinete y en un balance de promesas (Convoca) "
              "que midió metas anunciadas por el Ejecutivo, meses después del día 100.")
    else:
        s2 = ("Sin total, no entra en la comparación de rangos del índice. Su fila del semáforo sirve para leer cada dimensión por separado, "
              "con las mismas reglas que se aplican a los otros cuatro gobiernos.")
    items = [p for p in promise_items(k) if p["lvl"] and is_done(p["estado"])]
    cnt = {lv: sum(1 for p in items if p["lvl"] == lv) for lv in LEVELS}
    parts = [f"{cnt[lv]} {lv if cnt[lv] == 1 else lv + ('es' if lv.endswith('d') else 's')}" for lv in LEVELS if cnt[lv]]
    s3 = (f"<b>Valor público.</b> Ninguna promesa cumplida por completo llega al escalón de resultado. Lo cumplido de {name} que pudimos clasificar: "
          f"{', '.join(parts) if parts else 'ninguna promesa'}. A los 100 días se juzga la dirección y la capacidad de gestión; el valor público todavía no se puede medir.")
    return s1, s2, s3


def gov_report(k):
    G = GOV[k]; acc = G["color"]; S = styles(acc); R = Refs()
    g = I["gobiernos"][k]
    path = OUT / G["file"]
    tot = g.get("total"); tb = band(tot if isnum(tot) else g.get("total_comun"))
    ap = approvals(k); pb = promise_balance(k)

    COVER_H = 112 * mm

    def cover(c):
        c.saveState()
        bh = 80 * mm
        c.setFillColor(C(acc)); c.rect(0, PH - bh, PW, bh, stroke=0, fill=1)
        fg = on_color(acc)
        c.setFillColor(C(fg))
        c.setFont(F["Archivo-SB"], 8); c.drawString(ML, PH - 18 * mm, "100 DÍAS BAJO LA LUPA  ·  INFORME POR GOBIERNO")
        c.setFont(F["ArchivoC-XB"], 44)
        c.drawString(ML - 2, PH - 42 * mm, G["name"])
        c.setFont(F["Serif"], 14)
        c.drawString(ML, PH - 53 * mm, f"Los primeros 100 días: 28 de julio – 4 de noviembre de {G['year']}")
        c.setFont(F["Archivo"], 7.8)
        c.drawString(ML, PH - bh + 9 * mm, "Promesas · cadena de valor · gabinete · aprobación · mercados · inversión · resultados · contexto internacional · hitos")
        c.setFont(F["Archivo"], 7.2)
        c.drawString(ML, PH - bh + 4.5 * mm, "Día 100 = 4 de noviembre (el 28 de julio cuenta como día 1). Corte de datos: 7 de noviembre de 2026. Misma estructura para los cinco gobiernos.")
        # cifra y KPIs
        yb = PH - bh - 7 * mm
        c.setFillColor(C(INK)); c.setFont(F["Archivo-SB"], 7); c.drawString(ML, yb, "ÍNDICE DE LOS 100 DÍAS")
        bg, fgc, lab = SEM[band(tot)] if isnum(tot) else SEM["na"]
        c.setFillColor(C(bg)); c.roundRect(ML, yb - 24 * mm, 50 * mm, 21 * mm, 3, stroke=0, fill=1)
        c.setFillColor(C(fgc))
        if isnum(tot):
            c.setFont(F["ArchivoC-XB"], 32); c.drawString(ML + 4 * mm, yb - 14.5 * mm, fnum(tot))
            c.setFont(F["Archivo-SB"], 7.6); c.drawString(ML + 4 * mm, yb - 20.5 * mm, f"{lab}  ·  rango {fnum(g['rango']['p5'], 0)}–{fnum(g['rango']['p95'], 0)}")
        else:
            c.setFont(F["ArchivoC-XB"], 20); c.drawString(ML + 4 * mm, yb - 12 * mm, "sin total")
            c.setFont(F["Archivo-SB"], 7.4); c.drawString(ML + 4 * mm, yb - 19 * mm, f"núcleo común {fnum(g['total_comun'])} ({SEM[band(g['total_comun'])][2]})")
        kp = [("Promesas|cumplidas", f"{pb['c']} de {pb['total']}" if pb.get("total") else "sin balance"),
              ("Aprobación|Ipsos/Apoyo", f"{fnum(ap['first']['aprueba'], 0)} → {fnum(ap['last']['aprueba'], 0)} %"),
              ("Ministros del día 1|que siguen al día 100", gov_facts(k)["siguen"]),
              ("Inversión ago-oct|% del PIM (GN)", re.match(r"([\d.]+) %", g["dims"]["D7"]["valor"]).group(1).replace(".", ",") + " %")]
        x0 = ML + 56 * mm; colw = (PW - MR - x0) / 4
        for i, (lab2, val) in enumerate(kp):
            xx = x0 + i * colw
            c.setStrokeColor(C(RULE)); c.setLineWidth(0.6); c.line(xx - 3 * mm, yb + 2, xx - 3 * mm, yb - 24 * mm)
            c.setFillColor(C(MUTED)); c.setFont(F["Archivo"], 6.6)
            l1, l2 = lab2.split("|")
            c.drawString(xx, yb, l1); c.drawString(xx, yb - 3 * mm, l2)
            c.setFillColor(C(INK)); c.setFont(F["ArchivoC-XB"], 15); c.drawString(xx, yb - 13 * mm, val)
        c.linkURL(URL, (ML, 8 * mm, ML + 140, 14 * mm), relative=0)
        c.restoreState()

    doc = make_doc(path, f"Los 100 días de {G['name']} ({G['year']})", acc, f"{G['name']} · {G['year']}", cover, cover_h=COVER_H)
    st = [NextPageTemplate("body")]

    # ---- 1. resumen ejecutivo
    st += [P("RESUMEN EJECUTIVO", S["kicker"]), Rule(color=INK, thick=1.1, space=3), Spacer(1, 2)]
    s1, s2, s3 = verdict_sentences(k)
    bg = SEM[tb][0]
    vlabel = (f"Veredicto del índice: {SEM[band(tot)][2]} · {fnum(tot)} / 100 · rango {fnum(g['rango']['p5'], 0)}–{fnum(g['rango']['p95'], 0)}" if isnum(tot)
              else f"Veredicto del índice: sin total · núcleo común {fnum(g['total_comun'])} / 100 ({SEM[band(g['total_comun'])][2]})")
    box = Table([[P(esc(vlabel), ParagraphStyle("vb", fontName=F["Archivo-XB"], fontSize=10.5, leading=13, textColor=C(INK)))],
                 [P(s1, S["body"])], [P(s2, S["body"])]], colWidths=[PW - ML - MR - 14])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C(mix(bg, "#ffffff", 0.86))), ("LINEBEFORE", (0, 0), (0, -1), 4, C(bg)),
                             ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, 0), 8),
                             ("BOTTOMPADDING", (0, -1), (-1, -1), 4), ("TOPPADDING", (0, 1), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -2), 1)]))
    st += [box, Spacer(1, 8), P(s3, S["body"])]

    # ---- 2. semáforo
    st += section(S, "Índice experimental · 7 dimensiones", "Su fila del semáforo")
    rows = [[P("Dimensión (peso)", S["cellb"]), P("Puntaje", S["cellb"]), P("Dato y fuente", S["cellb"])]]
    cmds = [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK))]
    for i, d in enumerate(I["dimensiones"], start=1):
        c = g["dims"][d["id"]]
        peso = f"{d['peso']} %" if d["peso"] else "fuera del total"
        if isnum(c["score"]):
            cell, bgc = chip_cell(c["score"], fnum(c["score"], 0), None, S)
        else:
            cell, bgc = chip_cell(None, esc(c.get("corto") or "sin dato"), "fuera del total" if not d["peso"] else "sin dato", S, size=8.4)
        src = esc(c.get("fuente") or "")
        rows.append([[P(f"<b>{esc(d['nombre'])}</b> <font color='{MUTED}'>({peso})</font>", S["cell"])], cell,
                     [P(esc(comma_dec(c["valor"])), S["cell"]), P(src, S["cells"]) if src else Spacer(1, 0)]])
        cmds += [("BACKGROUND", (1, i), (1, i), C(bgc)), ("LINEBELOW", (0, i), (-1, i), 0.4, C(RULE))]
    n = len(rows)
    if isnum(tot):
        cell, bgc = chip_cell(tot, fnum(tot), f"{SEM[band(tot)][2]} · rango {fnum(g['rango']['p5'], 0)}–{fnum(g['rango']['p95'], 0)}", S, size=13)
        txt = (f"Promedio ponderado del núcleo (promesas, cadena de valor, gabinete, confianza e inversión). En el 90 % de las 20 000 simulaciones queda entre "
               f"{fnum(g['rango']['p5'])} y {fnum(g['rango']['p95'])} (mediana {fnum(g['rango']['p50'])}).")
    else:
        cell, bgc = chip_cell(None, "—", "sin balance de promesas", S, size=13)
        txt = "Sin balance de promesas: no se calcula el total (solo se calcula si hay dato en las cinco dimensiones del núcleo)."
    rows.append([P("<b>Índice de los 100 días</b>", S["cell"]), cell, P(txt, S["cell"])])
    cmds += [("BACKGROUND", (1, n), (1, n), C(bgc)), ("LINEABOVE", (0, n), (-1, n), 0.9, C(INK))]
    cell, bgc = chip_cell(g["total_comun"], fnum(g["total_comun"]), None, S, size=11)
    rows.append([P("<b>Núcleo común</b>", S["cell"]), cell, P("Solo gabinete, confianza e inversión: las tres dimensiones que existen para los cinco gobiernos.", S["cell"])])
    cmds += [("BACKGROUND", (1, n + 1), (1, n + 1), C(bgc))]
    st += [tbl(rows, [55 * mm, 31 * mm, PW - ML - MR - 86 * mm], cmds),
           P("Semáforo: verde ≥ 70 (bien), amarillo 50-69 (regular), naranja 30-49 (malo), rojo &lt; 30 (crítico), gris = sin dato o fuera del total. "
                     "La integridad (D4) y la veracidad (D5) se muestran pero no suman: los conteos de integridad salen de fuentes distintas según el año y la veracidad solo se verificó para el mensaje de Keiko.", S["note"])]

    # ---- 3. promesas
    st += section(S, "Promesas y cadena de valor público", "Las promesas", R(pb.get("url")))
    if pb.get("total"):
        st += [P(f"<b>{pb['c']} cumplidas de {pb['total']}</b> según {esc(pb['src'])}" + (f"; {pb['p']} en proceso" if pb["p"] else "") +
                         f"; {pb['n']} {esc(pb['labels'][2].lower())}" + (f"; {pb['u']} en otras categorías o no verificables" if pb["u"] else "") + ".", S["body"]),
               promise_bar(pb, PW - ML - MR), legend_promises(S, pb["labels"])]
        if pb.get("met"):
            st.append(P(f"<b>Cómo se midió.</b> {esc(pb['met'])}" + (f" {esc(pb['nota'])}" if pb.get("nota") else ""), S["small"]))
        if k == "keiko":
            A = D["pp2050_cumplimiento"]["cien_dias"]["acciones"]
            cnt = {s: sum(1 for a in A if a["estado_verificado"] == s) for s in ("con_norma", "anunciado", "sin_evidencia")}
            st.append(P(f"<b>Segunda medición</b> (Plan Perú 2050, normas en El Peruano): {cnt['con_norma']} con norma publicada (avance, no cumplimiento), "
                                f"{cnt['anunciado']} solo anunciadas y {cnt['sin_evidencia']} sin evidencia, de {len(A)}. Ninguna cumplida." + R(D['pp2050_cumplimiento']['meta'].get('origen_url')), S["small"]))
    else:
        st += [P(f"<b>Sin dato.</b> {esc(pb.get('met') or 'No se encontró un balance cuantitativo de promesas a los 100 días.')}", S["body"]), promise_bar(pb, PW - ML - MR)]
    its = promise_items(k)
    done = [p for p in its if p["lvl"] and is_done(p["estado"])]
    other = [p for p in its if p not in done]
    st += h2("Lo cumplido, escalón por escalón de la cadena de valor", S)
    st.append(P("Insumo → actividad → producto → resultado → impacto. Una promesa «cumplida» puede ser solo un insumo (una ley o un presupuesto); el valor público aparece arriba, "
                        "cuando cambia la vida de la gente. La clasificación es propia y otra persona podría ubicar alguna promesa un escalón más arriba o más abajo.", S["note"]))
    lad = [[P(f"<b>{lv.capitalize()}</b><br/><font size=6.4 color='{MUTED}'>{LEVEL_DEF[lv]}</font>", S["cell"]),
            [P("• " + esc(p["texto"]) + R(p["url"]), S["cell"]) for p in done if p["lvl"] == lv] or
            [P("Ninguna promesa llegó aquí" if LEVELS.index(lv) >= 3 else "—", S["cells"])]] for lv in LEVELS]
    lcmds = [("LINEBELOW", (0, 0), (-1, -2), 0.4, C(RULE))]
    for i, lv in enumerate(LEVELS):
        if any(p["lvl"] == lv for p in done):
            lcmds.append(("BACKGROUND", (0, i), (0, i), C(mix(acc, "#ffffff", 0.8))))
    st.append(tbl(lad, [38 * mm, PW - ML - MR - 38 * mm], lcmds, repeat=0))
    if other:
        st += h2("En proceso, parciales o pendientes al día 100 (promesas revisadas)", S)
        rows = [[P("Promesa", S["cellb"]), P("Estado", S["cellb"]), P("Escalón", S["cellb"])]]
        for p in other:
            rows.append([P(esc(p["texto"]) + R(p["url"]), S["cellsm"]), P(esc(comma_dec(p["estado"]).replace("_", " ")), S["cells"]), P(esc(p["lvl"] or "—"), S["cells"])])
        st.append(tbl(rows, [84 * mm, PW - ML - MR - 102 * mm, 18 * mm], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE)),
                                                                     ("TOPPADDING", (0, 1), (-1, -1), 2.4), ("BOTTOMPADDING", (0, 1), (-1, -1), 2.4)]))

    # ---- 4. gabinete
    f = gov_facts(k)
    st += section(S, "Gobernabilidad", "El gabinete", R.many(f["urls"]))
    kv = [("Premier", f["premieres"]), ("Estabilidad", f"{f['siguen']} ministros del día 1 siguen en el cargo al día 100. {f['cambios']}."),
          ("Idoneidad (0-100)", f"{f['idoneidad']}/100. Experiencia directiva previa en su sector: {f['exp_n']} de {f['exp_N']}; formación acorde al puesto: {f['form_n']} de {f['form_N']} (codificación propia, sin revisión independiente)."),
          ("Investigaciones reportadas", f"{f['inv']} ministros con investigación o proceso reportado (fuente: {f['inv_src']}). Ninguna investigación es una condena."),
          ("Voto de confianza", f["confianza"]), ("Facultades y normas", f["facultades"])]
    rows = [[P(f"<b>{esc(a)}</b>", S["cell"]), P(esc(comma_dec(b) if a != "Premier" else b), S["cell"])] for a, b in kv]
    st.append(tbl(rows, [36 * mm, PW - ML - MR - 36 * mm], [("LINEBELOW", (0, 0), (-1, -1), 0.4, C(RULE)), ("BACKGROUND", (0, 3), (-1, 3), C(SUNK))], repeat=0))
    st.append(P("<b>Advertencia de comparabilidad.</b> " + esc(D["idoneidad"]["caveats"][1]) + " " + esc(D["idoneidad"]["caveats"][2]), S["note"]))
    if f["ext"]:
        st.append(P("<b>Evaluaciones externas citadas:</b> " + " ".join(f"{esc(e['fuente'])} ({fdate(e['fecha'])}): {esc(e['hallazgo'])}{R(e['url'])}" for e in f["ext"]), S["small"]))

    # ---- 5. aprobación y mercados
    a1, a2 = ap["first"], ap["last"]
    k1 = ap["key"](a1); k2 = ap["key"](a2)
    E = eco_series(k)
    st += section(S, "Confianza ciudadana y contexto económico", "Aprobación y mercados", R.many([a1.get("fuente_url"), a2.get("fuente_url")] + [s_["url"] for s_ in E.values()]))
    st.append(P(f"Primera medición: <b>{fnum(a1['aprueba'], 0)} %</b> ({esc(a1['encuestadora'])}, {esc(fdate(k1))}). Última medición publicada antes del día 100: "
                        f"<b>{fnum(a2['aprueba'], 0)} %</b> ({esc(a2['encuestadora'])}, {esc(fdate(k2))}). "
                        f"Diferencia: {'+' if a2['aprueba'] - a1['aprueba'] > 0 else ''}{fnum(a2['aprueba'] - a1['aprueba'], 0)} puntos. "
                        f"En el índice (D6), la caída se compara con la esperada para quien empieza en ese nivel: {esc(comma_dec(g['dims']['D6']['valor']))}.", S["body"]))
    half = (PW - ML - MR) / 2 - 8
    cap = ParagraphStyle("cap", parent=S["cellb"], fontSize=7.8, spaceAfter=2)
    left = [P("Aprobación: primera medición → última antes del día 100", cap), img(chart_approval(highlight=k, width_in=3.4), half),
            P("○ primera · ● última antes del 4-nov. Misma regla para los cinco; fuentes y diseños de muestra varían.", S["note"])]
    right = [P("Mercados en su ventana (día 1 = 100)", cap), img(chart_markets_single(k), half),
             P("Contexto, no evaluación: los mercados también reaccionan a la Fed, al cobre y a China.", S["note"])]
    t2 = Table([[left, right]], colWidths=[half + 8, half + 8])
    t2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    st.append(t2)
    mk = []
    for key, code, title, sub in SERIES:
        s_ = E.get(key)
        if not s_:
            mk.append(f"<b>{title}:</b> sin dato"); continue
        d100 = f"{fsem(s_['d100'])} ({fdate(s_['d100f'])})" if isnum(s_["d100"]) else f"sin dato al día 100; {esc(s_['nota'] or '')}"
        var = f" → <b>{'+' if (s_['var'] or 0) > 0 else ''}{fnum(s_['var'], 1)} %</b>" if isnum(s_["var"]) else ""
        mk.append(f"<b>{title}:</b> {fsem(s_['d0'])} ({fdate(s_['d0f'])}) → {d100}{var}")
    st.append(P(" · ".join(mk) + ". Fuente: BCRPData.", S["small"]))

    # ---- 7. inversión y resultados
    T = D["performance"]["totales_gobierno_nacional"].get(str(G["year"]), {})
    mef = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx"
    st += section(S, "Ejecución y resultados", "Inversión, Estado y resultados", R(mef, "MEF – Consulta Amigable"))
    inv = [f"<b>Inversión en la ventana (D7):</b> {esc(comma_dec(g['dims']['D7']['valor']))}. Solo cuenta agosto-octubre, que es la gestión propia."]
    if T:
        inv.append(f"<b>Ejecución del Gobierno Nacional de enero a octubre:</b> {fnum(T['ActProy']['pct'])} % de todo el gasto y {fnum(T['Proyecto']['pct'])} % de los proyectos de inversión "
                   f"(devengado / PIM). El devengado de enero a julio corresponde al gobierno anterior.")
    conf = [c for c in D["performance"]["conflictos"] if c["anio"] == G["year"]]
    if conf:
        cs = [c for c in conf if isnum(c["total"])]
        inv.append("<b>Conflictos sociales (Defensoría):</b> " + " → ".join(f"{c['mes']}: {c['total']} ({c['activos']} activos)" for c in cs) + "." + R.many(c.get("fuente_url") for c in cs)
                   + (" El reporte de octubre aún no estaba publicado." if any(not isnum(c["total"]) for c in conf) else ""))
    if k == "keiko":
        inv.append("<b>PIM de 2026:</b> es el vigente al 7-nov (todavía puede crecer); el de los años cerrados es el PIM final. Eso favorece levemente a 2026 en la comparación.")
    st += bullets(inv, S, "small")
    Rz = D["resultados"]; yr = str(G["year"])
    st += h2("¿Se movió algún resultado?", S)
    if yr in Rz["ventanas"]:
        rows = [[P("Indicador", S["cellb"]), P("Antes → durante", S["cellb"]), P("Variación", S["cellb"])]]
        for ind in Rz["indicadores"]:
            r = ind.get(yr)
            if not r:
                continue
            a, b = (r.get("antes") or {}).get("valor"), (r.get("durante") or {}).get("valor")
            if isnum(a) and isnum(b):
                dv = (b / a - 1) * 100
                fm = lambda v: fnum(v, 0) if abs(v) >= 1000 else fnum(v, 1 if abs(v) < 20 else 0)
                vals = f"{fm(a)} → <b>{fm(b)}</b>"
                var = f"{'+' if dv > 0 else ''}{fnum(dv, 1)} %"
            else:
                vals = f"<font color='{MUTED}'>sin dato ({esc(a if a is not None else '—')})</font>"; var = "—"
            rows.append([P(f"{esc(ind['nombre'])}{R(ind.get('fuente_url'))} <font size=6.2 color='{MUTED}'>· {esc(ind['unidad'])}</font>", S["cell"]), P(vals, S["cell"]), P(var, S["cell"])])
        st.append(tbl(rows, [100 * mm, PW - ML - MR - 122 * mm, 22 * mm], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE)),
                                                                       ("TOPPADDING", (0, 1), (-1, -1), 2.4), ("BOTTOMPADDING", (0, 1), (-1, -1), 2.4)]))
        st.append(P("Ventanas: los 100 días previos frente a los 100 días de gobierno; las series mensuales comparan junio con octubre y las trimestrales, abr-jun con jul-sep.", S["note"]))
        st.append(P("<b>Lectura neutral.</b> " + esc(comma_dec(Rz["conclusion_neutral"])), S["note"]))
    else:
        st.append(P("<b>Sin dato.</b> El dashboard no construyó la comparación de indicadores de resultado (homicidios, empleo, inflación) para esta ventana. "
                            "Como en los demás gobiernos, 100 días casi nunca alcanzan para mover un indicador de resultado.", S["small"]))

    # ---- 8. contexto internacional
    st += section(S, "Índices internacionales anuales", "El país que recibió")
    st.append(P("Año previo a asumir → primer año de gobierno. Es contexto, no evaluación: estos índices son anuales y describen el país que recibió cada gobierno y su primer año, "
                        "no los 100 días." + (" Para Keiko solo existe la línea base." if k == "keiko" else "") + " Un verde en pobreza no significa que la pobreza sea baja, solo que es menor que en el pasado del Perú.", S["small"]))
    rows = [[P("Índice", S["cellb"]), P("Recibió → primer año", S["cellb"]), P("Escala", S["cellb"])]]
    cm2 = [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK))]
    for i, r in enumerate(I["contexto"], start=1):
        v = r["gobiernos"].get(k)
        if not v:
            cell, bgc = P("sin dato", ParagraphStyle("cx", fontName=F["Archivo-SB"], fontSize=7.2, leading=8.6, textColor=C(SEM["na"][1]))), SEM["na"][0]
        else:
            sx = lambda val, y: f"{fsem(val)}/10" if r["id"] == "cpi_score" and y and int(y) < 2012 else fsem(val)
            arrow = ""
            if isnum(v.get("score_primer")) and isnum(v.get("score_recibio")):
                arrow = "=" if abs(v["score_primer"] - v["score_recibio"]) < 0.5 else ("▲" if v["score_primer"] > v["score_recibio"] else "▼")
            main = f"{sx(v['recibio'], v['anio_recibio'])}" + (f" → {sx(v['primer'], v['anio_primer'])} {arrow}" if isnum(v.get("primer")) else " (base)")
            yrs = f"{v['anio_recibio'] or 's/d'}" + (f" → {v['anio_primer']}" if v.get("anio_primer") else "")
            sc = v["score_primer"] if isnum(v.get("score_primer")) else v.get("score_recibio")
            bgc, fgc, _ = SEM[band(sc)]
            cell = P(f"{main} <font name='{F['Archivo']}' size=5.8>{yrs}</font>", ParagraphStyle("cx", fontName=F["Archivo-SB"], fontSize=7.2, leading=8.6, textColor=C(fgc)))
        adv = "; ".join((r.get("advertencias") or {}).get(k, []))
        nm = short_idx(r["nombre"])
        rows.append([P(f"{esc(nm)}{R(r['fuente_url'])}", S["cell"]), cell, P(esc(r["escala_txt"].split(";")[0]) + (f" · <i>{esc(adv)}</i>" if adv else ""), S["cells"])])
        cm2 += [("BACKGROUND", (1, i), (1, i), C(bgc)), ("LINEBELOW", (0, i), (-1, i), 0.3, C(RULE))]
    st.append(tbl(rows, [64 * mm, 40 * mm, PW - ML - MR - 104 * mm], cm2 + [("TOPPADDING", (0, 1), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 1), (-1, -1), 2.2), ("VALIGN", (0, 1), (-1, -1), "MIDDLE")]))
    st.append(P("El color es el del último valor de la celda en su escala de 0 a 100 (mejor = 100): índices de escala fija por su escala; los sociales, por el rango histórico del Perú. "
                        "▲ mejoró y ▼ empeoró en el primer año. El CPI anterior a 2012 está en escala 0-10.", S["note"]))

    # ---- 9. hitos
    st += section(S, "Línea de tiempo", "Hitos de la ventana")
    hit = D["castillo"]["hitos"] if k == "castillo" else D["keiko"]["hitos"] if k == "keiko" else []
    lim = f"{G['year']}-11-04"
    hit = [h for h in hit if str(h["fecha"])[:10] <= lim]
    if hit:
        rows = [[P(f"<b>{esc(fdate(str(h['fecha'])[:10]))}</b>", S["cellsm"]), P(esc(h["texto"]) + R(h.get("fuente_url")), S["cellsm"])] for h in hit]
        st.append(tbl(rows, [20 * mm, PW - ML - MR - 20 * mm], [("LINEBELOW", (0, 0), (-1, -1), 0.3, C(RULE)), ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2)], repeat=0))
        st.append(P("Solo hechos ocurridos entre el 28 de julio y el 4 de noviembre (día 100). Fuentes de distintas líneas editoriales.", S["note"]))
    else:
        st.append(P("<b>Sin dato.</b> El dashboard construyó línea de tiempo solo para las ventanas de 2021 y 2026; para este gobierno no hay hitos verificados en el repositorio.", S["small"]))

    # ---- fuentes
    st += section(S, "Referencias", "Fuentes")
    st.append(P(f"Datos crudos y scripts: github.com/unimauro/cien-dias-peru (research/*.json, etl/). Índice: research/indice100.json, versión {I['version']}, generado el {I['generado']}.", S["note"]))
    st.append(ref_columns(R, S))
    build(doc, st)
    return path


def ref_columns(R, S):
    from reportlab.platypus.flowables import BalancedColumns
    items = [P(f"<b>{i}.</b> " + (f"{esc(lab)} · " if lab != host(u) else "") + f"<link href='{esc(u)}' color='{S['acc']}'>{esc(u)}</link>", S["ref"]) for i, (u, lab) in enumerate(R.items, start=1)]
    return BalancedColumns(items, nCols=2, spaceBefore=0, spaceAfter=0, innerPadding=10)


# =============================================================== COMPARATIVO
STAMP = {"v-ok": ("#1e7e3a", "✓"), "v-warn": ("#f08a3c", "!"), "v-bad": ("#c23a35", "✕"), "v-unk": ("#7a808c", "?")}


def stamp_cell(cls, label, S):
    col, ic = STAMP.get(cls, STAMP["v-unk"])
    st = ParagraphStyle("stamp", fontName=F["Archivo-XB"], fontSize=8, leading=10, textColor=C(on_color(col)))
    return P(f"{ic}  {esc(label).upper()}", st), col


def verdict_cls(v):
    s = str(v or "").lower()
    if s.startswith("falso"):
        return "v-bad"
    if re.search(r"engañ|parcial|exager|impreciso|prematur|matiz|insuficiente", s):
        return "v-warn"
    if re.match(r"^verdadero$|^cierto$", s):
        return "v-ok"
    return "v-unk"


def comparativo():
    acc = INK; S = styles("#2a78d6"); S["acc"] = "#1f5fae"; R = Refs()
    path = OUT / "comparativo.pdf"
    Sx = I["sensibilidad"]

    def cover(c):
        c.saveState()
        c.setFillColor(C(INK)); c.rect(0, 0, PW, PH, stroke=0, fill=1)
        sw = PW / 5
        for i, k in enumerate(ORDER):
            c.setFillColor(C(GOV[k]["color"])); c.rect(i * sw, PH - 14 * mm, sw, 14 * mm, stroke=0, fill=1)
        c.setFillColor(C("#ffffff")); c.setFont(F["Archivo-SB"], 8.5)
        c.drawString(ML, PH - 32 * mm, "PERÚ · PRIMEROS 100 DÍAS DE GOBIERNO · INFORME COMPARATIVO")
        c.setFont(F["ArchivoC-XB"], 64)
        c.drawString(ML - 3, PH - 72 * mm, "100 días")
        c.drawString(ML - 3, PH - 94 * mm, "bajo la lupa")
        c.setFont(F["Serif"], 15); c.setFillColor(C("#d9dce3"))
        c.drawString(ML, PH - 110 * mm, "Keiko Fujimori (2026) frente a Pedro Castillo (2021),")
        c.drawString(ML, PH - 117 * mm, "con García (2006), Humala (2011) y PPK (2016) como vara histórica")
        # mini semáforo de totales
        y0 = PH - 150 * mm
        c.setFont(F["Archivo-SB"], 7.5); c.setFillColor(C("#aab0bb")); c.drawString(ML, y0 + 8 * mm, "ÍNDICE EXPERIMENTAL DE LOS 100 DÍAS (0-100) · RANGO DEL 5 % AL 95 %")
        bw = (PW - ML - MR - 4 * 4) / 5
        for i, k in enumerate(ORDER):
            gg = I["gobiernos"][k]; x = ML + i * (bw + 4)
            tt = gg.get("total"); b = band(tt) if isnum(tt) else "na"
            c.setFillColor(C(GOV[k]["color"])); c.rect(x, y0, bw, 2.2, stroke=0, fill=1)
            c.setFillColor(C("#ffffff")); c.setFont(F["Archivo-SB"], 8.5); c.drawString(x, y0 - 6 * mm, f"{GOV[k]['short']} {GOV[k]['year']}")
            c.setFillColor(C(SEM[b][0] if isnum(tt) else "#3a404c")); c.roundRect(x, y0 - 27 * mm, bw, 18 * mm, 3, stroke=0, fill=1)
            c.setFillColor(C(SEM[b][1] if isnum(tt) else "#c9ccd3"))
            if isnum(tt):
                c.setFont(F["ArchivoC-XB"], 24); c.drawString(x + 3 * mm, y0 - 18.5 * mm, fnum(tt))
                c.setFont(F["Archivo"], 7); c.drawString(x + 3 * mm, y0 - 24 * mm, f"rango {fnum(gg['rango']['p5'], 0)}–{fnum(gg['rango']['p95'], 0)}")
            else:
                c.setFont(F["ArchivoC-XB"], 13); c.drawString(x + 3 * mm, y0 - 16 * mm, "sin total")
                c.setFont(F["Archivo"], 6.6); c.drawString(x + 3 * mm, y0 - 22.5 * mm, f"núcleo común {fnum(gg['total_comun'])}")
        c.setFillColor(C("#e8eaee")); c.setFont(F["Serif-It"], 11)
        tx = c.beginText(ML, PH - 196 * mm); tx.setLeading(15.5)
        for ln in ["Castillo y Keiko no se pueden distinguir con estos datos: sus rangos se superponen.",
                   f"PPK queda por encima de ambos en el {round(Sx['p_ppk_primero'] * 100)} % de las 20 000 simulaciones.",
                   "Ninguno llega al día 100 con resultados de valor público medibles."]:
            tx.textLine(ln)
        c.drawText(tx)
        c.setStrokeColor(C("#3a404c")); c.line(ML, 40 * mm, PW - MR, 40 * mm)
        c.setFont(F["Archivo"], 8); c.setFillColor(C("#aab0bb"))
        c.drawString(ML, 33 * mm, "Día 100 = 4 de noviembre (el 28 de julio cuenta como día 1). Corte de datos: 7 de noviembre de 2026.")
        c.drawString(ML, 28.5 * mm, "Versión corregida tras cinco revisiones adversariales (cifras, metodología, sesgo, QA y afirmaciones).")
        c.setFont(F["Archivo-SB"], 8.5); c.setFillColor(C("#ffffff")); c.drawString(ML, 20 * mm, URL_SHORT)
        c.linkURL(URL, (ML, 19 * mm, ML + 160, 24 * mm), relative=0)
        c.setFont(F["Archivo"], 7.4); c.setFillColor(C("#aab0bb")); c.drawString(ML, 15.5 * mm, CREDIT)
        c.restoreState()

    doc = make_doc(path, "100 días bajo la lupa: informe comparativo", "#161a22", "Informe comparativo · 2006-2026", cover)
    st = [Spacer(1, 1), NextPageTemplate("body"), PageBreak()]
    W = PW - ML - MR

    # ---- conclusión
    st += section(S, "La conclusión", "La conclusión, sin relato")
    st.append(P(esc(comma_dec(ED["lede"])), S["lede"]))
    for h in ED["hyps"]:
        cell, col = stamp_cell(h["cls"], h["label"], S)
        t = Table([[cell, [P(esc(h["title"]), ParagraphStyle("ht", fontName=F["Archivo-SB"], fontSize=10, leading=12.5, textColor=C(INK), spaceAfter=3)),
                           P(esc(comma_dec(h["text"])), S["body"])]]], colWidths=[34 * mm, W - 34 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), C(col)), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("LINEBELOW", (0, 0), (-1, -1), 0.4, C(RULE)), ("LEFTPADDING", (1, 0), (1, 0), 10)]))
        st += [t, Spacer(1, 6)]
    # ledger
    st += [PageBreak()] + section(S, "Castillo 2021 · Keiko 2026", "Dónde avanzó y dónde se quedó corto cada uno")
    cols = []
    for k in ("castillo", "keiko"):
        cc = [P(f"<font color='{GOV[k]['color']}'>■</font> {GOV[k]['short']} {GOV[k]['year']}", ParagraphStyle("lh", fontName=F["ArchivoC-XB"], fontSize=15, leading=18, textColor=C(INK), spaceAfter=4))]
        for h4, lis in ED["ledger"].get(k, []):
            cc.append(P(esc(h4).upper(), ParagraphStyle("lk", parent=S["kicker"], textColor=C(ink_of(GOV[k]["color"])), spaceBefore=6)))
            cc += bullets([esc(comma_dec(x)) for x in lis], S, "small")
        cols.append(cc)
    t = Table([cols], colWidths=[W / 2, W / 2]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 14),
                                                                       ("LINEBEFORE", (1, 0), (1, 0), 0.5, C(RULE)), ("LEFTPADDING", (1, 0), (1, 0), 12)]))
    st += [t, Spacer(1, 6), P(esc(ED["note"]), S["small"])]

    # ---- veredictos infografías
    fc = D["factcheck"]; b = fc["infografia_b"]; a = fc["infografia_a"]
    vc = b["verificacion_castillo"]
    kg = next(t for t in D["keiko"]["trackers"] if re.search("keiko gobierna", t["nombre"], re.I))
    kbody = (f"El dato existe: «Keiko Gobierna» es un tracker ciudadano, independiente y de código abierto, que al día 103 registra {kg['cumplidas']} cumplidas, {kg['en_proceso']} en proceso "
             f"y {kg['sin_avance']} sin avance de las {kg['total']} acciones de «Primeros 100 días» del plan «Perú con Orden». El «0 %» es correcto. Lo engañoso es el «100 % no cumplidas»: "
             "suma las 3 en proceso, y «sin avance» solo significa que no hay una norma publicada en El Peruano que lo acredite, no que se haya incumplido. Otros balances dan cifras parecidas: "
             "Hildebrandt en sus Trece, 1 de 67; el Observatorio de Planes de Gobierno, avances en 6 de 68.")
    claims = [(vc["veredicto"], "Engañoso", "«Castillo cumplió 3 de 43 promesas (7 %) y no cumplió 40 (93 %)»", "Infografía «Primeros 100 días: Castillo vs. Keiko»", vc["hechos"], vc.get("fuentes", [])),
              ("engañoso en la forma", "Engañoso en la forma", "«Keiko no registra ninguna de 67 promesas cumplidas (0 %)»", "Misma infografía; cita a «Keiko Gobierna (2026)»", kbody, [kg["url"]]),
              (a["veredicto_global"], "Engañoso", "«Colegios en el gobierno de Keiko: 0 construidos, 4 destruidos»", f"Infografía firmada por {a['autor'].split(' (')[0]}", a["resumen_global"], []),
              (a["construidos_check"]["veredicto"], "Engañoso", "«0 colegios construidos»", "Misma infografía", a["construidos_check"]["veredicto"].split("(", 1)[1].rstrip(")").capitalize() + ".",
               [o["fuente"] for o in a["construidos_check"].get("obras_culminadas_o_entregadas_en_periodo", [])][:3])]
    st += [PageBreak()] + section(S, "Veredictos", "Lo que circula, contra los datos")
    S["claim"] = ParagraphStyle("claim", parent=S["small"], fontSize=7.7, leading=10.2, spaceAfter=0)
    st.append(P("Cada afirmación viral recibe un veredicto: verdadero, engañoso, falso o no verificado.", S["small"]))
    for v, lab, title, src, body, urls in claims:
        cell, col = stamp_cell(verdict_cls(v), lab, S)
        inner = [P(esc(title), ParagraphStyle("ct", fontName=F["Archivo-SB"], fontSize=9.6, leading=12, textColor=C(INK))),
                 P(esc(src), S["cells"]), Spacer(1, 2), P(esc(comma_dec(body)) + R.many(urls), S["claim"])]
        t = Table([[cell, inner]], colWidths=[34 * mm, W - 34 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), C(col)), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                               ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LINEBELOW", (0, 0), (-1, -1), 0.4, C(RULE)), ("LEFTPADDING", (1, 0), (1, 0), 10)]))
        st += [t, Spacer(1, 3)]
    rows = [[P(esc(it["colegio"]) + R.many(it.get("fuentes", [])), S["cell"]), P(esc(it["veredicto"]), S["cells"])] for it in a["items"]]
    st += [P("Los 4 colegios «destruidos», uno por uno", S["h2"]),
           tbl([[P("Caso", S["cellb"]), P("Veredicto", S["cellb"])]] + rows, [W - 58 * mm, 58 * mm], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE))]),
           P("Por qué «3 de 43» y «0 de 67» no son comparables", S["h2"])] + bullets([esc(comma_dec(p)) for p in b["problemas_metodologicos"] if "no localizable" not in p], S, "claim")

    # ---- semáforo completo (página completa)
    st += [PageBreak()] + section(S, "Índice experimental · 5 gobiernos", "Semáforo de los 100 días")
    st.append(P(esc(ED["sem_intro"]), S["small"]))
    cw = [W - 5 * 23.5 * mm] + [23.5 * mm] * 5
    head = [P("Dimensión <font color='%s'>(peso)</font>" % MUTED, S["cellb"])] + [P(f"<font color='{GOV[k]['color']}'>■</font> {GOV[k]['short']} {GOV[k]['year']}", S["cellb"]) for k in ORDER]
    rows = [head]; cmds = [("LINEBELOW", (0, 0), (-1, 0), 0.9, C(INK)), ("VALIGN", (1, 0), (-1, -1), "MIDDLE")]
    for i, d in enumerate(I["dimensiones"], start=1):
        peso = f"{d['peso']} %" if d["peso"] else "fuera del total"
        r = [[P(f"<b>{esc(d['nombre'])}</b> <font color='{MUTED}'>({peso})</font>", S["cell"]), P(esc(d["desc"]), S["cells"])]]
        for j, k in enumerate(ORDER, start=1):
            c = I["gobiernos"][k]["dims"][d["id"]]
            if isnum(c["score"]):
                cell, bgc = chip_cell(c["score"], fnum(c["score"], 0), None, S, size=12)
            else:
                cell, bgc = chip_cell(None, esc(c.get("corto") or "sin dato"), "fuera del total" if not d["peso"] else "sin dato", S, size=6.8)
            r.append(cell); cmds.append(("BACKGROUND", (j, i), (j, i), C(bgc)))
        rows.append(r); cmds.append(("LINEBELOW", (0, i), (-1, i), 1.5, C("#ffffff")))
    n = len(rows)
    r = [[P("<b>Índice de los 100 días</b>", S["cell"]), P("Promedio ponderado del núcleo. Debajo, el rango del 5 % al 95 % de 20 000 simulaciones con otros pesos y fórmulas.", S["cells"])]]
    r2 = [[P("<b>Núcleo común</b>", S["cell"]), P("Solo gabinete, confianza e inversión: existen para los cinco gobiernos.", S["cells"])]]
    for j, k in enumerate(ORDER, start=1):
        gg = I["gobiernos"][k]
        if isnum(gg.get("total")):
            cell, bgc = chip_cell(gg["total"], fnum(gg["total"]), f"rango {fnum(gg['rango']['p5'], 0)}–{fnum(gg['rango']['p95'], 0)}", S, size=13)
        else:
            cell, bgc = chip_cell(None, "—", "sin balance de promesas", S, size=13)
        r.append(cell); cmds.append(("BACKGROUND", (j, n), (j, n), C(bgc)))
        cell, bgc = chip_cell(gg["total_comun"], fnum(gg["total_comun"]), None, S, size=11)
        r2.append(cell); cmds.append(("BACKGROUND", (j, n + 1), (j, n + 1), C(bgc)))
    rows += [r, r2]; cmds += [("LINEABOVE", (0, n), (-1, n), 1.1, C(INK)), ("LINEBELOW", (0, n), (-1, n), 1.5, C("#ffffff"))]
    st.append(tbl(rows, cw, cmds))
    st.append(P("Verde ≥ 70 (bien) · amarillo 50-69 (regular) · naranja 30-49 (malo) · rojo &lt; 30 (crítico) · gris: sin dato o fuera del total. "
                        "En las celdas grises de integridad y veracidad se muestran los conteos crudos, que no suman al total.", S["note"]))

    # ---- sensibilidad
    st += [PageBreak()] + section(S, "Incertidumbre", "Análisis de sensibilidad: rangos y probabilidades")
    st.append(P(f"El total depende mucho de los pesos y de las fórmulas. Por eso publicamos el rango del 5 % al 95 % de 20 000 simulaciones: si los rangos de dos gobiernos se superponen, "
                        f"no se pueden distinguir. Castillo supera a Keiko en el {round(Sx['p_castillo_mayor_keiko'] * 100)} % de las simulaciones; PPK queda primero en el {round(Sx['p_ppk_primero'] * 100)} %.", S["body"]))
    st.append(img(chart_sensitivity(), W))
    st.append(P("Barra: rango del 5 % al 95 % · ○ mediana de las simulaciones · ◆ total con los pesos publicados. Fondo: bandas del semáforo.", S["note"]))
    rows = [[P(x, S["cellb"]) for x in ("Gobierno", "Total publicado", "Percentil 5", "Mediana", "Percentil 95", "Núcleo común")]]
    for k in ORDER:
        gg = I["gobiernos"][k]; rr = Sx.get(k)
        rows.append([P(f"<font color='{GOV[k]['color']}'>■</font> {GOV[k]['short']} {GOV[k]['year']}", S["cell"]),
                     P(fnum(gg.get("total")) if isnum(gg.get("total")) else "sin total", S["cell"]),
                     *[P(fnum(rr[p]) if rr else "—", S["cell"]) for p in ("p5", "p50", "p95")],
                     P(fnum(gg["total_comun"]), S["cell"])])
    st.append(tbl(rows, [W - 5 * 25 * mm] + [25 * mm] * 5, [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE))]))
    st.append(P(esc(comma_dec(Sx["nota"])), S["note"]))
    st += bullets([f"<b>Probabilidad de que Castillo supere a Keiko:</b> {round(Sx['p_castillo_mayor_keiko'] * 100)} %. Es casi una moneda al aire: con estos datos no se puede decir cuál lo hizo peor.",
                   f"<b>Probabilidad de que PPK quede primero entre los tres con total:</b> {round(Sx['p_ppk_primero'] * 100)} %. Es lo único del orden que resiste.",
                   "<b>García y Humala</b> no tienen balance de promesas: solo tienen núcleo común, que no es comparable con el total.",
                   "El «empate exacto» de la primera versión (40,6 frente a 40,3) no era robusto: hoy decimos «no distinguibles»."], S, "small")

    # ---- Castillo vs Keiko por dimensión
    st += [PageBreak()] + section(S, "Castillo 2021 frente a Keiko 2026", "La comparación, dimensión por dimensión")
    st.append(P("Fallaron de formas distintas: el perfil de cada uno compensa al otro, y por eso el total no los separa.", S["small"]))
    st.append(img(chart_ck_dims(), W))
    rows = [[P("Dimensión", S["cellb"])] + [P(f"<font color='{GOV[k]['color']}'>■</font> {GOV[k]['short']} {GOV[k]['year']}", S["cellb"]) for k in ("castillo", "keiko")]]
    for d in I["dimensiones"]:
        rr = [P(f"<b>{esc(d['nombre'])}</b>" + ("" if d["peso"] else f" <font color='{MUTED}'>(fuera del total)</font>"), S["cell"])]
        for k in ("castillo", "keiko"):
            c = I["gobiernos"][k]["dims"][d["id"]]
            sc = f"<b>{fnum(c['score'], 0)}</b> · " if isnum(c["score"]) else ""
            rr.append(P(sc + esc(comma_dec(c["valor"])), S["cell"]))
        rows.append(rr)
    st.append(tbl(rows, [44 * mm, (W - 44 * mm) / 2, (W - 44 * mm) / 2], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE))]))

    # ---- promesas, aprobación y mercados de los cinco
    st += [PageBreak()] + section(S, "Los cinco gobiernos", "Promesas, aprobación y mercados")
    rows = [[P("Gobierno y fuente", S["cellb"]), P("Balance de promesas a los 100 días", S["cellb"]), P("Cumplidas", S["cellb"])]]
    bw = W - 48 * mm - 22 * mm - 12
    for k in ORDER:
        pb = promise_balance(k)
        rows.append([P(f"<font color='{GOV[k]['color']}'>■</font> <b>{GOV[k]['short']} {GOV[k]['year']}</b><br/><font size=6.4 color='{MUTED}'>{esc(pb.get('src') or 'sin balance')}</font>" + R(pb.get("url")), S["cell"]),
                     promise_bar(pb, bw, 11), P(f"<b>{fnum(pb['c'] / pb['total'] * 100, 0)} %</b><br/>{pb['c']} de {pb['total']}" if pb.get("total") else "—", S["cell"])])
    st.append(tbl(rows, [48 * mm, bw + 10, 22 * mm], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE)), ("VALIGN", (1, 1), (1, -1), "MIDDLE")]))
    st.append(legend_promises(S, ("Cumplidas", "En proceso", "No cumplidas / sin avance", "Otras / no verificables")))
    st.append(P("<b>Ojo con comparar porcentajes.</b> Cada balance cuenta una lista distinta con su propio criterio: El Comercio 2021 evaluó promesas del plan y de los anuncios; "
                        "Keiko Gobierna solo acredita normas en El Peruano; Convoca 2016 evaluó las promesas que el propio Ejecutivo anunció, meses después del día 100.", S["note"]))
    st.append(KeepTogether([P("Aprobación presidencial (Ipsos/Apoyo): primera medición → última antes del día 100", S["h2"]), img(chart_approval(None, 6.2), W - 20)]))
    st.append(KeepTogether([P("Mercados indexados (día 1 = 100)", S["h2"]), img(chart_markets_all(), W)]))
    st.append(P("Fuente: BCRPData (series diarias). El EMBIG diario de 2026 termina el 3-sep en BCRPData. Las ventanas históricas no incluyen el cobre. "
                        "Los mercados reflejan también el contexto global; no se atribuyen causalmente a ningún gobierno." + R("https://estadisticas.bcrp.gob.pe/estadisticas/series/", "BCRPData"), S["note"]))

    # ---- mapa de calor internacional
    st += [PageBreak()] + section(S, "Contexto internacional", "El país que recibieron: mapa de calor")
    st.append(P(esc(ED["intl_note"]), S["small"]))
    dimlab = {"corrupcion": "Corrupción", "democracia": "Democracia", "estado_de_derecho": "Estado de derecho", "efectividad": "Efectividad del gobierno", "libertades": "Libertades",
              "desigualdad": "Desigualdad", "pobreza": "Pobreza", "desarrollo_humano": "Desarrollo humano", "confianza": "Confianza ciudadana", "seguridad": "Seguridad"}
    head = [P("Índice", S["cellb"])] + [P(f"<font color='{GOV[k]['color']}'>■</font> {GOV[k]['short']}", S["cellb"]) for k in ORDER]
    rows = [head]; cmds = [("LINEBELOW", (0, 0), (-1, 0), 0.9, C(INK)), ("VALIGN", (1, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 1), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 1), (-1, -1), 1.8)]
    cs = ParagraphStyle("hm", fontName=F["Archivo-SB"], fontSize=7.2, leading=8.6)
    for grp in dict.fromkeys(r["dimension"] for r in I["contexto"]):
        i = len(rows)
        rows.append([P(dimlab.get(grp, grp).upper(), ParagraphStyle("gr", parent=S["kicker"], textColor=C(MUTED)))] + [""] * 5)
        cmds += [("SPAN", (0, i), (-1, i)), ("TOPPADDING", (0, i), (-1, i), 4), ("LINEBELOW", (0, i), (-1, i), 0.4, C(RULE))]
        for r in [x for x in I["contexto"] if x["dimension"] == grp]:
            i = len(rows)
            nm = short_idx(r["nombre"])
            row = [P(f"{esc(nm)}{R(r['fuente_url'], r['institucion'])} <font size=5.8 color='{MUTED}'>{esc(r['escala_txt'].split(';')[0])}</font>", S["cellsm"])]
            for j, k in enumerate(ORDER, start=1):
                v = r["gobiernos"].get(k)
                if not v:
                    row.append(P("—", ParagraphStyle("na", parent=cs, textColor=C(SEM["na"][1])))); cmds.append(("BACKGROUND", (j, i), (j, i), C(SEM["na"][0]))); continue
                sx = lambda val, y: f"{fsem(val)}/10" if r["id"] == "cpi_score" and y and int(y) < 2012 else fsem(val)
                arrow = ""
                if isnum(v.get("score_primer")) and isnum(v.get("score_recibio")):
                    arrow = " =" if abs(v["score_primer"] - v["score_recibio"]) < 0.5 else (" ▲" if v["score_primer"] > v["score_recibio"] else " ▼")
                main = sx(v["recibio"], v["anio_recibio"]) + (f" → {sx(v['primer'], v['anio_primer'])}{arrow}" if isnum(v.get("primer")) else " (base)")
                sc = v["score_primer"] if isnum(v.get("score_primer")) else v.get("score_recibio")
                bgc, fgc, _ = SEM[band(sc)]
                row.append(P(main, ParagraphStyle("hc", parent=cs, textColor=C(fgc)))); cmds.append(("BACKGROUND", (j, i), (j, i), C(bgc)))
            rows.append(row); cmds.append(("LINEBELOW", (0, i), (-1, i), 1.2, C("#ffffff")))
    st.append(tbl(rows, [W - 5 * 23 * mm] + [23 * mm] * 5, cmds))
    st.append(P("Año previo a asumir → primer año de gobierno. El color corresponde al último valor de la celda en su escala de 0 a 100 (mejor = 100). ▲ mejoró y ▼ empeoró en el primer año. "
                        "El CPI anterior a 2012 está en escala 0-10; RSF cambió de metodología en 2022.", S["note"]))

    # ---- metodología
    st += [PageBreak()] + section(S, "Cómo se hizo", "Metodología")
    st += bullets([esc(comma_dec(m)) for m in I["metodo"]], S, "small")
    st += h2("Las siete dimensiones", S)
    rows = [[P("Dimensión", S["cellb"]), P("Peso", S["cellb"]), P("Qué mide", S["cellb"])]]
    for d in I["dimensiones"]:
        rows.append([P(f"<b>{d['id']}</b> · {esc(d['nombre'])}", S["cell"]), P(f"{d['peso']} %" if d["peso"] else "fuera", S["cell"]), P(esc(d["desc"]), S["cells"])])
    st.append(tbl(rows, [52 * mm, 14 * mm, W - 66 * mm], [("LINEBELOW", (0, 0), (-1, 0), 0.8, C(INK)), ("LINEBELOW", (0, 1), (-1, -1), 0.3, C(RULE))]))
    st += bullets(["Ventana: del 28 de julio (asunción) al 4 de noviembre (día 100, contando el 28-jul como día 1) de cada año. Cuando no hay dato ese día, se usa el último día hábil.",
                   "Series macro tomadas directamente de la API del BCRPData, con el código de serie verificado contra su metadata. Resultados con datos de INEI, SINADEF/MINSA y MEF.",
                   "Diez líneas de investigación paralelas, asistidas por IA, cada una con su propia fuente de verdad (archivos en /research del repositorio). Enlaces validados el 7-nov-2026."], S, "small")

    # ---- límites
    st += section(S, "Lo que no sabemos", "Límites")
    groups = [("Índice y promesas", D["expresidentes"]["caveats"][5:7]), ("Castillo 2021", D["castillo"]["caveats"][:3]), ("Keiko 2026", D["keiko"]["caveats"][1:4]),
              ("Gabinetes e idoneidad", D["idoneidad"]["caveats"][1:5]), ("Mercados e inversión", D["indicadores"]["caveats"][:2] + D["indicadores"]["caveats"][4:5]),
              ("Resultados", D["resultados"]["caveats"][:3]), ("Planes de gobierno", D["planes"]["caveats"][:2])]
    for t_, cv in groups:
        cv = [x if isinstance(x, str) else x.get("texto", "") for x in cv]
        if cv:
            st += h2(esc(t_), S)
            st += bullets([esc(comma_dec(x)) for x in cv], S, "small")

    # ---- correcciones
    st += section(S, "Revisión adversarial", "Qué corregimos tras la revisión adversarial")
    st += bullets([esc(x) for x in FIXES], S, "bul")
    st.append(P("Criterio aplicado en este informe: día 100 = 4-nov; aprobación = última medición publicada antes del día 100; Castillo y Keiko «no distinguibles»; "
                        "Pensión 65 a S/700 todavía no pagada al día 100 (insumo, primer pago el 30-nov); 9 cambios de ministro de Castillo; "
                        "0 de 67 acciones cumplidas de Keiko, con 3 en progreso. Los informes de revisión están en /review del repositorio.", S["note"]))

    # ---- fuentes
    st += [CondPageBreak(60 * mm)] + section(S, "Referencias", "Fuentes")
    st.append(P("Datos crudos y scripts: github.com/unimauro/cien-dias-peru (research/*.json, etl/). Cada informe por gobierno trae sus propias fuentes numeradas.", S["note"]))
    st.append(ref_columns(R, S))
    build(doc, st)
    return path


def main():
    setup_fonts()
    assert len(ED["hyps"]) == 3 and len(ED["ledger"]) == 2, "no se pudo leer #conclusion de index.html"
    OUT.mkdir(exist_ok=True)
    # controles de coherencia con el dashboard (no se cambian cifras: si fallan, se detiene)
    exp = {"garcia": (63, 57), "humala": (55, 62), "ppk": (61, 55), "castillo": (38, 42), "keiko": (57, 40)}
    for k, (a, b) in exp.items():
        ap = approvals(k)
        assert (ap["first"]["aprueba"], ap["last"]["aprueba"]) == (a, b), (k, ap["first"]["aprueba"], ap["last"]["aprueba"])
    assert gov_facts("castillo")["cambios"].startswith("9 cambios")
    pk = promise_balance("keiko"); assert (pk["c"], pk["p"], pk["total"]) == (0, 3, 67)
    files = [comparativo()] + [gov_report(k) for k in ["keiko", "castillo", "ppk", "humala", "garcia"]]
    for p in files:
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    sys.exit(main())
