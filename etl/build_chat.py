#!/usr/bin/env python3
"""Arma data/chat.json: contexto compacto (< 120 KB) para el asistente «Pregúntale a los datos».

Lee research/*.json y produce fragmentos con etiquetas y fuentes. Lo usan:
  - el backend (deploy/api-tunky/cien.js), que recupera los fragmentos relevantes y se los pasa al modelo;
  - el widget (chat.js) en modo sin conexión, que busca por palabras clave y muestra los fragmentos.

Uso (desde la raíz del repo):  python3 etl/build_chat.py
Solo usa la biblioteca estándar.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "research"
OUT = RAIZ / "data" / "chat.json"
SITIO = "https://unimauro.github.io/cien-dias-peru/"
LIMITE = 120 * 1024

GOB = {
    "keiko": "Keiko Fujimori (2026)",
    "castillo": "Pedro Castillo (2021)",
    "ppk": "Pedro Pablo Kuczynski, PPK (2016)",
    "humala": "Ollanta Humala (2011)",
    "garcia": "Alan García (2006)",
}
ALIAS = {"garcia_2006": "garcia", "humala_2011": "humala", "ppk_2016": "ppk", "castillo_2021": "castillo", "keiko_2026": "keiko"}


def J(nombre):
    p = RES / f"{nombre}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # un archivo roto no debe tumbar todo el contexto
        print(f"aviso: no pude leer {p.name}: {e}", file=sys.stderr)
        return {}


def corto(s, n=420):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def urls(*xs):
    """Junta URLs de strings, listas o dicts (claves *url*/fuente*), sin repetir."""
    out = []

    def add(v):
        if isinstance(v, str) and v.startswith("http") and v not in out:
            out.append(v)
        elif isinstance(v, list):
            for i in v:
                add(i)
        elif isinstance(v, dict):
            for k, i in v.items():
                if "url" in k or "fuente" in k:
                    add(i)

    for x in xs:
        add(x)
    return out[:2]


def num(v, suf=""):
    if v is None:
        return "s/d"
    if isinstance(v, float):
        v = round(v, 2)
    return f"{v}{suf}"


FR = []


def frag(fid, sec, gob, titulo, texto, fuentes, tags=(), n=900):
    texto = corto(texto, n)
    if not texto:
        return
    gob = [g for g in (gob if isinstance(gob, list) else [gob]) if g]
    FR.append({
        "id": fid,
        "sec": sec,
        "gob": gob,
        "tags": sorted(set(t for t in tags if t and t != sec and t not in gob)),
        "t": corto(titulo, 140),
        "x": texto,
        "u": fuentes or [SITIO],
    })


# ---------------------------------------------------------------- conclusión
def conclusion():
    txt = ""
    try:
        h = (RAIZ / "index.html").read_text(encoding="utf-8")
        m = re.search(r'id="conclusion".*?</section>', h, re.S)
        if m:
            bloque = re.sub(r"<(script|style)\b.*?</\1>", " ", m.group(0), flags=re.S)
            txt = html.unescape(re.sub(r"<[^>]+>", " ", bloque))
            txt = re.sub(r"\s+", " ", txt)
            txt = re.sub(r'^.*?La conclusión, sin relato\s*', "", txt)  # quita el atributo y el título
            txt = re.sub(r"\s[≈?!]\s(?=[A-ZÁÉÍÓÚ])", " · ", txt).strip()  # íconos de los sellos
    except Exception:
        pass
    if len(txt) < 200:  # el HTML puede estar en rediseño: texto de respaldo
        txt = ("Ninguno de los dos llega al día 100 con resultados de valor público medibles. Con estos datos no se puede decir "
               "cuál lo hizo peor: en el índice experimental sus rangos se superponen. Fallaron de formas distintas: Castillo tuvo "
               "un gabinete inestable y poco idóneo; Keiko no cumplió ninguna de sus 67 acciones de 100 días según Keiko Gobierna "
               "y tuvo la mayor caída de aprobación de los cinco gobiernos comparados. Los dos están en rojo en promesas.")
    partes = [p.strip() for p in re.split(r"(?<=[.!?»])\s+(?=[A-ZÁÉÍÓÚÑ«¿])", txt) if p.strip()]
    # trozos de ~800 caracteres para que la recuperación sea fina
    trozo, n = "", 0
    for p in partes:
        if len(trozo) + len(p) > 800 and trozo:
            n += 1
            frag(f"conclusion-{n}", "conclusion", ["keiko", "castillo"], "La conclusión, sin relato" + (f" ({n})" if n > 1 else ""),
                 trozo, [SITIO + "#conclusion"], ["resumen", "veredicto", "quien", "peor", "mejor"])
            trozo = ""
        trozo += (" " if trozo else "") + p
    if trozo:
        n += 1
        frag(f"conclusion-{n}", "conclusion", ["keiko", "castillo"], "La conclusión, sin relato" + (f" ({n})" if n > 1 else ""),
             trozo, [SITIO + "#conclusion"], ["resumen", "veredicto", "quien", "peor", "mejor"])


# ---------------------------------------------------------------- índice v2
def indice():
    d = J("indice100")
    if not d:
        return
    s = d.get("sensibilidad", {})
    rng = lambda g: s.get(g, {})
    frag("indice-resumen", "indice", ["keiko", "castillo", "ppk"], f"Índice 100 días v{d.get('version')} (experimental): totales y rangos",
         "Índice propio y EXPERIMENTAL (0 a 100). " + "; ".join(
             f"{GOB[g]}: total {num(v.get('total'))}" + (f", rango p5–p95 {num(rng(g).get('p5'))}–{num(rng(g).get('p95'))} (mediana {num(rng(g).get('p50'))})" if rng(g) else "")
             + f", núcleo común {num(v.get('total_comun'))}"
             for g, v in d.get("gobiernos", {}).items() if g in GOB)
         + f". Castillo supera a Keiko en el {round(100 * (s.get('p_castillo_mayor_keiko') or 0))} % de las simulaciones y PPK queda primero en el "
         f"{round(100 * (s.get('p_ppk_primero') or 0))} %. Los rangos de Castillo y Keiko se superponen: NO son distinguibles. "
         "García y Humala no tienen total (sin balance de promesas), solo núcleo común. " + corto(s.get("nota"), 300),
         [SITIO + "#indice"], ["ranking", "puntaje", "rango", "simulaciones", "empate", "peor", "mejor", "nota"])
    for dim in d.get("dimensiones", []):
        vals = []
        for g, v in d.get("gobiernos", {}).items():
            x = (v.get("dims") or {}).get(dim.get("id"))
            if x and g in GOB:
                vals.append(f"{GOB[g]}: {num(x.get('score'))} ({corto(x.get('valor'), 140)})")
        frag(f"indice-{dim.get('id')}", "indice", list(GOB), f"Índice, {dim.get('id')} {dim.get('nombre')} (peso {dim.get('peso')} %)",
             corto(dim.get("desc"), 380) + " Valores: " + "; ".join(vals), [SITIO + "#indice"], ["dimension", "puntaje"])
    for i, m in enumerate(d.get("metodo", [])[:8], 1):
        frag(f"indice-metodo-{i}", "indice", [], "Método del índice", m, [SITIO + "#indice"], ["metodo", "metodologia", "advertencia"])


# ---------------------------------------------------------------- veredictos
def veredictos():
    f = J("factcheck")
    a = f.get("infografia_a") or {}
    if a:
        frag("veredicto-colegios", "veredictos", ["keiko"], f"Infografía «{a.get('titulo')}»: {a.get('veredicto_global')}",
             a.get("resumen_global"), [SITIO + "#veredictos"], ["infografia", "colegios", "escuelas", "destruidos", "helicoptero", "viral"])
        for it in a.get("items", []):
            frag(f"veredicto-colegio-{it.get('n')}", "veredictos", ["keiko"], f"Colegio {it.get('n')}: {corto(it.get('colegio'), 90)} ({it.get('veredicto')})",
                 f"Afirmación: {it.get('afirmacion')} Hechos: {it.get('hechos')}", urls(it.get("fuentes")), ["infografia", "colegios", "escuelas"])
        cc = a.get("construidos_check") or {}
        if cc:
            frag("veredicto-construidos", "veredictos", ["keiko"], f"«0 colegios construidos»: {cc.get('veredicto')}",
                 corto(cc.get("nota") or cc.get("afirmacion"), 600), urls(cc.get("fuentes")), ["infografia", "colegios", "construidos"])
    b = f.get("infografia_b") or {}
    for g in ("castillo", "keiko"):
        v = b.get(f"verificacion_{g}") or {}
        if v:
            frag(f"veredicto-promesas-{g}", "veredictos", [g], f"Infografía «{v.get('afirmacion')}»: {v.get('veredicto')}",
                 v.get("hechos"), urls(v.get("fuentes")), ["infografia", "promesas", "viral", "43", "67"])
    if b.get("comparabilidad"):
        frag("veredicto-comparabilidad", "veredictos", ["keiko", "castillo"], "¿Son comparables «3 de 43» y «0 de 67»?",
             b.get("comparabilidad"), [SITIO + "#veredictos"], ["infografia", "promesas", "comparable", "metodologia"])
    m = J("pp2050_mensaje")
    if m:
        r = m.get("resumen", {})
        vv = r.get("veredictos", {})
        frag("mensaje-resumen", "veredictos", ["keiko"], "Mensaje a la Nación de los 100 días (5-nov-2026), verificado",
             f"{r.get('n_afirmaciones')} afirmaciones con cifra: {vv.get('coincide')} coinciden, {vv.get('coincide_con_matices')} coinciden con matices, "
             f"{vv.get('no_coincide')} no coinciden y {vv.get('no_verificable')} no son verificables. " + " ".join(corto(x, 300) for x in m.get("analisis", [])[:3]),
             urls((m.get("meta") or {}).get("url"), (m.get("meta") or {}).get("origen_url")), ["mensaje", "discurso", "afirmaciones", "fact-check"])
        grupos = {}
        for af in m.get("afirmaciones", []):
            grupos.setdefault(af.get("veredicto"), []).append(af)
        for v, afs in grupos.items():  # una ficha por veredicto: lista de afirmaciones con su dato oficial
            frag(f"mensaje-{v}", "veredictos", ["keiko"], f"Mensaje de los 100 días: afirmaciones que «{str(v).replace('_', ' ')}» ({len(afs)})",
                 "; ".join(f"«{af.get('corto')}»" + (f" — {corto((af.get('verificacion') or [{}])[0].get('dato_oficial'), 110)}" if af.get("verificacion") else "") for af in afs),
                 urls([x.get("fuente_url") or x.get("url") for af in afs for x in af.get("verificacion") or []], (m.get("meta") or {}).get("url")),
                 ["mensaje", "discurso", "afirmaciones", str(v).replace("_", " ")], n=2200)

# ---------------------------------------------------------------- promesas
def promesas():
    k, c, e = J("keiko"), J("castillo"), J("expresidentes")
    ec = c.get("ecdata") or {}
    if ec:
        frag("promesas-castillo-ecdata", "promesas", ["castillo"], f"Castillo: balance de promesas de ECData ({ec.get('medio')})",
             f"De {ec.get('total')} promesas para los 100 días: {ec.get('cumplidas')} cumplidas, {ec.get('en_proceso')} en proceso, {ec.get('incumplidas')} incumplidas "
             f"({ec.get('inviables_dentro_de_incumplidas')} inviables). " + corto(ec.get("metodologia"), 400), urls(ec.get("fuente_url")),
             ["balance", "cumplidas", "43", "tracker"])
    for t in k.get("trackers", []):
        frag(f"promesas-keiko-tracker-{len(FR)}", "promesas", ["keiko"], f"Keiko: tracker {t.get('nombre')}",
             f"Total {num(t.get('total'))}: {num(t.get('cumplidas'))} cumplidas, {num(t.get('en_proceso'))} en proceso, {num(t.get('incumplidas'))} incumplidas"
             + (f", {t.get('sin_avance')} sin avance" if t.get("sin_avance") is not None else "") + ". "
             + ("; ".join(t.get("en_proceso_detalle") or [])[:300] + ". " if t.get("en_proceso_detalle") else "")
             + corto(t.get("metodologia"), 250) + (" Advertencia: " + corto(t.get("advertencia"), 200) if t.get("advertencia") else ""),
             urls(t.get("url")), ["balance", "cumplidas", "67", "68", "tracker"])
    base = J("promesas_base")
    if base.get("promesas"):
        promesas_base(base)
    else:  # respaldo: listas cortas de keiko.json y castillo.json
        for g, d in (("keiko", k), ("castillo", c)):
            for i, p in enumerate(d.get("promesas", []), 1):
                frag(f"promesa-{g}-{i}", "promesas", [g], f"{g.capitalize()}: {corto(p.get('texto'), 110)}",
                     f"Promesa: {p.get('texto')}. Estado: {p.get('estado')}. Eslabón: {p.get('nivel_cadena_valor')}. {corto(p.get('nota'), 350)}",
                     urls(p.get("fuente_url")), ["promesa", "cadena de valor"])
    if k.get("cadena_valor_resumen"):
        cv = k["cadena_valor_resumen"]
        cnt = cv.get("conteo_items_reportados_como_cumplidos_o_en_proceso", {})
        frag("cadena-keiko", "promesas", ["keiko"], "Keiko: cadena de valor de lo reportado",
             "Conteo: " + ", ".join(f"{a} {b}" for a, b in cnt.items()) + ". " + corto(cv.get("lectura"), 400), [SITIO + "#promesas"],
             ["cadena de valor", "valor publico", "resultado"])
    if c.get("evaluacion_cadena_valor"):
        cv = c["evaluacion_cadena_valor"]
        frag("cadena-castillo", "promesas", ["castillo"], "Castillo: cadena de valor de lo cumplido",
             corto(cv.get("conclusion"), 450) + " " + corto(cv.get("matiz_valor_publico"), 300), [SITIO + "#promesas"],
             ["cadena de valor", "valor publico", "resultado"])
    for key, g in (("garcia_2006", "garcia"), ("humala_2011", "humala"), ("ppk_2016", "ppk")):
        x = e.get(key) or {}
        bp = x.get("balance_promesas") or {}
        frag(f"promesas-{g}", "promesas", [g], f"{GOB[g]}: balance de promesas a los 100 días",
             (f"Total {num(bp.get('total'))}: {num(bp.get('cumplidas'))} cumplidas, {num(bp.get('incumplidas'))} incumplidas. " if bp.get("total") else "")
             + corto(bp.get("metodologia"), 350),
             urls(bp.get("fuente_url"), [p.get("fuente_url") for p in x.get("promesas_emblematicas") or []]), ["balance", "historico", "promesa"])


# ---------------------------------------------------------------- promesas_base (122 promesas, 5 gobiernos)
def promesas_base(b):
    est = b.get("estados") or {}
    ofi = b.get("balances_oficiales") or {}
    por = {}
    for p in b["promesas"]:
        por.setdefault(p.get("gobierno"), {}).setdefault(p.get("estado"), []).append(p)
    orden = ["cumplida", "parcial", "en_proceso", "anunciada", "incumplida", "no_verificable", "sin_evidencia"]
    for g, grupos in por.items():
        if g not in GOB:
            continue
        res = (b.get("resumen") or {}).get(g) or {}
        o = ofi.get(g) or {}
        frag(f"promesas-resumen-{g}", "promesas", [g], f"{GOB[g]}: promesas de 100 días en resumen",
             "Clasificación propia de las promesas recopiladas: " + ", ".join(f"{est.get(e, e).lower()} {res[e]}" for e in orden if res.get(e)) + ". "
             + (f"Balance publicado por {o.get('fuente')}: total {o.get('total')}, cumplidas {num(o.get('cumplidas'))}"
                + (f", en proceso {o.get('en_proceso')}" if o.get("en_proceso") is not None else "")
                + (f", incumplidas {o.get('incumplidas')}" if o.get("incumplidas") is not None else "")
                + (f", sin avance {o.get('sin_avance')}" if o.get("sin_avance") is not None else "") + ". " + corto(o.get("nota"), 200) if o else ""),
             urls([x for e in orden for p in grupos.get(e, []) for x in p.get("fuentes") or []]),
             ["balance", "cumplidas", "cumplio", "promesa", "tracker"], n=700)
        for e in orden:
            ps = grupos.get(e) or []
            if not ps:
                continue
            frag(f"promesas-{g}-{e}", "promesas", [g], f"{GOB[g]}: promesas «{est.get(e, e).lower()}» ({len(ps)})",
                 "; ".join(f"{corto(p.get('texto'), 75 if e == 'sin_evidencia' else 110)} [{p.get('nivel') or 's/n'}]" for p in ps),
                 urls([x for p in ps for x in p.get("fuentes") or []]), ["promesa", "promesas", e.replace("_", " "), "cumplio" if e in ("cumplida", "parcial") else "estado"],
                 n=4500 if e == "sin_evidencia" else 1600)
            if e in ("cumplida", "parcial", "incumplida"):  # detalle de lo que sí se puede afirmar
                for p in ps:
                    frag(f"promesa-{p.get('id')}", "promesas", [g], f"{GOB[g]}: {corto(p.get('texto'), 110)}",
                         f"Estado: {est.get(e, e)} ({corto(p.get('estado_fuente'), 80)}). Eslabón: {p.get('nivel')}. {corto(p.get('nota'), 220)}",
                         urls(p.get("fuentes")), ["promesa", "cadena de valor", "cumplio" if e != "incumplida" else "incumplio"], n=340)
    for i, cv in enumerate((b.get("caveats") or [])[:3], 1):
        frag(f"promesas-caveat-{i}", "caveats", [], "Advertencias: promesas", cv, [SITIO], ["advertencia", "promesas"])


# ---------------------------------------------------------------- gabinete
def gabinete():
    k, c, e, idn = J("keiko"), J("castillo"), J("expresidentes"), J("idoneidad")
    gk = k.get("gabinete") or {}
    if gk:
        cambios = "; ".join(f"{x.get('fecha')} {x.get('cartera')}: sale {corto(x.get('sale'), 80)}, entra {corto(x.get('entra'), 80)}" for x in gk.get("cambios", []))
        vc = gk.get("voto_de_confianza") or {}
        frag("gabinete-keiko", "gabinete", ["keiko"], "Keiko: gabinete y estabilidad",
             f"Premier: {gk.get('premier')}. {gk.get('n_carteras')} carteras. Cambios de ministros en 100 días: {gk.get('n_cambios_100_dias')} ({cambios}). "
             f"Voto de confianza: {corto(vc.get('detalle') if isinstance(vc, dict) else vc, 200)}. Censuras: {corto(json.dumps(gk.get('censuras'), ensure_ascii=False), 160)}. "
             f"Interpelaciones: {corto(json.dumps(gk.get('interpelaciones'), ensure_ascii=False), 160)}.",
             urls(gk.get("fuentes"), gk.get("cambios")), ["ministros", "premier", "galarreta", "rotacion", "estabilidad"])
    gc = c.get("gobernabilidad") or {}
    if gc:
        partes = []
        for kk in ("premieres", "gabinetes", "ministros_salientes_100_dias", "votos_de_confianza", "interpelaciones", "censuras", "proyectos_de_ley_ejecutivo", "decretos_de_urgencia"):
            v = gc.get(kk)
            if isinstance(v, dict):
                partes.append(f"{kk.replace('_', ' ')}: {num(v.get('valor'))} ({corto(v.get('detalle'), 140)})")
        frag("gabinete-castillo", "gabinete", ["castillo"], "Castillo: gabinete y gobernabilidad", ". ".join(partes),
             urls(*(gc.get(x) for x in ("premieres", "ministros_salientes_100_dias", "interpelaciones"))), ["ministros", "premier", "bellido", "rotacion", "estabilidad"])
    for key, g in (("garcia_2006", "garcia"), ("humala_2011", "humala"), ("ppk_2016", "ppk")):
        gb = (e.get(key) or {}).get("gobernabilidad") or {}
        if gb:
            vc, cg = gb.get("voto_confianza") or {}, gb.get("cambios_gabinete_100d") or {}
            frag(f"gabinete-{g}", "gabinete", [g], f"{GOB[g]}: gabinete",
                 f"Premier inicial: {gb.get('premier_inicial')}. Voto de confianza: {vc.get('fecha')} ({vc.get('a_favor')} a favor, {vc.get('en_contra')} en contra). "
                 f"Cambios de gabinete en 100 días: {cg.get('n')} ({corto(cg.get('detalle'), 160)}).", urls(vc.get("fuente_url")), ["ministros", "premier", "historico"])
    if idn:
        frag("idoneidad-criterio", "gabinete", [], "Cómo medimos la idoneidad de los ministros", corto(idn.get("criterio"), 600), [SITIO + "#gabinete"],
             ["idoneidad", "experiencia", "formacion", "metodologia"])
        for key, gab in (idn.get("gabinetes") or {}).items():
            g = ALIAS.get(key)
            ag = gab.get("agregados") or {}
            if not g:
                continue
            frag(f"idoneidad-{g}", "gabinete", [g], f"{GOB[g]}: idoneidad del gabinete del día 1",
                 f"Premier: {gab.get('premier')}. {ag.get('n_ministros_dia1_incl_premier')} ministros del día 1 (con premier). Con experiencia sectorial: {num(ag.get('pct_experiencia_si'), ' %')} "
                 f"(sí o parcial {num(ag.get('pct_experiencia_si_o_parcial'), ' %')}). Con formación acorde: {num(ag.get('pct_formacion_si'), ' %')} (sí o parcial {num(ag.get('pct_formacion_si_o_parcial'), ' %')}). "
                 f"Ministros con investigación reportada: {num(ag.get('n_investigacion_reportada_si'))} (no comparable entre años; ninguna investigación es una condena). "
                 + " ".join(corto(n, 200) for n in (gab.get("notas") or [])[:2]), [SITIO + "#gabinete"], ["idoneidad", "ministros", "experiencia", "investigaciones"])
        for i, ev in enumerate(idn.get("evaluaciones_externas", []), 1):
            g = ALIAS.get(ev.get("gabinete"))
            frag(f"idoneidad-ext-{i}", "gabinete", [g] if g else [], f"Evaluación externa del gabinete ({ev.get('fuente')}, {ev.get('fecha')})",
                 ev.get("hallazgo"), urls(ev.get("url")), ["idoneidad", "ministros"])


# ---------------------------------------------------------------- aprobación
def aprobacion():
    k, c, e = J("keiko"), J("castillo"), J("expresidentes")
    series = {"keiko": k.get("aprobacion", []), "castillo": c.get("aprobacion", [])}
    for key, g in (("garcia_2006", "garcia"), ("humala_2011", "humala"), ("ppk_2016", "ppk")):
        series[g] = (e.get(key) or {}).get("aprobacion", [])
    for g, s in series.items():
        if not s:
            continue
        frag(f"aprobacion-{g}", "aprobacion", [g], f"{GOB[g]}: aprobación en encuestas",
             "; ".join(f"{x.get('encuestadora')} {x.get('fecha') or x.get('campo')}: aprueba {num(x.get('aprueba'), ' %')}, desaprueba {num(x.get('desaprueba'), ' %')}" for x in s),
             urls([x.get("fuente_url") for x in s]), ["encuestas", "ipsos", "popularidad", "confianza ciudadana", "luna de miel"])


# ---------------------------------------------------------------- mercados
def mercados():
    i = J("indicadores")
    for s in i.get("series", []):
        def v(w):
            x = s.get(w) or {}
            d0, d1 = x.get("d0") or {}, x.get("d100") or {}
            return f"{d0.get('fecha')}: {num(d0.get('valor'))} → {d1.get('fecha')}: {num(d1.get('valor'))} (var. {num(x.get('var_pct'), ' %')})"
        frag(f"mercado-{s.get('id')}", "mercados", ["castillo", "keiko"], f"{s.get('nombre')} ({s.get('unidad')})",
             f"Castillo 2021: {v('v1')}. Keiko 2026: {v('v2')}. {corto(s.get('interpretacion_neutral'), 250)} Confianza: {corto(s.get('confianza'), 160)}",
             urls(s.get("fuente_url")), ["economia", "bcrp", "dolar" if "cambio" in (s.get("nombre") or "").lower() else "indicador", s.get("id") or ""])
    ip = i.get("inversion_publica") or {}
    if ip:
        def r(x):
            p = (x or {}).get("proyectos_gobierno_nacional") or (x or {}).get("proyectos_total") or {}
            return f"PIM S/ {num(round((p.get('pim_soles') or 0) / 1e9, 1))} mil millones; devengado jul-oct {num(p.get('devengado_jul_oct_pct_pim'), ' %')} del PIM; ene-oct {num(p.get('devengado_ene_oct_pct_pim'), ' %')}"
        frag("mercado-inversion", "mercados", ["castillo", "keiko"], "Inversión pública (proyectos, Gobierno Nacional, MEF)",
             f"2021: {r(ip.get('v1_2021'))}. 2026: {r(ip.get('v2_2026'))}. " + corto(ip.get("metodo"), 250), urls(ip.get("fuente_url")),
             ["inversion", "gasto", "mef", "ejecucion", "presupuesto"])
    pe = J("performance")
    tot = pe.get("totales_gobierno_nacional") or {}
    if tot:
        frag("ejecucion-totales", "mercados", list(GOB), "Ejecución presupuestal del Gobierno Nacional (ene-oct) por año de inicio",
             "; ".join(f"{a}: total {num((v.get('ActProy') or {}).get('pct'), ' %')}, proyectos {num((v.get('Proyecto') or {}).get('pct'), ' %')}" for a, v in tot.items()),
             urls([(v.get("ActProy") or {}).get("fuente_url") for v in tot.values()]), ["ejecucion", "gasto", "mef", "presupuesto"])
    for a in ("obras_paralizadas", "conflictos"):
        xs = pe.get(a) or []
        if xs:
            frag(f"perf-{a}", "mercados", list(GOB), a.replace("_", " ").capitalize() + " (por año)",
                 "; ".join(f"{x.get('anio')}{' ' + str(x.get('mes')) if x.get('mes') else ''}: {num(x.get('n_obras') or x.get('total'))}" + (f" ({x.get('monto_texto')})" if x.get("monto_texto") else "") for x in xs),
                 urls([x.get("fuente_url") for x in xs]), ["contraloria" if a == "obras_paralizadas" else "defensoria", "obras" if a == "obras_paralizadas" else "conflictos sociales"])


# ---------------------------------------------------------------- resultados
def resultados():
    r = J("resultados")
    if r.get("conclusion_neutral"):
        frag("resultados-lectura", "resultados", ["keiko", "castillo"], "Resultados: lectura neutral", r["conclusion_neutral"], [SITIO + "#resultados"],
             ["valor publico", "homicidios", "empleo", "inflacion", "vacunas", "resultado"])
    for x in r.get("indicadores", []):
        def v(a):
            y = x.get(a) or {}
            an, du = y.get("antes") or {}, y.get("durante") or {}
            return f"100 días previos {num(an.get('valor'))} → 100 días de gobierno {num(du.get('valor'))}" if (an or du) else "s/d"
        frag(f"resultado-{x.get('id')}", "resultados", ["castillo", "keiko"], f"{x.get('nombre')} ({x.get('unidad')})",
             f"2021 (Castillo): {v('2021')}. 2026 (Keiko): {v('2026')}. Fuente: {corto(x.get('fuente'), 120)}. {corto(x.get('rezago_nota'), 200)}",
             urls(x.get("fuente_url")), ["indicador", x.get("id") or ""])


# ---------------------------------------------------------------- planes
def planes():
    p = J("planes")
    for g, key in (("castillo", "castillo_2021"), ("keiko", "fp_2026")):
        x = p.get(key) or {}
        if x:
            frag(f"plan-{g}", "planes", [g], f"Plan de gobierno: {corto(x.get('nombre'), 100)}",
                 f"{x.get('paginas')} páginas. Metas cuantificadas: {x.get('n_metas_cuantificadas')} (con plazo: {x.get('n_metas_cuantificadas_con_plazo')}). "
                 f"Metas de resultado: {x.get('n_metas_resultado')}; de producto o actividad: {x.get('n_metas_producto_actividad')}. "
                 + (f"Compromisos de 100 días: {x.get('n_compromisos_100d')}. " if x.get("n_compromisos_100d") else "")
                 + corto(x.get("metodo") or x.get("nota_paginas"), 250), urls(x.get("url_pdf")), ["plan", "metas", "jne"])
    for i, ej in enumerate(p.get("ejes", []), 1):
        ca, ke = ej.get("castillo") or {}, ej.get("keiko") or {}
        frag(f"plan-eje-{i}", "planes", ["castillo", "keiko"], f"Planes comparados: {ej.get('eje')}",
             f"Castillo: {corto(ca.get('texto') if isinstance(ca, dict) else ca, 260)} Keiko: {corto(ke.get('texto') if isinstance(ke, dict) else ke, 260)} "
             f"Diferencia clave: {corto(ej.get('diferencia_clave'), 200)}", urls((p.get("castillo_2021") or {}).get("url_pdf"), (p.get("fp_2026") or {}).get("url_pdf")), ["plan", "eje"])
    for i, ct in enumerate(p.get("contradicciones", []), 1):
        g = "castillo" if "castillo" in str(ct.get("plan")) else "keiko"
        frag(f"plan-contradiccion-{i}", "planes", [g], f"{g.capitalize()}: plan frente a los hechos",
             f"El plan dice: {corto(ct.get('plan_dice'), 250)} Hecho: {corto(ct.get('hecho'), 350)}", urls(ct.get("fuente")), ["plan", "contradiccion"])


# ---------------------------------------------------------------- hitos
def hitos():
    for g in ("keiko", "castillo"):
        for i, h in enumerate(J(g).get("hitos", []), 1):
            frag(f"hito-{g}-{i}", "hitos", [g], f"{g.capitalize()}, {h.get('fecha')}: hito", h.get("texto"), urls(h.get("fuente_url")), ["linea de tiempo", "cronologia"], n=260)


# ---------------------------------------------------------------- caveats
def caveats():
    nombres = {"keiko": "datos de Keiko", "castillo": "datos de Castillo", "expresidentes": "García, Humala y PPK", "factcheck": "verificación de infografías",
               "idoneidad": "idoneidad del gabinete", "indicadores": "mercados", "resultados": "resultados", "planes": "planes de gobierno"}
    for f, nom in nombres.items():
        cs = J(f).get("caveats") or []
        for i in range(0, min(len(cs), 2), 2):
            frag(f"caveat-{f}-{i // 2 + 1}", "caveats", [g for g in GOB if g == f], f"Advertencias: {nom}",
                 " • ".join(corto(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False), 300) for c in cs[i:i + 2]),
                 [SITIO], ["advertencia", "limitaciones", "metodologia"])


def main():
    for fn in (conclusion, indice, veredictos, promesas, gabinete, aprobacion, mercados, resultados, planes, hitos, caveats):
        fn()
    salida = {
        "sitio": SITIO,
        "generado": date.today().isoformat(),
        "corte": "2026-11-07",
        "gobiernos": GOB,
        "aviso": "Índice experimental. Castillo y Keiko no son distinguibles con estos datos. Ninguna investigación es una condena.",
        "fuentes": [],  # tabla de URLs; cada fragmento guarda índices en "u"
        "fragmentos": FR,
    }
    tabla = {}
    for f in FR:
        f["u"] = [tabla.setdefault(u, len(tabla)) for u in f["u"]]
    salida["fuentes"] = list(tabla)
    txt = json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    # si se pasa del límite, recorta los textos más largos hasta entrar
    n = 900  # tope inicial; baja de 50 en 50 hasta entrar en LIMITE
    while len(txt.encode("utf-8")) > LIMITE and n > 300:
        n -= 50
        for f in FR:
            if f["sec"] != "conclusion" and f["id"] not in ("indice-resumen", "resultados-lectura") and not f["id"].startswith(("promesas-", "mensaje-", "gabinete-")):  # lo esencial no se recorta
                f["x"] = corto(f["x"], n)
        txt = json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(txt, encoding="utf-8")
    secs = {}
    for f in FR:
        secs[f["sec"]] = secs.get(f["sec"], 0) + 1
    print(f"{OUT.relative_to(RAIZ)}: {len(FR)} fragmentos, {len(txt.encode('utf-8')) / 1024:.1f} KB · " + ", ".join(f"{k} {v}" for k, v in secs.items()))


if __name__ == "__main__":
    main()
