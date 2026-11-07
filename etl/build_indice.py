"""Calcula research/indice100.json: Índice de los 100 Días + contexto internacional.

Usa solo los JSON de research/ (sin red). Uso: python3 etl/build_indice.py
Metodología: research/intl_marcos.json (propuesta_indice), con los ajustes documentados en METODO.
"""
import json, os, statistics

R = os.path.join(os.path.dirname(__file__), '..', 'research')
def load(n):
    p = os.path.join(R, n + '.json')
    return json.load(open(p)) if os.path.exists(p) else None

cas, kei, exp, idon, perf, msg, cum = (load(n) for n in ['castillo', 'keiko', 'expresidentes', 'idoneidad', 'performance', 'pp2050_mensaje', 'pp2050_cumplimiento'])
gob_i, soc_i = load('intl_gobernanza'), load('intl_social')

GOVS = {'castillo': 2021, 'keiko': 2026, 'ppk': 2016, 'humala': 2011, 'garcia': 2006}
HKEY = {'ppk': 'ppk_2016', 'humala': 'humala_2011', 'garcia': 'garcia_2006'}
IKEY = {'castillo': 'castillo_2021', 'keiko': 'keiko_2026', 'ppk': 'ppk_2016', 'humala': 'humala_2011', 'garcia': 'garcia_2006'}
clamp = lambda x: max(0.0, min(100.0, x))

DIMS = [
    {'id': 'D1', 'nombre': 'Promesas de 100 días', 'peso': 20, 'desc': 'Cumplidas = 1, en proceso o parciales = 0,5, el resto = 0 (estilo PolitiFact). Balance externo independiente.'},
    {'id': 'D2', 'nombre': 'Profundidad en la cadena de valor', 'peso': 10, 'desc': 'Nivel promedio de lo cumplido: insumo 0, actividad 25, producto 50, resultado 75, impacto 100.'},
    {'id': 'D3', 'nombre': 'Estabilidad e idoneidad del gabinete', 'peso': 15, 'desc': 'La mitad mide la permanencia de los ministros del día 1 (−10 por censura); la otra mitad, su experiencia y formación acordes al puesto.'},
    {'id': 'D4', 'nombre': 'Integridad', 'peso': 15, 'desc': 'Sin puntaje: las fuentes no son comparables entre gobiernos (ver nota). Se muestran los conteos crudos.'},
    {'id': 'D5', 'nombre': 'Veracidad del discurso oficial', 'peso': 10, 'desc': 'Afirmaciones con cifra del mensaje de los 100 días: coincide = 1, con matices = 0,5, no coincide = 0. Las no verificables se excluyen.'},
    {'id': 'D6', 'nombre': 'Confianza ciudadana (ajustada por luna de miel)', 'peso': 15, 'desc': 'Cambio en la aprobación Ipsos/Apoyo desde la primera medición hasta el ~día 100, frente a la caída esperada de −10 puntos. Puntaje = 50 + 2,5 × (Δ + 10).'},
    {'id': 'D7', 'nombre': 'Ejecución del gasto', 'peso': 15, 'desc': 'Ejecución del Gobierno Nacional a octubre frente al promedio de los cinco años: 50 + 50 × (ratio − 1) / 0,25.'},
]
LV = {'insumo': 0, 'actividad': 25, 'producto': 50, 'resultado': 75, 'impacto': 100}
def lvl(s):
    s = str(s or '').lower()
    for k, v in LV.items():
        if k in s: return v
    return None
done = lambda e: str(e or '').strip().lower().startswith('cumplid')

out = {k: {'dims': {}} for k in GOVS}
def put(k, d, score, valor, fuente=''):
    out[k]['dims'][d] = {'score': None if score is None else round(clamp(score), 1), 'valor': valor, 'fuente': fuente}

# D1 promesas
e = cas['ecdata']; put('castillo', 'D1', 100 * (e['cumplidas'] + .5 * e['en_proceso']) / e['total'], f"{e['cumplidas']} cumplidas y {e['en_proceso']} en proceso de {e['total']}", 'El Comercio – ECData')
kg = next(t for t in kei['trackers'] if 'Keiko Gobierna' in t['nombre'])
put('keiko', 'D1', 100 * (kg['cumplidas'] + .5 * kg['en_proceso']) / kg['total'], f"{kg['cumplidas']} cumplidas y {kg['en_proceso']} en proceso de {kg['total']}", 'Keiko Gobierna')
b = exp['ppk_2016']['balance_promesas']; o = b.get('otras_categorias', {})
parc = o.get('cumplida_fuera_de_plazo', 0) + o.get('cumplida_parcialmente', 0) + o.get('cumplida_pero', 0)
den = b['total'] - o.get('no_verificables', 0)
put('ppk', 'D1', 100 * (b['cumplidas'] + .5 * parc) / den, f"{b['cumplidas']} cumplidas y {parc} parciales de {den} verificables", 'Convoca (vía América TV)')
for k in ('humala', 'garcia'): put(k, 'D1', None, 'No existe un balance cuantitativo independiente')

# D2 cadena de valor de lo cumplido
def d2(k, arr, src):
    ls = [lvl(p.get('nivel_cadena_valor')) for p in arr if done(p.get('estado')) and lvl(p.get('nivel_cadena_valor')) is not None]
    put(k, 'D2', statistics.mean(ls) if ls else None, f"{len(ls)} promesas cumplidas clasificadas" if ls else 'Sin promesas cumplidas clasificadas', src)
d2('castillo', cas['promesas'], 'ECData + clasificación propia')
d2('keiko', kei['promesas'], 'Prensa + clasificación propia')
for k in HKEY: d2(k, exp[HKEY[k]]['promesas_emblematicas'], 'Promesas emblemáticas + clasificación propia')

# D3 estabilidad + idoneidad
SC = {'si': 1, 'parcial': .5, 'no': 0}
cens = {'castillo': 0, 'keiko': 0, 'ppk': 0, 'humala': 0, 'garcia': 0}
for k in GOVS:
    g = idon['gabinetes'][IKEY[k]] if IKEY[k] in idon['gabinetes'] else None
    if not g: put(k, 'D3', None, 'Sin datos'); continue
    ms = g['ministros']; n = len(ms); sal = sum(1 for m in ms if m.get('salio_100d'))
    est = 100 * (1 - sal / n) - 10 * cens[k]
    vals = [(SC[m['experiencia']] + SC[m['formacion']]) / 2 for m in ms if m.get('experiencia') in SC and m.get('formacion') in SC]
    ido = 100 * statistics.mean(vals) if vals else None
    sc = (est + ido) / 2 if ido is not None else est
    put(k, 'D3', sc, f"{n - sal} de {n} ministros del día 1 siguen en el cargo; idoneidad {round(ido) if ido is not None else '—'}/100", 'Prensa, gob.pe; codificación propia')

# D4 integridad: conteos crudos, sin puntaje
for k in GOVS:
    g = idon['gabinetes'].get(IKEY[k])
    n = sum(1 for m in g['ministros'] if m.get('investigacion_reportada') == 'si') if g else None
    put(k, 'D4', None, f"{n} ministros con investigación o proceso reportado (no comparable)" if n is not None else 'Sin datos', 'Ver nota de integridad')

# D5 veracidad (solo existe para el mensaje de Keiko)
v = msg['resumen']['veredictos']; nv = v['coincide'] + v['coincide_con_matices'] + v['no_coincide']
put('keiko', 'D5', 100 * (v['coincide'] + .5 * v['coincide_con_matices']) / nv, f"{v['coincide']} coinciden, {v['coincide_con_matices']} con matices y {v['no_coincide']} no coinciden (n = {nv})", 'Plan Perú 2050')
for k in ('castillo', 'ppk', 'humala', 'garcia'): put(k, 'D5', None, 'Sin verificación sistemática del mensaje de los 100 días')

# D6 aprobación ajustada (Ipsos/Apoyo, primera medición → la más cercana al día 100)
APR = {'castillo': (38, 35, 'ago → 12-nov-2021'), 'keiko': (57, 40, 'ago → oct-2026'), 'ppk': (61, 51, 'ago → nov-2016'),
       'humala': (55, 56, 'ago → nov-2011'), 'garcia': (63, 57, 'ago → oct-2006')}
for k, (a, z, per) in APR.items():
    put(k, 'D6', 50 + 2.5 * ((z - a) + 10), f"{a} % → {z} % ({per}); Δ {z - a:+d} pts frente a −10 esperado", 'Ipsos / Apoyo')

# D7 ejecución del gasto
T = perf['totales_gobierno_nacional']; pct = {k: T[str(y)]['ActProy']['pct'] for k, y in GOVS.items()}
avg = statistics.mean(pct.values())
for k in GOVS:
    put(k, 'D7', 50 + 50 * (pct[k] / avg - 1) / .25, f"{pct[k]} % ejecutado a octubre (promedio de los cinco años: {avg:.1f} %)", 'MEF – Consulta Amigable')

# agregación
W = {d['id']: d['peso'] for d in DIMS}
for k, g in out.items():
    have = [(d, c['score']) for d, c in g['dims'].items() if c['score'] is not None]
    wsum = sum(W[d] for d, _ in have)
    g['cobertura'] = round(wsum)
    g['n_dims'] = len(have)
    g['total'] = round(sum(W[d] * s for d, s in have) / wsum, 1) if wsum >= 70 else None
    g['total_pesos_iguales'] = round(statistics.mean(s for _, s in have), 1) if wsum >= 70 else None
    g['total_parcial'] = round(sum(W[d] * s for d, s in have) / wsum, 1) if wsum else None

# contexto internacional (selección curada; años según la regla de cada archivo)
def norm(v, lo, hi, best):
    if v is None or lo is None or hi is None or hi == lo: return None
    x = (v - lo) / (hi - lo) * 100
    return round(clamp(x if best == 'alto' else 100 - x), 1)
GOB_IDS = ['cpi_score', 'wgi_cc_sc', 'vdem_corr', 'vdem_libdem', 'eiu_democracy', 'fh_total', 'wgi_ge_sc', 'wgi_rl_sc', 'rsf_score']
SOC_IDS = ['gini', 'pobreza_monetaria', 'pobreza_extrema', 'idh', 'anemia_6_35m', 'desnutricion_cronica_5', 'lb_apoyo_democracia', 'lb_confianza_gobierno', 'victimizacion']
GKEY = {'castillo': 'castillo_2021', 'keiko': 'keiko_2026', 'ppk': 'ppk_2016', 'humala': 'humala_2011', 'garcia': 'garcia_2006'}
contexto = []
def scale_fix(iid, anio, v):
    if v is None: return None
    if iid == 'cpi_score' and anio is not None and int(anio) < 2012: return v * 10  # CPI 0-10 → 0-100
    return v
def g_get(o, *ks):
    for k in ks:
        if isinstance(o, dict) and isinstance(o.get(k), dict): return o[k]
    return None
def add_rows(items, ids, pg, pgkey, valkey, abs_scale):
    by = {i['id']: i for i in items}
    for iid in ids:
        it = by.get(iid)
        if not it: continue
        esc = it.get('escala') or {}
        best = esc.get('mejor') or it.get('mejor') or 'alto'
        serie = {int(k): v for k, v in (it.get('serie') or {}).items() if isinstance(v, (int, float))}
        if abs_scale and esc.get('min') is not None and esc.get('max') is not None:
            lo, hi = esc['min'], esc['max']; etxt = f"escala {lo}–{hi}; mejor = {best}"
        else:
            vals = [scale_fix(iid, y, v) for y, v in serie.items()]; lo, hi = min(vals), max(vals)
            etxt = f"{it.get('unidad', '')}; color relativo al rango del Perú {min(serie)}–{max(serie)} (mejor = {best})"
        row = {'id': iid, 'nombre': it['nombre'], 'dimension': it.get('dimension'), 'institucion': it.get('institucion') or it.get('fuente'),
               'fuente_url': it.get('fuente_url'), 'mejor': best, 'escala_txt': etxt, 'gobiernos': {}, 'advertencias': {}}
        for k, gk in GKEY.items():
            node = (pg.get(gk if pgkey == 'g' else k) or {}).get(valkey, {}).get(iid)
            if not node: continue
            r = g_get(node, 'recibio_anio', 'recibio', 'linea_base') or {}
            pr = g_get(node, 'primer_anio') or {}
            if k == 'keiko': pr = {}
            vr, vp = r.get('valor'), pr.get('valor')
            if not isinstance(vr, (int, float)) and not isinstance(vp, (int, float)): continue
            vr = vr if isinstance(vr, (int, float)) else None; vp = vp if isinstance(vp, (int, float)) else None
            row['gobiernos'][k] = {'anio_recibio': r.get('anio'), 'recibio': vr, 'anio_primer': pr.get('anio'), 'primer': vp,
                                   'score_recibio': norm(scale_fix(iid, r.get('anio'), vr), lo, hi, best),
                                   'score_primer': norm(scale_fix(iid, pr.get('anio'), vp), lo, hi, best)}
            if node.get('advertencias'): row['advertencias'][k] = node['advertencias']
        if row['gobiernos']: contexto.append(row)
if gob_i: add_rows(gob_i['indices'], GOB_IDS, gob_i['por_gobierno'], 'g', 'indices', True)
if soc_i: add_rows(soc_i['indicadores'], SOC_IDS, soc_i['por_gobierno'], 's', 'valores', False)

METODO = [
    'Índice propio, no oficial: no existe un estándar internacional para evaluar los 100 días (es una convención que nace con Roosevelt en 1933). Combinamos trackers de promesas (PolitiFact, Chequeado), gestión para resultados (BID PRODEV, CEPAL), estabilidad del gabinete (Martínez-Gallardo 2012) y aprobación con luna de miel (Mueller 1970; Carlin et al. 2018).',
    'Escala de 0 a 100 por dimensión. Semáforo: verde ≥70, amarillo 50-69, naranja 30-49, rojo <30.',
    'Si falta una dimensión, los pesos se reescalan entre las que tienen dato. No se publica la nota total si la cobertura es menor al 70 % del peso (OECD/JRC 2008); por eso García y Humala no tienen total.',
    'Integridad (D4) queda sin puntaje: en 2026 los conteos salen de las declaraciones juradas obligatorias (Ley 31227, que pueden incluir casos archivados); de 2006 a 2016, solo de la prensa. Compararlos castigaría la mayor transparencia. Ninguna investigación es una condena.',
    'Cadena de valor (D2): usamos (nivel − 1) / 4, de modo que un insumo vale 0 y no 25; es más exigente que la propuesta original.',
    'Ejecución (D7): de enero a julio el gasto corresponde al gobierno anterior, y el PIM de 2026 es el vigente, no el final. Se omitió el componente de indicadores mensuales por falta de historia comparable para 2006-2016.',
    'Aprobación (D6): la caída esperada de −10 puntos es un valor de trabajo. Un gobierno que empieza bajo (Castillo, 38 %) cae menos; por eso se informa también el nivel absoluto.',
    'Contexto internacional: los índices con escala fija (CPI, WGI, V-Dem, EIU, Freedom House, RSF) se colorean según su escala absoluta; los indicadores sociales (pobreza, Gini, IDH, anemia, encuestas), según el rango histórico del Perú entre 2005 y 2026. El CPI anterior a 2012 (escala 0-10) se multiplica por 10 para colorearlo. RSF cambió de metodología en 2022. Para Keiko solo hay línea base (el último dato publicado), no su primer año.',
    'Sensibilidad: con pesos iguales, el total cambia a {}.'.format(', '.join(f"{k} {out[k]['total_pesos_iguales']}" for k in GOVS if out[k]['total_pesos_iguales'] is not None)),
]
res = {'generado': '2026-11-07', 'dimensiones': DIMS, 'gobiernos': out, 'contexto': contexto, 'metodo': METODO}
json.dump(res, open(os.path.join(R, 'indice100.json'), 'w'), ensure_ascii=False, indent=1)
for k in GOVS:
    print(k, out[k]['total'], out[k]['cobertura'], {d: c['score'] for d, c in out[k]['dims'].items()})
print('contexto filas:', len(contexto))
