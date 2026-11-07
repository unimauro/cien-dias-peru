"""Ensambla research/expresidentes.json: datos curados (con URL y confianza) + macro de historico_bcrp.py.
Uso: python3 historico_bcrp.py /ruta/macro.json && python3 historico_build.py /ruta/macro.json
Investigación hecha el 7-nov-2026. Nada aquí es inferido sin marcarlo: los campos sin fuente van en null.
"""
import json, sys, os

MACRO = json.load(open(sys.argv[1]))
OUT = os.path.join(os.path.dirname(__file__), "..", "research", "expresidentes.json")

IPSOS_AGO06 = "https://www.ipsos.com/sites/default/files/publication/2009-11/Opinion_Data_Agosto_2006.pdf"
IPSOS_SET06 = "https://www.ipsos.com/sites/default/files/publication/2009-11/Opinion_Data_Setiembre_2006.pdf"
IPSOS_OCT06 = "https://www.ipsos.com/sites/default/files/publication/2009-11/Opinion_Data_Octubre_2006.pdf"
IPSOS_NOV06 = "https://www.ipsos.com/sites/default/files/publication/2009-11/Opinion_Data_Noviembre_2006.pdf"
IPSOS_AGO11 = "https://www.ipsos.com/sites/default/files/publication/2011-08/inicio_auspicioso.pdf"
IPSOS_NOV11 = "https://www.ipsos.com/sites/default/files/publication/2011-11/OpinionDataNoviembre2011.pdf"
IPSOS_NOV16 = "https://www.ipsos.com/sites/default/files/publication/2016-11/Opinion%20Data%20Noviembre.pdf"
FPIF = "https://fpif.org/garcas_first_100_days/"
CONVOCA = "https://www.americatv.com.pe/noticias/actualidad/gobierno-ppk-cumplio-solo-siete-29-promesas-n259854"


def macro(k):
    return [{kk: v for kk, v in m.items()} for m in MACRO[k]]


data = {
    "_meta": {
        "generado": "2026-11-07",
        "ventana": "28-jul (día 0) a 5-nov (día 100) de cada año",
        "escala_confianza": "alta = documento primario leído (PDF de la encuestadora, norma, nota oficial del Congreso); media = prensa/medio secundario leído; baja = fuente única secundaria, resumen de buscador o fecha aproximada",
        "cadena_valor": "insumo (recursos: dinero, personal, normas de gasto) / actividad (procesos, arreglos institucionales) / producto (bien o servicio entregado a la población) / resultado (cambio en la población) / impacto (efecto de largo plazo)",
        "scripts": ["etl/historico_bcrp.py", "etl/historico_build.py"],
    },
    "garcia_2006": {
        "presidente": "Alan García Pérez (2.º gobierno)",
        "dia0": "2006-07-28", "dia100": "2006-11-05",
        "balance_promesas": {
            "total": None, "cumplidas": None, "en_proceso": None, "incumplidas": None,
            "metodologia": "NO SE ENCONTRÓ un balance cuantitativo de promesas a los 100 días publicado por medios u ONG. Hay balances cualitativos (FPIF, 21-nov-2006, de John Feffer y Ronald Bruce St John) y académicos (CIES/PUCP). Las promesas emblemáticas abajo se clasifican a partir de normas y notas, no de un verificador.",
            "fuente_url": FPIF,
            "confianza": "media (sobre la inexistencia: búsqueda no exhaustiva en archivos de prensa 2006)",
        },
        "promesas_emblematicas": [
            {"texto": "Reducir sueldos de altos funcionarios (presidente S/ 16,000; congresistas y ministros S/ 15,600)",
             "estado": "cumplida — D.U. 019-2006 (31-jul-2006), compensación ago-dic 2006; se revirtió en ene-2009 (D.U. 001-2009)",
             "nivel_cadena_valor": "insumo",
             "fuente_url": "https://www.mef.gob.pe/es/por-instrumento/decreto-de-urgencia/1118-d-u-n-019-2006/file",
             "confianza": "media (montos en soles vienen de fuente secundaria; la norma los fija en URSP)"},
            {"texto": "Austeridad y racionalidad en el gasto público",
             "estado": "cumplida (norma emitida) — D.U. 020-2006 (ago-2006) y D.U. 021-2006 complementario",
             "nivel_cadena_valor": "insumo",
             "fuente_url": "https://www.mef.gob.pe/es/por-instrumento/decreto-de-urgencia/1113-d-u-n-020-2006/file",
             "confianza": "media"},
            {"texto": "Aporte de las mineras ('óbolo minero'; campaña: impuesto a sobreganancias) — S/ 2,500 M en 5 años",
             "estado": "en proceso a los 100 días — anunciado por el premier Del Castillo al presentar el gabinete (ago-2006); el formato de convenio (DS 071-2006-EM) es del 20-dic-2006, fuera de la ventana; se sustituyó el impuesto prometido por un aporte voluntario",
             "nivel_cadena_valor": "insumo",
             "fuente_url": "https://cdn.www.gob.pe/uploads/document/file/5271559/4738029-d-s-071-2006-em.pdf",
             "confianza": "media"},
            {"texto": "Crear Sierra Exportadora",
             "estado": "cumplida (creación legal) — Ley 28890 publicada el 7-oct-2006",
             "nivel_cadena_valor": "actividad",
             "fuente_url": "https://sni.org.pe/ley-que-crea-sierra-exportadora-ley-n-28890/",
             "confianza": "media"},
            {"texto": "Aprobación del TLC con EE. UU. por el Congreso estadounidense",
             "estado": "pendiente a los 100 días (gestión en Washington; el Congreso de EE. UU. no lo había votado)",
             "nivel_cadena_valor": "producto",
             "fuente_url": FPIF, "confianza": "media"},
            {"texto": "Cerrar seis embajadas (austeridad en la Cancillería)",
             "estado": "anunciada (ago-2006); ejecución no verificada",
             "nivel_cadena_valor": "insumo", "fuente_url": FPIF, "confianza": "baja"},
            {"texto": "Pena de muerte para violadores asesinos de niños",
             "estado": "propuesta anunciada (72 % la aprobaba según Apoyo, ago-2006); no aprobada en la ventana (no verificado en el registro del Congreso)",
             "nivel_cadena_valor": "actividad", "fuente_url": IPSOS_AGO06, "confianza": "baja"},
            {"texto": "Reducir la pobreza de 48 % a 40 % en cinco años",
             "estado": "meta de mediano plazo; no evaluable a los 100 días",
             "nivel_cadena_valor": "impacto", "fuente_url": FPIF, "confianza": "media"},
        ],
        "aprobacion": [
            {"encuestadora": "Apoyo Opinión y Mercado", "campo": "2006-08-09/11", "ambito": "urbano, 16 ciudades (n=1,500)", "aprueba": 63, "desaprueba": 16, "fuente_url": IPSOS_AGO06, "confianza": "alta"},
            {"encuestadora": "Apoyo Opinión y Mercado", "campo": "2006-09", "ambito": "urbano nacional", "aprueba": 58, "desaprueba": 21, "nota": "leído de la tabla del informe de setiembre (columna del mes); fecha de campo exacta no extraída", "fuente_url": IPSOS_SET06, "confianza": "media"},
            {"encuestadora": "Apoyo Opinión y Mercado", "campo": "2006-10-11/13", "ambito": "urbano nacional (62 % Lima, 54 % provincias)", "aprueba": 57, "desaprueba": None, "fuente_url": IPSOS_OCT06, "confianza": "alta"},
            {"encuestadora": "Apoyo Opinión y Mercado", "campo": "2006-11-08/09", "ambito": "SOLO Lima (n=502); no comparable con las nacionales", "aprueba": 57, "desaprueba": 24, "fuente_url": IPSOS_NOV06, "confianza": "alta"},
        ],
        "gobernabilidad": {
            "premier_inicial": "Jorge del Castillo (desde 28-jul-2006)",
            "voto_confianza": {"fecha": "2006-08-24/25 (nota de La República del 25-ago)", "a_favor": 75, "en_contra": 18, "abstenciones": 23,
                                "fuente_url": "https://blogs.ubc.ca/peru/2006/08", "confianza": "baja (blog académico que reproduce a La República)"},
            "cambios_gabinete_100d": {"n": 0, "detalle": "No se identificaron cambios de ministros en la ventana (búsqueda no exhaustiva).", "confianza": "baja"},
            "facultades_delegadas_100d": {"otorgadas": False, "detalle": "No se identificó una ley autoritativa en la ventana; la delegación conocida sobre crimen organizado (Ley 29009) es de 2007.", "confianza": "baja"},
        },
        "macro": macro("garcia_2006"),
    },
    "humala_2011": {
        "presidente": "Ollanta Humala Tasso",
        "dia0": "2011-07-28", "dia100": "2011-11-05",
        "balance_promesas": {
            "total": None, "cumplidas": None, "en_proceso": None, "incumplidas": None,
            "metodologia": "NO SE ENCONTRÓ un verificador cuantitativo de promesas a los 100 días. Hubo balances periodísticos cualitativos (El Comercio, infografía 'altas y bajas'; La República, edición especial del 5-nov-2011; no leídos: enlaces de 2011 caídos) y la encuesta de Ipsos sobre áreas: lucha contra la pobreza 55 % aprueba / 39 % desaprueba; inversión y empleo 52/39; seguridad 48/47; corrupción 47/48; narcotráfico 43/45; conflictos sociales 38/50.",
            "fuente_url": IPSOS_NOV11,
            "confianza": "media",
        },
        "promesas_emblematicas": [
            {"texto": "Subir la remuneración mínima de S/ 600 a S/ 675 (primer tramo)",
             "estado": "cumplida — DS 011-2011-TR (14-ago-2011), vigente desde el 15-ago-2011",
             "nivel_cadena_valor": "producto", "fuente_url": "https://noticierocontable.com/?p=4802", "confianza": "media"},
            {"texto": "Gravamen / nuevo régimen tributario minero",
             "estado": "cumplida — 3 leyes (incl. Ley 29790, gravamen especial) publicadas el 28-sep-2011, vigentes desde el 1-oct-2011; DS 173-2011-EF reglamento. Fue un acuerdo con las mineras, no el impuesto a sobreganancias de campaña",
             "nivel_cadena_valor": "insumo", "fuente_url": "https://www.congreso.gob.pe/Docs/DGP/DIDP/files/ley_29790.pdf", "confianza": "media"},
            {"texto": "Ley de consulta previa a pueblos indígenas",
             "estado": "cumplida — promulgada en Bagua en sep-2011 (Ley 29785)",
             "nivel_cadena_valor": "actividad", "fuente_url": "https://as-coa.org/articles/perus-president-ollanta-humalas-first-hundred-days", "confianza": "media"},
            {"texto": "Pensión 65 (pensión no contributiva para mayores de 65 en pobreza extrema)",
             "estado": "cumplida en su creación; en proceso en cobertura — DS 081-2011-PCM (19-oct-2011), lanzamiento en Huancavelica (84 % aprobó el lanzamiento, Ipsos nov-2011)",
             "nivel_cadena_valor": "producto", "fuente_url": IPSOS_NOV11, "confianza": "media (fecha del DS de fuente secundaria)"},
            {"texto": "Crear el Ministerio de Desarrollo e Inclusión Social (MIDIS)",
             "estado": "cumplida — Ley 29792 (oct-2011); ministra Carolina Trivelli",
             "nivel_cadena_valor": "actividad", "fuente_url": "https://as-coa.org/articles/perus-president-ollanta-humalas-first-hundred-days", "confianza": "media"},
            {"texto": "Cuna Más (cuidado diurno de niños menores de 3 años)",
             "estado": "no creada en la ventana — se creó con el DS 003-2012-MIDIS (2012)",
             "nivel_cadena_valor": "producto", "fuente_url": "https://siteal.iiep.unesco.org/node/467", "confianza": "media (fecha exacta del DS no verificada)"},
            {"texto": "Beca 18",
             "estado": "anunciada en el mensaje del 28-jul (fue la 2.ª medida mejor valorada); estado a los 100 días no verificado",
             "nivel_cadena_valor": "producto", "fuente_url": IPSOS_AGO11, "confianza": "baja"},
        ],
        "aprobacion": [
            {"encuestadora": "Ipsos APOYO", "campo": "2011-08-10/12", "ambito": "urbano, 16 ciudades (n=1,200)", "aprueba": 55, "desaprueba": 20, "fuente_url": IPSOS_AGO11, "confianza": "alta"},
            {"encuestadora": "Ipsos APOYO", "campo": "2011-09", "ambito": "urbano nacional", "aprueba": 65, "desaprueba": 18, "nota": "serie histórica del informe de noviembre", "fuente_url": IPSOS_NOV11, "confianza": "alta"},
            {"encuestadora": "Ipsos APOYO", "campo": "2011-10", "ambito": "urbano nacional", "aprueba": 62, "desaprueba": 22, "fuente_url": IPSOS_NOV11, "confianza": "alta"},
            {"encuestadora": "Ipsos APOYO", "campo": "2011-11-16/18", "ambito": "urbano, 16 ciudades (n=1,200)", "aprueba": 56, "desaprueba": 34, "fuente_url": IPSOS_NOV11, "confianza": "alta"},
        ],
        "gobernabilidad": {
            "premier_inicial": "Salomón Lerner Ghitis (28-jul a 10-dic-2011)",
            "voto_confianza": {"fecha": "2011-08 (fines de agosto; día exacto no confirmado)", "a_favor": 90, "en_contra": 0, "abstenciones": 33,
                                "nota": "abstenciones de Fuerza 2011",
                                "fuente_url": "https://www.peruviantimes.com/26/congress-approves-humalas-first-cabinet-following-speech-by-lerner-ghitis/13500",
                                "confianza": "baja (fuente única; la página devolvió 403, cifra tomada del resumen del buscador)"},
            "cambios_gabinete_100d": {"n": 0, "detalle": "Sin cambios de ministros hasta la renuncia de Lerner el 10-dic-2011 (fuera de la ventana). Crisis dentro de la ventana: caso del 2.º vicepresidente Omar Chehade (no es ministro).",
                                       "fuente_url": "https://cooperativa.cl/ollanta-humala-acepto-renuncia-del-presidente-del-consejo-de-ministros/prontus_nots/2011-12-10/190824.html", "confianza": "media"},
            "facultades_delegadas_100d": {"otorgadas": False, "detalle": "No se identificó una ley autoritativa en la ventana.", "confianza": "baja"},
        },
        "macro": macro("humala_2011"),
    },
    "ppk_2016": {
        "presidente": "Pedro Pablo Kuczynski",
        "dia0": "2016-07-28", "dia100": "2016-11-05",
        "balance_promesas": {
            "total": 29, "cumplidas": 7, "en_proceso": None, "incumplidas": 5,
            "otras_categorias": {"cumplida_fuera_de_plazo": 1, "cumplida_parcialmente": 1, "cumplida_pero": 1, "enganosas": 6, "no_verificables": 4},
            "nota_suma": "Las categorías reportadas suman 25, no 29; la nota no explica las 4 restantes. Convoca no usa la categoría 'en proceso'.",
            "metodologia": "Verificador de Promesas de Convoca.pe: verificación de las promesas que el propio Ejecutivo anunció para sus primeros 100 días (no del plan de gobierno). 'Engañosa' = obra iniciada por el gobierno anterior o presentada como cumplida sin estarlo.",
            "fuente_url": CONVOCA,
            "fuente_primaria": "Convoca.pe (no se leyó el verificador original; dato vía América TV)",
            "confianza": "media (fecha de la nota no visible; según el buscador, enero de 2017)",
        },
        "promesas_emblematicas": [
            {"texto": "Obtener facultades legislativas delegadas", "estado": "cumplida parcialmente — Ley 30506: 90 días (de 120 pedidos) en reactivación económica y formalización, seguridad ciudadana, anticorrupción, agua y saneamiento y Petroperú",
             "nivel_cadena_valor": "insumo", "fuente_url": "https://comunicaciones.congreso.gob.pe/noticias/ley-30506-ley-que-delega-en-el-poder-ejecutivo-la-facultad-de-legislar-en-materia-de-reactivacion-economica-y-formalizacion-seguridad-ciudadana-lucha-contra-la-corrupcion-agua-y-saneamiento-y-reor", "confianza": "alta"},
            {"texto": "Rebajar el IGV en 1 punto (18 % a 17 %)", "estado": "pendiente a los 100 días (la norma aún no salía, 3-nov-2016); luego el DL 1347 (ene-2017) la condicionó a una meta de recaudación de 7.2 % del PBI",
             "nivel_cadena_valor": "insumo", "fuente_url": "https://www.contadoresyempresas.com.pe/los-primeros-cien-dias-de-ppk-en-materia-tributaria/", "confianza": "media"},
            {"texto": "Destrabe de proyectos de infraestructura", "estado": "en proceso — percepción Ipsos (9-11 nov): 4 % importante avance, 41 % moderado, 43 % ninguno, 6 % retroceso; sin cifra oficial de proyectos verificada",
             "nivel_cadena_valor": "actividad", "fuente_url": IPSOS_NOV16, "confianza": "media"},
            {"texto": "Quinto y último aumento salarial a más de 120 mil policías", "estado": "cumplida (Convoca)", "nivel_cadena_valor": "insumo", "fuente_url": CONVOCA, "confianza": "media"},
            {"texto": "Atención 24 h en cinco Centros Emergencia Mujer", "estado": "cumplida (Convoca)", "nivel_cadena_valor": "producto", "fuente_url": CONVOCA, "confianza": "media"},
            {"texto": "Declarar viables 10 plantas de tratamiento para el lago Titicaca", "estado": "incumplida (Convoca: postergada)", "nivel_cadena_valor": "actividad", "fuente_url": CONVOCA, "confianza": "media"},
            {"texto": "Cambiar la Ley de Reforma Magisterial para elevar el piso salarial docente", "estado": "incumplida (Convoca)", "nivel_cadena_valor": "insumo", "fuente_url": CONVOCA, "confianza": "media"},
            {"texto": "Atención desde las 6:00 en tres hospitales", "estado": "cumplida parcialmente (solo el Arzobispo Loayza)", "nivel_cadena_valor": "producto", "fuente_url": CONVOCA, "confianza": "media"},
        ],
        "aprobacion": [
            {"encuestadora": "Ipsos Perú", "campo": "2016-08", "ambito": "nacional urbano", "aprueba": 61, "desaprueba": 16, "nota": "serie histórica del informe de noviembre; fecha de campo exacta no extraída", "fuente_url": IPSOS_NOV16, "confianza": "alta"},
            {"encuestadora": "Ipsos Perú", "campo": "2016-09", "ambito": "nacional urbano", "aprueba": 63, "desaprueba": 17, "fuente_url": IPSOS_NOV16, "confianza": "alta"},
            {"encuestadora": "Ipsos Perú", "campo": "2016-10", "ambito": "nacional urbano", "aprueba": 55, "desaprueba": 27, "fuente_url": IPSOS_NOV16, "confianza": "alta"},
            {"encuestadora": "Ipsos Perú", "campo": "2016-11-09/11", "ambito": "nacional (n=1,260; urbano y rural)", "aprueba": 51, "desaprueba": 35, "fuente_url": IPSOS_NOV16, "confianza": "alta"},
        ],
        "gobernabilidad": {
            "premier_inicial": "Fernando Zavala Lombardi",
            "voto_confianza": {"fecha": "2016-08-19 (tras 21 h 40 min de debate)", "a_favor": 121, "en_contra": 2, "abstenciones": 1,
                                "nota": "RPP reporta 0 abstenciones", "fuente_url": "https://comunicaciones.congreso.gob.pe/?p=25253", "confianza": "alta"},
            "cambios_gabinete_100d": {"n": 0, "detalle": "No se identificaron cambios de ministros. Renunciaron el asesor presidencial de salud Carlos Moreno (2-oct-2016, audios) y el viceministro de Agricultura Juan Carlos Gonzáles (~28-oct-2016).",
                                       "fuente_url": "https://www.as-coa.org/articles/peru-update-ppks-first-100-days-president", "confianza": "media"},
            "facultades_delegadas_100d": {"otorgadas": True, "ley": "Ley 30506", "plazo_dias": 90, "plazo_pedido_dias": 120,
                                           "votacion": "plazo: 117-0-0; reactivación económica 99-17-1; seguridad y anticorrupción 117; agua 115-2; Petroperú 117 (prensa)",
                                           "fecha": "aprobada por el Pleno a fines de sep/inicios de oct-2016; nota del Congreso del 10-oct-2016",
                                           "fuente_url": "https://www.izquierdadiario.es/Congreso-peruano-otorga-facultades-legislativas-a-Kuczynski-durante-90-dias",
                                           "confianza": "media (votos de prensa; fecha exacta de publicación no verificada)"},
        },
        "macro": macro("ppk_2016"),
    },
    "toledo_2001_bonus": {
        "presidente": "Alejandro Toledo",
        "nota": "BONUS PARCIAL: solo macro. Promesas, aprobación y gobernabilidad no se investigaron. El índice de la BVL en nivel (PD38026MD) empieza en 2006 y la tasa de referencia (PD12301MD) en 2003-09: no existen para 2001.",
        "macro": macro("toledo_2001"),
    },
    "caveats": [
        "Código del tipo de cambio: PD04640PD es el 'TC Sistema bancario SBS - Venta', NO el interbancario. Se usó PD04638PD ('TC Interbancario (S/ por US$) - Venta'), verificado en el catálogo de BCRPData.",
        "Día 0 = último dato <= 28-jul (feriado; para el TC es el 27-jul; EMBIG/BVL/tasa de referencia sí traen dato el 28-jul en BCRPData). Día 100 = último dato hábil <= 5-nov (3-nov-2006, 4-nov-2011, 4-nov-2016, 5-nov-2001).",
        "EMBIG Perú (PD04709XD) está en puntos básicos; var_pct es la variación porcentual del spread, no la diferencia en pb.",
        "La tasa de referencia no cambió en ninguna ventana (4.50 % en 2006; 4.25 % en 2011 y 2016).",
        "Aprobación de nov-2006 (Apoyo) es SOLO Lima; las demás son urbano-nacionales. La de nov-2016 incluye zona rural. Las comparaciones entre gobiernos tienen distinto diseño muestral.",
        "Solo PPK tiene un balance cuantitativo de promesas (Convoca: 7 de 29), y se mide sobre las promesas de 100 días anunciadas por el propio Ejecutivo, no sobre el plan de gobierno. Para García y Humala no se encontró un verificador equivalente; no comparar con un % inventado.",
        "La clasificación en la cadena de valor público (insumo/actividad/producto/resultado/impacto) es una codificación propia de este análisis, no de las fuentes.",
        "No se consultaron Datum, IEP ni CPI para las ventanas históricas; toda la aprobación es de Apoyo/Ipsos (series comparables entre sí).",
        "Las cifras macro reflejan sobre todo el contexto internacional (p. ej. 2011: crisis de deuda europea; 2016: elección en EE. UU. el 8-nov, fuera de la ventana); no se atribuyen causalmente al gobierno.",
    ],
}

json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
print("escrito", os.path.abspath(OUT))
