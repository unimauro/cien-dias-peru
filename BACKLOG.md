# Backlog: 100 días bajo la lupa

En vivo: https://unimauro.github.io/cien-dias-peru/ · Chat: https://api.tunky.net/cien/chat

## Hecho (7-nov-2026)
- [x] Investigación con 10 agentes (`research/*.json`), verificación de las infografías virales y conclusión.
- [x] Semáforo: índice propio v2 con Monte Carlo (Castillo 46,0 [29–60] y Keiko 36,8 [23–62], no distinguibles; PPK primero en el 77 %) y 18 índices internacionales.
- [x] Revisión adversarial con 5 agentes (`review/01-05`), correcciones aplicadas.
- [x] Sitio en 9 páginas, base de 122 promesas con CSV, 6 PDF, OG, favicon, GTM, Yape y chat IA (desplegado en api-tunky).

## Pendiente
- [ ] Revisar en un celular real que el count-up termine en la cifra exacta.
- [ ] Actualizar las rutas del contexto del chat (`etl/build_chat.py`): hoy cita anclas de la versión de una página (`#indice`, `#conclusion`); pasarlas a las páginas nuevas (`contexto.html`, `index.html#conclusion`, …) y volver a correr el script.
- [ ] Datos que se publican después: el reporte de conflictos de oct-2026 (Defensoría, RCS 272), el informe de obras paralizadas a jun-2026 (Contraloría, descarga manual), Ipsos de nov-2026 y las series del EMBIG después del 3-sep-2026.
- [ ] Integridad (D4) comparable: contar solo actos formales de autoridad dentro de la ventana (formalización, allanamiento, acusación o informe de control) para los cinco gobiernos (`review/02_metodologia.md`).
- [ ] Segundo codificador humano para la cadena de valor (D2) y la idoneidad (D3); revisar los perfiles de baja confianza de los ministros de 2006 y 2011.
- [ ] Lista completa de las 43 promesas de ECData 2021 (edición impresa) y de las 29 de Convoca 2016.
- [ ] Verificación sistemática del balance de Castillo del 10-nov-2021, para que la veracidad (D5) compare a los dos.
- [ ] Opcional: fotos de contexto de Wikimedia Commons con atribución, en `assets/img/`.
- [ ] Opcional: agregar el proyecto al portafolio unimauro.github.io (`build.py` + i18n).
- [ ] Revalidar los videos (oEmbed) y los enlaces antes de cada actualización.
