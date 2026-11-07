/* 100 días bajo la lupa — render desde research/*.json */
(() => {
'use strict';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl = u => { try { const p = new URL(u); return (p.protocol === 'http:' || p.protocol === 'https:') ? p.href : '#'; } catch { return '#'; } };
const $ = s => document.querySelector(s);
const isNum = v => typeof v === 'number' && isFinite(v);
const fmt = (v, d = 1) => isNum(v) ? v.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d }) : '—';
const fmtInt = v => isNum(v) ? Math.round(v).toLocaleString('es-PE') : (v ?? '—');
const host = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return 'fuente'; } };
const link = (u, label) => u && /^https?:/.test(u) ? `<a href="${esc(safeUrl(u))}" target="_blank" rel="noopener">${esc(label || host(u))}</a>` : '';
const cssVar = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

/* gobiernos: color fijo por entidad, orden fijo */
const GOV = {
  castillo: { name: 'Pedro Castillo', short: 'Castillo', year: 2021, v: '--castillo' },
  keiko:    { name: 'Keiko Fujimori', short: 'Keiko', year: 2026, v: '--keiko' },
  ppk:      { name: 'Pedro Pablo Kuczynski', short: 'PPK', year: 2016, v: '--ppk' },
  humala:   { name: 'Ollanta Humala', short: 'Humala', year: 2011, v: '--humala' },
  garcia:   { name: 'Alan García', short: 'García', year: 2006, v: '--garcia' },
};
const ORDER = ['castillo', 'keiko', 'ppk', 'humala', 'garcia'];
const sw = k => `<span class="swatch" style="background:var(${GOV[k].v})"></span>`;
const govLabel = k => `${sw(k)}${esc(GOV[k].short)} ${GOV[k].year}`;

/* tooltip compartido */
const tip = $('#tip');
document.addEventListener('mousemove', e => {
  const t = e.target.closest('[data-tip]');
  if (!t) { tip.classList.remove('on'); return; }
  tip.textContent = t.dataset.tip;
  tip.classList.add('on');
  const x = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8);
  const y = e.clientY + 16 + tip.offsetHeight > innerHeight ? e.clientY - tip.offsetHeight - 10 : e.clientY + 16;
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
});

/* tema */
$('#themeBtn').addEventListener('click', () => {
  const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('theme', next); } catch {}
  charts.forEach(c => restyle(c)); charts.forEach(c => c.update('none'));
  renderApproval();
});

/* nav activa */
const navLinks = [...document.querySelectorAll('.nav a')];
const io = new IntersectionObserver(es => es.forEach(en => {
  if (en.isIntersecting) navLinks.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id));
}), { rootMargin: '-40% 0px -55% 0px' });
document.querySelectorAll('section.block').forEach(s => io.observe(s));

/* veredictos */
function verdictClass(v) {
  const s = String(v || '').toLowerCase();
  if (/^falso/.test(s)) return 'v-bad';
  if (/^verdadero$|^cierto$|^verdadero\b(?!.*engañ)/.test(s)) return 'v-ok';
  if (/engañ|parcial|exager|impreciso|prematur|matiz|insuficiente/.test(s)) return 'v-warn';
  if (/verdadero/.test(s)) return 'v-warn';
  return 'v-unk';
}
const ICON = { 'v-ok': '✓', 'v-warn': '!', 'v-bad': '✕', 'v-unk': '?' };
const stamp = (v, label) => { const c = verdictClass(v); return `<span class="stamp ${c}"><span class="ic" aria-hidden="true">${ICON[c]}</span>${esc(label || v)}</span>`; };
const cap = s => { s = String(s || ''); return s.charAt(0).toUpperCase() + s.slice(1); };

const D = {};
const FILES = ['indice100', 'pp2050_mensaje', 'pp2050_cumplimiento', 'factcheck', 'castillo', 'keiko', 'indicadores', 'performance', 'noticias', 'videos', 'planes', 'expresidentes', 'resultados'];

Promise.all(FILES.map(f => fetch(`research/${f}.json`, { cache: 'no-cache' }).then(r => r.ok ? r.json() : null).catch(() => null)))
  .then(arr => {
    FILES.forEach((f, i) => D[f] = arr[i]);
    const run = (name, fn) => { try { fn(); } catch (e) { console.error(name, e); } };
    run('vs', renderVs); run('claims', renderClaims); run('promesas', renderPromises); run('ladder', renderLadder);
    run('resultados', renderResults); run('gov', renderGov); run('approval', renderApproval); run('eco', renderEco);
    run('estado', renderEstado); run('planes', renderPlanes); run('timeline', renderTimeline); run('videos', renderVideos);
    run('method', renderMethod); run('mensaje', renderMensaje); run('brujula', renderBrujula); run('semaforo', renderSemaforo);
  });

/* ---------- helpers de datos ---------- */
const hist = k => ({ ppk: D.expresidentes?.ppk_2016, humala: D.expresidentes?.humala_2011, garcia: D.expresidentes?.garcia_2006 })[k];

function promiseBalance(k) {
  if (k === 'castillo') {
    const e = D.castillo?.ecdata || {};
    const fc = D.factcheck?.infografia_b?.verificacion_castillo || {};
    const t = e.total ?? 43, c = e.cumplidas ?? 3, p = e.en_proceso ?? 4, n = e.incumplidas ?? 36;
    return { total: t, c, p, n, u: 0, src: 'El Comercio – ECData, nov-2021', url: e.fuente_url || fc.fuente_url, met: e.metodologia || 'Promesas del plan y anuncios evaluadas por la Unidad de Datos de El Comercio.' };
  }
  if (k === 'keiko') {
    const kg = (D.keiko?.trackers || []).find(t => /keiko gobierna/i.test(t.nombre || '')) || (D.keiko?.trackers || []).find(t => isNum(t.total) && isNum(t.cumplidas));
    if (!kg) return null;
    const c = kg.cumplidas || 0, p = kg.en_proceso || 0, n = (kg.incumplidas || 0) + (kg.sin_avance || 0);
    return { total: kg.total, c, p, n, u: Math.max(0, kg.total - c - p - n), src: 'Keiko Gobierna (tracker ciudadano)', url: kg.url, met: kg.metodologia, nLabel: 'Sin avance (sin norma que lo acredite)' };
  }
  const b = hist(k)?.balance_promesas;
  if (b && isNum(b.total)) {
    const c = b.cumplidas || 0, n = b.incumplidas || 0, p = b.en_proceso || 0;
    return { total: b.total, c, p, n, u: Math.max(0, b.total - c - n - p), src: 'Convoca.pe (vía América TV)', url: b.fuente_url, met: b.metodologia, nota: b.nota_suma };
  }
  return null;
}

function approvals(k) {
  let arr = [];
  if (k === 'castillo') arr = D.castillo?.aprobacion || [];
  else if (k === 'keiko') arr = D.keiko?.aprobacion || [];
  else arr = hist(k)?.aprobacion || [];
  arr = arr.filter(a => isNum(+a.aprueba) && a.aprueba !== null && a.aprueba !== '');
  const ip = arr.filter(a => /ipsos|apoyo/i.test(a.encuestadora || ''));
  const use = ip.length >= 2 ? ip : arr;
  const dkey = a => String(a.fecha || a.campo || '');
  use.sort((a, b) => dkey(a).localeCompare(dkey(b)));
  if (use.length < 1) return null;
  const first = use[0];
  const limit = `${GOV[k].year}-11-30`;
  const inWin = use.filter(a => dkey(a) <= limit);
  const last = inWin[inWin.length - 1] || use[use.length - 1];
  return { first, last, n: use.length };
}

/* ---------- portada ---------- */
function renderVs() {
  const box = $('#vs');
  box.innerHTML = ['castillo', 'keiko'].map(k => {
    const pb = promiseBalance(k);
    const ap = approvals(k);
    const res = (D.resultados?.indicadores || []).find(i => i.id === 'homicidios_sinadef');
    const r = res?.[GOV[k].year];
    const hom = r && isNum(r.antes?.valor) && isNum(r.durante?.valor) ? (r.durante.valor / r.antes.valor - 1) * 100 : null;
    const g = k === 'castillo' ? D.castillo?.gobernabilidad : D.keiko?.gobernabilidad;
    const pm = g ? (g.premieres?.valor ?? g.n_premieres?.valor ?? g.premieres ?? null) : null;
    const rows = [];
    rows.push([pb ? `${pb.c}/${pb.total}` : '—', pb ? `promesas cumplidas según ${esc(pb.src)}` : 'sin balance independiente con metodología pública']);
    if (ap) rows.push([`${ap.first.aprueba}→${ap.last.aprueba}`, `% de aprobación (${esc(ap.first.encuestadora)}, primera medición → ~día 100)`]);
    if (hom !== null) rows.push([`${hom > 0 ? '+' : ''}${fmt(hom)}%`, 'homicidios (SINADEF) frente a los 100 días previos']);
    return `<div>
      <div class="who">${sw(k)}${esc(GOV[k].name)}</div>
      <div class="when">28-jul-${GOV[k].year} → 5-nov-${GOV[k].year}</div>
      <dl>${rows.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join('')}</dl>
    </div>`;
  }).join('');
}

/* ---------- veredictos ---------- */
function renderClaims() {
  const fc = D.factcheck; const out = [];
  if (fc?.infografia_b) {
    const b = fc.infografia_b;
    const vc = b.verificacion_castillo || {}, vk = b.verificacion_keiko || {};
    out.push(claim(vc.veredicto || 'engañoso', '«Castillo cumplió 3 de 43 promesas (7 %) y no cumplió 40 (93 %)»', 'Infografía «Primeros 100 días: Castillo vs. Keiko»',
      vc.resumen || vc.hechos || txt(vc), vc.fuentes || [vc.fuente_url]));
    const kg = (D.keiko?.trackers || []).find(t => /keiko gobierna/i.test(t.nombre || ''));
    const kBody = kg
      ? `El dato existe: «Keiko Gobierna» es un tracker ciudadano, independiente y de código abierto, que al día 103 registra ${kg.cumplidas} cumplidas, ${kg.en_proceso} en proceso y ${kg.sin_avance} sin avance de las ${kg.total} acciones de «Primeros 100 días» del plan «Perú con Orden». El «0 %» es correcto. Lo engañoso es el «100 % no cumplidas»: suma las 3 en proceso, y «sin avance» solo significa que no hay una norma publicada en El Peruano que lo acredite, no que se haya incumplido. Otros balances dan cifras parecidas: Hildebrandt en sus Trece, 1 de 67; el Observatorio de Planes de Gobierno, avances en 6 de 68.`
      : (vk.resumen || vk.hechos || txt(vk));
    out.push(claim(kg ? 'engañoso en la forma' : (vk.veredicto || 'no verificado'), '«Keiko no registra ninguna de 67 promesas cumplidas (0 %)»', 'Misma infografía; cita a «Keiko Gobierna (2026)»',
      kBody, kg ? [kg.url, ...(D.keiko.trackers.filter(t => t.url && t !== kg && isNum(t.total)).map(t => t.url))] : (vk.fuentes || [vk.fuente_url]),
      (b.problemas_metodologicos || []).map(p => `<li>${esc(typeof p === 'string' ? p : p.texto || JSON.stringify(p))}</li>`).join(''), 'Por qué las dos cifras no son comparables'));
  }
  if (fc?.infografia_a) {
    const a = fc.infografia_a;
    const items = (a.items || []).map(it => `<li><span class="tag">${esc(it.colegio)}</span> ${stamp(it.veredicto, cap(String(it.veredicto).split(/[(/]/)[0].trim()))}<br>${esc(it.hechos)}<div class="srcs">${(it.fuentes || []).map(u => link(u)).join('')}</div></li>`).join('');
    out.push(claim(a.veredicto_global || 'engañoso', '«Colegios en el gobierno de Keiko: 0 construidos, 4 destruidos»', `Infografía firmada por ${a.autor ? a.autor.split(' (')[0] : '—'}`,
      a.resumen_global, [], items, 'Ver los 4 casos uno por uno'));
    const cc = a.construidos_check;
    if (cc) out.push(claim(cc.veredicto || 'engañoso', '«0 colegios construidos»', 'Misma infografía',
      cc.resumen || cc.hechos || txt(cc), cc.fuentes || []));
  }
  const rc = D.resultados?.conclusion_neutral;
  if (rc) out.push(claim('prematuro', '«Ninguno de los dos gobiernos tiene resultados = valor público»', 'Comentario en el grupo',
    rc, [], null, null, 'Prematuro'));
  $('#claims').innerHTML = out.join('') || '<p class="empty">Sin datos de verificación.</p>';
}
function txt(o) { if (!o) return ''; if (typeof o === 'string') return o; return Object.entries(o).filter(([k, v]) => typeof v === 'string' && !/url|fuente|veredicto/.test(k)).map(([, v]) => v).join(' '); }
function claim(v, title, src, body, urls, sub, subTitle, label) {
  const lab = label || cap(String(v).split(/[(/;]/)[0].trim());
  return `<article class="claim">
    ${stamp(v, lab)}
    <div>
      <h3>${esc(title)}<span class="src">${esc(src)}</span></h3>
      <p>${esc(body)}</p>
      ${(urls || []).filter(Boolean).length ? `<div class="srcs">${urls.filter(Boolean).map(u => link(u)).join('')}</div>` : ''}
      ${sub ? `<details class="more"><summary>${esc(subTitle)}</summary><ul class="sub-claims">${sub}</ul></details>` : ''}
    </div></article>`;
}

/* ---------- promesas ---------- */
function renderPromises() {
  $('#promLegend').innerHTML = `<span><i style="background:var(--ok)"></i>Cumplidas</span><span><i style="background:var(--warn)"></i>En proceso</span><span><i style="background:var(--rule-strong)"></i>No cumplidas</span><span><i style="background:repeating-linear-gradient(45deg,var(--rule) 0 4px,transparent 4px 8px);border:1px dashed var(--rule-strong)"></i>Otras / no verificables</span>`;
  const rows = ORDER.map(k => {
    const pb = promiseBalance(k);
    if (!pb) {
      const note = k === 'keiko'
        ? 'No hay un balance independiente con metodología pública. El «0 de 67» viral no tiene fuente verificable.'
        : 'No se encontró un balance cuantitativo de promesas a los 100 días.';
      return `<div class="prow"><div class="lbl">${govLabel(k)}</div><div class="note" style="margin:0">${esc(note)}</div><div class="tot">—</div></div>`;
    }
    const seg = (cls, n, lab) => n > 0 ? `<span class="${cls}" style="flex:${n}" data-tip="${esc(lab)}: ${n} de ${pb.total} (${fmt(n / pb.total * 100)} %)"></span>` : '';
    return `<div class="prow">
      <div class="lbl">${govLabel(k)}<small>${esc(pb.src)}</small></div>
      <div class="pbar" role="img" aria-label="${esc(GOV[k].short)}: ${pb.c} cumplidas, ${pb.p} en proceso, ${pb.n} no cumplidas de ${pb.total}">
        ${seg('c', pb.c, 'Cumplidas')}${seg('p', pb.p, 'En proceso')}${seg('n', pb.n, pb.nLabel || 'No cumplidas')}${seg('u', pb.u, 'Otras / no verificables')}
      </div>
      <div class="tot"><b class="num" style="font-size:22px;color:var(--ink)">${fmt(pb.c / pb.total * 100, 0)} %</b><br>${pb.c} de ${pb.total}</div>
    </div>`;
  });
  const A = D.pp2050_cumplimiento?.cien_dias?.acciones;
  if (A) {
    const cnt = st => A.filter(a => a.estado_verificado === st).length;
    const t = A.length, cn = cnt('con_norma'), an = cnt('anunciado'), se = cnt('sin_evidencia');
    const seg = (cls, n, lab) => n > 0 ? `<span class="${cls}" style="flex:${n}" data-tip="${lab}: ${n} de ${t}"></span>` : '';
    rows.splice(2, 0, `<div class="prow">
      <div class="lbl">${govLabel('keiko')}<small>Segunda medición: Plan Perú 2050 (El Peruano)</small></div>
      <div class="pbar" role="img" aria-label="Keiko, segunda medición: ${cn} con norma, ${an} anunciadas, ${se} sin evidencia de ${t}">${seg('p', cn, 'Con norma publicada (avance, no cumplimiento)')}${seg('u', an, 'Solo anunciado')}${seg('n', se, 'Sin evidencia')}</div>
      <div class="tot"><b class="num" style="font-size:22px;color:var(--ink)">0 %</b><br>${cn} con norma</div>
    </div>`);
  }
  $('#promRows').innerHTML = rows.join('');
  const ppk = promiseBalance('ppk');
  $('#promNote').innerHTML = `<b>Ojo con comparar porcentajes.</b> El Comercio 2021 evaluó promesas del plan y de los anuncios; Convoca 2016 evaluó solo las promesas que el propio Ejecutivo anunció para sus 100 días${ppk?.nota ? ' (' + esc(ppk.nota) + ')' : ''}. La infografía viral junta «en proceso» con «no cumplidas», algo que El Comercio no hizo.`;
}

/* ---------- escalera ---------- */
const LEVELS = [
  ['insumo', 'Insumo', 'Leyes, decretos, presupuesto, nombramientos.'],
  ['actividad', 'Actividad', 'Procesos en marcha: mesas, lanzamientos, operativos.'],
  ['producto', 'Producto', 'Bienes o servicios entregados: camas, pensiones, obras.'],
  ['resultado', 'Resultado', 'Cambia la situación de la población: menos delitos, más aprendizaje.'],
  ['impacto', 'Impacto', 'Cambio de largo plazo en bienestar o desarrollo.'],
];
const normLevel = s => { s = String(s || '').toLowerCase(); return LEVELS.find(([k]) => s.startsWith(k) || s.includes(k))?.[0] || null; };
const isDone = s => /^cumplid|^cumple|^s[ií]\b|^logrado|^hecho/i.test(String(s || '').trim());

function ladderItems() {
  const items = [];
  const push = (k, arr, onlyDone) => (arr || []).forEach(p => {
    const lvl = normLevel(p.nivel_cadena_valor);
    if (!lvl) return;
    if (onlyDone && !isDone(p.estado)) return;
    items.push({ k, lvl, texto: p.texto, estado: p.estado, url: p.fuente_url });
  });
  push('castillo', D.castillo?.promesas, true);
  push('keiko', D.keiko?.promesas, true);
  push('ppk', hist('ppk')?.promesas_emblematicas, true);
  push('humala', hist('humala')?.promesas_emblematicas, true);
  push('garcia', hist('garcia')?.promesas_emblematicas, true);
  return items;
}
function renderLadder() {
  const items = ladderItems();
  const present = ORDER.filter(k => items.some(i => i.k === k));
  $('#ladderLegend').innerHTML = present.map(k => `<span>${govLabel(k)}</span>`).join('');
  $('#ladder').innerHTML = LEVELS.map(([k, name, def], i) => {
    const its = items.filter(x => x.lvl === k);
    return `<div class="step" style="--i:${i}">
      <h4>${name}</h4><p class="def">${def}</p>
      <div class="dots">${its.map(x => `<span class="dot" style="background:var(${GOV[x.k].v})" data-tip="${esc(GOV[x.k].short)}: ${esc(x.texto)}"></span>`).join('') || `<span class="note" style="font-size:13px">${i >= 3 ? 'Ninguna promesa llegó aquí' : '—'}</span>`}</div>
    </div>`;
  }).join('');
  $('#ladderList').innerHTML = present.map(k => {
    const its = items.filter(x => x.k === k).sort((a, b) => LEVELS.findIndex(l => l[0] === a.lvl) - LEVELS.findIndex(l => l[0] === b.lvl));
    return `<div><h4>${govLabel(k)}</h4><ol>${its.map(x => `<li>${esc(x.texto)} <span class="lvl ${['resultado', 'impacto'].includes(x.lvl) ? 'hi' : ''}">${esc(x.lvl)}</span> ${x.url ? `<span class="srcs" style="display:inline">${link(x.url)}</span>` : ''}</li>`).join('')}</ol></div>`;
  }).join('');
}

/* ---------- resultados ---------- */
function renderResults() {
  const R = D.resultados; if (!R) { $('#resTable').outerHTML = '<p class="empty">Sin datos.</p>'; return; }
  const cell = r => {
    if (!r) return '<td class="n">—</td>';
    const a = r.antes?.valor, b = r.durante?.valor;
    if (!isNum(a) || !isNum(b)) return `<td class="n"><small>${esc(isNum(a) ? fmtNum(a) : a ?? '—')} → ${esc(isNum(b) ? fmtNum(b) : b ?? '—')}</small></td>`;
    const d = (b / a - 1) * 100;
    return `<td class="n" data-tip="${esc(r.antes.periodo)} → ${esc(r.durante.periodo)}">${fmtNum(a)} → <b>${fmtNum(b)}</b><br><small>${d > 0 ? '+' : ''}${fmt(d)} %</small></td>`;
  };
  const rows = R.indicadores.map(i => `<tr><td><span class="metric">${esc(i.nombre)}</span><br><small>${esc(i.unidad)} · ${link(i.fuente_url, host(i.fuente_url))}</small></td>${cell(i['2021'])}${cell(i['2026'])}<td><small>${esc(i.rezago_nota)}</small></td></tr>`).join('');
  $('#resTable').innerHTML = `<thead><tr><th>Indicador</th><th class="n">${sw('castillo')} 2021: antes → 100 días</th><th class="n">${sw('keiko')} 2026: antes → 100 días</th><th>Por qué ojo</th></tr></thead><tbody>${rows}</tbody>`;
  $('#resNote').innerHTML = `<b>Lectura neutral.</b> ${esc(R.conclusion_neutral)}`;
}
const fmtNum = v => Math.abs(v) >= 1000 ? fmtInt(v) : fmt(v, Math.abs(v) < 20 ? 1 : 0);

/* ---------- gobernabilidad ---------- */
function govFacts(k) {
  const f = { premier: '—', confianza: '—', cambios: '—', facultades: '—', u: {} };
  if (k === 'castillo') {
    const g = D.castillo?.gobernabilidad || {};
    f.premier = g.premieres?.detalle || '—'; f.u.premier = g.premieres?.fuente_url;
    const vc = Array.isArray(g.votos_de_confianza?.detalle) ? g.votos_de_confianza.detalle : [];
    f.confianza = vc.map(v => `${v.gabinete} (${fmtDate(v.fecha)}): ${v.a_favor}-${v.en_contra}-${v.abstenciones}`).join(' · ') || '—';
    f.u.confianza = vc[0]?.fuente_url;
    f.cambios = `${g.ministros_salientes_100_dias?.valor ?? '—'} ministros salientes, 2 gabinetes, ${g.interpelaciones?.valor ?? 0} interpelación, ${g.censuras?.valor ?? 0} censuras`;
    f.u.cambios = g.ministros_salientes_100_dias?.fuente_url;
    const pl = g.proyectos_de_ley_ejecutivo;
    f.facultades = `${pl?.valor ?? '—'} proyectos de ley del Ejecutivo (${pl?.desglose?.iniciativas_de_politica_sustantiva ?? '?'} de política sustantiva; el resto, tratados y trámites). No pidió facultades.`;
    f.u.facultades = pl?.fuente_url;
    return f;
  }
  if (k === 'keiko') {
    const K = D.keiko || {}, g = K.gobernabilidad || {}, gb = K.gabinete || {};
    f.premier = `${gb.premier || '—'}: el mismo premier los 100 días`;
    f.confianza = 'Sin votación: con la reforma bicameral, el gabinete se presentó ante Diputados el 20-ago (confianza media, una sola fuente)';
    f.cambios = '1 ministro reemplazado (Transportes, 18-sep, por salud); censura a Interior rechazada';
    f.facultades = g.decretos_legislativos?.detalle ? `Facultades por 90 días (Ley 32743, 22-oct). ${g.decretos_legislativos.n ?? 0} decretos legislativos emitidos al día 100.` : '—';
    f.u.facultades = g.decretos_legislativos?.fuente_url;
    return f;
  }
  const g = hist(k)?.gobernabilidad || {};
  f.premier = g.premier_inicial || '—';
  const vc = g.voto_confianza; if (vc) { f.confianza = isNum(vc.a_favor) ? `${vc.a_favor} a favor, ${vc.en_contra} en contra, ${vc.abstenciones ?? '?'} abst.` : (vc.nota || '—'); f.u.confianza = vc.fuente_url; }
  const cm = g.cambios_gabinete_100d; if (cm) { f.cambios = `${cm.n ?? '—'}${cm.detalle ? ' · ' + cm.detalle : ''}`; f.u.cambios = cm.fuente_url; }
  const fa = g.facultades_delegadas_100d; if (fa) { f.facultades = fa.otorgadas ? `Sí: ${fa.ley || ''} (${fa.plazo_dias ?? '?'} días)` : (fa.nota || 'No identificadas'); f.u.facultades = fa.fuente_url; }
  return f;
}
function renderGov() {
  const facts = Object.fromEntries(ORDER.map(k => [k, govFacts(k)]));
  const row = (lab, key) => `<tr><td><span class="metric">${lab}</span></td>${ORDER.map(k => `<td><small>${esc(facts[k][key])}</small>${facts[k].u[key] ? `<div class="srcs">${link(facts[k].u[key])}</div>` : ''}</td>`).join('')}</tr>`;
  $('#govTable').innerHTML = `<thead><tr><th></th>${ORDER.map(k => `<th>${govLabel(k)}</th>`).join('')}</tr></thead><tbody>
    ${row('Premier inicial', 'premier')}${row('Voto de confianza / investidura', 'confianza')}${row('Cambios de gabinete en 100 días', 'cambios')}${row('Facultades / normas', 'facultades')}</tbody>`;
}

/* aprobación: gráfico de pesas (SVG) */
function renderApproval() {
  const holder = $('#apChart')?.parentElement; if (!holder) return;
  const data = ORDER.map(k => ({ k, a: approvals(k) })).filter(d => d.a);
  if (!data.length) { holder.innerHTML = '<p class="empty">Sin datos de aprobación.</p>'; return; }
  const W = 640, rowH = 44, pad = { l: 112, r: 24, t: 26, b: 28 }, H = pad.t + pad.b + rowH * data.length;
  const x = v => pad.l + (W - pad.l - pad.r) * v / 100;
  const grid = [0, 25, 50, 75, 100].map(v => `<line x1="${x(v)}" x2="${x(v)}" y1="${pad.t - 8}" y2="${H - pad.b}" stroke="var(--rule)" ${v === 50 ? 'stroke-dasharray="3 3" stroke="var(--rule-strong)"' : ''}/><text x="${x(v)}" y="${H - 8}" text-anchor="middle" font-size="12" fill="var(--muted)" font-family="Archivo">${v}%</text>`).join('');
  const rows = data.map((d, i) => {
    const y = pad.t + rowH * i + rowH / 2, a = +d.a.first.aprueba, b = +d.a.last.aprueba;
    const col = `var(${GOV[d.k].v})`;
    const t1 = `${GOV[d.k].short}: ${a}% (${d.a.first.encuestadora || ''}, ${d.a.first.fecha || d.a.first.campo || ''})`;
    const t2 = `${GOV[d.k].short}: ${b}% (${d.a.last.encuestadora || ''}, ${d.a.last.fecha || d.a.last.campo || ''})`;
    return `<text x="0" y="${y + 4}" font-size="14" font-family="Archivo" font-weight="600" fill="var(--ink)">${esc(GOV[d.k].short)} ${GOV[d.k].year}</text>
      <line x1="${x(a)}" x2="${x(b)}" y1="${y}" y2="${y}" stroke="${col}" stroke-width="3" stroke-linecap="round"/>
      <circle cx="${x(a)}" cy="${y}" r="7" fill="var(--surface)" stroke="${col}" stroke-width="2.5"><title>${esc(t1)}</title></circle>
      <circle cx="${x(b)}" cy="${y}" r="8" fill="${col}" stroke="var(--surface)" stroke-width="2"><title>${esc(t2)}</title></circle>
      <rect x="${Math.min(x(a), x(b)) - 12}" y="${y - 16}" width="${Math.abs(x(b) - x(a)) + 24}" height="32" fill="transparent" data-tip="${esc(t1)} → ${esc(t2.split(': ')[1])}"/>
      <text x="${x(b) + (b >= a ? 14 : -14)}" y="${y + 4}" text-anchor="${b >= a ? 'start' : 'end'}" font-size="13" font-family="Archivo" font-weight="700" fill="var(--ink)">${b}%</text>
      <text x="${x(a) + (b >= a ? -12 : 12)}" y="${y + 4}" text-anchor="${b >= a ? 'end' : 'start'}" font-size="12" font-family="Archivo" fill="var(--muted)">${a}</text>`;
  }).join('');
  holder.style.height = 'auto';
  holder.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Aprobación presidencial: primera medición y cerca del día 100">${grid}${rows}</svg>
    <p class="note" style="margin-top:6px">○ primera medición · ● más cercana al día 100. Pasa el cursor para ver encuestadora y fecha.</p>`;
}

/* ---------- economía ---------- */
const charts = [];
function restyle(c) {
  const ink = cssVar('--muted'), rule = cssVar('--rule');
  c.options.scales.x.ticks.color = ink; c.options.scales.y.ticks.color = ink;
  c.options.scales.x.grid.color = 'transparent'; c.options.scales.y.grid.color = rule;
  c.data.datasets.forEach(ds => { ds.borderColor = cssVar(GOV[ds.gov].v); ds.backgroundColor = ds.borderColor; });
}
const SERIES = [
  { key: 'tc', re: /PD04638PD/, title: 'Tipo de cambio (S/ por US$)', sub: 'Índice: día 0 = 100. Más arriba = sol más débil.' },
  { key: 'embig', re: /PD04709XD/, title: 'Riesgo país (EMBIG Perú)', sub: 'Índice: día 0 = 100. Más arriba = más riesgo percibido.' },
  { key: 'bvl', re: /PD38026MD/, title: 'Bolsa de Valores de Lima', sub: 'Índice: día 0 = 100. Más arriba = acciones más valoradas.' },
  { key: 'cobre', re: /PD04701XD/, title: 'Precio del cobre (control externo)', sub: 'Índice: día 0 = 100. No depende del gobierno peruano: sirve de referencia.' },
];
function ecoSeries() {
  /* devuelve {serieKey: {gov: {pts:[[day, idx]], d0, d100, var, d0f, d100f, url}}} */
  const out = {}; SERIES.forEach(s => out[s.key] = {});
  const add = (k, s, obj) => {
    const sp = SERIES.find(x => x.re.test(String(obj.codigo || obj.codigo_bcrp || '')));
    if (!sp || !s) return;
    const y = GOV[k].year, t0 = Date.UTC(y, 6, 28);
    const raw = (s.serie || []).map(([f, v]) => [(Date.parse(f) - t0) / 864e5, +v]).filter(([d, v]) => d >= -1 && d <= 101 && isFinite(v));
    const d0v = isNum(s.d0) ? s.d0 : (s.d0?.valor ?? raw.find(p => p[0] >= -1)?.[1]);
    if (!isNum(d0v) || !raw.length) return;
    out[sp.key][k] = { pts: raw.map(([d, v]) => [Math.max(0, d), v / d0v * 100]), d0: d0v, d100: isNum(s.d100) ? s.d100 : s.d100?.valor, v: s.var_pct, d0f: s.d0_fecha || s.d0?.fecha, d100f: s.d100_fecha || s.d100?.fecha, url: s.fuente_url || obj.fuente_url, unidad: obj.unidad, nombre: obj.nombre };
  };
  (D.indicadores?.series || []).forEach(s => { add('castillo', s.v1, s); add('keiko', s.v2, s); });
  ['ppk', 'humala', 'garcia'].forEach(k => (hist(k)?.macro || []).forEach(m => add(k, m, m)));
  return out;
}
let ecoVisible = new Set(ORDER);
function renderEco() {
  const S = ecoSeries();
  const govs = ORDER.filter(k => SERIES.some(s => S[s.key][k]));
  if (!govs.length) { $('#ecoCharts').innerHTML = '<p class="empty">Sin series macro.</p>'; return; }
  $('#ecoSeg').innerHTML = govs.map(k => `<button aria-pressed="true" data-g="${k}">${govLabel(k)}</button>`).join('');
  $('#ecoSeg').onclick = e => {
    const b = e.target.closest('button'); if (!b) return;
    const on = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', on);
    on ? ecoVisible.add(b.dataset.g) : ecoVisible.delete(b.dataset.g);
    charts.forEach(c => { c.data.datasets.forEach(ds => ds.hidden = !ecoVisible.has(ds.gov)); c.update(); });
  };
  const grid = $('#ecoCharts');
  SERIES.filter(s => Object.keys(S[s.key]).length).forEach(s => {
    const div = document.createElement('div'); div.className = 'chart';
    div.innerHTML = `<h3>${s.title}</h3><p class="sub">${s.sub}</p><div class="canvas"><canvas></canvas></div>`;
    grid.appendChild(div);
    const ds = ORDER.filter(k => S[s.key][k]).map(k => ({
      gov: k, label: `${GOV[k].short} ${GOV[k].year}`, data: S[s.key][k].pts.map(([x, y]) => ({ x, y })),
      borderWidth: k === 'castillo' || k === 'keiko' ? 2.5 : 1.5, pointRadius: 0, pointHoverRadius: 4, tension: 0.15,
      borderColor: cssVar(GOV[k].v),
    }));
    const c = new Chart(div.querySelector('canvas'), {
      type: 'line', data: { datasets: ds },
      options: {
        responsive: true, maintainAspectRatio: false, animation: false, parsing: false,
        interaction: { mode: 'nearest', axis: 'x', intersect: false },
        plugins: {
          legend: { display: true, position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, font: { family: 'Archivo', size: 12 }, color: cssVar('--ink-2') }, onClick: () => {} },
          tooltip: { callbacks: { title: it => `Día ${Math.round(it[0].parsed.x)}`, label: it => `${it.dataset.label}: ${fmt(it.parsed.y)}` }, titleFont: { family: 'Archivo' }, bodyFont: { family: 'Archivo' } },
        },
        scales: {
          x: { type: 'linear', min: 0, max: 100, ticks: { stepSize: 25, callback: v => `día ${v}`, font: { family: 'Archivo', size: 11 } }, grid: {} },
          y: { ticks: { font: { family: 'Archivo', size: 11 } }, grid: {} },
        },
      },
    });
    restyle(c); c.update('none'); charts.push(c);
  });
  /* tabla */
  const head = `<thead><tr><th>Serie</th>${govs.map(k => `<th class="n">${govLabel(k)}</th>`).join('')}</tr></thead>`;
  const body = SERIES.filter(s => Object.keys(S[s.key]).length).map(s => `<tr><td><span class="metric">${s.title}</span></td>${govs.map(k => {
    const v = S[s.key][k]; if (!v) return '<td class="n">—</td>';
    const vv = isNum(v.v) ? v.v : (isNum(v.d100) ? (v.d100 / v.d0 - 1) * 100 : null);
    return `<td class="n" data-tip="${esc(v.d0f || '')} → ${esc(v.d100f || '')}">${fmtNum(v.d0)} → ${isNum(v.d100) ? fmtNum(v.d100) : '—'}<br><small>${isNum(vv) ? (vv > 0 ? '+' : '') + fmt(vv) + ' %' : ''} ${link(v.url, 'BCRP')}</small></td>`;
  }).join('')}</tr>`).join('');
  $('#ecoTable').innerHTML = head + '<tbody>' + body + '</tbody>';
}

/* ---------- Estado ---------- */
const yearGov = y => Object.keys(GOV).find(g => String(GOV[g].year) === String(y));
function hbar(rows, max = 100, unit = '%') {
  return `<div style="display:grid;gap:7px">${rows.map(r => `<div style="display:grid;grid-template-columns:120px minmax(0,1fr) 56px;gap:10px;align-items:center;font-family:Archivo;font-size:14px" data-tip="${esc(r.tip || '')}">
    <span>${r.label}</span>
    <span style="background:var(--sunk);height:16px;border-radius:0 4px 4px 0"><span style="display:block;height:100%;width:${Math.max(0, Math.min(100, r.v / max * 100))}%;background:${r.col};border-radius:0 4px 4px 0"></span></span>
    <span class="num" style="text-align:right;font-weight:700">${fmt(r.v, 1)}${unit}</span></div>`).join('')}</div>`;
}
function renderEstado() {
  const P = D.performance, I = D.indicadores?.inversion_publica;
  const parts = [];
  if (P?.totales_gobierno_nacional) {
    const T = P.totales_gobierno_nacional;
    const ys = ORDER.map(k => String(GOV[k].year)).filter(y => T[y]);
    const mk = key => ys.map(y => { const k = yearGov(y); const t = T[y][key]; return t ? { label: govLabel(k), v: t.pct, col: `var(${GOV[k].v})`, tip: `${GOV[k].short} ${y}: devengado ene-oct S/ ${fmt(t.devengado_ene_oct / 1e9)} mil M de un PIM de S/ ${fmt(t.pim / 1e9)} mil M` } : null; }).filter(Boolean);
    parts.push(`<div class="charts">
      <div class="chart"><h3>Ejecución del Gobierno Nacional, todo el gasto</h3><p class="sub">Devengado de enero a octubre / PIM (%). Mayor = gasta más de lo presupuestado.</p>${hbar(mk('ActProy'))}</div>
      <div class="chart"><h3>Ejecución del Gobierno Nacional, solo proyectos de inversión</h3><p class="sub">Devengado de enero a octubre / PIM (%). La inversión es la que construye.</p>${hbar(mk('Proyecto'))}</div>
    </div><p class="note">El PIM de 2026 es el vigente al 7-nov; el de los años cerrados es el PIM final al 31-dic, que suele ser mayor. Eso favorece algo a 2026 en la comparación. Además, el devengado de enero a julio corresponde al gobierno anterior. Fuente: ${link('https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx', 'MEF – Consulta Amigable')}.</p>`);
  }
  if (I?.v1_2021 && I?.v2_2026) {
    const rowsI = [['proyectos_total', 'Proyectos, 3 niveles de gobierno'], ['proyectos_gobierno_nacional', 'Proyectos, Gobierno Nacional']].map(([key, lab]) => {
      const a = I.v1_2021[key], b = I.v2_2026[key]; if (!a || !b) return '';
      const c = x => `<td class="n">S/ ${fmt(x.devengado_jul_oct_soles / 1e9)} mil M<br><small>${fmt(x.devengado_jul_oct_pct_pim)} % del PIM en jul-oct</small></td>`;
      return `<tr><td><span class="metric">${lab}</span></td>${c(a)}${c(b)}</tr>`;
    }).join('');
    parts.push(`<h3 class="group-h">Inversión pública devengada en la ventana (jul-oct)</h3><div class="tbl-wrap"><table><thead><tr><th></th><th class="n">${govLabel('castillo')}</th><th class="n">${govLabel('keiko')}</th></tr></thead><tbody>${rowsI}</tbody></table></div><p class="note">Soles corrientes, sin ajustar por inflación. Fuente: ${link(I.fuente_url, 'MEF – Consulta Amigable')}.</p>`);
  }
  if (P) {
    const R = P.ranking;
    if (R) {
      const ys = ['2021', '2026'].filter(y => R[y]?.ActProy);
      parts.push(`<h3 class="group-h">Qué sectores ejecutaron más y menos (todo el gasto, a octubre)</h3><div class="charts">${ys.map(y => {
        const k = yearGov(y), r = R[y].ActProy;
        const li = (arr) => arr.map(x => `<li><span>${esc(cap(String(x.sector).toLowerCase()))}</span> <b class="num">${fmt(x.pct, 1)}%</b></li>`).join('');
        return `<div class="chart"><h3>${govLabel(k)}</h3><p class="sub">${esc(r.criterio || '')}</p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;font-size:14px"><div><b style="font-family:Archivo;color:var(--ok-ink)">▲ Mejores</b><ol style="padding-left:18px;margin:6px 0">${li(r.mejores_5 || [])}</ol></div><div><b style="font-family:Archivo;color:var(--bad-ink)">▼ Peores</b><ol style="padding-left:18px;margin:6px 0">${li(r.peores_5 || [])}</ol></div></div></div>`;
      }).join('')}</div>`);
    }
    ['obras_paralizadas', 'conflictos', 'rotacion', 'otros'].forEach(key => {
      const arr = P[key]; if (!Array.isArray(arr) || !arr.length) return;
      const titles = { obras_paralizadas: 'Obras paralizadas (Contraloría)', conflictos: 'Conflictos sociales (Defensoría del Pueblo)', rotacion: 'Rotación de altos funcionarios', otros: 'Otros indicadores de gestión' };
      parts.push(`<h3 class="group-h">${titles[key]}</h3>${tableFromArray(arr)}`);
    });
  }
  $('#estadoBody').innerHTML = parts.join('') || '<p class="empty">Datos de desempeño estatal en preparación.</p>';
}
function sectorBars(y, arr) {
  const rows = arr.filter(r => isNum(+r.pct)).sort((a, b) => b.pct - a.pct);
  const show = rows.length > 12 ? [...rows.slice(0, 6), null, ...rows.slice(-6)] : rows;
  const k = Object.keys(GOV).find(g => String(GOV[g].year) === y);
  const col = k ? `var(${GOV[k].v})` : 'var(--muted)';
  return `<div class="chart"><h3>${k ? govLabel(k) : esc(y)}</h3><p class="sub">${rows.length} sectores · mayor y menor ejecución</p>
    <div style="display:grid;gap:5px">${show.map(r => r === null ? '<div class="note" style="font-size:12px;text-align:center">⋯</div>' : `<div style="display:grid;grid-template-columns:minmax(0,1fr) 130px 44px;gap:8px;align-items:center;font-size:13px;font-family:Archivo" data-tip="${esc(r.sector)}: devengado ${fmtInt(+r.devengado)} de PIM ${fmtInt(+r.pim)}">
      <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(cap(String(r.sector).toLowerCase()))}</span>
      <span style="background:var(--sunk);height:12px;border-radius:0 4px 4px 0"><span style="display:block;height:100%;width:${Math.min(100, +r.pct)}%;background:${col};border-radius:0 4px 4px 0"></span></span>
      <span class="num" style="text-align:right">${fmt(+r.pct, 0)}%</span></div>`).join('')}</div></div>`;
}
function tableFromArray(arr) {
  const keys = [...new Set(arr.flatMap(o => Object.keys(o)))].filter(k => !/^(fuente_url|fuentes|url|confianza)$/.test(k));
  return `<div class="tbl-wrap"><table><thead><tr>${keys.map(k => `<th>${esc(cap(k.replace(/_/g, ' ')))}</th>`).join('')}<th>Fuente</th></tr></thead><tbody>${arr.map(o => `<tr>${keys.map(k => { const v = o[k]; return `<td${isNum(v) ? ' class="n"' : ''}>${isNum(v) ? fmtNum(v) : `<small>${esc(typeof v === 'object' && v ? JSON.stringify(v) : v ?? '—')}</small>`}</td>`; }).join('')}<td><small>${[o.fuente_url, o.url, ...(o.fuentes || [])].filter(Boolean).map(u => link(u)).join(' ')}${o.confianza ? ` · confianza ${esc(o.confianza)}` : ''}</small></td></tr>`).join('')}</tbody></table></div>`;
}
function genericBlock(o) {
  if (Array.isArray(o)) return tableFromArray(o);
  const flat = Object.entries(o).filter(([, v]) => v != null && typeof v !== 'object');
  const nested = Object.entries(o).filter(([, v]) => v && typeof v === 'object');
  return `${flat.length ? `<div class="tbl-wrap"><table><tbody>${flat.map(([k, v]) => `<tr><td><span class="metric">${esc(cap(k.replace(/_/g, ' ')))}</span></td><td>${/url/.test(k) ? link(v) : esc(isNum(v) ? fmtNum(v) : v)}</td></tr>`).join('')}</tbody></table></div>` : ''}
    ${nested.map(([k, v]) => Array.isArray(v) ? `<p class="note" style="margin:16px 0 6px"><b>${esc(cap(k.replace(/_/g, ' ')))}</b></p>${v.every(x => typeof x === 'string') ? `<ul class="note">${v.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : tableFromArray(v)}` : `<p class="note" style="margin:16px 0 6px"><b>${esc(cap(k.replace(/_/g, ' ')))}</b></p>${genericBlock(v)}`).join('')}`;
}

/* ---------- planes ---------- */
function renderPlanes() {
  const P = D.planes; if (!P) return;
  const c = P.castillo_2021, f = P.fp_2026, sv = c.plan_segunda_vuelta || {};
  const stat = (k, title, url, pages, rows) => `<div><h3 class="group-h" style="margin-top:0">${sw(k)}${esc(title)}</h3>
    <p class="note" style="margin:-6px 0 12px">${pages} pp. · ${link(url, 'PDF en el JNE')}</p>
    <dl class="plan-stats" style="display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:0">${rows.map(([n, l]) => `<dt class="num" style="font-weight:800;font-stretch:75%;font-size:30px;line-height:1">${n ?? '—'}</dt><dd style="margin:0;align-self:center;font-size:15px;color:var(--ink-2)">${l}</dd>`).join('')}</dl></div>`;
  const svM = sv.n_metas_cuantificadas ?? sv.metas_cuantificadas;
  const top = `<div class="charts" style="margin-bottom:40px">
    ${stat('castillo', 'Perú Libre: Ideario y Programa (2021)', c.url_pdf, c.paginas, [[c.n_metas_cuantificadas, 'metas con cifra'], [c.n_metas_cuantificadas_con_plazo, 'con plazo'], [c.n_metas_resultado, 'metas de resultado'], [c.n_metas_producto_actividad, 'de insumo, producto o actividad']])}
    ${stat('keiko', 'Fuerza Popular: Perú con Orden (2026)', f.url_pdf, f.paginas, [[f.n_metas_unicas ?? f.n_metas_cuantificadas, 'metas al 2031 (únicas)'], [f.n_metas_resultado, 'metas de resultado'], [f.n_metas_producto_actividad, 'de producto o actividad'], [f.n_compromisos_100d, `compromisos a 100 días (${f.n_compromisos_100d_cuantificados ?? '?'} con cifra)`]])}
  </div>
  ${sv && (sv.nombre || svM) ? `<p class="note">Castillo presentó en segunda vuelta otro documento, <b>${esc(sv.nombre || 'Perú al Bicentenario')}</b>${svM ? `, con ${esc(svM)} metas con cifra` : ''}${sv.url ? ' (' + link(sv.url) + ')' : ''}. Comparar un ideario doctrinario con un plan que trae tablas de metas favorece en el conteo al segundo: el formato pesa.</p>` : ''}`;
  const ejes = `<div class="plan-head"><span>Eje</span><span>${govLabel('castillo')}</span><span>${govLabel('keiko')}</span></div><div class="plans">${(P.ejes || []).map(e => `<div class="plan-row">
      <h4>${esc(e.eje)}</h4>
      <div><span class="who-m">${govLabel('castillo')}</span><p>${esc(e.castillo?.texto)}</p><span class="pg">p. ${esc(e.castillo?.pag)}</span></div>
      <div><span class="who-m">${govLabel('keiko')}</span><p>${esc(e.keiko?.texto)}</p><span class="pg">p. ${esc(e.keiko?.pag)}</span></div>
      ${e.diferencia_clave ? `<p class="diff">${esc(e.diferencia_clave)}</p>` : ''}
    </div>`).join('')}</div>`;
  const comp = (P.compromisos_100d || []).filter(x => x.compromiso);
  const compH = comp.length ? `<h3 class="group-h">Compromisos a 100 días y qué pasó</h3><div class="tbl-wrap"><table><thead><tr><th>Plan</th><th>Compromiso</th><th>Qué pasó</th></tr></thead><tbody>${comp.map(x => {
    const k = /castillo/.test(x.plan) ? 'castillo' : 'keiko';
    return `<tr><td>${govLabel(k)}</td><td><small>${esc(x.compromiso)}${x.pag ? ` (${esc(x.pag)})` : ''}</small></td><td><small>${esc(x.cumplimiento)}</small><div class="srcs">${[].concat(x.fuente || []).map(u => link(u)).join('')}</div></td></tr>`; }).join('')}</tbody></table></div>` : '';
  const con = (P.contradicciones || []);
  const conH = con.length ? `<h3 class="group-h">Contradicciones entre el plan y la gestión</h3><ul class="sub-claims">${con.map(x => {
    const k = /castillo/.test(x.plan) ? 'castillo' : 'keiko';
    return `<li><span class="tag">${govLabel(k)}: ${esc(x.plan_dice)}</span><br>${esc(x.hecho)}<div class="srcs">${[].concat(x.fuente || []).map(u => link(u)).join('')}</div></li>`; }).join('')}</ul>` : '';
  $('#planesBody').innerHTML = top + ejes + compH + conH;
}

/* ---------- línea de tiempo ---------- */
let tlCat = 'todas';
function renderTimeline() {
  const N = D.noticias;
  if (!N) { $('#timeline').innerHTML = '<p class="empty">Línea de tiempo en preparación.</p>'; return; }
  const cats = [...new Set([...(N.castillo || []), ...(N.keiko || [])].map(i => i.categoria).filter(Boolean))].sort();
  const lab = c => cap(String(c).replace(/_/g, ' '));
  $('#tlSeg').innerHTML = ['todas', ...cats].map(c => `<button data-c="${esc(c)}" aria-pressed="${c === tlCat}">${c === 'todas' ? 'Todas' : esc(lab(c))}</button>`).join('');
  $('#tlSeg').onclick = e => { const b = e.target.closest('button'); if (!b) return; tlCat = b.dataset.c; renderTimeline(); };
  const col = k => {
    const items = (N[k] || []).filter(i => tlCat === 'todas' || i.categoria === tlCat).sort((a, b) => (a.dia_n ?? 0) - (b.dia_n ?? 0));
    return `<div class="tl-col"><h3>${govLabel(k)}</h3>${items.map(i => `<div class="tl-item">
      <div class="tl-day" style="color:var(${GOV[k].v})">${esc(i.dia_n ?? '')}<small>${esc(fmtDate(i.fecha))}</small></div>
      <div><h4>${esc(i.titulo)}</h4><p>${esc(i.resumen)}</p>
      <div class="tl-meta"><span class="tone ${esc(i.tono)}">${esc(i.tono)}</span><span>${esc(lab(i.categoria))}</span>${(i.fuentes || []).map(u => link(u)).join('')}</div></div>
    </div>`).join('') || '<p class="note">Nada en esta categoría.</p>'}</div>`;
  };
  $('#timeline').innerHTML = col('castillo') + col('keiko');
}
const MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'set', 'oct', 'nov', 'dic'];
const fmtDate = s => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || ''); return m ? `${+m[3]} ${MES[+m[2] - 1]}` : (s || ''); };

/* ---------- videos ---------- */
function renderVideos() {
  const V = D.videos; if (!V) return;
  const card = v => `<a class="vid" href="${esc(safeUrl(v.url))}" target="_blank" rel="noopener" data-yt="${esc(v.plataforma === 'youtube' ? v.id : '')}">
      <div class="thumb">${v.plataforma === 'youtube' ? `<img loading="lazy" src="https://i.ytimg.com/vi/${encodeURIComponent(v.id)}/hqdefault.jpg" alt="">` : ''}</div>
      <h4>${esc(v.titulo_oembed)}</h4>
      <div class="vm">${esc(v.canal_oembed)} · ${esc(fmtDate(v.fecha_publicacion))} ${v.fecha_publicacion ? String(v.fecha_publicacion).slice(0, 4) : ''}${v.linea_editorial_canal ? ` · <span data-tip="Clasificación aproximada del canal, no del video">${esc(v.linea_editorial_canal)}</span>` : ''}</div>
    </a>`;
  const group = (k, arr) => arr?.length ? `<h3 class="group-h">${govLabel(k)}</h3><div class="vids">${arr.map(card).join('')}</div>` : '';
  const h = V.historicos || {};
  $('#vidBody').innerHTML = group('castillo', V.castillo) + group('keiko', V.keiko) + group('ppk', h.ppk) + group('humala', h.humala) + group('garcia', h.garcia);
  /* reproducir en línea al hacer clic (sin cookies) */
  $('#vidBody').addEventListener('click', e => {
    const a = e.target.closest('a.vid[data-yt]'); if (!a || !a.dataset.yt || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    const th = a.querySelector('.thumb');
    th.outerHTML = `<div class="vid-frame"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(a.dataset.yt)}?autoplay=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="${esc(a.querySelector('h4').textContent)}"></iframe></div>`;
    a.removeAttribute('data-yt');
  });
}

/* ---------- método ---------- */
function renderMethod() {
  const groups = [
    ['Verificación de infografías', D.factcheck?.caveats],
    ['Castillo 2021', D.castillo?.caveats],
    ['Keiko 2026', D.keiko?.caveats],
    ['García, Humala y PPK', D.expresidentes?.caveats],
    ['Mercados e inversión', D.indicadores?.caveats],
    ['Desempeño estatal', D.performance?.caveats],
    ['Indicadores de resultado', D.resultados?.caveats],
    ['Planes de gobierno', D.planes?.caveats],
    ['Línea de tiempo', D.noticias?.caveats],
    ['Videos', D.videos?.caveats],
  ].filter(([, c]) => Array.isArray(c) && c.length);
  $('#method').innerHTML = `<h3>Cómo se hizo</h3><ul>
    <li>Diez líneas de investigación paralelas, asistidas por IA, cada una con su propia fuente de verdad (archivos en <a href="https://github.com/unimauro/cien-dias-peru/tree/main/research" target="_blank" rel="noopener">/research</a>).</li>
    <li>Series macro tomadas directamente de la API del BCRPData, con el código de serie verificado contra su metadata. Resultados con datos de INEI, SINADEF/MINSA y MEF.</li>
    <li>Ventana: del 28 de julio (asunción) al 5 de noviembre (día 100) de cada año. Cuando no hay dato ese día, se usa el último día hábil.</li>
    <li>La cadena de valor público (insumo → actividad → producto → resultado → impacto) la clasificamos nosotros; otra persona podría ubicar alguna promesa un escalón más arriba o más abajo.</li>
    <li>Enlaces y videos validados el 7-nov-2026; algunos medios bloquean clientes automáticos.</li>
  </ul>` + groups.map(([t, c]) => `<h3>${esc(t)}: límites</h3><ul>${c.map(x => `<li>${esc(typeof x === 'string' ? x : x.texto || JSON.stringify(x))}</li>`).join('')}</ul>`).join('');
}

/* ---------- Plan Perú 2050: mensaje, segunda medición, brújula ---------- */
const MV = {
  coincide: ['Coincide', 'var(--ok)', 'v-ok'],
  coincide_con_matices: ['Coincide con matices', 'var(--warn)', 'v-warn'],
  no_coincide: ['No coincide', 'var(--bad)', 'v-bad'],
  no_verificable: ['No verificable', 'var(--unk)', 'v-unk'],
};
function renderMensaje() {
  const M = D.pp2050_mensaje; const box = document.querySelector('#msgBody');
  if (!M) { box.innerHTML = '<p class="empty">Sin datos.</p>'; return; }
  const v = M.resumen.veredictos, tot = M.resumen.n_afirmaciones;
  const order = ['coincide', 'coincide_con_matices', 'no_coincide', 'no_verificable'];
  const bar = `<div class="legend">${order.map(k => `<span><i style="background:${MV[k][1]}"></i>${MV[k][0]}: <b class="num">${v[k]}</b></span>`).join('')}</div>
    <div class="pbar" style="height:40px;margin-bottom:8px" role="img" aria-label="31 afirmaciones: ${order.map(k => MV[k][0] + ' ' + v[k]).join(', ')}">${order.map(k => `<span style="flex:${v[k]};background:${MV[k][1]}" data-tip="${MV[k][0]}: ${v[k]} de ${tot}"></span>`).join('')}</div>
    <p class="note" style="margin-top:0">${tot} afirmaciones con cifra. Corte: ${esc(M.meta.corte_verificacion)}. ${link(M.meta.url, 'Ver el mensaje')} · ${link(M.meta.origen_url, 'Análisis completo en planperu2050.pe')}</p>`;
  const ana = `<ul class="sub-claims" style="margin:24px 0 32px">${(M.analisis || []).map(a => `<li style="font-size:16.5px">${esc(a)}</li>`).join('')}</ul>`;
  const r = M.resumen.anuncios_28jul;
  const rend = r ? `<p class="note"><b>Frente a sus propios anuncios del 28 de julio:</b> el mensaje reportó avances en ${r.reporto}, parciales en ${r.parcial} y no mencionó ${r.no_menciono} de los 19.</p>` : '';
  const ejes = (M.ejes || []).map(e => {
    const its = M.afirmaciones.filter(a => a.eje === e.id); if (!its.length) return '';
    return `<details class="more msg-eje"><summary><b>${esc(e.ico)} ${esc(e.nombre)}</b> · ${its.length} afirmaciones ${its.map(a => `<span class="mini" style="background:${MV[a.veredicto]?.[1] || 'var(--unk)'}" title="${esc(MV[a.veredicto]?.[0] || a.veredicto)}"></span>`).join('')}</summary>
      <div class="claims" style="margin-top:8px">${its.map(a => {
        const vv = MV[a.veredicto] || ['—', '', 'v-unk'];
        const det = (a.verificacion || []).map(x => `<li><span class="tag">${esc(x.afirmacion)}</span> <small>(${esc(MV[x.veredicto]?.[0] || x.veredicto)})</small><br>${esc(x.dato_oficial || '')}${x.nota ? ` <i>${esc(x.nota)}</i>` : ''}<div class="srcs">${link(x.url, x.fuente ? x.fuente.split('(')[0].trim().slice(0, 60) : null)}</div></li>`).join('');
        return `<article class="claim"><span class="stamp ${vv[2]}"><span class="ic" aria-hidden="true">${ICON[vv[2]]}</span>${vv[0]}</span><div><h3>«${esc(a.texto)}»<span class="src">Minuto ${esc(a.ts)}</span></h3>${det ? `<ul class="sub-claims">${det}</ul>` : ''}</div></article>`;
      }).join('')}</div></details>`;
  }).join('');
  box.innerHTML = bar + ana + rend + `<h3 class="group-h">Afirmación por afirmación</h3>` + ejes;
}
function renderBrujula() {
  const B = D.pp2050_cumplimiento?.brujula; const box = document.querySelector('#brujula'); if (!B || !box) return;
  const rows = B.indicadores.filter(i => isNum(+i.inicio?.valor) && isNum(+i.actual?.valor)).map(i => {
    const a = +i.inicio.valor, b = +i.actual.valor;
    const better = i.deseado === 'baja' ? b < a : i.deseado === 'sube' || i.deseado === 'alta' ? b > a : null;
    const same = Math.abs(b - a) < 1e-9;
    const st = better === null ? ['·', 'Contexto (sin dirección deseada)', 'var(--muted)'] : same ? ['=', 'Sin cambio', 'var(--muted)'] : better ? ['▲', 'Mejora', 'var(--ok-ink)'] : ['▼', 'Empeora', 'var(--bad-ink)'];
    return `<tr><td><span class="metric">${esc(i.nombre)}</span><br><small>${esc(i.unidad)}</small></td>
      <td class="n" data-tip="${esc(i.inicio.fuente || '')}">${fmtNum(a)}<br><small>${esc(i.inicio.periodo)}</small></td>
      <td class="n" data-tip="${esc(i.actual.fuente || '')}">${fmtNum(b)}<br><small>${esc(i.actual.periodo)}</small></td>
      <td><b style="color:${st[2]};font-family:Archivo">${st[0]} ${st[1]}</b>${i.nota ? `<br><small>${esc(i.nota)}</small>` : ''}<div class="srcs">${link(i.actual.url)}</div></td></tr>`;
  }).join('');
  box.innerHTML = `<h3 class="group-h">Brújula 2026: ¿el país está mejor o peor que el 28 de julio?</h3>
    <p class="note" style="margin-top:-6px">Indicadores oficiales al inicio del gobierno de Keiko Fujimori frente al último dato. «Mejora» o «empeora» según la dirección deseada de cada indicador; no implica que el cambio lo haya causado el gobierno. Fuente: ${link(D.pp2050_cumplimiento.meta.origen_url, 'Plan Perú 2050')}, corte ${esc(B.corte)}.</p>
    <div class="tbl-wrap"><table><thead><tr><th>Indicador</th><th class="n">Inicio</th><th class="n">Último dato</th><th>Dirección</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

/* ---------- semáforo ---------- */
const BANDS = [
  [70, 'Bien', 'sem-g'], [50, 'Regular', 'sem-y'], [30, 'Malo', 'sem-o'], [0, 'Crítico', 'sem-r'],
];
const band = sc => isNum(sc) ? BANDS.find(b => sc >= b[0]) : null;
function semCell(sc, main, sub, tipTxt) {
  const b = band(sc);
  if (!b) return `<td class="sem-cell sem-na" data-tip="${esc(tipTxt || 'Sin dato')}"><span class="sv">—</span><span class="sl">sin dato</span></td>`;
  return `<td class="sem-cell ${b[2]}" data-tip="${esc(tipTxt || '')}"><span class="sv">${main}</span><span class="sl">${b[1]}${sub ? ' · ' + sub : ''}</span></td>`;
}
function renderSemaforo() {
  $('#semLegend').innerHTML = BANDS.map(b => `<span><i class="${b[2]}" style="border-radius:3px"></i>${b[1]} (${{70: '≥70', 50: '50–69', 30: '30–49', 0: '<30'}[b[0]]})</span>`).join('') + '<span><i class="sem-na" style="border-radius:3px"></i>Sin dato</span>';
  const I = D.indice100;
  if (!I) { $('#semIndice').innerHTML = '<p class="empty">Índice en preparación.</p>'; return; }
  const govs = ORDER.filter(k => I.gobiernos?.[k]);
  const head = `<thead><tr><th>Dimensión <small>(peso)</small></th>${govs.map(k => `<th class="n">${govLabel(k)}</th>`).join('')}</tr></thead>`;
  const rows = I.dimensiones.map(d => `<tr><td><span class="metric">${esc(d.nombre)}</span> <small>(${d.peso} %)</small><br><small>${esc(d.desc)}</small></td>${govs.map(k => {
    const c = I.gobiernos[k].dims[d.id] || {};
    return semCell(c.score, isNum(c.score) ? Math.round(c.score) : '—', '', `${GOV[k].short}: ${c.valor || 'sin dato'}${c.fuente ? ' · ' + c.fuente : ''}`);
  }).join('')}</tr>`).join('');
  const tot = `<tr class="sem-total"><td><span class="metric">Índice de los 100 días</span><br><small>Promedio ponderado de las dimensiones con dato (los pesos se reescalan si falta alguna)</small></td>${govs.map(k => {
    const g = I.gobiernos[k];
    if (!isNum(g.total)) return `<td class="sem-cell sem-na" data-tip="Solo ${g.cobertura} % del peso tiene dato; con menos del 70 % no se publica el total"><span class="sv">—</span><span class="sl">cobertura ${g.cobertura} % (&lt;70 %)</span></td>`;
    return semCell(g.total, fmt(g.total, 1), `${g.cobertura} % de cobertura`, `${GOV[k].short}: ${fmt(g.total)} / 100 con ${g.n_dims} de ${I.dimensiones.length} dimensiones`);
  }).join('')}</tr>`;
  $('#semIndice').innerHTML = `<div class="tbl-wrap"><table class="sem">${head}<tbody>${rows}${tot}</tbody></table></div>`;
  const C = I.contexto || [];
  if (C.length) {
    const cg = ORDER.filter(k => C.some(r => r.gobiernos?.[k]));
    const dimLab = { corrupcion: 'Corrupción', democracia: 'Democracia', estado_de_derecho: 'Estado de derecho', efectividad: 'Efectividad del gobierno', libertades: 'Libertades', desigualdad: 'Desigualdad', pobreza: 'Pobreza', desarrollo_humano: 'Desarrollo humano', confianza: 'Confianza ciudadana', seguridad: 'Seguridad' };
    const groups = [...new Set(C.map(r => r.dimension))];
    const body = groups.map(g => `<tr class="sem-grp"><td colspan="${cg.length + 1}">${esc(dimLab[g] || cap(g))}</td></tr>` + C.filter(r => r.dimension === g).map(r => `<tr><td><span class="metric">${esc(r.nombre)}</span><br><small>${esc(r.escala_txt || '')} · ${link(r.fuente_url, r.institucion || host(r.fuente_url))}</small></td>${cg.map(k => {
      const v = r.gobiernos[k]; if (!v) return semCell(null);
      const arrow = isNum(v.score_primer) && isNum(v.score_recibio) ? (Math.abs(v.score_primer - v.score_recibio) < 0.5 ? '=' : (v.score_primer > v.score_recibio ? '▲' : '▼')) : '';
      const main = `${fmtSem(v.recibio)}${isNum(v.primer) ? ` → ${fmtSem(v.primer)} <b class="arr">${arrow}</b>` : (k === 'keiko' ? ' <small>(base)</small>' : '')}`;
      return semCell(isNum(v.score_primer) ? v.score_primer : v.score_recibio, main, '', `${GOV[k].short}: ${v.anio_recibio || ''} = ${fmtSem(v.recibio)}${isNum(v.primer) ? `; ${v.anio_primer} = ${fmtSem(v.primer)}` : ' (primer año aún sin medición)'}`);
    }).join('')}</tr>`).join('')).join('');
    $('#semIntl').innerHTML = `<div class="tbl-wrap"><table class="sem">${`<thead><tr><th>Índice</th>${cg.map(k => `<th class="n">${govLabel(k)}</th>`).join('')}</tr></thead>`}<tbody>${body}</tbody></table></div><p class="note">El color corresponde al último valor de la celda, ubicado en su escala de 0 a 100 (mejor = 100). ▲ mejoró y ▼ empeoró en el primer año.</p>`;
  } else $('#semIntl').innerHTML = '<p class="empty">Índices internacionales en preparación.</p>';
  if (I.metodo) $('#semMetodo').innerHTML = `<details class="more" style="margin-top:20px"><summary>Cómo se calcula el índice</summary><ul class="sub-claims">${I.metodo.map(m => `<li>${esc(m)}</li>`).join('')}</ul></details>`;
}
const fmtSem = v => !isNum(v) ? '—' : Math.abs(v) < 1 ? fmt(v, 2) : Math.abs(v) < 10 ? fmt(v, 1) : fmt(v, 0);

})();
