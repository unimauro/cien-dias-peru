# Revisión adversarial de cifras: «100 días bajo la lupa»

- Fecha de la revisión: 7-nov-2026
- Alcance: 34 cifras de alto impacto, sobre todo las de «La conclusión» (index.html, líneas 58-112) y las del semáforo (research/indice100.json).
- Método: re-consulté la API de BCRPData con curl el 7-nov-2026, sin pasar por el ETL del repo. También descargué de forma independiente el CSV de vacunación de OWID/MINSA, el espejo SINADEF, el XLSX del CPI 2025 de Transparency International y los CSV de V-Dem de OWID. Leí keikogobierna.com, la ficha de Ipsos de octubre de 2026 y la nota de ECData, y verifiqué el resto con búsquedas web.
- No modifiqué ningún archivo del repo. Este informe es el único archivo nuevo.

## Convención de severidad

- **Crítica**: una cifra falsa que cambia una conclusión publicada.
- **Alta**: un error de periodo, de método o una contradicción visible que altera una cifra destacada o el ranking del índice.
- **Media**: un error de redondeo o de etiqueta, o una cifra sin fuente primaria que no cambia la conclusión.
- **Baja**: un matiz de redacción.

No hallé ninguna cifra **inventada**. Todos los valores primarios que re-consulté existen en su fuente. Los problemas son de **periodo** (día 0 y día 100 asimétricos, una ventana de 101 días), de **comparabilidad**, que mueve el «empate» del índice, y de **contradicciones internas** entre archivos.

## Tabla de hallazgos (ordenada por severidad)

| # | Cifra (dónde) | Valor en el dashboard | Valor en la fuente (re-verificado) | ¿Coincide? | Severidad | Corrección propuesta |
|---|---|---|---|---|---|---|
| 1 | Empate del índice, Castillo 40,6 frente a Keiko 40,3 (index.html:58,64; indice100.json D6) | Castillo, D6 = 67,5, medido con Ipsos «38 → 35 (ago → 12-nov-2021)». Keiko, D6 = 32,5, medido con Ipsos «57 → 40 (ago → oct-2026)» | Castillo: el 35 % es de Ipsos de noviembre, publicado el 14-nov-2021 con trabajo de campo de ~10-12-nov (día ~105-107). La última medición Ipsos antes del día 100 fue la de octubre (15-oct, día ~80): **42 %** (RPP: «pasa de 42 a 35»). Keiko: el 40 % es de Ipsos con campo el 7-8-oct-2026 (día ~72) | Parcial: las cifras existen, pero la ventana es asimétrica (Castillo después del día 100, Keiko en el día 72) | **Alta**, casi crítica: si se mide a Castillo con la misma regla que a Keiko (la última medición Ipsos antes del día 100 = 42), su Δ es +4, su D6 = 85 y su total sube a **44,1**. El «empate» desaparece | Usar la misma regla de corte para los cinco gobiernos (p. ej., «última medición Ipsos publicada antes del día 100» o «primera después del día 100») y declararla. Si se mantiene el 35 de noviembre para Castillo, esperar la medición de Ipsos de noviembre de 2026 para Keiko |
| 2 | «9 ministros salientes» de Castillo (index.html:64,89; castillo.json) frente a la sección «Rotación» (performance.json, rotacion[2] y rotacion[3]) | castillo.json: 9. performance.json, mostrado en la sección «Desempeño del Estado»: «5 ministros el 6-oct», «Total 7», «Barranzuela renunció el 6-nov-2021, fuera de la ventana» | Barranzuela renunció el **2-nov-2021** y Avelino Guillén juró el **4-nov-2021** (Correo, Forbes, Bloomberg Línea, BioBio). El 6-oct salieron 7 (Bellido, Carrasco, Cadillo, Maraví, Quispe, Merino y Gálvez; en Educación entró Carlos Gallardo). Con Béjar (17-ago), el total es **9** | castillo.json **sí** coincide. performance.json **no** coincide | **Alta**: la página muestra dos cifras contradictorias (9 frente a 7) y la de performance.json usa una fecha falsa | performance.json → rotacion: «Ministros reemplazados el 6-oct» de 5 → **6** (sumar Educación: Cadillo → Gallardo). «Total de cambios» de 7 → **9**. Detalle: «Barranzuela renunció el 2-nov-2021 (dentro de la ventana)» |
| 3 | «Pensión 65 a S/700 (productos, no resultados)» (index.html, «Keiko: dónde avanzó») | Se presenta como producto entregado | El propio keiko.json la clasifica como `en_proceso` y en el nivel `insumo`: aprobada en el crédito suplementario, con primer pago previsto el **30-nov-2026**, después del día 100 | **No** (contradicción interna; sobrevalora el avance) | **Alta** | «Salario mínimo a S/1,230 (producto) y Pensión 65 a S/700 aprobada en el presupuesto (insumo; primer pago el 30-nov)» |
| 4 | Bolsa de Lima de Keiko, **−4.0 %** (index.html:108; indicadores.json bvl v2) | 57,237.6 (24-jul) → 54,971.46 (5-nov) = −3.96 % | BCRPData PD38026MD: el valor del 5-nov-2026 coincide. Pero si el 28-jul es el día 1, **el día 100 es el 4-nov**. Así lo dicen keiko.json `periodo.dia100` y castillo.json `periodo.nota`, y Keiko Gobierna da el plazo por vencido el 4-nov. El 4-nov la BVL estaba en 56,145.1, es decir, **−1.9 %**. La caída del 5-nov (−2.1 % en un día) es del día 101 | Parcial: el dato es correcto, pero el día no | **Alta**: la cifra destacada se duplica por un solo día | Usar el día 100 = 4-nov en todas las series: BVL Keiko **−1.9 %**, BVL Castillo **+7.9 %** (20,254.7), TC Castillo **+2.3 %** (4.0107), TC Keiko **+1.2 %**. Si se mantiene el 5-nov, decir «día 101» o declarar «día 0 = 28-jul» de forma explícita y coherente en keiko.json |
| 5 | Homicidios SINADEF, «+4.3 %» para Keiko y «+2.7 %» para Castillo (index.html:108; resultados.json) | 584 frente a 560 y 380 frente a 370 | Re-descargué el espejo SINADEF (corte 6-nov-2026). La ventana «durante» va del 28-jul al 5-nov = **101 días**; la ventana «antes» (19-abr a 27-jul) = 100 días. Con 100 días (28-jul a 4-nov): **2026 = 579 → +3.4 %**; **2021 = 377 → +1.9 %** | Parcial (ventanas de distinto largo) | **Alta**: la cifra destacada del conclusión queda inflada en ~1 punto | resultados.json → homicidios: «durante» 2021 = 377 y 2026 = 579; rezago_nota «+1.9 %» y «+3.4 %». Corregir `fin` a 11-04 en etl/resultados_sinadef.py |
| 6 | Ejecución del gasto, 75.3 % (2026) frente a 70.3 % (2021) y D7 del índice (index.html, Keiko; indice100.json D7; performance.json) | Keiko D7 = 64.3; Castillo D7 = 50.1 | La aritmética cuadra (128.27/170.45 = 75.25 %; 96.72/137.64 = 70.27 %). Pero el docstring de etl/performance_mef_sectores.py reconoce que en los años cerrados el denominador es el **PIM final al 31-dic**, y en 2026 es el **PIM vigente al 7-nov**. Como el PIM crece en nov-dic, esto **subestima** de forma sistemática la ejecución a octubre de 2006, 2011, 2016 y 2021 frente a 2026. No pude re-consultar la Consulta Amigable (redirección de sesión ASP.NET) | Parcial (sesgo metodológico a favor de 2026) | **Alta**: el sesgo mueve 14 puntos de D7 a favor de Keiko, y el texto lo despacha con «PIM no del todo comparable» | Usar un denominador homogéneo: PIM al cierre de octubre de cada año (por ejemplo, desde los reportes mensuales de SIAF o del portal de datos abiertos del MEF). Si no se puede, quitar D7 del total o mostrar el sesgo de forma explícita |
| 7 | «0 de 67 acciones de 100 días acreditadas con una norma (3 en proceso)» (index.html:105) | 0 / 3 / 64 | keikogobierna.com (leído el 7-nov, día 103): 67 en total, **0 cumplidas, 3 en progreso, 64 sin avance, 0 incumplidas**. Los 3 «en progreso» **sí** tienen norma (DU 015-2026, DS 121 y 143-2026-PCM, RM 383-2026-MINCETUR) | Las cifras coinciden; la redacción no | Media | «0 de 67 cumplidas; 3 con una norma parcial (en progreso); 64 sin norma que las acredite» |
| 8 | «23.4 M dosis de vacuna aplicadas en la ventana» (index.html:83) | 23.4 M | OWID/MINSA: 36,568,223 (5-nov) − 13,020,160 (27-jul) = **23,548,063 → 23.5 M**, como dice resultados.json. Con el día 100 en el 4-nov: 23,247,382 → 23.2 M | **No** (redondeo mal transcrito) | Media | «23.5 M» (o «23.2 M» si el día 100 pasa al 4-nov). «El doble» sigue siendo cierto (11.57 M antes) |
| 9 | Keiko D2: «7 promesas cumplidas clasificadas» (indice100.json) frente a D1: «0 cumplidas» y frente a la conclusión: «5 insumos, 7 actividades y 3 productos» (15) | 7 / 0 / 15 | Son tres conteos distintos para el mismo objeto | Inconsistencia interna | Media | Unificar la etiqueta de D2: «15 ítems reportados como cumplidos o en proceso (5 insumos, 7 actividades, 3 productos)», o explicar de dónde sale el 7 |
| 10 | Índice con dimensiones distintas: Keiko suma D5 (veracidad, 50) y Castillo no | Keiko: 6 dimensiones, cobertura 85; Castillo: 5 dimensiones, cobertura 75 | Recalculado: sin D5, Keiko = 2926.5/75 = **39.0** (frente a 40.3) | Método | Media | Para el «empate», comparar sobre las mismas dimensiones (D1, D2, D3, D6, D7) o declarar la diferencia junto a la cifra |
| 11 | Día 0 diferente según la serie (indicadores.json) | TC y BVL: 27-jul-2021 y 24-jul-2026; cobre y EMBIG: 28-jul en los dos años | BCRPData confirma n.d. el 27, 28 y 29-jul-2026 para TC y BVL. El cobre sí tiene el 24-jul-2026: 617.66. El «cobre subió 4 %» (618.86 → 644.15 = +4.09 %) pasa a **+4.3 %** con el mismo d0 que la BVL | Parcial | Media | Usar un d0 común por ventana (el último hábil con dato para todas las series, 24-jul-2026) o declarar la diferencia. El «control» con cobre exige el mismo d0 que la BVL |
| 12 | Salario mínimo a S/1,230 como «cumplida» | Cumplida, producto | DS de aumento progresivo: S/1,130 → S/1,230 desde oct-2026 y S/1,300 en 2027 (LP Derecho, Forbes, Infobae). La promesa del 28-jul fue **S/1,300** | Parcial | Media | Estado «cumplida en parte (primer tramo)», no «cumplida» |
| 13 | Datum, sep-2026: 42/44 (keiko.json aprobacion) | Se muestra con confianza baja | Sin URL ni ficha («resumen de buscador») | Cifra sin fuente | Media | Quitarla o conseguir la ficha de Datum |
| 14 | «2 votos de confianza ajustados» de Castillo (index.html:64) | «ajustados» | Bellido: 73-50-0 (margen de 23); Vásquez: 68-56-1 (margen de 12). Cifras **correctas** (Congreso, Gestión, Forbes) | Las cifras sí; el adjetivo no aplica a Bellido | Baja | «2 votos de confianza (el segundo, 68-56)» |
| 15 | Humala 55 → 56 | 55 (ago-2011) → 56 (nov-2011) | 55 confirmado (Ipsos-Apoyo/AP, 14-ago-2011). El 56 de noviembre no aparece en las notas de prensa, pero es coherente con el 47 de diciembre de 2011 («−9»). No leí la tabla del PDF | Parcial (probable) | Baja | Citar la página del PDF «OpinionDataNoviembre2011» |
| 16 | «60 proyectos de ley, 6 sustantivos» de Castillo | 60 / 6 | Infobae (11-nov-2021): «alrededor de 60». El desglose 45/4/3/2/6 es un conteo propio, sin lista enlazada al Congreso | Parcial | Baja | Enlazar la consulta del SPIJ o del Congreso que respalda el conteo |

### Cifras verificadas sin observaciones (coinciden)

| # | Cifra | Dashboard | Fuente re-consultada | Coincide |
|---|---|---|---|---|
| 17 | TC Castillo, S/3.92 → 4.01 (+2.4 %) | 3.9223 → 4.0148 | BCRP PD04638PD: 27-jul-21 3.92233; 5-nov-21 4.01483 | Sí (ver #4 por el día) |
| 18 | TC Keiko, d0 y d100 | 3.4066 → 3.4487 (+1.23 %) | PD04638PD: 24-jul-26 3.40664; 5-nov-26 3.44871 | Sí |
| 19 | BVL Castillo, +8.8 % | 18,775.12 → 20,420.1 | PD38026MD: idéntico | Sí (ver #4) |
| 20 | Cobre 2021 plano (+0.44 %) | 439.85 → 441.80 | PD04701XD: idéntico | Sí |
| 21 | Cobre 2026, d100 en el 4-nov | 644.1465 | PD04701XD: 4-nov 644.146; 5-nov n.d. | Sí |
| 22 | EMBIG Perú, 182 → 182 (2021); 113 al 28-jul-2026; sin d100 | igual | PD04709XD: 2021 idéntico; 2026 sin dato después de septiembre (n.d. el 4 y 5-nov) | Sí |
| 23 | Expectativa empresarial a 3 meses, 62 → 49.5 | 62.2677 → 49.5223 | PD38045AM: jul-26 62.2677; oct-26 49.5223 | Sí |
| 24 | Inflación Lima a 12 meses, 4.07 → 5.25 (2026) y 3.81 → 5.83 (2021) | igual | PN01273PM: idéntico | Sí |
| 25 | Desempleo Lima, 10.3 → 9.97 (2021) y 4.91 → 4.37 (2026) | igual | PN38063GM: idéntico (jun-21 10.324; sep-21 9.972; jun-26 4.913; sep-26 4.372) | Sí |
| 26 | Expectativa de inflación a 12 meses, 3.01 → 3.05 | igual | PD12912AM: idéntico | Sí |
| 27 | ECData: 43 promesas, 3 cumplidas, 4 en proceso, 36 incumplidas (5 inviables) | igual | El Comercio, 8-nov-2021 (Mayté Ciriaco): idéntico. El «8 %» en proceso es del propio medio (4/43 = 9.3 %); el repo lo advierte | Sí |
| 28 | Ipsos de Keiko, 57 → 40 (desaprobación de 25 a 49) | igual | Ficha de Ipsos/Perú21, oct-2026: 40/49, campo del 7 al 8-oct, n = 1,212; serie de agosto: 57/25 | Sí (ver #1 por el periodo) |
| 29 | Ipsos de Castillo, 38 (ago-2021) | 38 | Ipsos/El Comercio, 12-13-ago-2021: 38/45 | Sí |
| 30 | PPK 61 → 51 | igual | Ipsos, Opinión Data: ago-16 61; serie sep-ene 63, 55, 51, 48, 43 → nov 51 | Sí |
| 31 | Votos de confianza: Bellido 73-50-0 y Vásquez 68-56-1 (16 de Perú Libre en contra) | igual | Congreso, Gestión, Forbes y Peru21 | Sí |
| 32 | CPI 2025: puntaje 30, puesto 130 | 30 / 130 | CPI2025_Results.xlsx (TI): Peru, 30, 130 | Sí |
| 33 | V-Dem 2025: democracia liberal 0.506 y corrupción política 0.63. Castillo: 0.706 → 0.621 | igual | OWID (liberal-democracy-index, political-corruption-index): idéntico | Sí |
| 34 | Pobreza monetaria 2025: 25.7 % (2024: 27.6 %; extrema 4.7 %) | igual | INEI, 5-may-2026 (El Peruano, Correo, La República) | Sí |
| — | Keiko: 1 cambio de gabinete (Rafael Rey, 18-sep-2026, 52 días; entra Tangherlini) | igual | Forbes, El Peruano, Correo | Sí |
| — | Ley 32743: 27 materias, 12 de seguridad y 15 de El Niño, en vigor desde el 23-oct-2026 | igual | PPU Legal. El plazo de 90 días no lo confirmé en el texto | Sí / parcial |
| — | CPI 2020: 38 (puesto 94); CPI 2022: 36 (puesto 101) | igual | Ediciones de TI | Sí |
| — | Latinobarómetro: satisfacción 2024 ≈ 10 %; apoyo 2020 46 % → 2023 50 % | igual | Peru21 y La República. El apoyo de 2024 (44.2) no lo confirmé en el informe | Sí / parcial |

## Correcciones concretas

| Archivo | Campo | Valor actual → valor correcto | Fuente |
|---|---|---|---|
| research/performance.json | `rotacion[anio=2021, indicador="Ministros reemplazados en la recomposición del 6-oct-2021…"].valor` y `.detalle` | 5 → **6**; agregar «Educación (Juan Cadillo → Carlos Gallardo)» y borrar «solo se identifican estos 5» | Andina 864634; La República, «¿Quién es Carlos Gallardo…?» (6-oct-2021) |
| research/performance.json | `rotacion[anio=2021, indicador="Total de cambios en el Consejo de Ministros…"].valor` y `.detalle` | 7 → **9**; «Barranzuela renunció el 6-nov-2021, fuera de la ventana» → «Barranzuela renunció el 2-nov-2021 (Guillén juró el 4-nov), dentro de la ventana» | Correo, Forbes y Bloomberg Línea (4-nov-2021) |
| index.html (línea 104) | «Salario mínimo a S/1,230 y Pensión 65 a S/700 (productos, no resultados)» | → «Salario mínimo a S/1,230, primer tramo de S/1,300 (producto); Pensión 65 a S/700 aprobada en el presupuesto, con primer pago el 30-nov (insumo)» | research/keiko.json → promesas (Pensión 65: en_proceso / insumo) |
| index.html (línea 83) | «23.4 M dosis» | → **«23.5 M»** (o «23.2 M» si el día 100 pasa al 4-nov) | OWID Peru.csv: 36,568,223 − 13,020,160 |
| research/indicadores.json y etl/fetch_bcrp.py | `ventanas.v1.fin` y `ventanas.v2.fin` | 2021-11-05 / 2026-11-05 → **2021-11-04 / 2026-11-04** (día 100 si el 28-jul es el día 1; coherente con keiko.json `periodo.dia100`) | Conteo de calendario; Keiko Gobierna («venció el 4-nov») |
| index.html (líneas 85, 91 y 108) | BVL Keiko «−4.0 %»; BVL Castillo «+8.8 %»; TC Castillo «+2.4 % (3.92 → 4.01)» | → **−1.9 %** (56,145.1); **+7.9 %** (20,254.7); **+2.3 % (3.92 → 4.01)** | BCRPData PD38026MD y PD04638PD, valores del 4-nov |
| research/resultados.json | `indicadores[homicidios_sinadef]["2021"].durante.valor`, `["2026"].durante.valor` y `rezago_nota` | 380 → **377**; 584 → **579**; «+2.7 %» → **«+1.9 %»**; «+4.3 %» → **«+3.4 %»** (ventana 28-jul a 4-nov, 100 días) | Espejo SINADEF JudithCristina/sinadef-automatizado, corte 2026-11-06 (re-descargado) |
| etl/resultados_sinadef.py | `fin = date(y, 11, 5)` | → `date(y, 11, 4)` (para que las dos ventanas tengan 100 días) | — |
| index.html (línea 108) | «homicidios +4.3 % (provisional)» | → «+3.4 % (provisional)» | idem |
| research/indice100.json | `gobiernos.castillo.dims.D6` | Hoy: «38 → 35 (ago → 12-nov-2021)», con score 67.5. Aplicar la misma regla que a Keiko (última medición Ipsos antes del día 100): **38 → 42 (ago → 15-oct-2021), Δ +4, score 85.0**; total ≈ **44.1** (los pesos iguales también cambian). La alternativa es mantener el 35 y esperar Ipsos de noviembre de 2026 para Keiko | Ipsos/El Comercio, oct-2021 (42/48) y nov-2021 (35/57, publicado el 14-nov) |
| index.html (líneas 58, 64 y 112) | «Castillo 40,6 y Keiko 40,3 … empatan» | Recalcular después de corregir D6 (y D7, ver abajo); hoy el empate depende de una ventana asimétrica | idem |
| research/indice100.json + etl/performance_mef_sectores.py | D7 (ratio de ejecución) | Denominador homogéneo: **PIM a octubre** de cada año en lugar del PIM final de los años cerrados frente al PIM vigente de 2026; o sacar D7 del total hasta tenerlo | Docstring del propio ETL («año cerrado = PIM final al 31-dic; año en curso = PIM vigente») |
| research/indice100.json | `gobiernos.keiko.dims.D2.valor` | «7 promesas cumplidas clasificadas» → «15 ítems cumplidos o en proceso (5 insumos, 7 actividades, 3 productos)» o lo que realmente se use | research/keiko.json → cadena_valor_resumen |
| index.html (línea 105) | «0 de 67 acciones de 100 días acreditadas con una norma (3 en proceso)» | → «0 de 67 cumplidas; 3 en progreso con una norma parcial; 64 sin norma que las acredite» | keikogobierna.com/primeros-100-dias (7-nov-2026) |
| research/keiko.json | promesa RMV `estado` | «cumplida» → «cumplida en parte (primer tramo S/1,230 de S/1,300)» | LP Derecho («aumento progresivo hasta S/1,300»); Forbes, 28-jul-2026 |
| research/keiko.json | `aprobacion[Datum 2026-09]` | 42/44 sin URL → eliminar o enlazar la ficha | — |
| index.html (línea 64) | «2 votos de confianza ajustados» | → «2 votos de confianza (73-50 y 68-56)» | Congreso (comunicaciones.congreso.gob.pe) |

## Lo que no pude verificar de forma independiente

- **MEF, Consulta Amigable**: la página redirige («Object moved») sin estado de sesión. No pude re-consultar 70.3 % ni 75.3 %; solo comprobé la aritmética contra los montos guardados.
- **García 63 → 57 (Apoyo 2006)** y **Humala 56 (nov-2011)**: no leí las tablas de los PDF de Ipsos, aunque la evidencia secundaria es consistente.
- **Latinobarómetro 2024, apoyo a la democracia (44.2 %)**: lo vi en la prensa, pero no en el informe.
- **Desglose de los 60 proyectos de ley de Castillo**: es un conteo propio sin lista enlazada.

## Fuentes primarias usadas en esta revisión

- BCRPData API (curl, 7-nov-2026): PD04638PD, PD38026MD, PD04709XD, PD04708XD, PD04701XD, PD12301MD, PN01273PM, PD38045AM, PD12912AM y PN38063GM, rangos 2021-07-20/2021-11-10 y 2026-07-20/2026-11-10.
- OWID / MINSA, vacunación: https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/Peru.csv
- Espejo SINADEF: https://raw.githubusercontent.com/JudithCristina/sinadef-automatizado/main/data/processed/BASE_FINAL_GENERAL.csv
- Transparency International: https://images.transparencycdn.org/images/CPI2025_Results.xlsx
- V-Dem (OWID): https://ourworldindata.org/grapher/liberal-democracy-index.csv y https://ourworldindata.org/grapher/political-corruption-index.csv
- Keiko Gobierna: https://keikogobierna.com/primeros-100-dias/
- Ipsos, oct-2026: https://www.ipsos.com/es-pe/aprobacion-de-autoridades-encuesta-peru21-ipsos-octubre-2026
- ECData: https://elcomercio.pe/peru/los-primeros-100-dias-de-pedro-castillo-el-85-de-las-promesas-no-se-cumplieron-especial-ec-data-salud-economia-educacion-trabajo-ecdata-noticia/
- Barranzuela y Guillén: https://forbes.pe/actualidad/2021-11-04/avelino-guillen-es-el-nuevo-ministro-del-interior/ y https://www.bloomberglinea.com/2021/11/04/avelino-guillen-conocido-exfiscal-es-el-nuevo-ministro-de-interior-de-peru/
- Ipsos, nov-2021 (42 → 35): https://rpp.pe/peru/actualidad/aprobacion-del-presidente-pedro-castillo-pasa-de-42-a-35-puntos-noticia-1369095
- Ipsos, ago-2021 (38): https://canaln.pe/actualidad/pedro-castillo-mandatario-inicia-su-gestion-38-aprobacion-segun-ipsos-n438143
- Votos de confianza: https://comunicaciones.congreso.gob.pe/noticias/congreso-aprobo-voto-de-confianza-a-gabinete-ministerial-presidido-por-mirtha-vasquez y https://lpderecho.pe/gabinete-bellido-voto-confianza-congreso/
- Pobreza 2025: https://elperuano.pe/noticia/295035-inei-pobreza-se-redujo-en-19-en-el-2025-y-afecta-al-257-de-peruanos
- RMV y Pensión 65: https://lpderecho.pe/keiko-fujimori-firma-decreto-supremo-con-aumento-del-sueldo-minimo/ y https://gestion.pe/peru/politica/keiko-fujimori-en-mensaje-a-la-nacion-duplicara-monto-de-pension-65-adultos-mayores-recibiran-s-700-bimestral-noticia/
- Rafael Rey: https://forbes.pe/actualidad/2026-09-18/renuncio-rafael-rey-ministro-de-transportes-y-comunicaciones/
- Ley 32743: https://ppulegal.com/?p=34487
