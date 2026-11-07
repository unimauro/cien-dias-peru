"""Arma research/resultados.json a partir de las salidas de:
  resultados_bcrp.py, resultados_sinadef.py, resultados_vacunas.py
Uso: python3 -I resultados_build.py bcrp.json sinadef.json vacunas.json <out resultados.json>"""
import json, sys
bcrp, sin, vac = (json.load(open(p)) for p in sys.argv[1:4])
OUT = sys.argv[4]
MES = dict(Ene="01", Feb="02", Mar="03", Abr="04", May="05", Jun="06", Jul="07", Ago="08", Sep="09", Oct="10", Nov="11", Dic="12")
NP = "aún no publicado"
def iso(lbl):
    m, y = lbl.split("."); return f"{y}-{MES[m]}"
def ser(code, y, desde="01", hasta="12"):
    return [[iso(p), v] for p, v in bcrp[code]["serie"] if iso(p)[:4] == str(y) and desde <= iso(p)[5:] <= hasta]
def val(code, ym):
    return dict((iso(p), v) for p, v in bcrp[code]["serie"]).get(ym, NP)
TRI = {"06": "abr-may-jun", "07": "may-jun-jul", "08": "jun-jul-ago", "09": "jul-ago-set", "10": "ago-set-oct"}
BCRP_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/{}/html"
def lab(code, y, mes, trim=False):
    return {"periodo": (f"{TRI[mes]} {y} (trimestre móvil)" if trim else f"{y}-{mes}"), "valor": val(code, f"{y}-{mes}")}

ind = []
# 1. Homicidios
def hom(y):
    w = sin["ventanas"][str(y)]
    a, d = w["100_dias_previos"], w["100_dias_gobierno"]
    return {"antes": {"periodo": f"{a[0]} a {a[1]} (100 días previos)", "valor": a[2]},
            "durante": {"periodo": f"{d[0]} a {d[1]} (100 días de gobierno)", "valor": d[2]},
            "serie": [[m, n] for m, n in sin["mensual"] if m[:4] == str(y)]}
ind.append({"id": "homicidios_sinadef", "nombre": "Homicidios registrados en SINADEF (Perú)", "unidad": "defunciones",
  "fuente": f"MINSA – SINADEF (muerte violenta = HOMICIDIO con necropsia), vía espejo diario github.com/JudithCristina/sinadef-automatizado; corte {sin['corte_datos']}",
  "fuente_url": "https://www.minsa.gob.pe/defunciones/", "2021": hom(2021), "2026": hom(2026),
  "rezago_nota": "SINADEF se completa con semanas de retraso (p. ej. junio-2026 pasó de 188 a 196 entre el 22-jul y el 1-nov), así que las cifras de oct-nov 2026 todavía subirán. Las medidas de seguridad (estados de emergencia, facultades delegadas aprobadas en oct-2026) tardan meses en reflejarse. 2021: +2.7 % frente a los 100 días previos; 2026: +4.3 % (cifra provisional). Ninguna de las dos variaciones es grande frente al ruido mensual (±15 %).",
  "confianza": "media: fuente oficial, pero procesada por un tercero (el filtro exige necropsia) y con subregistro reciente. Los totales mensuales de 2026 coinciden ±5 con los que publicó la prensa (ago 178, set 153-158, mar 202)."})
# 2-4. Empleo Lima Metropolitana
for code, iid, nom, uni, nota in [
  ("PN38063GM", "desempleo_lima", "Tasa de desempleo, Lima Metropolitana", "%",
   "El mercado laboral responde al ciclo económico y a la demanda externa más que a 100 días de gestión. En 2021 la caída del desempleo es en gran parte la recuperación tras el confinamiento de 2020. El trimestre ago-set-oct 2026 sale a mediados de noviembre; en 2021 fue 9.6 %."),
  ("PN38051GM", "ocupados_lima", "Población ocupada, Lima Metropolitana", "miles de personas",
   "Igual que el desempleo: depende del ciclo económico. En 2021 influye el rebote pospandemia. En 2026 la serie ya venía creciendo desde antes del 28-jul."),
  ("PN38070GM", "ingreso_lima", "Ingreso promedio mensual por trabajo, Lima Metropolitana", "S/ corrientes",
   "Está en soles nominales: hay que descontar la inflación (4-5 % anual). Los salarios se ajustan con meses de retraso.")]:
    ind.append({"id": iid, "nombre": nom + " (trimestre móvil)", "unidad": uni,
      "fuente": f"INEI – Encuesta Permanente de Empleo, serie BCRPData {code}", "fuente_url": BCRP_URL.format(code),
      "2021": {"antes": lab(code, 2021, "06", True), "durante": lab(code, 2021, "09", True), "serie": ser(code, 2021, "01", "11")},
      "2026": {"antes": lab(code, 2026, "06", True), "durante": lab(code, 2026, "09", True), "serie": ser(code, 2026)},
      "rezago_nota": nota + " Se usa el mismo trimestre (jul-ago-set) en los dos años para que la comparación sea simétrica. Ese trimestre solo se superpone en parte con la ventana de 100 días.",
      "confianza": "alta (dato oficial INEI). La atribución al gobierno es baja."})
# 5. Inflación de alimentos 12m
a12 = dict(bcrp["ALIM12"]["serie"])
def al(y, m): return {"periodo": f"{y}-{m} (var. 12 meses)", "valor": a12.get(f"{MES_INV[m]}.{y}", NP)}
MES_INV = {v: k for k, v in MES.items()}
ind.append({"id": "inflacion_alimentos", "nombre": "Inflación de alimentos y bebidas, Lima Metropolitana (12 meses)", "unidad": "% interanual",
  "fuente": "INEI – IPC Lima Metropolitana. Serie BCRPData PN01313PM (variación mensual), compuesta a 12 meses en resultados_bcrp.py",
  "fuente_url": BCRP_URL.format("PN01313PM"),
  "2021": {"antes": al(2021, "06"), "durante": al(2021, "10"), "serie": [[iso(p), v] for p, v in bcrp["ALIM12"]["serie"] if p.endswith("2021")]},
  "2026": {"antes": al(2026, "06"), "durante": al(2026, "10"), "serie": [[iso(p), v] for p, v in bcrp["ALIM12"]["serie"] if p.endswith("2026")]},
  "rezago_nota": "La inflación de alimentos depende de choques de oferta: clima (El Niño en 2026), precios internacionales y tipo de cambio. En 2021 hubo un choque global de commodities y una depreciación del sol por la incertidumbre política: esa parte sí es atribuible en parte a la coyuntura política. La política monetaria (BCRP, autónomo) actúa con 12-18 meses de rezago. Octubre-2026: +1.03 % mensual.",
  "confianza": "alta para el dato. La variación a 12 meses se calculó componiendo las variaciones mensuales oficiales, así que puede diferir ±0.05 pp de la cifra que publica el INEI."})
# 6. IPC general
ind.append({"id": "inflacion_general", "nombre": "Inflación general, Lima Metropolitana (12 meses)", "unidad": "% interanual",
  "fuente": "INEI – IPC Lima Metropolitana, serie BCRPData PN01273PM", "fuente_url": BCRP_URL.format("PN01273PM"),
  "2021": {"antes": lab("PN01273PM", 2021, "06"), "durante": lab("PN01273PM", 2021, "10"), "serie": ser("PN01273PM", 2021, "01", "11")},
  "2026": {"antes": lab("PN01273PM", 2026, "06"), "durante": lab("PN01273PM", 2026, "10"), "serie": ser("PN01273PM", 2026)},
  "rezago_nota": "La inflación es un resultado macro que maneja el BCRP con 12-18 meses de rezago. En 100 días el gobierno solo influye mediante expectativas, el tipo de cambio y medidas sobre precios regulados.",
  "confianza": "alta (dato oficial). La atribución al gobierno es baja."})
# 7. Gas doméstico
ind.append({"id": "precio_gas_domestico", "nombre": "Precio real del gas doméstico (GLP / balón), índice", "unidad": "índice real 2010=100",
  "fuente": "BCRP – índices reales de precios de combustibles (sobre datos del INEI), serie PN01440PM", "fuente_url": BCRP_URL.format("PN01440PM"),
  "2021": {"antes": lab("PN01440PM", 2021, "06"), "durante": lab("PN01440PM", 2021, "10"), "serie": ser("PN01440PM", 2021, "01", "11")},
  "2026": {"antes": lab("PN01440PM", 2026, "06"), "durante": lab("PN01440PM", 2026, "10"), "serie": ser("PN01440PM", 2026)},
  "rezago_nota": "Es un índice deflactado, no el precio en soles del balón de 10 kg. Depende del precio internacional del GLP y del Fondo de Estabilización (FEPC). El precio nominal del balón y el del pollo NO se recolectaron: el buscador web se agotó y no se halló la serie en BCRPData.",
  "confianza": "media (índice oficial, pero solo una aproximación al precio que paga el hogar)."})
# 8. PBI
ind.append({"id": "pbi_mensual", "nombre": "Producción nacional (PBI mensual), variación interanual", "unidad": "% interanual",
  "fuente": "INEI – Avance coyuntural de la producción nacional, serie BCRPData PN01728AM", "fuente_url": BCRP_URL.format("PN01728AM"),
  "2021": {"antes": lab("PN01728AM", 2021, "06"), "durante": lab("PN01728AM", 2021, "08"), "serie": ser("PN01728AM", 2021, "01", "11")},
  "2026": {"antes": lab("PN01728AM", 2026, "06"), "durante": lab("PN01728AM", 2026, "08"), "serie": ser("PN01728AM", 2026)},
  "rezago_nota": "Es actividad económica, no valor público en sentido estricto; se incluye solo como contexto. En 2021 las tasas están infladas por el efecto base de 2020 (pandemia). El PBI de setiembre-2026 sale a mediados de noviembre: aún no publicado.",
  "confianza": "alta para el dato; es un indicador de contexto, no de resultado de gestión."})
# 9. Extorsión
ind.append({"id": "denuncias_extorsion", "nombre": "Denuncias por extorsión (SIDPOL, PNP)", "unidad": "denuncias/mes",
  "fuente": "PNP – SIDPOL / Mininter datos abiertos", "fuente_url": "https://www.datosabiertos.gob.pe/",
  "2021": {"antes": {"periodo": "abr-jun 2021", "valor": "no obtenido"}, "durante": {"periodo": "ago-oct 2021", "valor": "no obtenido"}, "serie": []},
  "2026": {"antes": {"periodo": "abr-jun 2026", "valor": "no publicado (SIDPOL reservado)"}, "durante": {"periodo": "ago-oct 2026", "valor": "no publicado (SIDPOL reservado)"}, "serie": []},
  "rezago_nota": "En agosto de 2025 la PNP declaró reservada por 5 años la información del SIDPOL (Infobae, 17-set-2025). El portal datosabiertos.gob.pe bloquea las descargas automáticas (WAF, HTTP 418), así que no se pudo bajar la serie de 2021. Referencias anuales encontradas: 22,675 denuncias en 2023, 22,361 en 2024 y 26,585 en 2025 (ComexPerú, citado por Expreso). Además, el Ministerio Público registró 11,946 denuncias en el primer semestre de 2026, pero es otra fuente y no es comparable. No se estima ningún valor.",
  "confianza": "nula: sin dato mensual verificable"})
# 10. Vacunación 2021
ind.append({"id": "vacunacion_covid_2021", "nombre": "Dosis de vacuna COVID-19 aplicadas (solo contexto 2021)", "unidad": "dosis",
  "fuente": "MINSA – datosabiertos.gob.pe/dataset/vacunacion, vía el espejo de Our World in Data", "fuente_url": vac["fuente"],
  "2021": {"antes": {"periodo": "2021-04-19 a 2021-07-27 (100 días previos)", "valor": vac["dosis_100_dias_previos"]},
           "durante": {"periodo": "2021-07-28 a 2021-11-05 (100 días de gobierno)", "valor": vac["dosis_100_dias_gobierno"]},
           "serie": [[m, v] for m, v in vac["serie_mensual_acumulado"] if m < "2021-11"] + [["2021-11-05", vac["acumulado_5nov"]]],
           "nota_serie": "acumulado de dosis al cierre de cada mes",
           "esquema_completo": {"2021-07-27": vac["completos_27jul"], "2021-11-05": vac["completos_5nov"]}},
  "2026": {"antes": {"periodo": "n/a", "valor": "no aplica"}, "durante": {"periodo": "n/a", "valor": "no aplica"}, "serie": []},
  "rezago_nota": "Es el único indicador de la lista que se movió con fuerza dentro de los 100 días: las dosis se duplicaron (11.6 M → 23.5 M) y las personas con esquema completo pasaron de 4.9 M a 16.2 M. Pero el ritmo depende sobre todo de la llegada de vacunas compradas antes (gobierno de Sagasti) y de la logística ya montada. Además, es un producto/cobertura y no un resultado final (el resultado sería la mortalidad COVID).",
  "confianza": "alta (dato oficial MINSA replicado por OWID)"})
# 11. Anemia
ind.append({"id": "anemia_infantil", "nombre": "Anemia en niñas y niños de 6-35 meses", "unidad": "%",
  "fuente": "INEI – ENDES", "fuente_url": "https://proyectos.inei.gob.pe/endes/",
  "2021": {"antes": {"periodo": "2020 (anual)", "valor": "no mensual"}, "durante": {"periodo": "n/a", "valor": "no mensual"}, "serie": []},
  "2026": {"antes": {"periodo": "2025 (anual)", "valor": "no mensual"}, "durante": {"periodo": "n/a", "valor": "no mensual"}, "serie": []},
  "rezago_nota": "La ENDES es anual (con algún avance semestral), así que no existe un dato mensual para medir 100 días. Lo mismo pasa con la pobreza monetaria (ENAHO, anual) y la victimización (ENAPRES, semestral móvil). Son los verdaderos indicadores de valor público, pero sus efectos se ven en años.",
  "confianza": "n/a"})

concl = ("Con datos oficiales mensuales, ninguno de los dos gobiernos muestra un cambio en los indicadores de resultado que se pueda atribuir a su gestión en 100 días. "
 "Tampoco es justo concluir que 'no tienen resultados': con el rezago de estos indicadores, 100 días no alcanzan para medirlo. "
 f"Homicidios (SINADEF): 2021 pasó de {sin['ventanas']['2021']['100_dias_previos'][2]} a {sin['ventanas']['2021']['100_dias_gobierno'][2]} y 2026 de {sin['ventanas']['2026']['100_dias_previos'][2]} a {sin['ventanas']['2026']['100_dias_gobierno'][2]} (provisional) frente a los 100 días previos: una ligera alza en ambos casos, dentro del ruido; 2026 parte de un nivel ~50 % más alto. "
 "El desempleo de Lima bajó en ambos casos (10.3→10.0 % en 2021; 4.9→4.4 % en 2026, mínimo histórico para un tercer trimestre), pero son tendencias que ya venían de antes (rebote pospandemia en 2021; ciclo económico en 2026). "
 "La inflación de alimentos subió en ambos: en 2021 con fuerza (3.7→7.5 %), con un choque global y la depreciación del sol por la incertidumbre política; en 2026 menos (3.5→5.3 %), con un salto en octubre ligado a choques de oferta. "
 "El único indicador que se movió mucho fue la vacunación COVID en 2021: 23.5 M dosis, el doble que en los 100 días previos. Es cobertura, no un resultado final, y heredaba compras previas. "
 "Lo honesto es decir que en 100 días se puede juzgar la dirección de las decisiones (insumos, actividades, productos) y advertir alertas tempranas, pero no el valor público, que requiere 12-24 meses y encuestas anuales (ENDES, ENAHO, ENAPRES).")
caveats = [
 "Efecto rezago: la mayoría de resultados (homicidios, empleo, inflación, anemia, pobreza) responde a políticas con 6-24 meses de retraso y a factores externos (ciclo global, clima, El Niño 2026, pandemia en 2021).",
 "Comparar 'antes' contra 'durante' no es un análisis causal: no hay contrafactual, y la estacionalidad (feriados, fiestas patrias, campaña agrícola) afecta los meses de jul-nov.",
 "2021 está distorsionado por la pandemia (efecto base en el PBI y el empleo, rebote de la movilidad y de los homicidios).",
 "SINADEF registra con retraso: las cifras de oct-nov 2026 son provisionales y van a subir. Además, SINADEF y la PNP dan cifras de homicidios distintas (PerúCheck: −3.5 % vs −24.6 % en el 1S-2026).",
 "El SIDPOL (denuncias de extorsión y otros delitos) está reservado desde ago-2025 y no hay serie mensual pública verificable para 2026. Para 2021 no se pudo descargar (datosabiertos.gob.pe bloquea los scripts).",
 "Los trimestres móviles de empleo de ago-set-oct 2026 y el PBI de setiembre-2026 aún no están publicados (el INEI los publica a mediados de noviembre). No se estimaron.",
 "No se recolectaron el precio nominal del pollo ni el del balón de gas: el buscador web se agotó. Se usa el IPC de alimentos y el índice real de gas doméstico del BCRP.",
 "Los homicidios vienen de un espejo de terceros del CSV oficial de MINSA (la descarga oficial está detrás de Cloudflare). Sus totales cuadran con las cifras de la prensa, ±5 por mes.",
 "Fecha de corte: 7-nov-2026. Se verificó que Keiko Fujimori asumió el 28-jul-2026 (Euronews, SCMP), por lo que sus 100 días terminaron el 4-5-nov-2026."]
json.dump({"generado": "2026-11-07", "ventanas": {"2021": "2021-07-28 a 2021-11-05", "2026": "2026-07-28 a 2026-11-05"},
           "indicadores": ind, "conclusion_neutral": concl, "caveats": caveats},
          open(OUT, "w"), ensure_ascii=False, indent=1)
print("ok", len(ind))
