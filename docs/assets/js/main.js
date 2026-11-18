/* CrediPensión — interacciones del sitio */
(function () {
  var C = window.CP_CONFIG || {};
  var WA = C.whatsapp || "573108038677";
  var fmt = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 });
  var money = function (n) { return "$" + fmt.format(Math.round(n)); };
  var pct = function (n) { return String(n.toFixed(2)).replace(".", ",") + "%"; };
  var waLink = function (msg) { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(msg); };

  /* Reescribe todos los enlaces de WhatsApp con el número configurado */
  document.querySelectorAll('a[href*="wa.me/"]').forEach(function (a) {
    a.href = a.href.replace(/wa\.me\/\d+/, "wa.me/" + WA);
    a.target = "_blank"; a.rel = "noopener";
  });

  /* Valores de tarifas desde config */
  var vals = {
    tasaNMV: pct(C.tasaMinNMV) + "–" + pct(C.tasaMaxNMV),
    tasaEA: pct(C.tasaMinEA) + "–" + pct(C.tasaMaxEA),
    plazo: C.plazoMin + " a " + C.plazoMax + " meses",
    plazoMax: String(C.plazoMax),
    seguro: money(C.seguroVidaPorMillon) + "/millón",
    actualizado: C.actualizado
  };
  document.querySelectorAll("[data-cp]").forEach(function (el) {
    var k = el.getAttribute("data-cp");
    if (vals[k] != null && C.tasaMinNMV != null) el.textContent = vals[k];
  });

  /* Menú móvil */
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
    nav.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }); });
  }

  /* Burbuja del WhatsApp flotante */
  var wf = document.querySelector(".wa-float");
  if (wf) setTimeout(function () { wf.classList.add("show-bubble"); setTimeout(function () { wf.classList.remove("show-bubble"); }, 6000); }, 3500);

  /* Animación al hacer scroll */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------------- Simulador ---------------- */
  var seguroFactor = (C.seguroVidaPorMillon || 0) / 1e6;
  function annuity(i, n) { return i / (1 - Math.pow(1 + i, -n)); }
  function cuotaDe(P, tasaPct, n) { return P * annuity(tasaPct / 100, n) + P * seguroFactor; }
  function montoDe(Q, tasaPct, n) { return Q / (annuity(tasaPct / 100, n) + seguroFactor); }
  function parseMoney(s) { return parseInt(String(s).replace(/\D/g, ""), 10) || 0; }
  function setFill(r) { var p = (r.value - r.min) / (r.max - r.min) * 100; r.style.setProperty("--p", p + "%"); }

  document.querySelectorAll("[data-sim]").forEach(function (sim) {
    var mode = "monto";
    var $ = function (s) { return sim.querySelector(s); };
    var tabs = sim.querySelectorAll(".sim-tabs button");
    var rMonto = $("[data-r=monto]"), iMonto = $("[data-i=monto]");
    var rCuota = $("[data-r=cuota]"), iCuota = $("[data-i=cuota]");
    var rPlazo = $("[data-r=plazo]"), oPlazo = $("[data-o=plazo]");
    var fMonto = $("[data-f=monto]"), fCuota = $("[data-f=cuota]");
    var pag = $("[data-i=pagaduria]");
    var out = { label: $("[data-o=label]"), main: $("[data-o=main]"), sub: $("[data-o=sub]"), d1l: $("[data-o=d1l]"), d1: $("[data-o=d1]"), d2: $("[data-o=d2]"), d3: $("[data-o=d3]"), d4: $("[data-o=d4]") };
    var send = $("[data-o=send]");

    rMonto.min = C.montoMin; rMonto.max = C.montoMax; rMonto.step = 500000; rMonto.value = C.montoInicial;
    rCuota.min = C.cuotaMin; rCuota.max = C.cuotaMax; rCuota.step = 10000; rCuota.value = C.cuotaInicial;
    rPlazo.min = C.plazoMin; rPlazo.max = C.plazoMax; rPlazo.step = 6; rPlazo.value = Math.min(C.plazoMax, 120);
    sim.querySelectorAll("[data-l]").forEach(function (el) {
      var k = el.getAttribute("data-l");
      el.textContent = k === "plazoMin" || k === "plazoMax" ? C[k] + " meses" : money(C[k]);
    });

    function calc() {
      var n = +rPlazo.value;
      oPlazo.textContent = n + " meses";
      [rMonto, rCuota, rPlazo].forEach(setFill);
      var msg;
      if (mode === "monto") {
        var P = +rMonto.value;
        var qMin = cuotaDe(P, C.tasaMinNMV, n), qMax = cuotaDe(P, C.tasaMaxNMV, n);
        out.label.textContent = "Cuota mensual aproximada";
        out.main.textContent = money(qMin) + " – " + money(qMax);
        out.sub.textContent = "Se descuenta directamente de tu mesada";
        out.d1l.textContent = "Monto solicitado"; out.d1.textContent = money(P);
        msg = "Hola CrediPensión 👋 Hice la simulación en la web y quiero asesoría gratuita.\n\n• Monto: " + money(P) + "\n• Plazo: " + n + " meses\n• Cuota aprox.: " + money(qMin) + " – " + money(qMax);
      } else {
        var Q = +rCuota.value;
        var pMax = montoDe(Q, C.tasaMinNMV, n), pMin = montoDe(Q, C.tasaMaxNMV, n);
        out.label.textContent = "Monto aproximado que podrías solicitar";
        out.main.textContent = money(pMin) + " – " + money(pMax);
        out.sub.textContent = "Con una cuota de " + money(Q) + " al mes";
        out.d1l.textContent = "Cuota disponible"; out.d1.textContent = money(Q);
        msg = "Hola CrediPensión 👋 Hice la simulación en la web y quiero asesoría gratuita.\n\n• Cuota disponible: " + money(Q) + "\n• Plazo: " + n + " meses\n• Monto aprox.: " + money(pMin) + " – " + money(pMax);
      }
      out.d2.textContent = n + " meses";
      out.d3.textContent = pct(C.tasaMinNMV) + " – " + pct(C.tasaMaxNMV) + " N.M.V.";
      out.d4.textContent = money(C.seguroVidaPorMillon) + " por millón";
      if (pag && pag.value) msg += "\n• Pagaduría: " + pag.value;
      send.href = waLink(msg);
    }
    function syncInput(r, i) {
      i.value = fmt.format(r.value);
      r.addEventListener("input", function () { i.value = fmt.format(r.value); calc(); });
      i.addEventListener("input", function () {
        var v = parseMoney(i.value);
        i.value = v ? fmt.format(v) : "";
        r.value = Math.max(+r.min, Math.min(+r.max, v));
        calc();
      });
      i.addEventListener("blur", function () { i.value = fmt.format(r.value); });
    }
    syncInput(rMonto, iMonto); syncInput(rCuota, iCuota);
    rPlazo.addEventListener("input", calc);
    if (pag) pag.addEventListener("change", calc);
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        mode = t.getAttribute("data-mode");
        tabs.forEach(function (x) { x.setAttribute("aria-selected", x === t); });
        fMonto.hidden = mode !== "monto"; fCuota.hidden = mode !== "cuota";
        calc();
      });
    });
    calc();
  });

  /* Formulario de contacto → WhatsApp */
  var cf = document.getElementById("contact-form");
  if (cf) cf.addEventListener("submit", function (e) {
    e.preventDefault();
    var d = new FormData(cf);
    var msg = "Hola CrediPensión. Escribo desde la página de contacto.\n\n• Nombre: " + (d.get("nombre") || "") + "\n• Motivo: " + (d.get("motivo") || "") + "\n• Mensaje: " + (d.get("mensaje") || "");
    window.open(waLink(msg), "_blank", "noopener");
  });

  var y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
})();

/* Botón de sonido del video del hero */
(function () {
  var v = document.getElementById("hero-video"), b = document.querySelector(".video-sound");
  if (!v || !b) return;
  b.addEventListener("click", function () {
    v.muted = !v.muted;
    if (!v.muted) { v.currentTime = 0; v.play(); }
    b.setAttribute("aria-pressed", String(!v.muted));
    b.setAttribute("aria-label", v.muted ? "Activar sonido del video" : "Silenciar video");
  });
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) v.pause();
})();
