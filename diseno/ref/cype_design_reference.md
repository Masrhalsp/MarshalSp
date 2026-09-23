# CYPE design reference — Muelle de Trasmallo (piles and beams)

Companion of `cype_design_reference.json`. Everything below is transcribed from Anejo 10 (`report/A10_CALC_ESTRUCTURAS.docx`), Trasmallo results in the body (P215–P608) and Apéndice 1 “Listados de cálculo muelle de trasmallo” (P1449–P1835). Muelle de Arrastre and casetas are out of scope. This page is generated from the JSON, so the two always agree.

## How to read the sources

- `P<n>` — paragraph index n of python-docx Document.paragraphs (same numbering as the a10_full.txt dump)
- `P<n> table` — the table that immediately follows paragraph P<n> in document order ('#k' if several)
- `[A > B] sym` — row found inside the table after the header rows A then B (e.g. '[Cortante en la dirección Y] VRd,max')
- `(occurrence k)` — k-th row with that symbol inside the (sub)segment
- `check k left/right` — k-th comparison row of the table ('value  ≤/≥  limit  ✓')
- `P<n> image <file>` — value read visually from an embedded image anchored at P<n> (Word media file name)
- `tabular rows` — for CYPE tables (bars, listing zones, pile tables) one src is given per row; column units are in the key names

Extraction: Values parsed directly from the .docx with python-docx INCLUDING nested tables (lost in a10_full.txt, e.g. 'Datos del pilar') and Symbol-font glyphs (η, σ, ν, ρ, λ, ϕ, θ, α, ε, γ, ≤, ≥ were lost in the dump). Equation images (WMF) were rendered via LibreOffice PDF export and are only partially legible: the 'formulas_seen_in_render' / 'formula...' strings are the legible parts completed with the Eurocode 2 expressions that reproduce the printed numbers — they are NOT verbatim transcriptions.

Sign conventions: bars: σs, ε: + compression, - tension (CYPE equilibrium tables); beam_moments: negative = hogging (top tension); pile_N: N > 0 compression.

Anything marked **INFERENCE** is not printed in the document and was deduced (arithmetic or drawings); everything else is a transcription.

## 1. Key reference numbers

### Pile P3 (the governing pile), 12Ø25, ties Ø10/150

| quantity | head section 'FORJADO 1' | source | base section 'EMPOTRAMIENTO' | source |
| --- | --- | --- | --- | --- |
| NEd | 620.06 kN | P245 table: [Comprobación de resistencia de la sección] NEd | 655.55 kN | P300 table: [Comprobación de resistencia de la sección] NEd |
| MEd_x_first_order | 288.36 kN·m | P245 table: [Comprobación de resistencia de la sección] MEd,x | -283.56 kN·m | P300 table: [Comprobación de resistencia de la sección] MEd,x |
| MEd_y_first_order | -3.81 kN·m | P245 table: [Comprobación de resistencia de la sección] MEd,y | 2.79 kN·m | P300 table: [Comprobación de resistencia de la sección] MEd,y |
| eta_1 | 0.670 | P242 table: η (occurrence 1) | 0.642 | P297 table: η (occurrence 1) |
| MSd_x_second_order | 353.51 kN·m | P245 table: [Comprobación del estado limite de inestabilidad] MSd,x | -352.07 kN·m | P300 table: [Comprobación del estado limite de inestabilidad] MSd,x |
| MSd_y_second_order | -68.95 kN·m | P245 table: [Comprobación del estado limite de inestabilidad] MSd,y | 71.29 kN·m | P300 table: [Comprobación del estado limite de inestabilidad] MSd,y |
| eta_2 | 0.913 | P242 table: η (occurrence 2) | 0.894 | P297 table: η (occurrence 2) |
| shear_eta_VRdmax | 0.086 | P237 table: [Se debe satisfacer] η (occurrence 1) | 0.085 | P292 table: [Se debe satisfacer] η |
| VRd_max | 996.63 kN | P237 table: [Se debe satisfacer] VRd,max | 1005.35 kN | P292 table: [Se debe satisfacer] VRd,max |
| listing_aprov_pct | 92.5 % | P1752 table: Cabeza (N,M) | 90.7 % | P1752 table: Arranque |

Head only: e2 = 92.12 mm, λ = 58.02, λlim = 42.58, VRd,c (printed 'VRd,s') = 142.85 kN with η = 0.552, As,min = 6.40 cm², As,max = 122.67 cm². Combination: 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo.

### Transverse beam P3–P4 (Pórtico 4, inverted T 50x55+15x30+15x30)

| item | value | source |
| --- | --- | --- |
| shear_position | 0.488 m | P364 table: statement 1 (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...') |
| shear_combination | 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo | P364 table: statement 1 (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...') |
| VEd_y | 390.18 kN | P364 table: [Se debe satisfacer] VEd,y (occurrence 1) |
| VRd_s | 407.15 kN | P364 table: [Se debe satisfacer] VRd,s,Vy |
| eta_VRds | 0.958 | P364 table: [Se debe satisfacer] η (occurrence 2) |
| VRd_max | 1512.00 kN | P364 table: [Se debe satisfacer] VRd,max,Vy |
| eta_VRdmax | 0.258 | P364 table: [Se debe satisfacer] η (occurrence 1) |
| Asw | 2.36 cm² | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] Asw |
| s | 100 mm | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] s |
| z | 43.20 cm | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] z |
| MEd_x_hogging_at_P3 | -273.71 kN·m | P369 table: MEd,x |
| MRd_x | -325.78 kN·m | P369 table: MRd,x |
| eta_bending | 0.840 | P369 table: η |
| As_top | 15.71 cm² | P359 table: As |
| As_min | 5.09 cm² | P359 table: As,min |
| fT_max | 1.53 mm | P583 table: fT,max |
| fT_lim | 12.20 mm | P583 table: fT,lim |
| fA_max | 1.33 mm | P581 table: fA,max |
| fA_lim | 6.10 mm | P581 table: fA,lim |
| crack_hand_check_M_qp | 86.0 kN·m | P571 image image118.png |
| crack_hand_check_sigma_ct | 2.20 MPa | P575 |
| crack_hand_check_fct | 3.2 MPa | P575 — 'La resistencia a tracción del C35 es de 3.2 Mpa' (fctm printed 3.21 in P364 table) |

## 2. Materials and design parameters used by CYPE

### HA-50 (piles)

| item | value | source |
| --- | --- | --- |
| fck | 50.00 MPa | P249 table: fck |
| gamma_c | 1.5 | P249 table: γc |
| alpha_cc | 1.00 | P249 table: αcc |
| fcd | 33.33 MPa | P249 table: fcd |
| eps_c2 | 0.0020 | P249 table: εc2 |
| eps_cu2 | 0.0035 | P249 table: εcu2 |
| Ec | 33550 MPa | P1583 table: Pilares y pantallas |
| aggregate_max | 20 mm | P220 table: Tamaño máximo de árido |
| cover_geometric | 5.0 cm | P220 table: Recubrimiento geométrico |
| fctm | — | not printed — fctm / fct,m,fl are not printed for HA-50 (no crack or As,min-bending check for piles) |
| phi_ef_lambda_lim | 1.8 | P245 table: [Comprobación del estado limite de inestabilidad > En el eje x] ϕef (occurrence 1) |
| phi_ef_K_phi | 1.750 | P245 table: [Comprobación del estado limite de inestabilidad > En el eje x] ϕef (occurrence 2) |

### HA-35 (beams)

| item | value | source |
| --- | --- | --- |
| fck | 35.00 MPa | P373 table: fck |
| gamma_c | 1.5 | P373 table: γc |
| alpha_cc | 1.00 | P373 table: αcc |
| fcd | 23.33 MPa | P373 table: fcd |
| eps_c2 | 0.0020 | P373 table: εc2 |
| eps_cu2 | 0.0035 | P373 table: εcu2 |
| fctm | 3.21 MPa | P364 table: fctm |
| fct_m_fl | 3.37 MPa | P359 table: fct,m,fl |
| Ec | 30669 MPa | P1583 table: Forjados |
| cover_geometric_top | 5.0 cm | P336 table: Recubrimiento geométrico superior |
| cover_geometric_bottom | 5.0 cm | P336 table: Recubrimiento geométrico inferior |
| cover_geometric_side | 5.0 cm | P336 table: Recubrimiento geométrico lateral |
| aggregate_max | 20 mm | P352 table: dg |

### B 500 S

| item | value | source |
| --- | --- | --- |
| fyk | 500.00 MPa | P253 table: fyk |
| gamma_s | 1.15 | P253 table: γs |
| fyd | 434.78 MPa | P253 table: fyd |
| eps_su | 0.0100 | P253 table: εsu |
| eps_yd | 0.00217 | P245 table: [Comprobación del estado limite de inestabilidad > En el eje x] εyd |
| fywk | 500.00 MPa | P364 table: fywk |
| fywd | 400.00 MPa | P364 table: fywd — limited to 400 MPa |
| Es | — | not printed — Es is not printed; εyd = 0.00217 = 434.78/Es implies Es ≈ 200000 MPa (INFERENCE) |

### Concretes (§1.11.1) and steel (§1.11.2)

| elemento | hormigón | fck MPa | γc | árido | max mm | Ec MPa | source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Forjados | HA-35 | 35 | 1.5 | Caliza | 20 | 30669 | P1583 table: Forjados |
| Pilares y pantallas | HA-50 | 50 | 1.5 | Caliza | 20 | 33550 | P1583 table: Pilares y pantallas |
| Muros | HA-25 | 25 | 1.5 | Caliza | 20 | 28328 | P1583 table: Muros |

Steel: B 500 S fyk 500 MPa, γs 1.15 (P1591 table: Todos). Project text: Hormigón armado HA-50/F/12/XS3. (P120); Acero para armaduras B500 SD (P121); 5 cm (P122).

### Partial and combination factors (§1.6.1)

| state | action | γ fav | γ desf | ψp | ψa | source |
| --- | --- | --- | --- | --- | --- | --- |
| ELU_rotura_hormigon | Carga permanente (G) | 1.0 | 1.35 | — | — | P1509 table: Carga permanente (G) |
| ELU_rotura_hormigon | Sobrecarga (Q) | 0.0 | 1.5 | 1.0 | 0.7 | P1509 table: Sobrecarga (Q) |
| ELU_rotura_hormigon | Viento (Q) | 0.0 | 1.5 | 1.0 | 0.6 | P1509 table: Viento (Q) |
| ELU_rotura_hormigon_cimentaciones | Carga permanente (G) | 1.0 | 1.6 | — | — | P1513 table: Carga permanente (G) |
| ELU_rotura_hormigon_cimentaciones | Sobrecarga (Q) | 0.0 | 1.6 | 1.0 | 0.7 | P1513 table: Sobrecarga (Q) |
| ELU_rotura_hormigon_cimentaciones | Viento (Q) | 0.0 | 1.6 | 1.0 | 0.6 | P1513 table: Viento (Q) |
| Desplazamientos | Carga permanente (G) | 1.0 | 1.0 | — | — | P1517 table: Carga permanente (G) |
| Desplazamientos | Sobrecarga (Q) | 0.0 | 1.0 | 1.0 | 1.0 | P1517 table: Sobrecarga (Q) |
| Desplazamientos | Viento (Q) | 0.0 | 1.0 | 1.0 | 1.0 | P1517 table: Viento (Q) |

Quasi-permanent combination printed by CYPE: “Peso propio+Cargas muertas - Tabiquería+Cargas muertas - Pavimento+0.3Sobrecarga de uso” (P583 table: combination of the deflection check); ψ2 of Qa = 0.3; ψ2 of the bollard pull ('viento') = 0.0 (P276 text + P275 image92.png (Tabla 5.10 Viento C = 0.0)). The 22 + 22 + 8 CYPE combinations (§1.6.2) are in the JSON (`materials_and_parameters.combinations_1_6_2`).

## 3. Piles

### 3.1 Section and CYPE naming

| item | value | source |
| --- | --- | --- |
| Dimensiones | 40x40 cm | P220 table: Dimensiones |
| Tramo | 0.000/7.250 m | P220 table: Tramo |
| Altura libre | 6.70 m | P220 table: Altura libre |
| Recubrimiento geométrico | 5.0 cm | P220 table: Recubrimiento geométrico |
| Tamaño máximo de árido | 20 mm | P220 table: Tamaño máximo de árido |
| Hormigón | HA-50, Yc=1.5 | P220 table: Hormigón |
| Acero | B 500 S, Ys=1.15 | P220 table: Acero |
| Plano ZX | 6.70 m | P220 table: Plano ZX |
| Plano ZY | 6.70 m | P220 table: Plano ZY |
| Esquina | 4Ø25 | P220 table: Esquina |
| Cara X | 4Ø25 | P220 table: Cara X |
| Cara Y | 4Ø25 | P220 table: Cara Y |
| Cuantía | 3.68 % | P220 table: Cuantía |
| Estribos | 2eØ10+1eØ10 | P220 table: Estribos |
| Separación | 15 cm | P220 table: Separación |

Arranque section (P281 table): Tramo -0.420/0.000 m, altura libre 0.00 m, estribos 1eØ8.

Sketch: 40x40 square, 12 bars (4 per face incl. corners); 3 closed ties drawn: one perimeter tie, one inner tie around the two middle columns of bars and one inner tie around the two middle rows (P220 image image16.png).

Model mapping (from `sap2000/model/trasmallo.py`):

| axis | X (m) | sea pile (Y=0) | land pile (Y=3.45) | edge / bollard point |
| --- | --- | --- | --- | --- |
| 1 | 0.0 | P1 | P2 | P9 |
| 2 | 6.5 | P3 | P4 | P10 |
| 3 | 13.0 | P5 | P6 | P11 |
| 4 | 19.5 | P7 | P8 | P12 |
| 5 | 26.0 | P13 | P14 | P19 |
| 6 | 32.5 | P15 | P17 | P21 |
| 7 | 39.0 | P16 | P18 | P20 |

Coefficients §1.9 (P1554/P1557 tables): empotramiento cabeza/pie 1.00/1.00, pandeo X/Y 1.00/1.00, coeficiente de rigidez axil 2.00 for all piles; P9–P12, P19–P21 are CHS 159.0x5.0 points 'sin vinculación exterior'.

### 3.2 Section 1 — 'FORJADO 1' (pile head, P3)

Heading: “1. FORJADO 1 (0 - 7.00 M)” (P218). Pile not named in the body; N/M values equal Apéndice 1 §3.5 P3 'Cabeza' row 'G, Q, V' (620.1 / 353.5 / -69.0) -> this is pile P3, head section. Heading says 0 - 7.00 M but 'Datos del pilar' prints Tramo 0.000/7.250 m and the listing 'Forjado 1 (0 - 7.25 m)'.

**Detailing (Disposiciones, A19.8.2 / A19.9.5)**

| check | value | source |
| --- | --- | --- |
| Un pilar es un elemento cuyo canto es inferior a 4 veces su ancho (Artículos A19.5.3.1(7) y A19.9.5.1). | 400 mm ≤ 1600 mm | P223 table |
| La distancia libre sb (horizontal y vertical) entre barras paralelas, o entre capas horizontales de barras par | 60 mm ≥ 25 mm | P225 table |
| Las barras longitudinales deberían tener un diámetro no menor que 12 mm (Artículo A19.9.5.2(1)): | 25 mm ≥ 12 mm | P225 table |
| La distancia libre sb (horizontal y vertical) entre barras aisladas paralelas o capas horizontales de barras p | 140 mm ≥ 25 mm | P227 table |
| La separación de la armadura transversal a lo largo del pilar no debe superar scl,max (Artículo A19.9.5.3(3)): | 150 mm ≤ 300 mm | P227 table |
| El diámetro de la armadura transversal no debe ser inferior a un cuarto del diámetro máximo de las barras long | 10 mm ≥ 6.3 mm | P227 table |

Longitudinal: smin = 25 mm (s1 25 mm, s2 25 mm, s3 20 mm), Ømax 25 mm, dg 20 mm, Ømin 25 mm. Ties: smin = 25 mm (s1 10 mm, s2 25 mm, s3 20 mm); scl,max = 300 mm (s1 300 mm, s2 375 mm, s3 400 mm). The s1/s2/s3 and scl,max formula images (WMF) do not render legibly; only 'φt ≥ 1/4·φmax' is legible. Arithmetic observations (INFERENCE, not printed): clear-spacing smin = max(s1, s2, s3) with s1 = Ø (25 bars / 10 ties), s2 = dg + 5 = 25, s3 = 20 mm; for scl,max = min(s1, s2, s3): 375 = 15·Ømin(25), 400 = b = 400 mm, 300 = 12·Ømin or a fixed 300 mm (cannot be decided from the document).

**Minimum / maximum reinforcement (A19.9.5.2)**

| check | value | source |
| --- | --- | --- |
| El área total de la armadura longitudinal As no debería ser menor que As,min (Artículo A19.9.5.2(2)): | 58.91 cm² ≥ 6.4 cm² | P232 table |
| El área de la armadura longitudinal As no debería superar As,max (Artículo A19.9.5.2(3)): | 58.91 cm² ≤ 122.67 cm² | P232 table |
| El área total de la armadura longitudinal A's no debería ser menor que As,min (Artículo A19.9.5.2(2)): | 58.91 cm² ≥ 1.55 cm² | P232 table |

A's,min uses NEd = 673.90 kN. As,min formula image not legible; 1.55 cm² ≈ 0.10·NEd/fyd = 0.1·673.9/434.78 (EC2 9.5.2(2)). 6.40 cm² = 0.004·Ac (Ac = 1600 cm²); formula image not legible.

**Shear (A19.6.2)**

| item | value | source |
| --- | --- | --- |
| η (VRd,max) | 0.086 | P237 table: [Se debe satisfacer] η (occurrence 1) |
| VEd,x / VEd,y | 0.98 kN / 85.36 kN | P237 table: [Se debe satisfacer] VEd,y (occurrence 1) |
| VRd,max | 996.63 kN | P237 table: [Se debe satisfacer] VRd,max |
| position / combination (η VRd,max) | Cabeza / 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo | P237 table: statement 1 (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...') |
| η (VRd,c, printed 'VRd,s') | 0.552 | P237 table: [Se debe satisfacer] η (occurrence 2) |
| VEd,x / VEd,y | 0.34 kN / 78.86 kN | P237 table: [Se debe satisfacer] VEd,y (occurrence 2) |
| VRd,c (printed 'VRd,s') | 142.85 kN | P237 table: [Se debe satisfacer] VRd,s |
| position / combination (η VRd,c) | Cabeza / PP+CM+1.5·Tirobolardo | P237 table: statement 2 (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...') |

| VRd,max parameter | direction X | direction Y |
| --- | --- | --- |
| VRd_max | 996.63 kN | 996.63 kN |
| alpha_cw | 1.000 | 1.000 |
| sigma_cp | -12.13 MPa | -1.46 MPa |
| NEd | 620.06 kN | 620.06 kN |
| As_comp | 58.91 cm² | 19.64 cm² |
| Ac | 1600.00 cm² | 1600.00 cm² |
| fyd | 434.78 MPa | 434.78 MPa |
| fcd | 33.33 MPa | 33.33 MPa |
| bw | 400.00 mm | 400.00 mm |
| z | 249.16 mm | 249.16 mm |
| nu1 | 0.600 | 0.600 |
| alpha | 90.0 grados | 90.0 grados |
| theta | 45.0 grados | 45.0 grados |

| VRd,c parameter | direction X | direction Y |
| --- | --- | --- |
| VRd_c_printed_VRd_s | 142.85 kN | 142.85 kN |
| VRd_c_min_printed_VRd_s | 99.73 kN | 99.73 kN |
| CRd_c | 0.120 | 0.120 |
| gamma_c | 1.500 | 1.500 |
| k | 1.871 | 1.871 |
| rho_l | 0.020 | 0.020 |
| Asl | 39.27 cm² | 39.27 cm² |
| fck | 50.00 MPa | 50.00 MPa |
| sigma_cp | 2.08 MPa | 2.08 MPa |
| NEd | 332.81 kN | 332.81 kN |
| Ac | 1600.00 cm² | 1600.00 cm² |
| fcd | 33.33 MPa | 33.33 MPa |
| bw | 400.00 mm | 400.00 mm |
| d | 263.75 mm | 263.75 mm |
| v_min | 0.63 MPa | 0.63 MPa |

**Axial force + biaxial bending (A19.5.8.8, A19.6.1)**

Position Cabeza, combination 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo; η1 = 0.670, η2 = 0.913 (P242 table: η (occurrence 2)).

| item | first order (η1) | second order (η2) |
| --- | --- | --- |
| N | 620.06 kN | 620.06 kN |
| M x | 288.36 kN·m | 353.51 kN·m |
| M y | -3.81 kN·m | -68.95 kN·m |
| NRd | 925.83 kN | 679.16 kN |
| MRd,x | 430.56 kN·m | 387.20 kN·m |
| MRd,y | -5.68 kN·m | -75.52 kN·m |
| ee,x / ee,y | -6.14 mm / 465.06 mm |  |
| emin | 20.00 mm |  |

| slenderness / 2nd-order parameter | 'En el eje x' | 'En el eje y' |
| --- | --- | --- |
| lambda | 58.02 | 58.02 |
| l0 | 6.700 m | 6.700 m |
| i_c | 11.55 cm | 11.55 cm |
| Ac | 1600.00 cm² | 1600.00 cm² |
| I | 213333.33 cm4 | 213333.33 cm4 |
| lambda_inf_lim | 42.58 | 42.58 |
| A | 0.74 | 0.74 |
| phi_ef_for_A | 1.8 | 1.8 |
| B | 1.40 | 1.40 |
| omega | 0.48 | 0.48 |
| As | 58.91 cm² | 58.91 cm² |
| fyd | 434.78 MPa | 434.78 MPa |
| fcd | 33.33 MPa | 33.33 MPa |
| C | 0.70 | 0.70 |
| n | 0.12 | 0.12 |
| NEd | 620.06 kN | 620.06 kN |
| NSd | 620.06 kN | 620.06 kN |
| MSd | 353.51 kN·m | -68.95 kN·m |
| e_tot | 570.12 mm | -111.20 mm |
| e_e | 465.06 mm | -6.14 mm |
| e_i | 12.94 mm | -12.94 mm |
| theta_i | 0.0039 | 0.0039 |
| theta_0 | 0.0050 | 0.0050 |
| alpha_h | 0.7727 | 0.7727 |
| l_height | 6.700 m | 6.700 m |
| alpha_m | 1.0000 | 1.0000 |
| e2 | 92.12 mm | -92.12 mm |
| c_curvature | 9.870 | 9.870 |
| one_over_r | 0.0203 m-1 | 0.0203 m-1 |
| K_r | 1.000 | 1.000 |
| n_u | 1.48 | 1.48 |
| omega_Kr | 0.48 | 0.48 |
| n_Kr | 0.12 | 0.12 |
| n_bal | 0.40 | 0.40 |
| K_phi | 1.373 | 1.373 |
| beta | 0.213 | 0.213 |
| phi_ef_for_Kphi | 1.750 | 1.750 |
| one_over_r0 | 0.0148 m-1 | 0.0148 m-1 |
| eps_yd | 0.00217 | 0.00217 |
| d | 328 mm | 328 mm |

Formulas (legible parts of the equation images completed with the EC2 5.8.8 expressions that reproduce the printed numbers — not verbatim): λ = l0/ic = l0/sqrt(I/Ac); λlim = 20·A·B·C/sqrt(n)  (label printed 'λinf'); A = 1/(1+0.2·ϕef); B = sqrt(1+2·ω) ('Formulación UNE-EN 1992-1-1:2013'); ω = As·fyd/(Ac·fcd); n = NEd/(Ac·fcd); NSd = NEd ; MSd = NEd·etot ; etot = ee + ei + e2 (partly legible); ei = θi·l0/2 (partly legible); θi = θ0·αh·αm; e2 = (1/r)·l0²/c (partly legible); 1/r = Kr·Kϕ·1/r0; 1/r0 = εyd/(0.45·d); Kr, Kϕ per A19.5.8.8.3 (nu = 1+ω, nbal = 0.4, Kϕ = 1+β·ϕef).

Capacity diagram labels: N_max_compression = 7689.61 kN; N_max_tension = -2561.11 kN; M_max_at_N_2098_3 = 473.52 kN·m; N_at_M_max = 2098.3 kN; design_point = (-68.95;353.51;620.06) (kN·m;kN·m;kN); capacity_point = (-75.52;387.2;679.16) (kN·m;kN·m;kN) (P245 image image50.png).

Section equilibrium at ultimate (same eccentricities) — P257 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø25 | -127.50 | 127.50 | +365.17 | +0.001826 |
| 2 | Ø25 | -42.50 | 127.50 | +296.43 | +0.001482 |
| 3 | Ø25 | 42.50 | 127.50 | +227.68 | +0.001138 |
| 4 | Ø25 | 127.50 | 127.50 | +158.93 | +0.000795 |
| 5 | Ø25 | 127.50 | 42.50 | -160.77 | -0.000804 |
| 6 | Ø25 | 127.50 | -42.50 | -434.78 | -0.002402 |
| 7 | Ø25 | 127.50 | -127.50 | -434.78 | -0.004001 |
| 8 | Ø25 | 42.50 | -127.50 | -434.78 | -0.003657 |
| 9 | Ø25 | -42.50 | -127.50 | -434.78 | -0.003313 |
| 10 | Ø25 | -127.50 | -127.50 | -434.78 | -0.002970 |
| 11 | Ø25 | -127.50 | -42.50 | -274.24 | -0.001371 |
| 12 | Ø25 | -127.50 | 42.50 | +45.46 | +0.000227 |

Resultants: Cc 1422.97 kN (ex -26.86 mm, ey 140.81 mm); Cs 536.86 kN (ex -32.01 mm, ey 123.97 mm); T 1280.67 kN (ex 15.7 mm, ey -93.92 mm). Summary values: NRd 679.16 kN, MRd,x 387.20 kN·m, MRd,y -75.52 kN·m, Cc 1422.97 kN, Cs 536.86 kN, T 1280.67 kN, ecc,x -26.86 mm, ecc,y 140.81 mm, ecs,x -32.01 mm, ecs,y 123.97 mm, eT,x 15.70 mm, eT,y -93.92 mm, εcmax 0.0035, εsmax 0.0040, σcmax 33.33 MPa, σsmax 434.78 MPa. Diagram: x_neutral_axis 181.04 mm, eps_max 3.48 ‰, eps_min -5.66 ‰, sigma_max 33.33 MPa.

Section equilibrium for the design forces — P265 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø25 | -127.50 | 127.50 | +276.91 | +0.001385 |
| 2 | Ø25 | -42.50 | 127.50 | +227.99 | +0.001140 |
| 3 | Ø25 | 42.50 | 127.50 | +179.08 | +0.000895 |
| 4 | Ø25 | 127.50 | 127.50 | +130.16 | +0.000651 |
| 5 | Ø25 | 127.50 | 42.50 | -95.41 | -0.000477 |
| 6 | Ø25 | 127.50 | -42.50 | -320.98 | -0.001605 |
| 7 | Ø25 | 127.50 | -127.50 | -434.78 | -0.002733 |
| 8 | Ø25 | 42.50 | -127.50 | -434.78 | -0.002488 |
| 9 | Ø25 | -42.50 | -127.50 | -434.78 | -0.002244 |
| 10 | Ø25 | -127.50 | -127.50 | -399.80 | -0.001999 |
| 11 | Ø25 | -127.50 | -42.50 | -174.23 | -0.000871 |
| 12 | Ø25 | -127.50 | 42.50 | +51.34 | +0.000257 |

Resultants: Cc 1321.67 kN (ex -28.89 mm, ey 141.1 mm); Cs 424.85 kN (ex -31.58 mm, ey 122.46 mm); T 1126.46 kN (ex 15.4 mm, ey -102.09 mm). Summary values: NSd 620.06 kN, MSd,x 353.51 kN·m, MSd,y -68.95 kN·m, Cc 1321.67 kN, Cs 424.85 kN, T 1126.46 kN, ecc,x -28.89 mm, ecc,y 141.10 mm, ecs,x -31.58 mm, ecs,y 122.46 mm, eT,x 15.40 mm, eT,y -102.09 mm, εcmax 0.0026, εsmax 0.0027, σcmax 33.33 MPa, σsmax 434.78 MPa. Diagram: x_neutral_axis 188.19 mm, eps_max 2.56 ‰, eps_min -3.9 ‰, sigma_max 33.33 MPa.

Cracking: “La carga que produce esfuerzos de flexion en los pilotes es el tiro de bolardo dado que en situacion cuasipermanente el coeficietne de combinacion para el viento es 0 los esfuerzos de flexion en el pilote son nulos por lo que no es necesario comprobar el pilote a fisuracion. ” (P276).

### 3.3 Section 2 — 'EMPOTRAMIENTO' (foundation start / arranque, P3)

Heading: “2. EMPOTRAMIENTO” (P279). Foundation start ('Arranque') of P3: Datos del pilar Tramo -0.420/0.000 m, altura libre 0.00 m, estribos 1eØ8; NSd/MSd equal Apéndice 1 §3.5 P3 'Cimentación / Arranque' (655.6 / -352.1 / 71.3)

Detailing and min/max reinforcement: “La comprobación no procede” (P285).

**Shear (A19.6.2)**

| item | value | source |
| --- | --- | --- |
| η (VRd,max) | 0.085 | P292 table: [Se debe satisfacer] η |
| VEd,x / VEd,y | 0.98 kN / 85.36 kN | P292 table: [Se debe satisfacer] VEd,y |
| VRd,max | 1005.35 kN | P292 table: [Se debe satisfacer] VRd,max |
| position / combination (η VRd,max) | — / 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo | P292 table: statement 1 (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...') |

| VRd,max parameter | direction X | direction Y |
| --- | --- | --- |
| VRd_max | 1005.35 kN | 1005.35 kN |
| alpha_cw | 1.000 | 1.000 |
| sigma_cp | -11.91 MPa | -1.24 MPa |
| NEd | 655.55 kN | 655.55 kN |
| As_comp | 58.91 cm² | 19.64 cm² |
| Ac | 1600.00 cm² | 1600.00 cm² |
| fyd | 434.78 MPa | 434.78 MPa |
| fcd | 33.33 MPa | 33.33 MPa |
| bw | 400.00 mm | 400.00 mm |
| z | 251.34 mm | 251.34 mm |
| nu1 | 0.600 | 0.600 |
| alpha | 90.0 grados | 90.0 grados |
| theta | 45.0 grados | 45.0 grados |

**Axial force + biaxial bending (A19.5.8.8, A19.6.1)**

Position —, combination 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo; η1 = 0.642, η2 = 0.894 (P297 table: η (occurrence 2)).

| item | first order (η1) | second order (η2) |
| --- | --- | --- |
| N | 655.55 kN | 655.55 kN |
| M x | -283.56 kN·m | -352.07 kN·m |
| M y | 2.79 kN·m | 71.29 kN·m |
| NRd | 1021.59 kN | 733.05 kN |
| MRd,x | -441.89 kN·m | -393.69 kN·m |
| MRd,y | 4.34 kN·m | 79.72 kN·m |
| ee,x / ee,y | 4.25 mm / -432.56 mm |  |
| emin | 20.00 mm |  |

| slenderness / 2nd-order parameter | 'En el eje x' | 'En el eje y' |
| --- | --- | --- |
| lambda | 58.02 | 58.02 |
| l0 | 6.700 m | 6.700 m |
| i_c | 11.55 cm | 11.55 cm |
| Ac | 1600.00 cm² | 1600.00 cm² |
| I | 213333.33 cm4 | 213333.33 cm4 |
| lambda_inf_lim | 41.42 | 41.42 |
| A | 0.74 | 0.74 |
| phi_ef_for_A | 1.8 | 1.8 |
| B | 1.40 | 1.40 |
| omega | 0.48 | 0.48 |
| As | 58.91 cm² | 58.91 cm² |
| fyd | 434.78 MPa | 434.78 MPa |
| fcd | 33.33 MPa | 33.33 MPa |
| C | 0.70 | 0.70 |
| n | 0.12 | 0.12 |
| NEd | 655.55 kN | 655.55 kN |
| NSd | 655.55 kN | 655.55 kN |
| MSd | -352.07 kN·m | 71.29 kN·m |
| e_tot | -537.06 mm | 108.75 mm |
| e_e | -432.56 mm | 4.25 mm |
| e_i | -12.94 mm | 12.94 mm |
| theta_i | 0.0039 | 0.0039 |
| theta_0 | 0.0050 | 0.0050 |
| alpha_h | 0.7727 | 0.7727 |
| l_height | 6.700 m | 6.700 m |
| alpha_m | 1.0000 | 1.0000 |
| e2 | -91.56 mm | 91.56 mm |
| c_curvature | 9.870 | 9.870 |
| one_over_r | 0.0201 m-1 | 0.0201 m-1 |
| K_r | 1.000 | 1.000 |
| n_u | 1.48 | 1.48 |
| omega_Kr | 0.48 | 0.48 |
| n_Kr | 0.12 | 0.12 |
| n_bal | 0.40 | 0.40 |
| K_phi | 1.373 | 1.373 |
| beta | 0.213 | 0.213 |
| phi_ef_for_Kphi | 1.750 | 1.750 |
| one_over_r0 | 0.0147 m-1 | 0.0147 m-1 |
| eps_yd | 0.00217 | 0.00217 |
| d | 330 mm | 330 mm |

Formulas (legible parts of the equation images completed with the EC2 5.8.8 expressions that reproduce the printed numbers — not verbatim): λ = l0/ic = l0/sqrt(I/Ac); λlim = 20·A·B·C/sqrt(n)  (label printed 'λinf'); A = 1/(1+0.2·ϕef); B = sqrt(1+2·ω) ('Formulación UNE-EN 1992-1-1:2013'); ω = As·fyd/(Ac·fcd); n = NEd/(Ac·fcd); NSd = NEd ; MSd = NEd·etot ; etot = ee + ei + e2 (partly legible); ei = θi·l0/2 (partly legible); θi = θ0·αh·αm; e2 = (1/r)·l0²/c (partly legible); 1/r = Kr·Kϕ·1/r0; 1/r0 = εyd/(0.45·d); Kr, Kϕ per A19.5.8.8.3 (nu = 1+ω, nbal = 0.4, Kϕ = 1+β·ϕef).

Capacity diagram labels: N_max_compression = 7689.61 kN; N_max_tension = -2561.11 kN; M_max_at_N_2098_3 = 477.19 kN·m; N_at_M_max = 2098.3 kN; design_point = (71.29;-352.07;655.55) (kN·m;kN·m;kN); capacity_point = (79.72;-393.69;733.05) (kN·m;kN·m;kN) (P300 image image94.png).

Section equilibrium at ultimate (same eccentricities) — P312 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø25 | -129.50 | 129.50 | -434.78 | -0.003951 |
| 2 | Ø25 | -43.17 | 129.50 | -434.78 | -0.003595 |
| 3 | Ø25 | 43.17 | 129.50 | -434.78 | -0.003239 |
| 4 | Ø25 | 129.50 | 129.50 | -434.78 | -0.002882 |
| 5 | Ø25 | 129.50 | 43.17 | -258.16 | -0.001291 |
| 6 | Ø25 | 129.50 | -43.17 | +60.12 | +0.000301 |
| 7 | Ø25 | 129.50 | -129.50 | +378.40 | +0.001892 |
| 8 | Ø25 | 43.17 | -129.50 | +307.14 | +0.001536 |
| 9 | Ø25 | -43.17 | -129.50 | +235.87 | +0.001179 |
| 10 | Ø25 | -129.50 | -129.50 | +164.61 | +0.000823 |
| 11 | Ø25 | -129.50 | -43.17 | -153.67 | -0.000768 |
| 12 | Ø25 | -129.50 | 43.17 | -434.78 | -0.002360 |

Resultants: Cc 1439.73 kN (ex 27.65 mm, ey -139.89 mm); Cs 562.62 kN (ex 33.63 mm, ey -124.97 mm); T 1269.29 kN (ex -16.54 mm, ey 96.1 mm). Summary values: NRd 733.05 kN, MRd,x -393.69 kN·m, MRd,y 79.72 kN·m, Cc 1439.73 kN, Cs 562.62 kN, T 1269.29 kN, ecc,x 27.65 mm, ecc,y -139.89 mm, ecs,x 33.63 mm, ecs,y -124.97 mm, eT,x -16.54 mm, eT,y 96.10 mm, εcmax 0.0035, εsmax 0.0040, σcmax 33.33 MPa, σsmax 434.78 MPa. Diagram: x_neutral_axis 184.36 mm, eps_max 3.48 ‰, eps_min -5.54 ‰, sigma_max 33.33 MPa.

Section equilibrium for the design forces — P320 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø25 | -129.50 | 129.50 | -434.78 | -0.002603 |
| 2 | Ø25 | -43.17 | 129.50 | -434.78 | -0.002362 |
| 3 | Ø25 | 43.17 | 129.50 | -424.31 | -0.002122 |
| 4 | Ø25 | 129.50 | 129.50 | -376.20 | -0.001881 |
| 5 | Ø25 | 129.50 | 43.17 | -158.87 | -0.000794 |
| 6 | Ø25 | 129.50 | -43.17 | +58.45 | +0.000292 |
| 7 | Ø25 | 129.50 | -129.50 | +275.77 | +0.001379 |
| 8 | Ø25 | 43.17 | -129.50 | +227.67 | +0.001138 |
| 9 | Ø25 | -43.17 | -129.50 | +179.56 | +0.000898 |
| 10 | Ø25 | -129.50 | -129.50 | +131.45 | +0.000657 |
| 11 | Ø25 | -129.50 | -43.17 | -85.87 | -0.000429 |
| 12 | Ø25 | -129.50 | 43.17 | -303.19 | -0.001516 |

Resultants: Cc 1315.83 kN (ex 29.49 mm, ey -140.53 mm); Cs 428.49 kN (ex 32.46 mm, ey -123.72 mm); T 1088.78 kN (ex -17.06 mm, ey 104.83 mm). Summary values: NSd 655.55 kN, MSd,x -352.07 kN·m, MSd,y 71.29 kN·m, Cc 1315.83 kN, Cs 428.49 kN, T 1088.78 kN, ecc,x 29.49 mm, ecc,y -140.53 mm, ecs,x 32.46 mm, ecs,y -123.72 mm, eT,x -17.06 mm, eT,y 104.83 mm, εcmax 0.0025, εsmax 0.0026, σcmax 33.33 MPa, σsmax 434.78 MPa. Diagram: x_neutral_axis 191.03 mm, eps_max 2.46 ‰, eps_min -3.69 ‰, sigma_max 33.33 MPa.

Cracking: “La carga que produce esfuerzos de flexion en los pilotes es el tiro de bolardo dado que en situacion cuasipermanente el coeficietne de combinacion para el viento es 0 los esfuerzos de flexion en el pilote son nulos por lo que no es necesario comprobar el pilote a fisuracion. ” (P330).

### 3.4 Apéndice 1 §3–§4: all piles

Armado (§3.2, P1692 table): every pile 40x40, 4Ø25 esquina + 4Ø25 cara X + 4Ø25 cara Y (cuantía 3.68 %), Forjado 1 estribos 2eØ10+1eØ10 at 15 cm, Cimentación 1eØ8.

| pile | Cabeza Q % | Cabeza N,M % | Pie Q % | Pie N,M % | Arranque Q % | Arranque N,M % | §3.2 aprov Forjado | §3.2 aprov Cimentación | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 57.3 | 84.1 | 56.2 | 85.7 | 8.1 | 84.7 | 85.7 | 84.7 | P1742 table |
| P2 | 84.3 | 80.9 | 82.0 | 82.5 | 7.9 | 81.9 | 84.3 | 81.9 | P1747 table |
| P3 | 55.2 | 92.5 | 54.2 | 91.9 | 8.5 | 90.7 | 92.5 | 90.7 | P1752 table |
| P4 | 75.4 | 73.2 | 73.5 | 77.1 | 7.4 | 76.4 | 77.1 | 76.4 | P1757 table |
| P5 | 52.6 | 87.0 | 51.7 | 88.0 | 8.1 | 86.9 | 88.0 | 86.9 | P1762 table |
| P6 | 76.9 | 73.9 | 74.8 | 77.2 | 7.4 | 76.5 | 77.2 | 76.5 | P1767 table |
| P7 | 53.6 | 88.2 | 52.7 | 88.0 | 8.1 | 86.9 | 88.2 | 86.9 | P1772 table |
| P8 | 73.1 | 70.9 | 71.2 | 74.6 | 7.1 | 74.0 | 74.6 | 74.0 | P1777 table |
| P13 | 51.0 | 84.6 | 50.1 | 85.5 | 7.8 | 84.4 | 85.5 | 84.4 | P1782 table |
| P14 | 73.6 | 71.2 | 71.7 | 74.3 | 7.1 | 73.7 | 74.3 | 73.7 | P1787 table |
| P15 | 51.9 | 87.4 | 51.0 | 86.4 | 8.0 | 85.3 | 87.4 | 85.3 | P1792 table |
| P16 | 53.1 | 76.1 | 52.0 | 77.5 | 7.3 | 76.5 | 77.5 | 76.5 | P1797 table |
| P17 | 69.2 | 67.8 | 67.5 | 71.5 | 6.9 | 70.9 | 71.5 | 70.9 | P1802 table |
| P18 | 74.2 | 72.5 | 72.2 | 73.9 | 7.1 | 73.3 | 74.2 | 73.3 | P1807 table |

Governing forces per position (§3.5, P1714 table; N > 0 compression; 'N,M' rows include 2nd-order amplification):

| pile | position | naturaleza | N kN | Mxx kN·m | Myy kN·m | Qx kN | Qy kN | pésima | aprov % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Cabeza | G, V | 279.6 | 258.9 | -4.6 | 1.2 | -78.8 | Q | 57.3 |
| P1 | Cabeza | G, Q, V | 414.1 | 312.4 | 59.7 | -3.7 | -81.2 | N,M | 84.1 |
| P1 | Pie | G, V | 305.9 | -269.3 | 3.2 | 1.2 | -78.8 | Q | 56.2 |
| P1 | Pie | G, Q, V | 449.6 | -322.2 | -55.5 | -3.7 | -81.2 | N,M | 85.7 |
| P1 | Arranque | G, Q, V | 449.6 | -322.0 | -55.2 | -3.7 | -81.2 | N,M | 84.7 |
| P2 | Cabeza | G, V | -162.5 | 259.3 | 21.1 | -5.0 | -78.9 | Q | 84.3 |
| P2 | Pie | G, V | -136.2 | -269.6 | -12.1 | -5.0 | -78.9 | N,M | 82.5 |
| P2 | Arranque | G, V | -136.2 | -269.6 | -12.1 | -5.0 | -78.9 | N,M | 81.9 |
| P3 | Cabeza | G, V | 332.8 | 260.4 | -1.0 | 0.3 | -78.9 | Q | 55.2 |
| P3 | Cabeza | G, Q, V | 620.1 | 353.5 | -69.0 | 1.0 | -85.4 | N,M | 92.5 |
| P3 | Pie | G, V | 359.1 | -305.7 | 39.0 | 0.3 | -78.9 | Q | 54.2 |
| P3 | Pie | G, Q, V | 655.6 | -352.4 | 71.7 | 1.0 | -85.4 | N,M | 91.9 |
| P3 | Arranque | G, Q, V | 655.6 | -352.1 | 71.3 | 1.0 | -85.4 | N,M | 90.7 |
| P4 | Cabeza | G, V | -115.3 | 240.8 | -2.3 | 0.5 | -74.3 | Q | 75.4 |
| P4 | Pie | G, V | -89.0 | -257.2 | 0.8 | 0.5 | -74.3 | N,M | 77.1 |
| P4 | Arranque | G, V | -89.0 | -257.2 | 0.8 | 0.5 | -74.3 | N,M | 76.4 |
| P5 | Cabeza | G, V | 337.6 | 282.4 | -35.7 | 0.2 | -75.4 | Q | 52.6 |
| P5 | Cabeza | G, Q, V | 598.5 | 334.3 | 63.2 | 0.0 | -81.1 | N,M | 87.0 |
| P5 | Pie | G, V | 363.9 | -296.6 | 39.1 | 0.2 | -75.4 | Q | 51.7 |
| P5 | Pie | G, Q, V | 634.0 | -338.7 | 67.1 | 0.0 | -81.1 | N,M | 88.0 |
| P5 | Arranque | G, Q, V | 634.0 | -338.3 | 66.8 | 0.0 | -81.1 | N,M | 86.9 |
| P6 | Cabeza | G, V | -137.2 | 241.1 | 1.1 | -0.3 | -74.1 | Q | 76.9 |
| P6 | Pie | G, V | -110.9 | -255.2 | -1.1 | -0.3 | -74.1 | N,M | 77.2 |
| P6 | Arranque | G, V | -110.9 | -255.2 | -1.1 | -0.3 | -74.1 | N,M | 76.5 |
| P7 | Cabeza | G, V | 321.1 | 250.8 | -0.4 | 0.2 | -76.0 | Q | 53.6 |
| P7 | Cabeza | G, Q, V | 589.6 | 338.2 | -62.3 | 0.2 | -81.9 | N,M | 88.2 |
| P7 | Pie | G, V | 347.3 | -294.8 | 37.4 | 0.2 | -76.0 | Q | 52.7 |
| P7 | Pie | G, Q, V | 625.0 | -338.2 | 66.6 | 0.2 | -81.9 | N,M | 88.0 |
| P7 | Arranque | G, Q, V | 625.0 | -337.9 | 66.2 | 0.2 | -81.9 | N,M | 86.9 |
| P8 | Cabeza | G, V | -117.8 | 232.9 | 0.6 | -0.2 | -71.9 | Q | 73.1 |
| P8 | Pie | G, V | -91.5 | -248.5 | -0.8 | -0.2 | -71.9 | N,M | 74.6 |
| P8 | Arranque | G, V | -91.5 | -248.5 | -0.8 | -0.2 | -71.9 | N,M | 74.0 |
| P13 | Cabeza | G, V | 331.7 | 238.2 | -0.5 | 0.2 | -72.7 | Q | 51.0 |
| P13 | Cabeza | G, Q, V | 592.6 | 324.9 | -63.3 | 0.4 | -78.4 | N,M | 84.6 |
| P13 | Pie | G, V | 358.0 | -286.9 | 38.6 | 0.2 | -72.7 | Q | 50.1 |
| P13 | Pie | G, Q, V | 628.1 | -328.9 | 67.3 | 0.4 | -78.4 | N,M | 85.5 |
| P13 | Arranque | G, Q, V | 628.1 | -328.5 | 66.9 | 0.4 | -78.4 | N,M | 84.4 |
| P14 | Cabeza | G, V | -131.2 | 232.3 | 0.2 | -0.1 | -71.4 | Q | 73.6 |
| P14 | Pie | G, V | -104.9 | -246.0 | -0.6 | -0.1 | -71.4 | N,M | 74.3 |
| P14 | Arranque | G, V | -104.9 | -246.0 | -0.6 | -0.1 | -71.4 | N,M | 73.7 |
| P15 | Cabeza | G, V | 320.9 | 242.9 | 0.2 | 0.1 | -73.5 | Q | 51.9 |
| P15 | Cabeza | G, Q, V | 608.2 | 334.8 | 66.9 | -0.6 | -80.0 | N,M | 87.4 |
| P15 | Pie | G, V | 347.2 | -286.2 | 37.0 | 0.1 | -73.5 | Q | 51.0 |
| P15 | Pie | G, Q, V | 643.7 | -332.9 | -68.6 | -0.6 | -80.0 | N,M | 86.4 |
| P15 | Arranque | G, Q, V | 643.7 | -332.5 | -68.2 | -0.6 | -80.0 | N,M | 85.3 |
| P16 | Cabeza | G, V | 236.2 | 232.2 | 2.6 | -0.5 | -70.7 | Q | 53.1 |
| P16 | Cabeza | G, Q, V | 370.7 | 281.1 | -57.2 | 4.3 | -73.1 | N,M | 76.1 |
| P16 | Pie | G, V | 262.5 | -241.6 | -0.7 | -0.5 | -70.7 | Q | 52.0 |
| P16 | Pie | G, Q, V | 406.2 | -290.0 | 53.4 | 4.3 | -73.1 | N,M | 77.5 |
| P16 | Arranque | G, Q, V | 406.2 | -289.7 | 53.2 | 4.3 | -73.1 | N,M | 76.5 |
| P17 | Cabeza | G, V | -103.6 | 223.3 | 3.5 | -0.9 | -69.0 | Q | 69.2 |
| P17 | Pie | G, V | -77.3 | -238.9 | -2.4 | -0.9 | -69.0 | N,M | 71.5 |
| P17 | Arranque | G, V | -77.3 | -238.9 | -2.4 | -0.9 | -69.0 | N,M | 70.9 |
| P18 | Cabeza | G, V | -144.6 | 232.6 | -19.2 | 4.4 | -70.8 | Q | 74.2 |
| P18 | Pie | G, V | -118.3 | -241.9 | 10.1 | 4.4 | -70.8 | N,M | 73.9 |
| P18 | Arranque | G, V | -118.3 | -241.9 | 10.1 | 4.4 | -70.8 | N,M | 73.3 |

Combinations: G, V = PP+CM+1.5·Tirobolardo; G, Q, V = 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo (notes of the §4.2 tables).

Medición (§3.6): encofrado 150.08 m², hormigón 15.01 m³, Ø25 6108.2 kg, Ø10 1309.0 kg, Ø8 16.8 kg, total +10 % 8177.4 kg, cuantía 495.27 kg/m³.

Per-hypothesis head/base forces (§3.3) are in the JSON (`piles.appendix_1_section_3.esfuerzos_por_hipotesis_3_3`).

## 4. Beams

### 4.1 Mapping CYPE pórticos ↔ model

| axis | X m | CYPE pórtico | section | cantilever tramo (sea) | span tramo | model frames |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.0 | Pórtico 3 | 80x55+15x30 (inverted L; model VIGA_L80x55_ALA15x30) | P9-P1 | P1-P2 | VT1_* (group PORTICO_3) |
| 2 | 6.5 | Pórtico 4 | 50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30) | P10-P3 | P3-P4 | VT2_* (group PORTICO_4) |
| 3 | 13.0 | Pórtico 5 | 50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30) | P11-P5 | P5-P6 | VT3_* (group PORTICO_5) |
| 4 | 19.5 | Pórtico 6 | 50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30) | P12-P7 | P7-P8 | VT4_* (group PORTICO_6) |
| 5 | 26.0 | Pórtico 7 | 50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30) | P19-P13 | P13-P14 | VT5_* (group PORTICO_7) |
| 6 | 32.5 | Pórtico 8 | 50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30) | P21-P15 | P15-P17 | VT6_* (group PORTICO_8) |
| 7 | 39.0 | Pórtico 9 | 80x55+15x30 (inverted L; model VIGA_L80x55_ALA15x30_M) | P20-P16 | P16-P18 | VT7_* (group PORTICO_9) |

Cantilever tramo: from the sea-edge / bollard point (CYPE CHS 159.0x5.0 'punto fijo' Y = -0.45, 'mitad inferior'; model Y = -0.375) to the sea pile (Y = 0.00); CYPE L = 0.10 m (clear length between the CHS and the pile face).
Span tramo: c/c 3.45 m, CYPE L = 3.05 m (clear span between pile faces).

- Pórtico 1 (25x30): P9-P20 — sea edge (bollard line) Y=-0.45 CYPE / -0.375 model; CYPE lists ONE tramo P9-P20 over the full 39 m; zone 1/3L, 2/3L, 3/3L split the whole beam; x up to 36.00 m Model: VBM_* (group PORTICO_1).
- Pórtico 10 (25x30): P2-P4, P4-P6, P6-P8, P8-P14, P14-P17, P17-P18 — land edge; CYPE runs it through the land piles (Y=3.45); model Y=3.675; L = 6.10 m = 6.50 - 0.40 (clear between pile faces) Model: VBT_* (group PORTICO_10).
- No 'Pórtico 2' appears in the listing (numbering jumps 1 -> 3).
- Listing 'x' = 'Distancia al origen de la barra' (P340 notation). For P1-P2-type tramos x = 0.00 .. 3.05 m, i.e. measured from the face of the sea pile (model Y ≈ 0.20 + x) — INFERENCE from L = 3.05 = 3.45 - 0.40; for the cantilevers x = 0.00 .. 0.10 m. Caveat C16: the body/drawing hogging moment at 'P3' (-273.71) exceeds the listing value at x = 0.00 (-266.03), so the section called 'P3' is not the listing x = 0.00.

### 4.2 Body check of P3–P4

| item | value | source |
| --- | --- | --- |
| Dimensiones | 50x55+15x30+15x30 | P336 table: Dimensiones |
| Luz libre | 3.1 m | P336 table: Luz libre |
| Recubrimiento geométrico superior | 5.0 cm | P336 table: Recubrimiento geométrico superior |
| Recubrimiento geométrico inferior | 5.0 cm | P336 table: Recubrimiento geométrico inferior |
| Recubrimiento geométrico lateral | 5.0 cm | P336 table: Recubrimiento geométrico lateral |
| Hormigón | HA-35, Yc=1.5 | P336 table: Hormigón |
| Armadura longitudinal | B 500 S, Ys=1.15 | P336 table: Armadura longitudinal |
| Armadura transversal | B 500 S, Ys=1.15 | P336 table: Armadura transversal |

Bars (drawing image97, P336 table): top: 5Ø20 (471), leg 25 drawn at the right (P4) end only; side (piel) web: I1Ø10+D1Ø10 (470), right end leg 17 + return 8; section tag: 50x55+15x30+15x30; ledges: I1Ø10+D1Ø10 M. Alas (421), straight; bottom web: 5Ø20 (471), leg 25 drawn at the right end only; bottom ledges: I1Ø20+D1Ø20 (490), leg 17 at the right end, marks 18 at both ends. Stirrups: Asw 2.36 cm² at 100 mm (P364 table); listing drawings show 37x{(1eØ10+1rØ10)+(1eØ10)}/10.

Summary (P340 table): Q η = 95.8 % at '0.488 m', N,M η = 84.0 % at 'P3', torsion checks N.P., Estado CUMPLE / η = 95.8. Cracking (P342 table): all faces N.P.(1), Vfis Cumple. Deflection (P345 table): fT,max 1.53 mm ≤ 12.20 mm (L/250), fA,max 1.33 mm ≤ 6.10 mm (L/500).

#### Section “P3 - P4 (P3 - 1.448 m, Negativos)”

| check | value | source |
| --- | --- | --- |
| La distancia libre sb (horizontal y vertical) entre barras paralelas, o entre capas horizontales de barras par | 63 mm ≥ 25 mm | P352 table |
| Las barras longitudinales deben disponerse con una separación máxima de 350 mm (Artículo 9.2.3(4)). | 150 mm ≤ 350 mm | P352 table |
| La distancia libre sb (horizontal y vertical) entre barras aisladas paralelas o capas horizontales de barras p | 90 mm ≥ 25 mm | P354 table |
| El área de la armadura longitudinal de tracción no debe ser inferior a As,min (Artículo A19.9.2.1.1(1)). | 15.71 cm² ≥ 5.09 cm² | P359 table |
| La separación longitudinal máxima entre grupos de armaduras de cortante no debería exceder (Artículo A19.9.2.2 | 100 mm ≤ 360 mm | P364 table |
| La separación transversal st,trans entre ramas de armaduras transversales debe cumplir la condición siguiente: | 180 mm ≤ 360 mm | P364 table |
| Cortante en la dirección Y: La cuantía de la armadura de cortante ρw no debe ser menor que ρw,min (Artículo A1 | 0.0047 ≥ 0.000900 | P364 table |

Longitudinal smin = 25 mm (s1 20 mm, s2 25 mm, s3 20 mm); sb = 150 mm. As,min: z 432.00 mm, W 28339.35 cm³, fct,m,fl 3.37 MPa, fyd 434.78 MPa.

Shear at 0.488 m, combination 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo:

| item | value | source |
| --- | --- | --- |
| η VRd,max / η VRd,s | 0.258 / 0.958 | P364 table: [Se debe satisfacer] η (occurrence 2) |
| VEd,y | 390.18 kN | P364 table: [Se debe satisfacer] VEd,y (occurrence 1) |
| VRd,max | 1512.00 kN | P364 table: [Se debe satisfacer] VRd,max,Vy |
| VRd,s | 407.15 kN | P364 table: [Se debe satisfacer] VRd,s,Vy |
| strut: VRd_max | 1512.00 kN | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] VRd,max |
| strut: alpha_cw | 1.000 | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] αcw |
| strut: sigma_cp | -2.62 MPa | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] σcp |
| strut: NEd | 0.00 kN | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] NEd |
| strut: As_comp | 21.99 cm² | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] A's |
| strut: Ac | 3650.00 cm² | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] Ac |
| strut: fyd | 434.78 MPa | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] fyd |
| strut: fcd | 23.33 MPa | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] fcd |
| strut: bw | 500.00 mm | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] bw |
| strut: z | 432.00 mm | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] z |
| strut: nu1 | 0.600 | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] ν1 |
| strut: alpha | 90.0 grados | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] α |
| strut: theta | 45.0 grados | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] θ |
| stirrups: VRd_s | 407.15 kN | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] VRd,s |
| stirrups: Asw | 2.36 cm² | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] Asw |
| stirrups: s | 100 mm | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] s |
| stirrups: z | 43.20 cm | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] z |
| stirrups: fywd | 400.00 MPa | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] fywd |
| stirrups: fywk | 500.00 MPa | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] fywk |
| stirrups: alpha | 90.0 grados | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] α |
| stirrups: theta | 45.0 grados | P364 table: [Esfuerzo cortante de agotamiento por tracción en el alma] θ |
| spacing: s | 100 mm | P364 table: [Separación de las armaduras transversales] s |
| spacing: s_l_max | 360 mm | P364 table: [Separación de las armaduras transversales] sl,max |
| spacing: d | 480.00 mm | P364 table: [Separación de las armaduras transversales] d |
| spacing: alpha | 90.0 grados | P364 table: [Separación de las armaduras transversales] α |
| spacing: s_t_max | 360 mm | P364 table: [Separación de las armaduras transversales > La separación transversal] st,max |
| spacing: d | 480.00 mm | P364 table: [Separación de las armaduras transversales > La separación transversal] d |
| min ratio: rho_w | 0.0047 | P364 table: [Cuantía mecánica mínima] ρw |
| min ratio: Asw | 2.36 cm² | P364 table: [Cuantía mecánica mínima] Asw |
| min ratio: s | 100 mm | P364 table: [Cuantía mecánica mínima] s |
| min ratio: bw | 500.00 mm | P364 table: [Cuantía mecánica mínima] bw |
| min ratio: alpha | 90.0 grados | P364 table: [Cuantía mecánica mínima] α |
| min ratio: rho_w_min | 0.000900 | P364 table: [Cuantía mecánica mínima] ρw,min |
| min ratio: fctm | 3.21 MPa | P364 table: [Cuantía mecánica mínima] fctm |
| min ratio: fck | 35.00 MPa | P364 table: [Cuantía mecánica mínima] fck |
| min ratio: fyk | 500.00 MPa | P364 table: [Cuantía mecánica mínima] fyk |

Bending at P3 (Envolvente de momentos mínimos en situaciones persistentes o transitorias): MEd,x = -273.71 kN·m, MRd,x = -325.78 kN·m, η = 0.840.

Equilibrium at ultimate — P381 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø20 | -180.00 | 235.82 | -434.78 | -0.009950 |
| 2 | Ø20 | -97.50 | 235.82 | -434.78 | -0.009950 |
| 3 | Ø20 | 0.00 | 235.82 | -434.78 | -0.009950 |
| 4 | Ø20 | 97.50 | 235.82 | -434.78 | -0.009950 |
| 5 | Ø20 | 180.00 | 235.82 | -434.78 | -0.009950 |
| 6 | Ø10 | 185.00 | -9.18 | +0.00 | -0.004026 |
| 7 | Ø10 | 335.00 | -9.18 | -434.78 | -0.004026 |
| 8 | Ø20 | 330.00 | -174.18 | -7.16 | -0.000036 |
| 9 | Ø20 | 180.00 | -174.18 | -7.16 | -0.000036 |
| 10 | Ø20 | 97.50 | -174.18 | -7.16 | -0.000036 |
| 11 | Ø20 | 0.00 | -174.18 | -7.16 | -0.000036 |
| 12 | Ø20 | -97.50 | -174.18 | -7.16 | -0.000036 |
| 13 | Ø20 | -180.00 | -174.18 | -7.16 | -0.000036 |
| 14 | Ø20 | -330.00 | -174.18 | -7.16 | -0.000036 |
| 15 | Ø10 | -335.00 | -9.18 | -434.78 | -0.004026 |
| 16 | Ø10 | -185.00 | -9.18 | +0.00 | -0.004026 |

Resultants: Cc 767.0 kN (ey -219.16 mm); Cs 0.0 kN (ey 0.0 mm); T 767.0 kN (ey 205.59 mm). Summary: NRd 0.00 kN, MRd,x -325.78 kN·m, MRd,y 0.00 kN·m, Cc 767.00 kN, Cs 0.00 kN, T 767.00 kN, ecc,x 0.00 mm, ecc,y -219.16 mm, ecs 0.00 mm, eT,x 0.00 mm, eT,y 205.59 mm, εcmax 0.0017, εsmax 0.0100, σcmax 22.65 MPa, σsmax 434.78 MPa. Diagram: x_neutral_axis 68.52 mm, eps_min_top -11.64 ‰, eps_max_bottom 1.66 ‰, sigma_max 22.65 MPa.

Equilibrium for the design forces — P389 table:

| bar | Ø | x mm | y mm | σs MPa | ε |
| --- | --- | --- | --- | --- | --- |
| 1 | Ø20 | -180.00 | 235.82 | -392.45 | -0.001962 |
| 2 | Ø20 | -97.50 | 235.82 | -392.45 | -0.001962 |
| 3 | Ø20 | 0.00 | 235.82 | -392.45 | -0.001962 |
| 4 | Ø20 | 97.50 | 235.82 | -392.45 | -0.001962 |
| 5 | Ø20 | 180.00 | 235.82 | -392.45 | -0.001962 |
| 6 | Ø10 | 185.00 | -9.18 | +0.00 | -0.000662 |
| 7 | Ø10 | 335.00 | -9.18 | -132.41 | -0.000662 |
| 8 | Ø20 | 330.00 | -174.18 | +42.72 | +0.000214 |
| 9 | Ø20 | 180.00 | -174.18 | +42.72 | +0.000214 |
| 10 | Ø20 | 97.50 | -174.18 | +42.72 | +0.000214 |
| 11 | Ø20 | 0.00 | -174.18 | +42.72 | +0.000214 |
| 12 | Ø20 | -97.50 | -174.18 | +42.72 | +0.000214 |
| 13 | Ø20 | -180.00 | -174.18 | +42.72 | +0.000214 |
| 14 | Ø20 | -330.00 | -174.18 | +42.72 | +0.000214 |
| 15 | Ø10 | -335.00 | -9.18 | -132.41 | -0.000662 |
| 16 | Ø10 | -185.00 | -9.18 | +0.00 | -0.000662 |

Resultants: Cc 543.32 kN (ey -206.44 mm); Cs 93.94 kN (ey -174.18 mm); T 637.26 kN (ey 227.83 mm). Summary: NEd 0.00 kN, MEd,x -273.71 kN·m, MEd,y 0.00 kN·m, Cc 543.32 kN, Cs 93.94 kN, T 637.26 kN, ecc,x 0.00 mm, ecc,y -206.44 mm, ecs,x 0.00 mm, ecs,y -174.18 mm, eT,x 0.00 mm, eT,y 227.83 mm, εcmax 0.000600, εsmax 0.0020, σcmax 11.65 MPa, σsmax 392.45 MPa. Diagram: x_neutral_axis 110.25 mm, eps_min_top -2.33 ‰, eps_max_bottom 0.59 ‰, sigma_max 11.65 MPa.

INFERENCE (geometry, not printed): coordinates are relative to the gross-section centroid, which lies 244.18 mm above the soffit for 50x55 + 2x(15x30) (Ac = 3650 cm² printed); hence y = +235.82 -> top bars 70 mm below the top face, y = -174.18 -> bottom bars 70 mm above the soffit, y = -9.18 -> side bars 235 mm above the soffit. x = ±185 is 65 mm inside the 50 cm web faces (web 'piel' bars I1Ø10+D1Ø10 (470)); x = ±335 is 65 mm inside the 80 cm ledge faces ('M. Alas (421)'). PRINTED fact: bars 6/16 (x = ±185) carry σs = 0.00 although their strain equals that of bars 7/15 (x = ±335) — reason not printed.

Torsion: every torsion check “La comprobación del estado límite de agotamiento por torsión no procede, ya que no hay momento torsor.” (P397–P435); comment P437: “En las vigas centrales dada las diferencias de rigidez entre vigas y alveoplacas los momentos por excentricidad de cargas se traducen en flexiones en las alveoplacas. En las vigas extremas la alveoplaca apoya en el eje de los pilotes por lo que tampoco produce torsiones.”.

The “Positivos” block: The 'Positivos' block (P440-P529) is a verbatim copy of the 'Negativos' block (P351-P437): same tables, MEd,x = -273.71 at 'P3', η = 0.840, same bars and stresses. No positive-moment (sagging) section check is printed.

#### Cracking (body, P531–P575)

Heading beam: “P5 - P6” — Heading names P5 - P6 while the summary table (P342) is for P3 - P4 and image117 shows Pórtico 6 (P7-P8). All 8 faces + minimum area: “La comprobación no procede, ya que la tensión de tracción máxima en el hormigón no supera la resistencia a tracción del mismo.”.

Hand check: “En situación cuasipermanente la viga tiene los siguientes momentos:” — image117 labels: M(P8) -8.47 kN·m, M span 86.66 kN·m, M(P7) -12.21 kN·m. “Comprobamos las tensiones con +86 kNm”.

| image118 value | value |
| --- | --- |
| NEd | 0.0 kN |
| MEd_x | 86.0 kN·m |
| MEd_y | 0.0 kN·m |
| strain_top_fibre | 0.000082 |
| strain_top_bars | 0.000069 |
| strain_bottom_bars | -0.000051 |
| strain_bottom_fibre | -0.000065 |
| stress_top_fibre | 2.73 MPa |
| stress_top_bars | 13.75 MPa |
| stress_bottom_bars | -10.27 MPa |
| stress_bottom_fibre | -2.2 MPa |
| wk | 0.0 mm |

Conclusion (P575): “La resistencia a tracción del C35 es de 3.2 Mpa y los momentos cuasipermanentes generan unas tracciones máximas de 2.20 Mpa. Por lo que no fisura.”

#### Deflection (P577–P588)

La flecha máxima se produce en la sección "1.45 m" para la combinación de acciones: Peso propio+Cargas muertas - Tabiquería+Cargas muertas - Pavimento+0.3Sobrecarga de uso. fT,max 1.53 mm ≤ fT,lim 12.20 mm = L/250 with L = 3.05 m.

| escalón | ti d | tf d | f0(ti) mm | Δfi(ti) mm | f(ti) mm | fdif mm | ftot mm | ftot,max mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1-2 | 28 | 90 | 0.0 | 0.15 | 0.15 | 0.05 | 0.21 | 0.21 |
| 2-3 | 90 | 120 | 0.21 | 0.02 | 0.23 | 0.01 | 0.24 | 0.24 |
| 3-4 | 120 | 360 | 0.24 | 0.03 | 0.27 | 0.07 | 0.34 | 0.34 |
| 4-∞ | 360 | ∞ | 0.34 | 0.67 | 1.01 | 0.53 | 1.53 | 1.53 |

### 4.3 Apéndice 1 §2 “Listado de armado de vigas” (all pórticos)

M in kN·m (negative = hogging), V in kN, T in kN·m (printed '[kN]'), x in m from the origin of the tramo, areas in cm² (Asw in cm²/m); '—' = '--' in the listing.

| pórtico | tramo | section | zone | M min @x | M max @x | V min @x | V max @x | T min @x | T max @x | As sup real/nec | As inf real/nec | Asw real/nec | src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pórtico 1 | P9-P20 | 25x30 | 1/3L | -32.84 @6.39 | 25.61 @2.86 | -33.25 @6.36 | 30.96 @6.5 | — | — | 4.02/3.44 | 4.02/2.65 | 6.7/3.95 | P1608 table |
| Pórtico 1 | P9-P20 | 25x30 | 2/3L | -28.85 @19.43 | 21.05 @16.18 | -30.54 @19.36 | 30.54 @19.5 | — | — | 4.02/3.0 | 4.02/2.17 | 6.7/3.62 | P1608 table |
| Pórtico 1 | P9-P20 | 25x30 | 3/3L | -32.84 @32.47 | 25.61 @36.0 | -30.96 @32.36 | 33.25 @32.5 | — | — | 4.02/3.44 | 4.02/2.65 | 6.7/3.95 | P1608 table |
| Pórtico 3 | P9-P1 | 80x55+15x30 | 1/3L | -58.06 @0.0 | 4.9 @0.0 | -101.53 @0.0 | 70.73 @0.0 | -25.79 @0.0 | — | 12.47/11.0 | 15.86/8.22 | 23.56/8.28 | P1614 table |
| Pórtico 3 | P9-P1 | 80x55+15x30 | 2/3L | -59.24 @0.05 | 8.42 @0.05 | -103.19 @0.05 | 70.05 @0.05 | -25.79 @0.05 | — | 13.58/11.0 | 18.85/8.22 | 23.56/8.38 | P1614 table |
| Pórtico 3 | P9-P1 | 80x55+15x30 | 3/3L | -60.51 @0.1 | 11.91 @0.1 | -104.85 @0.1 | 69.38 @0.1 | -25.79 @0.1 | — | 15.71/11.0 | 18.85/8.22 | 23.56/8.47 | P1614 table |
| Pórtico 3 | P1-P2 | 80x55+15x30 | 1/3L | -315.48 @0.0 | 119.59 @0.88 | — | 333.92 @0.0 | — | 27.43 @0.0 | 15.71/15.98 | 18.85/8.22 | 23.56/17.04 | P1614 table |
| Pórtico 3 | P1-P2 | 80x55+15x30 | 2/3L | -81.56 @1.07 | 168.21 @2.02 | -69.96 @2.02 | 233.15 @1.07 | -1.76 @2.02 | — | 15.71/7.96 | 18.85/10.91 | 23.56/13.49 | P1614 table |
| Pórtico 3 | P1-P2 | 80x55+15x30 | 3/3L | — | 275.15 @3.05 | -165.91 @3.05 | 173.67 @2.21 | -15.85 @2.78 | — | 15.71/0.4 | 18.85/13.8 | 23.56/10.05 | P1614 table |
| Pórtico 4 | P10-P3 | 50x55+15x30+15x30 | 1/3L | -5.19 @0.0 | — | -64.78 @0.0 | — | — | 2.81 @0.0 | 11.28/8.1 | 19.01/0.0 | 23.56/4.73 | P1620 table |
| Pórtico 4 | P10-P3 | 50x55+15x30+15x30 | 2/3L | -8.47 @0.05 | — | -66.38 @0.05 | — | — | 2.81 @0.05 | 13.42/8.1 | 21.99/0.0 | 23.56/4.73 | P1620 table |
| Pórtico 4 | P10-P3 | 50x55+15x30+15x30 | 3/3L | -11.83 @0.1 | — | -67.98 @0.1 | — | — | 2.81 @0.1 | 15.71/8.1 | 21.99/0.0 | 23.56/4.73 | P1620 table |
| Pórtico 4 | P3-P4 | 50x55+15x30+15x30 | 1/3L | -266.03 @0.0 | 219.89 @0.88 | — | 471.19 @0.0 | -3.16 @0.0 | — | 15.71/13.72 | 21.99/13.34 | 23.56/22.58 | P1620 table |
| Pórtico 4 | P3-P4 | 50x55+15x30+15x30 | 2/3L | -28.57 @1.07 | 294.61 @2.02 | -150.02 @2.02 | 256.78 @1.07 | — | — | 15.71/5.19 | 21.99/15.1 | 23.56/14.86 | P1620 table |
| Pórtico 4 | P3-P4 | 50x55+15x30+15x30 | 3/3L | — | 293.21 @2.4 | -333.66 @3.05 | 137.5 @2.21 | — | 2.05 @2.78 | 15.71/1.21 | 21.99/15.1 | 23.56/14.1 | P1620 table |
| Pórtico 5 | P11-P5 | 50x55+15x30+15x30 | 1/3L | -60.19 @0.0 | 4.12 @0.0 | -128.67 @0.0 | 60.99 @0.0 | — | — | 11.28/10.46 | 19.01/6.37 | 23.56/7.45 | P1626 table |
| Pórtico 5 | P11-P5 | 50x55+15x30+15x30 | 2/3L | -62.69 @0.05 | 7.16 @0.05 | -130.0 @0.05 | 60.47 @0.05 | — | — | 13.42/10.46 | 21.99/6.37 | 23.56/7.52 | P1626 table |
| Pórtico 5 | P11-P5 | 50x55+15x30+15x30 | 3/3L | -65.26 @0.1 | 10.17 @0.1 | -131.33 @0.1 | 59.96 @0.1 | — | — | 15.71/10.46 | 21.99/6.37 | 23.56/7.6 | P1626 table |
| Pórtico 5 | P5-P6 | 50x55+15x30+15x30 | 1/3L | -305.42 @0.0 | 201.96 @0.88 | — | 440.82 @0.0 | — | — | 15.71/15.75 | 21.99/12.02 | 23.56/21.75 | P1626 table |
| Pórtico 5 | P5-P6 | 50x55+15x30+15x30 | 2/3L | -60.3 @1.07 | 255.48 @2.02 | -134.27 @2.02 | 258.09 @1.07 | — | — | 15.71/6.94 | 21.99/13.51 | 23.56/14.94 | P1626 table |
| Pórtico 5 | P5-P6 | 50x55+15x30+15x30 | 3/3L | — | 270.09 @2.78 | -298.84 @3.05 | 152.52 @2.21 | — | — | 15.71/1.09 | 21.99/13.78 | 23.56/12.57 | P1626 table |
| Pórtico 6 | P12-P7 | 50x55+15x30+15x30 | 1/3L | -4.89 @0.0 | — | -61.11 @0.0 | — | — | — | 11.28/7.78 | 19.01/0.0 | 23.56/4.73 | P1632 table |
| Pórtico 6 | P12-P7 | 50x55+15x30+15x30 | 2/3L | -7.99 @0.05 | — | -62.71 @0.05 | — | — | — | 13.42/7.78 | 21.99/0.0 | 23.56/4.73 | P1632 table |
| Pórtico 6 | P12-P7 | 50x55+15x30+15x30 | 3/3L | -11.16 @0.1 | — | -64.31 @0.1 | — | — | — | 15.71/7.78 | 21.99/0.0 | 23.56/4.73 | P1632 table |
| Pórtico 6 | P7-P8 | 50x55+15x30+15x30 | 1/3L | -256.9 @0.0 | 200.74 @0.88 | — | 438.61 @0.0 | — | — | 15.71/13.22 | 21.99/12.13 | 23.56/21.12 | P1632 table |
| Pórtico 6 | P7-P8 | 50x55+15x30+15x30 | 2/3L | -30.08 @1.07 | 271.55 @2.02 | -136.04 @2.02 | 243.14 @1.07 | — | — | 15.71/5.1 | 21.99/14.07 | 23.56/14.07 | P1632 table |
| Pórtico 6 | P7-P8 | 50x55+15x30+15x30 | 3/3L | — | 275.5 @2.4 | -306.21 @3.05 | 134.36 @2.21 | — | — | 15.71/1.12 | 21.99/14.07 | 23.56/12.86 | P1632 table |
| Pórtico 7 | P19-P13 | 50x55+15x30+15x30 | 1/3L | -60.19 @0.0 | 4.12 @0.0 | -128.67 @0.0 | 60.99 @0.0 | — | — | 11.28/10.21 | 19.01/6.37 | 23.56/7.45 | P1638 table |
| Pórtico 7 | P19-P13 | 50x55+15x30+15x30 | 2/3L | -62.69 @0.05 | 7.16 @0.05 | -130.0 @0.05 | 60.47 @0.05 | — | — | 13.42/10.21 | 21.99/6.37 | 23.56/7.52 | P1638 table |
| Pórtico 7 | P19-P13 | 50x55+15x30+15x30 | 3/3L | -65.26 @0.1 | 10.17 @0.1 | -131.33 @0.1 | 59.96 @0.1 | — | — | 15.71/10.21 | 21.99/6.37 | 23.56/7.6 | P1638 table |
| Pórtico 7 | P13-P14 | 50x55+15x30+15x30 | 1/3L | -296.38 @0.0 | 201.96 @0.88 | — | 434.91 @0.0 | — | — | 15.71/15.28 | 21.99/12.02 | 23.56/21.41 | P1638 table |
| Pórtico 7 | P13-P14 | 50x55+15x30+15x30 | 2/3L | -57.58 @1.07 | 253.73 @2.02 | -134.27 @2.02 | 252.17 @1.07 | — | — | 15.71/6.69 | 21.99/13.23 | 23.56/14.59 | P1638 table |
| Pórtico 7 | P13-P14 | 50x55+15x30+15x30 | 3/3L | — | 262.67 @2.78 | -298.84 @3.05 | 146.6 @2.21 | — | — | 15.71/1.09 | 21.99/13.38 | 23.56/12.57 | P1638 table |
| Pórtico 8 | P21-P15 | 50x55+15x30+15x30 | 1/3L | -5.19 @0.0 | — | -64.78 @0.0 | — | -2.81 @0.0 | — | 11.28/7.61 | 19.01/0.0 | 23.56/4.73 | P1644 table |
| Pórtico 8 | P21-P15 | 50x55+15x30+15x30 | 2/3L | -8.47 @0.05 | — | -66.38 @0.05 | — | -2.81 @0.05 | — | 13.42/7.61 | 21.99/0.0 | 23.56/4.73 | P1644 table |
| Pórtico 8 | P21-P15 | 50x55+15x30+15x30 | 3/3L | -11.83 @0.1 | — | -67.98 @0.1 | — | -2.81 @0.1 | — | 15.71/7.61 | 21.99/0.0 | 23.56/4.73 | P1644 table |
| Pórtico 8 | P15-P17 | 50x55+15x30+15x30 | 1/3L | -247.96 @0.0 | 219.89 @0.88 | — | 464.06 @0.0 | — | 3.16 @0.0 | 15.71/12.79 | 21.99/13.34 | 23.56/21.89 | P1644 table |
| Pórtico 8 | P15-P17 | 50x55+15x30+15x30 | 2/3L | -23.16 @1.07 | 291.11 @2.02 | -150.02 @2.02 | 244.93 @1.07 | — | — | 15.71/5.09 | 21.99/14.91 | 23.56/14.17 | P1644 table |
| Pórtico 8 | P15-P17 | 50x55+15x30+15x30 | 3/3L | — | 282.86 @2.4 | -333.66 @3.05 | 125.67 @2.21 | -2.05 @2.78 | — | 15.71/1.21 | 21.99/14.91 | 23.56/14.1 | P1644 table |
| Pórtico 9 | P20-P16 | 80x55+15x30 | 1/3L | -58.07 @0.0 | 4.9 @0.0 | -101.53 @0.0 | 70.73 @0.0 | — | 25.79 @0.0 | 11.82/10.26 | 15.86/8.22 | 23.56/8.28 | P1650 table |
| Pórtico 9 | P20-P16 | 80x55+15x30 | 2/3L | -59.25 @0.05 | 8.42 @0.05 | -103.19 @0.05 | 70.05 @0.05 | — | 25.79 @0.05 | 13.42/10.26 | 18.85/8.22 | 23.56/8.38 | P1650 table |
| Pórtico 9 | P20-P16 | 80x55+15x30 | 3/3L | -60.52 @0.1 | 11.91 @0.1 | -104.85 @0.1 | 69.38 @0.1 | — | 25.79 @0.1 | 15.71/10.26 | 18.85/8.22 | 23.56/8.47 | P1650 table |
| Pórtico 9 | P16-P18 | 80x55+15x30 | 1/3L | -287.95 @0.0 | 119.59 @0.88 | — | 315.96 @0.0 | -27.64 @0.0 | — | 15.71/14.56 | 18.85/8.22 | 23.56/16.0 | P1650 table |
| Pórtico 9 | P16-P18 | 80x55+15x30 | 2/3L | -73.29 @1.07 | 159.32 @2.02 | -69.96 @2.02 | 215.09 @1.07 | — | 1.76 @2.02 | 15.71/7.56 | 18.85/10.11 | 23.56/12.45 | P1650 table |
| Pórtico 9 | P16-P18 | 80x55+15x30 | 3/3L | — | 247.61 @3.05 | -165.91 @3.05 | 155.61 @2.21 | — | 15.85 @2.78 | 15.71/0.4 | 18.85/12.38 | 23.56/9.01 | P1650 table |
| Pórtico 10 | P2-P4 | 25x30 | 1/3L | -16.79 @0.0 | 19.64 @2.03 | — | 27.27 @0.0 | — | — | 4.02/1.83 | 4.02/2.02 | 6.7/2.97 | P1656 table |
| Pórtico 10 | P2-P4 | 25x30 | 2/3L | — | 22.49 @2.71 | -12.01 @4.07 | 7.8 @2.03 | — | — | 4.02/0.0 | 4.02/2.32 | 6.7/2.37 | P1656 table |
| Pórtico 10 | P2-P4 | 25x30 | 3/3L | -29.22 @6.1 | 15.01 @4.07 | -31.49 @6.1 | — | — | — | 4.02/3.28 | 4.02/1.71 | 6.7/3.47 | P1656 table |
| Pórtico 10 | P4-P6 | 25x30 | 1/3L | -26.85 @0.0 | 13.69 @2.03 | — | 29.61 @0.0 | — | — | 4.02/3.25 | 4.02/1.71 | 6.7/3.24 | P1656 table |
| Pórtico 10 | P4-P6 | 25x30 | 2/3L | — | 18.94 @3.05 | -9.46 @4.07 | 10.12 @2.03 | — | — | 4.02/0.0 | 4.02/1.94 | 6.7/2.37 | P1656 table |
| Pórtico 10 | P4-P6 | 25x30 | 3/3L | -24.77 @6.1 | 14.3 @4.07 | -28.95 @6.1 | — | — | — | 4.02/2.89 | 4.02/1.71 | 6.7/3.17 | P1656 table |
| Pórtico 10 | P6-P8 | 25x30 | 1/3L | -25.09 @0.0 | 14.48 @2.03 | — | 29.2 @0.0 | — | — | 4.02/2.89 | 4.02/1.71 | 6.7/3.2 | P1656 table |
| Pórtico 10 | P6-P8 | 25x30 | 2/3L | — | 19.38 @3.05 | -9.8 @4.07 | 9.71 @2.03 | — | — | 4.02/0.0 | 4.02/1.99 | 6.7/2.37 | P1656 table |
| Pórtico 10 | P6-P8 | 25x30 | 3/3L | -25.39 @6.1 | 14.39 @4.07 | -29.29 @6.1 | — | — | — | 4.02/2.95 | 4.02/1.71 | 6.7/3.21 | P1656 table |
| Pórtico 10 | P8-P14 | 25x30 | 1/3L | -25.5 @0.0 | 14.36 @2.03 | — | 29.33 @0.0 | — | — | 4.02/2.95 | 4.02/1.71 | 6.7/3.21 | P1661 table |
| Pórtico 10 | P8-P14 | 25x30 | 2/3L | — | 19.38 @3.05 | -9.69 @4.07 | 9.84 @2.03 | — | — | 4.02/0.0 | 4.02/1.99 | 6.7/2.37 | P1661 table |
| Pórtico 10 | P8-P14 | 25x30 | 3/3L | -25.04 @6.1 | 14.53 @4.07 | -29.18 @6.1 | — | — | — | 4.02/2.89 | 4.02/1.71 | 6.7/3.19 | P1661 table |
| Pórtico 10 | P14-P17 | 25x30 | 1/3L | -24.77 @0.0 | 14.28 @2.03 | — | 28.95 @0.0 | — | — | 4.02/2.89 | 4.02/1.71 | 6.7/3.17 | P1661 table |
| Pórtico 10 | P14-P17 | 25x30 | 2/3L | — | 18.94 @3.05 | -10.05 @4.07 | 9.46 @2.03 | — | — | 4.02/0.0 | 4.02/1.94 | 6.7/2.37 | P1661 table |
| Pórtico 10 | P14-P17 | 25x30 | 3/3L | -26.65 @6.1 | 13.69 @4.07 | -29.55 @6.1 | — | — | — | 4.02/3.25 | 4.02/1.71 | 6.7/3.24 | P1661 table |
| Pórtico 10 | P17-P18 | 25x30 | 1/3L | -29.36 @0.0 | 14.94 @2.03 | — | 31.53 @0.0 | — | — | 4.02/3.28 | 4.02/1.71 | 6.7/3.47 | P1661 table |
| Pórtico 10 | P17-P18 | 25x30 | 2/3L | — | 22.48 @3.39 | -7.8 @4.07 | 12.05 @2.03 | — | — | 4.02/0.0 | 4.02/2.32 | 6.7/2.37 | P1661 table |
| Pórtico 10 | P17-P18 | 25x30 | 3/3L | -16.79 @6.1 | 19.65 @4.07 | -27.27 @6.1 | — | — | — | 4.02/1.83 | 4.02/2.02 | 6.7/2.97 | P1661 table |

| pórtico | tramo | F. activa | F. a plazo infinito |
| --- | --- | --- | --- |
| Pórtico 1 | P9-P20 | 4.45 mm, L/1354 (L: 6.03 m) | 5.67 mm, L/1065 (L: 6.04 m) |
| Pórtico 3 | P9-P1 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 3 | P1-P2 | 0.18 mm, L/17159 (L: 3.05 m) | 0.27 mm, L/11203 (L: 3.05 m) |
| Pórtico 4 | P10-P3 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 4 | P3-P4 | 1.33 mm, L/2300 (L: 3.05 m) | 1.53 mm, L/1992 (L: 3.05 m) |
| Pórtico 5 | P11-P5 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 5 | P5-P6 | 0.99 mm, L/3095 (L: 3.05 m) | 1.17 mm, L/2612 (L: 3.05 m) |
| Pórtico 6 | P12-P7 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 6 | P7-P8 | 1.05 mm, L/2896 (L: 3.05 m) | 1.24 mm, L/2456 (L: 3.05 m) |
| Pórtico 7 | P19-P13 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 7 | P13-P14 | 0.99 mm, L/3095 (L: 3.05 m) | 1.17 mm, L/2612 (L: 3.05 m) |
| Pórtico 8 | P21-P15 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 8 | P15-P17 | 1.33 mm, L/2300 (L: 3.05 m) | 1.53 mm, L/1992 (L: 3.05 m) |
| Pórtico 9 | P20-P16 | 0.00 mm, <L/1000 (L: 0.10 m) | 0.00 mm, <L/1000 (L: 0.10 m) |
| Pórtico 9 | P16-P18 | 0.18 mm, L/17159 (L: 3.05 m) | 0.27 mm, L/11203 (L: 3.05 m) |
| Pórtico 10 | P2-P4 | 1.80 mm, L/3390 (L: 6.10 m) | 2.70 mm, L/2262 (L: 6.10 m) |
| Pórtico 10 | P4-P6 | 1.59 mm, L/3840 (L: 6.10 m) | 2.27 mm, L/2685 (L: 6.10 m) |
| Pórtico 10 | P6-P8 | 1.68 mm, L/3636 (L: 6.10 m) | 2.39 mm, L/2549 (L: 6.10 m) |
| Pórtico 10 | P8-P14 | 1.68 mm, L/3636 (L: 6.10 m) | 2.39 mm, L/2549 (L: 6.10 m) |
| Pórtico 10 | P14-P17 | 1.59 mm, L/3837 (L: 6.10 m) | 2.27 mm, L/2683 (L: 6.10 m) |
| Pórtico 10 | P17-P18 | 1.80 mm, L/3388 (L: 6.10 m) | 2.70 mm, L/2262 (L: 6.10 m) |

### 4.4 Apéndice 1 §4.3 checks per tramo

| tramo | Q | N,M | torsion η | Estado | fT,max/lim mm | fA,max/lim mm | src |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P9 - P20 | 58.9 % @'6.359 m' | 82.3 % @'6.359 m' | N.P. | CUMPLE / η = 82.3 | 5.67/24.14 | 4.45/12.06 | P1813 table |
| P9 - P1 | 25.8 % @'0.100 m' | 80.5 % @'P9' | Tc 4.6 %, Tst 15.3 %, Tsl 9.8 % @'0.000 m', TNMx 86.1 % @'0.000 m', TVy 8.0 % @'0.100 m' | CUMPLE / η = 86.1 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P1 - P2 | 72.3 % @'0.488 m' | 93.4 % @'P1' | Tc 4.9 % @'0.000 m', TVy 15.7 % @'0.000 m' | CUMPLE / η = 93.4 | 0.27/12.2 | 0.18/6.1 | P1813 table |
| P10 - P3 | 16.7 % @'0.100 m' | 73.6 % @'P10' | N.P. | CUMPLE / η = 73.6 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P3 - P4 | 95.8 % @'0.488 m' | 84.0 % @'P3' | N.P. | CUMPLE / η = 95.8 | 1.53/12.2 | 1.33/6.1 | P1813 table |
| P11 - P5 | 32.3 % @'0.100 m' | 94.4 % @'P11' | N.P. | CUMPLE / η = 94.4 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P5 - P6 | 92.3 % @'0.488 m' | 96.0 % @'P5' | N.P. | CUMPLE / η = 96.0 | 1.17/12.2 | 0.99/6.1 | P1813 table |
| P12 - P7 | 15.8 % @'0.100 m' | 70.7 % @'P12' | N.P. | CUMPLE / η = 70.7 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P7 - P8 | 89.7 % @'0.488 m' | 81.0 % @'P7' | N.P. | CUMPLE / η = 89.7 | 1.24/12.2 | 1.05/6.1 | P1813 table |
| P19 - P13 | 32.3 % @'0.100 m' | 92.3 % @'P19' | N.P. | CUMPLE / η = 92.3 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P13 - P14 | 90.9 % @'0.488 m' | 93.3 % @'P13' | N.P. | CUMPLE / η = 93.3 | 1.17/12.2 | 0.99/6.1 | P1813 table |
| P21 - P15 | 16.7 % @'0.100 m' | 69.2 % @'P21' | N.P. | CUMPLE / η = 69.2 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P15 - P17 | 92.9 % @'0.488 m' | 78.5 % @'P15' | N.P. | CUMPLE / η = 92.9 | 1.53/12.2 | 1.33/6.1 | P1813 table |
| P20 - P16 | 25.8 % @'0.100 m' | 78.6 % @'P20' | Tc 4.6 %, Tst 15.3 %, Tsl 10.0 % @'0.000 m', TNMx 84.6 % @'0.000 m', TVy 8.0 % @'0.100 m' | CUMPLE / η = 84.6 | 0.0/0.4 | 0.0/0.2 | P1813 table |
| P16 - P18 | 67.9 % @'0.488 m' | 85.4 % @'P16' | Tc 4.9 % @'0.000 m', TVy 15.1 % @'0.000 m' | CUMPLE / η = 85.4 | 0.27/12.2 | 0.18/6.1 | P1813 table |
| P2 - P4 | 51.7 % @'5.862 m' | 78.5 % @'6.100 m' | N.P. | CUMPLE / η = 78.5 | 2.7/24.4 | 1.8/12.2 | P1813 table |
| P17 - P18 | 51.8 % @'0.238 m' | 78.7 % @'P17' | N.P. | CUMPLE / η = 78.7 | 2.7/24.4 | 1.8/12.2 | P1813 table |
| P4 - P6 | 48.4 % @'0.238 m' | 77.9 % @'P4' | N.P. | CUMPLE / η = 77.9 | 2.27/24.4 | 1.59/12.2 | P1815 table |
| P6 - P8 | 47.8 % @'5.862 m' | 71.0 % @'6.100 m' | N.P. | CUMPLE / η = 71.0 | 2.39/24.4 | 1.68/12.2 | P1815 table |
| P8 - P14 | 47.9 % @'0.238 m' | 71.0 % @'P8' | N.P. | CUMPLE / η = 71.0 | 2.39/24.4 | 1.68/12.2 | P1815 table |
| P14 - P17 | 48.3 % @'5.862 m' | 77.8 % @'6.100 m' | N.P. | CUMPLE / η = 77.8 | 2.27/24.4 | 1.59/12.2 | P1815 table |

Cracking (P1818–P1826 tables): every tramo N.P.(1) on all faces and σsr, Vfis Cumple, Estado CUMPLE.

### 4.5 Bar schedules from the listing drawings (images 203–212)

Bar schedules read from the CYPE beam drawings (Apéndice 1 §2, images 203-212). Lengths in cm; hook/anchor legs in cm; I = izquierda, D = derecha, e = estribo, r = rama; 'M. Alas' = bars in the ledges. Upper/lower group = position of the label in the drawing (upper group = top and web-side bars, lower group = bottom and ledge bars).

- **Pórtico 3** (P1613 image image204.png, confidence high); section: 80x55+15x30; upper: 5Ø20 (474) legs 29 / 25, D1Ø20 (490) legs 17 / 17, marks 18 / 18; stirrups: 37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40; lower: D1Ø20 (490) legs 17 / 17, marks 18 / 18, 5Ø20 (471) legs 25 / 25, D2Ø10 M. Alas (421); envelope labels: {"My_min": -318.8, "My_max": 275.15, "My_end": -8.28, "Vz": [70.73, -104.85, 333.92, -165.91]}
- **Pórtico 4** (P1619 image image205.png, confidence high); section: 50x55+15x30+15x30; upper: I1Ø10+D1Ø10 (470) legs 17 / 17, 8 / 8, 5Ø20 (471) legs 25 / 25; stirrups: 37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40; lower: I1Ø20+D1Ø20 (490) legs 17 / 17, marks 18 / 18, 5Ø20 (471) legs 25 / 25, I1Ø10+D1Ø10 M. Alas (421); envelope labels: {"My_min": -273.71, "My_max": 294.6, "My_end": -25.04, "Vz": [-67.98, 471.19, -333.66]}
- **Pórtico 5** (P1625 image image206.png, confidence high); same_bars_as: Pórtico 4; envelope labels: {"My_min": -312.87, "My_max": 270.09, "My_end": -22.53, "Vz": [60.99, -131.33, 440.82, -298.84]}
- **Pórtico 6** (P1631 image image207.png, confidence high); same_bars_as: Pórtico 4; envelope labels: {"My_min": -264.0, "My_max": 275.49, "My_end": -23.03, "Vz": [-64.31, 438.61, -306.21]}
- **Pórtico 7** (P1637 image image208.png, confidence high); same_bars_as: Pórtico 4; envelope labels: {"My_min": -303.83, "My_max": 262.67, "My_end": -22.53, "Vz": [60.99, -131.33, 434.91, -298.84]}
- **Pórtico 8** (P1643 image image209.png, confidence high); same_bars_as: Pórtico 4; envelope labels: {"My_min": -255.61, "My_max": 291.09, "My_end": -25.04, "Vz": [-67.98, 464.06, -333.66]}
- **Pórtico 9** (P1649 image image210.png, confidence high); section: 80x55+15x30; upper: 5Ø20 (472) legs 27 / 25, I1Ø20 (490) legs 17 / 17, marks 18 / 18; stirrups: 37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40; lower: I1Ø20 (490) legs 17 / 17, marks 18 / 18, 5Ø20 (471) legs 25 / 25, I2Ø10 M. Alas (421); envelope labels: {"My_min": -291.23, "My_max": 247.61, "My_end": -8.28, "Vz": [70.73, -104.85, 315.96, -165.91]}
- **Pórtico 1** (P1607 image image203.png, confidence low (small raster labels)); section: 25x30; stirrups: 261x1eØ8 /15 over 3914; top_bars: 2Ø16 (450), 2Ø16 (745), 2Ø16 (800), 2Ø16 (755), 2Ø16 (885), 2Ø16 (600)?, 2Ø16 (485); top_laps: 115.9, 116.4, 116.1, 115.2, 115.6, 117.1; bottom_bars: 2Ø16 (765), 2Ø16 (735), 2Ø16 (735), 2Ø16 (715), 2Ø16 (740), 2Ø16 (765); bottom_laps: 81.5, 81.5, 82, 82, 8?.2; envelope labels: {"support_My": {"P9": -16.68, "P10": -32.84, "P11": -27.93, "P12": -28.85, "P19": -27.93, "P21": -32.84, "P20": -16.83}, "span_My_max": [25.61, 20.22, 21.05, 21.05, 20.23, 25.61]}
- **Pórtico 10** (P1655 image image211.png + P1660 image image212.png, confidence medium); section: 25x30; stirrups: 128x1eØ8 /15 over 1910 (P2-P8, plus 40 / 20) and 128x1eØ8 /15 over 1910 (P8-P18, plus 20 / 40); top_bars: 2Ø16 (460) leg 12, 2Ø16 (820), 2Ø16 (690), 2Ø16 (835), 2Ø16 (695), 2Ø16 (810), 2Ø16 (435) leg 12; top_laps: 119.3, 117.5, 115.2, 114.9, 115, 115.6; bottom_bars: 2Ø16 (765) leg 12, 2Ø16 (725), 2Ø16 (745), 2Ø16 (725), 2Ø16 (730), 2Ø16 (765) leg 12; bottom_laps: 81.8, 80.7, 80.7, 81.6, 82.7; envelope labels: {"support_My": {"P2": -17.86, "P4": -31.36, "P6": -27.81, "P8": -28.34, "P14": -27.81, "P17": -31.4, "P18": -17.86}, "span_My_max": {"P2-P4": 22.49, "P4-P6": 18.94, "P6-P8": 19.38, "P8-P14": 19.38, "P14-P17": 18.94, "P17-P18": 22.48}}

### 4.6 Bar counts from As,real (INFERENCE)

- WARNING: INFERENCE (not transcribed): bar counts deduced from 'Área Real' values (Ø20 = 3.1416 cm², Ø16 = 2.0106 cm², Ø10 = 0.7854 cm², Ø8 = 0.5027 cm²) and cross-checked with the drawings.
- 15.71 cm²: 5Ø20 (15.708) — top of all transverse beams (drawings: 5Ø20 (471)/(472)/(474))
- 21.99 cm²: 7Ø20 (21.99) — bottom of inner beams P3-P4 type = 5Ø20 web + I1Ø20+D1Ø20 ledges; confirmed by P381 table (bars 8-14)
- 18.85 cm²: 6Ø20 (18.85) — bottom of end beams (Pórticos 3, 9) = 5Ø20 + 1Ø20 in the single ledge (D1Ø20 / I1Ø20)
- 4.02 cm²: 2Ø16 (4.02) — top and bottom of edge beams 25x30 (drawings 2Ø16)
- 23.56 cm²/m: 3 legs Ø10 at 10 cm (3·0.7854/0.10) — equals Asw 2.36 cm² @ 100 mm of P364 table; drawings 37x{(1eØ10+1rØ10)+(1eØ10)}/10
- 6.70 cm²/m: 2 legs Ø8 at 15 cm (2·0.5027/0.15) — edge beams 1eØ8/15
- non_integer_values: {"values": [11.28, 13.42, 19.01, 12.47, 13.58, 15.86, 11.82], "interpretation": "cantilever zones (L = 0.10 m) next to the bar ends: CYPE counts a reduced effective area of partially anchored bars — not a bar count. INFERENCE."}
- pile: 12Ø25 = 58.91 cm² (printed), 4 per face; A's = 19.64 cm² = 4Ø25 (one face) used in σcp for the Y direction (P237 table)
- pile_Asl_39_27: 39.27 cm² = 8Ø25 used as Asl for VRd,c (P237 table) — INFERENCE (2 faces?)

## 5. Alveoplacas (P592–P605, Apéndice 1 §1.10)

“Los momentos máximos positivos obtenidos en las alveoplacas son de 100.08 kN y los momentos máximos negativos son de -100.32 kN. Los cortantes máximos son de 105.52 kN.” (P593). Envelope (image121): spans M+ {"PL1": 100.08, "PL2": 70.79, "PL3": 77.06, "PL4": 77.06, "PL5": 70.79, "PL6": 100.08}; supports M− {"axis2 (P3-P4, Pórtico 4)": -100.32, "axis3 (P5-P6)": -74.16, "axis4 (P7-P8)": -82.07, "axis5 (P13-P14)": -74.16, "axis6 (P15-P17)": -100.32, "axis1/axis7": "M = -0.00 kN*m tooltip at P2"}; V start/end {"PL1": [71.9, -105.52], "PL2": [93.18, -84.87], "PL3": [87.77, -90.28], "PL4": [90.28, -87.77], "PL5": [84.87, -93.18], "PL6": [105.52, -71.9]} (kN·m/m and kN/m (per 1 m band, §1.10 'Esfuerzos por bandas de 1 m')).

Proposed plate (image122): P25-1 M.ULT 158.7, M.FIS 55.9, RIG.TOT 63550, RIG.FIS 63550, M.SER.1 71.9, M.SER.2 104.4 (kN·m/m ; rigidez kN·m²/m).

“Y se disponen los siguientes armados de acuerdo a la hoja de autorización de la misma:” — plan image123: axis1_P1_P2_B0: 17Ø8/13 (165), segment (150), distribution width 211; axis2_P3_P4_B1: 17Ø12/13 (3?0) segments (197) + (163) -> 360 (image121 prints (390) = 197+193: CONFLICT); axis3_P5_P6_B2: 18Ø10/12 (325) segments (162) + (163); plates: PL1, PL2, PL3 = P25-1, h=25+5; edge beams 25x30; note: image cropped after PL3 (axes 4-7 not shown). Negative bars along the pier (image121): axis1 Ø8/13 (165) = (150) + 15; axis2 Ø12/13 (390) = (197)+(193); axis3 Ø10/12 (325) = (162)+(163); axis4 Ø10/12 (325) = (162)+(163); axis5 Ø10/12 (325) = (162)+(163); axis6 Ø1?/13 (390) = (192)+(198) (partly hidden; Ø12 by symmetry — INFERENCE); axis7 Ø8/13 (165) = (150) + 15.

| DIAM. | SEPAR. | M.SEC.T | M.SEC.M | M.fis. |
| --- | --- | --- | --- | --- |
| Ø8 | 130 | 45.3 | 45.3 | 40.4 |
| Ø8 | 120 | 59.2 | 59.2 | 40.4 |
| Ø10 | 130 | 70.3 | 70.3 | 40.4 |
| Ø10 | 120 | 87.1 | 87.1 | 40.4 |
| Ø12 | 130 | 100.5 | 100.4 | 40.4 |
| Ø16 | 200 | 118.4 | 118.3 | 40.4 |

Ficha §1.10 (per 1 m band), positive bending (P1574 table) and negative bending (P1575 table):

| ref | M ult | M fis | EI total | EI fis | M serv I | M serv II | M serv III |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P25-1 | 158.7 | 55.9 | 63550.0 | 63550.0 | 71.9 | 104.4 | 121.0 |
| P25-2 | 220.6 | 55.9 | 64230.0 | 64230.0 | 109.1 | 142.1 | 159.0 |
| P25-3 | 221.2 | 55.9 | 64530.0 | 64530.0 | 115.4 | 162.8 | 179.7 |
| P25-4 | 235.5 | 55.9 | 65560.0 | 65560.0 | 114.5 | 193.3 | 210.6 |
| P25-5 | 240.2 | 55.9 | 65710.0 | 65710.0 | 115.9 | 212.3 | 229.6 |

| refuerzo superior | M ult tipo | M ult macizado | M fis | EI total | EI fis | V ult |
| --- | --- | --- | --- | --- | --- | --- |
| Ø8 /130 | 45.3 | 45.3 | 40.4 | 64390.0 | 4820.0 | 129.2 |
| Ø8 /120 | 59.2 | 59.2 | 40.4 | 65240.0 | 6270.0 | 125.8 |
| Ø10 /130 | 70.3 | 70.3 | 40.4 | 65920.0 | 7420.0 | 123.6 |
| Ø10 /120 | 87.1 | 87.1 | 40.4 | 66940.0 | 9160.0 | 126.8 |
| Ø12 /130 | 100.5 | 100.4 | 40.4 | 67760.0 | 10520.0 | 125.0 |
| Ø16 /200 | 118.4 | 118.3 | 40.4 | 68840.0 | 12340.0 | 125.0 |
| Ø16 /170 | 137.4 | 137.3 | 40.4 | 69980.0 | 14240.0 | 125.0 |
| Ø16 /150 | 156.1 | 156.0 | 40.4 | 71700.0 | 16090.0 | 125.0 |

Plate description (P1566 table): PRENOR (PREF. INDUSTRIALES DEL NORTE) / Canto total del forjado: 30 cm / Espesor de la capa de compresión: 5 cm / Ancho de la placa: 1200 mm / Ancho mínimo de la placa: 300 mm / Entrega mínima: 8 cm / Entrega máxima: 20 cm / Entrega lateral: 5 cm / Hormigón de la placa: HA-40, Yc=1.5 / Hormigón de la capa y juntas: HA-25, Yc=1.5 / Acero de negativos: B 500 S, Ys=1.15 / Peso propio: 4.1 kN/m² / Volumen de hormigón: 0.05 m³/m²

## 6. Viga cantil (P606–P608)

“Se dispone en el armado del cantil 4φ20 y cercos φ10/0.10 a efectos de la carga de atraque tenemos una losa de 5 cm de capa de compresion y 4.65 que actua como diafragma y transmite las cargas de los atraques a los dinteles principales. El momento debido al atraque es de 410 kNm tomando una luz de 6.50 m. Con una anchura de 4.65 m las tracciones en los extremos son de 410/4.65 = 83 kN.  La resistencia a traccion de 4φ20 son 4*314*400 N = 502 Kn que resisten adecuadamente las cargas de atraque. ”

| item | value |
| --- | --- |
| reinforcement | 4φ20 y cercos φ10/0.10 |
| compression_layer | 5 cm |
| diaphragm_width | 4.65 m |
| M_atraque | 410 kN·m |
| span | 6.5 m |
| end_tension | 83 kN |
| tension_resistance_4phi20 | 502 kN |

The document does not identify which member is the 'viga cantil'; its 4φ20 + cercos φ10/0.10 match no beam of the CYPE listing (edge beams Pórtico 1/10: 2Ø16 top + 2Ø16 bottom, cercos Ø8/15). The hand check uses 400 MPa for the bars and 314 mm² per φ20. UNRESOLVED. Arithmetic check: 410/4.65 = 88.2 kN, not the printed 83 kN (still far below 502 kN).

## 7. Discrepancies and caveats

- **C1** — Pile body section 1 heading 'FORJADO 1 (0 - 7.00 M)' (P218) but 'Datos del pilar' Tramo 0.000/7.250 m (P220 table) and listing 'Forjado 1 (0 - 7.25 m)' (P1714 table); §3.2 'Armado de pilares' (P1692 table) and §3.3 (P1702 table) print Tramo 0.00/6.70 m (flexible length below the beam soffit); buckling length l0 = 6.700 m (both planes). Origin of the 7.00: the model description (P175-P182) says the piles are taken as fixed 'a partir de una longitud de 6.40 m', the simplified frame gives the maximum moment at 6.5 m depth and 'del aldo [sic] de la seguridad' 7.00 is adopted for the fixity in the general model; the CYPE run actually listed uses 7.25 m (tramo 0.000/7.250). (P218, P220 table, P245 table, P1692 table, P175, P182)
- **C2** — Utilisation mismatch body vs listing for P3: body η2 = 0.913 (cabeza) vs listing 'N,M' 92.5 %; body EMPOTRAMIENTO η2 = 0.894 vs listing 'Arranque' 90.7 % (and 'Pie' 91.9 %). Forces are identical (620.06/353.51/-68.95 ↔ 620.1/353.5/-69.0; 655.55/-352.07/71.29 ↔ 655.6/-352.1/71.3). Recomputing η2 from the printed NSd/MSd/NRd/MRd gives 0.913 and 0.894, so the listing percentages use a different measure. UNRESOLVED. (P242 table, P297 table, P1714 table, P1751 table)
- **C3** — The body pile sections are not named. Identified as P3 because the printed forces equal the P3 rows of §3.5 (P3 is also the pile with the highest listing utilisation, 92.5 %). (P1714 table)
- **C4** — Pile shear 'VRd,s' (142.85 kN, min 99.73 kN) is computed with the formula for members WITHOUT shear reinforcement (VRd,c, A19.6.2.2(1)); ties are not counted. (P237 table)
- **C5** — Beam section 'P3 - P4 (P3 - P4, Positivos)' (P440-P529) is an exact copy of the 'Negativos' section (P351-P437): no sagging-moment check is printed; η_N,M = 0.840 is for MEd,x = -273.71 at 'P3'. (P351-P529)
- **C6** — Crack-check heading names 'P5 - P6' (P532) while the summary table is for P3 - P4 (P342 table); image117 of the hand check shows Pórtico 6 (P7-P8, P12) with M_qp = 86.66 kN·m; the check then uses +86 kN·m. (P532, P342 table, P569 image117)
- **C7** — Beam equilibrium tables: side bars 6/16 (x = ±185 mm) carry σs = 0.00 while bars 7/15 (x = ±335 mm, same strain) are counted; reason not printed. (P381 table, P389 table)
- **C8** — fywd printed 400 MPa (not 434.78) in the stirrup resistance VRd,s = 407.15 kN. (P364 table)
- **C9** — Steel printed 'B 500 S' by CYPE (P1591 table, P220 table) vs 'B500 SD' in the project text (P112, P121). (P1591 table, P121)
- **C10** — Listing Torsor values are printed with unit '[kN]' (should be kN·m). (P1614 table)
- **C11** — Slab negative bars at axis 2: image123 reads 17Ø12/13 (3?0) with segments 197+163 = 360, image121 reads Ø12/13 (390) with 197+193. (P600 image123, P593 image121)
- **C12** — Viga cantil text (P607) gives 4φ20 + cercos φ10/0.10, which does not match any beam in the listing (edge beams 2Ø16 + 2Ø16, Ø8/15). (P607, P1608 table)
- **C13** — Crack width limits (wmax) are never printed: every face is 'N.P.(1)' (concrete tension < fct). (P342 table, P1818-P1827 tables)
- **C14** — Listing zones where 'Área Nec.' exceeds 'Área Real' (CYPE still reports CUMPLE in §4.3): P1-P2 1/3L As_top: nec 15.98 > real 15.71 (P1614 table); P5-P6 1/3L As_top: nec 15.75 > real 15.71 (P1626 table) (P1608-P1661 tables)
- **C15** — Viga cantil hand check (P607): '410/4.65 = 83 kN' — the division gives 88.2 kN; the check still holds against the printed 502 kN (4·314 mm²·400 MPa). (P607)
- **C16** — Hogging moment at the sea pile: the body check and the listing drawings give a larger value than the listing zone table. Pórtico 4 / P3-P4: body MEd,x = -273.71 kN·m at 'P3' (P369 table) = drawing label -273.71 (image205), but listing 1/3L 'Momento mín.' = -266.03 kN·m at x = 0.00 (P1620 table). Same pattern on every transverse beam, span tramo, drawing label / listing 1/3L M_min at x = 0.00: Pórtico 3 (P1-P2) -318.80/-315.48, Pórtico 5 (P5-P6) -312.87/-305.42, Pórtico 6 (P7-P8) -264.00/-256.90, Pórtico 7 (P13-P14) -303.83/-296.38, Pórtico 8 (P15-P17) -255.61/-247.96, Pórtico 9 (P16-P18) -291.23/-287.95 kN·m. Shear peaks agree (e.g. 471.19 kN at x = 0.00 in both). The document does not say where 'P3' is taken; the listing x = 0.00 is therefore not the section of the body bending check, and the 'x from the pile face' reading of beams.model_mapping.x_origin_note is only an inference. (P369 table; listing P1614, P1620, P1626, P1632, P1638, P1644, P1650 tables; drawings image204-image210 (P1613-P1649))

## 8. Design data NOT in the document

- **Anchorage lengths (lbd) and lap lengths as computed values** — not printed as check values; lap lengths appear only as dimension labels in the edge-beam drawings (≈115-119 cm top, ≈81-83 cm bottom for 2Ø16, image203/211/212, low-medium confidence); hook legs in the transverse-beam drawings
- **Crack-width calculation values (wk, sr,max, σs, εsm-εcm, ρp,eff, Ac,eff, hc,eff, k1..k4, kt, wmax)** — not printed: all faces N.P.(1); only the hand check with σct = 2.20 MPa < 3.2 MPa and image118 (wk = 0.00 mm)
- **Positive-moment (sagging) section check of the transverse beams** — not printed (the 'Positivos' block duplicates the negative one); listing gives only As,nec/As,real per zone
- **Detailed checks for any beam other than P3-P4 and any pile other than P3** — only summary η per check in Apéndice 1 §4.2/§4.3 and As per zone in §2
- **Torsion design values** — only η for P9-P1 and P20-P16 in §4.3 (Tc 4.6 %, Tst 15.3 %, Tsl 9.8/10.0 %, TNMx 86.1/84.6 %, TVy 8.0 %, P1-P2/P16-P18 Tc 4.9 %, TVy 15.7/15.1 %); no detailed torsion calculation
- **Es of reinforcement, fctm of HA-50, fctk,0.05, Ecm used for deflection/cracking** — not printed (Es implied ≈ 200 GPa by εyd = 0.00217)
- **Pile fatigue / durability / crack checks** — pile crack check explicitly skipped (P276, P330)
- **Deflection check details for beams other than P3-P4** — only fT,max / fA,max per tramo (P1830 table, P1608-P1661 tables)
- **Exposure-class based cover calculation (cmin,dur, Δcdev)** — only the result 5 cm (P113/P118/P122) and 'Recubrimiento geométrico 5.0 cm'
- **Formula expressions** — stored as WMF images; partially legible after rendering; see formulas_seen_in_render fields
- **Bar layout of the other transverse beams** — AVAILABLE in the listing drawings image204-image210 (same scheme as P3-P4 for inner frames, 5Ø20 + 1Ø20 ledge for end frames) — see beams.drawings_bar_layout; counts cross-checked by beams.inferred_bar_layouts
