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
    {'id': 'D1', 'nombre': 'Promesas de 100 días', 'peso': 20, 'desc': 'Escala PolitiFact: cumplida = 1, en proceso = 0,3, el resto = 0. Ojo: cada gobierno tiene un tracker distinto (ECData, Keiko Gobierna, Convoca), con criterios diferentes.'},
    {'id': 'D2', 'nombre': 'Profundidad en la cadena de valor', 'peso': 10, 'desc': 'Solo las promesas cumplidas por completo, según su eslabón: insumo (normas, presupuesto) 0, actividad 25, producto 50, resultado 75, impacto 100. Hay muy pocos casos (3 a 7 por gobierno).'},
    {'id': 'D3', 'nombre': 'Estabilidad e idoneidad del gabinete', 'peso': 15, 'desc': 'La mitad mide la permanencia de los ministros del día 1; la otra mitad, su experiencia y formación acordes al puesto (codificación propia, sin revisión independiente).'},
    {'id': 'D4', 'nombre': 'Integridad (sin puntaje)', 'peso': 0, 'desc': 'Se muestran los conteos crudos, pero no entran al total: en 2026 vienen de declaraciones juradas obligatorias (Ley 31227) y en 2006-2021 solo de la prensa. Omitirla no es neutro (ver nota).'},
    {'id': 'D5', 'nombre': 'Veracidad del discurso (solo Keiko, no entra al total)', 'peso': 0, 'desc': 'Solo existe la verificación del mensaje de los 100 días de Keiko, así que no compara nada y queda fuera del total.'},
    {'id': 'D6', 'nombre': 'Confianza ciudadana', 'peso': 15, 'desc': 'Ipsos/Apoyo: primera medición frente a la última publicada ANTES del día 100 (la misma regla para todos), comparada con la caída esperada proporcional al nivel inicial (−10 × inicio / 55).'},
    {'id': 'D7', 'nombre': 'Ejecución de la inversión en la ventana', 'peso': 15, 'desc': 'Devengado de agosto a octubre en proyectos del Gobierno Nacional / PIM, frente al promedio de los cinco años. El PIM de 2026 aún es el vigente, lo que lo favorece levemente.'},
]
LV = {'insumo': 0, 'actividad': 25, 'producto': 50, 'resultado': 75, 'impacto': 100}
def lvl(s):
    s = str(s or '').lower()
    for k, v in LV.items():
        if k in s: return v
    return None
def done(e):
    e = str(e or '').strip().lower()
    return e.startswith('cumplid') and 'parcial' not in e

out = {k: {'dims': {}} for k in GOVS}
def put(k, d, score, valor, fuente='', corto=None):
    out[k]['dims'][d] = {'score': None if score is None else round(clamp(score), 1), 'valor': valor, 'fuente': fuente, 'corto': corto}

# D1 promesas (escala PolitiFact: en proceso = 0,3)
EP = 0.3
e = cas['ecdata']; put('castillo', 'D1', 100 * (e['cumplidas'] + EP * e['en_proceso']) / e['total'], f"{e['cumplidas']} cumplidas y {e['en_proceso']} en proceso de {e['total']}", 'El Comercio – ECData (plan + discurso, criterio periodístico)')
kg = next(t for t in kei['trackers'] if 'Keiko Gobierna' in t['nombre'])
put('keiko', 'D1', 100 * (kg['cumplidas'] + EP * kg['en_proceso']) / kg['total'], f"{kg['cumplidas']} cumplidas y {kg['en_proceso']} en proceso de {kg['total']}", 'Keiko Gobierna (solo normas en El Peruano)')
b = exp['ppk_2016']['balance_promesas']; o = b.get('otras_categorias', {})
parc = o.get('cumplida_fuera_de_plazo', 0) + o.get('cumplida_parcialmente', 0) + o.get('cumplida_pero', 0)
den = b['total'] - o.get('no_verificables', 0)
put('ppk', 'D1', 100 * (b['cumplidas'] + EP * parc) / den, f"{b['cumplidas']} cumplidas y {parc} parciales de {den} verificables", 'Convoca (metas anunciadas por el Ejecutivo; medido meses después)')
for k in ('humala', 'garcia'): put(k, 'D1', None, 'No existe un balance cuantitativo independiente', corto='sin balance')

# D2 cadena de valor (solo cumplidas por completo)
def d2(k, arr, src):
    ls = [lvl(p.get('nivel_cadena_valor')) for p in arr if done(p.get('estado')) and lvl(p.get('nivel_cadena_valor')) is not None]
    put(k, 'D2', statistics.mean(ls) if ls else None, f"{len(ls)} promesas cumplidas por completo, clasificadas" if ls else 'Sin promesas cumplidas por completo', src)
d2('castillo', cas['promesas'], 'ECData + clasificación propia')
d2('keiko', kei['promesas'], 'Prensa + clasificación propia (incluye medidas fuera de la lista de 100 días)')
for k in HKEY: d2(k, exp[HKEY[k]]['promesas_emblematicas'], 'Promesas emblemáticas + clasificación propia')

# D3 estabilidad + idoneidad
SC = {'si': 1, 'parcial': .5, 'no': 0}
for k in GOVS:
    g = idon['gabinetes'].get(IKEY[k])
    if not g: put(k, 'D3', None, 'Sin datos'); continue
    ms = g['ministros']; n = len(ms); sal = sum(1 for m in ms if m.get('salio_100d'))
    est = 100 * (1 - sal / n)
    vals = [(SC[m['experiencia']] + SC[m['formacion']]) / 2 for m in ms if m.get('experiencia') in SC and m.get('formacion') in SC]
    ido = 100 * statistics.mean(vals) if vals else None
    put(k, 'D3', (est + ido) / 2 if ido is not None else est, f"{n - sal} de {n} ministros del día 1 siguen en el cargo; idoneidad {round(ido) if ido is not None else '—'}/100", 'Prensa, gob.pe; codificación propia')

# D4 integridad: conteos crudos
for k in GOVS:
    g = idon['gabinetes'].get(IKEY[k])
    n = sum(1 for m in g['ministros'] if m.get('investigacion_reportada') == 'si') if g else None
    src = 'declaraciones juradas' if k == 'keiko' else 'prensa'
    put(k, 'D4', None, f"{n} ministros con investigación o proceso reportado ({src}; no comparable)", 'Ver nota de integridad', corto=f"{n} ({src})" if n is not None else 'sin datos')

# D5 veracidad: solo informativo
v = msg['resumen']['veredictos']; nv = v['coincide'] + v['coincide_con_matices'] + v['no_coincide']
for k in GOVS:
    if k == 'keiko': put(k, 'D5', None, f"{v['coincide']} coinciden, {v['coincide_con_matices']} con matices y {v['no_coincide']} no coinciden (n = {nv})", 'Plan Perú 2050', corto=f"{v['coincide']}/{v['coincide_con_matices']}/{v['no_coincide']} de {nv}")
    else: put(k, 'D5', None, 'Sin verificación sistemática del mensaje de los 100 días', corto='no medido')

# D6 aprobación: misma regla (última medición Ipsos/Apoyo antes del día 100) y caída esperada proporcional
APR = {'castillo': (38, 42, 'ago → 15-oct-2021'), 'keiko': (57, 40, 'ago → 7/8-oct-2026'), 'ppk': (61, 55, 'ago → oct-2016'),
       'humala': (55, 62, 'ago → oct-2011'), 'garcia': (63, 57, 'ago → 11/13-oct-2006')}
def d6(a, z, mode='prop'):
    if mode == 'nivel': return z / 0.6  # 60 % de aprobación = 100
    return 50 + 2.5 * ((z - a) - (-10 * a / 55))
for k, (a, z, per) in APR.items():
    put(k, 'D6', d6(a, z), f"{a} % → {z} % ({per}); Δ {z - a:+d} pts frente a {-10 * a / 55:.1f} esperado", 'Ipsos / Apoyo')

# D7 inversión agosto-octubre (Gobierno Nacional, proyectos)
P = perf['ejecucion_sectorial_proyectos']
inv = {k: 100 * sum(x['devengado_ago_oct'] for x in P[str(y)]) / sum(x['pim'] for x in P[str(y)]) for k, y in GOVS.items()}
avg = statistics.mean(inv.values())
T = perf['totales_gobierno_nacional']; act = {k: T[str(y)]['ActProy']['pct'] for k, y in GOVS.items()}; avg_act = statistics.mean(act.values())
def d7(k, mode='inv'):
    r = inv[k] / avg if mode == 'inv' else act[k] / avg_act
    return 50 + 50 * (r - 1) / .25
for k in GOVS:
    put(k, 'D7', d7(k), f"{inv[k]:.1f} % del PIM de inversión devengado en ago-oct (promedio de los cinco años: {avg:.1f} %)", 'MEF – Consulta Amigable')

# agregación: el total exige el núcleo D1, D2, D3, D6 y D7; el «núcleo común» (D3, D6, D7) existe para los cinco
W = {d['id']: d['peso'] for d in DIMS}
CORE = ['D1', 'D2', 'D3', 'D6', 'D7']; COMMON = ['D3', 'D6', 'D7']
def total(k, w=W, dims=CORE, scores=None):
    sc = scores or {d: out[k]['dims'][d]['score'] for d in dims}
    if any(sc[d] is None for d in dims): return None
    return sum(w[d] * sc[d] for d in dims) / sum(w[d] for d in dims)
for k, g in out.items():
    g['total'] = None if total(k) is None else round(total(k), 1)
    g['total_comun'] = round(total(k, dims=COMMON), 1)
    g['cobertura'] = round(100 * sum(W[d] for d in CORE if g['dims'][d]['score'] is not None) / sum(W[d] for d in CORE))
    g['n_dims'] = sum(1 for d in CORE if g['dims'][d]['score'] is not None)

# sensibilidad Monte Carlo: pesos Dirichlet(1) y fórmulas alternativas de D6 y D7
import random
random.seed(42)
N = 20000; sims = {k: [] for k in ('castillo', 'keiko', 'ppk')}; cgk = 0; ppk_top = 0
for _ in range(N):
    ws = [random.gammavariate(1, 1) for _ in CORE]; w = dict(zip(CORE, ws))
    m6 = random.choice(['prop', 'nivel']); m7 = random.choice(['inv', 'act'])
    t = {}
    for k in sims:
        sc = {d: out[k]['dims'][d]['score'] for d in CORE}
        a, z, _ = APR[k]; sc['D6'] = clamp(d6(a, z, m6)); sc['D7'] = clamp(d7(k, m7))
        t[k] = total(k, w, CORE, sc); sims[k].append(t[k])
    cgk += t['castillo'] > t['keiko']; ppk_top += t['ppk'] > max(t['castillo'], t['keiko'])
pct = lambda xs, q: sorted(xs)[int(q * (len(xs) - 1))]
sens = {k: {'p5': round(pct(v, .05), 1), 'p50': round(pct(v, .5), 1), 'p95': round(pct(v, .95), 1)} for k, v in sims.items()}
sens['p_castillo_mayor_keiko'] = round(cgk / N, 2); sens['p_ppk_primero'] = round(ppk_top / N, 2)
sens['nota'] = 'N = 20 000 simulaciones: pesos aleatorios Dirichlet(1) para D1, D2, D3, D6 y D7; D6 con caída proporcional o por nivel absoluto; D7 con inversión de ago-oct o gasto total de ene-oct. La revisión metodológica externa (review/02) obtuvo un rango similar con 35 variantes.'
for k in sims: out[k]['rango'] = sens[k]

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
    'Índice propio y experimental: no existe un estándar internacional para evaluar los 100 días (es una convención que nace con Roosevelt en 1933). Combinamos trackers de promesas (PolitiFact, Chequeado), gestión para resultados (BID PRODEV, CEPAL), estabilidad del gabinete (Martínez-Gallardo 2012) y aprobación con luna de miel (Mueller 1970; Carlin et al. 2018).',
    'Escala de 0 a 100 por dimensión. Semáforo: verde ≥70, amarillo 50-69, naranja 30-49, rojo <30.',
    'El total solo se calcula si hay dato en las cinco dimensiones del núcleo (promesas, cadena de valor, gabinete, confianza e inversión). García y Humala no tienen balance de promesas, así que solo tienen el «núcleo común» (gabinete, confianza e inversión), que sí existe para los cinco.',
    'Incertidumbre: el total depende mucho de los pesos y de las fórmulas. Publicamos el rango del 5 % al 95 % de 20 000 simulaciones; si los rangos de dos gobiernos se superponen, no se pueden distinguir. Castillo supera a Keiko en el {:.0%} de las simulaciones; PPK queda primero en el {:.0%}.'.format(sens['p_castillo_mayor_keiko'], sens['p_ppk_primero']),
    'Integridad (D4) no entra al total: en 2026 los conteos salen de declaraciones juradas obligatorias (Ley 31227, que pueden incluir casos archivados); de 2006 a 2021, solo de la prensa. Omitirla no es neutro: con una medida simple de ministros investigados, Keiko bajaría unos 3 puntos y Castillo subiría unos 5 (review/02). Ninguna investigación es una condena.',
    'Promesas (D1): los tres trackers no son homogéneos. ECData (Castillo) usó un criterio periodístico sobre el plan y el discurso; Keiko Gobierna solo cuenta normas publicadas en El Peruano; Convoca (PPK) midió metas anunciadas por el Ejecutivo, meses después del día 100.',
    'Confianza (D6): se usa la última medición Ipsos/Apoyo publicada antes del día 100, con la misma regla para todos (Castillo 42 % el 15-oct-2021; Keiko 40 % el 7/8-oct-2026). Quien empieza más alto suele caer más, así que la caída esperada es proporcional al nivel inicial.',
    'Inversión (D7): solo cuenta agosto-octubre, que es la gestión propia. El PIM de 2026 es el vigente (todavía puede crecer), lo que la favorece levemente.',
    'Cadena de valor (D2) e idoneidad (D3): son codificaciones propias, sin un segundo codificador independiente. Reclasificar una sola promesa de D2 puede mover el total en más de un punto.',
    'Contexto internacional: describe el país que recibió cada gobierno, no evalúa su gestión. Los índices con escala fija (CPI, WGI, V-Dem, EIU, Freedom House, RSF) se colorean por su escala; los sociales, por el rango histórico del Perú entre 2005 y 2026, así que un verde en pobreza solo significa «menor que en 2006». El CPI anterior a 2012 (escala 0-10) se multiplica por 10; RSF cambió de metodología en 2022.',
]
res = {'generado': '2026-11-07', 'version': 2, 'sensibilidad': sens, 'dimensiones': DIMS, 'gobiernos': out, 'contexto': contexto, 'metodo': METODO}
json.dump(res, open(os.path.join(R, 'indice100.json'), 'w'), ensure_ascii=False, indent=1)
for k in GOVS:
    print(k, out[k]['total'], out[k]['total_comun'], out[k].get('rango'), {d: c['score'] for d, c in out[k]['dims'].items()})
print(sens)
print('contexto filas:', len(contexto))
