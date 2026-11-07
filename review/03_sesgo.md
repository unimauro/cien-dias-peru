# 03 · Revisión adversarial de neutralidad política

**Sitio:** https://unimauro.github.io/cien-dias-peru/ (DOM renderizado en local con Chrome headless el 7-nov-2026)
**Archivos revisados:** `index.html`, `app.js`, `styles.css`, `research/*.json`
**Panel:** Crítico A (simpatizante de Fuerza Popular: busca sesgo contra Keiko Fujimori) · Crítico B (simpatizante de Perú Libre o de la izquierda: busca sesgo contra Pedro Castillo)
**Severidad:** ALTA = cambia la lectura de la comparación o es un error factual visible · MEDIA = asimetría de tono o de selección que un lector atento detecta · BAJA = matiz o detalle de estilo.

Cada hallazgo indica la **cita exacta**, el **problema**, la **severidad** y una **reescritura neutral** (texto exacto para reemplazar). Cuando el texto viene de un JSON o de `app.js`, se indica el archivo.

---

## 0. Errores factuales e incoherencias internas (los aprovecharían los dos críticos)

Antes de discutir el tono, conviene corregir esto: cada incoherencia le da a cualquiera de los dos bandos un argumento para descalificar el sitio entero.

| # | Cita exacta | Problema | Sev. | Reescritura |
|---|---|---|---|---|
| 0.1 | «60 proyectos de ley del Ejecutivo (? de política sustantiva; el resto, tratados y trámites). No pidió facultades.» (`app.js:297`, tabla de Gobernabilidad) | (a) Se ve un «?» literal porque falta el campo, mientras la conclusión dice «solo 6». (b) **«No pidió facultades» es falso según el propio sitio**: `planes.json` dice «El 28-oct-2021 pidió facultades al Congreso para legislar en materia tributaria». El pedido del gabinete Vásquez/Francke se hizo dentro de la ventana y terminó en la Ley 31380 (dic-2021). | ALTA | «60 proyectos de ley del Ejecutivo (6 de política sustantiva; el resto, tratados y trámites). El 28-oct-2021 pidió facultades en materia tributaria; el Congreso las delegó después del día 100.» |
| 0.2 | «Fuente 'Keiko Gobierna (2026)' no localizable: sin autor, fecha ni método, la cifra 0/67 no es replicable.» (`factcheck.json:162`) | Contradice la tarjeta de arriba, que describe Keiko Gobierna como un tracker «independiente y de código abierto» con un criterio explícito (norma en El Peruano) y lo enlaza. | MEDIA | «La infografía cita "Keiko Gobierna (2026)" sin enlace ni fecha de corte; el tracker existe (keikogobierna.com) y su criterio es exigir una norma publicada en El Peruano.» |
| 0.3 | «Sin categoría intermedia para Keiko: con tres categorías, medidas iniciadas […] podrían clasificarse 'en proceso'» (`factcheck.json:161`) | El mismo tracker sí tiene categoría intermedia («3 en proceso»). | BAJA | «La infografía omite la categoría intermedia que sí usa el tracker (3 en proceso) y presenta un binario cumplida/no cumplida.» |
| 0.4 | «Ninguna promesa «cumplida» llega al escalón de resultado. En Castillo: 1 producto (mascarillas) y 2 actividades. En Keiko: 5 insumos, 7 actividades y 3 productos» (`index.html:69`) | Unidades distintas: para Castillo se cuentan 3 promesas **cumplidas**; para Keiko, 15 entradas «cumplidas **o en proceso**» (`keiko.json:387`), aunque el propio sitio dice que Keiko tiene 0 cumplidas. Además, la escalera visible muestra para Keiko 1 insumo, 4 actividades y 2 productos. El lector concluye que Keiko «hizo más cosas». | ALTA | «Ninguna medida llega al escalón de resultado. Contando lo cumplido o en proceso con el mismo criterio para los dos: Castillo, [N] insumos, [N] actividades y [N] productos; Keiko, 5 insumos, 7 actividades y 3 productos.» (Recalcular Castillo con «cumplidas + en proceso»: 3 + 4 de EC Data.) |
| 0.5 | Línea de tiempo: «S/1500 millones en prevención» · Mensaje verificado: «S/ 100 millones invertidos en prevención en 3 meses» | Dos cifras distintas para la misma afirmación del mismo discurso. | MEDIA | Unificar con la cifra que figura en la transcripción del mensaje y citar el minuto. |
| 0.6 | Línea de tiempo: «retira 48 estaciones y 43 antenas ilegales» · Mensaje: «7 torres, 33 antenas y 194 equipos» | Dos conteos del mismo megaoperativo. | BAJA | Usar la cifra oficial de El Peruano en los dos lugares, o explicar que son operativos o cortes distintos. |
| 0.7 | «Pidió 120 días de facultades; la Cámara de Diputados aprobó 90 días […] el 6-oct-2026 (66-34-24), con el Senado pendiente.» (Contradicciones plan-gestión) | Desactualizado: el Senado completó la delegación el 22-oct (Ley 32743), como dice la propia línea de tiempo. | BAJA | «…aprobó 90 días el 6-oct-2026 (66-34-24) y el Senado completó la delegación el 22-oct (Ley 32743).» |
| 0.8 | «Frente al 28 de julio: de 19 anuncios, reportó avance en 4…» y, dos párrafos después, «Frente a sus propios anuncios del 28 de julio: el mensaje reportó avances en 4…» | Frase duplicada: repetir un dato negativo amplifica su peso. | BAJA | Eliminar la segunda frase. |
| 0.9 | «23.4 M dosis» (ledger) · «23.5 M dosis» (Resultados) | Dos fuentes con cifras distintas para el mismo dato. | BAJA | Usar una sola cifra (OWID 23,4 M) y anotar la otra fuente. |

---

## 1. Crítico A (simpatizante de Fuerza Popular): sesgo contra Keiko Fujimori

### A1. Una sección entera verifica solo el mensaje de Keiko · ALTA
- **Cita:** sección «El mensaje de los 100 días, verificado» (31 afirmaciones), en el menú como «Mensaje 100 días»; y en el índice, «Veracidad del discurso oficial (10 %) … — sin dato | 50 Regular | — sin dato…».
- **Problema:** Castillo también dio un balance de 100 días (10-nov-2021, Ayacucho, TVPerú) con cifras verificables, como «cerca del 60 % de la población objetivo» vacunada o «ningún trabajador formal ganará menos de S/ 1,000», y no se verifica. Solo Keiko queda expuesta a 31 chequeos, a titulares como «Solo 6 de las 31…» y a una dimensión del índice que solo se le aplica a ella. (Numéricamente, D5 hoy la sube de ~39,0 a 40,3, pero la asimetría de escrutinio es evidente.)
- **Reescritura:** verificar el mensaje de Castillo del 10-nov-2021 con el mismo protocolo. Mientras no se haga, cambiar el título y la entradilla así:
  - H2: «El mensaje de los 100 días de Keiko Fujimori, verificado»
  - Entradilla, agregar al final: «El balance de Pedro Castillo (10-nov-2021) aún no se verificó con este protocolo; por eso esta dimensión no entra en el índice de ninguno de los dos.»
  - Y **sacar D5 del índice** hasta que haya dato para ambos.

### A2. «Brújula 2026» solo para Keiko, con «Empeora» aplicado a desaceleraciones · ALTA
- **Cita:** «Brújula 2026: ¿el país está mejor o peor que el 28 de julio?» y filas como «Ingresos tributarios … 20 → 18.3 ▼ Empeora», «Producción de electricidad 7.8 → 6.7 ▼ Empeora», «PBI 3.6 → 3.2 ▼ Empeora».
- **Problema:** (a) No hay una brújula 2021 para Castillo, aunque en su ventana la inflación pasó de 3,3 a 5,8 % y el dólar marcó récords. (b) Un crecimiento real de dos dígitos que se modera se rotula «Empeora»: es una desaceleración, no un deterioro. El resultado visual es 10 «Empeora» frente a 3 «Mejora».
- **Reescritura:** agregar la brújula 2021 con los mismos indicadores o quitar la de 2026. En las tasas de crecimiento que siguen siendo positivas, cambiar «▼ Empeora» por «▽ Crece menos». Agregar este subtítulo: «Indicadores de 2026 y 2021 con la misma lista; "crece menos" significa que la variación sigue siendo positiva pero menor.»

### A3. La dimensión de confianza premia empezar con baja aprobación · ALTA
- **Cita:** «Confianza ciudadana (ajustada por luna de miel) (15 %) … Puntaje = 50 + 2,5 × (Δ + 10). 68 Regular | 33 Malo».
- **Problema:** Castillo empezó en 38 % y terminó en 35 %; Keiko empezó en 57 % y terminó en 40 %. Al día 100, Keiko tiene **más** aprobación que Castillo, pero esta dimensión le da 35 puntos menos (unos 5 puntos del índice total). La fórmula convierte el capital político inicial en una penalidad. Además, la medición de Keiko (campo del 7 y 8 de octubre, día ~71) no está a la misma distancia del día 100 que la de Castillo (12-nov, día ~107).
- **Reescritura:** puntuar 50 % por variación y 50 % por nivel al día 100, o mostrar las dos versiones. Texto de la fila: «Mitad: variación de la aprobación frente a la caída esperada de −10 puntos; mitad: nivel de aprobación en la medición más cercana al día 100. Fechas de campo: Keiko 7-8 oct (día 71); Castillo 12-nov (día 107).»

### A4. «Promesas de 100 días»: se compara un tracker estricto con otro laxo · ALTA
- **Cita:** «Promesas de 100 días (20 %) … 12 Crítico | 2 Crítico».
- **Problema:** para Keiko se usa el criterio más exigente disponible (solo cuenta si hay una norma en El Peruano); para Castillo, la clasificación periodística de EC Data, sin criterio operativo publicado (el propio sitio lo reconoce). La segunda medición del sitio (Plan Perú 2050: «5 con norma») y Hildebrandt (1 de 67) dan cifras más altas para Keiko. Con universos y criterios distintos, la dimensión de mayor peso (20 %) no es comparable, y el sitio lo admite en la sección de Promesas pero igual la puntúa.
- **Reescritura:** mostrar un rango en lugar de un solo valor, «Keiko 2–8 (según tracker)», o bajar el peso de D1 al 10 % con esta nota: «Fuentes con criterios distintos: EC Data (periodístico, 2021) y Keiko Gobierna (norma publicada, 2026). Puntaje indicativo, no comparable uno a uno.»

### A5. Margen electoral y protestas de asunción solo para Keiko · MEDIA
- **Cita:** «Jura ante el Congreso tras ganar la segunda vuelta por menos de 50 000 votos.» y el hito «Opositores y familiares de víctimas de 2022-2023 protestan durante la asunción … familiares afirman no reconocer a la nueva presidenta.»
- **Problema:** Castillo ganó por ~44 000 votos y asumió en medio de un desconocimiento masivo del resultado, pero su hito del día 0 no menciona ni el margen ni la protesta. Solo a Keiko se le presenta como presidenta de legitimidad estrecha y disputada.
- **Reescritura (Keiko):** «Jura ante el Congreso tras ganar la segunda vuelta. En su primer mensaje promete combatir el crimen con "mano dura", subir el salario mínimo de S/1130 a S/1300 y duplicar Pensión 65 de S/350 a S/700.» Para mantener el margen, agregar a Castillo: «…tras ganar la segunda vuelta por unos 44 000 votos y una proclamación demorada seis semanas por pedidos de nulidad.» (Ver B5 para la otra mitad.)

### A6. Detalles insinuantes en la línea de tiempo · MEDIA
| Cita exacta | Problema | Reescritura |
|---|---|---|
| «El reglamento, anunciado en el balance de los 100 días, se firma en el colegio donde estudió Alberto Fujimori.» | El dato no aporta información de gestión y asocia la medida con el expresidente condenado. | «Los lineamientos, anunciados en el balance de los 100 días, se firman en una ceremonia en un colegio de Lima. [Si ya fueron aprobados, citar la norma; si no, indicar "proyecto prepublicado por la RM 613-2026-MINEDU".]» |
| «…sube la proyección de 3,2 % a 3,4 % pese al riesgo de El Niño; aún lejos del 6 % ofrecido en campaña.» | Comentario editorial; no se contrasta ninguna proyección de 2021 con las promesas de campaña de Castillo. | «…sube la proyección de 3,2 % a 3,4 % pese al riesgo de El Niño. El plan de gobierno planteaba un crecimiento de 6 %.» (o eliminar la coletilla) |
| «Mensaje por los 100 días: el Gobierno reporta menos homicidios diarios y admite lentitud» | «Admite» enmarca la frase como confesión. | «Mensaje por los 100 días: el Gobierno reporta menos homicidios diarios y dice que "siempre se pueden hacer cosas con mayor rapidez"» |
| «…la visita recibe críticas por su beneficio concreto.» | Críticos sin nombre ni fuente. | «…anuncia dos megapenales. [Medio X] cuestionó el beneficio concreto de la visita.» (o eliminar) |
| «en Lima se reporta represión policial al anochecer.» | «Represión» es un término valorativo, no descriptivo. | «en Lima, Infobae reporta enfrentamientos con la policía al anochecer.» |
| «Primera baja del gabinete: renuncia Rafael Rey al MTC», con tono «negativo» | Una renuncia por salud no es un hecho negativo de gestión, y «baja» la equipara con la de Béjar. | Título: «Rafael Rey deja el MTC por motivos de salud»; tono: **neutro**. |

### A7. «Calló» y «Solo»: verbos cargados en la síntesis del mensaje · MEDIA
- **Citas:** «Calló lo que empeora en la brújula 2050.» · «Solo 6 de las 31 afirmaciones con cifra coinciden sin reparos…»
- **Problema:** «Calló» atribuye intención de ocultar. «Solo» orienta la lectura cuando el mismo dato admite decir que 19 de 31 coinciden total o parcialmente.
- **Reescritura:** «El mensaje no mencionó los indicadores que empeoraron en la brújula 2050: la inflación de Lima subió de 4,07 % a 5,25 %…» · «De 31 afirmaciones con cifra, 6 coinciden con fuentes oficiales, 13 coinciden con matices, 6 no coinciden y 6 no tienen fuente independiente.»

### A8. Ledger: a Castillo se le acredita lo heredado y a Keiko se le descuenta · MEDIA
- **Cita (Castillo, avanzó):** «23.4 M dosis de vacuna aplicadas en la ventana (el doble que en los 100 días previos)» · «+8.8 % la Bolsa de Lima, desde un nivel deprimido»
- **Problema:** el propio sitio dice que el ritmo de vacunación «depende sobre todo de la llegada de vacunas compradas antes (gobierno de Sagasti)», pero el ledger lo pone como avance sin esa salvedad. A Keiko no se le acreditan el desempleo de Lima en su mínimo de la serie (4,4 %), las exportaciones récord ni la baja del riesgo país, porque «son tendencias que ya venían de antes». El criterio de qué cuenta como avance no es el mismo para los dos.
- **Reescritura (Castillo):** «23.4 M dosis aplicadas en la ventana, el doble que en los 100 días previos (con vacunas compradas en gran parte por el gobierno anterior)». **Agregar a Keiko (avanzó):** «Desempleo de Lima en **4,4 %**, el más bajo de la serie, que empieza en 2001 (tendencia previa, no atribuible solo al gobierno)».

### A9. El ledger da por causa la caída de la Bolsa con Keiko · BAJA
- **Cita:** «−4.0 % la Bolsa de Lima, aunque el cobre subió 4 %»
- **Problema:** «aunque» insinúa una causa local, mientras el método dice «no se atribuyen causalmente al gobierno». (El mismo problema aparece con el dólar de Castillo; ver B7.)
- **Reescritura:** «−4.0 % la Bolsa de Lima (el cobre, control externo, subió 4 %)».

### A10. Etiquetas de los videos · BAJA
- **Cita:** «Arde Troya con Juliana Oxenford · independiente» y la nota de método «(Arde Troya y La Encerrona son críticos del fujimorismo)».
- **Problema:** el método reconoce una línea crítica que la etiqueta visible oculta.
- **Reescritura:** etiquetar «independiente (crítico del fujimorismo)» en Arde Troya y «independiente (crítico de Castillo y del fujimorismo)» en La Encerrona.

### A11. El helicóptero de Tumbes se atribuye «al gobierno» sin más · MEDIA
- **Cita (conclusión):** «solo uno (el helicóptero del premier en Tumbes) es atribuible al gobierno, y ningún colegio quedó destruido.»
- **Problema:** el detalle del caso dice que es un incidente operativo (la ráfaga de las hélices al aterrizar), con daños sobre todo en viviendas, versiones discrepantes sobre el colegio y reparaciones del Ejército y la municipalidad. «Atribuible al gobierno» sugiere una decisión o una política.
- **Reescritura:** «solo uno se vincula a una acción del Gobierno central: el aterrizaje del helicóptero que trasladaba al premier en Casitas (Tumbes) dañó techos de viviendas y, según dos medios, parte de un colegio. Los otros tres son deterioro de infraestructura antigua o un accidente en una obra regional. Ningún colegio quedó destruido.»

---

## 2. Crítico B (simpatizante de Perú Libre o de la izquierda): sesgo contra Pedro Castillo

### B1. El índice puntúa la «idoneidad» de Castillo y no la «integridad» del gabinete de Keiko · ALTA
- **Cita:** «Estabilidad e idoneidad del gabinete (15 %) … 48 Malo | 76 Bien» e «Integridad (15 %) Sin puntaje: las fuentes no son comparables… Se muestran los conteos crudos.»
- **Problema:** la dimensión en la que Castillo sale peor (perfil académico y experiencia de sus ministros) sí se puntúa. La dimensión en la que el gabinete de Keiko sale peor (15 de 19 ministros con investigaciones o procesos en sus declaraciones juradas, según La República del 30-jul-2026, frente a 5 de Castillo) no se puntúa, y los «conteos crudos» solo aparecen en un *tooltip* que no se ve en el celular. La justificación («castigaría la mayor transparencia») es razonable, pero se aplica en una sola dirección. Además, «idoneidad» mide credenciales formales y puede penalizar a gabinetes de origen popular o sindical.
- **Reescritura:** mostrar los conteos de integridad como texto visible en la celda: «Castillo 5 · Keiko 15 (de 19) · PPK 0 · Humala 1 · García 0 — no comparables: 2026 sale de declaraciones juradas obligatorias». Y aplicar la misma regla a idoneidad (puntuar solo la permanencia) o puntuar ambas con caveat. En la conclusión, cambiar «Castillo falló en gobernabilidad e idoneidad del gabinete» por la versión de B2.

### B2. La conclusión carga la inestabilidad a Castillo sin mencionar al Congreso · ALTA
- **Cita:** «Igual de malos en el total, pero por razones opuestas: Castillo falló en gobernabilidad e idoneidad del gabinete; Keiko, en cumplir su propia hoja de 100 días y en sostener la confianza que recibió.» y «Castillo: 2 premieres, 9 ministros salientes, 2 votos de confianza ajustados…»
- **Problema:** (a) «Falló» es un veredicto; para Keiko el texto no usa ese verbo. (b) No se menciona que el Congreso de 2021 era mayoritariamente opositor (FP, RP y Avanza País votaron contra la confianza) y aprobó la Ley 31355, que limitó la cuestión de confianza. (c) Keiko no tuvo que pasar un voto de investidura (por la reforma bicameral), así que la «estabilidad» no se mide en las mismas condiciones. (d) 73-50 no es un voto «ajustado».
- **Reescritura:** «Con puntajes similares, pero por razones distintas: Castillo puntúa bajo en estabilidad y perfil del gabinete (2 premieres y 9 salidas, frente a un Congreso mayoritariamente opositor); Keiko puntúa bajo en avance acreditado de su plan de 100 días y en variación de la aprobación (con un Congreso que le recortó las facultades pedidas). Su gabinete no requirió voto de investidura.» · «Castillo: 2 premieres, 9 ministros salientes, 2 votos de confianza aprobados (73-50 y 68-56)…»

### B3. La escalera del valor público deja fuera los dos productos más grandes de Castillo · ALTA
- **Cita:** escalera de Castillo con solo 3 puntos, «retorno seguro (actividad)», «Segunda reforma agraria (actividad)» y «20 millones de mascarillas (producto)»; en Keiko se incluye «Aumentar la RMV … (anunciado en el mensaje del 28-jul; **no figura en la lista de 100 días del plan**) producto».
- **Problema:** para Keiko se admite una medida fuera de su lista de 100 días; para Castillo se excluyen el **Bono Yanapay** (pagado desde el 13-set a ~14 M de personas, un producto) y la **vacunación** (compromiso del plan Bicentenario p8, 23,4 M dosis, un producto). Con esos dos, D2 de Castillo pasa de 33 a ~40. Además, a Pensión 65 a S/700 (que se paga desde el 30-nov, fuera de la ventana) el ledger le asigna «producto», cuando al día 100 era un crédito presupuestal (insumo).
- **Reescritura:** agregar a Castillo «Bono Yanapay de S/350 (pago desde el 13-set-2021) — producto» y «Vacunación COVID: 23,4 M dosis en la ventana (compromiso del plan Bicentenario, p8) — producto». En el ledger de Keiko: «Salario mínimo a S/1,230 (producto) y Pensión 65 a S/700 aprobada en el crédito suplementario, con pago desde el 30-nov (insumo al día 100)».

### B4. La categoría «Corrupción/investigaciones» muestra 0 para Keiko por falta de búsqueda · ALTA
- **Cita:** filtro de la línea de tiempo «Corrupcion investigaciones» (Castillo 1, Keiko 0) y, solo en Método: «El 0 en esta categoría refleja un vacío de la verificación, no una ausencia comprobada.»
- **Problema:** el lector del filtro ve «Keiko: 0». Hay hitos fechados y con fuente dentro de la ventana que ya están en `idoneidad.json`: «15 de 19 ministros declararon investigaciones o procesos» (La República, 30-jul-2026; N60, 31-jul-2026). Tampoco aparecen el incidente del helicóptero del premier en Tumbes (29-oct), que el propio sitio califica de atribuible, ni la polémica del ministro Chang sobre «retirar la ideología» del currículo (14-set, que solo está en Videos).
- **Reescritura:** agregar los hitos 30-jul-2026, «La República: 15 de 19 ministros declararon investigaciones o procesos en sus declaraciones juradas (ninguna es condena, salvo un caso rehabilitado)», tono negativo, categoría Corrupción/investigaciones; y 29-oct-2026, «El helicóptero que trasladaba al premier Galarreta daña techos de viviendas y, según dos medios, de un colegio en Casitas (Tumbes)», tono negativo, categoría Gabinete. Si el vacío persiste, mostrar en el filtro: «Keiko: sin hitos verificados (búsqueda incompleta)».

### B5. Falta el contexto del 2021: desconocimiento del resultado y Congreso hostil · MEDIA
- **Cita:** hito del día 0: «Castillo asume la presidencia y anuncia proyecto de Asamblea Constituyente… las bancadas reaccionaron de forma dividida.»
- **Problema:** a Keiko se le da el contexto de la protesta del día 0; a Castillo no se le da el contexto de que asumió tras seis semanas de pedidos de nulidad y denuncias de fraude sin pruebas por parte de Fuerza Popular. Esa herencia de deslegitimación explica en parte la gobernabilidad que el índice le cobra.
- **Reescritura:** «Castillo asume la presidencia tras una proclamación demorada seis semanas por pedidos de nulidad de Fuerza Popular, que el JNE rechazó. En su mensaje anuncia un proyecto de reforma para convocar una Asamblea Constituyente…»

### B6. Videos: Castillo no tiene ninguna voz que lo defienda y sí un escándalo de fuera de la ventana · ALTA
- **Citas:** «Secretario de Castillo guardaba US$20 mil en efectivo en un baño de Palacio — Peru21TV · 23 nov 2021 · derecha» · «Casto Ocando ▶ FORO «¿100 días de castrochavismo en el Perú?» — Wenceslao Cruz · derecha».
- **Problema:** (a) El video de Pacheco es del 23-nov, fuera de la ventana; para Keiko no hay un video equivalente de escándalo. (b) «Castrochavismo» es un rótulo propagandístico, y la fuente es un canal personal que vuelve a subir un foro. (c) Los 8 videos no oficiales de Castillo son críticos o neutros; ninguno lo defiende (incluso el de La República, «La victoria de Vladimir Cerrón», es crítico). Keiko tiene una defensa explícita (Carlos Mesía, «El balance es positivo») y 5 de sus 11 videos reproducen contenido oficial (TVPerú ×2, la transmisión del mensaje en Willax, la exposición de Galarreta y el mensaje completo en El Comercio).
- **Reescritura:** quitar el video de Pacheco (o moverlo a «Después del día 100» y agregar uno equivalente de Keiko). Reemplazar el foro de Casto Ocando por un análisis de derecha dentro de la ventana en un medio establecido. Agregar una voz que defienda los 100 días de Castillo (un ministro, un vocero de Perú Libre o un analista afín, en una entrevista de oct-nov 2021). Agregar el balance de Castillo del 10-nov-2021 en TVPerú si no se cuenta ya como oficial. Regla visible: «Por gobierno: 2 oficiales, 1 defensa, 2 críticas, 2 de análisis, todos dentro de la ventana».

### B7. Verbos y matices asimétricos en el ledger · MEDIA
| Cita exacta | Problema | Reescritura |
|---|---|---|
| Castillo: «**36 de 43** promesas incumplidas» · Keiko: «**0 de 67** acciones de 100 días acreditadas con una norma (3 en proceso)» | A Castillo se le dice «incumplidas»; a Keiko, «no acreditadas», un eufemismo técnico. | Castillo: «**3 de 43** cumplidas, 4 en proceso y 36 sin cumplir (EC Data)» · Keiko: «**0 de 67** cumplidas, 3 en proceso y 64 sin avance acreditado (Keiko Gobierna)». |
| Castillo: «+2.4 % el dólar (S/ 3.92 → 4.01), con el cobre plano: **fue presión local**» | Afirma una causa, contra el propio método («no se atribuyen causalmente al gobierno»). Además, el dólar ya había subido desde la primera vuelta. | «+2.4 % el dólar (S/ 3.92 → 4.01); el cobre, control externo, se mantuvo plano». |
| Castillo: «+8.8 % la Bolsa de Lima, **desde un nivel deprimido**» | Le resta mérito al único dato de mercado positivo de Castillo; a Keiko no se le descuenta nada similar. | «+8.8 % la Bolsa de Lima (el cobre, control externo, +0,4 %)». |
| Keiko: «**1** solo cambio de ministro, el mismo premier y facultades delegadas por 90 días» | Se presenta como avance la delegación de facultades, pero al día 100 había 0 decretos legislativos. A Castillo no se le acredita su pedido de facultades (ver 0.1). | «**1** cambio de ministro y el mismo premier; facultades delegadas por 90 días (27 de 66 materias), sin decretos legislativos al día 100». |

### B8. Falta la inflación en el ledger de Keiko y se atribuye la de 2021 a la política · MEDIA
- **Cita (Resultados, inflación de alimentos):** «En 2021 hubo un choque global de commodities y una depreciación del sol por la incertidumbre política: **esa parte sí es atribuible en parte a la coyuntura política.**» y, para 2026, «…clima (El Niño en 2026)…».
- **Problema:** a 2021 se le atribuye una parte política; a 2026, solo clima. La inflación de Lima en 2026 (5,3 %, la más alta desde ago-2023) no aparece en el ledger de Keiko, y tampoco el paro de transportistas por el diésel.
- **Reescritura:** «En 2021 coincidieron un choque global de commodities y una depreciación del sol asociada a la incertidumbre política. En 2026 pesan los choques de oferta (El Niño) y el alza del diésel.» En el ledger de Keiko, «Dónde se quedó corto», agregar: «Inflación de Lima **4,1 → 5,3 %**, la más alta desde ago-2023 (sobre todo choques de oferta)».

### B9. Tonos de la línea de tiempo: 7 positivos para Castillo y 10 para Keiko · MEDIA
- **Dato:** Castillo, 7 positivos, 9 negativos y 11 neutros; Keiko, 10 positivos, 6 negativos y 13 neutros (`noticias.json → conteos`).
- **Problema:** algunos tonos son discutibles: «La presidenta inspecciona un albergue y un hospital de campaña» (una visita protocolar, rotulada **positivo**); «Pasan al retiro a los comandantes generales» de Castillo (una prerrogativa legal, rotulada **negativo** cuando la denuncia ya tiene su propio hito); la Ley 31355 que recortó la cuestión de confianza (**neutro**, aunque restringió al Ejecutivo). Faltan hitos de Keiko con tono negativo y con fuente (ver B4) y positivos de Castillo, como la juramentación de Pedro Francke en el MEF, que calmó a los mercados (solo se menciona de pasada).
- **Reescritura:** inspección en Tumbes → tono **neutro**; retiro de los comandantes → **neutro** (la denuncia del 6-nov se queda como negativo); agregar para Castillo, el 29/30-jul-2021: «Pedro Francke jura como ministro de Economía y anuncia respeto a la autonomía del BCR; el dólar retrocede», tono positivo [verificar la fecha y el movimiento del tipo de cambio].

### B10. Contexto pandémico ausente en la conclusión y el ledger · BAJA
- **Problema:** la pandemia (2021) y El Niño (2026) solo aparecen en las notas técnicas. Ninguno de los dos tiene contexto atenuante en la conclusión, lo que es simétrico, pero el lector del ledger no sabe que Castillo gobernaba con restricciones sanitarias y Keiko frente a una emergencia climática.
- **Reescritura (agregar al final de la nota del ledger):** «Contexto que ninguno controlaba: Castillo asumió en plena pandemia (restricciones sanitarias, rebote estadístico de 2020) y Keiko frente a un Niño Costero pronosticado como extraordinario.»

---

## 3. Elementos transversales (hero, conclusión, colores, orden)

### T1. El título del hero induce la conclusión · ALTA (lo señalan los dos críticos)
- **Cita:** «Resultados = valor público. ¿Alguno lo tiene?» — comentario en un grupo de WhatsApp, 7-nov-2026
- **Problema:** el H1 adopta como titular la premisa que el propio sitio califica de «Cierto, pero prematuro». La pregunta retórica empuja hacia «ninguno». Una cita anónima de WhatsApp como H1 resta seriedad y no es verificable.
- **Reescritura:**
  - H1: «Los primeros 100 días de Keiko Fujimori y Pedro Castillo, con datos»
  - Kicker o cita bajo el H1: «La pregunta que motivó esta revisión, tomada de un chat: «Resultados = valor público. ¿Alguno lo tiene?». Respuesta corta: a los 100 días todavía no se puede medir.»

### T2. «✓ Cierto en el total» e «Igual de malos» · ALTA (los dos críticos)
- **Cita:** «✓ Cierto en el total» / «*Igual de malos* en el total»
- **Problema:** se rotula como «Cierto» un juicio de valor que sale de un índice propio, con pesos elegidos por el autor, cobertura del 75 al 85 % y una diferencia de 0,3 puntos que se invierte con pesos iguales (42,0 frente a 42,3). Si se retira D5 (ver A1), Castillo queda en ~40,8 y Keiko en ~39,0; si D6 usa el nivel de aprobación (ver A3), el orden cambia. Es un empate técnico, no una verdad verificada.
- **Reescritura:** sello «≈ Empate técnico». H3: «¿Son igual de malos los 100 días de ambos?». Texto: «En nuestro índice, ambos quedan en el tramo 30-49 (40,6 y 40,3; con pesos iguales, 42,0 y 42,3). La diferencia es menor que la incertidumbre del método, y la composición es distinta…». En la entradilla, cambiar «*Igual de malos* en el total» por «Con puntajes casi iguales».

### T3. Colores: Keiko lleva el naranja de su partido, que además coincide con el tramo «Malo» · MEDIA
- **Cita:** `styles.css`: `--keiko: #eb6834` (naranja Fuerza Popular), `--castillo: #2a78d6` (azul, no es el color de Perú Libre); conclusión: «quedan prácticamente empatados **en naranja**».
- **Problema:** (A) el color de Keiko se confunde con el naranja del semáforo, que significa «Malo». (B) solo un gobierno lleva su color partidario, lo que puede leerse como identificación de marca a su favor. En cualquier caso, la asimetría es evitable.
- **Reescritura:** usar colores neutros y no partidarios para ambos, lejos de la escala del semáforo (por ejemplo, Castillo `#2a78d6` y Keiko `#7a4fd1`, violeta). En el texto: «quedan prácticamente empatados en el tramo "Malo" (30-49)».

### T4. Orden de presentación · BAJA
- **Hallazgo:** Castillo va siempre primero (orden fijo `ORDER`), y el og:title dice «Keiko 2026 vs. Castillo 2021». Es defendible por cronología. No se detecta preferencia, pero conviene declararlo.
- **Reescritura (Método):** «Los gobiernos se ordenan cronológicamente entre los dos comparados (2021, 2026) y luego los de contexto; el orden no implica jerarquía.» Y og:title: «100 días bajo la lupa: Castillo 2021 y Keiko 2026».

### T5. Hero: cifras provisionales sin rótulo · BAJA
- **Cita:** tarjeta de Keiko: «+4.3% homicidios (SINADEF) frente a los 100 días previos»
- **Problema:** la cifra de 2026 es provisional (el SINADEF registra con retraso y tiende a subir), algo que el ledger sí aclara y el hero no.
- **Reescritura:** «+4.3 % homicidios (SINADEF, provisional) frente a los 100 días previos».

---

## 4. Hechos omitidos por gobierno (cherry-picking)

| Gobierno | Omisiones que señala A (contra Castillo) o B (contra Keiko) | Omisiones que señala B (a favor de Castillo) o A (a favor de Keiko) |
|---|---|---|
| **Castillo 2021** | Reuniones en la casa de Sarratea (Breña) y visitas de Karelim López a Palacio dentro de la ventana, reveladas a mediados de nov-2021 [**verificar fechas**]; nombramiento en Petroperú y licitación de biodiésel (Heaven Petroleum) [**verificar si cae antes del 5-nov**]; investigación fiscal a Bellido por apología (ago-2021); designación de Barranzuela (6-oct), abogado de Cerrón; frase de Bellido a la congresista Chirinos (set-2021). Hoy la categoría de corrupción de Castillo tiene **1** hito, y es del día 101. | Bono Yanapay y vacunación en la escalera (ver B3); pedido de facultades tributarias (ver 0.1); Francke en el MEF y ratificación de Velarde como señales de moderación; retorno escalonado a clases. |
| **Keiko 2026** | 15 de 19 ministros con investigaciones declaradas (30-jul); helicóptero del premier en Tumbes (29-oct) fuera de la línea de tiempo; contratos en Cultura (Beingolea) sin verificar; polémica curricular de Chang (14-set); inflación al máximo desde 2023; expectativa empresarial en tramo pesimista; 0 decretos legislativos al día 100. | Desempleo de Lima en su mínimo de la serie; adhesión al Escudo de las Américas y capturas con FBI y Bolivia (verificadas como «Coincide»); 980 ha recuperadas en Tambopata; reinicio del Tren Macho; inicio de la Torre Trecca; 6 500 laptops para los COAR; retorno de embajadores con Colombia y México (sí están). |

**Recomendación:** agregar al ledger una línea «Polémicas o investigaciones abiertas en la ventana» para **los dos** gobiernos, con la misma regla (hecho fechado, fuente primaria o dos medios, «ninguna investigación es una condena»).

---

## 5. Atribución del helicóptero de Tumbes y de los colegios

- **Coherente en lo esencial:** el sitio no le atribuye al Gobierno los colapsos por deterioro de Villa El Salvador y Ate ni el accidente de la obra regional de Junín, y aclara que ningún colegio quedó destruido. Es correcto y protege a Keiko de una infografía engañosa.
- **Desajustes:**
  1. En la conclusión, «atribuible al gobierno» es más fuerte que el detalle del caso (ver A11).
  2. El caso 1 lleva el veredicto «Engañoso» aunque el hecho existe y es atribuible a la comitiva; lo exagerado es «le arrancó los techos al colegio». Neutral: **«Exagerado»** o «Verdadero con matices».
  3. El incidente atribuible no figura en la línea de tiempo (ver B4).
  4. El método menciona a «Morca» sin explicarlo en ninguna sección visible: o se explica o se quita.
- **«0 construidos»:** la explicación («todo lo inaugurado en los primeros 100 días de cualquier gobierno es obra heredada») es justa y se aplica igual a los dos. Sin cambios.

---

## 6. Veredicto global

**El sitio no es propagandístico para ninguno de los dos, y su método es más honesto que el de la mayoría de los comparativos:** declara límites, usa el cobre como control externo, advierte que 100 días no alcanzan para ver resultados y no compara la integridad de forma injusta. El tono general es sobrio, y la conclusión de «empate con composición opuesta» es defendible.

Aun así, **los dos críticos tienen casos sólidos**, y tienden a compensarse en el total más que a desaparecer:

- **Contra Keiko (A):** el escrutinio no es simétrico. Hay una sección de 31 chequeos y una «brújula» solo para su gobierno, una fórmula de confianza que convierte su mayor aprobación al día 100 en un puntaje menor, un tracker de promesas más estricto que el de Castillo, verbos como «calló» y detalles insinuantes («el colegio donde estudió Alberto Fujimori», «menos de 50 000 votos»).
- **Contra Castillo (B):** la selección no es simétrica. Su escalera excluye Yanapay y la vacunación mientras la de Keiko admite medidas fuera de su lista. Se le puntúa la «idoneidad», pero no se puntúa la «integridad» del gabinete de Keiko (15 de 19 con investigaciones, solo en un *tooltip*). Hay un falso «No pidió facultades», un ledger que dice «incumplidas» para él y «no acreditadas» para ella, videos sin una sola voz que lo defienda y con un escándalo de fuera de la ventana, y una línea de tiempo con más positivos para Keiko (10 frente a 7) y un 0 en corrupción que se explica por falta de búsqueda.

**Prioridad de corrección (en este orden):** (1) incoherencias factuales 0.1 y 0.4; (2) hero y sello «Cierto» (T1, T2); (3) simetría de escrutinio: verificar el mensaje de Castillo o sacar D5, y hacer brújula para ambos o para ninguno (A1, A2); (4) reglas idénticas para la escalera y para integridad e idoneidad (B1, B3); (5) fórmula de D6 y rango en D1 (A3, A4); (6) videos (B6); (7) tonos y verbos de la línea de tiempo y del ledger (A6, A7, B7, B9); (8) colores (T3).

**Calificación de neutralidad actual: 6,5/10.** Con las correcciones de prioridad 1 a 5, el sitio podría resistir una revisión hostil de cualquiera de los dos lados (≈8,5/10).
