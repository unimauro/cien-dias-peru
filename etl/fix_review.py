"""Correcciones de la revisión adversarial (review/01-05, 7-nov-2026).

- Día 100 = 4-nov (si el 28-jul es el día 1): recalcula d100 y var_pct de las series de mercado.
- Homicidios SINADEF con ventana de 100 días (28-jul a 4-nov): 377 y 579 (review/01_cifras.md).
- Rotación del gabinete de Castillo en performance.json: 6 reemplazos el 6-oct y 9 cambios en total.
- Promesas de Keiko: el salario mínimo cumplido en parte; se elimina el dato de Datum sin fuente.
Es idempotente.
"""
import json, os
R = os.path.join(os.path.dirname(__file__), '..', 'research')
ld = lambda n: json.load(open(os.path.join(R, n + '.json')))
sv = lambda n, d: json.dump(d, open(os.path.join(R, n + '.json'), 'w'), ensure_ascii=False, indent=1)

def d100(serie, year):
    lim = f'{year}-11-04'
    pts = [(f, v) for f, v in serie if f <= lim and v is not None]
    return pts[-1] if pts else (None, None)

ind = ld('indicadores')
for s in ind['series']:
    if s.get('frecuencia') != 'diaria': continue
    for vk, y in (('v1', 2021), ('v2', 2026)):
        v = s.get(vk) or {}
        if not v.get('serie') or not isinstance(v.get('d0'), dict): continue
        f, val = d100(v['serie'], y)
        if f and f < f'{y}-10-25':  # la serie termina antes: no hay dato del día 100
            v['d100'] = {'fecha': None, 'valor': None, 'nota': f'no disponible: la serie diaria termina el {f} en BCRPData'}
            v['var_pct'] = None
            continue
        if f and v['d0'].get('valor'):
            v['d100'] = {'fecha': f, 'valor': val}
            if v.get('var_pct') is not None or s['id'] in ('tc_interbancario_venta', 'bvl_indice_general', 'control_cobre_lme', 'embig_peru', 'control_embig_latam'):
                v['var_pct'] = round((val / v['d0']['valor'] - 1) * 100, 2)
_cv = ('Revisión del 7-nov: el día 100 se fijó en el 4-nov (el 28-jul es el día 1); los valores d100 se recalcularon sobre el último dato hábil hasta el 4-nov.')
ind['caveats'] = [c for c in ind.get('caveats', []) if not c.startswith('Revisión del 7-nov')] + [_cv]
sv('indicadores', ind)

exp = ld('expresidentes')
for k, y in (('garcia_2006', 2006), ('humala_2011', 2011), ('ppk_2016', 2016)):
    for m in exp[k]['macro']:
        f, val = d100(m['serie'], y)
        if f and m.get('d0'):
            m['d100'], m['d100_fecha'] = val, f
            m['var_pct'] = round((val / m['d0'] - 1) * 100, 2)
sv('expresidentes', exp)

res = ld('resultados')
for i in res['indicadores']:
    if i['id'] == 'homicidios_sinadef':
        i['2021']['durante'] = {'periodo': '2021-07-28 a 2021-11-04 (100 días de gobierno)', 'valor': 377}
        i['2026']['durante'] = {'periodo': '2026-07-28 a 2026-11-04 (100 días de gobierno)', 'valor': 579}
        i['rezago_nota'] = ('Ventanas de 100 días (corregidas el 7-nov): 2021 +1,9 % y 2026 +3,4 % frente a los 100 días previos; ambas variaciones están dentro del ruido mensual. '
                            'El dato de 2026 es provisional (el SINADEF registra con semanas de rezago).')
res['conclusion_neutral'] = res['conclusion_neutral'].replace('380', '377').replace('584', '579')
sv('resultados', res)

perf = ld('performance')
for r in perf.get('rotacion', []):
    if r.get('anio') == 2021 and '6-oct' in r.get('indicador', ''):
        r['valor'] = 6
        r['detalle'] = 'Cultura, Trabajo, Interior, Producción, Energía y Minas y Educación (Juan Cadillo → Carlos Gallardo), además de la presidencia del Consejo de Ministros.'
    if r.get('anio') == 2021 and 'Total' in r.get('indicador', ''):
        r['valor'] = 9
        r['detalle'] = 'Béjar (17-ago), 7 salidas el 6-oct (incluido el premier Bellido) y Barranzuela, que renunció el 2-nov-2021 (Guillén juró el 4-nov), dentro de la ventana. Fuentes: Andina, Forbes y Bloomberg Línea.'
sv('performance', perf)

kei = ld('keiko')
for p in kei['promesas']:
    if 'Remuneración Mínima' in p['texto'] and p['estado'] == 'cumplida':
        p['estado'] = 'cumplida parcialmente (primer tramo: S/1,230 de S/1,300)'
kei['aprobacion'] = [a for a in kei['aprobacion'] if not (str(a.get('encuestadora', '')).startswith('Datum') and not a.get('fuente_url'))]
sv('keiko', kei)
print('ok')
