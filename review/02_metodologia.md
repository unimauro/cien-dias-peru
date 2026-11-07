# Revisión adversarial 02: metodología del «Índice de los 100 Días»

Revisión con el rigor del *Handbook on Constructing Composite Indicators* (OECD/JRC, 2008): marco teórico, imputación de faltantes, normalización, ponderación, agregación, y análisis de incertidumbre y sensibilidad.

- **Revisado:** `etl/build_indice.py`, `research/indice100.json`, `research/intl_marcos.json` (propuesta original) e insumos (`castillo.json`, `keiko.json`, `expresidentes.json`, `idoneidad.json`, `performance.json`, `pp2050_mensaje.json`, `intl_*.json`) y el texto del veredicto en `index.html` (líneas 58 y 64).
- **Reproducción:** los scripts de las variantes se ejecutaron en una copia aparte (`sens.py`, `run.py` y `run2.py`, en el scratchpad de la sesión). No se modificó ningún archivo del repo. La línea base reproduce exactamente lo publicado: Castillo 40,6, Keiko 40,3 y PPK 49,6.

---

## Veredicto

**El empate en 40,6 frente a 40,3 no es robusto como cifra; solo es robusto como «no distinguibles».** De las 35 variantes calculadas (0-34 y 6b):

- la diferencia Castillo − Keiko va de **−8,1 a +10,3** puntos (de +22,9 con agregación por rangos);
- el orden entre los dos **se invierte en 13 variantes**;
- en una simulación Monte Carlo con 20 000 combinaciones de pesos aleatorios y fórmulas alternativas, Castillo supera a Keiko en el **42 %** de los casos. La diferencia mediana es de −1,6, con un intervalo del 5 % al 95 % de **[−13,9; +12,5]**. Solo el 18 % de las simulaciones da una diferencia menor a 2 puntos.

El 0,3 de diferencia equivale a mucho menos que el efecto de reclasificar **una sola** promesa de Castillo en D2, donde n = 3 (ese cambio mueve el total ±1,1).

Además, el empate nace de la **compensación** entre perfiles opuestos: Castillo gana en D6 (67,5 frente a 32,5) y Keiko en D3 (76,3 frente a 47,7) y en D7 (64,3 frente a 50,1). Si se quita solo D6, Keiko queda 8 puntos arriba. Con una agregación no compensatoria (media geométrica), Castillo queda 10 puntos arriba.

Lo que sí resiste es que **PPK queda por encima de ambos** en todas las variantes salvo una (la 33, ilustrativa) y en el 69 % de las simulaciones Monte Carlo, aunque eso descansa en un D1 de PPK inflado (hallazgo 2) y en su D3.

---

## Tabla de sensibilidad

Entre paréntesis va el total que se obtendría aunque la cobertura no llegue al umbral (no se publicaría). Los pesos son los de la propuesta salvo que se indique otra cosa: D1 20, D2 10, D3 15, D5 10, D6 15 y D7 15; D4 vale 15, pero siempre queda sin dato.

| # | Esquema | Castillo | Keiko | PPK | Humala | García | Castillo − Keiko |
|---|---|---|---|---|---|---|---|
| 0 | **Publicado** (umbral del 70 %) | **40,6** | **40,3** | **49,6** | (60,7) | (54,5) | +0,3 |
| 1 | Pesos iguales | 42,0 | 42,3 | 49,0 | (58,1) | (50,7) | −0,3 |
| 2 | Sin D6 | 33,9 | 42,0 | 49,6 | (54,4) | (52,5) | **−8,1** |
| 3 | Sin D7 | 38,2 | 35,2 | 50,5 | (68,4) | (56,5) | +3,0 |
| 4 | D1 al doble (40) | 34,5 | 33,1 | 46,3 | (60,7) | (54,5) | +1,4 |
| 5 | Solo dimensiones con dato para los tres (sin D5) | 40,6 | 39,0 | 49,6 | (60,7) | (54,5) | +1,6 |
| 6 | Umbral de cobertura del 60 % | 40,6 | 40,3 | 49,6 | (60,7) | (54,5) | +0,3 (sin cambios: García y Humala tienen 55 %) |
| 6b | Umbral del 55 % | 40,6 | 40,3 | 49,6 | **60,7** | **54,5** | +0,3 |
| 7 | Sin D1 | (51,1) | 52,0 | (55,3) | (60,7) | (54,5) | (−0,9) |
| 8 | Solo D1, D2, D3 y D5 | (28,5) | 35,9 | (50,6) | (63,0) | (54,4) | (−7,4) |
| **D6** | | | | | | | |
| 9 | D6 = nivel absoluto de aprobación al ~día 100 | 34,1 | 41,6 | 49,8 | (54,8) | (53,7) | **−7,5** |
| 10 | D6 = caída esperada proporcional al nivel inicial (−10 × a/55) | 39,1 | 40,5 | 50,2 | (60,7) | (55,5) | −1,4 |
| 11 | D6 = caída relativa (Δ/a) frente a −18,2 % | 39,9 | 40,6 | 50,1 | (60,7) | (55,0) | −0,7 |
| 12 | D6 = 50 % luna de miel y 50 % nivel | 37,3 | 41,0 | 49,7 | (57,8) | (54,1) | −3,7 |
| **D7** | | | | | | | |
| 13 | D7 = solo agosto-octubre (todo el gasto) | 42,5 | 39,9 | 49,1 | (57,9) | (56,2) | +2,6 |
| 14 | D7 = agosto-octubre, solo inversión (como pedía la propuesta) | 44,5 | 38,8 | 49,6 | (63,0) | (49,3) | **+5,7** |
| 15 | D7 = agosto-octubre / saldo del PIM al 31 de julio | 41,6 | 42,6 | 48,6 | (56,6) | (55,2) | −1,0 |
| 34 | D7 publicado, con el PIM de 2026 un 3 % mayor (aprox. al PIM final) | 40,8 | 39,4 | 49,9 | (61,0) | (54,9) | +1,4 |
| **D1 y D2** | | | | | | | |
| 16 | D2 estricto (sin «cumplida parcialmente» ni «cumplida (creación)») | 40,6 | 40,6 | 49,6 | (59,8) | (53,0) | 0,0 |
| 32 | D2 con la regla «toda norma = insumo» | 40,6 | 38,6 | 49,6 | (57,1) | (53,0) | +2,0 |
| 17 | D1 de Keiko según el Observatorio (6 en proceso de 68) | 40,6 | 40,8 | 49,6 | (60,7) | (54,5) | −0,2 |
| 18 | D1 de Keiko según Hildebrandt (1 cumplida y 8 en proceso de 67) | 40,6 | 41,5 | 49,6 | (60,7) | (54,5) | −0,9 |
| 19 | D1 de PPK sobre las 21 promesas categorizadas | 40,6 | 40,3 | 51,4 | (60,7) | (54,5) | +0,3 |
| 20 | D1 de PPK sobre las 29 anunciadas | 40,6 | 40,3 | 48,4 | (60,7) | (54,5) | +0,3 |
| 21 | D1 con la escala PolitiFact de la propuesta (en proceso = 0,3) | 40,1 | 40,1 | 49,6 | (60,7) | (54,5) | 0,0 |
| 33 | D1 con las listas que codificó el proyecto (ilustrativo) | 45,3 | 51,6 | 49,6 | (60,7) | (54,5) | **−6,3** |
| **D3 y D4** | | | | | | | |
| 22 | D3 con la experiencia de Francke y Torres recodificada a «sí» | 40,9 | 40,3 | 49,6 | (60,7) | (54,5) | +0,6 |
| 31 | D4 incluida (100 × proporción de ministros sin investigación reportada) | 45,6 | 37,4 | 58,0 | 67,9 | 64,3 | **+8,2** |
| **Normalización y agregación** | | | | | | | |
| 23 | Media geométrica | 33,8 | 23,5 | 45,6 | (55,9) | (43,7) | **+10,3** |
| 24 | Min-máx entre los gobiernos, por dimensión | 45,0 | 45,0 | 68,5 | (67,2) | (51,2) | 0,0 |
| 25 | Puntaje z entre los gobiernos (50 + 15z) | 46,8 | 47,5 | 55,1 | (54,0) | (47,3) | −0,7 |
| 26 | Rangos (Borda) entre los gobiernos | 56,7 | 33,8 | 60,0 | (54,5) | (47,7) | **+22,9** |
| **Combinados** | | | | | | | |
| 27 | Corregido A: D6 proporcional, D7 agosto-octubre, D2 estricto y sin D5 | 41,0 | 39,0 | 49,6 | (57,0) | (55,7) | +2,0 |
| 28 | Corregido B: D6 nivel, D7 inversión agosto-octubre, D2 estricto y sin D5 | 38,0 | 39,2 | 49,8 | (56,2) | (46,9) | −1,2 |
| 29 | Corregido A con el D1 de Keiko según el Observatorio | 41,0 | 39,6 | 49,6 | (57,0) | (55,7) | +1,4 |
| 30 | Solo D3, D6 y D7 (las únicas con dato para los cinco) | 55,1 | 57,7 | 62,1 | 67,5 | 64,8 | −2,6 |

**Monte Carlo** (N = 20 000): pesos tomados de una distribución Dirichlet(1); D5 incluida en la mitad de los casos; fórmula de D6 elegida entre {publicada, proporcional, nivel, relativa, mixta}, la de D7 entre {publicada, agosto-octubre, inversión agosto-octubre, saldo} y la de D2 entre {publicada, estricta}; D1 de Keiko elegido entre {Keiko Gobierna, Observatorio, Hildebrandt, escala PolitiFact}. Resultados: P(Castillo > Keiko) = 0,42; P(|diferencia| < 2) = 0,18; P(PPK primero) = 0,69; diferencia en los percentiles 5, 50 y 95 = −13,9, −1,6 y +12,5.

---

## Hallazgos, de mayor a menor severidad

### CRÍTICO 1. El «empate» se presenta con una precisión que el índice no tiene, y el veredicto dice «igual de malos»

- **Problema.** Se publican décimas (40,6 frente a 40,3) y se concluye que son «igual de malos» (index.html:58). La incertidumbre de la propia construcción (pesos, fórmulas de D6 y D7, codificación de D2 y fuente de D1) es de ±13 puntos. El Handbook OECD/JRC pide acompañar el índice de un análisis de incertidumbre y sensibilidad. Hoy solo se reporta una variante (pesos iguales), y en ella el orden ya se invierte (42,0 frente a 42,3), lo que el texto menciona sin sacar la conclusión.
- **Compensabilidad.** La media aritmética permite que un 67,5 en aprobación «pague» un 11,6 en promesas. Los perfiles son opuestos, así que la cifra total oculta justo lo que interesa.
- **Corrección.**
  1. Publicar el total redondeado a enteros y con un **rango de sensibilidad**: el percentil 5-95 del Monte Carlo o, como mínimo, el mínimo y el máximo de las variantes 0-30.
  2. Agregar al panel la tabla de sensibilidad o un gráfico de bigotes.
  3. Reemplazar «igual de malos» por una formulación de indistinguibilidad.
  4. Mostrar el perfil por dimensión (gráfico de radar o barras) como resultado principal y el total como secundario.
- **Redacción sugerida:** «En nuestro índice experimental, Castillo (≈41) y Keiko (≈40) caen en la misma franja naranja. La diferencia entre ambos no es significativa: según cómo se midan la aprobación, el gasto y las promesas, cualquiera de los dos puede quedar arriba por hasta 8-10 puntos. Lo que sí se mantiene es que llegan al día 100 por caminos opuestos: Castillo, con un gabinete inestable y poco idóneo; Keiko, sin cumplir su hoja de 100 días y perdiendo 17 puntos de aprobación. PPK queda por encima de ambos en casi todas las variantes.»

### CRÍTICO 2. D1 pone en la misma fila tres instrumentos que miden cosas distintas, y contradice a D2

| | Castillo: ECData | Keiko: Keiko Gobierna | PPK: Convoca (vía América TV) |
|---|---|---|---|
| Universo | 43 promesas del plan de segunda vuelta y del discurso del 28 de julio | 67 acciones de la sección de 100 días del plan | 29 promesas que **el propio Ejecutivo anunció** para sus 100 días |
| Estándar de evidencia | Juicio periodístico con fuentes sectoriales y expertos | **Solo normas en El Peruano** («sin avance» no significa «no hecho») | Verificación periodística; categoría «engañosa» |
| Fecha | Día ~103 | Día 103 | **~enero de 2017 (día ~160+)** según el buscador; fuente secundaria |
| Problemas propios | Los porcentajes publicados no cuadran | Excluye las acciones sin norma (operativos, antenas, Comando) | 4 de las 29 sin explicar, y el código las cuenta como 0 (denominador 25 con 21 categorizadas) |

- **Sesgos de dirección conocida.** El D1 de PPK queda inflado: el gobierno eligió sus propias metas y se le midió más tarde. El D1 de Keiko queda deflactado por el estándar de «solo normas». Castillo queda en un punto intermedio.
- **Fragilidad.** Si se cambia el universo de promesas por las listas que el propio proyecto codificó (`keiko.json` y `castillo.json` → `promesas`), Keiko pasa de 2,2 a **50** y Castillo de 11,6 a 29,2 (variante 33: −6,3). Ninguna de esas listas es apta como sustituto, pero el ejercicio muestra que D1 mide sobre todo la elección del tracker.
- **Contradicción interna.** D1 de Keiko dice «0 cumplidas», pero D2 promedia la profundidad de **7 promesas «cumplidas»** del mismo gobierno. Un lector que vea las dos dimensiones recibe mensajes incompatibles.
- La escala usada (en proceso = 0,5) no es la de la propuesta (PolitiFact: en proceso = 0,3); ver la variante 21.
- **Corrección (en orden de preferencia).**
  - (a) Recodificar con **un mismo protocolo** las promesas de 100 días de los tres gobiernos: el mismo universo (plan + discurso del 28 de julio + presentación ante el Congreso), el mismo estándar de evidencia (norma, acto o entrega verificable), el mismo corte (día 100) y dos codificadores con kappa ≥ 0,7.
  - (b) Si no es posible, **sacar D1 del total** y mostrar los trackers como contexto, sin puntaje. En ese caso la cobertura de Castillo y PPK cae al 55 % y no habría total publicable bajo la regla actual, lo que debe decirse.
  - (c) Como mínimo, para PPK usar 21 en el denominador o marcar la cifra como fuera de la ventana.
- **Redacción sugerida (nota de D1):** «Las cifras de promesas no son comparables entre gobiernos: ECData (Castillo) evaluó el plan y el discurso con criterio periodístico; Keiko Gobierna solo cuenta normas publicadas en El Peruano; Convoca (PPK) evaluó las metas que el propio Ejecutivo anunció, y lo hizo meses después del día 100. Por eso las mostramos como referencia y no como medida homogénea.»

### CRÍTICO 3. D6 premia empezar bajo, y las mediciones no caen en el mismo día

- **Problema.** Con un Δ absoluto frente a −10 fijo, quien empieza en 38 % tiene menos que perder: la regresión a la media, más un piso de voto duro, hace que su caída esperada sea menor. Castillo obtiene 67,5, su mejor dimensión, y **sin D6 el empate desaparece (−8,1)**. Además:
  - el Δ de Castillo (−3, de 38 a 35 en Ipsos) está dentro del margen de error (±2,8 por medición), y el IEP declaró no significativa una caída parecida;
  - las fechas finales no son homogéneas: Keiko en el día ~72 (7-8 de octubre), García en el día ~76, Castillo en el día ~107 (12 de noviembre), PPK en el día ~105 y Humala en el día ~112. Medir antes favorece a quien sigue cayendo; en el caso de Castillo, el IEP de noviembre ya marcaba 25 %;
  - el −10 es un «valor de trabajo» no calibrado (lo admite la propuesta).
- **Alternativas calculadas:**

  | Fórmula de D6 | Castillo | Keiko | PPK | Humala | García |
  |---|---|---|---|---|---|
  | Publicada (Δ frente a −10) | 67,5 | 32,5 | 50,0 | 77,5 | 60,0 |
  | Caída esperada proporcional (−10 × a/55) | 59,8 | 33,4 | 52,7 | 77,5 | 63,6 |
  | Caída relativa (Δ/a frente a −18,2 %) | 64,2 | 34,0 | 52,5 | 77,5 | 61,9 |
  | Nivel absoluto al ~día 100 | 35 | 40 | 51 | 56 | 57 |
  | 50 % / 50 % | 51,2 | 36,2 | 50,5 | 66,8 | 58,5 |

- **Corrección.**
  1. Usar la **caída esperada proporcional al nivel inicial** (−10 × a/55) o, mejor, calibrarla con la Executive Approval Database. Con eso el total queda en 39,1 frente a 40,5.
  2. Exigir la medición de la **misma encuestadora más cercana al día 100**, y recalcular el dato de Keiko con Ipsos de noviembre de 2026 cuando salga.
  3. Si |Δ| es menor que el margen de error combinado (≈4 puntos), poner 50 (es decir, «sin diferencia con lo esperado»).
  4. Mostrar el nivel absoluto junto al puntaje, como ya pedía la propuesta.
- **Redacción sugerida:** «Confianza ciudadana: comparamos la caída de la aprobación con la que cabría esperar según el nivel de partida (quien empieza más alto suele caer más). Castillo bajó 3 puntos desde un 38 % (una variación dentro del margen de error) y Keiko, 17 puntos desde un 57 %. Las mediciones no son del mismo día: la de Keiko es del día ~72.»

### ALTO 4. D7 mide sobre todo el presupuesto del gobierno anterior, con denominadores que favorecen a 2026

- **Problemas.**
  1. Siete de los diez meses de la ventana enero-octubre son del gobierno saliente: alrededor del 67-70 % del devengado a octubre se hizo antes del 28 de julio.
  2. El PIM de 2026 es el vigente al ~6 de noviembre, mientras que el de los años cerrados es el **final**, que siempre es mayor. Eso infla el porcentaje de 2026. Con un PIM de 2026 un 3 % mayor, el D7 de Keiko baja de 64,3 a 59,4 (variante 34).
  3. ActProy está dominado por gasto inercial (planillas, pensiones), mientras que la propuesta pedía **inversión, agosto-octubre, frente a los 3 años previos**.
  4. El promedio de referencia incluye el propio año evaluado.
- **Alternativas** (`pct_ago_oct` agregado desde `ejecucion_sectorial` y `ejecucion_sectorial_proyectos`):

  | Medida | Castillo | Keiko | PPK | Humala | García |
  |---|---|---|---|---|---|
  | Enero-octubre, todo el gasto (publicada) | 70,3 % → **50,1** | 75,3 % → **64,3** | 69,0 % → 46,4 | 66,8 % → 40,1 | 70,0 % → 49,2 |
  | Agosto-octubre, todo el gasto | 23,6 % → 59,7 | 23,9 % → 61,7 | 21,8 % → 43,5 | 20,2 % → 29,7 | 23,1 % → 55,4 |
  | Agosto-octubre, solo inversión | 20,4 % → **69,8** | 19,1 % → **55,7** | 18,2 % → 46,1 | 18,4 % → 48,4 | 16,7 % → 29,9 |
  | Agosto-octubre / saldo al 31 de julio | 44,3 % → 54,9 | 49,1 % → 77,2 | 41,3 % → 41,0 | 37,8 % → 25,2 | 43,6 % → 51,7 |

  La ventana agosto-octubre sigue usando el PIM final de los años cerrados y el vigente de 2026 (es el mismo sesgo, aunque menor), y la variante «saldo» lo amplifica.
- **Corrección.**
  1. Usar **devengado de agosto a octubre de proyectos de inversión**, como pedía la propuesta (variante 14: total de 44,5 frente a 38,8).
  2. Para evitar el sesgo del PIM, usar como denominador el **devengado de agosto a octubre en términos reales** frente al promedio de los mismos meses en los años previos (crecimiento real), o el PIM a la misma fecha si se consigue la serie mensual.
  3. Promediar solo años anteriores al evaluado.
  4. Bajar el peso de D7 o marcarla como «herencia + gestión».
- **Redacción sugerida:** «Ejecución del gasto: solo cuenta lo devengado entre agosto y octubre en proyectos de inversión del Gobierno Nacional, que es lo que corresponde al nuevo gobierno. El PIM de 2026 todavía puede crecer hasta diciembre, así que el porcentaje de 2026 está levemente sobreestimado.»

### ALTO 5. Excluir D4 (integridad) no es neutral: equivale a imputarle a cada gobierno su propio promedio

- **Problema.** Al reescalar los pesos, la dimensión faltante se imputa implícitamente con el promedio de las demás dimensiones de cada gobierno (Handbook OECD/JRC, cap. sobre imputación). Eso beneficia a quien tiene más señales de integridad (Keiko: 15 de 19 ministros con investigación declarada) y perjudica a quien no tiene ninguna (PPK y García: 0). Con una D4 ingenua (proporción de ministros sin investigación reportada) el resultado es Castillo 45,6, Keiko 37,4 y PPK 58,0 (variante 31: +8,2). El argumento de que la declaración jurada de 2026 es más exhaustiva es válido, pero la solución adoptada **también sesga, en la dirección opuesta, y no se declara**.
- **Corrección.**
  1. Implementar D4 como la definía la propuesta: **solo actos formales de autoridad dentro de la ventana de 100 días** (formalización de la investigación, allanamiento, detención, acusación o informe de control), con ponderación por gravedad. Esa fuente (Ministerio Público, Poder Judicial, Contraloría y prensa que los reporta) existe para los cinco gobiernos y no depende de la Ley 31227.
  2. Mientras tanto, rotular el total como **«sin integridad»** y mostrar el rango con D4 = 0 y con D4 = 100 para cada gobierno.
- **Redacción sugerida:** «El total no incluye integridad. No es un dato neutro: al omitirla, el índice supone que cada gobierno es tan íntegro como su promedio en las otras dimensiones. Con una medida simple de ministros investigados, Keiko bajaría unos 3 puntos y Castillo subiría unos 5; no la usamos porque las fuentes de 2026 (declaraciones juradas) y de 2006-2021 (prensa) no son equivalentes.»

### ALTO 6. D2 tiene una codificación inconsistente, muestras mínimas y una contradicción con la regla declarada

- **Tamaños de muestra.** n = 3 (Castillo), 7 (Keiko), 4 (PPK), 5 (Humala) y 3 (García). Una sola promesa de Castillo mueve D2 ±8,3 y el total ±1,1, más que la diferencia publicada.
- **«Cumplida» se interpreta distinto.** `done()` acepta cualquier estado que empiece por «cumplid», incluidos «cumplida parcialmente» (facultades de Keiko, facultades y hospitales de PPK) y «cumplida (creación)» (Comando y Comisión de Keiko).
- **Mismo hecho, distinto nivel.**
  - *«Obtener facultades legislativas»:* **insumo** para PPK y **actividad** para Keiko.
  - *Leyes de creación:* MIDIS y la Ley de consulta previa (Humala) y Sierra Exportadora (García) son **actividad**, pero el gravamen minero (Humala) es **insumo**.
  - *Decretos:* el aumento de la RMV por decreto supremo es **producto** («producto regulatorio») para Keiko y Humala, pero el aumento a los policías (PPK) y la reducción de sueldos por decreto de urgencia (García) son **insumo**. La propuesta original decía «norma o dispositivo = 1 (insumo o habilitación)».
- **Escala que no coincide con la documentada.** La nota de método dice «(nivel − 1)/4», pero la propuesta tenía seis niveles (anuncio 0, norma 1, presupuesto 2, actividad 3, producto 4, resultado 5) y el código usa cinco etiquetas distintas (insumo 0 … impacto 100). No hay tabla de correspondencia.
- **Universos distintos.** Para Castillo se usaron las 12 promesas que ECData nombra; para Keiko, 20 promesas reunidas de varias fuentes; para los expresidentes, 7-8 «emblemáticas» elegidas por el proyecto.
- **Efecto.** Con la regla «toda norma = insumo» aplicada a todos, Keiko baja de 28,6 a 14,3 y Humala de 30 a 10 (variante 32: +2,0 para Castillo). Con el D2 estricto, empate exacto (variante 16).
- **Corrección.**
  1. Escribir un libro de códigos con ejemplos frontera (normas, creaciones, facultades, lanzamientos).
  2. Contar como «cumplida» solo la cumplida plena.
  3. Usar el mismo universo que D1.
  4. Exigir n ≥ 5 para puntuar.
  5. Dos codificadores y kappa reportado.
  6. Corregir la nota de método para que describa la escala realmente usada.
- **Redacción sugerida:** «Profundidad: clasificamos lo cumplido según su eslabón en la cadena de valor; toda norma cuenta como insumo. Con 3 a 7 promesas por gobierno, esta dimensión es muy sensible: reclasificar una sola promesa puede mover el total en más de un punto.»

### MEDIO 7. D3: la idoneidad se codificó con IA, sin revisión humana, y hay casos frontera resueltos de forma asimétrica

- **Estado de la codificación.** `idoneidad.json` declara «revisión humana pendiente» y que «se agotó el presupuesto de búsquedas». No hay segundo codificador ni kappa (la propuesta lo exigía).
- **Casos discutibles.**
  - *Pedro Francke (MEF), experiencia «parcial»:* exgerente general de EsSalud, exdirector de Foncodes y economista reconocido. El criterio dice «si» = «experto reconocido en la materia».
  - *Aníbal Torres (Justicia), «parcial»:* catedrático de derecho civil. En cambio, Eguiguren (2011) y Álvarez Miranda (2026) figuran con «sí».
  - *Regla de la PCM:* la regla que incluye «presidente del Congreso» le da «sí» a Galarreta; Bellido (congresista electo) recibe «no» y Lerner, «parcial».
  - *Casos «no_verificado»:* se excluyen del denominador (PPK 3, Humala 3, Castillo 1). Es un faltante no aleatorio: suelen ser los perfiles menos conocidos.
- Recodificar a Francke y Torres sube a Castillo +0,3 (variante 22). El efecto es pequeño, pero del mismo orden que el «empate».
- **Estabilidad.** Las 8 salidas de Castillo son casi todas un solo evento (la recomposición tras la renuncia de Bellido). Es legítimo contarlas, pero conviene decirlo.
- **Corrección.**
  1. Revisión humana doble antes de publicar, con kappa.
  2. Aplicar literalmente la cláusula de «experto reconocido».
  3. Imputar los «no_verificado» como «parcial» en un análisis de sensibilidad.
  4. Publicar la tabla de los 91 ministros con su código, para que se pueda auditar.
- **Redacción sugerida:** «La idoneidad es una codificación propia, todavía sin revisión independiente; personas razonables pueden discrepar en los casos frontera. La tabla completa está en idoneidad.json.»

### MEDIO 8. D5 existe solo para Keiko y la produce el propio proyecto

- **Problema.** Una dimensión con dato para un solo gobierno no compara nada: solo cambia la canasta de Keiko (cobertura del 85 % frente al 75 % de Castillo). Como su 50 está por encima de su promedio, la sube +1,3 (variante 5). La fuente es el análisis propio del mensaje («Plan Perú 2050»), que es autoevaluación y no viene de verificadores de la IFCN. Además usa una escala de 0,5 que no es la de la propuesta (0,66 y 0,33).
- **Corrección.** Excluir D5 del total hasta tener al menos dos gobiernos verificados con el mismo protocolo, y mostrarla como un recuadro aparte.
- **Redacción sugerida:** «La veracidad del discurso solo se pudo medir para el mensaje de Keiko Fujimori, así que no entra en el total.»

### MEDIO 9. Los faltantes premian a quien no tiene D1, y el umbral del 70 % se atribuye al Handbook OECD/JRC

- **Problema.**
  - D1 es la peor dimensión de todos, así que quien no la tiene (García y Humala) queda arriba: con un umbral del 55 %, Humala tendría 60,7 y García 54,5, y encabezarían el ranking. El umbral no protege de ese sesgo; solo lo oculta. Bajarlo al 60 % no cambia nada.
  - No encontramos en el Handbook OECD/JRC 2008 una regla de «70 % de cobertura». El Handbook discute la imputación y la sensibilidad, pero ese umbral parece una regla propia.
  - Los anclajes no son conmensurables: en D6 y D7, 50 significa «igual a lo esperado o al promedio»; en D1, D3 y D5, 50 significa «la mitad del máximo absoluto». Normalizar entre gobiernos da min-máx 45,0 frente a 45,0, z 46,8 frente a 47,5 y Borda 56,7 frente a 33,8.
- **Corrección.**
  1. Citar el umbral como regla propia.
  2. Publicar el total solo sobre el **núcleo común** de dimensiones disponibles para todos los gobiernos comparados (variante 30: D3, D6 y D7 para los cinco), o declarar que los totales con canastas distintas no se comparan.
  3. Explicitar el anclaje de cada dimensión.
- **Redacción sugerida:** «La regla del 70 % es nuestra. Cuando falta una dimensión, el índice supone que ese gobierno habría obtenido su propio promedio, así que los totales con distintas dimensiones no son estrictamente comparables.»

### MEDIO 10. El semáforo del contexto internacional mezcla escalas y lleva a atribuir mal

- **Problemas.**
  1. **Escalas mezcladas.** Los índices de gobernanza se colorean con su escala nominal (0-100) y los sociales con el rango min-máx del Perú entre 2005 y 2026. Con los mismos cortes (70/50/30), un CPI de 38 (cerca de la media mundial) sale naranja, y un Gini de 40,1 o una pobreza del 25,7 % salen **verdes**. El lector concluye que lo social está bien y la gobernanza mal, pero es un artefacto de la escala.
  2. **El min-máx histórico confunde la tendencia con el gobierno.** García 2006 es el mínimo por construcción (0,0 en Gini, pobreza, pobreza extrema e IDH) y el último año tiende al verde. La anemia del 43 % (problema severo según la OMS) sale amarilla y la desnutrición del 12 %, verde.
  3. **«Absoluto» no siempre es absoluto.** El WGI `_sc` es un **percentil entre países** (relativo), y se trata como escala absoluta.
  4. **Rupturas metodológicas.** El CPI anterior a 2012 multiplicado por 10 no es comparable (TI lo advierte). RSF cambió de metodología en 2022: el 42,9 de Keiko frente al 68,8 de PPK mezcla dos métodos.
  5. **Atribución.** Para Keiko solo se muestra lo «recibido» (heredado), junto al «primer año» de los demás, lo que invita a atribuirle el dato.
- **Corrección.**
  1. Usar una sola referencia para todo: el **percentil del Perú en América Latina o en el mundo** cada año, o directamente quitar el color y mostrar valor y flecha.
  2. No colorear el CPI anterior a 2012 ni comparar RSF a través de 2022.
  3. Rotular la columna de Keiko como «heredado».
  4. Usar umbrales normativos cuando existan (la clasificación de la OMS para anemia y desnutrición).
- **Redacción sugerida:** «Contexto, no evaluación: estos indicadores describen el país que recibió cada gobierno y no miden su gestión. Los colores comparan con el rango histórico del Perú o con la escala de cada índice, que no son equivalentes. Un verde en pobreza no significa que la pobreza sea baja, solo que es menor que en 2006.»

### BAJO 11. Ponderación sin justificar y una sola prueba de sensibilidad

- **Problema.** Los pesos (20/10/15/15/10/15/15) son normativos y no tienen respaldo empírico, ni de panel de expertos, ni de PCA (que con n = 5 no es posible). Solo se informa la variante de pesos iguales.
- **Corrección.** Publicar la tabla de sensibilidad de este documento, o un resumen, junto al índice, y el resultado Monte Carlo. Con n = 3-5 gobiernos, presentarlo explícitamente como «índice experimental».

---

## Resumen de correcciones mínimas antes de seguir publicando el total

1. Quitar las décimas y el «igual de malos», y publicar el rango de sensibilidad (hallazgo 1).
2. Sacar D1 del total o recodificarla con un solo protocolo (hallazgo 2); sacar D5 del total (hallazgo 8).
3. D6 con caída esperada proporcional y medición en una fecha homogénea (hallazgo 3).
4. D7 con inversión de agosto a octubre y sin el sesgo del PIM vigente (hallazgo 4).
5. Rotular el total como «sin integridad» y explicar hacia dónde sesga (hallazgo 5).
6. Libro de códigos y doble codificación para D2 y D3 (hallazgos 6 y 7).
7. Semáforo internacional con una sola escala de referencia o sin colores (hallazgo 10).
