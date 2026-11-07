/* 100 días bajo la lupa — render desde research/*.json */
(() => {
'use strict';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl = u => { try { const p = new URL(u); return (p.protocol === 'http:' || p.protocol === 'https:') ? p.href : '#'; } catch { return '#'; } };
const $ = s => document.querySelector(s);
const isNum = v => typeof v === 'number' && isFinite(v);
const fmt = (v, d = 1) => isNum(v) ? v.toLocaleString('es-ES', { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: 'always' }) : '—';
const fmtInt = v => isNum(v) ? Math.round(v).toLocaleString('es-ES', { useGrouping: 'always' }) : (v ?? '—');
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

/* tooltips en pantallas táctiles: tocar muestra la fuente */
document.addEventListener('click', e => {
  const t = e.target.closest('[data-tip]');
  if (!t || matchMedia('(hover: hover)').matches) return;
  tip.textContent = t.dataset.tip; tip.classList.add('on');
  const r = t.getBoundingClientRect();
  tip.style.left = Math.max(8, Math.min(r.left, innerWidth - tip.offsetWidth - 8)) + 'px';
  tip.style.top = (r.bottom + 6 + tip.offsetHeight > innerHeight ? r.top - tip.offsetHeight - 6 : r.bottom + 6) + 'px';
  clearTimeout(window.__tipT); window.__tipT = setTimeout(() => tip.classList.remove('on'), 4000);
});

/* tema */
$('#themeBtn').addEventListener('click', () => {
  requestAnimationFrame(() => { if ($('#apSeries')) renderApSeries(); if ($('#homSeries')) renderHomSeries(); });
  const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  $('#themeBtn').setAttribute('aria-pressed', String(next === 'dark'));
  try { localStorage.setItem('theme', next); } catch {}
  charts.forEach(c => restyle(c)); charts.forEach(c => c.update('none'));
  renderApproval();
});

/* estado inicial del botón de tema */
{
  const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  $('#themeBtn').setAttribute('aria-pressed', String(cur === 'dark'));
}

/* menú de páginas (móvil y tableta) */
const menu = $('#menu'), menuBtn = $('#menuBtn');
const setMenu = open => {
  if (!menu || !menuBtn) return;
  menuBtn.setAttribute('aria-expanded', String(open));
  menu.hidden = !open;
};
if (menuBtn) {
  menuBtn.addEventListener('click', () => setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menuBtn.getAttribute('aria-expanded') === 'true') { setMenu(false); menuBtn.focus(); } });
  document.addEventListener('click', e => { if (menuBtn.getAttribute('aria-expanded') === 'true' && !e.target.closest('#menu, #menuBtn')) setMenu(false); });
}

/* enlaces antiguos (#veredictos, etc.) llevan a su página nueva */
{
  const MOVED = { veredictos: 'verificacion.html#veredictos', mensaje: 'verificacion.html#mensaje', promesas: 'promesas.html#promesas', valor: 'promesas.html#valor',
    resultados: 'gestion.html#resultados', gobernabilidad: 'gestion.html#gobernabilidad', estado: 'gestion.html#estado', economia: 'gestion.html#economia',
    planes: 'planes.html', linea: 'linea.html', videos: 'linea.html#videos', metodo: 'metodo.html' };
  const h = location.hash.slice(1);
  if (document.body.dataset.page === 'index' && MOVED[h] && !document.getElementById(h)) location.replace(MOVED[h]);
}

/* en esta página: resalta la sección visible */
const onLinks = [...document.querySelectorAll('.onpage a')];
if (onLinks.length) {
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return;
    onLinks.forEach(a => { const on = a.getAttribute('href') === '#' + en.target.id; a.classList.toggle('on', on); on ? a.setAttribute('aria-current', 'location') : a.removeAttribute('aria-current'); });
  }), { rootMargin: '-35% 0px -60% 0px' });
  document.querySelectorAll('section.block').forEach(s => io.observe(s));
}

/* analítica: descargas de PDF */
document.addEventListener('click', e => {
  const a = e.target.closest('a[href$=".pdf"]');
  if (a) { try { (window.dataLayer = window.dataLayer || []).push({ event: 'descarga_pdf', archivo: a.getAttribute('href') }); } catch {} }
});

/* barra de progreso de lectura */
const prog = $('#prog');
let progQ = false;
const progUpd = () => {
  progQ = false;
  const max = document.documentElement.scrollHeight - innerHeight;
  prog.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
};
addEventListener('scroll', () => { if (!progQ) { progQ = true; requestAnimationFrame(progUpd); } }, { passive: true });
addEventListener('resize', progUpd);
progUpd();

/* apoyo: QR de Yape */
const yBtn = $('#yape-btn'), yBox = $('#yape-box');
if (yBtn && yBox) yBtn.addEventListener('click', () => {
  const open = yBtn.getAttribute('aria-expanded') !== 'true';
  yBtn.setAttribute('aria-expanded', String(open));
  yBox.hidden = !open;
});

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
const RENDERS = [
  ['#score', () => renderScore('#score'), ['indice100']],
  ['#scoreFull', () => renderScore('#scoreFull'), ['indice100']],
  ['#vs', renderVs, ['castillo', 'keiko', 'factcheck', 'resultados']],
  ['#claims', renderClaims, ['factcheck', 'keiko', 'resultados']],
  ['#waffle', renderWaffle, ['promesas_base']],
  ['#promRows', renderPromises, ['castillo', 'factcheck', 'keiko', 'expresidentes', 'pp2050_cumplimiento']],
  ['#ladder', renderLadder, ['castillo', 'keiko', 'expresidentes']],
  ['#homSeries', renderHomSeries, ['resultados']],
  ['#resTable', renderResults, ['resultados']],
  ['#govTable', renderGov, ['castillo', 'keiko', 'expresidentes']],
  ['#apChart', renderApproval, ['castillo', 'keiko', 'expresidentes']],
  ['#apSeries', renderApSeries, ['castillo', 'keiko', 'expresidentes']],
  ['#ecoCharts', renderEco, ['indicadores', 'expresidentes']],
  ['#estadoBody', renderEstado, ['performance', 'indicadores']],
  ['#planesBody', renderPlanes, ['planes']],
  ['#tlDensity', renderTlDensity, ['noticias']],
  ['#timeline', renderTimeline, ['noticias']],
  ['#vidBody', renderVideos, ['videos']],
  ['#method', renderMethod, ['factcheck', 'castillo', 'keiko', 'expresidentes', 'indicadores', 'performance', 'resultados', 'planes', 'noticias', 'videos']],
  ['#msgBody', renderMensaje, ['pp2050_mensaje']],
  ['#brujula', renderBrujula, ['pp2050_cumplimiento']],
  ['#semIndice', renderSemaforo, ['indice100']],
  ['#semBars', renderDimBars, ['indice100']],
  ['#pbBalances', renderBalances, ['promesas_base']],
  ['#pbApp', () => { if (!$('#govSem')) renderBase(); }, ['promesas_base']],
  ['#govSem', renderGovPage, ['indice100', 'castillo', 'keiko', 'expresidentes', 'noticias', 'videos', 'factcheck', 'promesas_base']],
].filter(([sel]) => document.querySelector(sel));
const FILES = [...new Set(RENDERS.flatMap(r => r[2]))];

Promise.all(FILES.map(f => fetch(`research/${f}.json`, { cache: 'no-cache' }).then(r => r.ok ? r.json() : null).catch(() => null)))
  .then(arr => {
    FILES.forEach((f, i) => D[f] = arr[i]);
    RENDERS.forEach(([sel, fn]) => { try { fn(); } catch (e) { console.error(sel, e); } });
    countUp();
    stackTables();
    if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t) setTimeout(() => t.scrollIntoView(), 60); }
  });

/* tablas largas: en móvil cada fila se vuelve una tarjeta con la etiqueta de su columna */
function stackTables() {
  document.querySelectorAll('.tbl-wrap table:not(.sem):not(#govTable):not(#ecoTable)').forEach(t => {
    const heads = [...t.querySelectorAll('thead th')].map(th => th.textContent.trim());
    if (!heads.length) return;
    t.classList.add('stack');
    t.querySelectorAll('tbody tr').forEach(tr => [...tr.children].forEach((td, i) => { if (heads[i]) td.dataset.label = heads[i]; }));
  });
}
let rzT;
addEventListener('resize', () => { clearTimeout(rzT); rzT = setTimeout(() => { if ($('#apSeries') && D.castillo) renderApSeries(); if ($('#homSeries') && D.resultados) renderHomSeries(); }, 200); });

/* números que cuentan hasta su valor (solo animación; el texto final es el dato exacto) */
function countUp() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const els = [...document.querySelectorAll('[data-count]')];
  const io2 = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return; io2.unobserve(en.target);
    const el = en.target, final = el.textContent, target = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0);
    if (!isFinite(target)) return;
    const t0 = performance.now(), dur = 900;
    const step = t => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(target * e, dec); if (k < 1) requestAnimationFrame(step); else el.textContent = final; };
    requestAnimationFrame(step);
  }), { threshold: .4 });
  els.forEach(el => io2.observe(el));
}

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
  const limit = `${GOV[k].year}-11-04`;
  const inWin = use.filter(a => dkey(a) <= limit);
  const last = inWin[inWin.length - 1] || use[use.length - 1];
  return { first, last, n: use.length };
}

/* ---------- portada: marcador del índice ---------- */
function renderScore(sel = '#score') {
  const box = $(sel); const I = D.indice100;
  if (!I?.gobiernos) { box.innerHTML = '<p class="empty">El índice no está disponible.</p>'; return; }
  const ks = ['castillo', 'keiko', 'ppk'].filter(k => isNum(I.gobiernos[k]?.total));
  const S = I.sensibilidad || {};
  const rc = I.gobiernos.castillo?.rango, rk = I.gobiernos.keiko?.rango;
  const pct = v => Math.max(0, Math.min(100, v));
  const ov = rc && rk ? [Math.max(rc.p5, rk.p5), Math.min(rc.p95, rk.p95)] : null;
  const ovOk = ov && ov[1] > ov[0];
  const rows = ks.map(k => {
    const g = I.gobiernos[k], r = g.rango, ref = k === 'ppk' ? ' ref' : '';
    const tipTxt = `${GOV[k].short} ${GOV[k].year}: ${fmt(g.total)} / 100${r ? `; en el 90 % de las simulaciones queda entre ${fmt(r.p5)} y ${fmt(r.p95)}` : ''}`;
    return `<div class="sc-row${ref}">
      <div class="sc-name">${sw(k)}<span><b>${esc(GOV[k].short)}</b> ${GOV[k].year}${ref ? ' <small>referencia</small>' : ''}</span></div>
      <div class="sc-track" data-tip="${esc(tipTxt)}">
        ${ovOk && !ref ? `<span class="sc-ov" style="left:${pct(ov[0])}%;width:${pct(ov[1]) - pct(ov[0])}%"></span>` : ''}
        ${r ? `<span class="sc-range" style="left:${pct(r.p5)}%;width:${pct(r.p95) - pct(r.p5)}%;--c:var(${GOV[k].v})"></span>` : ''}
        <span class="sc-pt" style="left:${pct(g.total)}%;--c:var(${GOV[k].v})"></span>
      </div>
      <div class="sc-val"><b class="num" data-count="${g.total}" data-dec="1">${fmt(g.total)}</b>${r ? `<small class="num">${fmt(r.p5, 0)}–${fmt(r.p95, 0)}</small>` : ''}</div>
    </div>`;
  }).join('');
  const sens = isNum(S.p_castillo_mayor_keiko)
    ? ` Castillo queda arriba solo en el ${Math.round(S.p_castillo_mayor_keiko * 100)} % de las simulaciones${isNum(S.p_ppk_primero) ? `; PPK queda por encima de ambos en el ${Math.round(S.p_ppk_primero * 100)} %` : ''}.` : '';
  box.innerHTML = `<div class="sc-top">
      <span class="stamp v-warn sc-stamp"><span class="ic" aria-hidden="true">≈</span>Empate técnico</span>
      <p class="sc-q">Castillo frente a Keiko en el índice de los 100 días</p>
    </div>
    <div class="sc-plot" role="img" aria-label="Índice de los 100 días, de 0 a 100. ${ks.map(k => `${GOV[k].short}: ${fmt(I.gobiernos[k].total)}, rango ${fmt(I.gobiernos[k].rango?.p5, 0)} a ${fmt(I.gobiernos[k].rango?.p95, 0)}`).join('. ')}.">
      ${rows}
      <div class="sc-row sc-axis-row"><span class="sc-name" aria-hidden="true"></span><div class="sc-axis">
        <span class="sc-bands"><i class="sem-r" style="flex:30"></i><i class="sem-o" style="flex:20"></i><i class="sem-y" style="flex:20"></i><i class="sem-g" style="flex:30"></i></span>
        ${[0, 30, 50, 70, 100].map(v => `<span class="sc-tick" style="left:${v}%">${v}</span>`).join('')}
      </div><span class="sc-val" aria-hidden="true"></span></div>
      ${ovOk ? `<p class="sc-ovl"><span class="sc-ovk" aria-hidden="true"></span>Zona rayada: donde se superponen los rangos de Castillo y Keiko (${fmt(ov[0], 0)}–${fmt(ov[1], 0)})</p>` : ''}
    </div>
    <figcaption id="${sel === '#score' ? 'scoreCap' : 'scoreCap2'}">Con estos datos no se puede decir cuál lo hizo peor: en nuestro índice experimental sus rangos se superponen. Punto: valor con nuestros pesos. Barra: rango del 5 % al 95 % de 20 000 simulaciones con otros pesos y fórmulas.${sens} ${sel === '#score' ? '<a href="contexto.html">Ver el semáforo completo</a>' : ''}</figcaption>`;
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
    if (ap) rows.push([`${ap.first.aprueba}→${ap.last.aprueba}`, `% de aprobación (${esc(ap.first.encuestadora)}, primera medición → última antes del día 100)`]);
    if (hom !== null) rows.push([`${hom > 0 ? '+' : ''}${fmt(hom)}%`, 'homicidios (SINADEF) frente a los 100 días previos']);
    return `<div>
      <div class="who">${sw(k)}${esc(GOV[k].name)}</div>
      <div class="when">28-jul-${GOV[k].year} → 4-nov-${GOV[k].year} (día 100)</div>
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
  if (rc) out.push(claim('no verificable', '«Ninguno de los dos gobiernos tiene resultados = valor público»', 'Comentario en el grupo',
    rc, [], null, null, 'Prematuro / no verificable'));
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
const isDone = s => { s = String(s || '').trim().toLowerCase(); return /^cumplid/.test(s) && !/parcial/.test(s); };

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
    f.facultades = `${pl?.valor ?? '—'} proyectos de ley del Ejecutivo (${pl?.desglose?.iniciativas_de_politica_sustantivas ?? '?'} de política sustantiva; el resto, tratados y trámites). Pidió facultades tributarias al Congreso el 28-oct-2021; no se aprobaron dentro de la ventana.`;
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
  const W = Math.max(340, Math.min(720, holder.clientWidth || 640)), rowH = 44, pad = { l: W < 480 ? 92 : 112, r: 34, t: 26, b: 28 }, H = pad.t + pad.b + rowH * data.length;
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
  holder.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" style="max-width:100%" role="img" aria-label="Aprobación presidencial: primera medición y cerca del día 100">${grid}${rows}</svg>
    <p class="note" style="margin-top:6px">○ primera medición · ● más cercana al día 100. Pasa el cursor para ver encuestadora y fecha.</p>`;
}

/* ---------- economía ---------- */
const charts = [];
function restyle(c) {
  const ink = cssVar('--muted'), rule = cssVar('--rule');
  c.options.scales.x.ticks.color = ink; c.options.scales.y.ticks.color = ink;
  c.options.scales.x.grid.color = 'transparent'; c.options.scales.y.grid.color = rule;
  c.data.datasets.forEach(ds => { ds.borderColor = cssVar(GOV[ds.gov].v); ds.backgroundColor = ds.borderColor; });
  if (c.options.plugins?.legend?.labels) c.options.plugins.legend.labels.color = cssVar('--ink-2');
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
    div.innerHTML = `<h3>${s.title}</h3><p class="sub">${s.sub}</p><div class="canvas"><canvas role="img" aria-label="${esc(s.title)}: serie indexada a 100 el día de la asunción, por gobierno. Los valores están en la tabla de abajo."></canvas></div>`;
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
    return `<tr><td>${govLabel(k)}</td><td><small>${esc(x.compromiso)}${x.pag ? ` (${esc(x.pag)})` : ''}</small></td><td><small>${esc(x.cumplimiento)}</small><div class="srcs">${[].concat(x.fuente || []).flatMap(f => String(f).match(/https?:\/\/[^\s;,)]+/g) || []).map(u => link(u)).join(' ')}</div></td></tr>`; }).join('')}</tbody></table></div>` : '';
  const con = (P.contradicciones || []);
  const conH = con.length ? `<h3 class="group-h">Contradicciones entre el plan y la gestión</h3><ul class="sub-claims">${con.map(x => {
    const k = /castillo/.test(x.plan) ? 'castillo' : 'keiko';
    return `<li><span class="tag">${govLabel(k)}: ${esc(x.plan_dice)}</span><br>${esc(x.hecho)}<div class="srcs">${[].concat(x.fuente || []).flatMap(f => String(f).match(/https?:\/\/[^\s;,)]+/g) || []).map(u => link(u)).join(' ')}</div></li>`; }).join('')}</ul>` : '';
  $('#planesBody').innerHTML = top + ejes + compH + conH;
}

/* ---------- línea de tiempo ---------- */
let tlCat = 'todas';
function renderTimeline() {
  const N = D.noticias;
  if (!N) { $('#timeline').innerHTML = '<p class="empty">Línea de tiempo en preparación.</p>'; return; }
  const cats = [...new Set([...(N.castillo || []), ...(N.keiko || [])].map(i => i.categoria).filter(Boolean))].sort();
  const CATS = { economia: 'Economía', gabinete: 'Gabinete', seguridad: 'Seguridad', educacion: 'Educación', salud: 'Salud', corrupcion_investigaciones: 'Corrupción e investigaciones', congreso: 'Congreso', protesta_social: 'Protesta social', politica_exterior: 'Política exterior', anuncio_politica: 'Anuncios de política', obra_servicio: 'Obras y servicios' };
  const lab = c => CATS[c] || cap(String(c).replace(/_/g, ' '));
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
  const fixes = [
    'Cinco revisores adversariales (cifras, metodología, sesgo, QA y afirmaciones) atacaron la primera versión. Sus informes están en /review del repositorio.',
    'Día 100 = 4-nov (antes 5-nov, día 101). Cambiaron la Bolsa con Keiko (−1,9 %, no −4,0 %), con Castillo (+7,9 %) y los homicidios (+3,4 % y +1,9 %, ahora con ventanas de 100 días).',
    'Aprobación con la misma regla para todos (última medición antes del día 100). Antes se usaba para Castillo una encuesta del día ~107.',
    'Índice v2: la inversión se mide solo de agosto a octubre, la caída esperada de aprobación es proporcional, la escala de promesas sigue a PolitiFact, la veracidad queda fuera del total (solo se midió para Keiko) y se agregan rangos de incertidumbre. El «empate exacto» de la v1 (40,6 frente a 40,3) no era robusto: hoy decimos «no distinguibles».',
    'Se corrigió: los 9 cambios de ministro de Castillo (había cifras de 7, 8 y 9), que Castillo sí pidió facultades (28-oct-2021), que Pensión 65 a S/700 todavía no se había pagado al día 100, que el salario mínimo es un primer tramo y que hay 3 acciones de Keiko con norma parcial (antes decíamos «0 acreditadas con una norma»).',
    'Neutralidad: el título ya no es la cita del chat; Keiko ya no usa el naranja de su partido (que además coincidía con el «Malo» del semáforo); los conteos de integridad se ven en la tabla; se quitó una inferencia causal sobre el dólar; se sumaron hechos omitidos de ambos gobiernos.',
  ];
  $('#method').innerHTML = `<h3>Qué corregimos tras la revisión adversarial</h3><ul>${fixes.map(f => `<li>${esc(f)}</li>`).join('')}</ul><h3>Cómo se hizo</h3><ul>
    <li>Diez líneas de investigación paralelas, asistidas por IA, cada una con su propia fuente de verdad (archivos en <a href="https://github.com/unimauro/cien-dias-peru/tree/main/research" target="_blank" rel="noopener">/research</a>).</li>
    <li>Series macro tomadas directamente de la API del BCRPData, con el código de serie verificado contra su metadata. Resultados con datos de INEI, SINADEF/MINSA y MEF.</li>
    <li>Ventana: del 28 de julio (asunción) al 4 de noviembre (día 100, contando el 28-jul como día 1) de cada año. Cuando no hay dato ese día, se usa el último día hábil. Corregido tras la revisión adversarial: antes usábamos el 5-nov (día 101).</li>
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
    const growth = /var|crec|%/i.test((i.unidad || '') + ' ' + (i.nombre || '')) && i.deseado === 'sube' && b < a && b > 0;
    const st = growth ? ['▽', 'Crece menos', 'var(--muted)'] : better === null ? ['·', 'Contexto (sin dirección deseada)', 'var(--muted)'] : same ? ['=', 'Sin cambio', 'var(--muted)'] : better ? ['▲', 'Mejora', 'var(--ok-ink)'] : ['▼', 'Empeora', 'var(--bad-ink)'];
    return `<tr><td><span class="metric">${esc(i.nombre)}</span><br><small>${esc(i.unidad)}</small></td>
      <td class="n" data-tip="${esc(i.inicio.fuente || '')}">${fmtNum(a)}<br><small>${esc(i.inicio.periodo)}</small></td>
      <td class="n" data-tip="${esc(i.actual.fuente || '')}">${fmtNum(b)}<br><small>${esc(i.actual.periodo)}</small></td>
      <td><b style="color:${st[2]};font-family:Archivo">${st[0]} ${st[1]}</b>${i.nota ? `<br><small>${esc(i.nota)}</small>` : ''}<div class="srcs">${link(i.actual.url)}</div></td></tr>`;
  }).join('');
  box.innerHTML = `<h3 class="group-h">Brújula 2026 (solo Keiko): ¿el país está mejor o peor que el 28 de julio?</h3>
    <p class="note" style="margin-top:-6px">Indicadores oficiales al inicio del gobierno de Keiko Fujimori frente al último dato. «Mejora» o «empeora» según la dirección deseada de cada indicador; no implica que el cambio lo haya causado el gobierno. No existe una brújula equivalente para 2021. Fuente: ${link(D.pp2050_cumplimiento.meta.origen_url, 'Plan Perú 2050')}, corte ${esc(B.corte)}.</p>
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
  const RANGE = { 70: '≥70', 50: '50–69', 30: '30–49', 0: '<30' }, WIDTH = { 70: 30, 50: 20, 30: 20, 0: 30 };
  $('#semLegend').innerHTML = `<div class="ss-bar" role="img" aria-label="Escala del semáforo: ${[...BANDS].reverse().map(b => `${b[1]} ${RANGE[b[0]]}`).join(', ')}">${[...BANDS].reverse().map(b => `<span class="${b[2]}" style="flex:${WIDTH[b[0]]}"><b>${b[1]}</b><small>${esc(RANGE[b[0]])}</small></span>`).join('')}</div>
    <p class="ss-help">Cada celda va de 0 a 100: cuanto más a la derecha de la escala, mejor. <span class="ss-na"><i class="sem-na"></i>Sin dato</span></p>`;
  const I = D.indice100;
  if (!I) { $('#semIndice').innerHTML = '<p class="empty">Índice en preparación.</p>'; return; }
  const govs = ORDER.filter(k => I.gobiernos?.[k]);
  const head = `<thead><tr><th>Dimensión <small>(peso)</small></th>${govs.map(k => `<th class="n">${govLabel(k)}</th>`).join('')}</tr></thead>`;
  const rows = I.dimensiones.map(d => `<tr${d.peso ? '' : ' class="sem-info"'}><td><span class="metric">${esc(d.nombre)}</span> <small>(${d.peso ? d.peso + ' %' : 'fuera del total'})</small><br><small>${esc(d.desc)}</small></td>${govs.map(k => {
    const c = I.gobiernos[k].dims[d.id] || {};
    if (!isNum(c.score)) return `<td class="sem-cell sem-na" data-tip="${esc(GOV[k].short + ': ' + (c.valor || 'sin dato'))}"><span class="sl" style="font-size:12.5px;opacity:1">${esc(c.corto || 'sin dato')}</span></td>`;
    return semCell(c.score, Math.round(c.score), '', `${GOV[k].short}: ${c.valor || ''}${c.fuente ? ' · ' + c.fuente : ''}`);
  }).join('')}</tr>`).join('');
  const tot = `<tr class="sem-total"><td><span class="metric">Índice de los 100 días</span><br><small>Promedio ponderado del núcleo (promesas, cadena de valor, gabinete, confianza e inversión). Debajo, el rango del 5 % al 95 % de 20 000 simulaciones con otros pesos y fórmulas.</small></td>${govs.map(k => {
    const g = I.gobiernos[k];
    if (!isNum(g.total)) return `<td class="sem-cell sem-na" data-tip="Sin balance de promesas: no se calcula el total"><span class="sv">—</span><span class="sl">sin balance de promesas</span></td>`;
    const r = g.rango;
    return semCell(g.total, fmt(g.total, 1), r ? `rango ${fmt(r.p5, 0)}–${fmt(r.p95, 0)}` : '', `${GOV[k].short}: ${fmt(g.total)} / 100${r ? `; en el 90 % de las simulaciones queda entre ${fmt(r.p5)} y ${fmt(r.p95)}` : ''}`);
  }).join('')}</tr>
  <tr class="sem-total"><td><span class="metric">Núcleo común</span><br><small>Solo gabinete, confianza e inversión: las tres dimensiones que existen para los cinco gobiernos.</small></td>${govs.map(k => semCell(I.gobiernos[k].total_comun, fmt(I.gobiernos[k].total_comun, 1), '', `${GOV[k].short}: ${fmt(I.gobiernos[k].total_comun)} / 100 (gabinete, confianza e inversión)`)).join('')}</tr>`;
  const S = I.sensibilidad;
  const sensTxt = S ? `<p class="note"><b>¿Se pueden distinguir?</b> Castillo y Keiko, no: sus rangos se superponen (${fmt(S.castillo.p5, 0)}–${fmt(S.castillo.p95, 0)} frente a ${fmt(S.keiko.p5, 0)}–${fmt(S.keiko.p95, 0)}), y Castillo queda arriba solo en el ${Math.round(S.p_castillo_mayor_keiko * 100)} % de las simulaciones. Lo que sí se sostiene: PPK queda por encima de ambos en el ${Math.round(S.p_ppk_primero * 100)} % de las simulaciones.</p>` : '';
  $('#semIndice').innerHTML = `<div class="tbl-wrap"><table class="sem">${head}<tbody>${rows}${tot}</tbody></table></div>${sensTxt}`;
  const C = I.contexto || [];
  if (!$('#semIntl')) { /* resumen en Inicio */ }
  else if (C.length) {
    const cg = ORDER.filter(k => C.some(r => r.gobiernos?.[k]));
    const dimLab = { corrupcion: 'Corrupción', democracia: 'Democracia', estado_de_derecho: 'Estado de derecho', efectividad: 'Efectividad del gobierno', libertades: 'Libertades', desigualdad: 'Desigualdad', pobreza: 'Pobreza', desarrollo_humano: 'Desarrollo humano', confianza: 'Confianza ciudadana', seguridad: 'Seguridad' };
    const groups = [...new Set(C.map(r => r.dimension))];
    const body = groups.map(g => `<tr class="sem-grp"><td colspan="${cg.length + 1}">${esc(dimLab[g] || cap(g))}</td></tr>` + C.filter(r => r.dimension === g).map(r => `<tr><td><span class="metric">${esc(r.nombre)}</span><br><small>${esc(r.escala_txt || '')} · ${link(r.fuente_url, r.institucion || host(r.fuente_url))}</small></td>${cg.map(k => {
      const v = r.gobiernos[k]; if (!v) return semCell(null);
      const arrow = isNum(v.score_primer) && isNum(v.score_recibio) ? (Math.abs(v.score_primer - v.score_recibio) < 0.5 ? '=' : (v.score_primer > v.score_recibio ? '▲' : '▼')) : '';
      const sx = (val, y) => r.id === 'cpi_score' && y && +y < 2012 ? `${fmtSem(val)}<small>/10</small>` : fmtSem(val);
      const main = `${sx(v.recibio, v.anio_recibio)}${isNum(v.primer) ? ` → ${sx(v.primer, v.anio_primer)} <b class="arr">${arrow}</b>` : (k === 'keiko' ? ' <small>(base)</small>' : '')}`;
      return semCell(isNum(v.score_primer) ? v.score_primer : v.score_recibio, main, '', `${GOV[k].short}: ${v.anio_recibio || ''} = ${fmtSem(v.recibio)}${isNum(v.primer) ? `; ${v.anio_primer} = ${fmtSem(v.primer)}` : ' (primer año aún sin medición)'}`);
    }).join('')}</tr>`).join('')).join('');
    $('#semIntl').innerHTML = `<div class="tbl-wrap"><table class="sem">${`<thead><tr><th>Índice</th>${cg.map(k => `<th class="n">${govLabel(k)}</th>`).join('')}</tr></thead>`}<tbody>${body}</tbody></table></div><p class="note">El color corresponde al último valor de la celda, ubicado en su escala de 0 a 100 (mejor = 100). ▲ mejoró y ▼ empeoró en el primer año.</p>`;
  } else $('#semIntl').innerHTML = '<p class="empty">Índices internacionales en preparación.</p>';
  if (I.metodo && $('#semMetodo')) $('#semMetodo').innerHTML = `<details class="more" style="margin-top:20px"><summary>Cómo se calcula el índice</summary><ul class="sub-claims">${I.metodo.map(m => `<li>${esc(m)}</li>`).join('')}</ul></details>`;
}
const fmtSem = v => !isNum(v) ? '—' : Math.abs(v) < 1 ? fmt(v, 2) : Math.abs(v) < 10 ? fmt(v, 1) : fmt(v, 0);


/* ---------- semáforo: barras agrupadas por dimensión ---------- */
function renderDimBars() {
  const I = D.indice100, box = $('#semBars'); if (!I) { box.innerHTML = ''; return; }
  const ks = ['castillo', 'keiko', 'ppk'].filter(k => I.gobiernos?.[k]);
  const dims = I.dimensiones.filter(d => d.peso && ks.some(k => isNum(I.gobiernos[k].dims?.[d.id]?.score)));
  box.innerHTML = `<div class="legend">${ks.map(k => `<span>${govLabel(k)}${k === 'ppk' ? '<small class="muted" style="margin-left:5px">(referencia)</small>' : ''}</span>`).join('')}</div>
    <div class="dimbars" role="img" aria-label="Puntaje por dimensión del índice, de 0 a 100: ${dims.map(d => `${d.nombre}: ${ks.map(k => `${GOV[k].short} ${fmt(I.gobiernos[k].dims[d.id]?.score, 0)}`).join(', ')}`).join('; ')}">
    ${dims.map(d => `<div class="db-dim"><p class="db-name">${esc(d.nombre)} <small>${d.peso} %</small></p>
      ${ks.map(k => { const c = I.gobiernos[k].dims[d.id] || {}, v = c.score, b = band(v);
        return `<div class="db-row${k === 'ppk' ? ' ref' : ''}" data-tip="${esc(`${GOV[k].short} ${GOV[k].year}: ${isNum(v) ? fmt(v, 0) + ' / 100' : 'sin dato'}${c.valor ? ' (' + c.valor + ')' : ''}`)}">
          <span class="db-g">${esc(GOV[k].short)}</span>
          <span class="db-track"><span class="db-bar" style="width:${isNum(v) ? Math.max(1.5, Math.min(100, v)) : 0}%;--c:var(${GOV[k].v})"></span></span>
          <span class="db-v num">${isNum(v) ? fmt(v, 0) : '—'}${b ? `<i class="db-b ${b[2]}" title="${b[1]}"></i>` : ''}</span></div>`; }).join('')}
    </div>`).join('')}</div>
    <p class="note">Barras de 0 a 100 por dimensión; el cuadradito de color indica la banda del semáforo. Pasa el cursor o toca una barra para ver el dato de origen.</p>`;
}

/* ---------- promesas: waffle de las listas oficiales ---------- */
function renderWaffle() {
  const B = D.promesas_base?.balances_oficiales, box = $('#waffle'); if (!B) { box.innerHTML = ''; return; }
  const mk = (k, parts) => {
    const b = B[k]; const cells = parts.flatMap(([n, cls]) => Array.from({ length: n || 0 }, () => cls));
    return `<figure class="waf"><figcaption>${govLabel(k)} <span class="muted">${esc(b.fuente)}: ${b.total}</span></figcaption>
      <div class="waf-grid" role="img" aria-label="${esc(GOV[k].short)}: ${parts.map(([n, , l]) => `${n} ${l}`).join(', ')} de ${b.total}">${cells.map(c => `<i class="${c}"></i>`).join('')}</div>
      <div class="legend waf-leg">${parts.filter(p => p[0] > 0 || p[3]).map(([n, cls, l]) => `<span><i class="wl ${cls}"></i>${esc(l)}: <b class="num">${n}</b></span>`).join('')}</div></figure>`;
  };
  box.innerHTML = `<div class="waf-wrap">
    ${B.castillo ? mk('castillo', [[B.castillo.cumplidas, 'c', 'Cumplidas', 1], [B.castillo.en_proceso, 'p', 'En proceso'], [B.castillo.incumplidas, 'n', 'Incumplidas']]) : ''}
    ${B.keiko ? mk('keiko', [[B.keiko.cumplidas, 'c', 'Cumplidas', 1], [B.keiko.en_proceso, 'p', 'En proceso'], [B.keiko.sin_avance, 'n', 'Sin avance']]) : ''}
  </div><p class="note">Un cuadro por promesa o acción, según cada balance. Las dos listas no son homogéneas: miden cosas distintas con criterios distintos.</p>`;
}

/* ---------- base de promesas ---------- */
const EST = {
  cumplida: { c: 'var(--sem-g)', ic: '✓' }, parcial: { c: '#7fb041', ic: '◐' }, en_proceso: { c: 'var(--sem-y)', ic: '…' },
  anunciada: { c: 'var(--sem-o)', ic: '!' }, sin_evidencia: { c: 'var(--unk)', ic: '∅' }, incumplida: { c: 'var(--sem-r)', ic: '✕' }, no_verificable: { c: 'var(--rule-strong)', ic: '?' },
};
const NIV = ['insumo', 'actividad', 'producto', 'resultado', 'impacto'];
function renderBalances() {
  const P = D.promesas_base, box = $('#pbBalances'); if (!P) { box.innerHTML = ''; return; }
  const B = P.balances_oficiales || {};
  const row = (k, b) => {
    const items = [['cumplidas', 'cumplidas'], ['en_proceso', 'en proceso'], ['incumplidas', 'incumplidas'], ['sin_avance', 'sin avance']].filter(([f]) => isNum(b[f]));
    return `<article class="bal" style="--c:var(${GOV[k].v})"><h3>${govLabel(k)}</h3><p class="bal-src">${esc(b.fuente)}</p>
      <p class="bal-big"><b class="num">${isNum(b.cumplidas) ? b.cumplidas : '—'}</b><span>de <b class="num">${b.total}</b> cumplidas</span></p>
      <p class="bal-parts">${items.slice(1).map(([f, l]) => `<span><b class="num">${b[f]}</b> ${l}</span>`).join('')}</p>
      ${b.nota ? `<p class="bal-note">${esc(b.nota)}</p>` : ''}</article>`;
  };
  box.innerHTML = `<h3 class="group-h">Los balances oficiales</h3><div class="bal-grid">${['castillo', 'keiko', 'ppk'].filter(k => B[k]).map(k => row(k, B[k])).join('')}</div>
    ${(P.caveats || []).length ? `<ul class="pb-cav">${P.caveats.map(c => `<li>${esc(c)}</li>`).join('')}</ul>` : ''}`;
}
function renderBase() {
  const P = D.promesas_base, box = $('#pbApp'); if (!P) { box.innerHTML = '<p class="empty">No se pudo cargar la base de promesas.</p>'; return; }
  const fixedGov = box.dataset.gov || '';
  const ALL = (P.promesas || []).filter(r => !fixedGov || r.gobierno === fixedGov);
  const ESTL = P.estados || {};
  const st = { q: '', gov: '', est: '', niv: '', all: false };
  const govs = ORDER.filter(k => ALL.some(r => r.gobierno === k));
  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const match = (r, skip) => (skip === 'gov' || !st.gov || r.gobierno === st.gov) && (skip === 'est' || !st.est || r.estado === st.est) &&
    (skip === 'niv' || !st.niv || (st.niv === 'sin' ? !r.nivel : r.nivel === st.niv)) &&
    (!st.q || norm([r.texto, r.nota, r.eje, r.codigo, r.lista, r.estado_fuente].join(' ')).includes(norm(st.q)));
  const chip = e => `<span class="est est-${esc(e)}" style="--e:${EST[e]?.c || 'var(--unk)'}"><i aria-hidden="true">${EST[e]?.ic || '·'}</i>${esc(ESTL[e] || e)}</span>`;
  box.innerHTML = `<div class="pb-ctrl" role="search">
      <label class="pb-q"><span class="sr">Buscar en las promesas</span><input type="search" id="pbQ" placeholder="Buscar: salario, Pensión 65, C5i…" autocomplete="off"></label>
      ${fixedGov ? '' : `<div class="seg pb-gov" role="group" aria-label="Gobierno"><button type="button" data-g="" aria-pressed="true">Todos</button>${govs.map(k => `<button type="button" data-g="${k}" aria-pressed="false">${govLabel(k)}</button>`).join('')}</div>`}
      <label class="pb-sel"><span>Nivel en la cadena de valor</span><select id="pbNiv"><option value="">Todos los niveles</option>${NIV.map(n => `<option value="${n}">${cap(n)}</option>`).join('')}<option value="sin">Sin clasificar</option></select></label>
    </div>
    <div class="pb-stack" id="pbStack"></div>
    <div class="pb-counts" id="pbCounts" role="group" aria-label="Filtrar por estado"></div>
    <div class="pb-bar"><p id="pbN" class="pb-n" aria-live="polite"></p><div class="pb-actions"><button type="button" class="btn-sm" id="pbReset">Limpiar filtros</button><button type="button" class="btn-sm btn-sm-main" id="pbCsv"><span class="dl-ic" aria-hidden="true"></span>Descargar CSV</button></div></div>
    <div class="pb-head" aria-hidden="true"><span>Gobierno</span><span>Promesa</span><span>Estado</span><span>Nivel</span></div>
    <ul class="pb-list" id="pbList"></ul>`;
  const push = () => { try { (window.dataLayer = window.dataLayer || []).push({ event: 'filtro_promesas', gobierno: st.gov || fixedGov, estado: st.est, nivel: st.niv, busqueda: st.q ? 1 : 0 }); } catch {} };
  const draw = () => {
    const rows = ALL.filter(r => match(r));
    const base = ALL.filter(r => match(r, 'est'));
    const estOrder = Object.keys(ESTL).filter(e => ALL.some(r => r.estado === e));
    const cnt = e => base.filter(r => r.estado === e).length;
    $('#pbCounts').innerHTML = estOrder.map(e => `<button type="button" class="pb-c" data-e="${esc(e)}" aria-pressed="${st.est === e}" style="--e:${EST[e]?.c || 'var(--unk)'}"><i aria-hidden="true">${EST[e]?.ic || '·'}</i><span>${esc(ESTL[e] || e)}</span><b class="num">${cnt(e)}</b></button>`).join('');
    const tot = base.length || 1;
    $('#pbStack').innerHTML = `<div class="pb-stk" role="img" aria-label="Por estado: ${estOrder.map(e => `${ESTL[e] || e} ${cnt(e)}`).join(', ')}">${estOrder.filter(cnt).map(e => `<span style="flex:${cnt(e)};--e:${EST[e]?.c}" data-tip="${esc(`${ESTL[e] || e}: ${cnt(e)} de ${base.length} (${fmt(cnt(e) / tot * 100, 0)} %)`)}"></span>`).join('')}</div>`;
    $('#pbN').innerHTML = `Mostrando <b class="num">${rows.length}</b> de <b class="num">${ALL.length}</b> promesas`;
    const LIM = 30, show = st.all ? rows : rows.slice(0, LIM);
    $('#pbList').innerHTML = show.map(r => `<li class="pb-item" style="--c:var(${GOV[r.gobierno]?.v || '--muted'})">
        <span class="pb-gv">${GOV[r.gobierno] ? govLabel(r.gobierno) : esc(r.gobierno)}${r.codigo ? ` <small class="num">${esc(r.codigo)}</small>` : ''}</span>
        <div class="pb-tx"><p>${esc(r.texto)}</p><small>${esc(r.eje ? r.eje + '. ' : '')}${esc(r.lista)}</small>
          <details class="more pb-more"><summary>Nota y fuentes</summary><p class="pb-note">${esc(r.nota)}</p>${r.estado_fuente ? `<p class="pb-note"><b>Estado según la fuente:</b> ${esc(r.estado_fuente)}</p>` : ''}<div class="srcs">${(r.fuentes || []).map(u => link(u)).join('')}</div></details></div>
        <span class="pb-es">${chip(r.estado)}</span>
        <span class="pb-nv">${r.nivel ? `<span class="lvl ${['resultado', 'impacto'].includes(r.nivel) ? 'hi' : ''}">${esc(r.nivel)}</span>` : '<span class="muted small">sin clasificar</span>'}</span>
      </li>`).join('') + (rows.length > show.length ? `<li class="pb-morebtn"><button type="button" class="btn btn-ghost" id="pbAll">Mostrar las ${rows.length} promesas</button></li>` : '') ||
      '<li class="empty">Ninguna promesa coincide con estos filtros. Prueba con otra búsqueda o limpia los filtros.</li>';
    const all = $('#pbAll'); if (all) all.onclick = () => { st.all = true; draw(); };
  };
  let qT;
  $('#pbQ').addEventListener('input', e => { st.q = e.target.value.trim(); st.all = false; clearTimeout(qT); qT = setTimeout(() => { draw(); push(); }, 160); });
  $('#pbNiv').addEventListener('change', e => { st.niv = e.target.value; st.all = false; draw(); push(); });
  const gseg = box.querySelector('.pb-gov');
  if (gseg) gseg.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; st.gov = b.dataset.g; st.all = false;
    gseg.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); draw(); push(); });
  $('#pbCounts').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; st.est = st.est === b.dataset.e ? '' : b.dataset.e; st.all = false; draw(); push(); });
  $('#pbReset').addEventListener('click', () => { Object.assign(st, { q: '', gov: '', est: '', niv: '', all: false }); $('#pbQ').value = ''; $('#pbNiv').value = '';
    if (gseg) gseg.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(!x.dataset.g))); draw(); });
  $('#pbCsv').addEventListener('click', () => {
    const rows = ALL.filter(r => match(r));
    const cols = ['id', 'gobierno', 'lista', 'codigo', 'eje', 'texto', 'estado', 'estado_fuente', 'nivel', 'nota', 'fuentes'];
    const cell = v => { let t = Array.isArray(v) ? v.join(' | ') : String(v ?? ''); if (/^[=+\-@\t\r]/.test(t)) t = "'" + t; return '"' + t.replace(/"/g, '""') + '"'; };
    const csv = '﻿' + [cols.join(','), ...rows.map(r => cols.map(c => cell(r[c])).join(','))].join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = `promesas-100-dias${fixedGov ? '-' + fixedGov : ''}${st.gov ? '-' + st.gov : ''}.csv`;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    try { (window.dataLayer = window.dataLayer || []).push({ event: 'descarga_csv_promesas', filas: rows.length }); } catch {}
  });
  draw();
}

/* ---------- gráficos de línea en SVG (sin dependencias) ---------- */
function lineChart({ series, xMin, xMax, yMin, yMax, xTicks, yTicks, xFmt, yFmt, shade, mark, h = 260, label, w = 680 }) {
  const W = Math.max(300, Math.min(820, Math.round(w))), pad = { l: 40, r: W < 420 ? 30 : 16, t: 14, b: 30 }, H = W < 420 ? Math.round(h * .9) : h;
  const x = v => pad.l + (W - pad.l - pad.r) * (v - xMin) / (xMax - xMin);
  const y = v => pad.t + (H - pad.t - pad.b) * (1 - (v - yMin) / (yMax - yMin));
  let g = '';
  if (shade) g += `<rect x="${x(shade[0])}" y="${pad.t}" width="${x(shade[1]) - x(shade[0])}" height="${H - pad.t - pad.b}" style="fill:var(--sunk)"/><text x="${x(shade[0]) + 6}" y="${pad.t + 14}" font-size="11.5" font-family="Archivo" style="fill:var(--muted)">${esc(shade[2] || '')}</text>`;
  g += yTicks.map(v => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${y(v)}" y2="${y(v)}" style="stroke:var(--rule)"/><text x="${pad.l - 6}" y="${y(v) + 4}" text-anchor="end" font-size="11.5" font-family="Archivo" style="fill:var(--muted)">${yFmt(v)}</text>`).join('');
  g += xTicks.map(v => `<text x="${x(v)}" y="${H - 9}" text-anchor="middle" font-size="11.5" font-family="Archivo" style="fill:var(--muted)">${xFmt(v)}</text>`).join('');
  if (mark) g += `<line x1="${x(mark[0])}" x2="${x(mark[0])}" y1="${pad.t}" y2="${H - pad.b}" style="stroke:var(--ink-2)" stroke-dasharray="4 3"/><text x="${x(mark[0]) - 5}" y="${pad.t + 14}" text-anchor="end" font-size="11.5" font-family="Archivo" font-weight="700" style="fill:var(--ink-2)">${esc(mark[1])}</text>`;
  series.forEach(s => {
    const pts = s.pts.filter(p => isNum(p[0]) && isNum(p[1]));
    if (!pts.length) return;
    g += `<polyline fill="none" points="${pts.map(p => `${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ')}" style="stroke:var(${s.v})" stroke-width="${s.w || 2.5}" stroke-linejoin="round" stroke-linecap="round"${s.dash ? ' stroke-dasharray="5 4"' : ''}/>`;
    g += pts.map(p => `<circle cx="${x(p[0])}" cy="${y(p[1])}" r="${s.r || 4.5}" style="fill:var(${s.v});stroke:var(--surface)" stroke-width="2"/><circle cx="${x(p[0])}" cy="${y(p[1])}" r="14" fill="transparent" data-tip="${esc(p[2] || '')}"/>`).join('');
    const last = pts[pts.length - 1];
    if (s.label) g += `<text x="${Math.min(x(last[0]) + 8, W - pad.r)}" y="${y(last[1]) + 4}" ${x(last[0]) + 60 > W ? 'text-anchor="end" dy="-12"' : ''} font-size="12.5" font-weight="700" font-family="Archivo" style="fill:var(--ink)">${esc(s.label)}</text>`;
  });
  return `<svg class="lc" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}
const dayOf = (k, f) => {
  const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(String(f || '')); if (!m) return null;
  return (Date.UTC(+m[1], +m[2] - 1, m[3] ? +m[3] : 15) - Date.UTC(GOV[k].year, 6, 28)) / 864e5;
};
function renderApSeries() {
  const box = $('#apSeries'); if (!box) return;
  const get = k => (k === 'castillo' ? D.castillo?.aprobacion : k === 'keiko' ? D.keiko?.aprobacion : hist(k)?.aprobacion) || [];
  const series = ORDER.map(k => {
    const arr = get(k).filter(a => /ipsos|apoyo/i.test(a.encuestadora || '') && isNum(+a.aprueba) && a.aprueba !== null && a.aprueba !== '');
    const pts = arr.map(a => [dayOf(k, a.fecha || a.campo), +a.aprueba, `${GOV[k].short} ${GOV[k].year}: ${a.aprueba} % (${a.encuestadora}, ${a.fecha || a.campo || ''})`]).filter(p => isNum(p[0]) && p[0] >= -20 && p[0] <= 140).sort((a, b) => a[0] - b[0]);
    return { k, v: GOV[k].v, pts, w: ['castillo', 'keiko'].includes(k) ? 3 : 1.6, r: ['castillo', 'keiko'].includes(k) ? 5 : 3.5, label: `${GOV[k].short}` };
  }).filter(s => s.pts.length >= 2);
  if (!series.length) { box.innerHTML = ''; return; }
  box.innerHTML = `<h3>Aprobación en el tiempo (Ipsos/Apoyo)</h3><p class="sub">Porcentaje que aprueba, por días desde la asunción (28 de julio). Las mediciones mensuales sin día exacto se ubican a mitad de mes.</p>
    ${lineChart({ w: box.clientWidth, series, xMin: 0, xMax: 130, yMin: 20, yMax: 70, xTicks: [0, 25, 50, 75, 100, 125], yTicks: [20, 30, 40, 50, 60, 70], xFmt: v => `día ${v}`, yFmt: v => v + '%', mark: [100, 'día 100'], label: 'Aprobación presidencial (Ipsos/Apoyo) por días desde la asunción: ' + series.map(s => `${GOV[s.k].short}: ${s.pts.map(p => fmt(p[1], 0) + ' %').join(', ')}`).join('; ') })}
    <div class="legend">${series.map(s => `<span>${govLabel(s.k)}</span>`).join('')}</div>`;
}
function renderHomSeries() {
  const box = $('#homSeries'); const R = D.resultados; if (!box || !R) return;
  const it = (R.indicadores || []).find(i => i.id === 'homicidios_sinadef'); if (!it) { box.innerHTML = ''; return; }
  const corte = (/corte (\d{4})-(\d{2})-(\d{2})/.exec(it.fuente || '') || []);
  const ser = (y, k) => (it[y]?.serie || []).filter(([f]) => !(corte[1] && f >= `${corte[1]}-${corte[2]}`)).map(([f, v]) => [+f.slice(5, 7), +v, `${GOV[k].short} ${y}, ${MES[+f.slice(5, 7) - 1]}: ${fmtInt(v)} homicidios`]);
  const s21 = ser('2021', 'castillo'), s26 = ser('2026', 'keiko');
  const vals = [...s21, ...s26].map(p => p[1]); if (!vals.length) { box.innerHTML = ''; return; }
  const yMax = Math.ceil(Math.max(...vals) / 20) * 20 + 10, yMin = Math.max(0, Math.floor(Math.min(...vals) / 20) * 20 - 10);
  const step = (yMax - yMin) > 100 ? 40 : 20, yt = []; for (let v = yMin; v <= yMax; v += step) yt.push(v);
  box.innerHTML = `<div class="chart"><h3>Homicidios por mes (SINADEF)</h3><p class="sub">Defunciones por homicidio registradas cada mes en 2021 y en 2026. La franja marca agosto a octubre, el grueso de cada ventana de 100 días.${corte[1] ? ` Se omite ${MES[+corte[2] - 1]} de ${corte[1]}: la fuente tiene corte al ${+corte[3]} de ese mes.` : ''}</p>
    ${lineChart({ w: box.clientWidth, series: [{ k: 'castillo', v: '--castillo', pts: s21, label: '2021' }, { k: 'keiko', v: '--keiko', pts: s26, label: '2026' }], xMin: 1, xMax: 12, yMin, yMax, xTicks: [1, 3, 5, 7, 9, 11], yTicks: yt, xFmt: v => MES[v - 1], yFmt: v => fmtInt(v), shade: [7.9, 10.1, 'ago–oct'], label: `Homicidios mensuales SINADEF. 2021: ${s21.map(p => p[1]).join(', ')}. 2026: ${s26.map(p => p[1]).join(', ')}.` })}
    <div class="legend"><span>${govLabel('castillo')}</span><span>${govLabel('keiko')}</span></div></div>`;
}

/* ---------- línea de tiempo: densidad de hechos ---------- */
function renderTlDensity() {
  const N = D.noticias, box = $('#tlDensity'); if (!N) { box.innerHTML = ''; return; }
  const row = k => {
    const items = (N[k] || []).filter(i => isNum(+i.dia_n));
    const bins = Array.from({ length: 10 }, () => []);
    items.forEach(i => bins[Math.min(9, Math.max(0, Math.floor((+i.dia_n - 1) / 10)))].push(i));
    const tc = t => t === 'positivo' ? 'pos' : t === 'negativo' ? 'neg' : 'neu';
    return `<div class="dens-row"><p class="dens-g">${govLabel(k)} <small class="muted">${items.length} hechos</small></p>
      <div class="dens-bins">${bins.map((b, j) => `<div class="dens-bin" data-tip="${esc(`${GOV[k].short}, días ${j * 10 + 1}–${j * 10 + 10}: ${b.length} hechos (${b.filter(i => i.tono === 'positivo').length} positivos, ${b.filter(i => i.tono === 'negativo').length} negativos)`)}">${b.sort((a, c) => tc(a.tono).localeCompare(tc(c.tono))).map(i => `<i class="${tc(i.tono)}"></i>`).join('')}</div>`).join('')}</div></div>`;
  };
  box.innerHTML = `<div class="dens" role="img" aria-label="Número de hechos por tramo de 10 días en cada ventana de 100 días">${row('castillo')}${row('keiko')}
    <div class="dens-axis"><span></span><div>${[1, 25, 50, 75, 100].map(v => `<span style="left:${(v - 1) / 99 * 100}%">día ${v}</span>`).join('')}</div></div></div>
    <div class="legend"><span><i class="tone-k pos"></i>Hecho positivo</span><span><i class="tone-k neg"></i>Hecho negativo</span><span><i class="tone-k neu"></i>Neutro</span></div>`;
}

/* ---------- ficha por gobierno ---------- */
function renderGovPage() {
  let k = new URLSearchParams(location.search).get('g'); if (!GOV[k]) k = 'keiko';
  const G = GOV[k], I = D.indice100;
  document.title = `${G.name} ${G.year}: ficha de los 100 días | 100 días bajo la lupa`;
  document.documentElement.style.setProperty('--gov', `var(${G.v})`);
  $('#govTitle').textContent = `${G.name}, ${G.year}`;
  document.querySelectorAll('.gov-switch a').forEach(a => { if (a.dataset.g === k) a.setAttribute('aria-current', 'page'); });
  const pdf = { keiko: 'keiko-2026', castillo: 'castillo-2021', ppk: 'ppk-2016', humala: 'humala-2011', garcia: 'garcia-2006' }[k];
  const g = I?.gobiernos?.[k];
  $('#govIntro').innerHTML = `<div class="gov-kpis">
      <div class="gk"><b class="num"${isNum(g?.total) ? ` data-count="${g.total}" data-dec="1"` : ''}>${isNum(g?.total) ? fmt(g.total) : '—'}</b><span>Índice de los 100 días${g?.rango ? ` (rango ${fmt(g.rango.p5, 0)}–${fmt(g.rango.p95, 0)})` : isNum(g?.total) ? '' : ': sin balance de promesas'}</span></div>
      <div class="gk"><b class="num"${isNum(g?.total_comun) ? ` data-count="${g.total_comun}" data-dec="1"` : ''}>${isNum(g?.total_comun) ? fmt(g.total_comun) : '—'}</b><span>Núcleo común (gabinete, confianza e inversión)</span></div>
    </div>
    <p class="cta"><a class="btn btn-main" href="pdf/${pdf}.pdf" download><span class="dl-ic" aria-hidden="true"></span>Descargar la ficha en PDF</a></p>`;
  const pb = $('#pbApp'); if (pb) pb.dataset.gov = k;
  if (I && g) {
    $('#govSem').innerHTML = `<div class="gs-grid">${I.dimensiones.map(d => { const c = g.dims?.[d.id] || {}, v = c.score, b = band(v);
      return `<div class="gs ${b ? b[2] : 'sem-na'}${d.peso ? '' : ' gs-info'}"><p class="gs-n">${esc(d.nombre)} <small>${d.peso ? d.peso + ' %' : 'fuera del total'}</small></p>
        <p class="gs-v num">${isNum(v) ? Math.round(v) : esc(c.corto || '—')}</p><p class="gs-b">${b ? b[1] : 'sin puntaje'}</p>${c.valor ? `<p class="gs-d">${esc(c.valor)}</p>` : ''}</div>`; }).join('')}</div>`;
  } else $('#govSem').innerHTML = '<p class="empty">Sin datos del índice.</p>';
  const f = govFacts(k), ap = approvals(k);
  const rows = [['Premier inicial', 'premier'], ['Voto de confianza o investidura', 'confianza'], ['Cambios de gabinete en 100 días', 'cambios'], ['Facultades y normas', 'facultades']];
  $('#govCab').innerHTML = `<dl class="cab">${rows.map(([l, key]) => `<div><dt>${l}</dt><dd>${esc(f[key])}${f.u[key] ? `<span class="srcs">${link(f.u[key])}</span>` : ''}</dd></div>`).join('')}
    ${ap ? `<div><dt>Aprobación (${esc(ap.first.encuestadora)})</dt><dd><b class="num">${ap.first.aprueba} → ${ap.last.aprueba} %</b>: primera medición frente a la última antes del día 100</dd></div>` : ''}</dl>`;
  const N = D.noticias?.[k] || [], V = (k === 'castillo' || k === 'keiko') ? D.videos?.[k] : D.videos?.historicos?.[k];
  const hitos = N.slice().sort((a, b) => (a.dia_n ?? 0) - (b.dia_n ?? 0)).map(i => `<div class="tl-item"><div class="tl-day" style="color:var(${G.v})">${esc(i.dia_n ?? '')}<small>${esc(fmtDate(i.fecha))}</small></div><div><h4>${esc(i.titulo)}</h4><p>${esc(i.resumen)}</p><div class="tl-meta"><span class="tone ${esc(i.tono)}">${esc(i.tono)}</span>${(i.fuentes || []).map(u => link(u)).join('')}</div></div></div>`).join('');
  const vids = (V || []).map(v => `<a class="vid" href="${esc(safeUrl(v.url))}" target="_blank" rel="noopener"><div class="thumb">${v.plataforma === 'youtube' ? `<img loading="lazy" src="https://i.ytimg.com/vi/${encodeURIComponent(v.id)}/hqdefault.jpg" alt="">` : ''}</div><h4>${esc(v.titulo_oembed)}</h4><div class="vm">${esc(v.canal_oembed)}</div></a>`).join('');
  $('#govHitos').innerHTML = (hitos ? `<h3 class="group-h">Hitos de la ventana</h3><div class="gov-tl">${hitos}</div>` : '<p class="note">No armamos una línea de tiempo para este gobierno: solo la hay para Castillo y Keiko.</p>') +
    (vids ? `<h3 class="group-h">Videos</h3><div class="vids">${vids}</div>` : '');
  if (pb) renderBase();
}

})();
