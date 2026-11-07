"""Arma research/indicadores.json a partir de bcrp_raw*.json y mef.json.
Uso: python build_indicadores.py BCRP_RAW.json BCRP_RAW2.json MEF.json OUT.json"""
import json, sys, datetime as dt
raw = json.load(open(sys.argv[1])); raw.update(json.load(open(sys.argv[2])))
mef = json.load(open(sys.argv[3]))
MES = {"Ene":1,"Feb":2,"Mar":3,"Abr":4,"May":5,"Jun":6,"Jul":7,"Ago":8,"Sep":9,"Set":9,"Oct":10,"Nov":11,"Dic":12}
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{c}/json"
W = {"v1": (dt.date(2021,7,28), dt.date(2021,11,5)), "v2": (dt.date(2026,7,28), dt.date(2026,11,5))}

def parse(name):
    p = name.split(".")
    if len(p) == 3: return dt.date(2000+int(p[2]), MES[p[1]], int(p[0]))
    return dt.date(int(p[1]), MES[p[0]], 1)

def pts(c, w):
    out = []
    for p in raw[c][w].get("periods", []):
        v = p["values"][0]
        try: out.append((parse(p["name"]), float(v)))
        except ValueError: pass
    return out

def r(x, n=4): return None if x is None else round(x, n)

def daily(c, w, pct_unit=False):
    a, b = W[w]; P = pts(c, w)
    d0 = [x for x in P if x[0] <= a][-1]
    inwin = [x for x in P if d0[0] <= x[0] <= b]
    last = inwin[-1]
    ok100 = (b - last[0]).days <= 7
    d100 = last if ok100 else None
    o = {"d0": {"fecha": d0[0].isoformat(), "valor": r(d0[1])},
         "d100": {"fecha": d100[0].isoformat(), "valor": r(d100[1])} if d100 else {"fecha": None, "valor": None, "nota": f"no disponible: la serie diaria termina el {last[0].isoformat()} en BCRPData"},
         "var_pct": (None if pct_unit or not d100 else r((d100[1]/d0[1]-1)*100, 2)),
         "serie": [[d.isoformat(), r(v)] for d, v in inwin]}
    if pct_unit and d100: o["var_pp"] = r(d100[1]-d0[1], 2)
    if not d100: o["ultimo_disponible"] = {"fecha": last[0].isoformat(), "valor": r(last[1])}
    return o

def monthly(c, w, m0, m1, pct_unit=True, ctx=(4, 12)):
    y = W[w][0].year; P = {d.month: v for d, v in pts(c, w)}
    v0, v1 = P.get(m0), P.get(m1)
    o = {"d0": {"fecha": f"{y}-{m0:02d}", "valor": r(v0)},
         "d100": {"fecha": f"{y}-{m1:02d}", "valor": r(v1)} if v1 is not None else {"fecha": None, "valor": None, "nota": "no disponible"},
         "var_pct": None if pct_unit or v1 is None else r((v1/v0-1)*100, 2),
         "serie": [[f"{y}-{m:02d}", r(v)] for m, v in sorted(P.items()) if ctx[0] <= m <= ctx[1]]}
    if pct_unit and v1 is not None: o["var_pp"] = r(v1-v0, 2)
    return o

def meta_name(c): return raw[c]["meta"]["config"]["series"][0]["name"]

S = []
def add(id_, nombre, c, unidad, frec, v1, v2, interp, conf, extra=None):
    d = {"id": id_, "nombre": nombre, "codigo_bcrp": c, "titulo_metadata_bcrp": meta_name(c), "unidad": unidad,
         "frecuencia": frec, "fuente_url": API.format(c=c), "v1": v1, "v2": v2,
         "interpretacion_neutral": interp, "confianza": conf}
    if extra: d.update(extra)
    S.append(d)

add("tc_interbancario_venta", "Tipo de cambio interbancario (venta)", "PD04638PD", "S/ por US$", "diaria",
    daily("PD04638PD","v1"), daily("PD04638PD","v2"),
    "Sube = el sol se deprecia frente al dólar. Refleja también el ciclo global del dólar y de tasas de la Fed, no solo el riesgo político local.", "alta",
    {"nota_codigo": "PD04640PD (sugerido inicialmente) es 'TC Sistema bancario SBS - Venta', NO el interbancario; se usa PD04638PD verificado en metadata."})
emb_v1 = daily("PD04709XD","v1"); emb_v2 = daily("PD04709XD","v2")
# mismo horizonte para comparar: V1 al 03-sep-2021
P1 = [x for x in pts("PD04709XD","v1") if x[0] <= dt.date(2021,9,3)][-1]
emb_v1["mismo_horizonte_que_v2"] = {"fecha": P1[0].isoformat(), "valor": P1[1], "var_pct": r((P1[1]/emb_v1["d0"]["valor"]-1)*100,2),
                                    "nota": "Comparación al mismo horizonte (~día 37) que el último dato diario de V2."}
emb_v2["var_pct_al_ultimo_disponible"] = r((emb_v2["ultimo_disponible"]["valor"]/emb_v2["d0"]["valor"]-1)*100, 2)
emb_v2["mensual_PN01129XM"] = monthly("PN01129XM","v2",7,10,False)["serie"]
emb_v1["mensual_PN01129XM"] = monthly("PN01129XM","v1",7,10,False)["serie"]
add("embig_peru", "Riesgo país: spread EMBIG Perú", "PD04709XD", "puntos básicos", "diaria", emb_v1, emb_v2,
    "Sube = el mercado exige más prima por deuda soberana peruana. Se mueve con el apetito global por riesgo emergente; compárese con EMBIG América Latina (control).",
    "media: en BCRPData la serie diaria de V2 termina el 2026-09-03 (día ~37); día 100 no disponible. El mensual PN01129XM llega a sep-2026.")
add("bvl_indice_general", "Índice General Bursátil BVL (S&P/BVL Peru General)", "PD38026MD", "índice", "diaria",
    daily("PD38026MD","v1"), daily("PD38026MD","v2"),
    "Mide precios de acciones listadas en Lima, con fuerte peso minero: muy sensible al precio de metales (ver cobre).", "alta")
add("tasa_referencia_bcrp", "Tasa de referencia de política monetaria", "PD12301MD", "% anual", "diaria",
    daily("PD12301MD","v1",True), daily("PD12301MD","v2",True),
    "La fija el BCRP (autónomo) según inflación y expectativas; no es una decisión del Ejecutivo. En 2021 el BCRP inició un ciclo de alzas desde el mínimo de 0.25 % de la pandemia.", "alta",
    {"nota_var": "Variación en puntos porcentuales (var_pp); var_pct no se calcula para tasas."})
add("inflacion_lima_12m", "Inflación 12 meses, IPC Lima Metropolitana", "PN01273PM", "var % 12 meses", "mensual",
    monthly("PN01273PM","v1",7,10), monthly("PN01273PM","v2",7,10),
    "d0 = julio, d100 = octubre (junio incluido en la serie). Influida por precios internacionales de alimentos y combustibles y por el tipo de cambio.", "alta",
    {"nota_var": "var_pp en puntos porcentuales."})
add("expectativa_economia_3m", "Expectativas empresariales: economía a 3 meses", "PD38045AM", "índice 0-100 (50 = neutral)", "mensual",
    monthly("PD38045AM","v1",7,10,False), monthly("PD38045AM","v2",7,10,False),
    "Encuesta mensual del BCRP a empresas. >50 = mayoría optimista, <50 = pesimista. Es percepción, no actividad.", "alta")
add("expectativa_inflacion_12m", "Expectativa de inflación a 12 meses (encuesta BCRP)", "PD12912AM", "%", "mensual",
    monthly("PD12912AM","v1",7,10), monthly("PD12912AM","v2",7,10),
    "Promedio de expectativas de analistas, sistema financiero y empresas encuestadas por el BCRP. Rango meta del BCRP: 1 %-3 %.", "alta",
    {"nota_var": "var_pp en puntos porcentuales."})
add("pbi_mensual_var_interanual", "PBI mensual, variación % interanual", "PN01728AM", "var % interanual", "mensual",
    monthly("PN01728AM","v1",5,8), monthly("PN01728AM","v2",5,8),
    "d0 = mayo (último mes publicado antes del 28-jul), d100 = agosto (último publicado antes del 5-nov; sep sale a mediados de nov). En 2021 la tasa está inflada por el efecto base de la caída de 2020 (pandemia): NO es comparable en nivel con 2026. Los meses medidos además reflejan en buena parte decisiones previas al gobierno entrante.", "media (comparabilidad baja por efecto base 2021)",
    {"nota_var": "var_pp en puntos porcentuales."})
add("control_cobre_lme", "CONTROL: precio del cobre (Londres)", "PD04701XD", "cUS$ por libra", "diaria",
    daily("PD04701XD","v1"), daily("PD04701XD","v2"),
    "Variable de contexto externo, no atribuible al gobierno. Explica parte de la BVL, del tipo de cambio y del riesgo país.", "alta", {"rol": "control"})
add("control_embig_latam", "CONTROL: spread EMBIG América Latina", "PD04708XD", "puntos básicos", "diaria",
    daily("PD04708XD","v1"), daily("PD04708XD","v2"),
    "Riesgo soberano regional: permite separar lo regional/global de lo específico de Perú (diferencia Perú - Latam).", "media (V2 termina 2026-09-03)", {"rol": "control"})

# ---------- MEF ----------
def month_rows(rows):
    out = {}
    for x in rows or []:
        lab = x["label"].split(":")[0].strip()
        if lab.isdigit(): out[int(lab)] = x["devengado"] or 0.0
    return out
def head(rows):
    return [x for x in rows if x["pim"] is not None][-1] if rows else None
def bloque(rows, nombre):
    h = head(rows); m = month_rows(rows)
    jul_oct = sum(m.get(i, 0) for i in (7,8,9,10)); ene_oct = sum(m.get(i, 0) for i in range(1,11)); ene_jun = sum(m.get(i,0) for i in range(1,7))
    return {"ambito": nombre, "pim_soles": h["pim"], "devengado_al_corte_soles": h["devengado"], "avance_al_corte_pct": h["avance_pct"],
            "devengado_jul_oct_soles": round(jul_oct,2), "devengado_jul_oct_pct_pim": r(jul_oct/h["pim"]*100,2),
            "devengado_ene_jun_soles": round(ene_jun,2), "devengado_ene_oct_soles": round(ene_oct,2),
            "devengado_ene_oct_pct_pim": r(ene_oct/h["pim"]*100,2),
            "devengado_mensual_soles": {f"{k:02d}": round(v,2) for k, v in sorted(m.items())}}
inv = {"fuente": "MEF - Consulta Amigable (Transparencia Económica), consulta de ejecución del gasto",
       "fuente_url": "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx",
       "fecha_consulta": "2026-11-07",
       "metodo": "Navegador 'Sólo Proyectos' (proyectos de inversión) -> Nivel de Gobierno -> Mes; y 'Actividades/Proyectos' -> Genérica 6-26 Adquisición de activos no financieros -> Mes. Script: etl/scrape_inversion_mef.py",
       "nota_api_ckan": "La API api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search_sql devolvió 404 'Recurso no encontrado' y datastore_search devolvió records=null (7-nov-2026); por eso se usó la Consulta Amigable.",
       "v1_2021": {}, "v2_2026": {}}
for y, k in (("2021","v1_2021"),("2026","v2_2026")):
    d = mef[y]
    inv[k]["proyectos_total"] = bloque(d["proyectos_total_por_mes"], "Proyectos de inversión - 3 niveles de gobierno")
    inv[k]["proyectos_gobierno_nacional"] = bloque(d["proyectos_gobierno_nacional_por_mes"], "Proyectos - Gobierno Nacional")
    inv[k]["proyectos_gobiernos_regionales"] = bloque(d["proyectos_gobiernos_regionales_por_mes"], "Proyectos - Gobiernos Regionales")
    inv[k]["proyectos_gobiernos_locales"] = bloque(d["proyectos_gobiernos_locales_por_mes"], "Proyectos - Gobiernos Locales")
    inv[k]["generica_2_6_total"] = bloque(d["generica_26_por_mes"], "Genérica 2.6 Adquisición de activos no financieros - 3 niveles")
inv["caveats_inversion"] = [
    "2021: PIM es el PIM FINAL del año 2021 (cierre); 2026: PIM vigente al 7-nov-2026. El PIM crece durante el año, por lo que el % del PIM de jul-oct 2021 queda sesgado a la baja frente a 2026. Comparar también los montos.",
    "Montos en soles corrientes (no deflactados). Inflación acumulada 2021-2026 hace que los montos nominales no sean directamente comparables.",
    "Julio completo se atribuye a la ventana aunque el cambio de gobierno fue el 28-jul.",
    "El devengado 2026 'al corte' incluye días de noviembre; las sumas jul-oct y ene-oct son por mes de ejecución y sí son comparables entre años.",
    "La ejecución de gobiernos regionales y locales depende de autoridades subnacionales, no del Ejecutivo nacional; para atribuir al gobierno central usar 'Gobierno Nacional'.",
    "Las cifras de 2026 pueden revisarse (regularizaciones del SIAF).",
]

out = {"generado": "2026-11-07",
       "ventanas": {"v1": {"inicio": "2021-07-28", "fin": "2021-11-05", "gobierno": "Pedro Castillo"},
                    "v2": {"inicio": "2026-07-28", "fin": "2026-11-05", "gobierno": "Keiko Fujimori"}},
       "regla_fechas": "Series diarias: d0 = último dato hábil en o antes del 28-jul (28 y 29-jul son feriados: mercados cerrados); d100 = último dato hábil en o antes del 5-nov. Mensuales: d0/d100 según se indica en cada serie.",
       "series": S, "inversion_publica": inv,
       "caveats": [
           "Los indicadores de mercado (tipo de cambio, EMBIG, BVL) reflejan también el contexto global (tasas de la Fed, fortaleza del dólar, precio del cobre y apetito por riesgo emergente), no solo al gobierno. Se incluyen como control el precio del cobre (PD04701XD) y el EMBIG América Latina (PD04708XD).",
           "100 días es un horizonte corto: inflación, PBI y ejecución de inversión tienen rezagos y reflejan en buena parte decisiones previas (presupuesto aprobado por el gobierno anterior, contratos ya en curso).",
           "La tasa de referencia la decide el BCRP (autónomo), no el Ejecutivo.",
           "PBI 2021 está distorsionado por el rebote post-pandemia (efecto base 2020); no comparar niveles de crecimiento entre ventanas.",
           "Correlación no es causalidad: las variaciones no se atribuyen al gobierno en este dataset.",
           "EMBIG Perú diario en BCRPData termina el 2026-09-03 (consultado 7-nov-2026): el día 100 de V2 no está disponible; se da la comparación al mismo horizonte (~día 37) y la serie mensual PN01129XM.",
           "Todas las series del BCRP se verificaron contra el título de su metadata (campo titulo_metadata_bcrp). Datos 2026 consultados el 7-nov-2026; pueden revisarse.",
           "Las expectativas empresariales y de inflación son encuestas de percepción, no mediciones de actividad.",
       ]}
json.dump(out, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
for s in S:
    for w in ("v1","v2"):
        v = s[w]; print(s["id"], w, v["d0"], v["d100"].get("fecha"), v["d100"].get("valor"), v.get("var_pct"), v.get("var_pp"))
for k in ("v1_2021","v2_2026"):
    for b, x in inv[k].items():
        print(k, b, round(x["pim_soles"]/1e9,2), round(x["devengado_jul_oct_soles"]/1e9,2), x["devengado_jul_oct_pct_pim"], x["devengado_ene_oct_pct_pim"])
