#!/usr/bin/env python3
"""
Generador del sitio estático de CrediPensión.

Uso:  python3 build.py
Lee  src/pages/*.html  (cuerpo de cada página con marcadores {{...}})
y escribe el sitio final en  public/  listo para subir al hosting.

Marcadores disponibles dentro de las páginas:
  {{i:nombre}}            icono SVG
  {{wa:mensaje}}          enlace de WhatsApp con mensaje prellenado
  {{block:nombre}}        bloque reutilizable (steps, why, cta, logos, sim, rates, cases, notice)
  {{faq:clave}}           preguntas frecuentes (y su schema FAQPage)
"""
import json, re, html, pathlib, urllib.parse, datetime

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"   # carpeta publicada (GitHub Pages / hosting)
DOMAIN = "https://credipension.org"
WA_NUMBER = "573108038677"
WA_DISPLAY = "310 803 8677"
EMAIL = "contacto@credipension.com"
FACEBOOK = "https://www.facebook.com/profile.php?id=61578810636517"
INSTAGRAM = "https://www.instagram.com/credi_pension"
DISCLAIMER = "Credipension no es entidad financiera. No garantizamos aprobación ni desembolso. No solicitamos anticipos. La aprobación, tasa, monto y plazo dependen del estudio de la entidad."

NAV = [
    ("inicio", "/", "Inicio"),
    ("creditos", "/creditos-para-pensionados-en-colombia/", "Créditos para Pensionados"),
    ("convenios", "/convenios/", "Convenios"),
    ("requisitos", "/requisitos/", "Requisitos"),
    ("bucaramanga", "/creditos-para-pensionados-bucaramanga/", "Bucaramanga"),
    ("contacto", "/contacto/", "Contacto"),
]

# ---------------------------------------------------------------- iconos
ICONS = {
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
 "x-circle": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
 "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
 "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
 "gift": '<path d="M20 12v10H4V12"/><path d="M2 7h20v5H2z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>',
 "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
 "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 "building": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
 "phone-app": '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
 "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
 "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
 "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
 "handshake": '<path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/>',
 "clipboard": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
 "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
 "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
 "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
 "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
 "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
 "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
 "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 "percent": '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
 "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
 "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
 "calc": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M16 14v4M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M8 18h.01M12 18h.01"/>',
 "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
 "whatsapp": 'FILL<path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.69.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.8h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.82 9.82 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88zm8.41-18.29A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.16-3.48-8.41z"/>',
 "facebook": 'FILL<path d="M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4v-8.5z"/>',
}

def icon(name):
    body = ICONS[name]
    cls = "ico"
    if body.startswith("FILL"):
        cls += " ico-fill"
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'

def sprite():
    syms = []
    for k, v in ICONS.items():
        syms.append(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v.replace("FILL", "")}</symbol>')
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(syms) + "</svg>"

def wa(msg="Hola CrediPensión 👋 Quiero recibir asesoría gratuita para mi crédito por libranza."):
    return f"https://wa.me/{WA_NUMBER}?text=" + urllib.parse.quote(msg)

# ---------------------------------------------------------------- convenios
LOGOS = [
    ("colpensiones", "Colpensiones"), ("fopep", "FOPEP"), ("casur", "Casur"), ("cremil", "Cremil"),
    ("porvenir", "Porvenir"), ("proteccion", "Protección"), ("colfondos", "Colfondos"), ("skandia", "Skandia"),
    ("fomag", "FOMAG"), ("ministerio-de-defensa", "Ministerio de Defensa"), ("bbva-seguros", "BBVA Seguros"),
    ("seguros-bolivar", "Seguros Bolívar"), ("seguros-alfa", "Seguros Alfa"), ("asulado", "Asulado"),
    ("mapfre", "MAPFRE"), ("sura", "Sura"), ("positiva", "Positiva"), ("seguros-la-equidad", "Seguros la Equidad"),
]
PAGADURIAS = ["Colpensiones", "FOPEP", "CASUR", "CREMIL", "Policía Nacional Pensionados", "CAGEN-TEGEN",
    "Fiduprevisora FOMAG", "FONCEP", "Porvenir", "Protección", "Colfondos", "Skandia", "BBVA Seguros Pensionados",
    "Seguros Bolívar", "Seguros de Vida Alfa", "Asulado Seguros", "AXA Colpatria", "ARL Equidad", "Andina Seguros",
    "MAPFRE", "Suramericana", "Positiva", "Otra pagaduría"]

# ---------------------------------------------------------------- FAQs
FAQS = {
 "inicio": [
  ("¿Qué es CrediPensión?", "CrediPensión es un canal digital de asesoría gratuita para pensionados en Colombia. No somos una entidad financiera; te orientamos y acompañamos para gestionar tu crédito por libranza con las entidades aliadas."),
  ("¿La asesoría tiene algún costo?", "No. Nuestra asesoría es completamente gratuita. No cobramos por orientarte ni solicitamos pagos por adelantado en ninguna etapa del proceso."),
  ("¿Con qué entidades de pensión trabajan?", "Atendemos pensionados de FOPEP, Cremil, Casur, Colpensiones y los principales fondos privados del país, como Porvenir, Protección, Colfondos y Skandia."),
  ("¿Puedo solicitar si estoy reportado?", "Sí, estudiamos tu caso según tu capacidad de descuento disponible. Estar reportado no es un impedimento por sí solo; lo evaluamos junto con la entidad."),
 ],
 "convenios": [
  ("¿Con qué entidades trabajan?", "Trabajamos con las principales pagadurías, fondos de pensión y aseguradoras del país, como Colpensiones, FOPEP, Casur, Cremil, Porvenir, Protección y muchas más. Puedes ver la lista completa más arriba en esta página."),
  ("¿Atienden pensionados de cualquier régimen?", "Sí, atendemos pensionados por vejez, invalidez, sobrevivientes y sustitución pensional, siempre que reciban su mesada a través de una de nuestras pagadurías. Lo importante es que seas pensionado: no aplicamos para empleados activos ni afiliados que aún no estén pensionados."),
  ("¿Qué pasa si mi pagaduría no aparece?", "Es posible que igual podamos ayudarte. La lista muestra las principales, pero también atendemos pensionados de algunas alcaldías, gobernaciones y entidades del Estado. Escríbenos por WhatsApp con el nombre de tu pagaduría y revisamos tu caso sin compromiso."),
  ("¿El crédito se descuenta directamente de mi pensión?", "Sí. El crédito por libranza se paga mediante un descuento que la pagaduría aplica directamente a tu mesada pensional, según tu capacidad de descuento disponible. Por eso no necesitas hacer pagos manuales ni desplazarte."),
 ],
 "creditos": [
  ("¿Qué es un crédito por libranza para pensionados?", "Es un préstamo cuyo pago se descuenta directamente de tu mesada pensional a través de tu pagaduría, sin que tengas que hacer pagos manuales ni presentar codeudor."),
  ("¿A cuántos años puedo diferir el crédito?", "Los plazos varían según la entidad y tu perfil, y pueden extenderse hasta varios años. En la simulación te mostramos las opciones de plazo y cuota disponibles para tu caso."),
  ("¿Necesito codeudor o fiador?", "No. Como el pago se descuenta directamente de tu pensión, el crédito por libranza no requiere codeudor ni fiador; tu mesada respalda el crédito."),
  ("¿Puedo unificar deudas o comprar cartera?", "Sí. Si tienes varios créditos, puedes unificarlos en uno solo mediante compra de cartera, según tu capacidad de descuento y las políticas de la entidad."),
 ],
 "requisitos": [
  ("¿Puedo solicitar si estoy reportado?", "Sí, estudiamos tu caso según tu capacidad de descuento disponible. Estar reportado no es un impedimento por sí solo; lo evaluamos junto con la entidad."),
  ("¿Qué pasa si tengo un proceso de insolvencia?", "Las personas con procesos de insolvencia o liquidación patrimonial no son sujetos de crédito ante ninguna entidad, en cualquier etapa del proceso. Este es el único caso que no podemos gestionar."),
  ("¿Hasta qué edad puedo solicitar?", "Estudiamos créditos para pensionados hasta los 89 años y 364 días, conforme a las políticas de riesgo de las entidades."),
  ("¿Necesito codeudor para solicitar?", "No. Al ser un crédito por libranza, la cuota se descuenta directamente de tu mesada pensional, por lo que no necesitas codeudor ni fiador."),
 ],
 "bucaramanga": [
  ("¿Dónde puedo pedir un crédito para pensionados en Bucaramanga?", "En CrediPensión te asesoramos gratis desde el Centro de Bucaramanga y por WhatsApp. Revisamos tu caso según tu pagaduría y te acompañamos con la entidad aliada, sin filas ni desplazamientos."),
  ("¿Atienden pensionados de Floridablanca, Girón y Piedecuesta?", "Sí. Atendemos pensionados de toda el área metropolitana de Bucaramanga y del resto de Santander. Todo el proceso es digital, así que puedes gestionarlo desde tu casa."),
  ("¿Cuánto me pueden prestar siendo pensionado?", "Depende de tu capacidad de descuento disponible, tu pagaduría y el estudio de la entidad. Con tus dos últimos desprendibles te mostramos monto, cuota y plazo según tu perfil, sin ningún compromiso. Puedes usar el simulador de esta página como referencia."),
  ("¿Necesito codeudor o ir a una oficina?", "No. Al ser un crédito por libranza, la cuota se descuenta directamente de tu mesada pensional, por lo que no necesitas codeudor ni fiador, y el proceso se hace en línea."),
  ("¿Puedo solicitar si estoy reportado?", "Sí, estudiamos tu caso según tu capacidad de descuento disponible. Estar reportado no es un impedimento por sí solo; lo evaluamos junto con la entidad."),
  ("¿La asesoría tiene algún costo?", "No. Nuestra asesoría es completamente gratuita. No cobramos por orientarte ni solicitamos pagos por adelantado en ninguna etapa del proceso."),
 ],
}

def faq_html(key, sub="Lo que más nos preguntan los pensionados antes de empezar."):
    items = "".join(
        f'<details{" open" if n == 0 else ""}><summary>{html.escape(q)}</summary><div><p>{html.escape(a)}</p></div></details>'
        for n, (q, a) in enumerate(FAQS[key]))
    return f'''<section class="section bg-soft" id="preguntas">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Preguntas frecuentes</span><h2>Resolvemos tus dudas</h2><p>{sub}</p></div>
    <div class="faq reveal">{items}</div>
  </div>
</section>'''

def faq_schema(key):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS[key]]}

# ---------------------------------------------------------------- bloques
def b_notice():
    return f'''<div class="notice reveal">{icon("shield")}<div><strong>Transparencia ante todo</strong>
<p>No otorgamos créditos. La aprobación y las condiciones dependen del estudio de cada entidad, tu capacidad de descuento y tu convenio.</p></div></div>'''

def b_logos():
    imgs = "".join(f'<img src="/assets/img/convenios/{f}.webp" alt="{n}" width="112" height="56" loading="lazy">' for f, n in LOGOS)
    dup = "".join(f'<img src="/assets/img/convenios/{f}.webp" alt="" aria-hidden="true" width="112" height="56" loading="lazy">' for f, n in LOGOS)
    return f'''<section class="logos" aria-label="Convenios y pagadurías">
  <div class="container"><p class="logos-title">Atendemos pensionados de las principales pagadurías, fondos y aseguradoras del país</p></div>
  <div class="marquee"><div class="marquee-track">{imgs}{dup}</div></div>
</section>'''

STEPS = [
    ("Contáctanos sin costo", "Escríbenos por WhatsApp y cuéntanos por qué pagaduría recibes tu pensión."),
    ("Comparte tus documentos", "Envíanos tus dos últimos desprendibles para revisar tu capacidad disponible."),
    ("Conoce tu simulación", "Te mostramos monto, cuota y plazo según tu perfil, sin ningún compromiso."),
    ("Gestionamos tu crédito", "Si te convence, avanzamos con la entidad y te acompañamos hasta el final."),
]
def b_steps(eyebrow="Paso a paso", title="Así de fácil es tu asesoría"):
    items = "".join(f'<div class="step reveal"><div class="step-n">{i+1}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(STEPS))
    return f'''<section class="section" id="como-funciona">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p>Todo en línea, sin filas ni desplazamientos.</p></div>
    <div class="steps">{items}</div>
    <div class="cta-row reveal" style="justify-content:center;margin-top:40px"><a class="btn btn-wa btn-lg" href="{wa("Hola CrediPensión 👋 Quiero empezar mi asesoría gratuita. Recibo mi pensión por: ")}">{icon("whatsapp")} Empezar por WhatsApp</a></div>
  </div>
</section>'''

WHY = [
    ("gift", "", "Asesoría 100% gratuita", "Te orientamos sin ningún costo. No cobramos por acompañarte."),
    ("ban", "o", "Sin anticipos", "Nunca pedimos pagos por adelantado. Desconfía de quien lo haga."),
    ("user", "g", "Atención personalizada", "Un asesor real te acompaña por WhatsApp en cada paso."),
    ("building", "", "Entidades autorizadas", "Trabajamos con entidades legalmente vigiladas, para tu tranquilidad."),
    ("phone-app", "o", "Todo digital", "Sin filas ni desplazamientos. Gestiona tu crédito desde casa."),
    ("refresh", "g", "También reportados", "Estudiamos tu caso según tu capacidad, aunque tengas reportes."),
]
def b_why(sub="Todo en línea, sin filas ni desplazamientos."):
    items = "".join(f'<div class="card reveal"><div class="card-ico {c}">{icon(i)}</div><h3>{t}</h3><p>{d}</p></div>' for i, c, t, d in WHY)
    return f'''<section class="section bg-soft" id="por-que">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Confianza</span><h2>¿Por qué elegir CrediPensión?</h2><p>{sub}</p></div>
    <div class="grid g-3">{items}</div>
  </div>
</section>'''

def b_cta(msg="Hola CrediPensión 👋 Quiero que un asesor revise mi caso sin costo."):
    return f'''<section class="section-sm">
  <div class="container">
    <div class="cta-band reveal">
      <div style="position:relative;z-index:1">
        <span class="eyebrow">Da el primer paso</span>
        <h2>¿Listo para conocer tu crédito?</h2>
        <p>Escríbenos por WhatsApp y un asesor revisa tu caso sin costo, sin compromiso y sin salir de casa. Tú decides si avanzar.</p>
        <ul>
          <li>{icon("check-circle")} Asesoría gratuita y personalizada</li>
          <li>{icon("check-circle")} Sin anticipos ni compromiso</li>
          <li>{icon("lock")} Tus datos protegidos · Ley 1581</li>
        </ul>
      </div>
      <div class="cta-box">
        <div class="wa-big">{icon("whatsapp")}</div>
        <strong>Asesoría por WhatsApp</strong>
        <p><span class="live">Respuesta en minutos</span></p>
        <a class="btn btn-wa btn-lg btn-block" href="{wa(msg)}">{icon("whatsapp")} Solicitar asesoría</a>
        <p style="margin:14px 0 0">o llámanos al <a href="tel:+{WA_NUMBER}"><b>{WA_DISPLAY}</b></a></p>
      </div>
    </div>
  </div>
</section>'''

def b_sim(compact=False, title=True):
    opts = '<option value="">Selecciona tu pagaduría (opcional)</option>' + "".join(f"<option>{p}</option>" for p in PAGADURIAS)
    head = "" if not title else f'''<div class="section-head reveal"><span class="eyebrow">Simulador</span><h2>Calcula tu crédito en segundos</h2>
<p>Mueve las barras y conoce una cuota aproximada con las tasas de referencia vigentes. Luego envíanos tu simulación por WhatsApp y un asesor la revisa gratis.</p></div>'''
    sim = f'''<div class="sim{" reveal" if not compact else ""}" data-sim id="simulador-app">
  <div class="sim-form">
    <div class="sim-tabs" role="tablist" aria-label="Tipo de simulación">
      <button type="button" role="tab" aria-selected="true" data-mode="monto">¿Cuánto necesito?</button>
      <button type="button" role="tab" aria-selected="false" data-mode="cuota">¿Cuánto puedo pagar?</button>
    </div>
    <div class="field" data-f="monto">
      <label for="sim-monto-{int(compact)}">Monto que necesitas</label>
      <div class="money"><span>$</span><input type="text" inputmode="numeric" id="sim-monto-{int(compact)}" data-i="monto" autocomplete="off"></div>
      <input type="range" data-r="monto" aria-label="Monto que necesitas">
      <div class="range-legend"><span data-l="montoMin"></span><span data-l="montoMax"></span></div>
    </div>
    <div class="field" data-f="cuota" hidden>
      <label for="sim-cuota-{int(compact)}">Cuota mensual que puedes pagar</label>
      <div class="money"><span>$</span><input type="text" inputmode="numeric" id="sim-cuota-{int(compact)}" data-i="cuota" autocomplete="off"></div>
      <input type="range" data-r="cuota" aria-label="Cuota mensual">
      <div class="range-legend"><span data-l="cuotaMin"></span><span data-l="cuotaMax"></span></div>
    </div>
    <div class="field">
      <div class="lbl"><span>Plazo</span><output data-o="plazo"></output></div>
      <input type="range" data-r="plazo" aria-label="Plazo en meses">
      <div class="range-legend"><span data-l="plazoMin"></span><span data-l="plazoMax"></span></div>
    </div>
    <div class="field" style="margin-bottom:0">
      <label for="sim-pag-{int(compact)}">¿Por qué entidad recibes tu pensión?</label>
      <select id="sim-pag-{int(compact)}" data-i="pagaduria">{opts}</select>
    </div>
  </div>
  <div class="sim-res" aria-live="polite">
    <span class="r-label" data-o="label">Cuota mensual aproximada</span>
    <div class="r-main" data-o="main">—</div>
    <div class="r-sub" data-o="sub"></div>
    <dl>
      <dt data-o="d1l">Monto solicitado</dt><dd data-o="d1"></dd>
      <dt>Plazo</dt><dd data-o="d2"></dd>
      <dt>Tasa de referencia</dt><dd data-o="d3"></dd>
      <dt>Seguro de vida (incluido)</dt><dd data-o="d4"></dd>
    </dl>
    <a class="btn btn-wa btn-lg btn-block" data-o="send" href="{wa()}">{icon("whatsapp")} Enviar mi simulación</a>
    <p class="disclaimer">Valores de referencia, no constituyen oferta. La tasa, la fianza, el estudio y el monto final dependen del estudio de la entidad, tu capacidad de descuento y tu convenio.</p>
  </div>
</div>'''
    if compact:
        return sim
    return f'''<section class="section" id="simulador"><div class="container">{head}{sim}</div></section>'''

EXAMPLES = [
    ("12 meses", "$2.603.633", "$37.041", "$12.042", "$247.866", "$119.000", "$2.187.684"),
    ("60 meses", "$8.419.447", "$119.780", "$38.940", "$801.531", "$119.000", "$7.340.196"),
    ("144 meses", "$11.785.934", "$167.674", "$54.510", "$1.122.021", "$119.000", "$10.322.729"),
]
def b_rates():
    ex = "".join(f'''<article class="example reveal"><header>{p}</header><dl>
<dt>Crédito</dt><dd>{c}</dd><dt>Intereses</dt><dd>{i}</dd><dt>Seguros</dt><dd>{s}</dd><dt>Fianza+IVA</dt><dd>{f}</dd><dt>Estudio+IVA</dt><dd>{e}</dd></dl>
<div class="recibes"><span>RECIBES</span><span>{r}</span></div></article>''' for p, c, i, s, f, e, r in EXAMPLES)
    return f'''<section class="section bg-soft" id="tarifas">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Información transparente</span><h2>Tarifas y condiciones vigentes</h2>
      <p>Crédito por libranza · actualizado a <span data-cp="actualizado">julio de 2026</span>.</p></div>
    <div class="rates reveal">
      <div class="rate"><small>Tasa N.M.V</small><strong data-cp="tasaNMV">1,45%–1,81%</strong></div>
      <div class="rate"><small>Tasa E.A</small><strong data-cp="tasaEA">18,86%–24,02%</strong></div>
      <div class="rate"><small>Plazo</small><strong data-cp="plazo">12 a 144 meses</strong></div>
    </div>
    <h3 class="reveal" style="margin-top:40px">Costos asociados</h3>
    <div class="costs reveal">
      <div class="cost"><b>Estudio</b>$100.000 + IVA</div>
      <div class="cost"><b>Seguro vida</b><span data-cp="seguro">$4.625/millón</span></div>
      <div class="cost"><b>Certificación</b>$20.000</div>
      <div class="cost"><b>Cheque gerencia</b>$19.500</div>
      <div class="cost"><b>Fianza</b>8,00%–22,84% + IVA</div>
    </div>
    <h3 class="reveal" style="margin-top:44px">Ejemplo del costo total</h3>
    <p class="reveal" style="color:var(--ink-2)">Misma cuota de <b>$250.000 al mes</b>, con distinto plazo:</p>
    <div class="examples">{ex}</div>
    <p class="disclaimer reveal" style="margin-top:24px">Cifras de referencia de una entidad aliada, vigentes a junio de 2026. La tasa, la fianza y el estudio varían según el perfil del solicitante y la entidad que apruebe el caso. CrediPensión es un servicio de asesoría, no una entidad financiera, y no desembolsa créditos. No solicitamos pagos por anticipado.</p>
  </div>
</section>'''

def b_cases(bg=""):
    return f'''<section class="section {bg}" id="informacion-clave">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Información clave</span><h2>Antes de continuar, conoce esto</h2>
      <p>Con transparencia, te contamos qué casos podemos estudiar y cuáles no aplican por políticas de las entidades.</p></div>
    <div class="cases">
      <div class="case-col yes reveal"><h3>{icon("check-circle")} Casos que sí estudiamos</h3>
        <div class="case-item"><b>Hijo con invalidez</b><p>Aplica cuando la pensión que recibe el hijo es vitalicia por su condición.</p></div>
        <div class="case-item"><b>Pensión de sobreviviente</b><p>Puede aplicar el cónyuge del pensionado fallecido.</p></div>
        <div class="case-item"><b>Hasta los 89 años</b><p>Estudiamos créditos hasta los 89 años y 364 días, según políticas de riesgo.</p></div>
        <div class="case-item"><b>Cremil y Casur con embargos</b><p>Aplican incluso con embargos por alimentos.</p></div>
      </div>
      <div class="case-col no reveal"><h3>{icon("x-circle")} Casos que no aplican</h3>
        <div class="case-item"><b>Hijos sin invalidez</b><p>Por normatividad interna, no pueden acceder al crédito.</p></div>
        <div class="case-item"><b>Procesos de insolvencia</b><p>Con insolvencia o liquidación patrimonial no son sujetos de crédito ante ninguna entidad.</p></div>
        <p class="alert" style="margin-top:18px">Esto aplica en cualquier etapa del proceso: iniciado, en curso o finalizado.</p>
      </div>
    </div>
  </div>
</section>'''

CONV_CATS = [
    ("Fondos públicos y régimen especial", "building", "", [("Colpensiones", "colpensiones"), ("FOPEP", "fopep"), ("CASUR", "casur"), ("CREMIL", "cremil"), ("Policía Nacional Pensionados", None), ("CAGEN-TEGEN", "ministerio-de-defensa"), ("Fiduprevisora FOMAG", "fomag"), ("FONCEP", None)]),
    ("Fondos privados de pensión", "wallet", "o", [("Porvenir", "porvenir"), ("Protección", "proteccion"), ("Colfondos", "colfondos"), ("Skandia", "skandia"), ("BBVA Seguros Pensionados", "bbva-seguros"), ("Seguros Bolívar", "seguros-bolivar")]),
    ("Aseguradoras y renta vitalicia", "shield", "g", [("Seguros de Vida Alfa", "seguros-alfa"), ("Asulado Seguros", "asulado"), ("AXA Colpatria", None), ("ARL Equidad", "seguros-la-equidad"), ("Andina Seguros", None), ("MAPFRE", "mapfre"), ("Suramericana", "sura"), ("Positiva", "positiva")]),
]
def b_convenios():
    cols = []
    for title, ic, c, items in CONV_CATS:
        lis = []
        for name, f in items:
            if f:
                lg = '<span class="lg"><img src="/assets/img/convenios/%s.webp" alt="" width="64" height="32" loading="lazy"></span>' % f
            else:
                lg = '<span class="lg txt">%s</span>' % "".join(w[0] for w in name.replace("-", " ").split()[:2]).upper()
            lis.append(f"<li>{lg}{name}</li>")
        cols.append(f'<div class="conv-cat reveal"><h3><span class="card-ico {c}" style="margin:0;width:48px;height:48px">{icon(ic)}</span>{title}</h3><ul class="conv-list">{"".join(lis)}</ul></div>')
    return '<div class="grid g-3" style="align-items:start">' + "".join(cols) + "</div>"

def b_logowall():
    return '<div class="logo-wall">' + "".join(f'<div class="reveal"><img src="/assets/img/convenios/{f}.webp" alt="{n}" width="112" height="56" loading="lazy"></div>' for f, n in LOGOS) + "</div>"

BLOCKS = {"convenios": b_convenios, "logowall": b_logowall, "notice": b_notice, "logos": b_logos, "steps": b_steps, "why": b_why, "cta": b_cta,
          "sim": b_sim, "sim-compact": lambda: b_sim(compact=True), "rates": b_rates,
          "cases": b_cases, "cases-soft": lambda: b_cases("bg-soft")}

# ---------------------------------------------------------------- layout
def header(active):
    cur = ' aria-current="page"'
    links = "".join(
        f'<a href="{href}"{cur if key == active else ""}>{label}</a>' for key, href, label in NAV if key != "bucaramanga")
    return f'''<a class="skip" href="#main">Saltar al contenido</a>
<div class="topbar"><div class="container">
  <div class="topbar-l">
    <span class="topbar-item">{icon("shield")} Asesoría 100% gratuita</span>
    <span class="topbar-item hide-md">{icon("pin")} Bucaramanga · Atención digital en toda Colombia</span>
    <span class="topbar-item hide-md">{icon("clock")} Lun a Vie · 8am – 6pm</span>
  </div>
  <div class="topbar-r">
    <a class="topbar-item" href="tel:+{WA_NUMBER}">{icon("phone")} {WA_DISPLAY}</a>
    <span class="social"><a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook">{icon("facebook")}</a><a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram")}</a></span>
  </div>
</div></div>
<header class="header"><div class="container">
  <a class="brand" href="/" aria-label="CrediPensión — Inicio"><img src="/assets/img/logo.webp" alt="CrediPensión" width="420" height="247"></a>
  <nav class="nav" id="nav" aria-label="Principal">{links}</nav>
  <div class="header-cta">
    <a class="btn btn-wa btn-sm" href="{wa()}">{icon("whatsapp")}<span class="btn-text">Asesoría gratis</span></a>
    <button class="menu-btn" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav">{icon("menu")}</button>
  </div>
</div></header>'''

def footer():
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="footer-logo" href="/"><img src="/assets/img/logo.webp" alt="CrediPensión" width="420" height="247" loading="lazy"></a>
        <p>Canal digital de asesoría gratuita para pensionados en Colombia. No somos una entidad financiera ni cobramos por nuestros servicios: te damos orientación confiable para gestionar tu crédito por libranza con respaldo y transparencia.</p>
        <div class="social"><a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook">{icon("facebook")}</a><a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram")}</a><a href="{wa()}" aria-label="WhatsApp">{icon("whatsapp")}</a></div>
      </div>
      <div>
        <h4>Navegación</h4>
        <ul>{"".join(f'<li><a href="{h}">{l}</a></li>' for k, h, l in NAV)}</ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="/politicas-de-cookies/">Políticas de Cookies</a></li>
          <li><a href="/politicas-de-privacidad-y-tratamiento-de-datos/">Privacidad y Tratamiento de Datos</a></li>
          <li><a href="/terminos-y-condiciones-de-uso/">Términos y Condiciones de Uso</a></li>
        </ul>
      </div>
      <div>
        <h4>Contacto</h4>
        <ul>
          <li>{icon("whatsapp")}<a href="{wa()}">{WA_DISPLAY}</a></li>
          <li>{icon("mail")}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{icon("pin")}<span>Centro, Bucaramanga, Santander<br>Atención digital · toda Colombia</span></li>
          <li>{icon("clock")}<span>Lun a Vie · 8am – 6pm</span></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer footer-disclaimer">Las condiciones del crédito dependen exclusivamente de las entidades financieras aliadas y del cumplimiento de sus requisitos. {DISCLAIMER}</p>
    <div class="footer-bottom"><span>CrediPensión © 2025–2030 · Todos los derechos reservados.</span><span>Tus datos protegidos · Ley 1581 de 2012</span></div>
  </div>
</footer>
<a class="wa-float" href="{wa()}" aria-label="Escríbenos por WhatsApp"><span class="wa-bubble">¿Te ayudamos? Escríbenos 👋</span><span class="wa-btn">{icon("whatsapp")}</span></a>'''

ORG = {
    "@type": "ProfessionalService", "@id": DOMAIN + "/#organizacion", "name": "CrediPensión",
    "description": "Canal digital de asesoría gratuita para pensionados en Colombia que desean gestionar un crédito por libranza.",
    "url": DOMAIN + "/", "logo": DOMAIN + "/assets/img/logo.png", "image": DOMAIN + "/assets/img/fotos/hero-pareja.webp",
    "telephone": "+57" + WA_NUMBER[2:], "email": EMAIL, "priceRange": "Asesoría gratuita",
    "address": {"@type": "PostalAddress", "streetAddress": "Centro", "addressLocality": "Bucaramanga", "addressRegion": "Santander", "addressCountry": "CO"},
    "geo": {"@type": "GeoCoordinates", "latitude": 7.1193, "longitude": -73.1227},
    "areaServed": [{"@type": "City", "name": "Bucaramanga"}, {"@type": "City", "name": "Floridablanca"}, {"@type": "City", "name": "Girón"}, {"@type": "City", "name": "Piedecuesta"}, {"@type": "Country", "name": "Colombia"}],
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "18:00"}],
    "sameAs": [FACEBOOK, INSTAGRAM],
}

def page(meta, body):
    path = meta["path"]
    url = DOMAIN + path
    graph = [ORG, {"@type": "WebPage", "@id": url, "url": url, "name": meta["title"], "description": meta["description"], "inLanguage": "es-CO", "isPartOf": {"@type": "WebSite", "name": "CrediPensión", "url": DOMAIN + "/"}}]
    if path != "/":
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": meta.get("crumb", meta["title"]), "item": url}]})
    if meta.get("faq"):
        graph.append(faq_schema(meta["faq"]))
    if meta.get("service"):
        graph.append({"@type": "Service", "name": meta["service"], "serviceType": "Asesoría en crédito por libranza para pensionados", "provider": {"@id": DOMAIN + "/#organizacion"}, "areaServed": meta.get("area", "Colombia"), "offers": {"@type": "Offer", "price": "0", "priceCurrency": "COP", "description": "Asesoría gratuita, sin anticipos"}})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    og = DOMAIN + meta.get("og", "/assets/img/fotos/hero-pareja.webp")
    preload = f'<link rel="preload" as="image" href="{meta["preload"]}" fetchpriority="high">' if meta.get("preload") else ""
    return f'''<!doctype html>
<html lang="es-CO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(meta["title"])}</title>
<meta name="description" content="{html.escape(meta["description"])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#22599b">
<meta name="geo.region" content="CO-SAN"><meta name="geo.placename" content="Bucaramanga">
<meta property="og:type" content="website"><meta property="og:locale" content="es_CO"><meta property="og:site_name" content="CrediPensión">
<meta property="og:title" content="{html.escape(meta["title"])}"><meta property="og:description" content="{html.escape(meta["description"])}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/img/favicon.png"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&display=swap">
{preload}
<link rel="stylesheet" href="/assets/css/styles.css?v={VERSION}">
<script type="application/ld+json">{ld}</script>
</head>
<body class="{meta.get("bodyclass", "")}">
{sprite()}
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
{meta.get("extra_end", "")}
<script src="/assets/js/config.js?v={VERSION}"></script>
<script src="/assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
'''

VERSION = datetime.date.today().strftime("%Y%m%d")

def render(body):
    body = re.sub(r"\{\{i:([\w-]+)\}\}", lambda m: icon(m.group(1)), body)
    body = re.sub(r"\{\{wa:(.*?)\}\}", lambda m: wa(m.group(1).strip()) if m.group(1).strip() else wa(), body, flags=re.S)
    body = re.sub(r"\{\{wa\}\}", lambda m: wa(), body)
    body = re.sub(r"\{\{block:([\w-]+)\}\}", lambda m: BLOCKS[m.group(1)](), body)
    body = re.sub(r"\{\{faq:(\w+)(?:\|(.*?))?\}\}", lambda m: faq_html(m.group(1), m.group(2)) if m.group(2) else faq_html(m.group(1)), body)
    body = body.replace("{{WA_DISPLAY}}", WA_DISPLAY).replace("{{WA_NUMBER}}", WA_NUMBER).replace("{{EMAIL}}", EMAIL)
    body = body.replace("{{FACEBOOK}}", FACEBOOK).replace("{{INSTAGRAM}}", INSTAGRAM).replace("{{DISCLAIMER}}", DISCLAIMER)
    return body

LEGAL = [
    ("politicas-de-cookies", "Políticas de Cookies"),
    ("politicas-de-privacidad-y-tratamiento-de-datos", "Política de Privacidad y Tratamiento de Datos"),
    ("terminos-y-condiciones-de-uso", "Términos y Condiciones de Uso"),
]

def relativize(doc, path):
    """Convierte rutas absolutas (/assets/..., /convenios/) en relativas,
    para que el sitio funcione en un subdirectorio (GitHub Pages) o en la raíz del dominio."""
    depth = len([x for x in path.strip("/").split("/") if x])
    pre = "../" * depth
    doc = re.sub(r'((?:href|src|poster)=")/(?!/)', lambda m: m.group(1) + (pre or "./"), doc)
    return doc

def main():
    urls = []
    for f in sorted((ROOT / "src/pages").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--META\s*(\{.*?\})\s*-->", raw, re.S)
        meta = json.loads(m.group(1)); body = raw[m.end():]
        dest = OUT / meta["path"].strip("/") / "index.html" if meta["path"] != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(relativize(page(meta, render(body)), meta["path"]), encoding="utf-8")
        urls.append((meta["path"], meta.get("priority", "0.8")))
        print("✓", dest.relative_to(ROOT))
    for slug, title in LEGAL:
        content = (ROOT / "src/legal" / f"{slug}.html").read_text(encoding="utf-8")
        body = f'''<section class="page-hero"><div class="container"><nav class="breadcrumb"><a href="/">Inicio</a><span>›</span>Legal</nav><h1>{title}</h1></div></section>
<section class="section"><div class="container legal">{content}</div></section>'''
        meta = {"path": f"/{slug}/", "title": f"{title} - CrediPensión", "description": f"{title} de CrediPensión, canal digital de asesoría gratuita para pensionados en Colombia.", "crumb": title}
        dest = OUT / slug / "index.html"; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(relativize(page(meta, body), meta["path"]), encoding="utf-8")
        urls.append((meta["path"], "0.3"))
        print("✓", dest.relative_to(ROOT))
    today = datetime.date.today().isoformat()
    sm = "".join(f"<url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>" for p, pr in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    print("✓ sitemap.xml, robots.txt")

if __name__ == "__main__":
    main()
