# CrediPensión — sitio web nuevo (credipension.org)

Sitio estático (HTML/CSS/JS), rápido y listo para subir a cualquier hosting.

## Qué subir al hosting
Sube **todo el contenido de la carpeta `docs/`** a la raíz del dominio (`public_html` en cPanel).
Incluye `.htaccess` (HTTPS, sin www, caché y compresión), `sitemap.xml` y `robots.txt`.

## Páginas
| URL | Página |
|---|---|
| `/` | Inicio |
| `/creditos-para-pensionados-en-colombia/` | Créditos para pensionados |
| `/convenios/` | Convenios y pagadurías |
| `/requisitos/` | Requisitos |
| `/contacto/` | Contacto |
| `/creditos-para-pensionados-bucaramanga/` | Landing SEO Bucaramanga |
| `/politicas-de-cookies/`, `/politicas-de-privacidad-y-tratamiento-de-datos/`, `/terminos-y-condiciones-de-uso/` | Legales |

Las URLs son las mismas del sitio actual, así que las redirecciones desde credipension.co son directas.

## Cambiar tasas o el WhatsApp (sin programar)
Edita `docs/assets/js/config.js`: tasas N.M.V. y E.A., seguro de vida, plazos, límites del simulador
y número de WhatsApp. El simulador y la tabla de tarifas se actualizan solos.

## Editar textos
Los textos están en `src/pages/*.html` y los bloques compartidos (pasos, preguntas frecuentes, tarifas,
pie de página, etc.) en `build.py`. Después de editar, ejecuta:

```bash
python3 build.py
```

y vuelve a subir `docs/` (o haz commit y push: GitHub Pages se actualiza solo).

## Al pasar a producción (credipension.org)
- Configurar redirección 301 de credipension.co → credipension.org (mismas rutas).
- Dar de alta el dominio en Google Search Console y enviar `https://credipension.org/sitemap.xml`.
- Crear/actualizar el Perfil de Empresa de Google en Bucaramanga apuntando a la landing.
