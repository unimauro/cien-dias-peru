"""Arma research/intl_gobernanza.json a partir de los archivos descargados por intl_gob_*.py.
Uso: python3 -I intl_gob_build.py DIR_DESCARGAS
DIR_DESCARGAS debe tener: wgi_per.json, cpi_per.json, rsf_per.json, wjp_per.json, bti_per.json y los CSV de Our World in Data
(owid_*.csv / owid2_*.csv, descargados de https://ourworldindata.org/grapher/<slug>.csv?country=~PER&useColumnShortNames=true)."""
import csv, json, os, sys
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "intl_gobernanza.json")
Y0, Y1 = 2005, 2026
J = lambda f: json.load(open(os.path.join(D, f)))

def owid(fname, col):
    s = {}
    for r in csv.DictReader(open(os.path.join(D, fname))):
        if r["code"] == "PER" and Y0 <= int(r["year"]) <= Y1:
            v = r[col]
            try: v = float(v)
            except ValueError: pass
            s[r["year"]] = v
    return s

def fill(s):
    """Serie completa 2005-2026 con null donde no hay dato."""
    return {str(y): s.get(str(y)) for y in range(Y0, Y1 + 1)}

idx = []
def add(**k):
    k["serie"] = fill(k["serie"]); idx.append(k)

# ---------- WGI ----------
wgi = J("wgi_per.json")
WGI_URL = "https://api.worldbank.org/v2/country/PER/indicator/{}?format=json&per_page=100&source=3"
DIMS = {"CC": ("Control de la corrupción", "corrupcion"), "GE": ("Efectividad del gobierno", "efectividad"),
        "RL": ("Estado de derecho", "estado_de_derecho"), "RQ": ("Calidad regulatoria", "efectividad"),
        "VA": ("Voz y rendición de cuentas", "libertades"), "PV": ("Estabilidad política y ausencia de violencia", "democracia")}
for d, (nom, dim) in DIMS.items():
    for suf, esc, desc in (("EST", {"min": -2.5, "max": 2.5, "mejor": "alto"}, "estimación (aprox. -2.5 a +2.5)"),
                           ("SC", {"min": 0, "max": 100, "mejor": "alto"}, "puntaje 0-100 (nueva métrica de la edición 2025+, NO es el percentil)")):
        code = f"GOV_WGI_{d}.{suf}"
        add(id=f"wgi_{d.lower()}_{suf.lower()}", nombre=f"WGI – {nom} ({desc})", institucion="Banco Mundial (Worldwide Governance Indicators)",
            dimension=dim, escala=esc, fuente_url=WGI_URL.format(code),
            serie={k: round(v, 3 if suf == "EST" else 1) for k, v in wgi[code].items()},
            nota=f"Código API {code} (los códigos CC.EST / CC.PER.RNK ya no existen: la API devuelve 'Invalid value'). Año = año de los datos. "
                 "El percentil (PER.RNK) fue retirado del API source=3 en la revisión metodológica 2025; se usa el puntaje 0-100 (.SC). "
                 "Último dato: 2025. La serie entera se re-estima en cada edición, por eso puede diferir de cifras publicadas antes.")

# ---------- CPI ----------
cpi = J("cpi_per.json")
add(id="cpi_score", nombre="Índice de Percepción de la Corrupción (CPI) – puntaje", institucion="Transparency International",
    dimension="corrupcion", escala={"min": 0, "max": 100, "mejor": "alto"},
    fuente_url="https://images.transparencycdn.org/images/CPI2025_Results.xlsx",
    serie={k: v["score"] for k, v in cpi.items()},
    nota="RUPTURA DE ESCALA: 2005-2011 en escala 0-10 (valores originales, p. ej. 3.5), 2012-2025 en 0-100. TI advierte que no son comparables "
         "(no basta multiplicar por 10). 2005-2011 de los CSV del archivo histórico transparency.org/en/cpi/<año>; 2012-2025 de la hoja 'CPI Historical' del XLSX oficial. "
         "Año = edición (publicada en enero-febrero del año siguiente). CPI 2026 se publicará ~feb-2027.")
add(id="cpi_rank", nombre="CPI – puesto en el ranking mundial", institucion="Transparency International",
    dimension="corrupcion", escala={"min": 1, "max": 182, "mejor": "bajo"},
    fuente_url="https://images.transparencycdn.org/images/CPI2025_Results.xlsx",
    serie={k: v["rank"] for k, v in cpi.items()},
    nota="Puesto (1 = menos corrupto). El número de países cambia cada año: " + ", ".join(f"{k}: {v['n_paises']}" for k, v in cpi.items()) + ".")

# ---------- V-Dem (vía OWID) ----------
VD = [("vdem_libdem", "V-Dem – Índice de Democracia Liberal", "owid_liberal-democracy-index.csv", "libdem_vdem__estimate_best", "liberal-democracy-index", "democracia", "alto"),
      ("vdem_electdem", "V-Dem – Índice de Democracia Electoral", "owid_electoral-democracy-index.csv", "electdem_vdem__estimate_best", "electoral-democracy-index", "democracia", "alto"),
      ("vdem_corr", "V-Dem – Índice de Corrupción Política", "owid_political-corruption-index.csv", "corruption_vdem__estimate_best", "political-corruption-index", "corrupcion", "bajo")]
for i, n, f, c, slug, dim, mejor in VD:
    add(id=i, nombre=n, institucion="V-Dem Institute (Univ. de Gotemburgo), redistribuido por Our World in Data", dimension=dim,
        escala={"min": 0, "max": 1, "mejor": mejor}, fuente_url=f"https://ourworldindata.org/grapher/{slug}.csv?country=~PER&useColumnShortNames=true",
        serie=owid(f, c),
        nota="Estimación central (best). Año = año evaluado. Último dato disponible en OWID: 2025. "
             + ("Más alto = MÁS corrupción." if mejor == "bajo" else ""))

# ---------- EIU (Wikipedia; OWID no redistribuye) ----------
eiu = {"2006": 6.11, "2008": 6.31, "2010": 6.40, "2011": 6.59, "2012": 6.47, "2013": 6.54, "2014": 6.54, "2015": 6.58, "2016": 6.65,
       "2017": 6.49, "2018": 6.60, "2019": 6.60, "2020": 6.53, "2021": 6.09, "2022": 5.92, "2023": 5.81, "2024": 5.69, "2025": 5.88}
add(id="eiu_democracy", nombre="EIU Democracy Index – puntaje global", institucion="Economist Intelligence Unit",
    dimension="democracia", escala={"min": 0, "max": 10, "mejor": "alto"},
    fuente_url="https://en.wikipedia.org/wiki/The_Economist_Democracy_Index",
    serie=eiu,
    nota="FUENTE SECUNDARIA: Our World in Data devuelve 403 (datos no redistribuibles) y la EIU exige registro; los valores vienen de la tabla de Wikipedia "
         "(que transcribe los informes EIU). Sin ediciones 2005, 2007 ni 2009 (el índice fue bienal hasta 2010). Ranking 2025: puesto 76. Desglose 2025: proceso electoral 8.75, "
         "funcionamiento del gobierno 5.71, participación 5.00, cultura política 2.50, libertades civiles 6.47.")
regimen = {k: ("Democracia plena" if v >= 8 else "Democracia defectuosa" if v > 6 else "Régimen híbrido" if v > 4 else "Autoritario") for k, v in eiu.items()}
add(id="eiu_regimen", nombre="EIU Democracy Index – tipo de régimen", institucion="Economist Intelligence Unit",
    dimension="democracia", escala={"min": None, "max": None, "mejor": "alto"},
    fuente_url="https://en.wikipedia.org/wiki/The_Economist_Democracy_Index",
    serie=regimen,
    nota="Derivado de los umbrales EIU (>8 plena; >6 defectuosa; >4 híbrido; ≤4 autoritario). Wikipedia confirma 'Hybrid regime' para 2025; los años previos se derivan del puntaje.")

# ---------- Freedom House (vía OWID) ----------
pr = owid("owid2_political-rights-score-fh.csv", "polrights_score")
cl = owid("owid2_civil-liberties-score-fh.csv", "civlibs_score")
st = owid("owid2_political-regime-fh.csv", "regime")
add(id="fh_total", nombre="Freedom House – Freedom in the World, puntaje total", institucion="Freedom House",
    dimension="libertades", escala={"min": 0, "max": 100, "mejor": "alto"},
    fuente_url="https://ourworldindata.org/grapher/political-rights-score-fh.csv?country=~PER (+ civil-liberties-score-fh)",
    serie={k: int(pr[k] + cl[k]) for k in pr if k in cl},
    nota="Total = derechos políticos (0-40) + libertades civiles (0-60), según los subpuntajes agregados de FH que redistribuye OWID. Año = AÑO CUBIERTO "
         "(la edición 'Freedom in the World 2026' cubre 2025). Verificado contra freedomhouse.org: 2025 = 66 (PR 27, CL 39; 'Partly Free'); 2024 = 67; 2020 = 71 (PR 29, CL 42; 'Partly Free'). "
         "FH publica el puntaje agregado de forma prominente desde ~2013; antes se usaban las calificaciones 1-7.")
add(id="fh_status", nombre="Freedom House – estatus", institucion="Freedom House", dimension="libertades",
    escala={"min": None, "max": None, "mejor": "alto"},
    fuente_url="https://ourworldindata.org/grapher/political-regime-fh.csv?country=~PER&useColumnShortNames=true",
    serie={k: {"Free": "Libre", "Partly free": "Parcialmente libre", "Not free": "No libre"}.get(v, v) for k, v in st.items()},
    nota="Libre / Parcialmente libre / No libre. Año = año cubierto. Perú pasó a 'Parcialmente libre' en 2020, volvió a 'Libre' en 2021 y es 'Parcialmente libre' desde 2022.")

# ---------- WJP ----------
wjp = J("wjp_per.json")
kmap = {"2012-2013": "2012", "2017-2018": "2017"}
add(id="wjp_rol", nombre="WJP Rule of Law Index – puntaje global", institucion="World Justice Project",
    dimension="estado_de_derecho", escala={"min": 0, "max": 1, "mejor": "alto"},
    fuente_url="https://worldjusticeproject.org/rule-of-law-index/downloads/2025_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx",
    serie={kmap.get(k, k): v["score"] for k, v in wjp.items()},
    nota="Año = edición. La edición '2012-2013' se guarda en 2012 y la '2017-2018' en 2017 (no hubo ediciones 2013 ni 2018). Puntajes 2015-2017 re-estimados por WJP con la metodología 2017-18. "
         "No hay datos de Perú antes de 2012 en el archivo histórico oficial. Edición 2026 no encontrada al 7-nov-2026 (se usa 2025, publicada en oct-2025).")
add(id="wjp_rank", nombre="WJP Rule of Law Index – puesto (calculado)", institucion="World Justice Project",
    dimension="estado_de_derecho", escala={"min": 1, "max": 143, "mejor": "bajo"},
    fuente_url="https://worldjusticeproject.org/rule-of-law-index/downloads/2025_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx",
    serie={kmap.get(k, k): v["rank_calc"] for k, v in wjp.items()},
    nota="Puesto CALCULADO por nosotros ordenando los puntajes (redondeados a 2 decimales) de cada hoja anual; puede diferir ±1 del puesto oficial. N.º de países: "
         + ", ".join(f"{kmap.get(k, k)}: {v['n_paises']}" for k, v in wjp.items()) + ".")

# ---------- RSF ----------
rsf = J("rsf_per.json")
add(id="rsf_score", nombre="RSF – Clasificación Mundial de la Libertad de Prensa, puntaje", institucion="Reporteros sin Fronteras",
    dimension="libertades", escala={"min": 0, "max": 100, "mejor": "alto"},
    fuente_url="https://rsf.org/sites/default/files/import_classement/{año}.csv",
    serie={k: v["score"] for k, v in rsf.items()},
    nota="RUPTURA METODOLÓGICA en 2022: 2013-2021 (metodología antigua; en los CSV oficiales de RSF ya figura reexpresada como alto = mejor) NO es comparable con 2022-2026. "
         "Año = edición (publicada en abril-mayo; refleja sobre todo el año anterior). Los CSV anteriores a 2013 no están en esa ruta.")
add(id="rsf_rank", nombre="RSF – puesto en la clasificación", institucion="Reporteros sin Fronteras",
    dimension="libertades", escala={"min": 1, "max": 180, "mejor": "bajo"},
    fuente_url="https://rsf.org/sites/default/files/import_classement/{año}.csv",
    serie={k: v["rank"] for k, v in rsf.items()},
    nota="Sobre 179-180 países. 2026: puesto 144 (37.86); 2025: 130 (42.88) — coincide con rsf.org/en/country/peru.")

# ---------- BTI ----------
bti = J("bti_per.json")
for key, nom, dim in (("SI | Democracy Status", "BTI – Estado de la democracia", "democracia"),
                      ("G | Governance Index", "BTI – Índice de gobernanza", "efectividad"),
                      ("Q15.3 | Anti-corruption policy", "BTI – Política anticorrupción (pregunta 15.3)", "corrupcion")):
    add(id="bti_" + key.split("|")[0].strip().lower().replace(".", "_"), nombre=nom, institucion="Bertelsmann Stiftung (BTI)", dimension=dim,
        escala={"min": 1, "max": 10, "mejor": "alto"},
        fuente_url="https://bti-project.org/fileadmin/api/content/en/downloads/data/BTI_2006-2026_Scores.xlsx",
        serie={k.replace("BTI ", ""): v[key] for k, v in bti.items() if k.replace("BTI ", "").isdigit()},
        nota="BIENAL. Año = EDICIÓN; la edición E evalúa el periodo 1-feb-(E-3) a 31-ene-(E-1) (p. ej., BTI 2026 = feb-2023 a ene-2025). "
             "Puestos del Status Index: " + ", ".join(f"{k.replace('BTI ', '')}: {v['Ranking Status Index']}" for k, v in bti.items() if k.replace("BTI ", "").isdigit()) + "; "
             "del Governance Index: " + ", ".join(f"{k.replace('BTI ', '')}: {v['Ranking Governance Index']}" for k, v in bti.items() if k.replace("BTI ", "").isdigit()) + ".")

# ---------- Contexto peruano ----------
add(id="contraloria_perjuicio", nombre="Contraloría – perjuicio económico estimado por corrupción e inconducta funcional (S/ millones)",
    institucion="Contraloría General de la República", dimension="corrupcion", escala={"min": 0, "max": None, "mejor": "bajo"},
    fuente_url="https://www.infobae.com/america/peru/2022/07/06/peru-perdio-mas-de-24-mil-millones-de-soles-por-corrupcion-estimo-la-contraloria/",
    serie={"2021": 24262},
    nota="Solo se verificó 2021: 'alrededor de 24,262 millones de soles' ('13 de cada 100 soles'), presentación 'Balance del Control Gubernamental del Primer Semestre 2022 y "
         "Resultados de la Estimación de la Corrupción 2021' (contralor Nelson Shack, 6-jul-2022), vía Infobae. Otros años (estimación iniciada con datos de 2019) NO verificados: "
         "gob.pe bloquea la descarga automática (HTTP 418) y se agotó el presupuesto de búsquedas. Es una estimación, no una medición.")
add(id="proetica_corrupcion_problema", nombre="Proética – % que menciona la corrupción entre los principales problemas del país",
    institucion="Proética (Encuesta Nacional sobre Percepciones de la Corrupción, trabajo de campo de Ipsos)", dimension="corrupcion",
    escala={"min": 0, "max": 100, "mejor": "bajo"},
    fuente_url="https://www.proetica.org.pe/contenido/encuesta-nacional-sobre-percepciones-de-la-corrupcion-en-el-peru/",
    serie={"2013": 44, "2017": 52, "2019": 62, "2025": 67},
    nota="Pregunta: '¿Cuáles son los tres principales problemas del país?' (respuesta múltiple; no es 'el principal problema'). 2013 y 2019: nota de la XI encuesta (2019, 'de 44% en 2013 a 62% en 2019'); "
         "2017: X encuesta, PDF p. 21, total nacional (1,314 entrevistas, Ipsos, ago-2017); 2025: XIII encuesta (dic-2025), 'máximo histórico con un 67%' (cifra de la publicación de Proética embebida en la nota; confianza media). "
         "Ediciones 2006, 2008, 2010, 2012, 2015 y 2022 existen, pero no se extrajo el dato de forma verificable.")

# ---------- por gobierno ----------
GOB = {"garcia_2006": 2006, "humala_2011": 2011, "ppk_2016": 2016, "castillo_2021": 2021, "keiko_2026": 2026}
def pick(s, cands):
    for y in cands:
        v = s.get(str(y))
        if v is not None: return {"anio": y, "valor": v}
    return None
def bti_pick(s, t):
    rec = max((e for e in range(2006, 2027, 2) if e - 1 <= t and s.get(str(e)) is not None), default=None)
    pri = next((e for e in (t + 3, t + 4) if s.get(str(e)) is not None), None) if t < 2026 else None
    return ({"anio": rec, "valor": s[str(rec)]} if rec else None, {"anio": pri, "valor": s[str(pri)]} if pri else None)

por = {}
for g, t in GOB.items():
    por[g] = {"asume": f"{t}-07-28", "indices": {}}
    for ix in idx:
        s = ix["serie"]
        if ix["id"].startswith("bti_"):
            rec, pri = bti_pick(s, t)
        else:
            rec = pick(s, [t - 1, t, t - 2])
            pri = pick(s, [t + 1, t + 2]) if t < 2026 else None
        e = {"recibio_anio": rec, "primer_anio": pri}
        if t == 2026:
            last = max((int(k) for k, v in s.items() if v is not None), default=None)
            e["primer_anio"] = None
            e["linea_base"] = {"anio": last, "valor": s[str(last)]} if last else None
            e["nota"] = "Primer año aún no medido; línea base = última medición disponible al 7-nov-2026."
        flags = []
        if rec and rec["anio"] != t - 1: flags.append(f"recibió usa {rec['anio']} (no hay {t-1})" if not ix["id"].startswith("bti_") else "BTI: edición cuyo periodo termina antes de asumir")
        if pri and pri["anio"] != t + 1 and not ix["id"].startswith("bti_"): flags.append(f"primer año usa {pri['anio']} (no hay {t+1})")
        if ix["id"] == "cpi_score" and rec and pri and (rec["anio"] < 2012) != (pri["anio"] < 2012): flags.append("ruptura de escala CPI entre ambos valores")
        if ix["id"] in ("rsf_score", "rsf_rank") and rec and pri and (rec["anio"] < 2022) != (pri["anio"] < 2022): flags.append("ruptura metodológica RSF 2022: no comparar")
        if flags: e["advertencias"] = flags
        por[g]["indices"][ix["id"]] = e
por["_regla"] = ("recibio_anio = dato del año t-1 (último año completo antes de asumir el 28-jul-t); si no existe, el de asunción t, luego t-2. "
                 "primer_anio = año t+1 (primer año calendario completo); si no existe, t+2. Para BTI (bienal, por edición): recibió = última edición cuyo periodo "
                 "termina antes de asumir; primer año = edición t+3 (cubre feb-(t) a ene-(t+2)). Keiko (t=2026): sin primer año; linea_base = última medición.")

caveats = [
    "Fecha de corte: 7-nov-2026. Ningún índice anual mide aún el gobierno iniciado el 28-jul-2026: las últimas mediciones (WGI 2025, CPI 2025, V-Dem 2025, EIU 2025, FH 2025, WJP 2025, RSF 2026, BTI 2026) describen el país que RECIBE Keiko Fujimori, no su gestión.",
    "Atribución: el año t-1 de cada gobierno es también el último año del gobierno anterior; además, entre 2016 y 2026 hubo presidentes no electos (Vizcarra, Merino, Sagasti, Boluarte y sucesores) cuyos años cuentan como 'país que recibió'. El índice mide al país, no al presidente.",
    "Los índices de percepción (CPI, WGI, V-Dem por expertos) reaccionan a escándalos y destapes: más investigaciones pueden empeorar la percepción aunque haya más control.",
    "WGI: el Banco Mundial cambió de metodología (2025): los códigos antiguos (CC.EST, CC.PER.RNK) ya no responden; se usan GOV_WGI_*.EST y GOV_WGI_*.SC (0-100, no percentil). La serie completa se re-estima en cada edición; los intervalos de confianza son amplios (diferencias < ~0.2 en la estimación no son significativas).",
    "CPI: escala 0-10 hasta 2011 y 0-100 desde 2012 (no comparables). García (2005 vs 2007) y Humala recibió (2010, 0-10) vs primer año (2012, 0-100) cruzan la ruptura en Humala.",
    "RSF: metodología nueva desde 2022; Castillo recibió (2020) y primer año (2022) no son comparables. El año RSF es la edición (abr-may), que refleja sobre todo el año anterior.",
    "EIU: valores tomados de Wikipedia (fuente secundaria) porque OWID no redistribuye (HTTP 403) y la EIU pide registro. Sin datos 2005, 2007 ni 2009.",
    "Freedom House: año = año cubierto (edición siguiente). Total = PR + CL (OWID). Verificado contra freedomhouse.org en 2020, 2024 y 2025.",
    "WJP: rango calculado por nosotros (posible diferencia de ±1 con el oficial). Sin datos de Perú antes de 2012 en el archivo histórico. El número de países varía (97 a 143), por lo que el puesto no es comparable entre años; usar el puntaje.",
    "BTI: bienal; año = edición, cuyo periodo de evaluación termina el 31 de enero del año anterior.",
    "Global State of Democracy (IDEA): NO incluido; no se halló una descarga directa sin buscador (se agotó el presupuesto de búsquedas web de la sesión).",
    "Contraloría: solo 2021 verificado (S/ 24,262 millones). Proética: solo 2013, 2017, 2019 y 2025 verificados; el dato 2025 (67 %) proviene de una publicación de Proética embebida, no del PDF.",
    "Semáforo sugerido: comparar cada valor contra el 'recibió' del mismo gobierno (dirección del cambio) y no contra otros índices; para puestos, considerar que el número de países cambia.",
]

out = {"generado": "2026-11-07", "descripcion": "Valores de Perú en índices internacionales de gobernanza, corrupción y democracia, 2005-2026, y comparación por gobierno.",
       "scripts": ["etl/intl_gob_wgi.py", "etl/intl_gob_cpi.py", "etl/intl_gob_rsf.py", "etl/intl_gob_wjp.py", "etl/intl_gob_bti.py", "etl/intl_gob_build.py"],
       "indices": idx, "por_gobierno": por, "caveats": caveats}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print("OK", os.path.abspath(OUT), len(idx), "índices")
