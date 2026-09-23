# Código Estructural (2021), Anejo 19: design formulas for the Muelle de Trasmallo checks

**Scope.** This spec covers the concrete checks we have to code for the SAP2000 model of the 40 m module: 14 piles 40x40 HA-50 with 12Ø25, inner transverse beams "50x55+15x30+15x30" and end beams "80x55+15x30" in HA-35, edge beams 25x30, B500SD, exposure XS3, cover 50 mm.

- The legal basis is Real Decreto 470/2021, *Código Estructural* (CE). Its Anejo 19 (A19) is EN 1992-1-1 with the Spanish nationally determined parameters written into the text. Anejo 18 covers basis of design.
- Every formula below was checked against the numbers CYPECAD 2023 printed in Anejo 10: the body results at P217-P575 and Apéndice 1 at P1449-P1835.
- The script `validate_codigo.py`, in this folder, recomputes them. Result: **151 PASS, 0 FAIL, 25 INFO** (after the independent check, which added U.53, U.54, K.18 and P.06 and corrected several notes). A PASS means the value is within 0.5 %, or within half a unit of the last digit CYPE printed. INFO rows are either code-strict alternatives, sensitivity runs or items that have no CYPE target.
- The full output is in section 11.
- Clause numbers are given as "A19.x.y". Page references "BOE p. 98xxx" point to BOE-A-2021-13681, Sección I (PDF saved as `boe/ce2021.pdf`).

---------------------------------------------------------------------------------------------------

## 0. Main findings (read first)

**Checks that match exactly (to 0.00-0.02 %)**

- All CYPE ULS capacities, using a fibre section, provided CYPE's conventions **C1-C3** are reproduced:
  - pile: NRd/MRd = 679.16/387.20/-75.52, 925.83/430.56/-5.68, 1021.59/-441.89/4.34 and 733.05/-393.69/79.72;
  - beam: MRd,x = -325.78.
- The concrete, compression-steel and tension resultants and their eccentricities.
- Every bar strain in the equilibrium tables.
- The required areas in the beam listing: 15.10 and 13.72 cm² for bending, 22.58 cm²/m for shear.

**CYPE conventions found while matching (C1-C3 carry the fibre-section match)**

| # | CYPE convention (implement a `cype_compat` switch) | Code-strict alternative | Effect |
|---|---|---|---|
| C1 | CYPE's failure plane stops at **99.5 % of the strain limits**: εcu2,eff = 0.0034825 and εsu,eff = 0.00995. The steel limit εsu = 10 ‰ is a CYPE choice: A19.3.2.7(2)b, with a horizontal top branch, needs no strain limit. Evidence: CYPE prints bar strains of -0.009950 (P381), and its printed pile bar strains extrapolate to εc = 0.003483 at the compressed corner (P257), not 0.0035. | εcu2 = 0.0035, no steel strain limit. | The 0.995 factor alone: +0.09 % (piles), +0.02 % (beam). **Dropping the 10 ‰ steel limit raises the beam MRd by 2.15 %** (-332.78 vs -325.78, U.54): the beam is steel-governed and its concrete reaches only 1.66 ‰. Piles are concrete-governed and unchanged. |
| C2 | **Gross concrete area**: bars do not displace concrete. | Net area. | Net area lowers NRd by about 0.9 %. |
| C3 | In the inner beam, the two web Ø10 at x = ±185 mm (bars 6 and 16) carry **zero stress**. They look like the ledge-stirrup erection bars. The Ø10 at ±335 mm do count. | All bars active. | MRd = -338.26 instead of -325.78 (+3.8 %). |
| C4 | The detailed check gives the utilisation **along the load ray**: η = NSd/NRd = MSd/MRd ("mismas excentricidades"). The summary listing (Apéndice §3.5.1, "Aprov.") gives the utilisation **at constant NEd**: Cimentación 90.7 % reproduced exactly (U.34). The two Forjado-1 points (Cabeza 92.5, Pie 91.9) both come out 0.2 points low (92.30 / 91.70, U.35 / U.53). Rounded listing forces do not explain this (92.31). Both are matched if the bars sit at ±127.0 mm instead of the ±127.5 mm printed in the detailed check. Cause unconfirmed. | Either definition. | For the piles the constant-N value is 1.0-1.3 points higher (worse). |
| C5 | Second order: ee + ei + e2 is added in **both** axes at once, each with the sign of its ee, followed by one biaxial section check. | A19.5.8.9(2): the imperfection is needed only in the worst direction, with separate checks allowed by (5.38). | CYPE is conservative. |
| C6 | The minimum eccentricity (A19.6.1(4)) is applied only when **both** e0,x and e0,y are below emin. | Apply emin in the direction considered. | Not triggered in our piles. |
| C7 | For 1/r0, d is taken to the **extreme tension bar row**: 327.5 / 329.5 mm. | A19.5.8.8.3(2) (5.35): for bars distributed along the sides, d = h/2 + is = 308.6 mm. | The code-strict e2 is **+6.9 %** (97.75 vs 91.56 mm; S.29). |
| C8 | λlim uses B = √(1+2ω) (EN form). The BOE text prints B = 1 + √(1+2ω), an erratum; CYPE labels its formula "Formulación UNE-EN 1992-1-1:2013". | Use the EN form. | - |
| C9 | φef = 1.75 is a CYPE input. C = 0.7 (rm unknown, sway frame). | A19.5.8.4: φef = φ(∞,t0)·M0Eqp/M0Ed. Because the bollard ψ2 = 0, M0Eqp is small, so the true φef would be much lower. | 1.75 is conservative. |
| C10 | Shear in the piles is only checked as VEd ≤ **VRd,c**, which CYPE labels "VRd,s". Asl = every bar except the compressed-face row (8Ø25); d is the centroid of those bars (263.75 mm). σcp comes from the least-compressed combination G + 1.5 TB. | Same. | - |
| C11 | For αcw, σcp = (NEd - A's·fyd)/Ac (EHE-08 44.2.3.1 heritage). A's is all 12 bars in direction X and 4 bars in direction Y. Only matters when σcp > 0. | A19.6.2.3(3) (BOE p. 98363): σcp is the mean concrete compression from NEd, "obtenida mediante el promedio de toda la sección de hormigón **teniendo en cuenta la armadura**". CYPE's formula is one (conservative) reading of that phrase. The αcw list starts "1 para estructuras sin pretensado". | None here (αcw = 1). |
| C12 | For the column VRd,max, z = 249.16 / 251.34 mm is an internal CYPE lever arm. It could **not** be reproduced; it is not 0.9d for any d we tried (section 4.3). Beams use z = 0.9d = 432. | z = 0.9d with d = 263.75 gives VRd,max = 949.5 kN (-4.7 %). | Utilisation is only 0.09. |
| C13 | Shear design uses θ = 45°, **fywd = 0.8·fywk = 400 MPa (no γs)** and ν1 = 0.6. | Spain allows **0.5 ≤ cot θ ≤ 2.0** (A19 (6.7)); the EN range is 1-2.5. | - |
| C14 | Beam As,min = W·fctm,fl/(z·fyd) with **z = 0.9d**. | The code gives z ≈ 0.8h. | 5.09 vs 4.99 cm². |
| C15 | Column As,min = **0.004·Ac** and As,max = **fcd·Ac/fyd**. Both come from the *Anejo Nacional AN/UNE-EN 1992-1-1*, not from the A19 text. The AN prints "As,min = 0,004·Ac/fyd", which is dimensionally inconsistent; CYPE reads it as 0.004·Ac. The AN maximum is 0.5·fcd·Ac/fyc,d per face with fyc,d ≤ 400, i.e. 133.3 cm² total; CYPE uses fyd = 434.78, giving 122.67. | A19.9.5.2(3): As,max = 0.04·Ac = 64 cm² (0.08·Ac at laps). A19 has no 0.004·Ac. | 58.91 ≤ 64 still passes (92 % of the limit). |
| C16 | Minimum clear spacing uses s2 = 1.25·dg (EHE). | A19.8.2(2): dg + 5 mm. | Identical for dg = 20. |
| C17 | The 350 mm longitudinal bar spacing (A19.9.2.3(4), a torsion clause) is applied to every beam. | Only for torsion. | - |
| C18 | The crack-width check is "N.P." (not applicable) when σct ≤ the concrete tensile strength. The engineer's hand check used fctm = 3.2 MPa. | A19.7.1(2): fct,eff = fctm, or fctm,fl if As,min uses the same value. | - |
| C19 | ψ factors come from **CTE DB SE Tabla 4.2, category A (residential) or B (administrative)**, both 0.7 / 0.5 / 0.3. The 0.3 is confirmed by CYPE's quasi-permanent deflection combination "...+0.3Sobrecarga de uso" (P583). The bollard pull was entered as "Viento": 0.6 / 0.5 / 0. | Port works fall under ROM 2.0-11 (section 6). | ψ2 for the quay load drives cracking. |
| C20 | "Área Nec." in the beam listing is **singly reinforced** (no compression or side bars), sized for the node moment (-273.71, not the zone value -266.03). | - | - |
| C21 | The CYPE crack check at P5-P6 is skipped (σct < fct), and the beam torsion checks are "N.P." (not applicable). | - | - |

**Serviceability flags for the orchestrator**

- The code crack-width limit for **XS3 is wmax = 0.1 mm** under the **quasi-permanent** combination (CE Art. 27, Tabla 27.2).
- With ψ2,Qa = 0.3 (CYPE) the inner beams stay uncracked, but with the port-code value ψ2 = 0.8 (ROM 2.0-11) they are not:
  - M_qp = 151.9 kN·m exceeds Mcr = 125.2 kN·m in the SAP model (VT2/VT6; VT4 = Pórtico 6 has 139.8, also cracked);
  - wk ≈ **0.18 mm** with 7Ø20, so the beams **fail** the check (K.12-K.17, P.03);
  - at ψ2 = 0.5 they stay uncracked.
  - The threshold is **ψ2 ≈ 0.58** (0.63 if fct,eff = fctm,fl is used, which A19.7.1(2) allows because As,min uses fctm,fl) (P.06).
  - Once the section cracks, even at M = Mcr, wk = 0.149 mm > 0.1 mm (K.18). With 7Ø20 the XS3 limit can therefore only be met by keeping the beams uncracked. Meeting it cracked needs more or smaller bars.
- Piles: they stay uncracked with ψ2,TB = 0 (3.58 < 4.07 MPa). With ψ2,TB = 0.5 they crack (11.0 MPa, P.05).

---------------------------------------------------------------------------------------------------

## 0.1 What the text dump lost, and how it was recovered

- All CYPE formulas are **WMF images** (MathType-type metafiles), so `a10_full.txt` holds only the numbers.
- Greek letters set with `w:sym` (Symbol font) are also missing: γc, ρl, σcp, αcw, ν1, θ, α, λ, φef, ω, ε, η.
- Recovery: `wmf/wmftext.py` reads the WMF text records (MOVETO, TA_UPDATECP, the dx arrays, and the Symbol-to-Unicode mapping), and `wmf/dumpform.py` rewrites the document with the formulas inline.
- Outputs:
  - `trasmallo_body_formulas.txt` (P217-P609);
  - `trasmallo_app_formulas.txt` (appendix);
  - `wmf/formulas_unique.txt`, a de-duplicated list of 85 formulas.
- The two PNG figures of the hand check at P569/P571 (`wmf/docx/word/media/image117.png` and `image118.png`) were read visually:
  - P569: the quasi-permanent moment diagram of Pórtico 6, peak 86.66 kN·m;
  - P571: the stresses and strains at M = 86 kN·m.
- The ULS section figure (image112) gives x = 68.52 mm, εmax = 1.66 ‰, εmin = -11.64 ‰ and σmax = 22.65 MPa.

Recovered CYPE formulas, verbatim apart from notation:

```
Asmin = 0.004·Ac                  Asmax = fcd/fyd·Ac             A's,min = 0.10·NEd/fyd
s1 = φmax ; s2 = 1,25·dg ; s3 = 20 mm        φmin ≥ 12 mm        h ≤ 4·b
s_cl,max: s1 = 15·φmin ; s2 = 300 mm ; s3 = min(G,h)   (sic, copies the BOE typo; G = b)
φt ≥ 1/4·φmax ≮ 6 mm
η1 = sqrt((VEd,x/VRd,max,Vx)² + (VEd,y/VRd,max,Vy)²) ≤ 1     η2 idem with VRd,s
VRd,max = αcw·bw·z·ν1·fcd·(cotθ+cotα)/(1+cot²θ)   σcp ≤ 0 → αcw = 1   σcp = (NEd − A's·fyd)/Ac
fck ≤ 60 MPa → ν1 = 0.6
VRd,c = [CRd,c·k·(100·ρl·fck)^1/3 + 0.15·σcp]·bw·d ; VRd,c = (vmin + 0.15·σcp)·bw·d
CRd,c = 0.18/γc ; k = 1+sqrt(200/d) ≤ 2.0 ; ρl = Asl/(bw·d) ≤ 0.02 ; σcp = NEd/Ac ≤ 0.2·fcd ; vmin = 0.035·k^3/2·fck^1/2
η = sqrt(NEd²+MEd,x²+MEd,y²)/sqrt(NRd²+MRd,x²+MRd,y²) ≤ 1  (η1 first order, η2 with NSd, MSd)
NEd = Nd ; MEd = Nd·ee ; ee,x = e0,x … ; emin = h/30 ≮ 20 mm ; e0 = Md/Nd
λ = l0/ic = l0/sqrt(I/Ac) ; λlim = 20·A·B·C/sqrt(n) ; A = 1/(1+0.2·φef) ; B = sqrt(1+2·ω) ; ω = As·fyd/(Ac·fcd) ; C = 0.7 ; n = NEd/(Ac·fcd)
NSd = Nd ; MSd = Nd·etot ; etot = ee + ei + e2 ; ei = θi·l0/2 ; θi = θ0·αh·αm ; αh = 2/sqrt(l), 2/3 ≤ αh ≤ 1
e2 = (1/r)·l0²/c ; 1/r = Kr·Kφ·1/r0 ; Kr = (nu−n)/(nu−nbal) ≤ 1 ; nu = 1+ω ; nbal = 0.4
Kφ = 1+β·φef ≥ 1 ; β = 0.35 + fck/200 − λ/150 ; 1/r0 = εyd/(0.45·d) ; εyd = fyd/Es
fcd = αcc·fck/γc ; fyd = fyk/γs
NRd = Cc + Cs − T ; MRd,x = Cc·ecc,y + Cs·ecs,y − T·eT,y ; MRd,y = Cc·ecc,x + Cs·ecs,x − T·eT,x
As,min = W/z·fct,m,fl/fyd (beams)
VRd,s = Asw/s·z·fywd·(cotθ+cotα)·sinα ; fywd = 0.8·fywk
s ≤ sl,max = 0.75·d·(1+cotα) ; st,trans ≤ st,max = 0,75·d ≤ 600 mm ; sb ≤ 350 mm
ρw = Asw/(s·bw·sinα) ; ρw,min = 0.08·sqrt(fck)/fyk ; fck ≤ 50 MPa → fctm = 0.30·fck^2/3
fT,max ≤ fT,lim
```

---------------------------------------------------------------------------------------------------

## 1. Materials (A19.2.4.2.4, A19.3.1, A19.3.2)

| Quantity | Formula / Spanish value | Clause | Our values | Validated |
|---|---|---|---|---|
| γc, γs | 1.5 / 1.15 (persistent/transient); 1.3 / 1.0 (accidental) | A19.2.4.2.4 Tabla A19.2.1 (BOE p. 98304) | | M.01-03 |
| fcd | **αcc·fck/γc, with αcc = 1.00** (0.85-1.0 allowed if permanent load exceeds 80 % of the total) | A19.3.1.6(1) (3.15), p. 98313 | HA-50: 33.33; HA-35: 23.33 | M.01, M.02 |
| fctd | αct·fctk,0.05/γc, with αct = 1.00 | A19.3.1.6(2) (3.16) | | - |
| fcm | fck + 8 | Tabla A19.3.1 (p. 98308) | | |
| fctm | 0.30·fck^(2/3) (fck ≤ 50); 2.12·ln(1 + fcm/10) (fck > 50) | Tabla A19.3.1 | HA-35: 3.21; HA-50: 4.07 | M.05 |
| fctk,0.05 / fctk,0.95 | 0.7·fctm / 1.3·fctm | Tabla A19.3.1 | | |
| fctm,fl | **max{(1.6 - h/1000)·fctm; fctm}**, h in mm (also applies to the characteristic values) | A19.3.1.8 (3.23), p. 98315 | h = 550: 3.37 | M.06 |
| Ecm | 22·(fcm/10)^0.3 GPa for quartzite aggregate; **×0.9 limestone ("caliza")**, ×0.7 sandstone, ×1.2 basalt | Tabla A19.3.1 + A19.3.1.3(2) | 30669 / 33550 / 28328 MPa (CYPE lists limestone) | M.07-09 |
| εc2, εcu2, n (fck ≤ 50) | 2.0 ‰, 3.5 ‰, n = 2 | Tabla A19.3.1 | | M.10-11 |
| εc2 (fck > 50) | 2.0 + **0.085**(fck-50)^0.53 ‰. The BOE prints 0,85, a typo; the tabulated values need 0.085. | Tabla A19.3.1 | | |
| εcu2, n (fck > 50) | 2.6 + 35[(90-fck)/100]^4 ‰; n = 1.4 + 23.4[(90-fck)/100]^4 | Tabla A19.3.1 | | |
| Parabola-rectangle | σc = fcd[1 - (1 - εc/εc2)^n] for 0 ≤ εc ≤ εc2; σc = fcd for εc2 ≤ εc ≤ εcu2 (compression positive) | A19.3.1.7(1) (3.17)(3.18) | used by CYPE | U.42, U.49 |
| Rectangular block | λ = 0.8, η = 1.0 (fck ≤ 50); λ = 0.8 - (fck-50)/400, η = 1 - (fck-50)/200 (50 < fck ≤ 90); reduce η·fcd by 10 % if the compressed width shrinks towards the extreme fibre | A19.3.1.7(3) (3.19)-(3.22) | not used by CYPE | - |
| Steel B500SD | fyd = fyk/γs = 434.78; Es = 200 000 MPa; εyd = 0.00217 | A19.3.2.7(4) | | M.03-04, M.13 |
| Steel diagram | (a) inclined top branch to k·fyk/γs at εud = 0.9·εuk; or **(b) horizontal top branch with no strain limit**. CYPE uses **(b) plus εsu = 10 ‰** (C1), e.g. -434.78 MPa at ε = -0.00995. | A19.3.2.7(2) (p. 98319) | | M.12, U.40 |

---------------------------------------------------------------------------------------------------

## 2. ULS bending with axial force (A19.6.1): fibre-section algorithm

### 2.1 Assumptions (A19.6.1(2)-(6), BOE p. 98357-98358)

- Plane sections; perfect bond; no concrete tension; the stress-strain laws of section 1.
- Strain limits:
  - concrete εcu2 at the most compressed fibre;
  - for sections loaded close to centric compression (ed/h < 0.1), a mean strain limit of εc2, which in the domain construction becomes the pivot point C at (1 - εc2/εcu2)·h;
  - steel: εud when the inclined branch is used; CYPE applies 10 ‰ (C1).
- Minimum eccentricity for compression: **e0 = max(h/30, 20 mm)** (A19.6.1(4)).
- Allowable strain diagrams: A19 Figura 6.1 (pivots A, B and C).

### 2.2 Implementation (as in `RCSection`, validate_codigo.py)

- **Section**: a union of rectangles (x0, x1, y0, y1) plus bars (x, y, area, active), with coordinates about the gross centroid. Integrate the concrete on a 1-2 mm grid; the error is below 0.01 %. Bars are points and do **not** displace concrete (C2).
- **Sign convention (CYPE)**: compression positive. N = Σσ dA, Mx = Σσ·y dA, My = Σσ·x dA.
- **Strain plane**: ε(x, y) = ε0 + kx·x + ky·y.
- **Ultimate planes** are parameterised by the neutral-axis direction α, with (cos α, sin α) pointing to the compressed side, and by t ∈ [0, 3]. Let s = x·cosα + y·sinα, s_top = max over the concrete vertices, h = s_top - s_bot, and s_bar = the smallest s of the active bars.

  | t range | Pivot | Strain plane |
  |---|---|---|
  | 0-1 | A | ε(s_bar) = -εsu; ε(s_top) goes linearly from -εsu to +εcu2 |
  | 1-2 | B | ε(s_top) = εcu2; the neutral-axis depth x goes from x_AB = εcu2/(εcu2 + εsu)·(s_top - s_bar) to h |
  | 2-3 | C | ε = εc2 at s_C = s_top - (1 - εc2/εcu2)·h; ε(s_top) goes from εcu2 to εc2 (uniform compression) |

  With `strain_factor = 0.995` this reproduces CYPE (C1).
- **Capacity with the same eccentricities** (CYPE's N,M check), `capacity_ray(S)`:
  - Scale moments by L = max section dimension, so r = (N, Mx/L, My/L).
  - Find (α, t) such that r(α, t)/|r| = ŝ: coarse grid search (3° × 0.025, 10 mm mesh), then a `least_squares` refinement on the fine mesh.
  - Output NRd, MRd,x, MRd,y, Cc, Cs, T, their eccentricities, εc,max (at the vertices), bar strains and stresses.
  - Utilisation η = |S|/|R|, which equals NEd/NRd when NEd ≠ 0 (CYPE: "η = sqrt(NEd² + MEd,x² + MEd,y²)/sqrt(NRd² + ...)").
- **Utilisation at constant N** (C4, CYPE summary listing), `capacity_constant_N(S)`: solve for R with R_N = NEd and the same Mx:My ratio; η = |MEd|/|MRd|.
- **Design-load equilibrium** (CYPE "Equilibrio ... esfuerzos solicitantes"), `equilibrium(S)`: least-squares solve of (ε0, kx, ky) for R = S with multiple starting points; the resulting cost is about 1e-30.
- **Required tension steel** (CYPE "Área Nec."), `required_tension_steel`: singly reinforced, N = 0; brentq on As so that MRd = |MEd| (C20).
- **Validation** (U.01-U.52; every PASS is 0.00-0.04 % except where a value is rounded):

  | Case | CYPE | Computed |
  |---|---|---|
  | Pile head, 2nd order | NRd/MRd,x/MRd,y = 679.16/387.20/-75.52; Cc/Cs/T = 1422.97/536.86/1280.67; bar-7 ε = -0.004001 | 679.15/387.20/-75.52; 1422.96/536.85/1280.66; -0.004001 |
  | Pile head, 1st order | 925.83/430.56/-5.68 | 925.82/430.56/-5.69 |
  | Fixity section, 1st order | 1021.59/-441.89/4.34 | 1021.58/-441.89/4.35 |
  | Fixity section, 2nd order | 733.05/-393.69/79.72 | 733.04/-393.69/79.72 |
  | Beam, hogging | MRd = -325.78; Cc = 767.00; ecc,y = -219.16; eT,y = 205.59; x = 68.52; σc,max = 22.65 | same (MRd = -325.78) |
  | Beam at MEd = -273.71 | Cc/Cs/T = 543.32/93.94/637.26; σs = -392.45 | 543.33/93.94/637.27; σs = -392.46 |
  | Beam Área Inf./Sup. Nec. | 15.10 / 13.72 cm² | 15.10 / 13.72 cm² |
- **Biaxial**: CYPE always integrates the full biaxial section (no (5.39) interaction). Implement the same. The A19.5.8.9(4) simplified check (MEdz/MRdz)^a + (MEdy/MRdy)^a ≤ 1 can be added as a cross-check: a = 1 / 1.5 / 2 for NEd/NRd = 0.1 / 0.7 / 1.0, with NRd = Ac·fcd + As·fyd.

---------------------------------------------------------------------------------------------------

## 3. Piles as columns (A19.5.2, A19.5.8, A19.6.1(4), A19.9.5, A19.8.2)

### 3.1 Effective length and slenderness (A19.5.8.3.2)

- λ = l0/i with i = sqrt(Ic/Ac), using the gross concrete section.
- CYPE input: **l0 = 6.70 m**. That is β = 1.0 on the flexible length 7.25 - 0.55 = 6.70 m, consistent with (5.16) for a sway member fixed at both ends (k1 = k2 → 0).
- i = 115.5 mm and λ = 58.02 (S.01-S.02).

### 3.2 Slenderness limit (A19.5.8.3.1, (5.13), BOE p. 98340)

- λlim = 20·A·B·C/√n, with:
  - A = 1/(1 + 0.2·φef), or 0.7 if φef is unknown;
  - **B = √(1 + 2ω)**, or 1.1 if unknown (C8, BOE erratum);
  - C = 1.7 - rm, with 0.7 for unbraced members, for braced members whose first-order moments come from imperfections or transverse loads, or when rm is unknown;
  - ω = As·fyd/(Ac·fcd);
  - n = NEd/(Ac·fcd).
- Our values: φef = 1.75 (C9), so A = 0.7407; ω = 0.4802, so B = 1.4001; C = 0.7.
  - The λlim block prints φef as "1.8" (one decimal); the Kφ block prints "1.750" (P459). λlim = 42.58 and Kφ = 1.373 both require 1.75; 1.8 would give λlim = 42.27.
  - NEd = 620.06 gives n = 0.1163 and **λlim = 42.58**;
  - NEd = 655.55 gives n = 0.1229 and **λlim = 41.42** (S.03-S.09).
- λ > λlim, so second-order effects must be included.
- Biaxial bending (A19.5.8.3.1(2)) may be checked separately in each direction.
- The Spanish *Anejo Nacional AN/UNE-EN* has a different, EHE-type λlim = 35·sqrt(C/ν·[1 + 0.24/(e2/h) + 3.4(e1/e2 - 1)²]) ≯ 100. It does **not** apply under the CE, and CYPE did not use it.

### 3.3 Geometric imperfections (A19.5.2, p. 98329-98330)

- θi = θ0·αh·αm, with:
  - θ0 = 1/200;
  - αh = 2/√l, limited to 2/3 ≤ αh ≤ 1 (l in m: the real length of an isolated member);
  - αm = sqrt(0.5·(1 + 1/m)), with m = 1 for an isolated member.
- ei = θi·l0/2 (5.2). An alternative for braced walls and columns is l0/400.
- Our values (l = 6.70 m): αh = 0.7727, θi = 0.003863, **ei = 12.94 mm** (S.10-S.12).
- Imperfections are for ULS only (A19.5.2(2)-(3)).
- A19.5.8.9(2): for biaxial checks they are needed only in the worst direction. CYPE adds them in both (C5).

### 3.4 First-order eccentricity and minimum eccentricity

- e0 = MEd/NEd, with emin = max(h/30, 20 mm) = 20 mm (A19.6.1(4); S.13-S.14).
- CYPE: "ee" = e0 unless both e0,x and e0,y are below emin (C6).

### 3.5 Nominal-curvature method (A19.5.8.8, p. 98347-98348)

| Quantity | Formula | Validation (head / fixity) |
|---|---|---|
| Design moment | MEd = M0Ed + M2, with M2 = NEd·e2. For members without end loads M0e = 0.6·M02 + 0.4·M01 ≥ 0.4·M02 (5.32); CYPE uses the moment at the checked section. | |
| e2 | e2 = (1/r)·l0²/c, with **c = π² = 9.870** (constant section, sinusoidal curvature). Use c = 8 if the first-order moment is constant. | 92.12 / 91.56 mm (S.17, S.20) |
| Curvature | 1/r = Kr·Kφ·1/r0 (5.34) | 0.0203 / 0.0201 m⁻¹ |
| 1/r0 | εyd/(0.45·d), εyd = fyd/Es | 0.0148 / 0.0147 m⁻¹ |
| d | Code: for bars distributed along the sides, d = h/2 + is (5.35), where is is the radius of gyration of the total steel. **CYPE: d to the extreme tension row**, 327.5 / 329.5 mm (C7). | S.29: code d = 308.6 gives e2 = 97.75 mm (+6.9 %) |
| Kr | (nu - n)/(nu - nbal) ≤ 1, with nu = 1 + ω and nbal = 0.4 (5.36) | raw 1.26, so 1.000 |
| Kφ | 1 + β·φef ≥ 1, with β = 0.35 + fck/200 - λ/150 (5.37) | β = 0.213, Kφ = 1.373 |
| Total eccentricity (CYPE) | etot = ee + ei + e2 per axis, all with the sign of ee (C5). MSd = NSd·etot. | fixity: etot,x = -432.56 - 12.94 - 91.56 = -537.06 → MSd,x = -352.07; etot,y = 4.25 + 12.94 + 91.56 = 108.75 → MSd,y = 71.29 (S.26-S.28) |

- φef (A19.5.8.4) = φ(∞, t0)·M0Eqp/M0Ed. Take φ(∞, t0) from Figura A19.3.1 or Apéndice B.
- CYPE used 1.75. For the bollard-pull combinations M0Eqp ≈ 0 because ψ2 = 0, so a strict φef would be close to 0. Keep 1.75 to match CYPE and flag it as conservative.

### 3.6 Column detailing

| Rule | Code (A19) | CYPE / AN value | Our case | Validation |
|---|---|---|---|---|
| Definition of a column | h ≤ 4b (A19.9.5.1) | | 400 ≤ 1600 | - |
| Min. bar diameter | **Ømin = 12 mm** (A19.9.5.2(1)) | | Ø25 | D.04 |
| Min. longitudinal steel | A19.9.5.2(2): **A's1,min = A's2,min = 0.05·NEd/fyc,d per face**, with fyc,d = fyd ≯ 400 N/mm². Symmetric pure compression: **As,min = 0.10·NEd/fyd** (9.12). | CYPE adds **As,min = 0.004·Ac** (AN/UNE-EN 1992-1-1 9.5.2(2)) | 0.10·673.90/434.78 = **1.55 cm²**; 0.004·1600 = **6.40 cm²**; per face 0.84 cm² | D.07-D.09 |
| Max. longitudinal steel | A19.9.5.2(3): **As,max = 0.04·Ac** (0.08·Ac at laps) = 64.0 cm² | CYPE: **fcd·Ac/fyd = 122.67 cm²** (AN: 0.5·fcd·Ac/fyc,d per face) | 58.91 passes both | D.10-D.11 |
| Tie diameter | Øt ≥ max(6 mm, Ømax/4) (A19.9.5.3(1)) | CYPE prints 6.3 | 6.25 → Ø10 OK | D.06 |
| Tie spacing | **scl,max = min(15·Ømin, 300 mm, min(b, h))** (A19.9.5.3(3); the BOE prints "min(G,h)", where G = b). EN recommends 20Ø / b / 400. | AN: 15Ø ≤ 300 | terms 375 / 300 / 400 → **300 mm**. CYPE's printed s1 = 300, s2 = 375 swap the labels of the 15Ø and 300 mm terms; the formula images show s1 = 15·φmin, s2 = 300 mm, s3 = min(b,h). | D.05 |
| Tie spacing reduction and corner restraint | ×**0.6** over a length equal to the larger column dimension above and below a beam or slab, and at laps when Ømax > 14 mm (with at least 3 ties along the lap) (A19.9.5.3(4), BOE p. 98435). Every corner bar must be tied, and no compressed bar may be more than **150 mm** from a restrained bar (9.5.3(6)). | | pile head and base zones: 0.6·300 = 180 ≥ 150 OK | - |
| Clear bar spacing | A19.8.2(2): **max(k1·Ø, dg + k2, 20 mm), k1 = 1, k2 = 5 mm** | CYPE prints s2 = 1.25·dg (EHE) (C16) | 25 mm ≤ 60 mm (piles) and ≤ 63 mm (beam) | D.01-D.03 |

---------------------------------------------------------------------------------------------------

## 4. Beams

### 4.1 Longitudinal reinforcement limits (A19.9.2.1.1, BOE p. 98424)

- **As,min = (W/z)·(fctm,fl/fyd)** (9.1), Spanish formula (from EHE-08 Art. 42.3.2). The same formula is in AN/UNE-EN.
  - W is the gross section modulus about the most tensioned fibre;
  - z is the ULS lever arm, **≈ 0.8h per the code; CYPE uses 0.9d** (C14).
  - Alternatively, for secondary elements: As,min = 1.2 × As required by ULS.
- **As,max = 0.04·Ac** outside laps (9.2.1.1(3)).
- Compression bars counted in the resistance must be tied with a transverse spacing ≤ 15Ø (9.2.1.2(3)).
- Partial end fixity: at supports, design for ≥ β1·Mspan with β1 = 0.15 (9.2.1.2(1)).
- Longitudinal bar spacing ≤ **350 mm**. This is 9.2.3(4), a torsion clause; CYPE applies it generally (C17). Slabs: smax,slabs < 300 mm and < 3h (9.3.1.1(3)).
- Inner beam: W,top = 28 339.35 cm³, fctm,fl = 3.37 MPa, z = 432 → **As,min = 5.09 cm²**. With z = 0.8h = 440 it is 4.99 cm². As,max = 146 cm² (D.12-D.16).

### 4.2 Shear: members without shear reinforcement (A19.6.2.2, p. 98359-98360)

- VRd,c = [CRd,c·k·(100·ρl·fck)^(1/3) + k1·σcp]·bw·d ≥ (vmin + k1·σcp)·bw·d (6.2.a/b), with:
  - CRd,c = **0.18/γc**; k1 = **0.15**; vmin = **0.035·k^1.5·fck^0.5** (6.3);
  - k = 1 + √(200/d) ≤ 2 (d in mm);
  - ρl = Asl/(bw·d) ≤ 0.02 (Asl anchored ≥ lbd + d beyond the section);
  - σcp = NEd/Ac < 0.2·fcd (compression positive).
- The Spanish AN/UNE-EN uses vmin = 0.075/γc·k^1.5·fck^0.5. That does **not** apply under the CE; CYPE uses 0.035.
- Pile at the head, comb. G + 1.5·TB: NEd = 332.81 kN, bw = 400, d = 263.75, Asl = 8Ø25 = 39.27 cm² (C10).
  - k = 1.871, ρl = 0.02 (capped), σcp = 2.08 MPa, vmin = 0.633 MPa;
  - **VRd,c = 142.85 kN**, with a minimum of 99.73 kN;
  - η2 = sqrt(0.34² + 78.86²)/142.85 = 0.552 (V.10-V.18).
- Other rules:
  - VEd ≤ VRd,c: no calculated shear reinforcement, but the minimum per 9.2.2 is still required (6.2.1(3)-(4));
  - VEd ≤ 0.5·bw·d·ν·fcd with ν = 0.6(1 - fck/250) (6.2.2(6));
  - for uniform loads, check at d from the support face (6.2.1(8)).

### 4.3 Shear: members with shear reinforcement (A19.6.2.3, p. 98362-98364)

- **Strut angle: 0.5 ≤ cot θ ≤ 2.0** (6.7). This is a Spanish choice; EN recommends 1 ≤ cot θ ≤ 2.5. CYPE used θ = 45°.
- VRd,s = (Asw/s)·z·fywd·cot θ (6.8); for inclined links, VRd,s = (Asw/s)·z·fywd·(cot θ + cot α)·sin α (6.13).
- VRd,max = αcw·bw·z·ν1·fcd/(cot θ + tan θ) (6.9); for inclined links, ... × (cot θ + cot α)/(1 + cot²θ) (6.14).
- ν1 = 0.6·(1 - fck/250). **If the design stress of the shear reinforcement is < 0.8·fyk, then ν1 = 0.6 (fck ≤ 60), or 0.9 - fck/200 > 0.5 (fck > 60) (6.10a/b), AND "if (6.10) is used, fywd shall be reduced to 0.8·fywk in (6.8)"** (NOTA, p. 98363).
  - CYPE: fywd = 0.8·500 = **400 MPa** and ν1 = 0.600 (C13).
- αcw = 1 for non-prestressed members. Otherwise: 1 + σcp/fcd (0 < σcp ≤ 0.25 fcd), 1.25 (up to 0.5 fcd), 2.5(1 - σcp/fcd) (up to 1.0 fcd).
  - CYPE evaluates σcp = (NEd - A's·fyd)/Ac and sets αcw = 1 when σcp ≤ 0 (C11). Values: -12.13 / -1.46 / -11.91 / -2.62 MPa (V.02-V.05, V.20).
- z = 0.9d for members without axial force (6.2.3(1)). Beam: **z = 432 mm**.
  - Column VRd,max: CYPE prints z = 249.16 (head) and 251.34 (fixity). With these, 996.63 and 1005.35 kN are reproduced exactly (V.06-V.07). z itself was not reproduced (C12). Candidates tested (`research` notes):
    - 0.9 × tension-bar centroid depth: 237.4 / 238.3;
    - 0.9·(h/2 + is): 276.3 / 277.8;
    - C-T lever arms from the ULS state (225.6-234.3) and from the **first-order** design state (NEd, MEd without ei/e2: 250.1 / 252.7, within 0.4-0.6 %). The second-order design state, whose resultants CYPE prints at P264-P269, gives only 242.8 / 245.8;
    - elastic cracked lever arm: 253.
  - The closest is the C-T lever arm of the first-order design-load biaxial equilibrium (+0.36 % / +0.56 %). This is still not an exact match. Recommended default: z = 0.9·d with d = 263.75 (949.5 kN, conservative), or the first-order design-state C-T lever arm.
- Beam P3-P4: bw = 500, d = 480, z = 432, Asw = 3 legs Ø10 = 2.356 cm², s = 100.
  - **VRd,max = 1512.00 kN**, **VRd,s = 407.15 kN**, VEd = 390.18 kN at x = 0.488 m from the pile face (≈ d), η = 0.258 / 0.958;
  - required Asw/s = VEd/(z·fywd·cot θ) = **22.58 cm²/m** (V.19-V.27).
- Additional tension in the longitudinal steel: ΔFtd = 0.5·VEd·(cot θ - cot α) (6.18), or the shift rule al = z(cot θ - cot α)/2 (9.2.1.3(2)).

### 4.4 Shear reinforcement detailing (A19.9.2.2, p. 98427-98428)

- Links at 45°-90° to the axis.
- β3 = **0.5**: at least half of the required shear reinforcement as links (9.2.2(4)). The AN says 0.33.
- ρw = Asw/(s·bw·sin α) ≥ **ρw,min = 0.08·√fck/fyk** (9.4)(9.5).
  - HA-35: 0.000947. That gives minimum links of 4.73 cm²/m for bw = 500 and 2.37 cm²/m for bw = 250, matching the CYPE listing "Nec." (V.28-V.31).
- sl,max = 0.75·d·(1 + cot α) = 360 mm (9.6); bent-up bars: sb,max = 0.6·d·(1 + cot α) (9.7).
- st,max = 0.75·d ≤ 600 mm = 360 mm between legs (9.8) (V.32-V.33).

### 4.5 Torsion, basics only (A19.6.3, p. 98369-98370)

CYPE reports "no torque" for P3-P4. The listing torques are ≤ 3.2 kN·m in the inner frames and up to 27.6 kN·m at the ends of the end frames 3 and 9, 80x55+15x30. Implement the following for the end frames:

- Thin-walled equivalent section: tef,i = A/u (≥ 2 × the distance from the face to the longitudinal bar axis); Ak is the area inside the wall centre line; uk is its perimeter.
- τt,i·tef,i = TEd/(2·Ak) (6.26); VEd,i = τt,i·tef,i·zi (6.27).
- Longitudinal steel: ΣAsl·fyd/uk = TEd·cot θ/(2·Ak) (6.28).
- Links: Asw·fywd/s = TEd/(2·Ak·cot θ) (EN form).
- Strut crushing: TEd/TRd,max + VEd/VRd,max ≤ 1 (6.29), with TRd,max = 2·ν·αcw·fcd·Ak·tef,i·sin θ·cos θ (6.30), ν = 0.6(1 - fck/250).
- Only minimum reinforcement is needed if TEd/TRd,c + VEd/VRd,c ≤ 1 (6.31); TRd,c is found from τt,i = fctd.
- Detailing: torsion links are closed; their spacing is ≤ uk/8, ≤ sl,max and ≤ the least section dimension (9.2.3(3)). Longitudinal bars are needed in each corner at ≤ 350 mm (9.2.3(4)).

---------------------------------------------------------------------------------------------------

## 5. Serviceability: stresses, cracking and deflection (A19.7, CE Art. 27)

### 5.1 Stress limits (A19.7.2, p. 98392)

- Characteristic combination:
  - concrete in XD/XF/XS classes: σc ≤ k1·fck with **k1 = 0.6**; this applies to our **XS3**;
  - steel: σs ≤ **k3·fyk = 0.8·fyk** (imposed deformations: k4 = 1.0; prestress: k5 = 0.75).
- Quasi-permanent combination: if σc ≤ **k2·fck = 0.45·fck**, creep is linear; otherwise use non-linear creep (3.1.4).

### 5.2 Crack-width limits: **CE Artículo 27, Tabla 27.2** (p. 98393; A19.7.3.1(5) refers to it)

| Exposure | RC, quasi-permanent comb. | Prestressed, frequent comb. |
|---|---|---|
| X0, XC1 | 0.4 mm | 0.2 |
| XC2, XC3, XF1, XF3, XC4 | 0.3 mm | 0.2 |
| XS1, XS2, XD1-3, XF2, XF4, XA1 | 0.2 mm | decompression |
| **XS3**, XA2, XA3 | **0.1 mm** | decompression |

Also: XD3 needs "special measures" (7.3.1(7)). The AN/UNE-EN Tabla AN/9 gives the same values.

### 5.3 Is the section cracked? (A19.7.1(2))

- Stresses and deformations are computed on the uncracked section as long as the flexural tensile stress ≤ **fct,eff**.
- fct,eff = **fctm**, or fctm,fl provided the minimum steel uses the same value. Crack widths and tension stiffening always use fctm.
- CYPE: if σct,max ≤ fct, the wk check is "N.P." (C18). The engineer's P570-P575 check compares against 3.2 MPa (= fctm).
- Implementation: quasi-permanent combination; homogenised uncracked section with n = Es/Ecm (HA-35 limestone: n = 6.52); compare σct,max with fctm.
- Validation: M = +86 kN·m (Pórtico 6) gives σct,bottom = **-2.20 MPa** (K.01, -0.2 %) and σs,bottom = -10.27 (K.03).
  - The top fibre in the figure, 2.73, is 1.3 % off (INFO K.02).
  - The figure's printed strains (0.000082 / -0.000065 at the fibres, 0.000069 / -0.000051 at the bars) imply Ec ≈ 33.5 GPa and bars about 50 mm from the faces. This model uses Ecm = 30.7 GPa (HA-35 limestone) with bars at 70 mm, so its strains are about 10 % higher (0.000090 / -0.000072).
  - A grid search over cover (40-75 mm) and Ec (29-36 GPa) finds no single linear homogenised section that reproduces all eight printed values within rounding.
  - The fibre stress is dominated by the gross section: -2.16 to -2.23 MPa across those variants. The K.01 match therefore confirms the method (uncracked, compared with fctm) rather than the engineer's exact inputs.
- Homogenised cracking moments of the inner beam (fctm = 3.21): **Mcr,sag = 125.2 kN·m**, **Mcr,hog = 99.8 kN·m** (K.05-K.06).

### 5.4 Minimum steel for crack control (A19.7.3.2, p. 98394-98395)

- As,min·σs = kc·k·fct,eff·Act (7.1), with:
  - σs ≤ fyk, or lower to satisfy the wk tables;
  - fct,eff = fctm (or fctm(t) before 28 days);
  - k = 1.0 for webs with h ≤ 300 mm or flanges narrower than 300 mm, k = 0.65 for h ≥ 800 mm or flanges wider than 800 mm, interpolated between;
  - kc = 1 in pure tension; kc = 0.4·[1 - σc/(k1·(h/h*)·fct,eff)] ≤ 1 for rectangles and webs (7.2); kc = 0.9·Fcr/(Act·fct,eff) ≥ 0.5 for flanges (7.3);
  - σc = NEd/(b·h); h* = min(h, 1.0 m); k1 = 1.5 when N is compression, 2h*/(3h) when N is tension.
- T-sections are treated part by part (web, flanges).
- CYPE's "Área mínima de armadura" is a "Criterio de CYPE" based on 7.3.2 and was N.P. here.
- Skin reinforcement for h ≥ 1000 mm (7.3.3(3)) does not apply (h = 550).

### 5.5 Crack width (A19.7.3.4, p. 98398-98400); constants as in EN, confirmed in the BOE and in the AN

```
wk = sr,max·(εsm − εcm)                                                    (7.8)
εsm − εcm = [σs − kt·fct,eff/ρp,eff·(1 + αe·ρp,eff)]/Es ≥ 0.6·σs/Es        (7.9)
  kt = 0.6 short-term, 0.4 long-term (use 0.4 for quasi-permanent);  αe = Es/Ecm
  ρp,eff = (As + ξ1²·A'p)/Ac,eff (7.10);  Ac,eff = b × hc,ef,  hc,ef = min{2.5(h−d), (h−x)/3, h/2}  (7.3.2(3), Fig. A19.7.1)
sr,max = k3·c + k1·k2·k4·φ/ρp,eff   if bar spacing ≤ 5(c + φ/2)          (7.11)
  k1 = 0.8 (ribbed), k2 = 0.5 bending / 1.0 tension / (ε1+ε2)/(2ε1) (7.13),  **k3 = 3.4, k4 = 0.425**,
  c = cover to the longitudinal bar (here 50 + Ø10 link = 60 mm);  φeq = Σnφ²/Σnφ (7.12)
sr,max = 1.3·(h − x)                if spacing > 5(c + φ/2), or no bonded steel in the tension zone   (7.14)
```

- σs comes from the fully cracked linear-elastic section (n = Es/Ecm, no concrete tension) under the quasi-permanent combination.
- Demonstration with no CYPE target (K.12-K.17): inner beam, sagging, M_qp = 151.9 kN·m, which is the SAP value for ψ2,Qa = 0.8.
  - x = 132.0 mm, σs = 159.6 MPa, hc,ef = 139.3 mm, ρp,eff = 0.0197, sr,max = 376 mm, εsm - εcm = 0.479 ‰ (the 0.6·σs/Es floor governs);
  - **wk = 0.18 mm > 0.10 mm**.
  - At first cracking (M = Mcr = 125.2 kN·m) wk is already 0.149 mm (K.18), because the 0.6·σs/Es floor of (7.9) governs. Checked by hand: x = 132 mm; Icr ≈ 2.16e9 mm⁴.
  - The script counts the compression bars as n·As' (no displaced concrete). Using (n-1)·As' gives x = 133 mm, a negligible difference.
- Shear cracking (CYPE "Vfis") is deemed controlled by the 9.2.2, 9.2.3, 9.3.2 and 9.4.3 detailing (7.3.3(5)).

### 5.6 Deflection (A19.7.4.1(4)-(5), p. 98400-98401)

- Total deflection under the quasi-permanent combination ≤ span/250. Deflection after construction (CYPE's "activa") ≤ span/500.
- CYPE: fT,lim = L/250 = 12.20 mm and fA,lim = L/500 = 6.10 mm for L = 3.05 m (K.08-K.09). CYPE fT,max = 1.53 mm: stepwise history with creep, 28 → 90 → 120 → 360 days → ∞ (P584-P588).
- Implementation: A19.7.4.3 (7.18) interpolation α = ζ·αII + (1 - ζ)·αI, with ζ = 1 - β·(σsr/σs)², β = 1.0 short-term or 0.5 sustained; creep through Ec,eff = Ecm/(1 + φ).

---------------------------------------------------------------------------------------------------

## 6. Combinations and ψ factors

### 6.1 Combination formats (Código Estructural Anejo 18)

- ULS persistent/transient: **eq. 6.10**, Σγ_G·G + γ_Q,1·Q1 + Σγ_Q,i·ψ0,i·Qi. A18 Apéndice A.1 (buildings) and A.2 (bridges) both prescribe 6.10 (BOE p. 98256).
- SLS: characteristic ΣG + Q1 + Σψ0,i·Qi; frequent ΣG + ψ1,1·Q1 + Σψ2,i·Qi; **quasi-permanent ΣG + Σψ2,i·Qi**, used for cracking in RC, long-term deflection and φef.
- A18 Apéndice A.1 (buildings) says "Se adoptará lo establecido en el Código Técnico de la Edificación". A.2 (bridges) points to the "Reglamentación específica vigente" (BOE p. 98256).
- A18 has **no appendix for port works**. The sector references are the Puertos del Estado ROM documents (ROM 0.2-90, ROM 2.0-11). Their use for ψ is a project decision: they are recommendations, not regulations cited by the CE.
- CYPE used (appendix §1.6, P1509), validated in C.01-C.07:
  - γG = 1.35/1.00 and γQ = 1.50/0 (Código Estructural);
  - foundations 1.60 (CTE DB SE-C; the SAP "CIM" combinations);
  - ψ0 = **0.7** for Qa (hence 1.05 = 1.5·0.7) and ψ0 = **0.6** for the bollard pull ("Viento"; 0.9 = 1.5·0.6).
- Its quasi-permanent combination is PP + CM + **0.3**·Qa, with ψ2 = 0 for the bollard.
- Note: the SAP "ELS01-08" combinations are **characteristic**, all ψ = 1 (CYPE's "Desplazamientos"). The quasi-permanent combination needed for cracking and deflection must be created separately.

### 6.2 ψ values by source

| Action | CTE DB SE Tabla 4.2 (used by CYPE) | EN 1990 Tabla A1.1 | ROM 0.2-90 Parte 3 §3.2.3.2 | **ROM 2.0-11** (berthing and mooring works, 2012) |
|---|---|---|---|---|
| (a) Uniform quay load: storage, operations, parking (qv,1) | Cat. A residential: 0.7 / 0.5 / **0.3** (C, D, E: 0.7 / 0.7 / 0.6) | Cat. E storage: 1.0 / 0.9 / **0.8** | QV "uso o explotación": 0.70 / 0.60 / **0.50** | Tabla 4.6.4.1, no statistical data: combination value = nominal (**ψ0 = 1.0**), frequent **0.95**, quasi-permanent **0.80** × nominal. With statistics: 95 % / 85 % / 50 % quantiles. The table is headed "para ... estados límite últimos", and its 0.95 / 0.80 values sit in the "excepcionales" column. The paragraph just before it (p. 125) says that SLS checks with the frequent or quasi-permanent combination use "los valores frecuentes o cuasi-permanentes definidos en dicha tabla para condiciones excepcionales". That is what makes ψ2 = 0.80 applicable to the crack check. |
| (b) Wind | 0.6 / 0.5 / **0** | 0.6 / 0.2 / **0** | QM environmental: 0.70 / 0.30 / **0.00** | Tabla 4.6.2.2 climatic agents: quasi-permanent = 50 % non-exceedance in the mean regime (≈ 0 load for design). Also A18 4.1.3(1)c NOTE: "for wind ... [ψ2] normally zero". |
| (c) Bollard pull (mooring, qv,5) | treated as wind by CYPE: 0.6 / 0.5 / 0 | - | a QV operational load: 0.70 / 0.60 / 0.50 | 4.6.4.4.7 / Tabla 4.6.4.58: characteristic and combination value = 95 % quantile at the operational limit (vessel at berth); frequent and quasi-permanent = **85 % / 50 % quantiles** of the mean marginal distribution. No fixed ψ. Minimum characteristic bollard loads: Tabla 4.6.4.66, e.g. 100 kN for Δ ≤ 1000 t. |

### 6.3 Recommendation

- **Qa, the 15 kN/m² uniform load on the fishing quay**: use **ψ2 = 0.8** (with ψ1 = 0.95 and ψ0 = 1.0) per ROM 2.0-11 Tabla 4.6.4.1, the current port recommendation for storage and parking loads without statistical data. It agrees with EN 1990 category E (storage).
  - CYPE's 0.3 is the building "residential" value and is not appropriate.
  - Keep 0.3 and 0.5 as sensitivity cases to show the effect.
  - Consequence (SAP results, P.01-P.03):
    - inner-beam quasi-permanent sagging moment = 90.4 / 115.0 / 151.9 kN·m for ψ2 = 0.3 / 0.5 / 0.8;
    - σct = 2.32 / 2.95 / 3.89 MPa against fctm = 3.21;
    - so the beams **crack only at 0.8**, where wk ≈ 0.18 mm > 0.1 mm (XS3).
    - The cracking threshold is ψ2 ≈ 0.58 (0.63 with fctm,fl) (P.06). Above it the 7Ø20 section fails wk ≤ 0.1 mm immediately (0.149 mm at Mcr, K.18).
    - For Pórtico 6 alone (VT4, where CYPE reports 86.66), SAP gives 83.4 / 106.0 / 139.8 kN·m. CYPE's own value is 3.9 % above SAP's for that frame.
  - For ULS, ROM 2.0-11 also sets ψ0 = 1.0, compared with CYPE's 0.7.
- **Wind**: ψ2 = 0.
- **Bollard pull**: ψ2 = 0 is what CYPE and the engineer assumed ("coeficiente de combinación para el viento es 0", P276). It is defensible only when mooring loads are transient; ROM 2.0-11 makes it the 50 % quantile of the recorded mooring loads.
  - Without data, the ROM 0.2-90 operational value 0.5 is an upper bound.
  - Consequence (P.04-P.05): with ψ2,Qa = 0.8 and ψ2,TB = 0 the piles stay uncracked (max corner σct = 3.58 < 4.07 MPa, gross section). With ψ2,TB = 0.5 they crack (11.0 MPa), which would need the 0.1 mm wk check in the piles too. The engineer's decision should be documented.
  - TB1 governs. The checker also ran TB2 and TB3 at ψ2,TB = 0.5, giving at most 3.82 MPa (uncracked); the script evaluates only TB1.

---------------------------------------------------------------------------------------------------

## 7. Hand-check targets: CYPE inputs → CYPE output → recomputed

All rows are produced by `validate_codigo.py` (IDs in brackets); the full table is in section 11. A selection:

| Formula | CYPE inputs | CYPE | Ours |
|---|---|---|---|
| fcd = αcc·fck/γc | 1.00, 50, 1.5 | 33.33 | 33.33 [M.01] |
| fctm,fl = (1.6 - h/1000)·fctm | h 550, fctm 3.2098 | 3.37 | 3.3705 [M.06] |
| Ecm × 0.9 (limestone) | fcm 43 | 30669 | 30669.4 [M.07] |
| NEd = 1.35(PP+CM) + 1.05·Qa + 1.5·TB (head) | 86.0, 27.5, 235.7, 146.2 | 620.06 | 620.01 [C.01] |
| NRd, MRd along the ray (pile head, 2nd order) | 620.06/353.51/-68.95, 12Ø25 at ±127.5/±42.5 | 679.16/387.20/-75.52 | 679.15/387.20/-75.52 [U.01-03] |
| (same, fixity section) | 655.55/-352.07/71.29, bars at ±129.5/±43.17 | 733.05/-393.69/79.72 | 733.04/-393.69/79.72 [U.21-23] |
| MRd beam, hogging | 5Ø20 top + 2Ø10 ledge + 7Ø20 bottom | -325.78 | -325.78 [U.36] |
| As,nec, sagging | Mmax 294.61 | 15.10 cm² | 15.10 [U.51] |
| λ = l0/i | 6.70 m, i 115.5 mm | 58.02 | 58.02 [S.02] |
| λlim = 20ABC/√n | φef 1.75, ω 0.48, n 0.1229 | 41.42 | 41.42 [S.05] |
| ei = θ0·αh·αm·l0/2 | 1/200, l 6.70 | 12.94 | 12.94 [S.12] |
| e2 = Kr·Kφ·εyd/(0.45d)·l0²/π² | d 329.5, β 0.213 | 91.56 | 91.56 [S.20] |
| MSd,x = N(ee + ei + e2) | 655.55, -432.56 | -352.07 | -352.07 [S.27] |
| VRd,c | d 263.75, Asl 39.27, σcp 2.08 | 142.85 (min 99.73) | 142.85 / 99.73 [V.16-17] |
| VRd,max pile | z 249.16 / 251.34, ν1 0.6 | 996.63 / 1005.35 | 996.64 / 1005.36 [V.06-07] |
| VRd,max beam | bw 500, z 432, ν1 0.6, fcd 23.33 | 1512.00 | 1512.00 [V.21] |
| VRd,s beam | Asw 2.356, s 100, z 432, fywd 400 | 407.15 | 407.15 [V.24] |
| ρw,min = 0.08√fck/fyk | 35, 500 | 0.0009 | 0.000947 [V.29] |
| sl,max, st,max | d 480 | 360, 360 | 360, 360 [V.32-33] |
| As,min pile 0.004Ac; As,max fcd·Ac/fyd; A's,min 0.1·NEd/fyd | 1600, 33.33, 434.78, NEd 673.90 | 6.40 / 122.67 / 1.55 | 6.40 / 122.67 / 1.55 [D.07-10] |
| scl,max | Ø 25, b = h = 400 | 300 | 300 [D.05] |
| As,min beam W·fctm,fl/(z·fyd) | W 28339.35, z 432 | 5.09 | 5.085 [D.13] |
| σct (uncracked, n = 6.52), M = 86 | inverted T + 5Ø20 + 7Ø20 | -2.20 | -2.205 [K.01] |

**Values that do not match directly, and why**

- Column shear z (C12): the formula matches exactly with CYPE's z, but z itself could not be derived.
- Pile summary "Aprov." for the Forjado-1 points: constant-N definition gives 92.30 vs 92.5 (Cabeza) and 91.70 vs 91.9 (Pie). Both are 0.2 %, within tolerance; the ray definition gives 91.3.
  - This is **not** a rounding effect: the rounded listing forces give 92.31.
  - Both points match if the bars are at ±127.0 mm instead of ±127.5 mm (92.53 / 91.92). The Cimentación point matches exactly with ±129.5 (C4).
- Hand-check figure, top fibre: 2.765 vs 2.73. The figure's strains imply Ec ≈ 33.5 GPa and bars about 50 mm from the faces. No single linear homogenised section reproduces all eight printed values (INFO K.02, section 5.3).
- A10 P607: "410/4.65 = 83 kN" is an arithmetic slip; the correct value is 88.2 kN, still far below the 502 kN tie capacity (INFO K.11).

---------------------------------------------------------------------------------------------------

## 8. Implementation checklist (what to code, in order)

1. `concrete()`, `steel()` and `fctm_fl()`, with the aggregate factor. HA-35 and HA-50 use limestone per the CYPE listing (§1.11).
2. `RCSection`, with `strain_factor` (0.995 for CYPE parity, 1.0 code-strict) and per-bar `active` flags. Code-strict also needs `eps_su` set very large (no steel strain limit, A19.3.2.7(2)b). Leaving it at 0.010 keeps CYPE's steel limit and hides the +2.15 % beam effect (U.54). Section builders:
   - pile: 12Ø25 at c = 72.5 mm to the bar centre (head, tie Ø10) or 70.5 mm (fixity, tie Ø8);
   - T beam "50x55+15x30+15x30": gross centroid 244.18 mm above the soffit; bars 70 mm from the faces; ledge Ø10 at 235 mm above the soffit;
   - L beam "80x55+15x30" and edge beam 25x30: same approach.
3. For every ULS combination (SAP ELU01-22), frame station and member:
   - first-order check (NEd, MEd + emin);
   - piles: second-order check (ei and e2 in both axes, C5);
   - utilisation η along the ray, and optionally at constant N.
4. Shear: VRd,c (columns and beams), VRd,s and VRd,max with cot θ = 1 by default (0.5-2.0 allowed); ν1 = 0.6 with fywd = 400; minimum links and spacing; biaxial η for piles.
5. Torsion checks for the end frames (TEd up to about 28 kN·m): (6.29), (6.31), plus the longitudinal and link steel.
6. Detailing (section 3.6 and section 4). Report both the CE value and the CYPE/AN value where they differ (As,max column; As,min 0.004Ac; z in beam As,min).
7. SLS on a **new quasi-permanent combination** (ψ2 per section 6.3, with sensitivity cases):
   - uncracked check against fctm, then wk ≤ 0.1 mm (XS3);
   - stress limits 0.6·fck (characteristic, XS) and 0.45·fck (quasi-permanent);
   - deflection L/250 and L/500.
8. Test harness: run `validate_codigo.py` in CI (exit code 1 on any FAIL).

---------------------------------------------------------------------------------------------------

## 9. Open questions

- **Column shear lever arm z** (CYPE 249.16 / 251.34). Not reproducible; the definition is internal to CYPE. The impact is negligible (η ≈ 0.09).
- **CYPE bars 6 and 16** (web Ø10 at x = ±185 mm, zero stress). Assumed to be non-structural erection bars; confirm against the beam reinforcement drawing.
- **ψ2 of the uniform quay load** (0.8 per ROM 2.0-11 vs CYPE's 0.3) and **ψ2 of the bollard pull** (0 vs up to 0.5). This is a project decision with a real SLS consequence: the inner beams fail wk ≤ 0.1 mm at ψ2 = 0.8 with the current 7Ø20.
- **φef = 1.75** was a CYPE input. A code-consistent φef (A19.5.8.4) for bollard-governed combinations would be much lower; keep 1.75 unless the orchestrator decides otherwise.
- **Forjado-1 summary 'Aprov.' offset** (92.5 / 91.9 vs 92.30 / 91.70): consistent with bars at ±127.0 mm in the summary run. The detailed check prints and reproduces ±127.5 mm. Unexplained; the effect is 0.2 points.
- **ψ2 threshold.** The inner beams crack for ψ2,Qa > 0.58 (0.63 with fctm,fl). With 7Ø20, any cracked state fails the 0.1 mm limit (wk ≥ 0.149 mm). If the orchestrator adopts ψ2 = 0.8, the beams need a reinforcement change or a documented argument for a lower ψ2.
- **The listing's 'Forjado 1 (0 - 7.25 m)' vs the body's '(0 - 7.00 M)'.** The body pile checks and the listing share the same forces and l0 = 6.70 m, so this looks like a label difference only.
- **BOE errata** we rely on:
  - B = 1 + √(1+2ω) in 5.8.3.1 (use √(1+2ω));
  - "0,85" in the εc2 formula for fck > 50 (use 0.085);
  - "min(G,h)" in 9.5.3(3) (G = b).
  - A check for later *corrección de errores* in the BOE was not done.
  - All three typos were confirmed on the BOE page images:
    - p. 98340: "B = 1 + √(1+2ω) (si ω no es conocido, se puede usar B = 1,1)". The fallback 1.1 only makes sense with √(1+2ω).
    - Tabla A19.3.1: "2,0 + 0,85[(fck-50)]^0,53".
    - p. 98434: "min(G,h)".

### 9.1 Independent check (what was re-verified)

- **BOE page images read by the checker.**
  - 6.2.2 (6.2)/(6.3): CRd,c = 0.18/γc, k1 = 0.15, vmin = 0.035·k^1.5·fck^0.5.
  - 6.2.3: 0.5 ≤ cot θ ≤ 2 (6.7); ν1 (6.10.a/b); the NOTA "fywd deberá reducirse a 0,8fywk"; αcw; (6.9), (6.13), (6.14).
  - 9.2.1.1 (9.1): z "de forma aproximada como z = 0,8h"; As,max = 0.04·Ac.
  - 9.2.2: β3 = 0.5, (9.4)-(9.8).
  - 9.5.2: 0.05·NEd/fyc,d (fyc,d ≯ 400), (9.12) 0.10·NEd/fyd, 0.04·Ac.
  - 9.5.3(1)/(3).
  - 5.2 (5.1)/(5.2); 5.8.3.1 (5.13); C = 0.7 cases; 5.8.3.2 (5.14)-(5.16); 5.8.8.3 (5.34)-(5.37).
  - 6.1(2)-(6); 3.1.6 (αcc = αct = 1.00); 3.1.7; 3.2.7(2)b; 7.1(2); 7.2 (k1 … k5 = 0.6 / 0.45 / 0.8 / 1 / 0.75).
  - Tabla 27.2: XS3 = 0.1 mm, quasi-permanent. 7.3.4 (7.10)-(7.13) with k3 = 3.4, k4 = 0.425; 8.2(2).
  - A18 Apéndice A.1/A.2.
- **Other sources.**
  - AN/UNE-EN 9.5.2/9.5.3 (page image), β3 = 0.33.
  - ROM 2.0-11 Tabla 4.6.4.1 with the preceding paragraph, Tablas 4.6.4.58 and 4.6.4.66.
  - ROM 0.2-90 §3.2.3.2 ψ0/ψ1/ψ2 tables; mooring = QV5 (§3.4.2.3.5).
  - CTE DB SE Tabla 4.2.
- **CYPE targets re-read against `a10_full.txt` / `trasmallo_body_formulas.txt`**, over 40 values:
  - P3 pile head and fixity: every NRd/MRd, Cc/Cs/T with eccentricities, bar strains of bars 1 and 7, ee/ei/e2/etot, λ, λlim, A/B/C, Kr/Kφ/β, d = 328/330, σcp -12.13/-1.46/-11.91/-1.24, z 249.16/251.34, VRd 996.63/1005.35/142.85/99.73, η 0.086/0.552/0.670/0.913/0.894.
  - Hypothesis table (§3.3) for C.01-C.07; listing 'Aprov.' 92.5/91.9/90.7.
  - Beam P3-P4: bar table P381/P389 (bars 6 and 16 print σ = 0.00, so C3 is observed, not tuned); figure image112 (x = 68.52, 1.66 ‰, -11.64 ‰, 22.65).
  - Listing Pórtico 4: -266.03, 294.61, 13.72, 15.10, 22.58, 4.73; edge-beam minimum 2.37.
  - Hand-check figures image117/118; P583 "+0.3Sobrecarga de uso"; P607.
- **Frame mapping** against `sap2000/model/trasmallo.py`:
  - VT1/VT7 are the L end frames and VT2-VT6 the T inner frames;
  - pórtico = axis + 2, so P3-P4 = VT2 (Pórtico 4) and the hand check = VT4 (Pórtico 6);
  - SAP column indices P = 5, M2 = 9, M3 = 10.
- **Sensitivity figures re-run:**
  - C1 +0.088 % (pile);
  - C2 -0.89 %;
  - C3 -338.26;
  - S.29 d = 308.6.

---------------------------------------------------------------------------------------------------

## 10. Sources

- Real Decreto 470/2021, **Código Estructural**, BOE-A-2021-13681, 10-08-2021. Anejo 18 (bases) and Anejo 19 (EC2-1-1 with national parameters) are in the PDF saved as `boe/ce2021.pdf`; the pages used are listed above.
  - https://www.boe.es/buscar/doc.php?id=BOE-A-2021-13681
  - https://www.boe.es/boe/dias/2021/08/10/pdfs/BOE-A-2021-13681.pdf
- Ministerio de Transportes, **Anejo Nacional AN/UNE-EN 1992-1-1** (Eurocódigo 2), `boe/an_en1992.pdf`. Used for comparison and for CYPE's column As,min/As,max, pp. 22, 25, 30-35. https://cdn.mitma.gob.es/portal-web-drupal/carreteras/normativa/AN_UNE-EN%201992-1-1.pdf
- Puertos del Estado, **ROM 2.0-11** *Recomendaciones para el proyecto y ejecución en Obras de Atraque y Amarre* (2012), Tomo II: Tabla 4.6.4.1 (p. 126), Tabla 4.6.2.2, §4.6.4.4.7, Tablas 4.6.4.58 and 4.6.4.66. `rom/rom20_11.pdf`; https://www.puertos.es/system/files/2024-04/ROM%202.0-11.pdf
- Puertos del Estado, **ROM 0.2-90** *Acciones en el proyecto de obras marítimas y portuarias*, Parte 3, §3.2.3.2 (ψ tables). `rom/rom02_90_p3.pdf`; http://www.abcpuertos.cl/documentos/Rom_02/rom_02_90_3_Acciones.pdf
- **CTE DB SE** (Documento Básico Seguridad Estructural), Tabla 4.2 *Coeficientes de simultaneidad*. `cte/DBSE.pdf`; https://www.codigotecnico.org/pdf/Documentos/SE/DBSE.pdf
- EN 1990:2002 Annex A1, Table A1.1 (ψ for category E storage and for wind), for reference.
- Anejo 10 (A10_CALC_ESTRUCTURAS.docx): CYPECAD 2023, licence 84023, "muelle mod 5".
  - Body: P217-P608.
  - Appendix: P1449-P1835.
  - Formulas recovered to `trasmallo_body_formulas.txt`.

---------------------------------------------------------------------------------------------------

## 11. Output of `python3 validate_codigo.py --json validate_codigo_results.json` (verbatim, re-run after the independent check)

```
   [ULS fibre analyses: 17.6 s]

====================================================================================================================================
M - MATERIALS (A19.2.4.2.4, A19.3.1, A19.3.2)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
M.01    fcd HA-50 = acc*fck/gc (acc=1.00)                    A19.3.1.6(1)                 33.33        33.33   +0.01%  PASS
M.02    fcd HA-35                                            A19.3.1.6(1)                 23.33        23.33   +0.01%  PASS
M.03    fyd B500SD = fyk/gs                                  A19.2.4.2.4                 434.78       434.78   +0.00%  PASS
M.04    eps_yd = fyd/Es (Es = 200 GPa)                       A19.3.2.7(4)               0.00217     0.002174   +0.18%  PASS
M.05    fctm HA-35 = 0.30 fck^(2/3)                          A19 Tabla 3.1                 3.21       3.2100   -0.00%  PASS
M.06    fctm,fl HA-35, h = 550 mm                            A19.3.1.8 (3.23)              3.37       3.3705   +0.01%  PASS
M.07    Ecm HA-35 limestone (x0.9)                           A19.3.1.3(2)                 30669     30669.43   +0.00%  PASS
M.08    Ecm HA-50 limestone (x0.9)                           A19.3.1.3(2)                 33550     33550.08   +0.00%  PASS
M.09    Ecm HA-25 limestone (x0.9)                           A19.3.1.3(2)                 28328     28328.23   +0.00%  PASS
M.10    eps_cu2 (fck<=50)                                    A19 Tabla 3.1               0.0035     0.003500   +0.00%  PASS
M.11    eps_c2 (fck<=50)                                     A19 Tabla 3.1               0.0020     0.002000   +0.00%  PASS
M.12    Steel stress at eps=-0.00995 (horizontal branch)     A19.3.2.7(2)b              -434.78      -434.78   -0.00%  PASS  P381 bars 1-5: -434.78 @ -0.009950
M.13    Steel stress at eps=+0.001826 (elastic, Es)          A19.3.2.7(4)                365.17       365.20   +0.01%  PASS

====================================================================================================================================
C - LOAD COMBINATIONS (Anejo 18 eq. 6.10, CTE DB SE-AE psi as used by CYPE)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
C.01    NEd head 1.35G+1.05Qa+1.5TB (1.05=1.5*0.7)           A18 (6.10); CTE psi0        620.06       620.01   -0.01%  PASS
C.02    MEd,x head same comb. (listing My)                   A18 (6.10)                  288.36       288.31   -0.02%  PASS
C.03    VEd,y head same comb.                                A18 (6.10)                   85.36        85.29   -0.08%  PASS
C.04    NEd base (Empotramiento) same comb.                  A18 (6.10)                  655.55       655.51   -0.01%  PASS
C.05    NEd max: 1.35G+1.5Qa+0.9TB (0.9=1.5*0.6)             A18 (6.10); CTE psi0        673.90       673.86   -0.01%  PASS
C.06    NEd min for VRd,c: 1.0G+1.5TB (head)                 A18 (6.10)                  332.81       332.80   -0.00%  PASS
C.07    VEd,y for VRd,c: 1.0G+1.5TB (head)                   A18 (6.10)                   78.86        78.85   -0.01%  PASS

====================================================================================================================================
U - ULS BENDING + AXIAL, FIBRE SECTION (A19.6.1, A19.3.1.7, A19.3.2.7)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
U.01    Pile head NRd (2nd-order ray)                        A19.6.1                     679.16       679.15   -0.00%  PASS
U.02    Pile head MRd,x                                      A19.6.1                     387.20       387.20   -0.00%  PASS
U.03    Pile head MRd,y                                      A19.6.1                     -75.52       -75.52   -0.00%  PASS
U.04    Pile head Cc (concrete resultant)                    A19.6.1                    1422.97      1422.96   -0.00%  PASS
U.05    Pile head Cs                                         A19.6.1                     536.86       536.85   -0.00%  PASS
U.06    Pile head T                                          A19.6.1                    1280.67      1280.66   -0.00%  PASS
U.07    Pile head ecc,y                                      A19.6.1                     140.81       140.81   -0.00%  PASS
U.08    Pile head eT,y                                       A19.6.1                     -93.92       -93.92   -0.00%  PASS
U.09    Pile head eps bar 7 (most tensioned)                 A19.6.1(3)               -0.004001    -0.004001   -0.00%  PASS
U.10    Pile head eps bar 1                                  A19.6.1(3)                0.001826     0.001826   -0.01%  PASS
U.11    Pile head eps_c,max (=0.995*eps_cu2)                 A19.6.1(3)                  0.0035     0.003482   -0.50%  PASS  CYPE stops at 99.5 % of eps_cu2
U.12    Pile head eta = NSd/NRd (instability)                A19.6.1                      0.913       0.9130   -0.00%  PASS
U.13    Pile head 1st-order NRd                              A19.6.1                     925.83       925.82   -0.00%  PASS
U.14    Pile head 1st-order MRd,x                            A19.6.1                     430.56       430.56   -0.00%  PASS
U.15    Pile head 1st-order MRd,y                            A19.6.1                      -5.68      -5.6888   -0.15%  PASS
U.16    Pile head eta section = NEd/NRd                      A19.6.1                      0.670       0.6697   -0.04%  PASS
U.17    Pile fixity 1st-order NRd                            A19.6.1                    1021.59      1021.58   -0.00%  PASS
U.18    Pile fixity 1st-order MRd,x                          A19.6.1                    -441.89      -441.89   +0.00%  PASS
U.19    Pile fixity 1st-order MRd,y                          A19.6.1                       4.34       4.3478   +0.18%  PASS
U.20    Pile fixity eta section                              A19.6.1                      0.642       0.6417   -0.05%  PASS
U.21    Pile fixity 2nd-order NRd                            A19.6.1                     733.05       733.04   -0.00%  PASS
U.22    Pile fixity 2nd-order MRd,x                          A19.6.1                    -393.69      -393.69   +0.00%  PASS
U.23    Pile fixity 2nd-order MRd,y                          A19.6.1                      79.72        79.72   -0.00%  PASS
U.24    Pile fixity Cc / Cs / T : Cc                         A19.6.1                    1439.73      1439.72   -0.00%  PASS
U.25    Pile fixity T                                        A19.6.1                    1269.29      1269.28   -0.00%  PASS
U.26    Pile fixity eta (instability)                        A19.6.1                      0.894       0.8943   +0.03%  PASS
U.27    Pile head design-load equilibrium Cc                 A19.6.1                    1321.67      1321.69   +0.00%  PASS
U.28    Pile head design-load equilibrium T                  A19.6.1                    1126.46      1126.48   +0.00%  PASS
U.29    Pile head design-load eps bar 7                      A19.6.1                  -0.002733    -0.002733   +0.00%  PASS
U.30    Pile head design-load eps_c,max                      A19.6.1                     0.0026     0.002555   -1.72%  PASS
U.31    Pile fixity design-load equilibrium Cc               A19.6.1                    1315.83      1315.84   +0.00%  PASS
U.32    Pile fixity design-load equilibrium Cs               A19.6.1                     428.49       428.49   +0.00%  PASS
U.33    Pile fixity design-load eps bar 1                    A19.6.1                  -0.002603    -0.002603   +0.01%  PASS
U.34    Listing Aprov. P3 Cimentacion (constant-N def.)      CYPE listing 3.5.1            90.7        90.70   -0.00%  PASS
U.35    Listing Aprov. P3 Cabeza (constant-N def.)           CYPE listing 3.5.1            92.5        92.30   -0.21%  PASS  ray def. gives 91.3; NOT a force-rounding effect (listing forces 620.1/353.5/-69.0 give 92.31); Forjado-1 points run 0.2 pt low (see U.53), matched if bars sit at +-127.0 mm (92.53)
U.36    Beam P3-P4 hogging MRd,x (N=0)                       A19.6.1                    -325.78      -325.78   -0.00%  PASS
U.37    Beam Cc = T                                          A19.6.1                     767.00       766.98   -0.00%  PASS
U.38    Beam ecc,y                                           A19.6.1                    -219.16      -219.16   -0.00%  PASS
U.39    Beam eT,y                                            A19.6.1                     205.59       205.60   +0.00%  PASS
U.40    Beam eps top bars (=0.995*eps_su)                    A19.6.1(3)               -0.009950    -0.009950   +0.00%  PASS
U.41    Beam eps_c,max                                       A19.6.1                     0.0017     0.001657   -2.53%  PASS  figure: 1.66 permil
U.42    Beam sig_c,max                                       A19.3.1.7                    22.65        22.65   -0.01%  PASS
U.43    Beam neutral-axis depth x (figure P381)              A19.6.1                      68.52        68.52   +0.00%  PASS
U.44    Beam eta = MEd/MRd                                   A19.6.1                      0.840       0.8402   +0.02%  PASS
U.45    Beam design-load Cc                                  A19.6.1                     543.32       543.33   +0.00%  PASS
U.46    Beam design-load Cs                                  A19.6.1                      93.94        93.94   +0.00%  PASS
U.47    Beam design-load T                                   A19.6.1                     637.26       637.27   +0.00%  PASS
U.48    Beam design-load sig_s top bars                      A19.6.1                    -392.45      -392.46   -0.00%  PASS
U.49    Beam design-load sig_c,max                           A19.3.1.7                    11.65        11.66   +0.04%  PASS
U.50    Beam design-load eps ledge O10 (bar 7)               A19.6.1                  -0.000662    -0.000662   -0.01%  PASS
U.51    Beam 'Area Inf. Nec.' Mmax=294.61 (singly r.)        A19.6.1                      15.10        15.10   +0.01%  PASS
U.52    Beam 'Area Sup. Nec.' M(P3)=-273.71                  A19.6.1                      13.72        13.72   +0.04%  PASS  listing zone shows -266.03; CYPE sizes with the node value
U.53    Listing Aprov. P3 Pie (constant-N def.)              CYPE listing 3.5.1            91.9        91.70   -0.22%  PASS  same +0.2 pt offset as U.35 (Cimentacion U.34 exact); bars at +-127.0 give 91.92
U.54    Beam MRd code-strict (no 10 permil steel limit)      A19.3.2.7(2)b                    -      -332.78           INFO  +2.15 % vs CYPE -325.78 (concrete reaches 3.5 permil); piles unchanged +0.09 %

====================================================================================================================================
S - COLUMN SLENDERNESS / IMPERFECTIONS / NOMINAL CURVATURE (A19.5.2, A19.5.8)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
S.01    Radius of gyration ic                                A19.5.8.3.2                  11.55        11.55   -0.03%  PASS
S.02    Slenderness lambda = l0/i (l0 = 6.70 m)              A19.5.8.3.2 (5.14)           58.02        58.02   +0.01%  PASS
S.03    omega = As fyd/(Ac fcd)                              A19.5.8.3.1                   0.48       0.4802   +0.04%  PASS
S.04    lambda_lim, NEd=620.06 (n=0.116)                     A19.5.8.3.1 (5.13)           42.58        42.58   +0.01%  PASS
S.05    lambda_lim, NEd=655.55 (n=0.123)                     A19.5.8.3.1 (5.13)           41.42        41.42   -0.01%  PASS
S.06    A = 1/(1+0.2 phi_ef), phi_ef=1.75                    A19.5.8.3.1                   0.74       0.7407   +0.10%  PASS
S.07    B = sqrt(1+2 omega) (UNE-EN form)                    A19.5.8.3.1                   1.40       1.4001   +0.01%  PASS  BOE erratum 1+sqrt()
S.08    C (rm unknown/unbraced)                              A19.5.8.3.1                   0.70       0.7000   +0.00%  PASS
S.09    n = NEd/(Ac fcd), fixity                             A19.5.8.3.1                   0.12       0.1229   +2.43%  PASS
S.10    alpha_h = 2/sqrt(l), l = 6.70 m                      A19.5.2(5)                  0.7727       0.7727   -0.00%  PASS
S.11    theta_i = theta0 ah am (theta0 = 1/200)              A19.5.2 (5.1)               0.0039     0.003863   -0.94%  PASS
S.12    ei = theta_i l0/2                                    A19.5.2 (5.2)                12.94        12.94   +0.02%  PASS
S.13    e_min = max(h/30, 20)                                A19.6.1(4)                   20.00        20.00   +0.00%  PASS
S.14    e0,x head = MEd/NEd                                  A19.6.1(4)                  465.06       465.05   -0.00%  PASS
S.15    1/r0 = eps_yd/(0.45 d), d=327.5                      A19.5.8.8.3 (5.34)          0.0148       0.0148   -0.33%  PASS
S.16    1/r = Kr Kphi /r0                                    A19.5.8.8.3                 0.0203       0.0203   -0.23%  PASS
S.17    e2 = (1/r) l0^2 / c, c = pi^2                        A19.5.8.8.2                  92.12        92.12   +0.00%  PASS
S.18    1/r0 = eps_yd/(0.45 d), d=329.5                      A19.5.8.8.3 (5.34)          0.0147       0.0147   -0.26%  PASS
S.19    1/r = Kr Kphi /r0                                    A19.5.8.8.3                 0.0201       0.0201   +0.15%  PASS
S.20    e2 = (1/r) l0^2 / c, c = pi^2                        A19.5.8.8.2                  91.56        91.56   +0.00%  PASS
S.21    Kr = (nu-n)/(nu-nbal) <= 1                           A19.5.8.8.3 (5.36)           1.000       1.0000   +0.00%  PASS  raw=1.26
S.22    nu = 1 + omega                                       A19.5.8.8.3                   1.48       1.4802   +0.01%  PASS
S.23    beta = 0.35 + fck/200 - lambda/150                   A19.5.8.8.3                  0.213       0.2132   +0.08%  PASS
S.24    Kphi = 1 + beta phi_ef                               A19.5.8.8.3 (5.37)           1.373       1.3731   +0.00%  PASS
S.25    c = pi^2 (sinusoidal curvature)                      A19.5.8.8.2(4)               9.870       9.8696   -0.00%  PASS
S.26    etot = ee + ei + e2 (fixity, x)                      A19.5.8.8.2 (5.31)          537.06       537.06   +0.00%  PASS
S.27    MSd,x = N etot (fixity)                              A19.5.8.8.2                 352.07       352.07   +0.00%  PASS
S.28    MSd,y = N (ee,y + ei + e2) (fixity)                  A19.5.8.8.2                  71.29        71.29   +0.00%  PASS  CYPE adds ei and e2 in BOTH axes
S.29    e2 with d = h/2 + i_s (5.35, code-strict)            A19.5.8.8.3(2)                   -        97.75           INFO  CYPE uses d to extreme bar row (91.56); +6.9 %

====================================================================================================================================
V - SHEAR (A19.6.2.2, A19.6.2.3, A19.9.2.2)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
V.01    nu1 = 0.6 (fck<=60, fywd=0.8 fywk)                   A19.6.2.3(3) (6.10.a)        0.600       0.6000   +0.00%  PASS
V.02    sigma_cp (CYPE) = (NEd - As' fyd)/Ac, dir X          A19.6.2.3(3)                -12.13       -12.13   -0.01%  PASS
V.03    sigma_cp (CYPE), dir Y, As' = 4O25                   A19.6.2.3(3)                 -1.46      -1.4602   -0.01%  PASS
V.04    sigma_cp (CYPE) fixity dir X                         A19.6.2.3(3)                -11.91       -11.91   +0.00%  PASS
V.05    alpha_cw (sigma_cp <= 0 -> 1)                        A19.6.2.3(3) (6.11)          1.000       1.0000   +0.00%  PASS
V.06    Pile VRd,max head (z = 249.16 CYPE)                  A19.6.2.3(3) (6.9)          996.63       996.64   +0.00%  PASS
V.07    Pile VRd,max fixity (z = 251.34 CYPE)                A19.6.2.3(3) (6.14)        1005.35      1005.36   +0.00%  PASS
V.08    Pile VRd,max with z = 0.9 d (d = 263.75)             A19.6.2.3(1)                     -       949.50           INFO  CYPE's column z not reproduced (internal lever arm); -4.7 %, conservative
V.09    eta1 = sqrt((Vx/VRdmax)^2+(Vy/VRdmax)^2) head        CYPE biaxial                 0.086       0.0857   -0.40%  PASS
V.10    Asl = 8 O25 (all bars except compressed row)         A19.6.2.2(1)                 39.27        39.27   -0.00%  PASS
V.11    CRd,c = 0.18/gc                                      A19.6.2.2(1)                 0.120       0.1200   +0.00%  PASS
V.12    k = 1 + sqrt(200/d) <= 2, d = 263.75                 A19.6.2.2(1)                 1.871       1.8708   -0.01%  PASS
V.13    rho_l = Asl/(bw d) <= 0.02                           A19.6.2.2(1)                 0.020       0.0200   +0.00%  PASS
V.14    sigma_cp = NEd/Ac <= 0.2 fcd                         A19.6.2.2(1)                  2.08       2.0801   +0.00%  PASS
V.15    vmin = 0.035 k^1.5 fck^0.5                           A19.6.2.2(1) (6.3)            0.63       0.6333   +0.52%  PASS
V.16    Pile VRd,c (CYPE label VRd,s)                        A19.6.2.2(1) (6.2.a)        142.85       142.85   -0.00%  PASS
V.17    Pile VRd,c minimum                                   A19.6.2.2(1) (6.2.b)         99.73        99.73   -0.00%  PASS
V.18    eta2 = VEd/VRd,c (Vx=0.34, Vy=78.86)                 A19.6.2.1(3)                 0.552       0.5521   +0.01%  PASS
V.19    Beam z = 0.9 d                                       A19.6.2.3(1)                432.00       432.00   +0.00%  PASS
V.20    Beam sigma_cp (CYPE), As' = 7O20                     A19.6.2.3(3)                 -2.62      -2.6196   +0.02%  PASS
V.21    Beam VRd,max (theta = 45 deg)                        A19.6.2.3(3) (6.9)         1512.00      1512.00   +0.00%  PASS
V.22    fywd = 0.8 fywk (NOTA to 6.2.3(3))                   A19.6.2.3(3) NOTA           400.00       400.00   +0.00%  PASS
V.23    Asw = 3 legs O10                                     -                             2.36       2.3562   -0.16%  PASS
V.24    Beam VRd,s = Asw/s z fywd cot(theta)                 A19.6.2.3(3) (6.8)          407.15       407.15   +0.00%  PASS
V.25    Beam eta VEd/VRd,max (VEd = 390.18)                  A19.6.2                      0.258       0.2581   +0.02%  PASS
V.26    Beam eta VEd/VRd,s                                   A19.6.2                      0.958       0.9583   +0.03%  PASS
V.27    'Area Transv. Nec.' = VEd/(z fywd)                   A19.6.2.3(3)                 22.58        22.58   -0.00%  PASS
V.28    rho_w = Asw/(s bw sin a)                             A19.9.2.2(5) (9.4)          0.0047     0.004712   +0.26%  PASS
V.29    rho_w,min = 0.08 sqrt(fck)/fyk                       A19.9.2.2(5) (9.5)          0.0009     0.000947   +5.17%  PASS
V.30    Min. stirrups 50 cm web (listing 'Nec.')             A19.9.2.2(5)                  4.73       4.7329   +0.06%  PASS
V.31    Min. stirrups 25x30 edge beam                        A19.9.2.2(5)                  2.37       2.3664   -0.15%  PASS
V.32    s_l,max = 0.75 d (1 + cot a)                         A19.9.2.2(6) (9.6)             360       360.00   +0.00%  PASS
V.33    s_t,max = 0.75 d <= 600                              A19.9.2.2(8) (9.8)             360       360.00   +0.00%  PASS

====================================================================================================================================
D - DETAILING, MIN/MAX REINFORCEMENT (A19.8.2, A19.9.2, A19.9.5 + AN/UNE-EN 1992-1-1)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
D.01    Clear spacing min, long. O25, dg 20                  A19.8.2(2)                      25        25.00   +0.00%  PASS  CYPE s2 = 1.25 dg = 25 = dg + 5
D.02    Clear spacing pile bars (85 - 25)                    geometry                        60        60.00   +0.00%  PASS
D.03    Clear spacing beam top bars (82.5 - 20)              geometry                        63        62.50   -0.79%  PASS
D.04    phi_long >= 12 mm (pile O25)                         A19.9.5.2(1)                    12        12.00   +0.00%  PASS
D.05    s_cl,max = min(15 phi_min, 300, min(b,h))            A19.9.5.3(3)                   300       300.00   +0.00%  PASS  terms (375.0, 300.0, 400.0) (CYPE prints s1=300, s2=375, s3=400: s1/s2 labels swapped)
D.06    phi_t >= max(6, phi_max/4)                           A19.9.5.3(1)                   6.3       6.2500   -0.79%  PASS
D.07    A's,min = 0.10 NEd/fyd (NEd = 673.90)                A19.9.5.2(2) (9.12)           1.55       1.5500   -0.00%  PASS
D.08    As,min = 0.004 Ac (AN/UNE-EN 1992-1-1)               AN 9.5.2(2)                   6.40       6.4000   +0.00%  PASS  not in the CE A19 text
D.09    A's,min per face 0.05 NEd/fyc,d (fyc,d<=400)         A19.9.5.2(2)                     -       0.8424           INFO
D.10    As,max = fcd Ac / fyd (AN / CYPE)                    AN 9.5.2(3)                 122.67       122.67   -0.00%  PASS
D.11    As,max = 0.04 Ac (CE A19 text) vs 58.91              A19.9.5.2(3)                     -        64.00           INFO  58.91 <= 64.00 also OK
D.12    Beam W top fibre (gross)                             A19.9.2.1.1               28339.35     28339.35   +0.00%  PASS
D.13    Beam As,min = W fctm,fl/(z fyd), z=0.9d=432          A19.9.2.1.1(1) (9.1)          5.09       5.0854   -0.09%  PASS
D.14    Beam As,min with z = 0.8 h (code text)               A19.9.2.1.1(1)                   -       4.9929           INFO  -1.8 % vs CYPE
D.15    Beam As,max = 0.04 Ac                                A19.9.2.1.1(3)                   -       146.00           INFO
D.16    Long. bar spacing <= 350 mm (bottom bars)            A19.9.2.3(4)                   150       150.00   +0.00%  PASS

====================================================================================================================================
K - SLS: CRACKING CRITERION, CRACK WIDTH, DEFLECTION LIMITS (A19.7.1, A19.7.3, CE Tabla 27.2)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
K.01    sigma_ct bottom, M_qp = +86 kN*m (P570)              A19.7.1(2)                   -2.20      -2.2048   -0.22%  PASS  n = Es/Ecm = 6.52
K.02    sigma_c top, M_qp = +86                              A19.7.1(2)                    2.73       2.7651   +1.28%  INFO  figure strains imply Ec ~33.5 GPa and bars ~50 mm from the faces; no single linear homogenised section fits all 8 printed values; governing bottom value matches
K.03    sigma_s bottom bars, M_qp = +86                      A19.7.1(2)                  -10.27       -10.25   +0.17%  PASS
K.04    fct,eff = fctm used by engineer (3.2)                A19.7.1(2)                     3.2       3.2100   +0.31%  PASS
K.05    Mcr sagging (homogenised, fctm)                      A19.7.1(2)                       -       125.21           INFO
K.06    Mcr hogging (homogenised, fctm)                      A19.7.1(2)                       -        99.84           INFO
K.07    wmax XS3, RC, quasi-permanent comb.                  CE Tabla 27.2                    -       0.1000           INFO
K.08    fT,lim = L/250, L = 3.05 m                           CYPE (CTE/A19.7.4.1)         12.20        12.20   +0.00%  PASS
K.09    fA,lim = L/500                                       CYPE (CTE/A19.7.4.1)          6.10       6.1000   +0.00%  PASS
K.10    Cantil tie: 4O20 x 400 MPa (P607)                    hand check                     502       502.40   +0.08%  PASS
K.11    Cantil tie force 410/4.65 (P607 prints 83)           hand check                      83        88.17   +6.23%  INFO  arithmetic slip in A10: 410/4.65 = 88.2 kN (still << 502)
K.12    Cracked x (M = 151.9, sagging)                       A19.7.3.4                        -       131.99           INFO
K.13    sigma_s bottom bars (cracked)                        A19.7.3.4                        -       159.64           INFO
K.14    hc,ef = min(2.5(h-d), (h-x)/3, h/2)                  A19.7.3.2(3)                     -       139.34           INFO
K.15    sr,max = k3 c + k1 k2 k4 phi/rho_p,eff               A19.7.3.4(3) (7.11)              -       376.34           INFO
K.16    eps_sm - eps_cm (kt = 0.4)                           A19.7.3.4(2) (7.9)               -       0.4789           INFO
K.17    wk (limit 0.1 mm XS3)                                A19.7.3.4 (7.8)                  -       0.1802           INFO
K.18    wk at M = Mcr,sag = 125.2 (first cracking)           A19.7.3.4 (7.8)                  -       0.1486           INFO  > 0.1 mm: with 7O20 the XS3 limit can only be met by staying uncracked

====================================================================================================================================
P - PSI2 SENSITIVITY WITH THE SAP2000 v27.1 RESULTS (quasi-permanent combination)
====================================================================================================================================
id      check                                                clause                        CYPE     computed    delta  status
P.01    Inner beams M_qp,max sag (psi2=0.3) SAP              A18 6.5.3 (6.16b)            86.66        90.41   +4.33%  INFO  max of VT2-VT6 (VT4 = Portico 6: 83.43); hog -30.2; sigma_ct = 2.32 MPa vs fctm 3.21 -> UNCRACKED
P.02    Inner beams M_qp,max sag (psi2=0.5) SAP              A18 6.5.3 (6.16b)                -       115.01           INFO  max of VT2-VT6 (VT4 = Portico 6: 105.99); hog -37.7; sigma_ct = 2.95 MPa vs fctm 3.21 -> UNCRACKED
P.03    Inner beams M_qp,max sag (psi2=0.8) SAP              A18 6.5.3 (6.16b)                -       151.90           INFO  max of VT2-VT6 (VT4 = Portico 6: 139.83); hog -48.9; sigma_ct = 3.89 MPa vs fctm 3.21 -> CRACKED: check wk <= 0.1 mm
P.06    psi2,Qa at which inner beams crack (SAP)             A19.7.1(2)                       -       0.5830           INFO  VT2_9 x=0: M_qp = 53.5 + 123.0 psi2; Mcr 125.2 (fctm); 0.63 with fct,eff = fctm,fl
P.04    Piles max corner sigma_ct, psi2 Qa=0.8, TB=0.0       A19.7.1(2)                       -       3.5799           INFO  PIL_P2 z=6.7 m; fctm(HA-50) = 4.07 -> UNCRACKED
P.05    Piles max corner sigma_ct, psi2 Qa=0.8, TB=0.5       A19.7.1(2)                       -        11.01           INFO  PIL_P1 z=6.7 m; fctm(HA-50) = 4.07 -> CRACKED: wk check needed (0.1 mm)

====================================================================================================================================
SUMMARY: 151 PASS, 0 FAIL, 25 INFO  (tolerance: max(0.5 %, half unit of CYPE's last printed digit))
JSON written to validate_codigo_results.json
```
