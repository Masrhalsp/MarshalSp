# Sismo — Muelle de Trasmallo, módulo 40 m (análisis modal espectral independiente)

Generado por `python3 diseno/python/sismo/run_sismo.py` (`sismo/modal.py`, `sismo/comprobaciones.py`). Tiempo 59.4 s. Acción sísmica de `sap2000/model/trasmallo.py` (SEISMIC, proyecto Rover): ac = 0.24352 g, espectro elástico NCSE-02 TA = 0.22 s, TB = 0.88 s, vertical x 0.7, amortiguamiento 5%, 30 modos, SRSS, direccional (1.0, 0.3, 0.3). Los resultados de SAP2000 se compararán cuando estén disponibles.

## 1. Veredicto

- **El sismo gobierna.** Pilotes: η N-M = 1.85 (P3 Pie nm2 SISXQ[N+,Mx-,My+]) frente a 0.987 estático; cortante η = 1.65 (P18 Arranque SISY[N-,Vx+,Vy+]).
- Vigas transversales: flexión η = 1.33 (VT6 cara pilote mar - vano MEd <= MRd (hog) SISYQ[E-]) frente a 0.879 estático; con el armado propuesto η = 1.33 (la armadura inferior añadida no actúa: rige el momento negativo en la cara del pilote). Estribos (V + suspensión) η = 0.72, bielas η = 0.41. Torsión + cortante (información, (6.29)) η = 1.63.
- **El armado propuesto (diseno_final.md) NO se mantiene con el sismo elástico** (sin reducción por ductilidad, como Rover): los pilotes 40x40 con 12Ø25 (As ≈ 0.92·As,máx) no pueden resistir el momento sísmico; la solución exige otra sección de pilote, más pilotes o una reducción justificada del espectro.
- Sensibilidad (no veredicto) con μ = 2 (NCSE-02 §3.7.3.1, ductilidad baja, fuerzas sísmicas / 2): pilotes η N-M = 0.98, cortante 0.70; vigas flexión 0.67 (propuesto 0.67), torsión (info) 0.87.

## 2. Modelo y masa

Rigidez: modelo PyNite de `sap2000/tools/verify_pynite.py` (`build()`), sin las diagonales que emulan el diafragma; diafragma rígido exacto (maestro en el centro de masas X = 19.500, Y = 1.650 m); 1179 nudos, 3540 GDL reducidos. Masa concentrada traslacional (X, Y, Z), sin inercia rotacional; fuente de masa = cargas PP (con el peso propio de las barras, multiplicador 1) + CM + 0.8·Qa, sin masa propia de elementos (no se cuenta dos veces), como SAP2000 (Elements = No, Masses = No, Loads = Yes).

| Fuente | Peso [kN] |
|---|---|
| PP: peso propio de barras | 794.9 |
| PP: alveoplaca 4.10 kN/m² | 560.2 |
| CM | 301.0 |
| 0.8·Qa | 2064.0 |
| total (nudos libres + base) | 3720.2 |
| PP + CM + 0.8·Qa de `load_totals()` | 3720.2 |
| en los nudos de base (no vibra) | 170.1 |
| masa que vibra | 3550.1 kN = 362.01 t |

## 3. Modos, periodos y masa participante

| modo | T [s] | Sa,H/g | UX | UY | UZ | ΣUX | ΣUY | ΣUZ |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.6965 | 0.609 | 0.9993 | 0.0000 | 0.0000 | 0.9993 | 0.0000 | 0.0000 |
| 2 | 0.6175 | 0.609 | 0.0000 | 1.0000 | 0.0000 | 0.9993 | 1.0000 | 0.0000 |
| 3 | 0.5510 | 0.609 | 0.0001 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.0000 |
| 4 | 0.1219 | 0.446 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.0000 |
| 5 | 0.1185 | 0.440 | 0.0000 | 0.0000 | 0.0658 | 0.9994 | 1.0000 | 0.0658 |
| 6 | 0.1057 | 0.419 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.0658 |
| 7 | 0.0982 | 0.407 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.0658 |
| 8 | 0.0982 | 0.407 | 0.0000 | 0.0000 | 0.0002 | 0.9994 | 1.0000 | 0.0661 |
| 9 | 0.0949 | 0.401 | 0.0000 | 0.0000 | 0.0291 | 0.9994 | 1.0000 | 0.0952 |
| 10 | 0.0937 | 0.399 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.0952 |
| 11 | 0.0918 | 0.396 | 0.0000 | 0.0000 | 0.0404 | 0.9994 | 1.0000 | 0.1355 |
| 12 | 0.0916 | 0.396 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1355 |
| 13 | 0.0916 | 0.396 | 0.0000 | 0.0000 | 0.0007 | 0.9994 | 1.0000 | 0.1362 |
| 14 | 0.0911 | 0.395 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1362 |
| 15 | 0.0911 | 0.395 | 0.0000 | 0.0000 | 0.0036 | 0.9994 | 1.0000 | 0.1398 |
| 16 | 0.0909 | 0.394 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1398 |
| 17 | 0.0909 | 0.394 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1399 |
| 18 | 0.0908 | 0.394 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1399 |
| 19 | 0.0908 | 0.394 | 0.0000 | 0.0000 | 0.0001 | 0.9994 | 1.0000 | 0.1400 |
| 20 | 0.0903 | 0.393 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1400 |
| 21 | 0.0903 | 0.393 | 0.0000 | 0.0000 | 0.0001 | 0.9994 | 1.0000 | 0.1401 |
| 22 | 0.0903 | 0.393 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1401 |
| 23 | 0.0903 | 0.393 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1401 |
| 24 | 0.0902 | 0.393 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1401 |
| 25 | 0.0902 | 0.393 | 0.0000 | 0.0000 | 0.0001 | 0.9994 | 1.0000 | 0.1402 |
| 26 | 0.0890 | 0.391 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1402 |
| 27 | 0.0889 | 0.391 | 0.0000 | 0.0000 | 0.0006 | 0.9994 | 1.0000 | 0.1408 |
| 28 | 0.0887 | 0.391 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1408 |
| 29 | 0.0886 | 0.391 | 0.0000 | 0.0000 | 0.0009 | 0.9994 | 1.0000 | 0.1417 |
| 30 | 0.0835 | 0.382 | 0.0000 | 0.0000 | 0.0000 | 0.9994 | 1.0000 | 0.1417 |

Σ 30 modos: X 0.9994, Y 1.0000, Z 0.1417. La dirección Z (modos locales de la losa) no llega al 90 %: se añade la respuesta residual de la masa no captada (missing mass) con la aceleración de periodo cero 0.7·ac en EQZ; sin ella (30 modos, como SAP2000 por defecto) el cortante vertical sería 87 kN en lugar de 527 kN.

## 4. Comprobaciones cruzadas

- Periodos eigsh (shift-invert) vs. condensación de Guyan densa (eigh): 0.6965/0.6965, 0.6175/0.6175, 0.5510/0.5510, 0.1219/0.1219 s.
- Rayleigh con la rigidez del modelo (fuerza unitaria en el maestro): kX = 29365, kY = 37447 kN/m -> TX = 0.6976, TY = 0.6178 s.
- A mano: 14 pilotes 12EI/h³ (h = 6.70 m, cabeza sin giro): kX = 39979 kN/m, TX = 0.598 s (cota inferior: la losa sólo coacciona parcialmente el giro en X); 7 pórticos (Chopra 1.3.5, extremos rígidos de la viga): kY = 38318 kN/m, TY = 0.611 s.
- Fuerza lateral equivalente V = M·Sa(T1): X: T1 = 0.697 s, Sa = 0.609 g, V = 2161 kN (espectral 2160); Y: T1 = 0.617 s, Sa = 0.609 g, V = 2161 kN (espectral 2161).

## 5. Cortante en la base (SRSS por dirección) [kN]

| caso | FX | FY | FZ |
|---|---|---|---|
| EQX | 2159.8 | 0.0 | 0.0 |
| EQY | 0.0 | 2161.3 | 0.8 |
| EQZ | 0.0 | 0.6 | 526.7 |

## 6. Envolventes sísmicas de los pilotes (SRSS, convenio CYPE, z desde el empotramiento)

| pilote | z | N X | Mx X | My X | Qx X | Qy X | N Y | Mx Y | My Y | Qx Y | Qy Y | N Z | Mx Z | My Z | Qx Z | Qy Z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.00 | 84.4 | 430.2 | 12.4 | 95.7 | 3.7 | 346.4 | 0.1 | 531.5 | 0.0 | 156.2 | 22.1 | 2.7 | 0.8 | 1.1 | 0.3 |
| P1 | 6.70 | 84.4 | 210.8 | 12.2 | 95.7 | 3.7 | 346.4 | 0.1 | 515.1 | 0.0 | 156.2 | 22.1 | 4.9 | 1.5 | 1.1 | 0.3 |
| P2 | 0.00 | 95.3 | 429.7 | 12.3 | 95.7 | 3.6 | 346.3 | 0.0 | 531.5 | 0.0 | 156.2 | 20.2 | 2.7 | 0.8 | 1.1 | 0.4 |
| P2 | 6.70 | 95.3 | 211.5 | 11.9 | 95.7 | 3.6 | 346.3 | 0.0 | 515.1 | 0.0 | 156.2 | 20.2 | 4.9 | 1.5 | 1.1 | 0.4 |
| P3 | 0.00 | 9.5 | 628.2 | 5.3 | 178.5 | 1.3 | 338.7 | 0.0 | 525.4 | 0.0 | 153.7 | 40.4 | 5.1 | 1.8 | 2.1 | 0.8 |
| P3 | 6.70 | 9.5 | 567.7 | 4.1 | 178.5 | 1.3 | 338.7 | 0.0 | 504.1 | 0.0 | 153.7 | 40.4 | 9.3 | 3.2 | 2.1 | 0.8 |
| P4 | 0.00 | 14.2 | 624.5 | 11.3 | 177.2 | 3.7 | 338.6 | 0.0 | 525.4 | 0.0 | 153.7 | 36.7 | 5.0 | 1.9 | 2.1 | 0.8 |
| P4 | 6.70 | 14.2 | 562.5 | 13.8 | 177.2 | 3.7 | 338.6 | 0.0 | 504.1 | 0.0 | 153.7 | 36.7 | 9.1 | 3.4 | 2.1 | 0.8 |
| P5 | 0.00 | 3.1 | 628.4 | 4.1 | 178.6 | 1.2 | 338.9 | 0.0 | 525.4 | 0.0 | 153.6 | 53.8 | 3.3 | 2.5 | 1.4 | 1.0 |
| P5 | 6.70 | 3.1 | 568.1 | 4.0 | 178.6 | 1.2 | 338.9 | 0.0 | 504.1 | 0.0 | 153.6 | 53.8 | 5.9 | 4.5 | 1.4 | 1.0 |
| P6 | 0.00 | 2.4 | 623.3 | 4.0 | 176.7 | 1.2 | 338.8 | 0.0 | 525.4 | 0.0 | 153.7 | 49.6 | 3.3 | 2.6 | 1.4 | 1.1 |
| P6 | 6.70 | 2.4 | 560.4 | 3.8 | 176.7 | 1.2 | 338.8 | 0.0 | 504.1 | 0.0 | 153.7 | 49.6 | 5.9 | 4.7 | 1.4 | 1.1 |
| P7 | 0.00 | 0.0 | 628.4 | 0.0 | 178.6 | 0.0 | 338.9 | 0.0 | 525.4 | 0.0 | 153.6 | 61.9 | 0.0 | 3.1 | 0.0 | 1.3 |
| P7 | 6.70 | 0.0 | 568.0 | 0.0 | 178.6 | 0.0 | 338.9 | 0.0 | 504.1 | 0.0 | 153.6 | 61.9 | 0.0 | 5.6 | 0.0 | 1.3 |
| P8 | 0.00 | 0.0 | 623.3 | 0.0 | 176.7 | 0.0 | 338.8 | 0.0 | 525.4 | 0.0 | 153.7 | 57.4 | 0.0 | 3.2 | 0.0 | 1.3 |
| P8 | 6.70 | 0.0 | 560.4 | 0.0 | 176.7 | 0.0 | 338.8 | 0.0 | 504.1 | 0.0 | 153.7 | 57.4 | 0.0 | 5.8 | 0.0 | 1.3 |
| P13 | 0.00 | 3.1 | 628.4 | 4.1 | 178.6 | 1.2 | 338.9 | 0.0 | 525.4 | 0.0 | 153.6 | 53.8 | 3.3 | 2.5 | 1.4 | 1.0 |
| P13 | 6.70 | 3.1 | 568.1 | 4.0 | 178.6 | 1.2 | 338.9 | 0.0 | 504.1 | 0.0 | 153.6 | 53.8 | 5.9 | 4.5 | 1.4 | 1.0 |
| P14 | 0.00 | 2.4 | 623.3 | 4.0 | 176.7 | 1.2 | 338.8 | 0.0 | 525.4 | 0.0 | 153.7 | 49.6 | 3.3 | 2.6 | 1.4 | 1.1 |
| P14 | 6.70 | 2.4 | 560.4 | 3.8 | 176.7 | 1.2 | 338.8 | 0.0 | 504.1 | 0.0 | 153.7 | 49.6 | 5.9 | 4.7 | 1.4 | 1.1 |
| P15 | 0.00 | 9.5 | 628.2 | 5.3 | 178.5 | 1.3 | 338.7 | 0.0 | 525.4 | 0.0 | 153.7 | 40.4 | 5.1 | 1.8 | 2.1 | 0.8 |
| P15 | 6.70 | 9.5 | 567.7 | 4.1 | 178.5 | 1.3 | 338.7 | 0.0 | 504.1 | 0.0 | 153.7 | 40.4 | 9.3 | 3.2 | 2.1 | 0.8 |
| P16 | 0.00 | 84.4 | 430.2 | 12.4 | 95.7 | 3.7 | 346.4 | 0.1 | 531.5 | 0.0 | 156.2 | 22.1 | 2.7 | 0.8 | 1.1 | 0.3 |
| P16 | 6.70 | 84.4 | 210.8 | 12.2 | 95.7 | 3.7 | 346.4 | 0.1 | 515.1 | 0.0 | 156.2 | 22.1 | 4.9 | 1.5 | 1.1 | 0.3 |
| P17 | 0.00 | 14.2 | 624.5 | 11.3 | 177.2 | 3.7 | 338.6 | 0.0 | 525.4 | 0.0 | 153.7 | 36.7 | 5.0 | 1.9 | 2.1 | 0.8 |
| P17 | 6.70 | 14.2 | 562.5 | 13.8 | 177.2 | 3.7 | 338.6 | 0.0 | 504.1 | 0.0 | 153.7 | 36.7 | 9.1 | 3.4 | 2.1 | 0.8 |
| P18 | 0.00 | 95.3 | 429.7 | 12.3 | 95.7 | 3.6 | 346.3 | 0.0 | 531.5 | 0.0 | 156.2 | 20.2 | 2.7 | 0.8 | 1.1 | 0.4 |
| P18 | 6.70 | 95.3 | 211.5 | 11.9 | 95.7 | 3.6 | 346.3 | 0.0 | 515.1 | 0.0 | 156.2 | 20.2 | 4.9 | 1.5 | 1.1 | 0.4 |

## 7. Envolventes sísmicas de las vigas transversales (SRSS, M flector +, V = dM/dy) en las caras

| viga | sección | y | M X | V X | T X | M Y | V Y | T Y | M Z | V Z | T Z |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.20 | 9.5 | 55.5 | 214.8 | 0.4 | 0.2 | 0.4 | 0.5 | 2.8 | 2.0 |
| VT1 | cara pilote mar - vano | 0.20 | 8.1 | 19.3 | 34.3 | 527.9 | 346.0 | 0.3 | 0.7 | 13.7 | 3.0 |
| VT1 | cara pilote tierra - vano | 3.25 | 20.0 | 28.6 | 21.5 | 527.9 | 346.0 | 0.3 | 0.8 | 13.2 | 3.2 |
| VT1 | cara pilote tierra - vuelo | 3.65 | 1.3 | 60.3 | 231.8 | 0.4 | 0.2 | 0.3 | 0.1 | 2.8 | 2.2 |
| VT2 | cara pilote mar - voladizo | -0.20 | 5.6 | 34.9 | 222.7 | 0.4 | 0.1 | 0.3 | 1.0 | 5.5 | 2.6 |
| VT2 | cara pilote mar - vano | 0.20 | 18.2 | 27.5 | 301.0 | 516.2 | 338.4 | 0.3 | 1.2 | 24.7 | 10.8 |
| VT2 | cara pilote tierra - vano | 3.25 | 4.4 | 38.9 | 313.5 | 516.2 | 338.4 | 0.2 | 0.7 | 23.9 | 10.9 |
| VT2 | cara pilote tierra - vuelo | 3.65 | 0.5 | 36.3 | 249.0 | 0.4 | 0.1 | 0.2 | 0.2 | 5.7 | 2.6 |
| VT3 | cara pilote mar - voladizo | -0.20 | 0.2 | 0.2 | 143.8 | 0.0 | 0.2 | 0.0 | 1.1 | 6.1 | 1.4 |
| VT3 | cara pilote mar - vano | 0.20 | 4.1 | 3.3 | 348.6 | 516.6 | 338.6 | 0.0 | 0.9 | 34.0 | 6.3 |
| VT3 | cara pilote tierra - vano | 3.25 | 3.8 | 2.1 | 370.5 | 516.5 | 338.6 | 0.0 | 0.4 | 33.2 | 6.4 |
| VT3 | cara pilote tierra - vuelo | 3.65 | 0.2 | 0.2 | 166.7 | 0.0 | 0.2 | 0.0 | 0.3 | 6.5 | 1.3 |
| VT4 | cara pilote mar - voladizo | -0.20 | 0.0 | 0.0 | 144.3 | 0.0 | 0.2 | 0.0 | 1.2 | 6.4 | 0.0 |
| VT4 | cara pilote mar - vano | 0.20 | 0.0 | 0.0 | 347.9 | 516.6 | 338.6 | 0.0 | 0.8 | 40.8 | 0.0 |
| VT4 | cara pilote tierra - vano | 3.25 | 0.0 | 0.0 | 369.7 | 516.5 | 338.6 | 0.0 | 0.5 | 39.9 | 0.0 |
| VT4 | cara pilote tierra - vuelo | 3.65 | 0.0 | 0.0 | 167.2 | 0.0 | 0.2 | 0.0 | 0.3 | 6.9 | 0.0 |
| VT5 | cara pilote mar - voladizo | -0.20 | 0.2 | 0.2 | 143.8 | 0.0 | 0.2 | 0.0 | 1.1 | 6.1 | 1.4 |
| VT5 | cara pilote mar - vano | 0.20 | 4.1 | 3.3 | 348.6 | 516.6 | 338.6 | 0.0 | 0.9 | 34.0 | 6.3 |
| VT5 | cara pilote tierra - vano | 3.25 | 3.8 | 2.1 | 370.5 | 516.5 | 338.6 | 0.0 | 0.4 | 33.2 | 6.4 |
| VT5 | cara pilote tierra - vuelo | 3.65 | 0.2 | 0.2 | 166.7 | 0.0 | 0.2 | 0.0 | 0.3 | 6.5 | 1.3 |
| VT6 | cara pilote mar - voladizo | -0.20 | 5.6 | 34.9 | 222.7 | 0.4 | 0.1 | 0.3 | 1.0 | 5.5 | 2.6 |
| VT6 | cara pilote mar - vano | 0.20 | 18.2 | 27.5 | 301.0 | 516.2 | 338.4 | 0.3 | 1.2 | 24.7 | 10.8 |
| VT6 | cara pilote tierra - vano | 3.25 | 4.4 | 38.9 | 313.5 | 516.2 | 338.4 | 0.2 | 0.7 | 23.9 | 10.9 |
| VT6 | cara pilote tierra - vuelo | 3.65 | 0.5 | 36.3 | 249.0 | 0.4 | 0.1 | 0.2 | 0.2 | 5.7 | 2.6 |
| VT7 | cara pilote mar - voladizo | -0.20 | 9.5 | 55.5 | 214.8 | 0.4 | 0.2 | 0.4 | 0.5 | 2.8 | 2.0 |
| VT7 | cara pilote mar - vano | 0.20 | 8.1 | 19.3 | 34.3 | 527.9 | 346.0 | 0.3 | 0.7 | 13.7 | 3.0 |
| VT7 | cara pilote tierra - vano | 3.25 | 20.0 | 28.6 | 21.5 | 527.9 | 346.0 | 0.3 | 0.8 | 13.2 | 3.2 |
| VT7 | cara pilote tierra - vuelo | 3.65 | 1.3 | 60.3 | 231.8 | 0.4 | 0.2 | 0.3 | 0.1 | 2.8 | 2.2 |

## 8. Pilotes: situación accidental (γc 1.3, γs 1.0) frente al estático (ROM, Mode.CODIGO)

| pilote | η N-M 1er | η N-M (1º/2º) |  | posición | combinación | N | MEd,x | MEd,y | η cortante | η N-M estático | η V estático |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 1.526 | 1.609 | nm2 | Pie | SISYQ[N+,Mx-,My-] | 556.3 | -611.1 | -213.8 | 1.638 | 0.919 | 0.560 |
| P2 | 1.528 | 1.605 | nm2 | Pie | SISYQ[N+,Mx+,My-] | 546.3 | 609.4 | -212.4 | 1.651 | 0.815 | 0.814 |
| P3 | 1.720 | 1.846 | nm2 | Pie | SISXQ[N+,Mx-,My+] | 455.0 | -229.7 | 693.0 | 1.564 | 0.987 | 0.538 |
| P4 | 1.720 | 1.838 | nm2 | Pie | SISXQ[N+,Mx+,My+] | 433.2 | 233.2 | 686.3 | 1.584 | 0.764 | 0.734 |
| P5 | 1.715 | 1.823 | nm2 | Pie | SISXQ[N+,Mx-,My-] | 422.9 | -223.7 | -683.8 | 1.578 | 0.915 | 0.515 |
| P6 | 1.704 | 1.805 | nm2 | Pie | SISXQ[N+,Mx+,My-] | 398.1 | 220.7 | -675.6 | 1.587 | 0.763 | 0.745 |
| P7 | 1.706 | 1.815 | nm2 | Pie | SISXQ[N+,Mx-,My-] | 429.4 | -220.8 | -682.5 | 1.572 | 0.924 | 0.524 |
| P8 | 1.696 | 1.797 | nm2 | Pie | SISXQ[N+,Mx+,My+] | 404.6 | 217.8 | 674.3 | 1.582 | 0.739 | 0.711 |
| P13 | 1.715 | 1.823 | nm2 | Pie | SISXQ[N+,Mx-,My+] | 422.9 | -223.7 | 683.8 | 1.578 | 0.893 | 0.499 |
| P14 | 1.704 | 1.805 | nm2 | Pie | SISXQ[N+,Mx+,My+] | 398.1 | 220.7 | 675.6 | 1.587 | 0.735 | 0.714 |
| P15 | 1.720 | 1.846 | nm2 | Pie | SISXQ[N+,Mx-,My-] | 455.0 | -229.7 | -693.0 | 1.564 | 0.937 | 0.506 |
| P16 | 1.526 | 1.609 | nm2 | Pie | SISYQ[N+,Mx-,My+] | 556.3 | -611.1 | 213.8 | 1.638 | 0.843 | 0.519 |
| P17 | 1.720 | 1.838 | nm2 | Pie | SISXQ[N+,Mx+,My-] | 433.2 | 233.2 | -686.3 | 1.584 | 0.710 | 0.675 |
| P18 | 1.528 | 1.605 | nm2 | Pie | SISYQ[N+,Mx+,My+] | 546.3 | 609.4 | 212.4 | 1.651 | 0.730 | 0.719 |

## 9. Vigas transversales: situación accidental

| viga | armado | η flexión | sección |  | MEd | MRd | combinación | η bielas | η estribos | η T+V (info) | η flexión estático | η estribos estático |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | dispuesto | 1.278 | cara pilote tierra - vano | MEd <= MRd (hog) | 532.8 | 416.8 | SISY[E-] | 0.205 | 0.573 | 0.499 | 0.873 | 0.478 |
| VT2 | dispuesto | 1.332 | cara pilote mar - vano | MEd <= MRd (hog) | 527.5 | 396.1 | SISYQ[E-] | 0.410 | 0.718 | 1.466 | 0.770 | 0.717 |
| VT2 | propuesto | 1.331 | cara pilote mar - vano | MEd <= MRd (hog) | 527.5 | 396.4 | SISYQ[E-] | 0.410 | 0.718 | 1.469 | 0.769 | 0.717 |
| VT3 | dispuesto | 1.320 | cara pilote mar - vano | MEd <= MRd (hog) | 522.9 | 396.1 | SISYQ[E-] | 0.391 | 0.695 | 1.626 | 0.879 | 0.700 |
| VT3 | propuesto | 1.319 | cara pilote mar - vano | MEd <= MRd (hog) | 522.9 | 396.4 | SISYQ[E-] | 0.391 | 0.695 | 1.629 | 0.878 | 0.700 |
| VT4 | dispuesto | 1.318 | cara pilote mar - vano | MEd <= MRd (hog) | 522.0 | 396.1 | SISYQ[E-] | 0.395 | 0.701 | 1.615 | 0.744 | 0.684 |
| VT4 | propuesto | 1.317 | cara pilote mar - vano | MEd <= MRd (hog) | 522.0 | 396.4 | SISYQ[E-] | 0.395 | 0.701 | 1.618 | 0.743 | 0.684 |
| VT5 | dispuesto | 1.320 | cara pilote mar - vano | MEd <= MRd (hog) | 522.9 | 396.1 | SISYQ[E-] | 0.391 | 0.695 | 1.626 | 0.853 | 0.693 |
| VT5 | propuesto | 1.319 | cara pilote mar - vano | MEd <= MRd (hog) | 522.9 | 396.4 | SISYQ[E-] | 0.391 | 0.695 | 1.629 | 0.853 | 0.693 |
| VT6 | dispuesto | 1.332 | cara pilote mar - vano | MEd <= MRd (hog) | 527.5 | 396.1 | SISYQ[E-] | 0.410 | 0.718 | 1.466 | 0.719 | 0.703 |
| VT6 | propuesto | 1.331 | cara pilote mar - vano | MEd <= MRd (hog) | 527.5 | 396.4 | SISYQ[E-] | 0.410 | 0.718 | 1.469 | 0.718 | 0.703 |
| VT7 | dispuesto | 1.278 | cara pilote tierra - vano | MEd <= MRd (hog) | 532.8 | 416.8 | SISY[E-] | 0.205 | 0.573 | 0.499 | 0.798 | 0.456 |

## 10. Hipótesis y dudas

- Espectro elástico sin reducción por ductilidad (μ = 1), como Rover y `trasmallo.SEISMIC`; la sensibilidad con μ = 2 se da sólo como información.
- Combinaciones de signo independientes (N±, M±) de las envolventes SRSS: conservador frente a la correlación modal.
- φef = 1.75 (dato de CYPE) en el 2º orden, también en sismo (conservador para una acción de corta duración).
- La torsión de las vigas transversales bajo EQX (el momento de cabeza de los pilotes pasa a la losa a través de la viga) es elevada; se da como información, igual que la hipótesis de continuidad de la alveoplaca del modelo.
- Peso propio de las barras en la masa a través del patrón PP (multiplicador de peso propio 1, con WMod del pilote 6.70/7.25), igual que SAP2000 con la masa 'desde cargas'.
