/* chat.js — «Pregúntale a los datos»: asistente IA de 100 días bajo la lupa.
 * Se monta solo: <link rel="stylesheet" href="chat.css"> + <script src="chat.js" defer></script>.
 * Llama a https://api.tunky.net/cien/chat. Si el backend no responde, cae a un modo sin IA que busca
 * en data/chat.json por palabras clave y muestra los fragmentos con sus fuentes. Nunca usa innerHTML.
 * API opcional: window.CienChat.open(), .close(), .ask("pregunta"). Abre solo con el hash #preguntar.
 * El endpoint se puede cambiar con data-endpoint en el <script> o window.CIEN_CHAT_ENDPOINT.
 */
(function () {
  "use strict";
  if (window.CienChat) return;
  var script = document.currentScript;
  var ENDPOINT = window.CIEN_CHAT_ENDPOINT || (script && script.getAttribute("data-endpoint")) || "https://api.tunky.net/cien/chat";
  var DATOS = new URL("data/chat.json", (script && script.src) || location.href).href;
  var SUGERENCIAS = [
    "¿Quién lo hizo peor en sus 100 días, Keiko o Castillo?",
    "¿Cuántos cambios de ministros hubo en cada gobierno?",
    "¿Es cierto lo de los colegios destruidos?",
    "¿Cómo cambió la aprobación de Keiko frente a la de Castillo?",
  ];
  var AVISO = "Responde con los datos del sitio; puede equivocarse. Verifica las fuentes.";
  var MAX_Q = 400;

  // ---------- utilidades DOM (sin innerHTML) ----------
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "class") n.className = attrs[k];
      else if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  var norm = function (t) { return String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var dominio = function (u) { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (e) { return "fuente"; } };
  var seguro = function (u) { try { var x = new URL(u, location.href); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  function enlace(href, texto) {
    var h = seguro(href);
    if (!h) return document.createTextNode(texto);
    return el("a", { href: h, target: "_blank", rel: "noopener noreferrer", text: texto });
  }

  // Renderer mínimo y seguro: **negritas**, listas («- », «• », «* », «1. »), [texto](url) y URLs sueltas.
  function inline(texto) {
    var frag = document.createDocumentFragment();
    var re = /\*\*([^*]+)\*\*|\[([^\]]{1,200})\]\((https?:\/\/[^\s)]+)\)|(https?:\/\/[^\s<>()«»"]+[^\s<>()«»".,;:!?])/g;
    var i = 0, m;
    while ((m = re.exec(texto))) {
      if (m.index > i) frag.appendChild(document.createTextNode(texto.slice(i, m.index)));
      if (m[1]) frag.appendChild(el("strong", { text: m[1] }));
      else if (m[2]) frag.appendChild(enlace(m[3], m[2]));
      else frag.appendChild(enlace(m[4], dominio(m[4])));
      i = re.lastIndex;
    }
    if (i < texto.length) frag.appendChild(document.createTextNode(texto.slice(i)));
    return frag;
  }
  function render(texto) {
    var cont = el("div", { class: "cc-md" }), lista = null;
    String(texto).replace(/\r/g, "").split("\n").forEach(function (lin) {
      lin = lin.replace(/^\s*#{1,6}\s*/, "");
      var li = lin.match(/^\s*(?:[-•*]|\d{1,2}[.)])\s+(.*)$/);
      if (li) {
        if (!lista) { lista = el("ul"); cont.appendChild(lista); }
        lista.appendChild(el("li", null, [inline(li[1])]));
      } else if (lin.trim()) {
        lista = null;
        cont.appendChild(el("p", null, [inline(lin.trim())]));
      } else lista = null;
    });
    return cont;
  }

  // ---------- modo sin IA: búsqueda local en data/chat.json ----------
  var datosP = null;
  function cargarDatos() {
    if (!datosP) datosP = fetch(DATOS, { cache: "no-cache" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var F = d.fuentes || [];
        d.fragmentos = (d.fragmentos || []).map(function (f) {
          f.u = (f.u || []).map(function (i) { return typeof i === "number" ? F[i] : i; }).filter(Boolean);
          f._t = norm(f.t + " " + (f.tags || []).join(" ") + " " + f.sec); f._x = norm(f.x); return f;
        });
        return d;
      }).catch(function (e) { datosP = null; throw e; });
    return datosP;
  }
  var STOP = {};
  ("de la el los las y o a en que con por para del un una se su sus es al lo como mas sobre hay cual cuales me mi te tu le les esta este " +
    "estas estos quien quienes cuanto cuantos cuantas algo dime quiero saber hola gracias dias dia cien gobierno gobiernos fue era hizo tuvo tiene cierto verdad")
    .split(" ").forEach(function (w) { STOP[w] = 1; });
  var GOBS = { keiko: ["keiko", "fujimori", "2026"], castillo: ["castillo", "2021"], ppk: ["ppk", "kuczynski", "2016"], humala: ["humala", "ollanta", "2011"], garcia: ["garcia", "alan", "2006"] };
  var SIN = { ministros: ["gabinete"], ministro: ["gabinete"], premier: ["gabinete"], encuesta: ["aprobacion"], encuestas: ["aprobacion"], popularidad: ["aprobacion"],
    dolar: ["cambio"], bolsa: ["bursatil"], economia: ["mercados"], promesa: ["promesas"], cumplio: ["promesas", "cumplidas"], destruidos: ["colegio"], colegios: ["colegio"],
    peor: ["conclusion", "indice"], mejor: ["conclusion", "indice"], crimen: ["homicidios"], inseguridad: ["homicidios"], discurso: ["mensaje"], plan: ["planes"], inversion: ["ejecucion"] };
  function buscar(d, q) {
    var nq = norm(q), nombres = {};
    var gob = Object.keys(GOBS).filter(function (g) { return GOBS[g].some(function (w) { nombres[w] = 1; return nq.indexOf(w) >= 0; }); });
    var ws = [];
    nq.split(/[^a-z0-9ñ]+/).forEach(function (w) {
      if (w.length < 3 || STOP[w] || nombres[w]) return;
      [w].concat(SIN[w] || []).forEach(function (x) { x = x.length > 5 ? x.slice(0, -2) : x; if (ws.indexOf(x) < 0) ws.push(x); });
    });
    var comp = /compar|mejor|peor|ranking|indice|conclusi|los dos|ambos/.test(nq);
    return d.fragmentos.map(function (f) {
      var p = ws.reduce(function (n, w) { return n + (f._t.indexOf(w) >= 0 ? 5 : 0) + (f._x.indexOf(w) >= 0 ? 2 : 0); }, 0);
      if (p && gob.length && (f.gob || []).length) p += f.gob.some(function (g) { return gob.indexOf(g) >= 0; }) ? 4 : -8;
      if (p && /cumpli/.test(nq) && /-(cumplida|parcial)$/.test(f.id)) p += 6;
      if (comp && (f.sec === "conclusion" || f.id === "indice-resumen")) p += 6;
      return { f: f, p: p };
    }).filter(function (x) { return x.p >= 4; }).sort(function (a, b) { return b.p - a.p; }).slice(0, 4).map(function (x) { return x.f; });
  }
  function respuestaLocal(q) {
    return cargarDatos().then(function (d) {
      var r = buscar(d, q), box = el("div", { class: "cc-md" });
      box.appendChild(el("p", { class: "cc-modo" }, [el("strong", { text: "Modo sin IA:" }), " estos son los datos relacionados."]));
      if (!r.length) {
        box.appendChild(el("p", null, ["No encontré datos sobre eso. Prueba con otras palabras (por ejemplo «ministros», «aprobación», «promesas», «dólar» o «colegios») o revisa ",
          enlace(d.sitio || "./", "el sitio"), "."]));
        return box;
      }
      r.forEach(function (f) {
        var corto = f.x.length > 320 ? f.x.slice(0, 319).replace(/\s+\S*$/, "") + "…" : f.x;
        var src = el("span", { class: "cc-src" }, ["Fuente: "]);
        f.u.slice(0, 2).forEach(function (u, i) { if (i) src.appendChild(document.createTextNode(" · ")); src.appendChild(enlace(u, dominio(u))); });
        box.appendChild(el("div", { class: "cc-frag" }, [el("strong", { text: f.t }), el("p", { text: corto }), src]));
      });
      return box;
    }, function () {
      return el("p", { text: "No pude cargar los datos del sitio. Revisa tu conexión e inténtalo de nuevo." });
    });
  }

  // ---------- IA ----------
  var HIST = [];
  var sinIA = false; // se activa tras un fallo de red o del servidor
  function preguntarIA(q) {
    var ctl = "AbortController" in window ? new AbortController() : null;
    var t = setTimeout(function () { if (ctl) ctl.abort(); }, 32000);
    return fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ q: q, hist: HIST.slice(-4) }), signal: ctl ? ctl.signal : undefined })
      .then(function (r) {
        clearTimeout(t);
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (r.ok && j && j.ok && j.reply) return j;
          // 400 = pregunta inválida: se muestra el mensaje sin pasar al modo sin IA
          if (r.status === 400 && j && j.error) return { userError: j.error };
          throw new Error((j && j.error) || "HTTP " + r.status);
        });
      }, function (e) { clearTimeout(t); throw e; });
  }

  // ---------- interfaz ----------
  var fab, panel, log, form, input, estado, sug, anterior = null, montado = false;
  function montar() {
    if (montado) return; montado = true;
    fab = el("button", { type: "button", class: "cc-fab", "aria-haspopup": "dialog", "aria-expanded": "false", "aria-controls": "cc-panel" },
      [el("span", { class: "cc-fab-ico", "aria-hidden": "true", text: "?" }), el("span", { text: "Pregúntale a los datos" })]);
    var cerrar = el("button", { type: "button", class: "cc-x", "aria-label": "Cerrar el asistente", text: "×" });
    estado = el("span", { class: "cc-estado", text: "IA" });
    log = el("div", { class: "cc-log", role: "log", "aria-live": "polite", "aria-relevant": "additions" });
    sug = el("div", { class: "cc-sug", role: "group", "aria-label": "Preguntas sugeridas" });
    SUGERENCIAS.forEach(function (s) { sug.appendChild(el("button", { type: "button", class: "cc-chip", text: s })); });
    log.appendChild(el("div", { class: "cc-msg cc-bot" }, [render("Hola. Puedo responder preguntas sobre los 100 días de **Keiko Fujimori (2026)** y **Pedro Castillo (2021)**, con García, Humala y PPK como referencia, usando solo los datos de este sitio.")]));
    log.appendChild(sug);
    input = el("textarea", { class: "cc-q", id: "cc-q", rows: "1", maxlength: String(MAX_Q), placeholder: "Escribe tu pregunta…", "aria-label": "Tu pregunta", autocomplete: "off" });
    var enviar = el("button", { type: "submit", class: "cc-send", text: "Enviar" });
    form = el("form", { class: "cc-form" }, [input, enviar]);
    panel = el("section", { class: "cc-panel", id: "cc-panel", role: "dialog", "aria-modal": "false", "aria-labelledby": "cc-tit", "aria-describedby": "cc-aviso", hidden: "" }, [
      el("header", { class: "cc-head" }, [el("div", null, [el("h2", { id: "cc-tit", class: "cc-tit", text: "Pregúntale a los datos" }), estado]), cerrar]),
      el("p", { id: "cc-aviso", class: "cc-aviso", text: AVISO }),
      log, form,
    ]);
    document.body.appendChild(fab);
    document.body.appendChild(panel);

    fab.addEventListener("click", function () { abrir(); });
    cerrar.addEventListener("click", function () { cerrarPanel(); });
    sug.addEventListener("click", function (ev) { var b = ev.target.closest(".cc-chip"); if (b) preguntar(b.textContent); });
    form.addEventListener("submit", function (ev) { ev.preventDefault(); var q = input.value.trim(); if (q) { input.value = ""; ajustar(); preguntar(q); } });
    input.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event("submit", { cancelable: true })); } });
    input.addEventListener("input", ajustar);
    panel.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { ev.stopPropagation(); cerrarPanel(); return; }
      if (ev.key !== "Tab") return; // mantiene el foco dentro del panel
      var f = panel.querySelectorAll("button:not([disabled]), textarea, a[href]");
      if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (ev.shiftKey && document.activeElement === a) { ev.preventDefault(); z.focus(); }
      else if (!ev.shiftKey && document.activeElement === z) { ev.preventDefault(); a.focus(); }
    });
    if (location.hash === "#preguntar") abrir();
  }
  function ajustar() { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 140) + "px"; }
  function marcarSinIA(motivo) {
    sinIA = true;
    estado.textContent = "Sin IA"; estado.className = "cc-estado cc-off";
    estado.title = motivo || "El asistente con IA no está disponible; busco en los datos del sitio.";
  }
  function abrir() {
    montar();
    if (!panel.hidden) { input.focus(); return; }
    anterior = document.activeElement;
    panel.hidden = false; fab.hidden = true; fab.setAttribute("aria-expanded", "true");
    document.documentElement.classList.add("cc-abierto");
    cargarDatos().catch(function () {}); // precarga para el modo sin IA
    if (navigator.onLine === false) marcarSinIA("Sin conexión.");
    setTimeout(function () { input.focus(); }, 30);
  }
  function cerrarPanel() {
    if (!panel || panel.hidden) return;
    panel.hidden = true; fab.hidden = false; fab.setAttribute("aria-expanded", "false");
    document.documentElement.classList.remove("cc-abierto");
    (anterior && document.contains(anterior) && anterior !== document.body ? anterior : fab).focus();
  }
  function burbuja(cls, nodo) {
    var m = el("div", { class: "cc-msg " + cls }, [nodo]);
    log.appendChild(m); log.scrollTop = log.scrollHeight; return m;
  }
  var ocupado = false;
  function preguntar(q) {
    montar();
    q = String(q).trim().slice(0, MAX_Q);
    if (!q || ocupado) return Promise.resolve();
    ocupado = true; form.classList.add("cc-busy"); form.querySelector(".cc-send").disabled = true;
    if (sug.parentNode) sug.remove();
    burbuja("cc-user", document.createTextNode(q));
    var carga = burbuja("cc-bot cc-cargando", el("span", { class: "cc-dots", "aria-label": "Buscando la respuesta" }, [el("span"), el("span"), el("span")]));
    panel.setAttribute("aria-busy", "true");
    var p = sinIA ? Promise.reject(new Error("sin IA")) : preguntarIA(q);
    return p.then(function (j) {
      if (j.userError) return el("p", { text: j.userError });
      HIST.push({ r: "u", t: q }, { r: "a", t: String(j.reply).slice(0, 400) });
      if (HIST.length > 8) HIST = HIST.slice(-8);
      var cont = render(j.reply);
      if (j.fuentes && j.fuentes.length) {
        var src = el("p", { class: "cc-src" }, ["Fuentes: "]);
        j.fuentes.slice(0, 5).forEach(function (f, i) { if (i) src.appendChild(document.createTextNode(" · ")); src.appendChild(enlace(f.u, dominio(f.u))); });
        cont.appendChild(src);
      }
      return cont;
    }, function (e) {
      var antes = sinIA;
      if (!antes) marcarSinIA("El asistente con IA no respondió (" + (e && e.message ? e.message : "error") + ").");
      return respuestaLocal(q).then(function (nodo) {
        if (!antes) {
          var re = el("button", { type: "button", class: "cc-retry", text: "Reintentar con IA" });
          re.addEventListener("click", function () { sinIA = false; estado.textContent = "IA"; estado.className = "cc-estado"; estado.title = ""; re.remove(); input.focus(); });
          nodo.insertBefore(el("p", { class: "cc-nota" }, ["El asistente con IA no está disponible ahora. ", re]), nodo.firstChild);
        }
        return nodo;
      });
    }).then(function (nodo) {
      carga.remove(); burbuja("cc-bot", nodo);
    }).finally(function () {
      ocupado = false; form.classList.remove("cc-busy"); form.querySelector(".cc-send").disabled = false;
      panel.removeAttribute("aria-busy");
    });
  }

  window.CienChat = { open: abrir, close: cerrarPanel, ask: function (q) { abrir(); return preguntar(q); } };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", montar); else montar();
  addEventListener("hashchange", function () { if (location.hash === "#preguntar") abrir(); });
})();
