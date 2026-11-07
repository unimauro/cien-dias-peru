"""Construye research/intl_social.json: indicadores de desigualdad, pobreza, desarrollo humano,
confianza ciudadana y seguridad del Perú (2005-2026) y su corte por gobierno.

Fuentes descargables (cache en etl/cache/intl_soc/):
  - Banco Mundial API (Gini SI.POV.GINI)
  - PNUD HDR25_Composite_indices_complete_time_series.csv (IDH, IDH-D)
  - INEI xlsx de pobreza 2015-2025 (m.inei.gob.pe/estadisticas/indice-tematico/poverty/)
  - ONU SDG API VC_IHR_PSRC (homicidios, UNODC)
Valores transcritos de PDF oficiales (INEI, ENDES, Latinobarómetro, LAPOP) con su página citada abajo.
Latinobarómetro: % calculados de microdatos con etl/intl_soc_latinobarometro.py y cotejados con los informes.

Uso: ~/.venvs/cien-dias/bin/python etl/intl_soc_build.py
"""
import csv, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "etl", "cache", "intl_soc")
OUT = os.path.join(ROOT, "research", "intl_social.json")
os.makedirs(CACHE, exist_ok=True)


def get(url, fname):
    p = os.path.join(CACHE, fname)
    if not os.path.exists(p):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(p, "wb") as f:
            f.write(r.read())
    return p


def wb(ind):
    p = get(f"https://api.worldbank.org/v2/country/PER/indicator/{ind}?format=json&per_page=100", f"wb_{ind}.json")
    d = json.load(open(p))
    return {r["date"]: r["value"] for r in d[1] if r["value"] is not None and 2005 <= int(r["date"]) <= 2026}


def hdr():
    p = get("https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv",
            "HDR25_Composite_indices_complete_time_series.csv")
    row = [r for r in csv.DictReader(open(p, encoding="latin-1")) if r["iso3"] == "PER"][0]
    hdi = {str(y): float(row[f"hdi_{y}"]) for y in range(2005, 2024) if row.get(f"hdi_{y}")}
    ihdi = {str(y): float(row[f"ihdi_{y}"]) for y in range(2005, 2024) if row.get(f"ihdi_{y}")}
    return hdi, ihdi, int(row["hdi_rank_2023"])


def inei_pobreza():
    import openpyxl  # venv ~/.venvs/cien-dias
    out = {}
    for k, url in (("total", "https://m.inei.gob.pe/media/MenuRecursivo/indices_tematicos/cd1_82.xlsx"),
                   ("extrema", "https://m.inei.gob.pe/media/MenuRecursivo/indices_tematicos/cd2_73.xlsx")):
        p = get(url, f"inei_pov_{'1' if k == 'total' else '2'}.xlsx")
        ws = openpyxl.load_workbook(p, read_only=True, data_only=True).worksheets[0]
        rows = [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
        hdr_ = next(r for r in rows if r[0] and str(r[0]).startswith("Ámbito"))
        tot = next(r for r in rows if r[0] and str(r[0]).strip() == "Total")
        out[k] = {str(y): round(v, 1) for y, v in zip(hdr_[1:], tot[1:]) if y and v is not None}
    return out


def sdg_homicidios():
    p = get("https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode=VC_IHR_PSRC&areaCode=604&pageSize=200",
            "sdg_hom.json")
    d = json.load(open(p))
    return {str(int(x["timePeriodStart"])): round(float(x["value"]), 2) for x in d["data"]
            if x["dimensions"].get("Sex") == "BOTHSEX"}


# ---------------- datos transcritos de PDF oficiales ----------------
URL_POB_0412 = "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1106/libro.pdf"
URL_POB_0914 = "https://www.inei.gob.pe/media/cifras_de_pobreza/informetecnico_pobreza2014.pdf"
URL_POB_XLSX = "https://m.inei.gob.pe/estadisticas/indice-tematico/poverty/"
# Perfil de la pobreza 2004-2012 (p.11-12, gráficos) y Evolución de la pobreza monetaria 2009-2014 (cuadros 3.1 y 3.4)
POB_0514 = {"2005": 55.6, "2006": 49.1, "2007": 42.4, "2008": 37.3, "2009": 33.5, "2010": 30.8,
            "2011": 27.8, "2012": 25.8, "2013": 23.9, "2014": 22.7}
EXT_0514 = {"2005": 15.8, "2006": 13.8, "2007": 11.2, "2008": 10.9, "2009": 9.5, "2010": 7.6,
            "2011": 6.3, "2012": 6.0, "2013": 4.7, "2014": 4.3}

URL_ENDES23 = "https://proyectos.inei.gob.pe/endes/2023/INFORME_PRINCIPAL/INFORMES_PRINCIPALES_2023.pdf"
URL_MCLCP = "https://intranet.mesadeconcertacion.org.pe/storage/documentos/2026-07-14/presentacion-seguimiento-concertado-social-2026-1.pdf"
YEARS_0923 = [str(y) for y in range(2009, 2024)]
# ENDES 2023, "Principales indicadores 2009-2023", p.30
ANEMIA_0923 = [50.4, 50.3, 41.6, 44.5, 46.4, 46.8, 43.5, 43.6, 43.6, 43.5, 40.1, 40.0, 38.8, 42.4, 43.1]
DCI_0923 = [23.8, 23.2, 19.5, 18.1, 17.5, 14.6, 14.4, 13.1, 12.9, 12.2, 12.2, 12.1, 11.5, 11.7, 11.5]
ANEMIA = dict(zip(YEARS_0923, ANEMIA_0923)) | {"2024": 43.7, "2025": 43.4}  # MCLCP p.5 (fuente INEI/ENDES 2025)
DCI = dict(zip(YEARS_0923, DCI_0923)) | {"2024": 12.1, "2025": 12.1}  # MCLCP p.3 (fuente INEI/ENDES 2025)

URL_INF_0719 = "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1764/libro.pdf"
URL_INF_0720 = "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1828/libro.pdf"
URL_INF_2223 = "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1972/libro.pdf"
URL_INF_2224 = "https://cdn.www.gob.pe/uploads/document/file/9215525/7564428-libro.pdf"
INFORMAL = dict(zip([str(y) for y in range(2007, 2020)],
                    [80.0, 79.2, 77.2, 77.1, 75.1, 74.3, 73.7, 72.8, 73.2, 72.0, 72.5, 72.4, 72.7]))  # Lib1764 p.64 (ENAHO)
INFORMAL |= {"2020": 75.3,   # Lib1828 p.71 (ENAHO)
             "2022": 74.0, "2023": 71.1,  # Lib1972 cuadro 4.1 (EPEN)
             "2024": 70.9}   # Cuenta satélite 2022-2024 p.7/36 (EPEN)

URL_LB24 = "https://www.latinobarometro.org/documents/LAT-2024/latinobarometro-informe-2024.pdf"
URL_LB23 = "https://www.latinobarometro.org/documents/LAT-2023/latinobarometro-informe-2023.pdf"
URL_LB26 = "https://www.latinobarometro.org/documents/informe-latinobarometro-2026.pdf"
LB_APOYO = {"2005": 39.7, "2006": 54.6, "2007": 47.4, "2008": 45.0, "2009": 51.9, "2010": 61.0, "2011": 58.9,
            "2013": 55.8, "2015": 55.9, "2016": 52.9, "2017": 45.1, "2018": 42.8, "2020": 46.4, "2023": 50.4,
            "2024": 44.2, "2026": 53.0}
LB_SATIS = {"2005": 13.2, "2006": 22.8, "2007": 17.1, "2008": 15.8, "2009": 22.2, "2010": 28.2, "2011": 30.8,
            "2013": 24.8, "2015": 24.9, "2016": 24.4, "2017": 15.6, "2018": 10.5, "2020": 10.9, "2023": 7.9,
            "2024": 10.0}
LB_CONF = {"2005": 14.9, "2006": 37.2, "2007": 22.2, "2008": 14.8, "2009": 22.1, "2010": 24.9, "2011": 33.5,
           "2013": 23.9, "2015": 19.9, "2016": 18.7, "2017": 18.4, "2018": 12.9, "2020": 16.2, "2023": 9.2,
           "2024": 8.4}

LAPOP = "https://www.vanderbilt.edu/cgd/wp-content/uploads/sites/157/lapop/peru/"
URL_LAPOP21 = LAPOP + "AB2021PER-Country-Report-Spanish-Final-220411.pdf"
URL_LAPOP19 = LAPOP + "AB2018-19-Peru-Country-Report-Final-W-200811.pdf"
URL_LAPOP23 = LAPOP + "ABPER2023-Pulso-de-la-democracia-20240905.pdf"
URL_LAPOP26 = "https://cdn.vanderbilt.edu/vu-wpfsx/wp-content/uploads/sites/157/2026/11/2026_Pulse-of-Democracy_20261105_ESP.pdf"
LAPOP_APOYO = {"2006": 53, "2008": 63, "2010": 52, "2012": 60, "2014": 59, "2017": 53, "2019": 49, "2021": 50,
               "2023": 51, "2025": 50}
LAPOP_EXC7 = {"2006": 85, "2008": 83, "2010": 89, "2012": 81, "2014": 88, "2017": 78, "2019": 76}
LAPOP_EXC7NEW = {"2017": 77.0, "2019": 84.7, "2021": 88}

URL_VIC25 = "https://cdn.www.gob.pe/uploads/document/file/9703029/7938429-victimizacion-en-el-peru-2025.pdf"
YRS_1525 = [str(y) for y in range(2015, 2026)]
VICTIM = dict(zip(YRS_1525, [30.8, 28.8, 26.4, 25.7, 26.6, 23.4, 18.2, 22.9, 27.1, 27.1, 25.3]))  # cuadro 1.1
INSEG = dict(zip(YRS_1525, [88.4, 90.0, 86.9, 86.3, 85.8, 83.2, 83.9, 85.2, 83.6, 86.0, 84.4]))  # cuadro 3.1


def build():
    gini = wb("SI.POV.GINI")
    hdi, ihdi, rank23 = hdr()
    pob = inei_pobreza()
    hom = sdg_homicidios()

    def full(serie):
        return {str(y): serie.get(str(y)) for y in range(2005, 2027)}

    ind = [
        dict(id="gini", nombre="Coeficiente de Gini (ingreso)", dimension="desigualdad", unidad="índice 0-100",
             mejor="bajo", fuente="Banco Mundial, WDI SI.POV.GINI (base SEDLAC sobre ENAHO-INEI)",
             fuente_url="https://api.worldbank.org/v2/country/PER/indicator/SI.POV.GINI?format=json&per_page=100",
             serie=full(gini),
             nota="Gini de ingreso per cápita del Banco Mundial; 2025 y 2026 aún no publicados. El INEI publica además un Gini del gasto (p. ej. 0,41 en 2007 y 0,35 en 2017, Lib1533 p.21), que no es comparable con esta serie."),
        dict(id="pobreza_monetaria", nombre="Pobreza monetaria (% de la población)", dimension="pobreza",
             unidad="%", mejor="bajo", fuente="INEI – ENAHO, informes técnicos de evolución de la pobreza monetaria",
             fuente_url=URL_POB_XLSX, serie=full(POB_0514 | pob["total"]),
             fuente_por_tramo={"2005-2012": URL_POB_0412 + " (p.11)", "2009-2014": URL_POB_0914 + " (cuadro 3.1)",
                               "2015-2025": URL_POB_XLSX + " (cd1_82.xlsx)"},
             nota="Serie con la metodología revisada de 2012 (aplicada hacia atrás desde 2004). El dato de 2025 (25,7 %) lo publicó el INEI el 5-may-2026; 2026 se publicará hacia mayo de 2027."),
        dict(id="pobreza_extrema", nombre="Pobreza extrema (% de la población)", dimension="pobreza", unidad="%",
             mejor="bajo", fuente="INEI – ENAHO", fuente_url=URL_POB_XLSX, serie=full(EXT_0514 | pob["extrema"]),
             fuente_por_tramo={"2005-2012": URL_POB_0412 + " (p.12)", "2009-2014": URL_POB_0914 + " (cuadro 3.4)",
                               "2015-2025": URL_POB_XLSX + " (cd2_73.xlsx)"},
             nota="En el informe de 2025, la pobreza extrema de 2024 figura como 5,5 % (el xlsx vigente da 5,50)."),
        dict(id="idh", nombre="Índice de Desarrollo Humano (IDH)", dimension="desarrollo_humano", unidad="índice 0-1",
             mejor="alto", fuente="PNUD – Informe sobre Desarrollo Humano 2025 (serie temporal de índices compuestos)",
             fuente_url="https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv",
             serie=full(hdi), ranking={"2023": rank23, "de": 193},
             nota=f"Serie recalculada por el PNUD con la metodología del HDR 2025 (el último dato es 2023). En 2023 el Perú ocupa el puesto {rank23} de 193. Los rankings publicados en informes anteriores no son comparables entre sí y por eso no se incluyen."),
        dict(id="idh_ajustado_desigualdad", nombre="IDH ajustado por desigualdad (IDH-D)",
             dimension="desarrollo_humano", unidad="índice 0-1", mejor="alto", fuente="PNUD – HDR 2025",
             fuente_url="https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv",
             serie=full(ihdi), nota="Existe desde 2010. En 2023 la pérdida por desigualdad es (0,794-0,633)/0,794 ≈ 20,3 %."),
        dict(id="anemia_6_35m", nombre="Anemia en niñas y niños de 6 a 35 meses", dimension="desarrollo_humano",
             unidad="%", mejor="bajo", fuente="INEI – ENDES", fuente_url=URL_ENDES23, serie=full(ANEMIA),
             fuente_por_tramo={"2009-2023": URL_ENDES23 + " (Principales indicadores, p.30)",
                               "2024-2025": URL_MCLCP + " (p.5, tabla con fuente INEI/ENDES 2025)"},
             nota="Serie comparable con el ajuste de hemoglobina por altitud anterior. Con la nueva directriz OMS 2024 (RM 251-2024-MINSA) el INEI da 28,4 (2021), 33,5 (2022), 34,6 (2023), 35,3 (2024) y 34,9 (2025); no hay que mezclar las dos series. La ENDES anual nacional empieza en 2009: 2005 y 2007-2008 eran muestras agrupadas (ENDES Continua), así que aquí no se usan."),
        dict(id="desnutricion_cronica_5", nombre="Desnutrición crónica en menores de 5 años (patrón OMS)",
             dimension="desarrollo_humano", unidad="%", mejor="bajo", fuente="INEI – ENDES", fuente_url=URL_ENDES23,
             serie=full(DCI),
             fuente_por_tramo={"2009-2023": URL_ENDES23 + " (p.30)", "2024-2025": URL_MCLCP + " (p.3, fuente INEI/ENDES 2025)"},
             nota="Antes de 2009 la ENDES no era anual. Como referencia, el Banco Mundial (SH.STA.STNT.ZS) da 29,2 en 2005 y 28,0 en 2007."),
        dict(id="informalidad_laboral", nombre="Tasa de empleo informal (% de la PEA ocupada)", dimension="pobreza",
             unidad="%", mejor="bajo", fuente="INEI – ENAHO (2007-2020) y EPEN (2022-2024)", fuente_url=URL_INF_0719,
             serie=full(INFORMAL),
             fuente_por_tramo={"2007-2019": URL_INF_0719 + " (p.64, ENAHO)", "2020": URL_INF_0720 + " (p.71, ENAHO)",
                               "2022-2023": URL_INF_2223 + " (cuadro 4.1, EPEN)", "2024": URL_INF_2224 + " (p.7 y 36, EPEN)"},
             nota="QUIEBRE DE SERIE en 2022: el INEI pasó de la ENAHO a la EPEN; para el mismo 2022, la ENAHO daba 75,7 y la EPEN 74,0. No hay dato ENAHO de 2005-2006 (la serie empieza en 2007). El 2021 (76,8 según ENAHO) y el 2025 (70,7 según EPEN) solo se vieron en prensa y no se verificaron en el documento del INEI, así que quedan en null. Para dimension se usó 'pobreza' porque el esquema no tiene una categoría de empleo."),
        dict(id="lb_apoyo_democracia", nombre="Apoyo a la democracia (Latinobarómetro)", dimension="confianza",
             unidad="% 'la democracia es preferible'", mejor="alto", fuente="Latinobarómetro (microdatos, ponderador wt; cotejado con los informes)",
             fuente_url=URL_LB24, serie=full(LB_APOYO),
             fuente_por_tramo={"2005-2024": URL_LB24 + " (tabla p.34; % de microdatos)", "2026": URL_LB26 + " (tabla 1, p.13; trabajo de campo may-jun 2026)"},
             nota="No hubo encuesta en 2012, 2014, 2019, 2021, 2022 ni 2025. El dato de 2026 (53) se levantó antes de la asunción del 28-jul-2026."),
        dict(id="lb_satisfaccion_democracia", nombre="Satisfacción con la democracia (Latinobarómetro)",
             dimension="confianza", unidad="% muy + más bien satisfecho", mejor="alto",
             fuente="Latinobarómetro (microdatos)", fuente_url=URL_LB23, serie=full(LB_SATIS),
             nota="Cotejado con los informes de 2023 (p.39) y 2024 (p.42). El dato de 2026 solo aparece en un gráfico como imagen y no se transcribió."),
        dict(id="lb_confianza_gobierno", nombre="Confianza en el gobierno (Latinobarómetro)", dimension="confianza",
             unidad="% mucha + algo", mejor="alto", fuente="Latinobarómetro (microdatos)", fuente_url=URL_LB24,
             serie=full(LB_CONF),
             nota="Solo 2024 se cotejó con un informe (8 %, Informe 2024 p.60); los demás años salen de los microdatos. La redacción del ítem cambia (desde 2018 dice 'Gobierno de la Nación'). El dato de 2026 no está disponible."),
        dict(id="lapop_apoyo_democracia", nombre="Apoyo a la democracia (LAPOP, ING4)", dimension="confianza",
             unidad="% de acuerdo 5-7 en escala 1-7", mejor="alto", fuente="LAPOP / AmericasBarometer – informes Perú",
             fuente_url=URL_LAPOP21, serie=full(LAPOP_APOYO),
             fuente_por_tramo={"2006-2021": URL_LAPOP21 + " (p.22-23)", "2017": "AB2016-17 Perú p.33 (52,7)",
                               "2019": URL_LAPOP19 + " (49,3)", "2023": URL_LAPOP23 + " (gráfico 1.6)",
                               "2025": URL_LAPOP26 + " (p.48-49)"},
             nota="El año es el del trabajo de campo: la ronda 2016/17 va como 2017, la 2018/19 como 2019 y la del AmericasBarometer 2026 (oct-dic 2025) como 2025. Los informes de 2006-2012 publicaban promedios 0-100; aquí se usa la serie recalculada en %."),
        dict(id="lapop_corrupcion_funcionarios", nombre="Percepción de corrupción en funcionarios públicos (LAPOP, EXC7)",
             dimension="confianza", unidad="% muy + algo generalizada", mejor="bajo", fuente="LAPOP – informe Perú 2018/19, gráfico 4.9",
             fuente_url=URL_LAPOP19, serie=full(LAPOP_EXC7),
             nota="La pregunta no se reportó para el Perú en 2021 ni en 2023."),
        dict(id="lapop_corrupcion_politicos", nombre="Políticos involucrados en corrupción (LAPOP, EXC7NEW)",
             dimension="confianza", unidad="% 'más de la mitad' + 'todos'", mejor="bajo", fuente="LAPOP – informes Perú 2018/19 y 2021",
             fuente_url=URL_LAPOP21, serie=full(LAPOP_EXC7NEW),
             nota="Pregunta nueva desde 2016/17. No hay cifra del Perú publicada para 2023 ni para 2025; harían falta los microdatos, que requieren registro."),
        dict(id="victimizacion", nombre="Población urbana de 15+ años víctima de algún hecho delictivo", dimension="seguridad",
             unidad="% (últimos 12 meses)", mejor="bajo", fuente="INEI – ENAPRES, Victimización en el Perú 2025 (cuadro 1.1)",
             fuente_url=URL_VIC25, serie=full(VICTIM),
             nota="Ámbito nacional urbano. Desde 2025 el cálculo incluye las tentativas de extorsión, y la serie 2015-2024 publicada en el informe de 2025 es igual a la del informe de 2024. La ENAPRES empezó en 2010, pero los años 2010-2014 no se pudieron verificar en un documento del INEI y quedan en null. 2020-2021 están afectados por la pandemia."),
        dict(id="percepcion_inseguridad", nombre="Percepción de inseguridad (próximos 12 meses)", dimension="seguridad",
             unidad="% población urbana 15+", mejor="bajo", fuente="INEI – ENAPRES, Victimización en el Perú 2025 (cuadro 3.1)",
             fuente_url=URL_VIC25, serie=full(INSEG), nota="Los años 2010-2014 no se verificaron."),
        dict(id="homicidios_tasa", nombre="Tasa de homicidios intencionales por 100 mil habitantes", dimension="seguridad",
             unidad="por 100 mil hab.", mejor="bajo", fuente="UNODC (UN-CTS), vía ONU ODS 16.1.1 / Banco Mundial VC.IHR.PSRC.P5",
             fuente_url="https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode=VC_IHR_PSRC&areaCode=604",
             serie=full(hom),
             nota="La serie internacional solo cubre 2011-2021. Para 2022-2025 no se encontró una tasa oficial anual verificada. El proyecto tiene conteos SINADEF en research/resultados.json, pero no son una tasa ni son comparables con esta serie. Por eso Keiko no tiene línea base en este indicador."),
    ]

    gobiernos = [("garcia", "Alan García", "2006-07-28", 2006), ("humala", "Ollanta Humala", "2011-07-28", 2011),
                 ("ppk", "Pedro Pablo Kuczynski", "2016-07-28", 2016), ("castillo", "Pedro Castillo", "2021-07-28", 2021),
                 ("keiko", "Keiko Fujimori", "2026-07-28", 2026)]
    por = {}
    for gid, nom, fecha, t in gobiernos:
        vals = {}
        for i in ind:
            s = {k: v for k, v in i["serie"].items() if v is not None}
            if gid == "keiko":
                yrs = [int(y) for y in s if int(y) <= 2026]
                y0 = str(max(yrs)) if yrs else None
                t0 = {"anio": y0, "valor": s[y0], "regla": "última medición disponible (línea base)"} if y0 else None
                if t0 and 2026 - int(y0) > 3:  # dato demasiado viejo para describir el país de 2026
                    t0 = {"sin_dato_reciente": True, "ultimo_disponible": {"anio": y0, "valor": s[y0]},
                          "regla": "última medición > 3 años de antigüedad; no se usa como línea base"}
                t1 = None
            else:
                t0 = t1 = None
                for y, regla in ((t - 1, "año previo"), (t, "año de asunción"), (t - 2, "dos años antes (no hay t-1 ni t)")):
                    if str(y) in s:
                        t0 = {"anio": str(y), "valor": s[str(y)], "regla": regla}; break
                for y, regla in ((t + 1, "primer año (t+1)"), (t + 2, "t+2 (no hay dato en t+1)")):
                    if str(y) in s:
                        t1 = {"anio": str(y), "valor": s[str(y)], "regla": regla}; break
            cambio = sentido = None
            if t0 and t1:
                cambio = round(t1["valor"] - t0["valor"], 3)
                sentido = "igual" if cambio == 0 else (
                    "mejora" if (cambio > 0) == (i["mejor"] == "alto") else "empeora")
            vals[i["id"]] = {"recibio": t0 or "sin dato", "primer_anio": t1 if t1 else (
                "aún no existe" if gid == "keiko" else "sin dato"), "cambio": cambio, "sentido": sentido}
        por[gid] = {"nombre": nom, "asuncion": fecha, "valores": vals}

    caveats = [
        "Regla: «recibió» = año previo a la asunción (t-1), luego el año de asunción (t), luego t-2; «primer año» = t+1, o t+2 si no hay dato en t+1. Cada valor lleva el año que se usó y la regla aplicada.",
        "Keiko Fujimori asumió el 28-jul-2026: su «primer año» aún no existe. Su línea base es la última medición publicada, que en varios indicadores es 2025 o anterior (IDH 2023, Gini 2024) y no refleja su gestión.",
        "Las encuestas anuales (ENAHO, ENDES, ENAPRES) de un año t cubren en parte al gobierno saliente. El año de asunción mezcla a los dos gobiernos.",
        "Castillo recibió el país de 2020 (pandemia): el desplome de 2020 y el rebote de 2021-2022 son efecto del COVID-19, no de la gestión.",
        "Latinobarómetro y LAPOP no son anuales; cuando falta un año se usa el más cercano según la regla y se indica.",
        "Informalidad: quiebre ENAHO→EPEN en 2022. No hay que comparar valores de antes y después de ese año como si fueran la misma serie.",
        "Anemia: hay que usar la serie con el ajuste por altitud anterior; la cifra de 34,9 % de 2025 (nueva directriz OMS 2024) no es comparable con los años previos.",
        "Faltan sin verificar: victimización y percepción de inseguridad 2010-2014, homicidios 2005-2010 y 2022-2026, informalidad 2021 y 2025, satisfacción y confianza Latinobarómetro 2026, y LAPOP EXC7NEW 2023 y 2025.",
        "El semáforo solo debe leerse como dirección del cambio en el primer año; los indicadores estructurales (pobreza, anemia, IDH) responden con rezago y no pueden atribuirse solo a un gobierno.",
    ]
    out = {"generado": "2026-11-07", "indicadores": ind, "por_gobierno": por, "caveats": caveats}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("ok", OUT, len(ind))


if __name__ == "__main__":
    build()
