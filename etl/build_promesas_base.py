"""Base unificada de promesas de los cinco gobiernos → research/promesas_base.json.

Fuentes (todas ya en research/):
- Castillo 2021: castillo.json (las promesas identificadas del balance ECData; El Comercio no publicó la lista completa de 43).
- Keiko 2026: pp2050_cumplimiento.json (las 67 acciones de «Primeros 100 días» del plan, con el estado de Keiko Gobierna y
  una verificación propia en El Peruano) + keiko.json (medidas reportadas por la prensa, fuera de esa lista).
- PPK, Humala y García: expresidentes.json (promesas emblemáticas de los 100 días).
Estados normalizados: cumplida | parcial | en_proceso | anunciada | sin_evidencia | incumplida | no_verificable.
"""
import json, os
R = os.path.join(os.path.dirname(__file__), '..', 'research')
ld = lambda n: json.load(open(os.path.join(R, n + '.json')))

def norm_estado(e):
    e = str(e or '').lower()
    if 'parcial' in e or 'en parte' in e: return 'parcial'
    if e.startswith('cumplid') or e.startswith('cumple'): return 'cumplida'
    if 'proceso' in e or 'progreso' in e or 'pendiente' in e: return 'en_proceso'
    if 'anunci' in e or 'autodeclar' in e: return 'anunciada'
    if 'incumplid' in e or 'no cumplid' in e: return 'incumplida'
    if 'sin_evidencia' in e or 'sin avance' in e or 'sin evidencia' in e: return 'sin_evidencia'
    return 'no_verificable'

def nivel(s):
    s = str(s or '').lower()
    for k in ('insumo', 'actividad', 'producto', 'resultado', 'impacto'):
        if k in s: return k
    return None

rows = []
cas = ld('castillo')
for p in cas['promesas']:
    rows.append({'gobierno': 'castillo', 'lista': 'ECData: promesas identificadas (plan de 2.ª vuelta y discurso del 28-jul)',
                 'texto': p['texto'], 'estado': norm_estado(p['estado']), 'estado_fuente': p['estado'],
                 'nivel': nivel(p.get('nivel_cadena_valor')), 'nota': p.get('nota', ''), 'fuentes': [p['fuente_url']] if p.get('fuente_url') else []})

cum = ld('pp2050_cumplimiento')
for a in cum['cien_dias']['acciones']:
    ev = a.get('evidencias') or []
    v = a['estado_verificado']
    est = {'con_norma': 'en_proceso', 'anunciado': 'anunciada', 'sin_evidencia': 'sin_evidencia'}.get(v, norm_estado(v))
    rows.append({'gobierno': 'keiko', 'lista': 'Plan «Perú con Orden»: 67 acciones de los primeros 100 días',
                 'codigo': a.get('codigo'), 'eje': f"{a.get('pilar', '')} · {a.get('tema', '')}", 'texto': a['texto'],
                 'estado': est, 'estado_fuente': f"Keiko Gobierna: {a['estado_keikogobierna']} · verificación en El Peruano: {v.replace('_', ' ')}",
                 'nivel': 'insumo' if v == 'con_norma' else None, 'nota': a.get('nota', ''),
                 'fuentes': [e['url'] for e in ev if e.get('url')] + ['https://www.keikogobierna.com/primeros-100-dias/']})
kei = ld('keiko')
for p in kei['promesas']:
    rows.append({'gobierno': 'keiko', 'lista': 'Medidas reportadas por la prensa (incluye anuncios fuera de la lista de 100 días)',
                 'texto': p['texto'], 'estado': norm_estado(p['estado']), 'estado_fuente': p['estado'],
                 'nivel': nivel(p.get('nivel_cadena_valor')), 'nota': p.get('nota', ''), 'fuentes': [p['fuente_url']] if p.get('fuente_url') else []})

exp = ld('expresidentes')
for g, k in (('ppk', 'ppk_2016'), ('humala', 'humala_2011'), ('garcia', 'garcia_2006')):
    for p in exp[k]['promesas_emblematicas']:
        rows.append({'gobierno': g, 'lista': 'Promesas emblemáticas de los 100 días', 'texto': p['texto'],
                     'estado': norm_estado(p['estado']), 'estado_fuente': p['estado'], 'nivel': nivel(p.get('nivel_cadena_valor')),
                     'nota': p.get('nota', ''), 'fuentes': [p['fuente_url']] if p.get('fuente_url') else []})

for i, r in enumerate(rows): r['id'] = f"{r['gobierno']}-{i + 1:03d}"
resumen = {}
for r in rows:
    resumen.setdefault(r['gobierno'], {}).setdefault(r['estado'], 0); resumen[r['gobierno']][r['estado']] += 1
out = {'generado': '2026-11-07', 'n': len(rows), 'resumen': resumen, 'promesas': rows,
       'balances_oficiales': {
           'castillo': {'fuente': 'El Comercio – ECData', 'total': 43, 'cumplidas': 3, 'en_proceso': 4, 'incumplidas': 36,
                        'nota': 'El Comercio no publicó la lista completa de las 43; aquí están las que se pudieron identificar.'},
           'keiko': {'fuente': 'Keiko Gobierna', 'total': 67, 'cumplidas': 0, 'en_proceso': 3, 'sin_avance': 64,
                     'nota': 'Las 67 acciones están completas. La verificación propia en El Peruano encuentra 5 con alguna norma, 2 solo anunciadas y 60 sin evidencia.'},
           'ppk': {'fuente': 'Convoca', 'total': 29, 'cumplidas': 7, 'nota': 'Solo se muestran las emblemáticas; la lista completa de Convoca no fue accesible.'}},
       'estados': {'cumplida': 'Cumplida', 'parcial': 'Cumplida en parte', 'en_proceso': 'En proceso / con norma parcial',
                   'anunciada': 'Solo anunciada', 'sin_evidencia': 'Sin evidencia', 'incumplida': 'Incumplida', 'no_verificable': 'No verificable'},
       'caveats': ['Las listas no son homogéneas: cada gobierno tiene un tracker distinto con criterios diferentes.',
                   'El estado «en proceso» de las acciones de Keiko con norma significa que existe al menos una norma relacionada; no que la acción esté cumplida.',
                   'La clasificación en la cadena de valor (insumo → impacto) es una codificación propia.']}
json.dump(out, open(os.path.join(R, 'promesas_base.json'), 'w'), ensure_ascii=False, indent=1)
print(out['n'], json.dumps(resumen, ensure_ascii=False))
