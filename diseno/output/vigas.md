# Vigas transversales y vigas de borde: comprobación Código Estructural (Anejo 19)

Generado por `diseno/codigo/vigas.py` en 15.8 s. Casos:

- **CYPE**: base CYPE, modo cype, psi2,Qa = 0.3, cot(theta) = 1, nu(torsión) = 0.6, suspensión en veredicto = False. parity with Anejo 10: Mode.CYPE, psi0,Qa = 0.7, psi2,Qa = 0.3, theta = 45 deg (suspension steel A19.6.2.1(9) reported as information, CYPE does not check it)
- **CE-CYPE**: base CYPE, modo codigo, psi2,Qa = 0.3, cot(theta) = opt, nu(torsión) = 0.516, suspensión en veredicto = True. code-strict section with the Anejo 10 load assumptions (psi2,Qa = 0.3)
- **CE-ROM**: base ROM, modo codigo, psi2,Qa = 0.8, cot(theta) = opt, nu(torsión) = 0.516, suspensión en veredicto = True. FINAL DESIGN: code-strict, ROM 2.0-11 (psi0,Qa = 1.0, psi2,Qa = 0.8, bollard psi2 = 0), XS3 0.1 mm

## 1. Veredicto por elemento

| member | label | case | flexión ELU | cortante | torsión | disposiciones | fisuración ELS | tensiones ELS | flecha | torsión [info] | torsión ala [sensib.] | fisuración TB 0.5 [sensib.] | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | Pórtico 3 (eje 1) | CYPE | 0.925 | 0.721 | 0.964 | 0.958 | 0 | 0.715 | 0.04 |  | 1.076 | 0 | CUMPLE |
| VT1 | Pórtico 3 (eje 1) | CE-CYPE | 0.872 | 0.427 | 0.949 | 0.958 | 0 | 0.715 | 0.04 |  | 1.114 | 0 | CUMPLE |
| VT1 | Pórtico 3 (eje 1) | CE-ROM | 0.873 | 0.478 | 0.973 | 0.958 | 0 | 0.715 | 0.069 |  | 1.185 | 0 | CUMPLE |
| VT2 | Pórtico 4 (eje 2) | CYPE | 0.81 | 0.944 |  | 0.542 | 0 | 0.622 | 0.098 | 1.052 |  | 0 | CUMPLE |
| VT2 | Pórtico 4 (eje 2) | CE-CYPE | 0.766 | 0.634 |  | 0.542 | 0 | 0.622 | 0.098 | 0.816 |  | 0 | CUMPLE |
| VT2 | Pórtico 4 (eje 2) | CE-ROM | 0.77 | 0.717 |  | 0.542 | 1.72 | 0.622 | 0.178 | 0.833 |  | 1.858 | NO CUMPLE |
| VT3 | Pórtico 5 (eje 3) | CYPE | 0.926 | 0.923 |  | 0.542 | 0 | 0.696 | 0.088 | 0.928 |  | 1.547 | CUMPLE |
| VT3 | Pórtico 5 (eje 3) | CE-CYPE | 0.876 | 0.611 |  | 0.542 | 0 | 0.696 | 0.088 | 0.879 |  | 1.547 | CUMPLE |
| VT3 | Pórtico 5 (eje 3) | CE-ROM | 0.879 | 0.7 |  | 0.542 | 1.55 | 0.696 | 0.161 | 0.883 |  | 1.653 | NO CUMPLE |
| VT4 | Pórtico 6 (eje 4) | CYPE | 0.783 | 0.887 |  | 0.542 | 0 | 0.588 | 0.09 | 0.893 |  | 0 | CUMPLE |
| VT4 | Pórtico 6 (eje 4) | CE-CYPE | 0.74 | 0.604 |  | 0.542 | 0 | 0.588 | 0.09 | 0.743 |  | 0 | CUMPLE |
| VT4 | Pórtico 6 (eje 4) | CE-ROM | 0.744 | 0.684 |  | 0.542 | 1.584 | 0.588 | 0.164 | 0.747 |  | 1.724 | NO CUMPLE |
| VT5 | Pórtico 7 (eje 5) | CYPE | 0.899 | 0.908 |  | 0.542 | 0 | 0.675 | 0.088 | 0.925 |  | 0 | CUMPLE |
| VT5 | Pórtico 7 (eje 5) | CE-CYPE | 0.85 | 0.606 |  | 0.542 | 0 | 0.675 | 0.088 | 0.859 |  | 0 | CUMPLE |
| VT5 | Pórtico 7 (eje 5) | CE-ROM | 0.853 | 0.693 |  | 0.542 | 1.55 | 0.675 | 0.161 | 0.864 |  | 1.642 | NO CUMPLE |
| VT6 | Pórtico 8 (eje 6) | CYPE | 0.756 | 0.915 |  | 0.542 | 0 | 0.609 | 0.098 | 1.028 |  | 0 | CUMPLE |
| VT6 | Pórtico 8 (eje 6) | CE-CYPE | 0.715 | 0.625 |  | 0.542 | 0 | 0.609 | 0.098 | 0.759 |  | 0 | CUMPLE |
| VT6 | Pórtico 8 (eje 6) | CE-ROM | 0.719 | 0.703 |  | 0.542 | 1.72 | 0.609 | 0.178 | 0.776 |  | 1.836 | NO CUMPLE |
| VT7 | Pórtico 9 (eje 7) | CYPE | 0.846 | 0.678 | 0.888 | 0.958 | 0 | 0.654 | 0.04 |  | 1.044 | 0 | CUMPLE |
| VT7 | Pórtico 9 (eje 7) | CE-CYPE | 0.798 | 0.406 | 0.882 | 0.958 | 0 | 0.654 | 0.04 |  | 1.047 | 0 | CUMPLE |
| VT7 | Pórtico 9 (eje 7) | CE-ROM | 0.798 | 0.456 | 0.906 | 0.958 | 0 | 0.654 | 0.069 |  | 1.118 | 0 | CUMPLE |
| VBM | Pórtico 1 (viga de borde) | CYPE | 0.937 | 1.041 |  | 0.855 | 1.559 | 0.771 | 0.184 | 1.674 |  | 1.572 | NO CUMPLE |
| VBM | Pórtico 1 (viga de borde) | CE-CYPE | 0.927 | 0.521 |  | 0.855 | 1.559 | 0.771 | 0.184 | 1.051 |  | 1.572 | NO CUMPLE |
| VBM | Pórtico 1 (viga de borde) | CE-ROM | 0.931 | 0.522 |  | 0.855 | 3.063 | 0.771 | 0.328 | 1.054 |  | 3.084 | NO CUMPLE |
| VBT | Pórtico 10 (viga de borde) | CYPE | 0.952 | 1.081 |  | 0.855 | 1.566 | 0.789 | 0.184 | 1.678 |  | 1.606 | NO CUMPLE |
| VBT | Pórtico 10 (viga de borde) | CE-CYPE | 0.942 | 0.54 |  | 0.855 | 1.566 | 0.789 | 0.184 | 1.055 |  | 1.606 | NO CUMPLE |
| VBT | Pórtico 10 (viga de borde) | CE-ROM | 0.953 | 0.547 |  | 0.855 | 3.083 | 0.789 | 0.328 | 1.06 |  | 3.15 | NO CUMPLE |

## 2. Comprobaciones determinantes, caso final CE-ROM

| member | family | eta | ok | check | section | combo |
|---|---|---|---|---|---|---|
| VT1 | flexión ELU | 0.873 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT1 | cortante | 0.478 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT1 | torsión | 0.973 | sí | M/MRd + ΣAsl,T(cordón)/As <= 1 | cara pilote mar - vano | ELR08 |
| VT1 | disposiciones | 0.958 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT1 | fisuración ELS | 0 | sí | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT1 | tensiones ELS | 0.715 | sí | sigma_s <= 0.8 fyk (característica ELS01-08) | hog | ELS04 |
| VT1 | flecha | 0.069 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT2 | flexión ELU | 0.77 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT2 | cortante | 0.717 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT2 | disposiciones | 0.542 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT2 | fisuración ELS | 1.72 | NO | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT2 | tensiones ELS | 0.622 | sí | sigma_c <= 0.6 fck (característica ELS01-08) | sag | ELS04 |
| VT2 | flecha | 0.178 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT3 | flexión ELU | 0.879 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT3 | cortante | 0.7 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT3 | disposiciones | 0.542 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT3 | fisuración ELS | 1.55 | NO | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT3 | tensiones ELS | 0.696 | sí | sigma_s <= 0.8 fyk (característica ELS01-08) | hog | ELS04 |
| VT3 | flecha | 0.161 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT4 | flexión ELU | 0.744 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT4 | cortante | 0.684 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT4 | disposiciones | 0.542 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT4 | fisuración ELS | 1.584 | NO | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT4 | tensiones ELS | 0.588 | sí | sigma_s <= 0.8 fyk (característica ELS01-08) | hog | ELS04 |
| VT4 | flecha | 0.164 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT5 | flexión ELU | 0.853 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT5 | cortante | 0.693 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT5 | disposiciones | 0.542 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT5 | fisuración ELS | 1.55 | NO | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT5 | tensiones ELS | 0.675 | sí | sigma_s <= 0.8 fyk (característica ELS01-08) | hog | ELS04 |
| VT5 | flecha | 0.161 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT6 | flexión ELU | 0.719 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT6 | cortante | 0.703 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT6 | disposiciones | 0.542 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT6 | fisuración ELS | 1.72 | NO | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT6 | tensiones ELS | 0.609 | sí | sigma_c <= 0.6 fck (característica ELS01-08) | sag | ELS04 |
| VT6 | flecha | 0.178 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VT7 | flexión ELU | 0.798 | sí | MEd <= MRd (hog) | cara pilote mar - vano | ELR08 |
| VT7 | cortante | 0.456 | sí | estribos V + suspensión alveoplaca (todas las ramas) | cara pilote mar - vano | ELR08 |
| VT7 | torsión | 0.906 | sí | M/MRd + ΣAsl,T(cordón)/As <= 1 | cara pilote mar - vano | ELR08 |
| VT7 | disposiciones | 0.958 | sí | st <= st,max = 0.75d <= 600 | todas |  |
| VT7 | fisuración ELS | 0 | sí | wk <= 0.1 mm (XS3, QP) | sag | QP(psi2=0.8) |
| VT7 | tensiones ELS | 0.654 | sí | sigma_s <= 0.8 fyk (característica ELS01-08) | hog | ELS04 |
| VT7 | flecha | 0.069 | sí | f activa (f total - f inst. PP) <= L/500 | vano | QP(psi2=0.8) |
| VBM | flexión ELU | 0.931 | sí | MEd <= MRd (hog) | tramo 1 cara der. (X=6.25) | ELR14 |
| VBM | cortante | 0.522 | sí | VEd(d) <= VRd,s | tramo 1 cara der. (X=6.25) | ELR14 |
| VBM | disposiciones | 0.855 | sí | s <= sl,max = 0.75d | todas |  |
| VBM | fisuración ELS | 3.063 | NO | wk <= 0.1 mm (XS3, QP) | hog | QP(psi2=0.8) |
| VBM | tensiones ELS | 0.771 | sí | sigma_c <= 0.6 fck (característica ELS01-08) | hog | ELS06 |
| VBM | flecha | 0.328 | sí | f activa (f total - f inst. PP) <= L/500 | tramo 1 | QP(psi2=0.8) |
| VBT | flexión ELU | 0.953 | sí | MEd <= MRd (hog) | tramo 6 cara izq. (X=32.75) | ELR08 |
| VBT | cortante | 0.547 | sí | VEd(d) <= VRd,s | tramo 6 cara izq. (X=32.75) | ELR08 |
| VBT | disposiciones | 0.855 | sí | s <= sl,max = 0.75d | todas |  |
| VBT | fisuración ELS | 3.083 | NO | wk <= 0.1 mm (XS3, QP) | hog | QP(psi2=0.8) |
| VBT | tensiones ELS | 0.789 | sí | sigma_c <= 0.6 fck (característica ELS01-08) | hog | ELS04 |
| VBT | flecha | 0.328 | sí | f activa (f total - f inst. PP) <= L/500 | tramo 1 | QP(psi2=0.8) |

## 3. Armadura necesaria / dispuesta (ELU, caso CE-ROM)

As,uls = armadura de tracción de cálculo (simple, CYPE 'Área Nec.'); As,req = max(As,uls, As,min CE).

| member | section | face | MEd_kNm | As_uls_cm2 | As_min_cm2 | As_req_cm2 | As_prov_cm2 | req_over_prov | combo |
|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | bottom | 12.377 | 0.594 | 8.07 | 8.07 | 18.85 | 0.428 | ELR17 |
| VT1 | cara pilote mar - voladizo | top | -58.572 | 2.823 | 7.42 | 7.42 | 15.708 | 0.472 | ELR08 |
| VT1 | cara pilote mar - vano | bottom | 23.448 | 1.127 | 8.07 | 8.07 | 18.85 | 0.428 | ELR17 |
| VT1 | cara pilote mar - vano | top | -316.328 | 15.673 | 7.42 | 15.67 | 15.708 | 0.998 | ELR08 |
| VT1 | cara pilote tierra - vano | bottom | 275.78 | 13.681 | 8.07 | 13.68 | 18.85 | 0.726 | ELR08 |
| VT1 | cara pilote tierra - vuelo | bottom | 6.906 | 0.331 | 8.07 | 8.07 | 18.85 | 0.428 | ELR14 |
| VT1 | vano: máx. positivo | bottom | 275.607 | 13.672 | 8.07 | 13.67 | 18.85 | 0.725 | ELR08 |
| VT1 | eje pilote mar (info, nudo rígido) | bottom | 24.622 | 1.183 | 8.07 | 1.18 | 18.85 | 0.063 | ELR17 |
| VT1 | eje pilote mar (info, nudo rígido) | top | -388.56 | 19.41 | 7.42 | 19.41 | 15.708 | 1.236 | ELR08 |
| VT1 | eje pilote tierra (info, nudo rígido) | bottom | 300.645 | 14.964 | 8.07 | 14.96 | 18.85 | 0.794 | ELR05 |
| VT1 | eje pilote tierra (info, nudo rígido) | top | -26.24 | 1.261 | 7.42 | 1.26 | 15.708 | 0.08 | ELR20 |
| VT2 | cara pilote mar - voladizo | top | -10.007 | 0.48 | 4.99 | 4.99 | 15.708 | 0.318 | ELR14 |
| VT2 | cara pilote mar - vano | top | -265.234 | 13.14 | 4.99 | 13.14 | 15.708 | 0.836 | ELR08 |
| VT2 | cara pilote tierra - vano | bottom | 261.388 | 13.222 | 6.25 | 13.22 | 21.991 | 0.601 | ELR08 |
| VT2 | cara pilote tierra - vano | top | -0.517 | 0.025 | 4.99 | 4.99 | 15.708 | 0.318 | ELR17 |
| VT2 | cara pilote tierra - vuelo | bottom | 5.15 | 0.247 | 6.25 | 6.25 | 21.991 | 0.284 | ELR20 |
| VT2 | vano: máx. positivo | bottom | 315.955 | 16.184 | 6.25 | 16.18 | 21.991 | 0.736 | ELR08 |
| VT2 | eje pilote mar (info, nudo rígido) | top | -373.323 | 18.767 | 4.99 | 18.77 | 15.708 | 1.195 | ELR08 |
| VT2 | eje pilote tierra (info, nudo rígido) | bottom | 276.082 | 14.012 | 6.25 | 14.01 | 21.991 | 0.637 | ELR05 |
| VT2 | eje pilote tierra (info, nudo rígido) | top | -67.299 | 3.251 | 4.99 | 3.25 | 15.708 | 0.207 | ELR20 |
| VT3 | cara pilote mar - voladizo | bottom | 10.594 | 0.509 | 6.25 | 6.25 | 21.991 | 0.284 | ELR17 |
| VT3 | cara pilote mar - voladizo | top | -63.43 | 3.063 | 4.99 | 4.99 | 15.708 | 0.318 | ELR08 |
| VT3 | cara pilote mar - vano | bottom | 20.346 | 0.979 | 6.25 | 6.25 | 21.991 | 0.284 | ELR17 |
| VT3 | cara pilote mar - vano | top | -302.775 | 15.075 | 4.99 | 15.07 | 15.708 | 0.96 | ELR08 |
| VT3 | cara pilote tierra - vano | bottom | 258.227 | 13.053 | 6.25 | 13.05 | 21.991 | 0.594 | ELR08 |
| VT3 | cara pilote tierra - vano | top | -0.524 | 0.025 | 4.99 | 4.99 | 15.708 | 0.318 | ELR17 |
| VT3 | cara pilote tierra - vuelo | bottom | 4.209 | 0.202 | 6.25 | 6.25 | 21.991 | 0.284 | ELR14 |
| VT3 | vano: máx. positivo | bottom | 292.696 | 14.912 | 6.25 | 14.91 | 21.991 | 0.678 | ELR08 |
| VT3 | eje pilote mar (info, nudo rígido) | bottom | 21.533 | 1.036 | 6.25 | 1.04 | 21.991 | 0.047 | ELR17 |
| VT3 | eje pilote mar (info, nudo rígido) | top | -406.383 | 20.523 | 4.99 | 20.52 | 15.708 | 1.307 | ELR08 |
| VT3 | eje pilote tierra (info, nudo rígido) | bottom | 276.635 | 14.042 | 6.25 | 14.04 | 21.991 | 0.639 | ELR05 |
| VT3 | eje pilote tierra (info, nudo rígido) | top | -61.836 | 2.985 | 4.99 | 2.99 | 15.708 | 0.19 | ELR20 |
| VT4 | cara pilote mar - voladizo | top | -9.561 | 0.459 | 4.99 | 4.99 | 15.708 | 0.318 | ELR14 |
| VT4 | cara pilote mar - vano | top | -256.243 | 12.679 | 4.99 | 12.68 | 15.708 | 0.807 | ELR08 |
| VT4 | cara pilote tierra - vano | bottom | 252.276 | 12.735 | 6.25 | 12.74 | 21.991 | 0.579 | ELR08 |
| VT4 | cara pilote tierra - vano | top | -0.554 | 0.026 | 4.99 | 4.99 | 15.708 | 0.318 | ELR17 |
| VT4 | cara pilote tierra - vuelo | bottom | 4.228 | 0.203 | 6.25 | 6.25 | 21.991 | 0.284 | ELR20 |
| VT4 | vano: máx. positivo | bottom | 298.463 | 15.226 | 6.25 | 15.23 | 21.991 | 0.692 | ELR08 |
| VT4 | eje pilote mar (info, nudo rígido) | top | -357.463 | 17.93 | 4.99 | 17.93 | 15.708 | 1.141 | ELR08 |
| VT4 | eje pilote tierra (info, nudo rígido) | bottom | 267.256 | 13.537 | 6.25 | 13.54 | 21.991 | 0.616 | ELR05 |
| VT4 | eje pilote tierra (info, nudo rígido) | top | -62.269 | 3.006 | 4.99 | 3.01 | 15.708 | 0.191 | ELR20 |
| VT5 | cara pilote mar - voladizo | bottom | 10.594 | 0.509 | 6.25 | 6.25 | 21.991 | 0.284 | ELR17 |
| VT5 | cara pilote mar - voladizo | top | -63.451 | 3.064 | 4.99 | 4.99 | 15.708 | 0.318 | ELR08 |
| VT5 | cara pilote mar - vano | bottom | 20.346 | 0.979 | 6.25 | 6.25 | 21.991 | 0.284 | ELR17 |
| VT5 | cara pilote mar - vano | top | -293.961 | 14.618 | 4.99 | 14.62 | 15.708 | 0.931 | ELR08 |
| VT5 | cara pilote tierra - vano | bottom | 249.45 | 12.585 | 6.25 | 12.58 | 21.991 | 0.572 | ELR08 |
| VT5 | cara pilote tierra - vano | top | -0.524 | 0.025 | 4.99 | 4.99 | 15.708 | 0.318 | ELR17 |
| VT5 | cara pilote tierra - vuelo | bottom | 4.209 | 0.202 | 6.25 | 6.25 | 21.991 | 0.284 | ELR14 |
| VT5 | vano: máx. positivo | bottom | 287.063 | 14.606 | 6.25 | 14.61 | 21.991 | 0.664 | ELR08 |
| VT5 | eje pilote mar (info, nudo rígido) | bottom | 21.533 | 1.036 | 6.25 | 1.04 | 21.991 | 0.047 | ELR17 |
| VT5 | eje pilote mar (info, nudo rígido) | top | -396.371 | 19.989 | 4.99 | 19.99 | 15.708 | 1.273 | ELR08 |
| VT5 | eje pilote tierra (info, nudo rígido) | bottom | 266.619 | 13.503 | 6.25 | 13.5 | 21.991 | 0.614 | ELR05 |
| VT5 | eje pilote tierra (info, nudo rígido) | top | -61.836 | 2.985 | 4.99 | 2.99 | 15.708 | 0.19 | ELR20 |
| VT6 | cara pilote mar - voladizo | top | -10.007 | 0.48 | 4.99 | 4.99 | 15.708 | 0.318 | ELR14 |
| VT6 | cara pilote mar - vano | top | -247.608 | 12.238 | 4.99 | 12.24 | 15.708 | 0.779 | ELR08 |
| VT6 | cara pilote tierra - vano | bottom | 243.839 | 12.286 | 6.25 | 12.29 | 21.991 | 0.559 | ELR08 |
| VT6 | cara pilote tierra - vano | top | -0.517 | 0.025 | 4.99 | 4.99 | 15.708 | 0.318 | ELR17 |
| VT6 | cara pilote tierra - vuelo | bottom | 5.15 | 0.247 | 6.25 | 6.25 | 21.991 | 0.284 | ELR20 |
| VT6 | vano: máx. positivo | bottom | 307.009 | 15.693 | 6.25 | 15.69 | 21.991 | 0.714 | ELR08 |
| VT6 | eje pilote mar (info, nudo rígido) | top | -353.294 | 17.711 | 4.99 | 17.71 | 15.708 | 1.128 | ELR08 |
| VT6 | eje pilote tierra (info, nudo rígido) | bottom | 256.06 | 12.937 | 6.25 | 12.94 | 21.991 | 0.588 | ELR05 |
| VT6 | eje pilote tierra (info, nudo rígido) | top | -67.299 | 3.251 | 4.99 | 3.25 | 15.708 | 0.207 | ELR20 |
| VT7 | cara pilote mar - voladizo | bottom | 12.377 | 0.594 | 8.07 | 8.07 | 18.85 | 0.428 | ELR17 |
| VT7 | cara pilote mar - voladizo | top | -58.624 | 2.826 | 7.42 | 7.42 | 15.708 | 0.472 | ELR08 |
| VT7 | cara pilote mar - vano | bottom | 23.448 | 1.127 | 8.07 | 8.07 | 18.85 | 0.428 | ELR17 |
| VT7 | cara pilote mar - vano | top | -289.416 | 14.297 | 7.42 | 14.3 | 15.708 | 0.91 | ELR08 |
| VT7 | cara pilote tierra - vano | bottom | 248.843 | 12.301 | 8.07 | 12.3 | 18.85 | 0.653 | ELR08 |
| VT7 | cara pilote tierra - vuelo | bottom | 6.906 | 0.331 | 8.07 | 8.07 | 18.85 | 0.428 | ELR14 |
| VT7 | vano: máx. positivo | bottom | 248.718 | 12.295 | 8.07 | 12.29 | 18.85 | 0.652 | ELR08 |
| VT7 | eje pilote mar (info, nudo rígido) | bottom | 24.622 | 1.183 | 8.07 | 1.18 | 18.85 | 0.063 | ELR17 |
| VT7 | eje pilote mar (info, nudo rígido) | top | -358.093 | 17.826 | 7.42 | 17.83 | 15.708 | 1.135 | ELR08 |
| VT7 | eje pilote tierra (info, nudo rígido) | bottom | 270.147 | 13.392 | 8.07 | 13.39 | 18.85 | 0.71 | ELR05 |
| VT7 | eje pilote tierra (info, nudo rígido) | top | -26.24 | 1.261 | 7.42 | 1.26 | 15.708 | 0.08 | ELR20 |
| VBM | tramo 1 cara izq. (X=0.40) | top | -20.984 | 2.137 | 1.5 | 2.14 | 4.021 | 0.532 | ELR20 |
| VBM | tramo 1 cara der. (X=6.25) | top | -37.525 | 3.943 | 1.5 | 3.94 | 4.021 | 0.981 | ELR14 |
| VBM | tramo 2 cara izq. (X=6.75) | top | -36.537 | 3.832 | 1.5 | 3.83 | 4.021 | 0.953 | ELR14 |
| VBM | tramo 2 cara der. (X=12.75) | top | -29.058 | 3.004 | 1.5 | 3 | 4.021 | 0.747 | ELR20 |
| VBM | tramo 3 cara izq. (X=13.25) | top | -29.887 | 3.094 | 1.5 | 3.09 | 4.021 | 0.769 | ELR20 |
| VBM | tramo 3 cara der. (X=19.25) | top | -31.547 | 3.276 | 1.5 | 3.28 | 4.021 | 0.815 | ELR14 |
| VBM | tramo 4 cara izq. (X=19.75) | top | -31.547 | 3.276 | 1.5 | 3.28 | 4.021 | 0.815 | ELR14 |
| VBM | tramo 4 cara der. (X=25.75) | top | -29.887 | 3.094 | 1.5 | 3.09 | 4.021 | 0.769 | ELR20 |
| VBM | tramo 5 cara izq. (X=26.25) | top | -29.058 | 3.004 | 1.5 | 3 | 4.021 | 0.747 | ELR20 |
| VBM | tramo 5 cara der. (X=32.25) | top | -36.537 | 3.832 | 1.5 | 3.83 | 4.021 | 0.953 | ELR14 |
| VBM | tramo 6 cara izq. (X=32.75) | top | -37.525 | 3.943 | 1.5 | 3.94 | 4.021 | 0.981 | ELR14 |
| VBM | tramo 6 cara der. (X=38.60) | top | -20.984 | 2.137 | 1.5 | 2.14 | 4.021 | 0.532 | ELR20 |
| VBM | tramo 1: máx. positivo | bottom | 18.544 | 1.881 | 1.5 | 1.88 | 4.021 | 0.468 | ELR20 |
| VBM | tramo 2: máx. positivo | bottom | 10.774 | 1.078 | 1.5 | 1.5 | 4.021 | 0.373 | ELR14 |
| VBM | tramo 3: máx. positivo | bottom | 12.145 | 1.218 | 1.5 | 1.5 | 4.021 | 0.373 | ELR14 |
| VBM | tramo 4: máx. positivo | bottom | 12.145 | 1.218 | 1.5 | 1.5 | 4.021 | 0.373 | ELR14 |
| VBM | tramo 5: máx. positivo | bottom | 10.774 | 1.078 | 1.5 | 1.5 | 4.021 | 0.373 | ELR14 |
| VBM | tramo 6: máx. positivo | bottom | 18.544 | 1.881 | 1.5 | 1.88 | 4.021 | 0.468 | ELR20 |
| VBT | tramo 1 cara izq. (X=0.40) | top | -21.572 | 2.2 | 1.5 | 2.2 | 4.021 | 0.547 | ELR08 |
| VBT | tramo 1 cara der. (X=6.25) | top | -38.254 | 4.025 | 1.5 | 4.03 | 4.021 | 1.001 | ELR08 |
| VBT | tramo 2 cara izq. (X=6.75) | top | -37.341 | 3.922 | 1.5 | 3.92 | 4.021 | 0.975 | ELR08 |
| VBT | tramo 2 cara der. (X=12.75) | top | -29.537 | 3.056 | 1.5 | 3.06 | 4.021 | 0.76 | ELR08 |
| VBT | tramo 3 cara izq. (X=13.25) | top | -30.525 | 3.164 | 1.5 | 3.16 | 4.021 | 0.787 | ELR08 |
| VBT | tramo 3 cara der. (X=19.25) | top | -32.235 | 3.352 | 1.5 | 3.35 | 4.021 | 0.834 | ELR08 |
| VBT | tramo 4 cara izq. (X=19.75) | top | -32.449 | 3.376 | 1.5 | 3.38 | 4.021 | 0.84 | ELR08 |
| VBT | tramo 4 cara der. (X=25.75) | top | -30.281 | 3.138 | 1.5 | 3.14 | 4.021 | 0.78 | ELR08 |
| VBT | tramo 5 cara izq. (X=26.25) | top | -29.721 | 3.076 | 1.5 | 3.08 | 4.021 | 0.765 | ELR08 |
| VBT | tramo 5 cara der. (X=32.25) | top | -37.061 | 3.89 | 1.5 | 3.89 | 4.021 | 0.967 | ELR08 |
| VBT | tramo 6 cara izq. (X=32.75) | top | -38.405 | 4.042 | 1.5 | 4.04 | 4.021 | 1.005 | ELR08 |
| VBT | tramo 6 cara der. (X=38.60) | top | -21.302 | 2.171 | 1.5 | 2.17 | 4.021 | 0.54 | ELR14 |
| VBT | tramo 1: máx. positivo | bottom | 18.63 | 1.89 | 1.5 | 1.89 | 4.021 | 0.47 | ELR08 |
| VBT | tramo 2: máx. positivo | bottom | 11.035 | 1.105 | 1.5 | 1.5 | 4.021 | 0.373 | ELR08 |
| VBT | tramo 3: máx. positivo | bottom | 12.379 | 1.242 | 1.5 | 1.5 | 4.021 | 0.373 | ELR08 |
| VBT | tramo 4: máx. positivo | bottom | 12.386 | 1.243 | 1.5 | 1.5 | 4.021 | 0.373 | ELR08 |
| VBT | tramo 5: máx. positivo | bottom | 11.016 | 1.103 | 1.5 | 1.5 | 4.021 | 0.373 | ELR08 |
| VBT | tramo 6: máx. positivo | bottom | 18.624 | 1.889 | 1.5 | 1.89 | 4.021 | 0.47 | ELR08 |

## 4. Fisuración (QP) y umbral de psi2

| case | member | section | pos_m | check | M_kNm | demand | capacity | eta | ok | sigma_s | sr_max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CYPE | VT1 | sag | 1.725 | sigma_ct <= fctm (QP) | 47.998 | 0.981 | 3.21 | 0.306 | sí |  |  |
| CYPE | VT1 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 47.998 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT1 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.549 | 0.035 | 3.21 | 0.011 | sí |  |  |
| CYPE | VT1 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.549 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT1 | sag | 3.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 91.921 | 1.879 | 3.21 | 0.585 | sí |  |  |
| CYPE | VT1 | sag | 3.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 91.921 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT1 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -105.613 | 2.356 | 3.21 | 0.734 | sí |  |  |
| CYPE | VT1 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -105.613 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT2 | sag | 1.725 | sigma_ct <= fctm (QP) | 90.413 | 2.317 | 3.21 | 0.722 | sí |  |  |
| CYPE | VT2 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 90.413 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT2 | hog | -0.2 | sigma_ct <= fctm (QP) | -4.133 | 0.133 | 3.21 | 0.041 | sí |  |  |
| CYPE | VT2 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -4.133 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT2 | sag | 2.462 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 108.618 | 2.784 | 3.21 | 0.867 | sí |  |  |
| CYPE | VT2 | sag | 2.462 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 108.618 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT2 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -88.596 | 2.849 | 3.21 | 0.887 | sí |  |  |
| CYPE | VT2 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -88.596 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT3 | sag | 1.725 | sigma_ct <= fctm (QP) | 81.683 | 2.094 | 3.21 | 0.652 | sí |  |  |
| CYPE | VT3 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 81.683 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT3 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.739 | 0.12 | 3.21 | 0.037 | sí |  |  |
| CYPE | VT3 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.739 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT3 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 100.224 | 2.569 | 3.21 | 0.8 | sí |  |  |
| CYPE | VT3 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 100.224 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT3 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -101.104 | 3.251 | 3.21 | 1.013 | NO |  |  |
| CYPE | VT3 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -101.104 | 0.155 | 0.1 | 1.547 | NO | 140.452 | 367.23 |
| CYPE | VT4 | sag | 1.725 | sigma_ct <= fctm (QP) | 83.428 | 2.138 | 3.21 | 0.666 | sí |  |  |
| CYPE | VT4 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 83.428 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT4 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.956 | 0.127 | 3.21 | 0.04 | sí |  |  |
| CYPE | VT4 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.956 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT4 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 102.177 | 2.619 | 3.21 | 0.816 | sí |  |  |
| CYPE | VT4 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 102.177 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT4 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -85.634 | 2.754 | 3.21 | 0.858 | sí |  |  |
| CYPE | VT4 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -85.634 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT5 | sag | 1.725 | sigma_ct <= fctm (QP) | 81.683 | 2.094 | 3.21 | 0.652 | sí |  |  |
| CYPE | VT5 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 81.683 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT5 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.739 | 0.12 | 3.21 | 0.037 | sí |  |  |
| CYPE | VT5 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.739 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT5 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 98.346 | 2.521 | 3.21 | 0.785 | sí |  |  |
| CYPE | VT5 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 98.346 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT5 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -98.179 | 3.157 | 3.21 | 0.984 | sí |  |  |
| CYPE | VT5 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -98.179 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT6 | sag | 1.725 | sigma_ct <= fctm (QP) | 90.413 | 2.317 | 3.21 | 0.722 | sí |  |  |
| CYPE | VT6 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 90.413 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT6 | hog | -0.2 | sigma_ct <= fctm (QP) | -4.133 | 0.133 | 3.21 | 0.041 | sí |  |  |
| CYPE | VT6 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -4.133 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT6 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 106.725 | 2.736 | 3.21 | 0.852 | sí |  |  |
| CYPE | VT6 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 106.725 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT6 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -82.746 | 2.661 | 3.21 | 0.829 | sí |  |  |
| CYPE | VT6 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -82.746 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT7 | sag | 1.725 | sigma_ct <= fctm (QP) | 47.998 | 0.981 | 3.21 | 0.306 | sí |  |  |
| CYPE | VT7 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 47.998 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT7 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.549 | 0.035 | 3.21 | 0.011 | sí |  |  |
| CYPE | VT7 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.549 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT7 | sag | 3.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 82.958 | 1.696 | 3.21 | 0.528 | sí |  |  |
| CYPE | VT7 | sag | 3.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 82.958 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VT7 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -96.658 | 2.156 | 3.21 | 0.672 | sí |  |  |
| CYPE | VT7 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -96.658 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VBM | sag | 3 | sigma_ct <= fctm (QP) | 6.604 | 1.668 | 3.21 | 0.52 | sí |  |  |
| CYPE | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) | 6.604 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VBM | hog | 6.25 | sigma_ct <= fctm (QP) | -13.534 | 3.419 | 3.21 | 1.065 | NO |  |  |
| CYPE | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -13.534 | 0.156 | 0.1 | 1.559 | NO | 156.581 | 331.873 |
| CYPE | VBM | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 6.608 | 1.669 | 3.21 | 0.52 | sí |  |  |
| CYPE | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 6.608 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VBM | hog | 6.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -13.644 | 3.446 | 3.21 | 1.074 | NO |  |  |
| CYPE | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -13.644 | 0.157 | 0.1 | 1.572 | NO | 157.857 | 331.873 |
| CYPE | VBT | sag | 3 | sigma_ct <= fctm (QP) | 6.603 | 1.668 | 3.21 | 0.52 | sí |  |  |
| CYPE | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) | 6.603 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VBT | hog | 6.25 | sigma_ct <= fctm (QP) | -13.598 | 3.435 | 3.21 | 1.07 | NO |  |  |
| CYPE | VBT | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -13.598 | 0.157 | 0.1 | 1.566 | NO | 157.328 | 331.873 |
| CYPE | VBT | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 6.635 | 1.676 | 3.21 | 0.522 | sí |  |  |
| CYPE | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 6.635 | 0 | 0.1 | 0 | sí |  |  |
| CYPE | VBT | hog | 32.75 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -13.944 | 3.522 | 3.21 | 1.097 | NO |  |  |
| CYPE | VBT | hog | 32.75 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -13.944 | 0.161 | 0.1 | 1.606 | NO | 161.323 | 331.873 |
| CE-CYPE | VT1 | sag | 1.725 | sigma_ct <= fctm (QP) | 47.998 | 0.981 | 3.21 | 0.306 | sí |  |  |
| CE-CYPE | VT1 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 47.998 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT1 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.549 | 0.035 | 3.21 | 0.011 | sí |  |  |
| CE-CYPE | VT1 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.549 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT1 | sag | 3.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 91.921 | 1.879 | 3.21 | 0.585 | sí |  |  |
| CE-CYPE | VT1 | sag | 3.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 91.921 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT1 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -105.613 | 2.356 | 3.21 | 0.734 | sí |  |  |
| CE-CYPE | VT1 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -105.613 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT2 | sag | 1.725 | sigma_ct <= fctm (QP) | 90.413 | 2.317 | 3.21 | 0.722 | sí |  |  |
| CE-CYPE | VT2 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 90.413 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT2 | hog | -0.2 | sigma_ct <= fctm (QP) | -4.133 | 0.133 | 3.21 | 0.041 | sí |  |  |
| CE-CYPE | VT2 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -4.133 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT2 | sag | 2.462 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 108.618 | 2.784 | 3.21 | 0.867 | sí |  |  |
| CE-CYPE | VT2 | sag | 2.462 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 108.618 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT2 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -88.596 | 2.849 | 3.21 | 0.887 | sí |  |  |
| CE-CYPE | VT2 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -88.596 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT3 | sag | 1.725 | sigma_ct <= fctm (QP) | 81.683 | 2.094 | 3.21 | 0.652 | sí |  |  |
| CE-CYPE | VT3 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 81.683 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT3 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.739 | 0.12 | 3.21 | 0.037 | sí |  |  |
| CE-CYPE | VT3 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.739 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT3 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 100.224 | 2.569 | 3.21 | 0.8 | sí |  |  |
| CE-CYPE | VT3 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 100.224 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT3 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -101.104 | 3.251 | 3.21 | 1.013 | NO |  |  |
| CE-CYPE | VT3 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -101.104 | 0.155 | 0.1 | 1.547 | NO | 140.452 | 367.23 |
| CE-CYPE | VT4 | sag | 1.725 | sigma_ct <= fctm (QP) | 83.428 | 2.138 | 3.21 | 0.666 | sí |  |  |
| CE-CYPE | VT4 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 83.428 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT4 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.956 | 0.127 | 3.21 | 0.04 | sí |  |  |
| CE-CYPE | VT4 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.956 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT4 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 102.177 | 2.619 | 3.21 | 0.816 | sí |  |  |
| CE-CYPE | VT4 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 102.177 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT4 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -85.634 | 2.754 | 3.21 | 0.858 | sí |  |  |
| CE-CYPE | VT4 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -85.634 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT5 | sag | 1.725 | sigma_ct <= fctm (QP) | 81.683 | 2.094 | 3.21 | 0.652 | sí |  |  |
| CE-CYPE | VT5 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 81.683 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT5 | hog | -0.2 | sigma_ct <= fctm (QP) | -3.739 | 0.12 | 3.21 | 0.037 | sí |  |  |
| CE-CYPE | VT5 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -3.739 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT5 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 98.346 | 2.521 | 3.21 | 0.785 | sí |  |  |
| CE-CYPE | VT5 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 98.346 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT5 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -98.179 | 3.157 | 3.21 | 0.984 | sí |  |  |
| CE-CYPE | VT5 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -98.179 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT6 | sag | 1.725 | sigma_ct <= fctm (QP) | 90.413 | 2.317 | 3.21 | 0.722 | sí |  |  |
| CE-CYPE | VT6 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 90.413 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT6 | hog | -0.2 | sigma_ct <= fctm (QP) | -4.133 | 0.133 | 3.21 | 0.041 | sí |  |  |
| CE-CYPE | VT6 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -4.133 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT6 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 106.725 | 2.736 | 3.21 | 0.852 | sí |  |  |
| CE-CYPE | VT6 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 106.725 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT6 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -82.746 | 2.661 | 3.21 | 0.829 | sí |  |  |
| CE-CYPE | VT6 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -82.746 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT7 | sag | 1.725 | sigma_ct <= fctm (QP) | 47.998 | 0.981 | 3.21 | 0.306 | sí |  |  |
| CE-CYPE | VT7 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 47.998 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT7 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.549 | 0.035 | 3.21 | 0.011 | sí |  |  |
| CE-CYPE | VT7 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.549 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT7 | sag | 3.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 82.958 | 1.696 | 3.21 | 0.528 | sí |  |  |
| CE-CYPE | VT7 | sag | 3.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 82.958 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VT7 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -96.658 | 2.156 | 3.21 | 0.672 | sí |  |  |
| CE-CYPE | VT7 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -96.658 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VBM | sag | 3 | sigma_ct <= fctm (QP) | 6.604 | 1.668 | 3.21 | 0.52 | sí |  |  |
| CE-CYPE | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) | 6.604 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VBM | hog | 6.25 | sigma_ct <= fctm (QP) | -13.534 | 3.419 | 3.21 | 1.065 | NO |  |  |
| CE-CYPE | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -13.534 | 0.156 | 0.1 | 1.559 | NO | 156.581 | 331.873 |
| CE-CYPE | VBM | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 6.608 | 1.669 | 3.21 | 0.52 | sí |  |  |
| CE-CYPE | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 6.608 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VBM | hog | 6.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -13.644 | 3.446 | 3.21 | 1.074 | NO |  |  |
| CE-CYPE | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -13.644 | 0.157 | 0.1 | 1.572 | NO | 157.857 | 331.873 |
| CE-CYPE | VBT | sag | 3 | sigma_ct <= fctm (QP) | 6.603 | 1.668 | 3.21 | 0.52 | sí |  |  |
| CE-CYPE | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) | 6.603 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VBT | hog | 6.25 | sigma_ct <= fctm (QP) | -13.598 | 3.435 | 3.21 | 1.07 | NO |  |  |
| CE-CYPE | VBT | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -13.598 | 0.157 | 0.1 | 1.566 | NO | 157.328 | 331.873 |
| CE-CYPE | VBT | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 6.635 | 1.676 | 3.21 | 0.522 | sí |  |  |
| CE-CYPE | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 6.635 | 0 | 0.1 | 0 | sí |  |  |
| CE-CYPE | VBT | hog | 32.75 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -13.944 | 3.522 | 3.21 | 1.097 | NO |  |  |
| CE-CYPE | VBT | hog | 32.75 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -13.944 | 0.161 | 0.1 | 1.606 | NO | 161.323 | 331.873 |
| CE-ROM | VT1 | sag | 1.725 | sigma_ct <= fctm (QP) | 76.116 | 1.556 | 3.21 | 0.485 | sí |  |  |
| CE-ROM | VT1 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 76.116 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT1 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.868 | 0.042 | 3.21 | 0.013 | sí |  |  |
| CE-ROM | VT1 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.868 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT1 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 101.011 | 2.065 | 3.21 | 0.643 | sí |  |  |
| CE-ROM | VT1 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 101.011 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT1 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -105.682 | 2.358 | 3.21 | 0.735 | sí |  |  |
| CE-ROM | VT1 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -105.682 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT2 | sag | 1.725 | sigma_ct <= fctm (QP) | 151.895 | 3.893 | 3.21 | 1.213 | NO |  |  |
| CE-ROM | VT2 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 151.895 | 0.172 | 0.1 | 1.72 | NO | 153.038 | 374.687 |
| CE-ROM | VT2 | hog | -0.2 | sigma_ct <= fctm (QP) | -5.941 | 0.191 | 3.21 | 0.059 | sí |  |  |
| CE-ROM | VT2 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -5.941 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT2 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 164.026 | 4.204 | 3.21 | 1.31 | NO |  |  |
| CE-ROM | VT2 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 164.026 | 0.186 | 0.1 | 1.858 | NO | 165.26 | 374.687 |
| CE-ROM | VT2 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -89.608 | 2.881 | 3.21 | 0.898 | sí |  |  |
| CE-ROM | VT2 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -89.608 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT3 | sag | 1.725 | sigma_ct <= fctm (QP) | 136.846 | 3.508 | 3.21 | 1.093 | NO |  |  |
| CE-ROM | VT3 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 136.846 | 0.155 | 0.1 | 1.55 | NO | 137.876 | 374.687 |
| CE-ROM | VT3 | hog | -0.2 | sigma_ct <= fctm (QP) | -5.289 | 0.17 | 3.21 | 0.053 | sí |  |  |
| CE-ROM | VT3 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -5.289 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT3 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 145.963 | 3.741 | 3.21 | 1.166 | NO |  |  |
| CE-ROM | VT3 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 145.963 | 0.165 | 0.1 | 1.653 | NO | 147.061 | 374.687 |
| CE-ROM | VT3 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -101.903 | 3.277 | 3.21 | 1.021 | NO |  |  |
| CE-ROM | VT3 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -101.903 | 0.156 | 0.1 | 1.56 | NO | 141.562 | 367.23 |
| CE-ROM | VT4 | sag | 1.725 | sigma_ct <= fctm (QP) | 139.833 | 3.584 | 3.21 | 1.117 | NO |  |  |
| CE-ROM | VT4 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 139.833 | 0.158 | 0.1 | 1.584 | NO | 140.885 | 374.687 |
| CE-ROM | VT4 | hog | -0.2 | sigma_ct <= fctm (QP) | -5.66 | 0.182 | 3.21 | 0.057 | sí |  |  |
| CE-ROM | VT4 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -5.66 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT4 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 152.275 | 3.903 | 3.21 | 1.216 | NO |  |  |
| CE-ROM | VT4 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 152.275 | 0.172 | 0.1 | 1.724 | NO | 153.42 | 374.687 |
| CE-ROM | VT4 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -86.579 | 2.784 | 3.21 | 0.867 | sí |  |  |
| CE-ROM | VT4 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -86.579 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT5 | sag | 1.725 | sigma_ct <= fctm (QP) | 136.846 | 3.508 | 3.21 | 1.093 | NO |  |  |
| CE-ROM | VT5 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 136.846 | 0.155 | 0.1 | 1.55 | NO | 137.876 | 374.687 |
| CE-ROM | VT5 | hog | -0.2 | sigma_ct <= fctm (QP) | -5.289 | 0.17 | 3.21 | 0.053 | sí |  |  |
| CE-ROM | VT5 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -5.289 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT5 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 145.025 | 3.717 | 3.21 | 1.158 | NO |  |  |
| CE-ROM | VT5 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 145.025 | 0.164 | 0.1 | 1.642 | NO | 146.117 | 374.687 |
| CE-ROM | VT5 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -98.978 | 3.183 | 3.21 | 0.992 | sí |  |  |
| CE-ROM | VT5 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -98.978 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT6 | sag | 1.725 | sigma_ct <= fctm (QP) | 151.895 | 3.893 | 3.21 | 1.213 | NO |  |  |
| CE-ROM | VT6 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 151.895 | 0.172 | 0.1 | 1.72 | NO | 153.038 | 374.687 |
| CE-ROM | VT6 | hog | -0.2 | sigma_ct <= fctm (QP) | -5.941 | 0.191 | 3.21 | 0.059 | sí |  |  |
| CE-ROM | VT6 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -5.941 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT6 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 162.149 | 4.156 | 3.21 | 1.295 | NO |  |  |
| CE-ROM | VT6 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 162.149 | 0.184 | 0.1 | 1.836 | NO | 163.369 | 374.687 |
| CE-ROM | VT6 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -83.758 | 2.693 | 3.21 | 0.839 | sí |  |  |
| CE-ROM | VT6 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -83.758 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT7 | sag | 1.725 | sigma_ct <= fctm (QP) | 76.116 | 1.556 | 3.21 | 0.485 | sí |  |  |
| CE-ROM | VT7 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 76.116 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT7 | hog | -0.2 | sigma_ct <= fctm (QP) | -1.868 | 0.042 | 3.21 | 0.013 | sí |  |  |
| CE-ROM | VT7 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | -1.868 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT7 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 95.23 | 1.947 | 3.21 | 0.607 | sí |  |  |
| CE-ROM | VT7 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 95.23 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VT7 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -96.727 | 2.158 | 3.21 | 0.672 | sí |  |  |
| CE-ROM | VT7 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -96.727 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VBM | sag | 3 | sigma_ct <= fctm (QP) | 10.996 | 2.778 | 3.21 | 0.865 | sí |  |  |
| CE-ROM | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) | 10.996 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VBM | hog | 6.25 | sigma_ct <= fctm (QP) | -22.175 | 5.601 | 3.21 | 1.745 | NO |  |  |
| CE-ROM | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -22.175 | 0.306 | 0.1 | 3.063 | NO | 256.558 | 331.873 |
| CE-ROM | VBM | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 10.999 | 2.778 | 3.21 | 0.866 | sí |  |  |
| CE-ROM | VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 10.999 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VBM | hog | 6.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -22.285 | 5.629 | 3.21 | 1.754 | NO |  |  |
| CE-ROM | VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -22.285 | 0.308 | 0.1 | 3.084 | NO | 257.833 | 331.873 |
| CE-ROM | VBT | sag | 3 | sigma_ct <= fctm (QP) | 10.997 | 2.778 | 3.21 | 0.865 | sí |  |  |
| CE-ROM | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) | 10.997 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VBT | hog | 6.25 | sigma_ct <= fctm (QP) | -22.279 | 5.628 | 3.21 | 1.753 | NO |  |  |
| CE-ROM | VBT | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | -22.279 | 0.308 | 0.1 | 3.083 | NO | 257.765 | 331.873 |
| CE-ROM | VBT | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 11.028 | 2.786 | 3.21 | 0.868 | sí |  |  |
| CE-ROM | VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 11.028 | 0 | 0.1 | 0 | sí |  |  |
| CE-ROM | VBT | hog | 32.75 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | -22.624 | 5.715 | 3.21 | 1.78 | NO |  |  |
| CE-ROM | VBT | hog | 32.75 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | -22.624 | 0.315 | 0.1 | 3.15 | NO | 261.76 | 331.873 |

Umbral de psi2,Qa con la armadura dispuesta (TB psi2 = 0):

| member | face | Mcr_kNm | M_qp_03 | M_qp_08 | psi2_crack_fctm | psi2_crack_fctm_fl | psi2_wk_fail |
|---|---|---|---|---|---|---|---|
| VT1 | bottom | 157.03 | 48 | 76.12 |  |  |  |
| VT1 | top | 143.89 | -1.55 | -1.87 |  |  |  |
| VT2 | bottom | 125.23 | 90.41 | 151.9 | 0.583 | 0.634 | 0.583 |
| VT2 | top | 99.83 | -4.13 | -5.94 |  |  |  |
| VT3 | bottom | 125.23 | 81.68 | 136.85 | 0.695 | 0.751 | 0.695 |
| VT3 | top | 99.83 | -3.74 | -5.29 |  |  |  |
| VT4 | bottom | 125.23 | 83.43 | 139.83 | 0.671 | 0.726 | 0.671 |
| VT4 | top | 99.83 | -3.96 | -5.66 |  |  |  |
| VT5 | bottom | 125.23 | 81.68 | 136.85 | 0.695 | 0.751 | 0.695 |
| VT5 | top | 99.83 | -3.74 | -5.29 |  |  |  |
| VT6 | bottom | 125.23 | 90.41 | 151.9 | 0.583 | 0.634 | 0.583 |
| VT6 | top | 99.83 | -4.13 | -5.94 |  |  |  |
| VT7 | bottom | 157.03 | 48 | 76.12 |  |  |  |
| VT7 | top | 143.89 | -1.55 | -1.87 |  |  |  |
| VBM | bottom | 12.71 | 6.6 | 11 | 0.995 |  | 0.995 |
| VBM | top | 12.71 | -13.53 | -22.17 | 0.252 | 0.473 | 0.252 |
| VBT | bottom | 12.71 | 6.6 | 11 | 0.995 |  | 0.995 |
| VBT | top | 12.71 | -13.6 | -22.28 | 0.249 | 0.468 | 0.249 |

## 5. Propuesta de armado (caso final)

### inner (ejes 2-6, pórticos 4-8)

- **bottom**: dispuesto 7Ø20 (eta 1.72) -> **8Ø20 alma + 4Ø16 alas** (eta 0.962), wk = 0.096 mm
- **top**: dispuesto 5Ø20 (eta 0.878) -> sin cambio
- **stirrups**: dispuesto 3 ramas Ø10/100 (1e+1r) (eta 0.717) -> sin cambio
- peso armadura longitudinal: 32.06 -> 40.84 kg/m
- verificación con la propuesta: VT2: CUMPLE, VT3: CUMPLE, VT4: CUMPLE, VT5: CUMPLE, VT6: CUMPLE

### end (ejes 1 y 7, pórticos 3 y 9)

- **bottom**: dispuesto 6Ø20 (eta 0.729) -> sin cambio
- **top**: dispuesto 5Ø20 (eta 0.973) -> sin cambio
- **stirrups**: dispuesto 3 ramas Ø10/100 (1e+1r) (eta 0.958) -> sin cambio
- peso armadura longitudinal: 30.83 -> 30.83 kg/m
- verificación con la propuesta: VT1: CUMPLE, VT7: CUMPLE

### end (ejes 1 y 7, pórticos 3 y 9) + torsión del ala (sensibilidad)

- **bottom**: dispuesto 6Ø20 (eta 0.906) -> sin cambio
- **top**: dispuesto 5Ø20 (eta 1.185) -> **4Ø25** (eta 0.982), wk = 0.0 mm
- **stirrups**: dispuesto 3 ramas Ø10/100 (1e+1r) (eta 0.963) -> sin cambio
- peso armadura longitudinal: 30.83 -> 33.91 kg/m
- eta máx. de las filas de sensibilidad con la propuesta: {'VT1': 0.982, 'VT7': 0.926}
- nota: sensitivity, not the verdict: SAP torque + equilibrium torque of the hollow-core plates bearing on the single ledge (e = 0.42 m from the pile axis, T = q·Lp/2·e·L/2 = 56 kN·m at the pile faces for 1.35G + 1.5Qa); CYPE P437 assumes no torsion

### edge (pórticos 1 y 10)

- **bottom**: dispuesto 2Ø16 (eta 0.462) -> sin cambio
- **top**: dispuesto 2Ø16 (eta 3.083) -> **3Ø25** (eta 0.847), wk = 0.067 mm
- **stirrups**: dispuesto 2 ramas Ø8/150 (1e) (eta 0.871) -> sin cambio
- peso armadura longitudinal: 6.31 -> 14.72 kg/m
- verificación con la propuesta: VBM: CUMPLE, VBT: CUMPLE

## 6. Comparación con CYPE (Anejo 10)

| quantity | ours | cype | diff_pct | status | src | note |
|---|---|---|---|---|---|---|
| P3-P4 MRd,x (hogging, Mode.CYPE) | -325.781 | -325.78 | 0 | PASS | P369 table: MRd,x |  |
| P3-P4 neutral-axis depth x (figure image112) | 68.519 | 68.52 | -0 | PASS | P381 figure image112 |  |
| P3-P4 Cc at ultimate | 766.996 | 767 | -0 | PASS | P384 table |  |
| P3-P4 eta N,M = 273.71/MRd | 0.84 | 0.84 | 0.02 | PASS | P369 table: η |  |
| P3-P4 z = 0.9 d | 432 | 432 | 0 | PASS | P364 table: [Esfuerzo cortante de agotamiento por compresión oblicua e...] z |  |
| P3-P4 VRd,max (theta 45) | 1512.0 | 1512.0 | 0 | PASS | P364 table: [Se debe satisfacer] VRd,max,Vy |  |
| P3-P4 VRd,s (3 legs Ø10/100, fywd 400) | 407.15 | 407.15 | 0 | PASS | P364 table: [Se debe satisfacer] VRd,s,Vy |  |
| P3-P4 eta VEd/VRd,s (VEd = 390.18) | 0.958 | 0.958 | 0.03 | PASS | P364 table: [Se debe satisfacer] η (occurrence 2) |  |
| P3-P4 eta VEd/VRd,max | 0.258 | 0.258 | 0.02 | PASS | P364 table: [Se debe satisfacer] η (occurrence 1) |  |
| P3-P4 'Área Transv. Nec.' = VEd/(z fywd) [cm2/m] | 22.58 | 22.58 | -0 | PASS | listing P1620 table, Pórtico 4 P3-P4 1/3L |  |
| As,min top (z = 0.9d = 432, CYPE C14) [cm2] | 5.085 | 5.09 | -0.09 | PASS | P359 table: As,min |  |
| W top (gross) [cm3] | 28339.4 | 28339.3 | 0 | PASS | P359 table: W |  |
| As,min top with z = 0.8h (CE text) [cm2] | 4.993 | 5.09 | -1.91 | INFO | A19.9.2.1.1(1) | code-strict alternative (-1.8 %) |
| As,min bottom (z = 0.9d) [cm2] | 6.369 | 6.37 | -0.01 | PASS | listing P1626 table, Pórtico 5 P11-P5 As_bot_nec (M > 0 exists, As,min governs) |  |
| 'Área Inf. Nec.' Mmax = 294.61 [cm2] | 15.101 | 15.1 | 0.01 | PASS | listing P1620 table 2/3L |  |
| 'Área Sup. Nec.' M(P3) = -273.71 [cm2] | 13.725 | 13.72 | 0.04 | PASS | listing P1620 table 1/3L (node moment, C20) |  |
| rho_w,min·bw (50 cm web) [cm2/m] | 4.733 | 4.73 | 0.06 | PASS | listing 'Nec.' minimum links |  |
| rho_w,min·bw (25 cm edge beam) [cm2/m] | 2.366 | 2.37 | -0.15 | PASS | listing Pórtico 10 'Nec.' |  |
| sl,max = 0.75 d [mm] | 360 | 360 | 0 | PASS | P364 table: check 1 right |  |
| st,max = 0.75 d [mm] | 360 | 360 | 0 | PASS | P364 table: check 2 right |  |
| clear spacing top bars [mm] | 62.5 | 63 | -0.79 | PASS | P352 table |  |
| max bar spacing bottom [mm] | 150 | 150 | 0 | PASS | P352 table (sb) |  |
| sigma_ct bottom at M_qp = 86 kN·m (hand check) [MPa] | -2.205 | -2.2 | 0.22 | PASS | P575 / image118 | homogenised n = Es/Ecm = 6.52, bars 5Ø20 + 7Ø20 |
| Mcr,sag (fctm, homogenised) [kN·m] | 125.209 | 125.21 | -0 | PASS | validate_codigo K.05 (no CYPE print) |  |
| Mcr,hog (fctm, homogenised) [kN·m] | 99.838 | 99.84 | -0 | PASS | validate_codigo K.06 (no CYPE print) |  |
| fT,lim = L/250 (L = 3.05) [mm] | 12.2 | 12.2 | 0 | PASS | P583 table |  |
| fA,lim = L/500 [mm] | 6.1 | 6.1 | 0 | PASS | P581 table |  |
| wk at M = 151.9 (psi2 0.8, SAP) [mm], bars 5Ø20+7Ø20 | 0.18 | 0.18 | 0.02 | PASS | validate_codigo K.17 (research, no CYPE print) |  |
| wk at M = Mcr,sag [mm] | 0.149 | 0.149 | -0.03 | PASS | validate_codigo K.18 |  |
| Pórtico 3 'Área Sup. Nec.' node M = -318.8 [cm2] | 15.977 | 15.98 | -0.02 | PASS | P1614 table: column 'Tramo: P1-P2' zone 1/3L |  |
| Pórtico 3 'Área Inf. Nec.' M = 275.15 [cm2] | 13.799 | 13.8 | -0.01 | PASS | P1614 table: column 'Tramo: P1-P2' zone 3/3L |  |
| Pórtico 3 §4.3 N,M eta at the node (M = -318.8) [%] | 93.249 | 93.4 | -0.16 | PASS | P1813 table: P1 - P2 N,M | calibrates the end-frame bars at 235 mm (Ø20 active, 2Ø10 inactive) |
| Pórtico 9 'Área Sup. Nec.' node M = -291.23 [cm2] | 14.558 | 14.56 | -0.01 | PASS | P1650 table: column 'Tramo: P16-P18' zone 1/3L |  |
| Pórtico 9 'Área Inf. Nec.' M = 247.61 [cm2] | 12.381 | 12.38 | 0.01 | PASS | P1650 table: column 'Tramo: P16-P18' zone 3/3L |  |
| Pórtico 9 §4.3 N,M eta at the node (M = -291.23) [%] | 85.185 | 85.4 | -0.25 | PASS | P1813 table: P16 - P18 N,M | calibrates the end-frame bars at 235 mm (Ø20 active, 2Ø10 inactive) |
| Pórtico 3 P9-P1 Tc = T/TRd,max (T = 25.79, nu 0.6) [%] | 4.585 | 4.6 | -0.33 | PASS | P1813 table P9 - P1 Tc |  |
| Pórtico 3 P1-P2 Tc (T = 27.43) [%] | 4.876 | 4.9 | -0.48 | PASS | P1813 table P1 - P2 Tc |  |
| Pórtico 3 P9-P1 Tst = (T/(2 Ak fyd))/(Ø10/100) [%] | 15.316 | 15.3 | 0.1 | PASS | P1813 table P9 - P1 Tst |  |
| Pórtico 3 P9-P1 'Área Transv. Nec.' 1/3L = V/(z fywd) + 2 T/(2 Ak fyd) [cm2/m] | 8.281 | 8.28 | 0.02 | PASS | listing P1614 table |  |
| Pórtico 3 P9-P1 TRd,max with nu = 0.6(1 - fck/250) (CE) [kN·m] | 483.763 | 562.515 | -14 | INFO | A19.6.3.2(4) | code-strict nu = 0.516: TRd,max -14 % |
| VT1 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1614 table: column 'Tramo: P1-P2' zone 3/3L |  |
| VT1 As_bot_real (Área Real) | 18.85 | 18.85 | 0 | PASS | P1614 table: column 'Tramo: P1-P2' zone 3/3L |  |
| VT1 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1614 table: column 'Tramo: P1-P2' zone 3/3L |  |
| VT2 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1620 table: column 'Tramo: P3-P4' zone 3/3L |  |
| VT2 As_bot_real (Área Real) | 21.99 | 21.99 | 0 | PASS | P1620 table: column 'Tramo: P3-P4' zone 3/3L |  |
| VT2 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1620 table: column 'Tramo: P3-P4' zone 3/3L |  |
| VT3 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1626 table: column 'Tramo: P5-P6' zone 3/3L |  |
| VT3 As_bot_real (Área Real) | 21.99 | 21.99 | 0 | PASS | P1626 table: column 'Tramo: P5-P6' zone 3/3L |  |
| VT3 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1626 table: column 'Tramo: P5-P6' zone 3/3L |  |
| VT4 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1632 table: column 'Tramo: P7-P8' zone 3/3L |  |
| VT4 As_bot_real (Área Real) | 21.99 | 21.99 | 0 | PASS | P1632 table: column 'Tramo: P7-P8' zone 3/3L |  |
| VT4 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1632 table: column 'Tramo: P7-P8' zone 3/3L |  |
| VT5 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1638 table: column 'Tramo: P13-P14' zone 3/3L |  |
| VT5 As_bot_real (Área Real) | 21.99 | 21.99 | 0 | PASS | P1638 table: column 'Tramo: P13-P14' zone 3/3L |  |
| VT5 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1638 table: column 'Tramo: P13-P14' zone 3/3L |  |
| VT6 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1644 table: column 'Tramo: P15-P17' zone 3/3L |  |
| VT6 As_bot_real (Área Real) | 21.99 | 21.99 | 0 | PASS | P1644 table: column 'Tramo: P15-P17' zone 3/3L |  |
| VT6 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1644 table: column 'Tramo: P15-P17' zone 3/3L |  |
| VT7 As_top_real (Área Real) | 15.71 | 15.71 | 0 | PASS | P1650 table: column 'Tramo: P16-P18' zone 3/3L |  |
| VT7 As_bot_real (Área Real) | 18.85 | 18.85 | 0 | PASS | P1650 table: column 'Tramo: P16-P18' zone 3/3L |  |
| VT7 Asw_per_m_real (Área Real) | 23.56 | 23.56 | 0 | PASS | P1650 table: column 'Tramo: P16-P18' zone 3/3L |  |
| VBM As_top_real (Área Real) | 4.02 | 4.02 | 0 | PASS | P1608 table: column 'Tramo: P9-P20' zone 1/3L |  |
| VBM As_bot_real (Área Real) | 4.02 | 4.02 | 0 | PASS | P1608 table: column 'Tramo: P9-P20' zone 1/3L |  |
| VBM Asw_per_m_real (Área Real) | 6.7 | 6.7 | 0 | PASS | P1608 table: column 'Tramo: P9-P20' zone 1/3L |  |
| VBT As_top_real (Área Real) | 4.02 | 4.02 | 0 | PASS | P1656 table: column 'Tramo: P2-P4' zone 1/3L |  |
| VBT As_bot_real (Área Real) | 4.02 | 4.02 | 0 | PASS | P1656 table: column 'Tramo: P2-P4' zone 1/3L |  |
| VBT Asw_per_m_real (Área Real) | 6.7 | 6.7 | 0 | PASS | P1656 table: column 'Tramo: P2-P4' zone 1/3L |  |
| inner beams M_qp,max sag (psi2 0.3, SAP) [kN·m] | 90.41 | 90.41 | 0 | PASS | validate_codigo P.01 |  |
| inner beams M_qp,max sag (psi2 0.8, SAP) [kN·m] | 151.9 | 151.9 | 0 | PASS | validate_codigo P.03 |  |
| Pórtico 6 (VT4) M_qp,max (psi2 0.3) vs CYPE figure [kN·m] | 83.43 | 86.66 | -3.73 | INFO | P569 image117 (CYPE) | SAP vs CYPE model (-3.7 %) |
| psi2,Qa at which the inner beams crack (VT2, fctm) | 0.583 | 0.583 | 0 | PASS | validate_codigo P.06 | with 7Ø20 any cracked state fails wk <= 0.1 mm |
| idem with fct,eff = fctm,fl | 0.634 | 0.63 | 0.63 | PASS | validate_codigo P.06 note |  |
| VT1 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.306 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT1 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.011 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT2 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.722 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT2 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.041 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT3 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.652 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT3 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.037 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT4 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.666 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT4 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.04 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT5 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.652 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT5 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.037 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT6 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.722 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT6 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.041 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT7 sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.306 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VT7 hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.011 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VBM sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.52 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VBM hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 1.065 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | CRACKED (CYPE: not cracked) |
| VBT sag sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 0.52 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | uncracked |
| VBT hog sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)' | 1.07 |  |  | INFO | P1818-P1827 tables (all faces N.P.(1)) | CRACKED (CYPE: not cracked) |
| Pórtico 3 P1-P2 1/3L As_top_nec from the drawing node moment -318.8 [cm2] | 15.977 | 15.98 | -0.02 | PASS | P1614 table: column 'Tramo: P1-P2' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 4 P3-P4 1/3L As_top_nec from the drawing node moment -273.71 [cm2] | 13.725 | 13.72 | 0.04 | PASS | P1620 table: column 'Tramo: P3-P4' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 5 P5-P6 1/3L As_top_nec from the drawing node moment -312.87 [cm2] | 15.755 | 15.75 | 0.03 | PASS | P1626 table: column 'Tramo: P5-P6' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 6 P7-P8 1/3L As_top_nec from the drawing node moment -264.0 [cm2] | 13.224 | 13.22 | 0.03 | PASS | P1632 table: column 'Tramo: P7-P8' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 7 P13-P14 1/3L As_top_nec from the drawing node moment -303.83 [cm2] | 15.285 | 15.28 | 0.03 | PASS | P1638 table: column 'Tramo: P13-P14' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 8 P15-P17 1/3L As_top_nec from the drawing node moment -255.61 [cm2] | 12.792 | 12.79 | 0.02 | PASS | P1644 table: column 'Tramo: P15-P17' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| Pórtico 9 P16-P18 1/3L As_top_nec from the drawing node moment -291.23 [cm2] | 14.558 | 14.56 | -0.01 | PASS | P1650 table: column 'Tramo: P16-P18' zone 1/3L | CYPE sizes the support steel with the node moment (C20), not the zone value |
| listing §2 M: mean |diff| over 104 zone values [%] | 19.619 |  |  | INFO | tables.cype_listing_nec | median 14.1 %, max 93.3 % |
| listing §2 V: mean |diff| over 63 zone values [%] | 36.595 |  |  | INFO | tables.cype_listing_nec | median 26.9 %, max 108.7 % |
| listing §2 As: mean |diff| over 111 zone values [%] | 18.557 |  |  | INFO | tables.cype_listing_nec | median 8.7 %, max 100.0 % |
| listing §2 Asw: mean |diff| over 63 zone values [%] | 33.31 |  |  | INFO | tables.cype_listing_nec | median 15.4 %, max 126.8 % |
| listing §2 As Nec from CYPE's own zone M: mean |diff| over 104 [%] | 10.792 |  |  | INFO | tables.cype_listing_nec | median 1.76 %; exact where CYPE sizes with the zone moment |
| §4.3 P9-P1 N,M eta [%] | 17.034 | 80.5 | -78.84 | INFO | P1813 table: P9 - P1 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P9-P1 Q eta [%] | 32.69 | 25.8 | 26.71 | INFO | P1813 table: P9 - P1 Q |  |
| §4.3 P9-P1 Tc eta [%] | 7.77 | 4.6 | 68.91 | INFO | P1813 table: P9 - P1 Tc | SAP torsion is larger than CYPE's (edge-beam continuity) |
| §4.3 P9-P1 TVy eta [%] | 12.52 | 8 | 56.5 | INFO | P1813 table: P9 - P1 TVy |  |
| §4.3 P1-P2 N,M eta [%] | 92.257 | 93.4 | -1.22 | INFO | P1813 table: P1 - P2 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P1-P2 Q eta [%] | 72.11 | 72.3 | -0.26 | INFO | P1813 table: P1 - P2 Q |  |
| §4.3 P1-P2 Tc eta [%] | 4.82 | 4.9 | -1.63 | INFO | P1813 table: P1 - P2 Tc | SAP torsion is larger than CYPE's (edge-beam continuity) |
| §4.3 P1-P2 TVy eta [%] | 17.08 | 15.7 | 8.79 | INFO | P1813 table: P1 - P2 TVy |  |
| §4.3 P1-P2 fT,max [mm] | 0.302 | 0.27 | 11.85 | INFO | P1830 table: P1 - P2 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P10-P3 N,M eta [%] | 2.98 | 73.6 | -95.95 | INFO | P1813 table: P10 - P3 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P10-P3 Q eta [%] | 25.94 | 16.7 | 55.33 | INFO | P1813 table: P10 - P3 Q |  |
| §4.3 P3-P4 N,M eta [%] | 80.264 | 84 | -4.45 | INFO | P1813 table: P3 - P4 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P3-P4 Q eta [%] | 94.36 | 95.8 | -1.5 | INFO | P1813 table: P3 - P4 Q |  |
| §4.3 P3-P4 fT,max [mm] | 0.722 | 1.53 | -52.81 | INFO | P1830 table: P3 - P4 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P11-P5 N,M eta [%] | 18.982 | 94.4 | -79.89 | INFO | P1813 table: P11 - P5 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P11-P5 Q eta [%] | 37.91 | 32.3 | 17.37 | INFO | P1813 table: P11 - P5 Q |  |
| §4.3 P5-P6 N,M eta [%] | 91.868 | 96 | -4.3 | INFO | P1813 table: P5 - P6 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P5-P6 Q eta [%] | 92.27 | 92.3 | -0.03 | INFO | P1813 table: P5 - P6 Q |  |
| §4.3 P5-P6 fT,max [mm] | 0.653 | 1.17 | -44.19 | INFO | P1830 table: P5 - P6 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P12-P7 N,M eta [%] | 2.844 | 70.7 | -95.98 | INFO | P1813 table: P12 - P7 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P12-P7 Q eta [%] | 24.02 | 15.8 | 52.03 | INFO | P1813 table: P12 - P7 Q |  |
| §4.3 P7-P8 N,M eta [%] | 77.576 | 81 | -4.23 | INFO | P1813 table: P7 - P8 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P7-P8 Q eta [%] | 88.74 | 89.7 | -1.07 | INFO | P1813 table: P7 - P8 Q |  |
| §4.3 P7-P8 fT,max [mm] | 0.667 | 1.24 | -46.21 | INFO | P1830 table: P7 - P8 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P19-P13 N,M eta [%] | 18.988 | 92.3 | -79.43 | INFO | P1813 table: P19 - P13 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P19-P13 Q eta [%] | 37.91 | 32.3 | 17.37 | INFO | P1813 table: P19 - P13 Q |  |
| §4.3 P13-P14 N,M eta [%] | 89.174 | 93.3 | -4.42 | INFO | P1813 table: P13 - P14 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P13-P14 Q eta [%] | 90.84 | 90.9 | -0.07 | INFO | P1813 table: P13 - P14 Q |  |
| §4.3 P13-P14 fT,max [mm] | 0.653 | 1.17 | -44.19 | INFO | P1830 table: P13 - P14 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P21-P15 N,M eta [%] | 2.98 | 69.2 | -95.69 | INFO | P1813 table: P21 - P15 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P21-P15 Q eta [%] | 25.94 | 16.7 | 55.33 | INFO | P1813 table: P21 - P15 Q |  |
| §4.3 P15-P17 N,M eta [%] | 74.877 | 78.5 | -4.62 | INFO | P1813 table: P15 - P17 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P15-P17 Q eta [%] | 91.49 | 92.9 | -1.52 | INFO | P1813 table: P15 - P17 Q |  |
| §4.3 P15-P17 fT,max [mm] | 0.722 | 1.53 | -52.81 | INFO | P1830 table: P15 - P17 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P20-P16 N,M eta [%] | 17.049 | 78.6 | -78.31 | INFO | P1813 table: P20 - P16 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P20-P16 Q eta [%] | 32.69 | 25.8 | 26.71 | INFO | P1813 table: P20 - P16 Q |  |
| §4.3 P20-P16 Tc eta [%] | 7.77 | 4.6 | 68.91 | INFO | P1813 table: P20 - P16 Tc | SAP torsion is larger than CYPE's (edge-beam continuity) |
| §4.3 P20-P16 TVy eta [%] | 12.52 | 8 | 56.5 | INFO | P1813 table: P20 - P16 TVy |  |
| §4.3 P16-P18 N,M eta [%] | 84.399 | 85.4 | -1.17 | INFO | P1813 table: P16 - P18 N,M | ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced anchorage area near the bar ends, not modelled) |
| §4.3 P16-P18 Q eta [%] | 67.77 | 67.9 | -0.19 | INFO | P1813 table: P16 - P18 Q |  |
| §4.3 P16-P18 Tc eta [%] | 4.82 | 4.9 | -1.63 | INFO | P1813 table: P16 - P18 Tc | SAP torsion is larger than CYPE's (edge-beam continuity) |
| §4.3 P16-P18 TVy eta [%] | 16.69 | 15.1 | 10.53 | INFO | P1813 table: P16 - P18 TVy |  |
| §4.3 P16-P18 fT,max [mm] | 0.302 | 0.27 | 11.85 | INFO | P1830 table: P16 - P18 | ours: cracked-section integration, phi = 2.0, beta = 0.5 |
| §4.3 P9-P20 N,M eta [%] | 93.655 | 82.3 | 13.8 | INFO | P1813 table: P9 - P20 N,M |  |
| §4.3 P9-P20 Q eta [%] | 104.13 | 58.9 | 76.79 | INFO | P1813 table: P9 - P20 Q |  |
| §4.3 P2-P4 N,M eta [%] | 94.926 | 78.5 | 20.92 | INFO | P1813 table: P2 - P4 N,M |  |
| §4.3 P2-P4 Q eta [%] | 107.96 | 51.7 | 108.82 | INFO | P1813 table: P2 - P4 Q |  |
| §4.3 P4-P6 N,M eta [%] | 92.454 | 77.9 | 18.68 | INFO | P1815 table: P4 - P6 N,M |  |
| §4.3 P4-P6 Q eta [%] | 102.18 | 48.4 | 111.12 | INFO | P1815 table: P4 - P6 Q |  |
| §4.3 P6-P8 N,M eta [%] | 79.924 | 71 | 12.57 | INFO | P1815 table: P6 - P8 N,M |  |
| §4.3 P6-P8 Q eta [%] | 92.17 | 47.8 | 92.82 | INFO | P1815 table: P6 - P8 Q |  |
| §4.3 P8-P14 N,M eta [%] | 80.245 | 71 | 13.02 | INFO | P1815 table: P8 - P14 N,M |  |
| §4.3 P8-P14 Q eta [%] | 92.43 | 47.9 | 92.96 | INFO | P1815 table: P8 - P14 Q |  |
| §4.3 P14-P17 N,M eta [%] | 92.033 | 77.8 | 18.29 | INFO | P1815 table: P14 - P17 N,M |  |
| §4.3 P14-P17 Q eta [%] | 101.79 | 48.3 | 110.75 | INFO | P1815 table: P14 - P17 Q |  |
| §4.3 P17-P18 N,M eta [%] | 95.151 | 78.7 | 20.9 | INFO | P1813 table: P17 - P18 N,M |  |
| §4.3 P17-P18 Q eta [%] | 108.08 | 51.8 | 108.65 | INFO | P1813 table: P17 - P18 Q |  |

### Listado §2 por zona (fuerzas SAP, Mode.CYPE, base CYPE)

| quantity | ours | ours_from_cype_M | cype | diff_pct | diff_cypeM_pct |
|---|---|---|---|---|---|
| Pórtico 3 P9-P1 1/3L As_top_nec [cm2] | 7.556 | 7.56 | 11 | -31.31 | -31.31 |
| Pórtico 3 P9-P1 1/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 3 P9-P1 1/3L Asw_per_m_nec [cm2/m] | 11.614 |  | 8.28 | 40.27 |  |
| Pórtico 3 P9-P1 2/3L As_top_nec [cm2] | 7.556 | 7.56 | 11 | -31.31 | -31.31 |
| Pórtico 3 P9-P1 2/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 3 P9-P1 2/3L Asw_per_m_nec [cm2/m] | 11.663 |  | 8.38 | 39.17 |  |
| Pórtico 3 P9-P1 3/3L As_top_nec [cm2] | 7.556 | 7.56 | 11 | -31.31 | -31.31 |
| Pórtico 3 P9-P1 3/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 3 P9-P1 3/3L Asw_per_m_nec [cm2/m] | 11.844 |  | 8.47 | 39.84 |  |
| Pórtico 3 P1-P2 1/3L As_top_nec [cm2] | 15.843 | 15.81 | 15.98 | -0.86 | -1.09 |
| Pórtico 3 P1-P2 1/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 3 P1-P2 1/3L Asw_per_m_nec [cm2/m] | 16.99 |  | 17.04 | -0.3 |  |
| Pórtico 3 P1-P2 2/3L As_top_nec [cm2] | 7.556 | 7.56 | 7.96 | -5.08 | -5.08 |
| Pórtico 3 P1-P2 2/3L As_bot_nec [cm2] | 9.612 | 8.34 | 10.91 | -11.9 | -23.59 |
| Pórtico 3 P1-P2 2/3L Asw_per_m_nec [cm2/m] | 14.532 |  | 13.49 | 7.72 |  |
| Pórtico 3 P1-P2 3/3L As_top_nec [cm2] | 0 |  | 0.4 | -100 |  |
| Pórtico 3 P1-P2 3/3L As_bot_nec [cm2] | 13.752 | 13.8 | 13.8 | -0.34 | -0.01 |
| Pórtico 3 P1-P2 3/3L Asw_per_m_nec [cm2/m] | 10.105 |  | 10.05 | 0.55 |  |
| Pórtico 4 P10-P3 1/3L As_top_nec [cm2] | 5.085 | 5.09 | 8.1 | -37.22 | -37.22 |
| Pórtico 4 P10-P3 1/3L As_bot_nec [cm2] | 0.031 |  | 0 |  |  |
| Pórtico 4 P10-P3 1/3L Asw_per_m_nec [cm2/m] | 5.742 |  | 4.73 | 21.39 |  |
| Pórtico 4 P10-P3 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 8.1 | -37.22 | -37.22 |
| Pórtico 4 P10-P3 2/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 4 P10-P3 2/3L Asw_per_m_nec [cm2/m] | 5.765 |  | 4.73 | 21.89 |  |
| Pórtico 4 P10-P3 3/3L As_top_nec [cm2] | 5.085 | 5.09 | 8.1 | -37.22 | -37.22 |
| Pórtico 4 P10-P3 3/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 4 P10-P3 3/3L Asw_per_m_nec [cm2/m] | 6.113 |  | 4.73 | 29.24 |  |
| Pórtico 4 P3-P4 1/3L As_top_nec [cm2] | 13.222 | 13.33 | 13.72 | -3.63 | -2.85 |
| Pórtico 4 P3-P4 1/3L As_bot_nec [cm2] | 12.181 | 11.12 | 13.34 | -8.69 | -16.65 |
| Pórtico 4 P3-P4 1/3L Asw_per_m_nec [cm2/m] | 22.232 |  | 22.58 | -1.54 |  |
| Pórtico 4 P3-P4 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 5.19 | -2.02 | -2.02 |
| Pórtico 4 P3-P4 2/3L As_bot_nec [cm2] | 14.321 | 15.1 | 15.1 | -5.16 | 0.01 |
| Pórtico 4 P3-P4 2/3L Asw_per_m_nec [cm2/m] | 17.144 |  | 14.86 | 15.37 |  |
| Pórtico 4 P3-P4 3/3L As_top_nec [cm2] | 0.025 |  | 1.21 | -97.95 |  |
| Pórtico 4 P3-P4 3/3L As_bot_nec [cm2] | 14.474 | 15.03 | 15.1 | -4.15 | -0.5 |
| Pórtico 4 P3-P4 3/3L Asw_per_m_nec [cm2/m] | 15.333 |  | 14.1 | 8.75 |  |
| Pórtico 5 P11-P5 1/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.46 | -51.38 | -51.38 |
| Pórtico 5 P11-P5 1/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 5 P11-P5 1/3L Asw_per_m_nec [cm2/m] | 8.3 |  | 7.45 | 11.41 |  |
| Pórtico 5 P11-P5 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.46 | -51.38 | -51.38 |
| Pórtico 5 P11-P5 2/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 5 P11-P5 2/3L Asw_per_m_nec [cm2/m] | 8.323 |  | 7.52 | 10.68 |  |
| Pórtico 5 P11-P5 3/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.46 | -51.38 | -51.38 |
| Pórtico 5 P11-P5 3/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 5 P11-P5 3/3L Asw_per_m_nec [cm2/m] | 8.931 |  | 7.6 | 17.52 |  |
| Pórtico 5 P5-P6 1/3L As_top_nec [cm2] | 15.175 | 15.37 | 15.75 | -3.65 | -2.43 |
| Pórtico 5 P5-P6 1/3L As_bot_nec [cm2] | 11.323 | 10.18 | 12.02 | -5.8 | -15.3 |
| Pórtico 5 P5-P6 1/3L Asw_per_m_nec [cm2/m] | 21.74 |  | 21.75 | -0.05 |  |
| Pórtico 5 P5-P6 2/3L As_top_nec [cm2] | 5.612 | 5.09 | 6.94 | -19.14 | -26.72 |
| Pórtico 5 P5-P6 2/3L As_bot_nec [cm2] | 12.654 | 13 | 13.51 | -6.34 | -3.77 |
| Pórtico 5 P5-P6 2/3L Asw_per_m_nec [cm2/m] | 17.089 |  | 14.94 | 14.38 |  |
| Pórtico 5 P5-P6 3/3L As_top_nec [cm2] | 0.025 |  | 1.09 | -97.69 |  |
| Pórtico 5 P5-P6 3/3L As_bot_nec [cm2] | 13.404 | 13.78 | 13.78 | -2.73 | 0 |
| Pórtico 5 P5-P6 3/3L Asw_per_m_nec [cm2/m] | 14.036 |  | 12.57 | 11.66 |  |
| Pórtico 6 P12-P7 1/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.78 | -34.64 | -34.64 |
| Pórtico 6 P12-P7 1/3L As_bot_nec [cm2] | 0.011 |  | 0 |  |  |
| Pórtico 6 P12-P7 1/3L Asw_per_m_nec [cm2/m] | 5.183 |  | 4.73 | 9.58 |  |
| Pórtico 6 P12-P7 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.78 | -34.64 | -34.64 |
| Pórtico 6 P12-P7 2/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 6 P12-P7 2/3L Asw_per_m_nec [cm2/m] | 5.207 |  | 4.73 | 10.08 |  |
| Pórtico 6 P12-P7 3/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.78 | -34.64 | -34.64 |
| Pórtico 6 P12-P7 3/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 6 P12-P7 3/3L Asw_per_m_nec [cm2/m] | 5.66 |  | 4.73 | 19.67 |  |
| Pórtico 6 P7-P8 1/3L As_top_nec [cm2] | 12.763 | 12.86 | 13.22 | -3.45 | -2.73 |
| Pórtico 6 P7-P8 1/3L As_bot_nec [cm2] | 11.173 | 10.12 | 12.13 | -7.89 | -16.59 |
| Pórtico 6 P7-P8 1/3L Asw_per_m_nec [cm2/m] | 20.908 |  | 21.12 | -1 |  |
| Pórtico 6 P7-P8 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 5.1 | -0.29 | -0.29 |
| Pórtico 6 P7-P8 2/3L As_bot_nec [cm2] | 13.244 | 13.86 | 14.07 | -5.87 | -1.5 |
| Pórtico 6 P7-P8 2/3L Asw_per_m_nec [cm2/m] | 16.199 |  | 14.07 | 15.13 |  |
| Pórtico 6 P7-P8 3/3L As_top_nec [cm2] | 0.027 |  | 1.12 | -97.63 |  |
| Pórtico 6 P7-P8 3/3L As_bot_nec [cm2] | 13.677 | 14.07 | 14.07 | -2.8 | 0 |
| Pórtico 6 P7-P8 3/3L Asw_per_m_nec [cm2/m] | 14.133 |  | 12.86 | 9.9 |  |
| Pórtico 7 P19-P13 1/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.21 | -50.19 | -50.19 |
| Pórtico 7 P19-P13 1/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 7 P19-P13 1/3L Asw_per_m_nec [cm2/m] | 8.3 |  | 7.45 | 11.41 |  |
| Pórtico 7 P19-P13 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.21 | -50.19 | -50.19 |
| Pórtico 7 P19-P13 2/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 7 P19-P13 2/3L Asw_per_m_nec [cm2/m] | 8.323 |  | 7.52 | 10.68 |  |
| Pórtico 7 P19-P13 3/3L As_top_nec [cm2] | 5.085 | 5.09 | 10.21 | -50.19 | -50.19 |
| Pórtico 7 P19-P13 3/3L As_bot_nec [cm2] | 6.369 | 6.37 | 6.37 | -0.01 | -0.01 |
| Pórtico 7 P19-P13 3/3L Asw_per_m_nec [cm2/m] | 8.931 |  | 7.6 | 17.52 |  |
| Pórtico 7 P13-P14 1/3L As_top_nec [cm2] | 14.718 | 14.9 | 15.28 | -3.68 | -2.5 |
| Pórtico 7 P13-P14 1/3L As_bot_nec [cm2] | 11.323 | 10.18 | 12.02 | -5.8 | -15.3 |
| Pórtico 7 P13-P14 1/3L Asw_per_m_nec [cm2/m] | 21.404 |  | 21.41 | -0.03 |  |
| Pórtico 7 P13-P14 2/3L As_top_nec [cm2] | 5.404 | 5.09 | 6.69 | -19.22 | -23.99 |
| Pórtico 7 P13-P14 2/3L As_bot_nec [cm2] | 12.565 | 12.91 | 13.23 | -5.03 | -2.44 |
| Pórtico 7 P13-P14 2/3L Asw_per_m_nec [cm2/m] | 16.757 |  | 14.59 | 14.85 |  |
| Pórtico 7 P13-P14 3/3L As_top_nec [cm2] | 0.025 |  | 1.09 | -97.69 |  |
| Pórtico 7 P13-P14 3/3L As_bot_nec [cm2] | 13.103 | 13.38 | 13.38 | -2.07 | 0.03 |
| Pórtico 7 P13-P14 3/3L Asw_per_m_nec [cm2/m] | 14.036 |  | 12.57 | 11.66 |  |
| Pórtico 8 P21-P15 1/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.61 | -33.18 | -33.18 |
| Pórtico 8 P21-P15 1/3L As_bot_nec [cm2] | 0.031 |  | 0 |  |  |
| Pórtico 8 P21-P15 1/3L Asw_per_m_nec [cm2/m] | 5.742 |  | 4.73 | 21.39 |  |
| Pórtico 8 P21-P15 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.61 | -33.18 | -33.18 |
| Pórtico 8 P21-P15 2/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 8 P21-P15 2/3L Asw_per_m_nec [cm2/m] | 5.765 |  | 4.73 | 21.89 |  |
| Pórtico 8 P21-P15 3/3L As_top_nec [cm2] | 5.085 | 5.09 | 7.61 | -33.18 | -33.18 |
| Pórtico 8 P21-P15 3/3L As_bot_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 8 P21-P15 3/3L Asw_per_m_nec [cm2/m] | 6.113 |  | 4.73 | 29.24 |  |
| Pórtico 8 P15-P17 1/3L As_top_nec [cm2] | 12.315 | 12.4 | 12.79 | -3.71 | -3.06 |
| Pórtico 8 P15-P17 1/3L As_bot_nec [cm2] | 12.181 | 11.12 | 13.34 | -8.69 | -16.65 |
| Pórtico 8 P15-P17 1/3L Asw_per_m_nec [cm2/m] | 21.558 |  | 21.89 | -1.52 |  |
| Pórtico 8 P15-P17 2/3L As_top_nec [cm2] | 5.085 | 5.09 | 5.09 | -0.09 | -0.09 |
| Pórtico 8 P15-P17 2/3L As_bot_nec [cm2] | 14.139 | 14.91 | 14.91 | -5.17 | 0.01 |
| Pórtico 8 P15-P17 2/3L Asw_per_m_nec [cm2/m] | 16.48 |  | 14.17 | 16.3 |  |
| Pórtico 8 P15-P17 3/3L As_top_nec [cm2] | 0.025 |  | 1.21 | -97.95 |  |
| Pórtico 8 P15-P17 3/3L As_bot_nec [cm2] | 14.139 | 14.47 | 14.91 | -5.17 | -2.98 |
| Pórtico 8 P15-P17 3/3L Asw_per_m_nec [cm2/m] | 15.333 |  | 14.1 | 8.75 |  |
| Pórtico 9 P20-P16 1/3L As_top_nec [cm2] | 7.556 | 7.56 | 10.26 | -26.36 | -26.36 |
| Pórtico 9 P20-P16 1/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 9 P20-P16 1/3L Asw_per_m_nec [cm2/m] | 11.614 |  | 8.28 | 40.27 |  |
| Pórtico 9 P20-P16 2/3L As_top_nec [cm2] | 7.556 | 7.56 | 10.26 | -26.36 | -26.36 |
| Pórtico 9 P20-P16 2/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 9 P20-P16 2/3L Asw_per_m_nec [cm2/m] | 11.663 |  | 8.38 | 39.17 |  |
| Pórtico 9 P20-P16 3/3L As_top_nec [cm2] | 7.556 | 7.56 | 10.26 | -26.36 | -26.36 |
| Pórtico 9 P20-P16 3/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 9 P20-P16 3/3L Asw_per_m_nec [cm2/m] | 11.844 |  | 8.47 | 39.84 |  |
| Pórtico 9 P16-P18 1/3L As_top_nec [cm2] | 14.459 | 14.39 | 14.56 | -0.7 | -1.17 |
| Pórtico 9 P16-P18 1/3L As_bot_nec [cm2] | 8.221 | 8.22 | 8.22 | 0.01 | 0.01 |
| Pórtico 9 P16-P18 1/3L Asw_per_m_nec [cm2/m] | 15.967 |  | 16 | -0.2 |  |
| Pórtico 9 P16-P18 2/3L As_top_nec [cm2] | 7.556 | 7.56 | 7.56 | -0.06 | -0.06 |
| Pórtico 9 P16-P18 2/3L As_bot_nec [cm2] | 8.964 | 8.22 | 10.11 | -11.34 | -18.69 |
| Pórtico 9 P16-P18 2/3L Asw_per_m_nec [cm2/m] | 13.513 |  | 12.45 | 8.53 |  |
| Pórtico 9 P16-P18 3/3L As_top_nec [cm2] | 0 |  | 0.4 | -100 |  |
| Pórtico 9 P16-P18 3/3L As_bot_nec [cm2] | 12.366 | 12.38 | 12.38 | -0.12 | 0.01 |
| Pórtico 9 P16-P18 3/3L Asw_per_m_nec [cm2/m] | 9.086 |  | 9.01 | 0.84 |  |
| Pórtico 1 P9-P20 1/3L As_top_nec [cm2] | 3.947 | 3.44 | 3.44 | 14.74 | 0.03 |
| Pórtico 1 P9-P20 1/3L As_bot_nec [cm2] | 1.902 | 2.65 | 2.65 | -28.23 | 0.17 |
| Pórtico 1 P9-P20 1/3L Asw_per_m_nec [cm2/m] | 7.129 |  | 3.95 | 80.48 |  |
| Pórtico 1 P9-P20 2/3L As_top_nec [cm2] | 3.281 | 3 | 3 | 9.37 | 0.15 |
| Pórtico 1 P9-P20 2/3L As_bot_nec [cm2] | 1.709 | 2.17 | 2.17 | -21.24 | -0.12 |
| Pórtico 1 P9-P20 2/3L Asw_per_m_nec [cm2/m] | 6.091 |  | 3.62 | 68.26 |  |
| Pórtico 1 P9-P20 3/3L As_top_nec [cm2] | 3.947 | 3.44 | 3.44 | 14.74 | 0.03 |
| Pórtico 1 P9-P20 3/3L As_bot_nec [cm2] | 1.902 | 2.65 | 2.65 | -28.23 | 0.17 |
| Pórtico 1 P9-P20 3/3L Asw_per_m_nec [cm2/m] | 7.129 |  | 3.95 | 80.48 |  |
| Pórtico 10 P2-P4 1/3L As_top_nec [cm2] | 2.208 | 1.72 | 1.83 | 20.66 | -6.12 |
| Pórtico 10 P2-P4 1/3L As_bot_nec [cm2] | 1.786 | 2.02 | 2.02 | -11.59 | -0.09 |
| Pórtico 10 P2-P4 1/3L Asw_per_m_nec [cm2/m] | 6.735 |  | 2.97 | 126.78 |  |
| Pórtico 10 P2-P4 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P2-P4 2/3L As_bot_nec [cm2] | 1.908 | 2.32 | 2.32 | -17.78 | 0.02 |
| Pórtico 10 P2-P4 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P2-P4 3/3L As_top_nec [cm2] | 4.004 | 3.04 | 3.28 | 22.08 | -7.17 |
| Pórtico 10 P2-P4 3/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P2-P4 3/3L Asw_per_m_nec [cm2/m] | 7.267 |  | 3.47 | 109.43 |  |
| Pórtico 10 P4-P6 1/3L As_top_nec [cm2] | 3.893 | 2.79 | 3.25 | 19.8 | -14.22 |
| Pórtico 10 P4-P6 1/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P4-P6 1/3L Asw_per_m_nec [cm2/m] | 6.88 |  | 3.24 | 112.36 |  |
| Pórtico 10 P4-P6 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P4-P6 2/3L As_bot_nec [cm2] | 1.709 | 1.94 | 1.94 | -11.91 | 0.22 |
| Pórtico 10 P4-P6 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P4-P6 3/3L As_top_nec [cm2] | 3.049 | 2.56 | 2.89 | 5.5 | -11.27 |
| Pórtico 10 P4-P6 3/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P4-P6 3/3L Asw_per_m_nec [cm2/m] | 5.745 |  | 3.17 | 81.22 |  |
| Pórtico 10 P6-P8 1/3L As_top_nec [cm2] | 3.147 | 2.6 | 2.89 | 8.91 | -10.08 |
| Pórtico 10 P6-P8 1/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P6-P8 1/3L Asw_per_m_nec [cm2/m] | 5.939 |  | 3.2 | 85.61 |  |
| Pórtico 10 P6-P8 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P6-P8 2/3L As_bot_nec [cm2] | 1.709 | 1.99 | 1.99 | -14.12 | 0.03 |
| Pórtico 10 P6-P8 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P6-P8 3/3L As_top_nec [cm2] | 3.339 | 2.63 | 2.95 | 13.18 | -10.82 |
| Pórtico 10 P6-P8 3/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P6-P8 3/3L Asw_per_m_nec [cm2/m] | 6.209 |  | 3.21 | 93.44 |  |
| Pórtico 10 P8-P14 1/3L As_top_nec [cm2] | 3.353 | 2.64 | 2.95 | 13.66 | -10.42 |
| Pórtico 10 P8-P14 1/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P8-P14 1/3L Asw_per_m_nec [cm2/m] | 6.227 |  | 3.21 | 93.98 |  |
| Pórtico 10 P8-P14 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P8-P14 2/3L As_bot_nec [cm2] | 1.709 | 1.99 | 1.99 | -14.12 | 0.03 |
| Pórtico 10 P8-P14 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P8-P14 3/3L As_top_nec [cm2] | 3.131 | 2.59 | 2.89 | 8.36 | -10.27 |
| Pórtico 10 P8-P14 3/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P8-P14 3/3L Asw_per_m_nec [cm2/m] | 5.918 |  | 3.19 | 85.52 |  |
| Pórtico 10 P14-P17 1/3L As_top_nec [cm2] | 3.061 | 2.56 | 2.89 | 5.92 | -11.27 |
| Pórtico 10 P14-P17 1/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P14-P17 1/3L Asw_per_m_nec [cm2/m] | 5.758 |  | 3.17 | 81.64 |  |
| Pórtico 10 P14-P17 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P14-P17 2/3L As_bot_nec [cm2] | 1.709 | 1.94 | 1.94 | -11.91 | 0.22 |
| Pórtico 10 P14-P17 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P14-P17 3/3L As_top_nec [cm2] | 3.875 | 2.77 | 3.25 | 19.22 | -14.88 |
| Pórtico 10 P14-P17 3/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P14-P17 3/3L Asw_per_m_nec [cm2/m] | 6.854 |  | 3.24 | 111.55 |  |
| Pórtico 10 P17-P18 1/3L As_top_nec [cm2] | 4.014 | 3.06 | 3.28 | 22.39 | -6.71 |
| Pórtico 10 P17-P18 1/3L As_bot_nec [cm2] | 1.709 | 1.71 | 1.71 | -0.06 | -0.06 |
| Pórtico 10 P17-P18 1/3L Asw_per_m_nec [cm2/m] | 7.276 |  | 3.47 | 109.67 |  |
| Pórtico 10 P17-P18 2/3L As_top_nec [cm2] | 0 |  | 0 |  |  |
| Pórtico 10 P17-P18 2/3L As_bot_nec [cm2] | 1.907 | 2.32 | 2.32 | -17.79 | -0.02 |
| Pórtico 10 P17-P18 2/3L Asw_per_m_nec [cm2/m] | 2.366 |  | 2.37 | -0.15 |  |
| Pórtico 10 P17-P18 3/3L As_top_nec [cm2] | 2.191 | 1.72 | 1.83 | 19.72 | -6.12 |
| Pórtico 10 P17-P18 3/3L As_bot_nec [cm2] | 1.788 | 2.02 | 2.02 | -11.51 | -0.04 |
| Pórtico 10 P17-P18 3/3L Asw_per_m_nec [cm2/m] | 6.713 |  | 2.97 | 126.02 |  |

## Anexo: Flexión ELU (caso final CE-ROM)

| member | section | pos_m | check | demand | capacity | unit | eta | ok | combo | in_verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (sag) | 12.377 | 429.257 | kN·m | 0.029 | sí | ELR17 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -58.572 | 362.568 | kN·m | 0.162 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | MEd <= MRd (sag) | 23.448 | 429.257 | kN·m | 0.055 | sí | ELR17 | sí |
| VT1 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -316.328 | 362.568 | kN·m | 0.873 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 275.78 | 429.257 | kN·m | 0.642 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 6.906 | 429.257 | kN·m | 0.016 | sí | ELR14 | sí |
| VT1 | vano: máx. positivo | 3.25 | MEd <= MRd (sag) | 275.607 | 429.257 | kN·m | 0.642 | sí | ELR08 | sí |
| VT1 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (sag) | 24.622 | 429.257 | kN·m | 0.057 | sí | ELR17 | NO |
| VT1 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -388.56 | 362.568 | kN·m | 1.072 | NO | ELR08 | NO |
| VT1 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 300.645 | 429.257 | kN·m | 0.7 | sí | ELR05 | NO |
| VT1 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -26.24 | 362.568 | kN·m | 0.072 | sí | ELR20 | NO |
| VT2 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -10.007 | 344.48 | kN·m | 0.029 | sí | ELR14 | sí |
| VT2 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -265.234 | 344.48 | kN·m | 0.77 | sí | ELR08 | sí |
| VT2 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 261.388 | 453.1 | kN·m | 0.577 | sí | ELR08 | sí |
| VT2 | cara pilote tierra - vano | 3.25 | MEd <= MRd (hog) | -0.517 | 344.48 | kN·m | 0.002 | sí | ELR17 | sí |
| VT2 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 5.15 | 453.1 | kN·m | 0.011 | sí | ELR20 | sí |
| VT2 | vano: máx. positivo | 2.708 | MEd <= MRd (sag) | 315.955 | 453.1 | kN·m | 0.697 | sí | ELR08 | sí |
| VT2 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -373.323 | 344.48 | kN·m | 1.084 | NO | ELR08 | NO |
| VT2 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 276.082 | 453.1 | kN·m | 0.609 | sí | ELR05 | NO |
| VT2 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -67.299 | 344.48 | kN·m | 0.195 | sí | ELR20 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (sag) | 10.594 | 453.1 | kN·m | 0.023 | sí | ELR17 | sí |
| VT3 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -63.43 | 344.48 | kN·m | 0.184 | sí | ELR08 | sí |
| VT3 | cara pilote mar - vano | 0.2 | MEd <= MRd (sag) | 20.346 | 453.1 | kN·m | 0.045 | sí | ELR17 | sí |
| VT3 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -302.775 | 344.48 | kN·m | 0.879 | sí | ELR08 | sí |
| VT3 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 258.227 | 453.1 | kN·m | 0.57 | sí | ELR08 | sí |
| VT3 | cara pilote tierra - vano | 3.25 | MEd <= MRd (hog) | -0.524 | 344.48 | kN·m | 0.002 | sí | ELR17 | sí |
| VT3 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 4.209 | 453.1 | kN·m | 0.009 | sí | ELR14 | sí |
| VT3 | vano: máx. positivo | 2.708 | MEd <= MRd (sag) | 292.696 | 453.1 | kN·m | 0.646 | sí | ELR08 | sí |
| VT3 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (sag) | 21.533 | 453.1 | kN·m | 0.048 | sí | ELR17 | NO |
| VT3 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -406.383 | 344.48 | kN·m | 1.18 | NO | ELR08 | NO |
| VT3 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 276.635 | 453.1 | kN·m | 0.611 | sí | ELR05 | NO |
| VT3 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -61.836 | 344.48 | kN·m | 0.179 | sí | ELR20 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -9.561 | 344.48 | kN·m | 0.028 | sí | ELR14 | sí |
| VT4 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -256.243 | 344.48 | kN·m | 0.744 | sí | ELR08 | sí |
| VT4 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 252.276 | 453.1 | kN·m | 0.557 | sí | ELR08 | sí |
| VT4 | cara pilote tierra - vano | 3.25 | MEd <= MRd (hog) | -0.554 | 344.48 | kN·m | 0.002 | sí | ELR17 | sí |
| VT4 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 4.228 | 453.1 | kN·m | 0.009 | sí | ELR20 | sí |
| VT4 | vano: máx. positivo | 2.708 | MEd <= MRd (sag) | 298.463 | 453.1 | kN·m | 0.659 | sí | ELR08 | sí |
| VT4 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -357.463 | 344.48 | kN·m | 1.038 | NO | ELR08 | NO |
| VT4 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 267.256 | 453.1 | kN·m | 0.59 | sí | ELR05 | NO |
| VT4 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -62.269 | 344.48 | kN·m | 0.181 | sí | ELR20 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (sag) | 10.594 | 453.1 | kN·m | 0.023 | sí | ELR17 | sí |
| VT5 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -63.451 | 344.48 | kN·m | 0.184 | sí | ELR08 | sí |
| VT5 | cara pilote mar - vano | 0.2 | MEd <= MRd (sag) | 20.346 | 453.1 | kN·m | 0.045 | sí | ELR17 | sí |
| VT5 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -293.961 | 344.48 | kN·m | 0.853 | sí | ELR08 | sí |
| VT5 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 249.45 | 453.1 | kN·m | 0.55 | sí | ELR08 | sí |
| VT5 | cara pilote tierra - vano | 3.25 | MEd <= MRd (hog) | -0.524 | 344.48 | kN·m | 0.002 | sí | ELR17 | sí |
| VT5 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 4.209 | 453.1 | kN·m | 0.009 | sí | ELR14 | sí |
| VT5 | vano: máx. positivo | 2.708 | MEd <= MRd (sag) | 287.063 | 453.1 | kN·m | 0.634 | sí | ELR08 | sí |
| VT5 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (sag) | 21.533 | 453.1 | kN·m | 0.048 | sí | ELR17 | NO |
| VT5 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -396.371 | 344.48 | kN·m | 1.151 | NO | ELR08 | NO |
| VT5 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 266.619 | 453.1 | kN·m | 0.588 | sí | ELR05 | NO |
| VT5 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -61.836 | 344.48 | kN·m | 0.179 | sí | ELR20 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -10.007 | 344.48 | kN·m | 0.029 | sí | ELR14 | sí |
| VT6 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -247.608 | 344.48 | kN·m | 0.719 | sí | ELR08 | sí |
| VT6 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 243.839 | 453.1 | kN·m | 0.538 | sí | ELR08 | sí |
| VT6 | cara pilote tierra - vano | 3.25 | MEd <= MRd (hog) | -0.517 | 344.48 | kN·m | 0.002 | sí | ELR17 | sí |
| VT6 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 5.15 | 453.1 | kN·m | 0.011 | sí | ELR20 | sí |
| VT6 | vano: máx. positivo | 2.217 | MEd <= MRd (sag) | 307.009 | 453.1 | kN·m | 0.678 | sí | ELR08 | sí |
| VT6 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -353.294 | 344.48 | kN·m | 1.026 | NO | ELR08 | NO |
| VT6 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 256.06 | 453.1 | kN·m | 0.565 | sí | ELR05 | NO |
| VT6 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -67.299 | 344.48 | kN·m | 0.195 | sí | ELR20 | NO |
| VT7 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (sag) | 12.377 | 429.257 | kN·m | 0.029 | sí | ELR17 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | MEd <= MRd (hog) | -58.624 | 362.568 | kN·m | 0.162 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | MEd <= MRd (sag) | 23.448 | 429.257 | kN·m | 0.055 | sí | ELR17 | sí |
| VT7 | cara pilote mar - vano | 0.2 | MEd <= MRd (hog) | -289.416 | 362.568 | kN·m | 0.798 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vano | 3.25 | MEd <= MRd (sag) | 248.843 | 429.257 | kN·m | 0.58 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | MEd <= MRd (sag) | 6.906 | 429.257 | kN·m | 0.016 | sí | ELR14 | sí |
| VT7 | vano: máx. positivo | 3.25 | MEd <= MRd (sag) | 248.718 | 429.257 | kN·m | 0.579 | sí | ELR08 | sí |
| VT7 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (sag) | 24.622 | 429.257 | kN·m | 0.057 | sí | ELR17 | NO |
| VT7 | eje pilote mar (info, nudo rígido) | 0 | MEd <= MRd (hog) | -358.093 | 362.568 | kN·m | 0.988 | sí | ELR08 | NO |
| VT7 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (sag) | 270.147 | 429.257 | kN·m | 0.629 | sí | ELR05 | NO |
| VT7 | eje pilote tierra (info, nudo rígido) | 3.45 | MEd <= MRd (hog) | -26.24 | 362.568 | kN·m | 0.072 | sí | ELR20 | NO |
| VBM | tramo 1 cara izq. (X=0.40) | 0.4 | MEd <= MRd (hog) | -20.984 | 40.314 | kN·m | 0.52 | sí | ELR20 | sí |
| VBM | tramo 1 cara der. (X=6.25) | 6.25 | MEd <= MRd (hog) | -37.525 | 40.314 | kN·m | 0.931 | sí | ELR14 | sí |
| VBM | tramo 2 cara izq. (X=6.75) | 6.75 | MEd <= MRd (hog) | -36.537 | 40.314 | kN·m | 0.906 | sí | ELR14 | sí |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | MEd <= MRd (hog) | -29.058 | 40.314 | kN·m | 0.721 | sí | ELR20 | sí |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | MEd <= MRd (hog) | -29.887 | 40.314 | kN·m | 0.741 | sí | ELR20 | sí |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | MEd <= MRd (hog) | -31.547 | 40.314 | kN·m | 0.782 | sí | ELR14 | sí |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | MEd <= MRd (hog) | -31.547 | 40.314 | kN·m | 0.782 | sí | ELR14 | sí |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | MEd <= MRd (hog) | -29.887 | 40.314 | kN·m | 0.741 | sí | ELR20 | sí |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | MEd <= MRd (hog) | -29.058 | 40.314 | kN·m | 0.721 | sí | ELR20 | sí |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | MEd <= MRd (hog) | -36.537 | 40.314 | kN·m | 0.906 | sí | ELR14 | sí |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | MEd <= MRd (hog) | -37.525 | 40.314 | kN·m | 0.931 | sí | ELR14 | sí |
| VBM | tramo 6 cara der. (X=38.60) | 38.6 | MEd <= MRd (hog) | -20.984 | 40.314 | kN·m | 0.52 | sí | ELR20 | sí |
| VBM | tramo 1: máx. positivo | 3 | MEd <= MRd (sag) | 18.544 | 40.314 | kN·m | 0.46 | sí | ELR20 | sí |
| VBM | tramo 2: máx. positivo | 10 | MEd <= MRd (sag) | 10.774 | 40.314 | kN·m | 0.267 | sí | ELR14 | sí |
| VBM | tramo 3: máx. positivo | 16 | MEd <= MRd (sag) | 12.145 | 40.314 | kN·m | 0.301 | sí | ELR14 | sí |
| VBM | tramo 4: máx. positivo | 23 | MEd <= MRd (sag) | 12.145 | 40.314 | kN·m | 0.301 | sí | ELR14 | sí |
| VBM | tramo 5: máx. positivo | 29 | MEd <= MRd (sag) | 10.774 | 40.314 | kN·m | 0.267 | sí | ELR14 | sí |
| VBM | tramo 6: máx. positivo | 36 | MEd <= MRd (sag) | 18.544 | 40.314 | kN·m | 0.46 | sí | ELR20 | sí |
| VBT | tramo 1 cara izq. (X=0.40) | 0.4 | MEd <= MRd (hog) | -21.572 | 40.314 | kN·m | 0.535 | sí | ELR08 | sí |
| VBT | tramo 1 cara der. (X=6.25) | 6.25 | MEd <= MRd (hog) | -38.254 | 40.314 | kN·m | 0.949 | sí | ELR08 | sí |
| VBT | tramo 2 cara izq. (X=6.75) | 6.75 | MEd <= MRd (hog) | -37.341 | 40.314 | kN·m | 0.926 | sí | ELR08 | sí |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | MEd <= MRd (hog) | -29.537 | 40.314 | kN·m | 0.733 | sí | ELR08 | sí |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | MEd <= MRd (hog) | -30.525 | 40.314 | kN·m | 0.757 | sí | ELR08 | sí |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | MEd <= MRd (hog) | -32.235 | 40.314 | kN·m | 0.8 | sí | ELR08 | sí |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | MEd <= MRd (hog) | -32.449 | 40.314 | kN·m | 0.805 | sí | ELR08 | sí |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | MEd <= MRd (hog) | -30.281 | 40.314 | kN·m | 0.751 | sí | ELR08 | sí |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | MEd <= MRd (hog) | -29.721 | 40.314 | kN·m | 0.737 | sí | ELR08 | sí |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | MEd <= MRd (hog) | -37.061 | 40.314 | kN·m | 0.919 | sí | ELR08 | sí |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | MEd <= MRd (hog) | -38.405 | 40.314 | kN·m | 0.953 | sí | ELR08 | sí |
| VBT | tramo 6 cara der. (X=38.60) | 38.6 | MEd <= MRd (hog) | -21.302 | 40.314 | kN·m | 0.528 | sí | ELR14 | sí |
| VBT | tramo 1: máx. positivo | 3 | MEd <= MRd (sag) | 18.63 | 40.314 | kN·m | 0.462 | sí | ELR08 | sí |
| VBT | tramo 2: máx. positivo | 10 | MEd <= MRd (sag) | 11.035 | 40.314 | kN·m | 0.274 | sí | ELR08 | sí |
| VBT | tramo 3: máx. positivo | 16 | MEd <= MRd (sag) | 12.379 | 40.314 | kN·m | 0.307 | sí | ELR08 | sí |
| VBT | tramo 4: máx. positivo | 23 | MEd <= MRd (sag) | 12.386 | 40.314 | kN·m | 0.307 | sí | ELR08 | sí |
| VBT | tramo 5: máx. positivo | 29 | MEd <= MRd (sag) | 11.016 | 40.314 | kN·m | 0.273 | sí | ELR08 | sí |
| VBT | tramo 6: máx. positivo | 36 | MEd <= MRd (sag) | 18.624 | 40.314 | kN·m | 0.462 | sí | ELR08 | sí |

## Anexo: Cortante y torsión (caso final CE-ROM)

| member | section | pos_m | check | demand | capacity | unit | eta | ok | combo | in_verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 146.548 | 1935.4 | kN | 0.076 | sí | ELR14 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 146.548 | 814.301 | kN | 0.18 | sí | ELR14 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 146.548 | 184.118 | kN | 0.796 | sí | ELR14 | NO |
| VT1 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 6.263 | 23.562 | cm²/m | 0.266 | sí | ELR14 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 43.502 | 387.01 | kN·m | 0.188 | sí | ELR14 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 43.502 | 120.377 | kN·m | 1.157 | NO | ELR14 | NO |
| VT1 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 3.102 | 7.854 | cm²/m·rama | 0.395 | sí | ELR14 | sí |
| VT1 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 43.182 |  | kN·m | 0.325 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 358.311 | 1935.4 | kN | 0.185 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 319.338 | 814.301 | kN | 0.392 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 319.338 | 184.118 | kN | 1.734 | NO | ELR08 | NO |
| VT1 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 11.263 | 23.562 | cm²/m | 0.478 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 26.486 | 387.01 | kN·m | 0.254 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 26.486 | 120.377 | kN·m | 2.166 | NO | ELR08 | NO |
| VT1 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 4.246 | 7.854 | cm²/m·rama | 0.541 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 26.486 |  | kN·m | 0.973 | sí | ELR08 | sí |
| VT1 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 82.486 |  | kN·m | 0.398 | sí | ELR08 | NO |
| VT1 | cara pilote mar - vano | 0.2 | estribos V + T (por rama del cerco) [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 77.101 |  | kN·m | 0.707 | sí | ELR08 | NO |
| VT1 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 82.486 |  | kN·m | 1.185 | NO | ELR08 | NO |
| VT1 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 161.826 | 1935.4 | kN | 0.084 | sí | ELR20 | sí |
| VT1 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 162.061 | 814.301 | kN | 0.199 | sí | ELR05 | sí |
| VT1 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 162.061 | 184.118 | kN | 0.88 | sí | ELR05 | NO |
| VT1 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 5.75 | 23.562 | cm²/m | 0.244 | sí | ELR20 | sí |
| VT1 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 27.192 | 387.01 | kN·m | 0.154 | sí | ELR20 | sí |
| VT1 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 27.192 | 120.377 | kN·m | 1.105 | NO | ELR20 | NO |
| VT1 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 2.454 | 7.854 | cm²/m·rama | 0.312 | sí | ELR20 | sí |
| VT1 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 27.598 |  | kN·m | 0.73 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 83.192 |  | kN·m | 0.299 | sí | ELR20 | NO |
| VT1 | cara pilote tierra - vano | 3.25 | estribos V + T (por rama del cerco) [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 79.024 |  | kN·m | 0.479 | sí | ELR20 | NO |
| VT1 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 83.598 |  | kN·m | 0.906 | sí | ELR08 | NO |
| VT1 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 63.7 | 1935.4 | kN | 0.033 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 63.7 | 814.301 | kN | 0.078 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 63.7 | 184.118 | kN | 0.346 | sí | ELR08 | NO |
| VT1 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 1.843 | 23.562 | cm²/m | 0.078 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 44.986 | 387.01 | kN·m | 0.149 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 44.986 | 120.377 | kN·m | 0.72 | sí | ELR08 | NO |
| VT1 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 1.664 | 7.854 | cm²/m·rama | 0.212 | sí | ELR08 | sí |
| VT1 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 44.986 |  | kN·m | 0.158 | sí | ELR08 | sí |
| VT2 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 105.807 | 1209.6 | kN | 0.087 | sí | ELR14 | sí |
| VT2 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 105.807 | 814.301 | kN | 0.13 | sí | ELR14 | sí |
| VT2 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 105.807 | 134.591 | kN | 0.786 | sí | ELR14 | NO |
| VT2 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 7.131 | 23.562 | cm²/m | 0.303 | sí | ELR14 | sí |
| VT2 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.136 | 199.036 | kN·m | 0.102 | sí | ELR20 | NO |
| VT2 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.905 | 61.909 | kN·m | 0.833 | sí | ELR14 | NO |
| VT2 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 2.491 | 7.854 | cm²/m·rama | 0.317 | sí | ELR20 | NO |
| VT2 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.905 |  | kN·m | 0.039 | sí | ELR14 | NO |
| VT2 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 539.236 | 1209.6 | kN | 0.446 | sí | ELR08 | sí |
| VT2 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 443.196 | 814.301 | kN | 0.544 | sí | ELR08 | sí |
| VT2 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 443.196 | 134.591 | kN | 3.293 | NO | ELR08 | NO |
| VT2 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 16.893 | 23.562 | cm²/m | 0.717 | sí | ELR08 | sí |
| VT2 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 17.536 | 199.036 | kN·m | 0.534 | sí | ELR08 | NO |
| VT2 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 17.536 | 61.909 | kN·m | 4.29 | NO | ELR08 | NO |
| VT2 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 6.154 | 7.854 | cm²/m·rama | 0.784 | sí | ELR08 | NO |
| VT2 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 17.536 |  | kN·m | 0.833 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 355.26 | 1209.6 | kN | 0.294 | sí | ELR20 | sí |
| VT2 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 265.249 | 814.301 | kN | 0.326 | sí | ELR20 | sí |
| VT2 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 265.249 | 134.591 | kN | 1.971 | NO | ELR20 | NO |
| VT2 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 11.744 | 23.562 | cm²/m | 0.498 | sí | ELR20 | sí |
| VT2 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 16.507 | 199.036 | kN·m | 0.377 | sí | ELR20 | NO |
| VT2 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 16.507 | 61.909 | kN·m | 2.906 | NO | ELR20 | NO |
| VT2 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 4.429 | 7.854 | cm²/m·rama | 0.564 | sí | ELR20 | NO |
| VT2 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 15.803 |  | kN·m | 0.616 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 102.573 | 1209.6 | kN | 0.085 | sí | ELR08 | sí |
| VT2 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 102.573 | 814.301 | kN | 0.126 | sí | ELR08 | sí |
| VT2 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 102.573 | 134.591 | kN | 0.762 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 2.968 | 23.562 | cm²/m | 0.126 | sí | ELR08 | sí |
| VT2 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.019 | 199.036 | kN·m | 0.095 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.019 | 61.909 | kN·m | 0.795 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 1.068 | 7.854 | cm²/m·rama | 0.136 | sí | ELR08 | NO |
| VT2 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.315 |  | kN·m | 0.017 | sí | ELR20 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 173.132 | 1209.6 | kN | 0.143 | sí | ELR14 | sí |
| VT3 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 173.132 | 814.301 | kN | 0.213 | sí | ELR14 | sí |
| VT3 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 173.132 | 134.591 | kN | 1.286 | NO | ELR14 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 9.102 | 23.562 | cm²/m | 0.386 | sí | ELR14 | sí |
| VT3 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 1.57 | 199.036 | kN·m | 0.151 | sí | ELR14 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 1.57 | 61.909 | kN·m | 1.312 | NO | ELR14 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 3.095 | 7.854 | cm²/m·rama | 0.394 | sí | ELR14 | NO |
| VT3 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.246 |  | kN·m | 0.189 | sí | ELR08 | NO |
| VT3 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 516.833 | 1209.6 | kN | 0.427 | sí | ELR08 | sí |
| VT3 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 428.571 | 814.301 | kN | 0.526 | sí | ELR08 | sí |
| VT3 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 428.571 | 134.591 | kN | 3.184 | NO | ELR08 | NO |
| VT3 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 16.494 | 23.562 | cm²/m | 0.7 | sí | ELR08 | sí |
| VT3 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 1.249 | 199.036 | kN·m | 0.434 | sí | ELR08 | NO |
| VT3 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 1.249 | 61.909 | kN·m | 3.86 | NO | ELR08 | NO |
| VT3 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 5.526 | 7.854 | cm²/m·rama | 0.704 | sí | ELR08 | NO |
| VT3 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.249 |  | kN·m | 0.883 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 327.379 | 1209.6 | kN | 0.271 | sí | ELR20 | sí |
| VT3 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 245.542 | 814.301 | kN | 0.301 | sí | ELR20 | sí |
| VT3 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 245.542 | 134.591 | kN | 1.824 | NO | ELR20 | NO |
| VT3 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 11.198 | 23.562 | cm²/m | 0.475 | sí | ELR20 | sí |
| VT3 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.279 | 199.036 | kN·m | 0.282 | sí | ELR20 | NO |
| VT3 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.279 | 61.909 | kN·m | 2.469 | NO | ELR20 | NO |
| VT3 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 3.794 | 7.854 | cm²/m·rama | 0.483 | sí | ELR20 | NO |
| VT3 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.165 |  | kN·m | 0.577 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 88.669 | 1209.6 | kN | 0.073 | sí | ELR08 | sí |
| VT3 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 88.669 | 814.301 | kN | 0.109 | sí | ELR08 | sí |
| VT3 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 88.669 | 134.591 | kN | 0.659 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 2.566 | 23.562 | cm²/m | 0.109 | sí | ELR08 | sí |
| VT3 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 1.537 | 199.036 | kN·m | 0.081 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 1.537 | 61.909 | kN·m | 0.684 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 0.915 | 7.854 | cm²/m·rama | 0.117 | sí | ELR08 | NO |
| VT3 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.249 |  | kN·m | 0.013 | sí | ELR14 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 98.012 | 1209.6 | kN | 0.081 | sí | ELR14 | sí |
| VT4 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 98.012 | 814.301 | kN | 0.12 | sí | ELR14 | sí |
| VT4 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 98.012 | 134.591 | kN | 0.728 | sí | ELR14 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 6.929 | 23.562 | cm²/m | 0.294 | sí | ELR14 | sí |
| VT4 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 0 | 199.036 | kN·m | 0.081 | sí | ELR14 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 0 | 61.909 | kN·m | 0.728 | sí | ELR14 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 2.31 | 7.854 | cm²/m·rama | 0.294 | sí | ELR14 | NO |
| VT4 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 0.345 |  | kN·m | 0.028 | sí | ELR08 | NO |
| VT4 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 504.893 | 1209.6 | kN | 0.417 | sí | ELR08 | sí |
| VT4 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 415.507 | 814.301 | kN | 0.51 | sí | ELR08 | sí |
| VT4 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 415.507 | 134.591 | kN | 3.087 | NO | ELR08 | NO |
| VT4 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 16.116 | 23.562 | cm²/m | 0.684 | sí | ELR08 | sí |
| VT4 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 0.797 | 199.036 | kN·m | 0.421 | sí | ELR08 | NO |
| VT4 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 0.797 | 61.909 | kN·m | 3.764 | NO | ELR08 | NO |
| VT4 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 5.396 | 7.854 | cm²/m·rama | 0.687 | sí | ELR08 | NO |
| VT4 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 0.797 |  | kN·m | 0.747 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 328.38 | 1209.6 | kN | 0.272 | sí | ELR20 | sí |
| VT4 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 244.531 | 814.301 | kN | 0.3 | sí | ELR20 | sí |
| VT4 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 244.531 | 134.591 | kN | 1.817 | NO | ELR20 | NO |
| VT4 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 11.168 | 23.562 | cm²/m | 0.474 | sí | ELR20 | sí |
| VT4 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 0 | 199.036 | kN·m | 0.272 | sí | ELR20 | NO |
| VT4 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 0 | 61.909 | kN·m | 2.44 | NO | ELR20 | NO |
| VT4 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 3.723 | 7.854 | cm²/m·rama | 0.474 | sí | ELR20 | NO |
| VT4 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 0.782 |  | kN·m | 0.559 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 93.156 | 1209.6 | kN | 0.077 | sí | ELR08 | sí |
| VT4 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 93.156 | 814.301 | kN | 0.114 | sí | ELR08 | sí |
| VT4 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 93.156 | 134.591 | kN | 0.692 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 2.695 | 23.562 | cm²/m | 0.114 | sí | ELR08 | sí |
| VT4 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 0.292 | 199.036 | kN·m | 0.079 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 0.292 | 61.909 | kN·m | 0.697 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 0.91 | 7.854 | cm²/m·rama | 0.116 | sí | ELR08 | NO |
| VT4 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 0.175 |  | kN·m | 0.009 | sí | ELR10 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 173.132 | 1209.6 | kN | 0.143 | sí | ELR14 | sí |
| VT5 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 173.132 | 814.301 | kN | 0.213 | sí | ELR14 | sí |
| VT5 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 173.132 | 134.591 | kN | 1.286 | NO | ELR14 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 9.102 | 23.562 | cm²/m | 0.386 | sí | ELR14 | sí |
| VT5 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 1.57 | 199.036 | kN·m | 0.151 | sí | ELR14 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 1.57 | 61.909 | kN·m | 1.312 | NO | ELR14 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 3.095 | 7.854 | cm²/m·rama | 0.394 | sí | ELR14 | NO |
| VT5 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.93 |  | kN·m | 0.191 | sí | ELR08 | NO |
| VT5 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 510.841 | 1209.6 | kN | 0.422 | sí | ELR08 | sí |
| VT5 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 422.757 | 814.301 | kN | 0.519 | sí | ELR08 | sí |
| VT5 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 422.757 | 134.591 | kN | 3.141 | NO | ELR08 | NO |
| VT5 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 16.325 | 23.562 | cm²/m | 0.693 | sí | ELR08 | sí |
| VT5 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.84 | 199.036 | kN·m | 0.437 | sí | ELR08 | NO |
| VT5 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.84 | 61.909 | kN·m | 3.841 | NO | ELR08 | NO |
| VT5 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 5.518 | 7.854 | cm²/m·rama | 0.703 | sí | ELR08 | NO |
| VT5 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.84 |  | kN·m | 0.864 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 327.379 | 1209.6 | kN | 0.271 | sí | ELR20 | sí |
| VT5 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 245.542 | 814.301 | kN | 0.301 | sí | ELR20 | sí |
| VT5 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 245.542 | 134.591 | kN | 1.824 | NO | ELR20 | NO |
| VT5 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 11.198 | 23.562 | cm²/m | 0.475 | sí | ELR20 | sí |
| VT5 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.279 | 199.036 | kN·m | 0.282 | sí | ELR20 | NO |
| VT5 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.279 | 61.909 | kN·m | 2.469 | NO | ELR20 | NO |
| VT5 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 3.794 | 7.854 | cm²/m·rama | 0.483 | sí | ELR20 | NO |
| VT5 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.261 |  | kN·m | 0.554 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 88.557 | 1209.6 | kN | 0.073 | sí | ELR08 | sí |
| VT5 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 88.557 | 814.301 | kN | 0.109 | sí | ELR08 | sí |
| VT5 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 88.557 | 134.591 | kN | 0.658 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 2.562 | 23.562 | cm²/m | 0.109 | sí | ELR08 | sí |
| VT5 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 0.951 | 199.036 | kN·m | 0.078 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 0.951 | 61.909 | kN·m | 0.673 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 0.891 | 7.854 | cm²/m·rama | 0.114 | sí | ELR08 | NO |
| VT5 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 1.249 |  | kN·m | 0.013 | sí | ELR14 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 105.807 | 1209.6 | kN | 0.087 | sí | ELR14 | sí |
| VT6 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 105.807 | 814.301 | kN | 0.13 | sí | ELR14 | sí |
| VT6 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 105.807 | 134.591 | kN | 0.786 | sí | ELR14 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 7.131 | 23.562 | cm²/m | 0.303 | sí | ELR14 | sí |
| VT6 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.136 | 199.036 | kN·m | 0.102 | sí | ELR20 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.905 | 61.909 | kN·m | 0.833 | sí | ELR14 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 2.491 | 7.854 | cm²/m·rama | 0.317 | sí | ELR20 | NO |
| VT6 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.905 |  | kN·m | 0.039 | sí | ELR14 | NO |
| VT6 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 527.218 | 1209.6 | kN | 0.436 | sí | ELR08 | sí |
| VT6 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 431.544 | 814.301 | kN | 0.53 | sí | ELR08 | sí |
| VT6 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 431.544 | 134.591 | kN | 3.206 | NO | ELR08 | NO |
| VT6 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 16.556 | 23.562 | cm²/m | 0.703 | sí | ELR08 | sí |
| VT6 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 15.932 | 199.036 | kN·m | 0.516 | sí | ELR08 | NO |
| VT6 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 15.932 | 61.909 | kN·m | 4.175 | NO | ELR08 | NO |
| VT6 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 5.994 | 7.854 | cm²/m·rama | 0.763 | sí | ELR08 | NO |
| VT6 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 15.932 |  | kN·m | 0.776 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 355.26 | 1209.6 | kN | 0.294 | sí | ELR20 | sí |
| VT6 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 265.249 | 814.301 | kN | 0.326 | sí | ELR20 | sí |
| VT6 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 265.249 | 134.591 | kN | 1.971 | NO | ELR20 | NO |
| VT6 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 11.744 | 23.562 | cm²/m | 0.498 | sí | ELR20 | sí |
| VT6 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 16.507 | 199.036 | kN·m | 0.377 | sí | ELR20 | NO |
| VT6 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 16.507 | 61.909 | kN·m | 2.906 | NO | ELR20 | NO |
| VT6 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 4.429 | 7.854 | cm²/m·rama | 0.564 | sí | ELR20 | NO |
| VT6 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 17.501 |  | kN·m | 0.581 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 102.332 | 1209.6 | kN | 0.085 | sí | ELR08 | sí |
| VT6 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 102.332 | 814.301 | kN | 0.126 | sí | ELR08 | sí |
| VT6 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 102.332 | 134.591 | kN | 0.76 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 2.961 | 23.562 | cm²/m | 0.126 | sí | ELR08 | sí |
| VT6 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.606 | 199.036 | kN·m | 0.098 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.606 | 61.909 | kN·m | 0.802 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 1.089 | 7.854 | cm²/m·rama | 0.139 | sí | ELR08 | NO |
| VT6 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.315 |  | kN·m | 0.017 | sí | ELR20 | NO |
| VT7 | cara pilote mar - voladizo | -0.2 | VEd(cara) <= VRd,max | 146.548 | 1935.4 | kN | 0.076 | sí | ELR14 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,s | 146.548 | 814.301 | kN | 0.18 | sí | ELR14 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | VEd(d) <= VRd,c (info: links needed?) | 146.548 | 184.118 | kN | 0.796 | sí | ELR14 | NO |
| VT7 | cara pilote mar - voladizo | -0.2 | estribos V + suspensión alveoplaca (todas las ramas) | 6.263 | 23.562 | cm²/m | 0.266 | sí | ELR14 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 43.502 | 387.01 | kN·m | 0.188 | sí | ELR14 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 43.502 | 120.377 | kN·m | 1.157 | NO | ELR14 | NO |
| VT7 | cara pilote mar - voladizo | -0.2 | estribos V + T (por rama del cerco) | 3.102 | 7.854 | cm²/m·rama | 0.395 | sí | ELR14 | sí |
| VT7 | cara pilote mar - voladizo | -0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 43.774 |  | kN·m | 0.327 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | VEd(cara) <= VRd,max | 340.536 | 1935.4 | kN | 0.176 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,s | 301.672 | 814.301 | kN | 0.37 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.68 | VEd(d) <= VRd,c (info: links needed?) | 301.672 | 184.118 | kN | 1.639 | NO | ELR08 | NO |
| VT7 | cara pilote mar - vano | 0.68 | estribos V + suspensión alveoplaca (todas las ramas) | 10.752 | 23.562 | cm²/m | 0.456 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 | 28.416 | 387.01 | kN·m | 0.249 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 28.416 | 120.377 | kN·m | 2.086 | NO | ELR08 | NO |
| VT7 | cara pilote mar - vano | 0.68 | estribos V + T (por rama del cerco) | 4.121 | 7.854 | cm²/m·rama | 0.525 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 28.416 |  | kN·m | 0.906 | sí | ELR08 | sí |
| VT7 | cara pilote mar - vano | 0.2 | TEd/TRd,max + VEd/VRd,max <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 84.416 |  | kN·m | 0.394 | sí | ELR08 | NO |
| VT7 | cara pilote mar - vano | 0.2 | estribos V + T (por rama del cerco) [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 79.045 |  | kN·m | 0.691 | sí | ELR08 | NO |
| VT7 | cara pilote mar - vano | 0.2 | M/MRd + ΣAsl,T(cordón)/As <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 84.416 |  | kN·m | 1.118 | NO | ELR08 | NO |
| VT7 | cara pilote tierra - vano | 3.25 | VEd(cara) <= VRd,max | 161.826 | 1935.4 | kN | 0.084 | sí | ELR20 | sí |
| VT7 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,s | 144.38 | 814.301 | kN | 0.177 | sí | ELR05 | sí |
| VT7 | cara pilote tierra - vano | 2.77 | VEd(d) <= VRd,c (info: links needed?) | 144.38 | 184.118 | kN | 0.784 | sí | ELR05 | NO |
| VT7 | cara pilote tierra - vano | 2.77 | estribos V + suspensión alveoplaca (todas las ramas) | 5.75 | 23.562 | cm²/m | 0.244 | sí | ELR20 | sí |
| VT7 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 27.192 | 387.01 | kN·m | 0.154 | sí | ELR20 | sí |
| VT7 | cara pilote tierra - vano | 3.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 27.192 | 120.377 | kN·m | 1.105 | NO | ELR20 | NO |
| VT7 | cara pilote tierra - vano | 2.77 | estribos V + T (por rama del cerco) | 2.454 | 7.854 | cm²/m·rama | 0.312 | sí | ELR20 | sí |
| VT7 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 25.676 |  | kN·m | 0.661 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vano | 3.25 | TEd/TRd,max + VEd/VRd,max <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 83.192 |  | kN·m | 0.299 | sí | ELR20 | NO |
| VT7 | cara pilote tierra - vano | 3.25 | estribos V + T (por rama del cerco) [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 79.024 |  | kN·m | 0.479 | sí | ELR20 | NO |
| VT7 | cara pilote tierra - vano | 3.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m] | 81.676 |  | kN·m | 0.837 | sí | ELR08 | NO |
| VT7 | cara pilote tierra - vuelo | 3.65 | VEd(cara) <= VRd,max | 63.399 | 1935.4 | kN | 0.033 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,s | 63.399 | 814.301 | kN | 0.078 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | VEd(d) <= VRd,c (info: links needed?) | 63.399 | 184.118 | kN | 0.344 | sí | ELR08 | NO |
| VT7 | cara pilote tierra - vuelo | 3.65 | estribos V + suspensión alveoplaca (todas las ramas) | 1.834 | 23.562 | cm²/m | 0.078 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,max + VEd/VRd,max <= 1 | 44.441 | 387.01 | kN·m | 0.148 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 44.441 | 120.377 | kN·m | 0.714 | sí | ELR08 | NO |
| VT7 | cara pilote tierra - vuelo | 3.65 | estribos V + T (por rama del cerco) | 1.648 | 7.854 | cm²/m·rama | 0.21 | sí | ELR08 | sí |
| VT7 | cara pilote tierra - vuelo | 3.65 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 44.468 |  | kN·m | 0.156 | sí | ELR14 | sí |
| VBM | tramo 1 cara izq. (X=0.40) | 0.4 | VEd(cara) <= VRd,max | 56.585 | 294.84 | kN | 0.192 | sí | ELR20 | sí |
| VBM | tramo 1 cara izq. (X=0.40) | 0.634 | VEd(d) <= VRd,s | 27.323 | 112.916 | kN | 0.242 | sí | ELR20 | sí |
| VBM | tramo 1 cara izq. (X=0.40) | 0.634 | VEd(d) <= VRd,c (info: links needed?) | 27.323 | 39.001 | kN | 0.701 | sí | ELR20 | NO |
| VBM | tramo 1 cara izq. (X=0.40) | 0.4 | TEd/TRd,max + VEd/VRd,max <= 1 | 8.461 | 25.205 | kN·m | 0.523 | sí | ELR08 | NO |
| VBM | tramo 1 cara izq. (X=0.40) | 0.4 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 8.461 | 7.84 | kN·m | 2.498 | NO | ELR08 | NO |
| VBM | tramo 1 cara izq. (X=0.40) | 0.634 | estribos V + T (por rama del cerco) | 2.38 | 3.351 | cm²/m·rama | 0.71 | sí | ELR08 | NO |
| VBM | tramo 1 cara izq. (X=0.40) | 0.4 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 8.021 |  | kN·m | 0.794 | sí | ELR20 | NO |
| VBM | tramo 1 cara der. (X=6.25) | 6.25 | VEd(cara) <= VRd,max | 60.24 | 294.84 | kN | 0.204 | sí | ELR14 | sí |
| VBM | tramo 1 cara der. (X=6.25) | 6.016 | VEd(d) <= VRd,s | 58.976 | 112.916 | kN | 0.522 | sí | ELR14 | sí |
| VBM | tramo 1 cara der. (X=6.25) | 6.016 | VEd(d) <= VRd,c (info: links needed?) | 58.976 | 39.001 | kN | 1.512 | NO | ELR14 | NO |
| VBM | tramo 1 cara der. (X=6.25) | 6.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.794 | 25.205 | kN·m | 0.349 | sí | ELR08 | NO |
| VBM | tramo 1 cara der. (X=6.25) | 6.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.603 | 7.84 | kN·m | 2.004 | NO | ELR14 | NO |
| VBM | tramo 1 cara der. (X=6.25) | 6.016 | estribos V + T (por rama del cerco) | 2.807 | 3.351 | cm²/m·rama | 0.838 | sí | ELR20 | NO |
| VBM | tramo 1 cara der. (X=6.25) | 6.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.603 |  | kN·m | 1.054 | NO | ELR14 | NO |
| VBM | tramo 2 cara izq. (X=6.75) | 6.75 | VEd(cara) <= VRd,max | 56.97 | 294.84 | kN | 0.193 | sí | ELR14 | sí |
| VBM | tramo 2 cara izq. (X=6.75) | 6.984 | VEd(d) <= VRd,s | 55.709 | 112.916 | kN | 0.493 | sí | ELR14 | sí |
| VBM | tramo 2 cara izq. (X=6.75) | 6.984 | VEd(d) <= VRd,c (info: links needed?) | 55.709 | 39.001 | kN | 1.428 | NO | ELR14 | NO |
| VBM | tramo 2 cara izq. (X=6.75) | 6.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.577 | 25.205 | kN·m | 0.331 | sí | ELR20 | NO |
| VBM | tramo 2 cara izq. (X=6.75) | 6.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.39 | 7.84 | kN·m | 1.893 | NO | ELR14 | NO |
| VBM | tramo 2 cara izq. (X=6.75) | 6.984 | estribos V + T (por rama del cerco) | 2.657 | 3.351 | cm²/m·rama | 0.793 | sí | ELR20 | NO |
| VBM | tramo 2 cara izq. (X=6.75) | 6.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.39 |  | kN·m | 1.022 | NO | ELR14 | NO |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | VEd(cara) <= VRd,max | 48.374 | 294.84 | kN | 0.164 | sí | ELR20 | sí |
| VBM | tramo 2 cara der. (X=12.75) | 12.516 | VEd(d) <= VRd,s | 47.111 | 112.916 | kN | 0.417 | sí | ELR20 | sí |
| VBM | tramo 2 cara der. (X=12.75) | 12.516 | VEd(d) <= VRd,c (info: links needed?) | 47.111 | 39.001 | kN | 1.208 | NO | ELR20 | NO |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.489 | 25.205 | kN·m | 0.292 | sí | ELR08 | NO |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.01 | 7.84 | kN·m | 1.624 | NO | ELR20 | NO |
| VBM | tramo 2 cara der. (X=12.75) | 12.516 | estribos V + T (por rama del cerco) | 2.318 | 3.351 | cm²/m·rama | 0.692 | sí | ELR08 | NO |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.01 |  | kN·m | 0.823 | sí | ELR20 | NO |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | VEd(cara) <= VRd,max | 49.954 | 294.84 | kN | 0.169 | sí | ELR20 | sí |
| VBM | tramo 3 cara izq. (X=13.25) | 13.484 | VEd(d) <= VRd,s | 48.694 | 112.916 | kN | 0.431 | sí | ELR20 | sí |
| VBM | tramo 3 cara izq. (X=13.25) | 13.484 | VEd(d) <= VRd,c (info: links needed?) | 48.694 | 39.001 | kN | 1.248 | NO | ELR20 | NO |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.329 | 25.205 | kN·m | 0.29 | sí | ELR08 | NO |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.848 | 7.84 | kN·m | 1.644 | NO | ELR20 | NO |
| VBM | tramo 3 cara izq. (X=13.25) | 13.484 | estribos V + T (por rama del cerco) | 2.312 | 3.351 | cm²/m·rama | 0.69 | sí | ELR08 | NO |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.848 |  | kN·m | 0.838 | sí | ELR20 | NO |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | VEd(cara) <= VRd,max | 51.54 | 294.84 | kN | 0.175 | sí | ELR14 | sí |
| VBM | tramo 3 cara der. (X=19.25) | 19.016 | VEd(d) <= VRd,s | 50.278 | 112.916 | kN | 0.445 | sí | ELR14 | sí |
| VBM | tramo 3 cara der. (X=19.25) | 19.016 | VEd(d) <= VRd,c (info: links needed?) | 50.278 | 39.001 | kN | 1.289 | NO | ELR14 | NO |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.104 | 25.205 | kN·m | 0.294 | sí | ELR20 | NO |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.919 | 7.84 | kN·m | 1.694 | NO | ELR14 | NO |
| VBM | tramo 3 cara der. (X=19.25) | 19.016 | estribos V + T (por rama del cerco) | 2.358 | 3.351 | cm²/m·rama | 0.704 | sí | ELR20 | NO |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.919 |  | kN·m | 0.882 | sí | ELR14 | NO |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | VEd(cara) <= VRd,max | 51.54 | 294.84 | kN | 0.175 | sí | ELR14 | sí |
| VBM | tramo 4 cara izq. (X=19.75) | 19.984 | VEd(d) <= VRd,s | 50.278 | 112.916 | kN | 0.445 | sí | ELR14 | sí |
| VBM | tramo 4 cara izq. (X=19.75) | 19.984 | VEd(d) <= VRd,c (info: links needed?) | 50.278 | 39.001 | kN | 1.289 | NO | ELR14 | NO |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.104 | 25.205 | kN·m | 0.294 | sí | ELR20 | NO |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.919 | 7.84 | kN·m | 1.694 | NO | ELR14 | NO |
| VBM | tramo 4 cara izq. (X=19.75) | 19.984 | estribos V + T (por rama del cerco) | 2.358 | 3.351 | cm²/m·rama | 0.704 | sí | ELR20 | NO |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.919 |  | kN·m | 0.882 | sí | ELR14 | NO |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | VEd(cara) <= VRd,max | 49.954 | 294.84 | kN | 0.169 | sí | ELR20 | sí |
| VBM | tramo 4 cara der. (X=25.75) | 25.516 | VEd(d) <= VRd,s | 48.694 | 112.916 | kN | 0.431 | sí | ELR20 | sí |
| VBM | tramo 4 cara der. (X=25.75) | 25.516 | VEd(d) <= VRd,c (info: links needed?) | 48.694 | 39.001 | kN | 1.248 | NO | ELR20 | NO |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.322 | 25.205 | kN·m | 0.291 | sí | ELR08 | NO |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.848 | 7.84 | kN·m | 1.644 | NO | ELR20 | NO |
| VBM | tramo 4 cara der. (X=25.75) | 25.516 | estribos V + T (por rama del cerco) | 2.318 | 3.351 | cm²/m·rama | 0.692 | sí | ELR08 | NO |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.848 |  | kN·m | 0.838 | sí | ELR20 | NO |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | VEd(cara) <= VRd,max | 48.374 | 294.84 | kN | 0.164 | sí | ELR20 | sí |
| VBM | tramo 5 cara izq. (X=26.25) | 26.484 | VEd(d) <= VRd,s | 47.111 | 112.916 | kN | 0.417 | sí | ELR20 | sí |
| VBM | tramo 5 cara izq. (X=26.25) | 26.484 | VEd(d) <= VRd,c (info: links needed?) | 47.111 | 39.001 | kN | 1.208 | NO | ELR20 | NO |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.49 | 25.205 | kN·m | 0.291 | sí | ELR08 | NO |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.01 | 7.84 | kN·m | 1.624 | NO | ELR20 | NO |
| VBM | tramo 5 cara izq. (X=26.25) | 26.484 | estribos V + T (por rama del cerco) | 2.313 | 3.351 | cm²/m·rama | 0.69 | sí | ELR08 | NO |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.01 |  | kN·m | 0.823 | sí | ELR20 | NO |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | VEd(cara) <= VRd,max | 56.97 | 294.84 | kN | 0.193 | sí | ELR14 | sí |
| VBM | tramo 5 cara der. (X=32.25) | 32.016 | VEd(d) <= VRd,s | 55.709 | 112.916 | kN | 0.493 | sí | ELR14 | sí |
| VBM | tramo 5 cara der. (X=32.25) | 32.016 | VEd(d) <= VRd,c (info: links needed?) | 55.709 | 39.001 | kN | 1.428 | NO | ELR14 | NO |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.577 | 25.205 | kN·m | 0.331 | sí | ELR20 | NO |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.39 | 7.84 | kN·m | 1.893 | NO | ELR14 | NO |
| VBM | tramo 5 cara der. (X=32.25) | 32.016 | estribos V + T (por rama del cerco) | 2.657 | 3.351 | cm²/m·rama | 0.793 | sí | ELR20 | NO |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.39 |  | kN·m | 1.022 | NO | ELR14 | NO |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | VEd(cara) <= VRd,max | 60.24 | 294.84 | kN | 0.204 | sí | ELR14 | sí |
| VBM | tramo 6 cara izq. (X=32.75) | 32.984 | VEd(d) <= VRd,s | 58.976 | 112.916 | kN | 0.522 | sí | ELR14 | sí |
| VBM | tramo 6 cara izq. (X=32.75) | 32.984 | VEd(d) <= VRd,c (info: links needed?) | 58.976 | 39.001 | kN | 1.512 | NO | ELR14 | NO |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.737 | 25.205 | kN·m | 0.349 | sí | ELR20 | NO |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.603 | 7.84 | kN·m | 2.004 | NO | ELR14 | NO |
| VBM | tramo 6 cara izq. (X=32.75) | 32.984 | estribos V + T (por rama del cerco) | 2.807 | 3.351 | cm²/m·rama | 0.838 | sí | ELR20 | NO |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.603 |  | kN·m | 1.054 | NO | ELR14 | NO |
| VBM | tramo 6 cara der. (X=38.60) | 38.6 | VEd(cara) <= VRd,max | 56.585 | 294.84 | kN | 0.192 | sí | ELR20 | sí |
| VBM | tramo 6 cara der. (X=38.60) | 38.366 | VEd(d) <= VRd,s | 27.323 | 112.916 | kN | 0.242 | sí | ELR20 | sí |
| VBM | tramo 6 cara der. (X=38.60) | 38.366 | VEd(d) <= VRd,c (info: links needed?) | 27.323 | 39.001 | kN | 0.701 | sí | ELR20 | NO |
| VBM | tramo 6 cara der. (X=38.60) | 38.6 | TEd/TRd,max + VEd/VRd,max <= 1 | 8.467 | 25.205 | kN·m | 0.525 | sí | ELR08 | NO |
| VBM | tramo 6 cara der. (X=38.60) | 38.6 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 8.467 | 7.84 | kN·m | 2.508 | NO | ELR08 | NO |
| VBM | tramo 6 cara der. (X=38.60) | 38.366 | estribos V + T (por rama del cerco) | 2.392 | 3.351 | cm²/m·rama | 0.714 | sí | ELR08 | NO |
| VBM | tramo 6 cara der. (X=38.60) | 38.6 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 8.467 |  | kN·m | 0.796 | sí | ELR08 | NO |
| VBT | tramo 1 cara izq. (X=0.40) | 0.4 | VEd(cara) <= VRd,max | 57.187 | 294.84 | kN | 0.194 | sí | ELR08 | sí |
| VBT | tramo 1 cara izq. (X=0.40) | 0.634 | VEd(d) <= VRd,s | 25.918 | 112.916 | kN | 0.23 | sí | ELR08 | sí |
| VBT | tramo 1 cara izq. (X=0.40) | 0.634 | VEd(d) <= VRd,c (info: links needed?) | 25.918 | 39.001 | kN | 0.664 | sí | ELR08 | NO |
| VBT | tramo 1 cara izq. (X=0.40) | 0.4 | TEd/TRd,max + VEd/VRd,max <= 1 | 8.146 | 25.205 | kN·m | 0.515 | sí | ELR14 | NO |
| VBT | tramo 1 cara izq. (X=0.40) | 0.4 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 8.025 | 7.84 | kN·m | 2.49 | NO | ELR08 | NO |
| VBT | tramo 1 cara izq. (X=0.40) | 0.634 | estribos V + T (por rama del cerco) | 2.277 | 3.351 | cm²/m·rama | 0.679 | sí | ELR14 | NO |
| VBT | tramo 1 cara izq. (X=0.40) | 0.4 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 8.025 |  | kN·m | 0.808 | sí | ELR08 | NO |
| VBT | tramo 1 cara der. (X=6.25) | 6.25 | VEd(cara) <= VRd,max | 62.955 | 294.84 | kN | 0.213 | sí | ELR08 | sí |
| VBT | tramo 1 cara der. (X=6.25) | 6.016 | VEd(d) <= VRd,s | 61.694 | 112.916 | kN | 0.546 | sí | ELR08 | sí |
| VBT | tramo 1 cara der. (X=6.25) | 6.016 | VEd(d) <= VRd,c (info: links needed?) | 61.694 | 39.001 | kN | 1.582 | NO | ELR08 | NO |
| VBT | tramo 1 cara der. (X=6.25) | 6.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.577 | 25.205 | kN·m | 0.349 | sí | ELR20 | NO |
| VBT | tramo 1 cara der. (X=6.25) | 6.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.577 | 7.84 | kN·m | 2.023 | NO | ELR20 | NO |
| VBT | tramo 1 cara der. (X=6.25) | 6.016 | estribos V + T (por rama del cerco) | 2.814 | 3.351 | cm²/m·rama | 0.84 | sí | ELR20 | NO |
| VBT | tramo 1 cara der. (X=6.25) | 6.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.144 |  | kN·m | 1.056 | NO | ELR08 | NO |
| VBT | tramo 2 cara izq. (X=6.75) | 6.75 | VEd(cara) <= VRd,max | 59.754 | 294.84 | kN | 0.203 | sí | ELR08 | sí |
| VBT | tramo 2 cara izq. (X=6.75) | 6.984 | VEd(d) <= VRd,s | 58.49 | 112.916 | kN | 0.518 | sí | ELR08 | sí |
| VBT | tramo 2 cara izq. (X=6.75) | 6.984 | VEd(d) <= VRd,c (info: links needed?) | 58.49 | 39.001 | kN | 1.5 | NO | ELR08 | NO |
| VBT | tramo 2 cara izq. (X=6.75) | 6.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.376 | 25.205 | kN·m | 0.33 | sí | ELR20 | NO |
| VBT | tramo 2 cara izq. (X=6.75) | 6.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.052 | 7.84 | kN·m | 1.921 | NO | ELR08 | NO |
| VBT | tramo 2 cara izq. (X=6.75) | 6.984 | estribos V + T (por rama del cerco) | 2.654 | 3.351 | cm²/m·rama | 0.792 | sí | ELR20 | NO |
| VBT | tramo 2 cara izq. (X=6.75) | 6.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.052 |  | kN·m | 1.03 | NO | ELR08 | NO |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | VEd(cara) <= VRd,max | 49.953 | 294.84 | kN | 0.169 | sí | ELR08 | sí |
| VBT | tramo 2 cara der. (X=12.75) | 12.516 | VEd(d) <= VRd,s | 48.691 | 112.916 | kN | 0.431 | sí | ELR08 | sí |
| VBT | tramo 2 cara der. (X=12.75) | 12.516 | VEd(d) <= VRd,c (info: links needed?) | 48.691 | 39.001 | kN | 1.248 | NO | ELR08 | NO |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.998 | 25.205 | kN·m | 0.283 | sí | ELR14 | NO |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.845 | 7.84 | kN·m | 1.644 | NO | ELR08 | NO |
| VBT | tramo 2 cara der. (X=12.75) | 12.516 | estribos V + T (por rama del cerco) | 2.271 | 3.351 | cm²/m·rama | 0.678 | sí | ELR14 | NO |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.845 |  | kN·m | 0.83 | sí | ELR08 | NO |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | VEd(cara) <= VRd,max | 51.692 | 294.84 | kN | 0.175 | sí | ELR08 | sí |
| VBT | tramo 3 cara izq. (X=13.25) | 13.484 | VEd(d) <= VRd,s | 50.429 | 112.916 | kN | 0.447 | sí | ELR08 | sí |
| VBT | tramo 3 cara izq. (X=13.25) | 13.484 | VEd(d) <= VRd,c (info: links needed?) | 50.429 | 39.001 | kN | 1.293 | NO | ELR08 | NO |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.84 | 25.205 | kN·m | 0.282 | sí | ELR14 | NO |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.685 | 7.84 | kN·m | 1.668 | NO | ELR08 | NO |
| VBT | tramo 3 cara izq. (X=13.25) | 13.484 | estribos V + T (por rama del cerco) | 2.275 | 3.351 | cm²/m·rama | 0.679 | sí | ELR08 | NO |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.685 |  | kN·m | 0.849 | sí | ELR08 | NO |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | VEd(cara) <= VRd,max | 53.971 | 294.84 | kN | 0.183 | sí | ELR08 | sí |
| VBT | tramo 3 cara der. (X=19.25) | 19.016 | VEd(d) <= VRd,s | 52.71 | 112.916 | kN | 0.467 | sí | ELR08 | sí |
| VBT | tramo 3 cara der. (X=19.25) | 19.016 | VEd(d) <= VRd,c (info: links needed?) | 52.71 | 39.001 | kN | 1.351 | NO | ELR08 | NO |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.954 | 25.205 | kN·m | 0.294 | sí | ELR20 | NO |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.64 | 7.84 | kN·m | 1.721 | NO | ELR08 | NO |
| VBT | tramo 3 cara der. (X=19.25) | 19.016 | estribos V + T (por rama del cerco) | 2.37 | 3.351 | cm²/m·rama | 0.707 | sí | ELR20 | NO |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.64 |  | kN·m | 0.889 | sí | ELR08 | NO |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | VEd(cara) <= VRd,max | 54.214 | 294.84 | kN | 0.184 | sí | ELR08 | sí |
| VBT | tramo 4 cara izq. (X=19.75) | 19.984 | VEd(d) <= VRd,s | 52.953 | 112.916 | kN | 0.469 | sí | ELR08 | sí |
| VBT | tramo 4 cara izq. (X=19.75) | 19.984 | VEd(d) <= VRd,c (info: links needed?) | 52.953 | 39.001 | kN | 1.358 | NO | ELR08 | NO |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.954 | 25.205 | kN·m | 0.294 | sí | ELR20 | NO |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.638 | 7.84 | kN·m | 1.727 | NO | ELR08 | NO |
| VBT | tramo 4 cara izq. (X=19.75) | 19.984 | estribos V + T (por rama del cerco) | 2.37 | 3.351 | cm²/m·rama | 0.707 | sí | ELR20 | NO |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.638 |  | kN·m | 0.895 | sí | ELR08 | NO |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | VEd(cara) <= VRd,max | 51.39 | 294.84 | kN | 0.174 | sí | ELR08 | sí |
| VBT | tramo 4 cara der. (X=25.75) | 25.516 | VEd(d) <= VRd,s | 50.128 | 112.916 | kN | 0.444 | sí | ELR08 | sí |
| VBT | tramo 4 cara der. (X=25.75) | 25.516 | VEd(d) <= VRd,c (info: links needed?) | 50.128 | 39.001 | kN | 1.285 | NO | ELR08 | NO |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.84 | 25.205 | kN·m | 0.282 | sí | ELR14 | NO |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.694 | 7.84 | kN·m | 1.661 | NO | ELR08 | NO |
| VBT | tramo 4 cara der. (X=25.75) | 25.516 | estribos V + T (por rama del cerco) | 2.27 | 3.351 | cm²/m·rama | 0.677 | sí | ELR14 | NO |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.694 |  | kN·m | 0.843 | sí | ELR08 | NO |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | VEd(cara) <= VRd,max | 50.139 | 294.84 | kN | 0.17 | sí | ELR08 | sí |
| VBT | tramo 5 cara izq. (X=26.25) | 26.484 | VEd(d) <= VRd,s | 48.877 | 112.916 | kN | 0.433 | sí | ELR08 | sí |
| VBT | tramo 5 cara izq. (X=26.25) | 26.484 | VEd(d) <= VRd,c (info: links needed?) | 48.877 | 39.001 | kN | 1.253 | NO | ELR08 | NO |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 2.998 | 25.205 | kN·m | 0.283 | sí | ELR14 | NO |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 2.85 | 7.84 | kN·m | 1.649 | NO | ELR08 | NO |
| VBT | tramo 5 cara izq. (X=26.25) | 26.484 | estribos V + T (por rama del cerco) | 2.277 | 3.351 | cm²/m·rama | 0.68 | sí | ELR08 | NO |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 2.85 |  | kN·m | 0.834 | sí | ELR08 | NO |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | VEd(cara) <= VRd,max | 59.386 | 294.84 | kN | 0.201 | sí | ELR08 | sí |
| VBT | tramo 5 cara der. (X=32.25) | 32.016 | VEd(d) <= VRd,s | 58.122 | 112.916 | kN | 0.515 | sí | ELR08 | sí |
| VBT | tramo 5 cara der. (X=32.25) | 32.016 | VEd(d) <= VRd,c (info: links needed?) | 58.122 | 39.001 | kN | 1.49 | NO | ELR08 | NO |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.376 | 25.205 | kN·m | 0.33 | sí | ELR20 | NO |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.068 | 7.84 | kN·m | 1.914 | NO | ELR08 | NO |
| VBT | tramo 5 cara der. (X=32.25) | 32.016 | estribos V + T (por rama del cerco) | 2.654 | 3.351 | cm²/m·rama | 0.792 | sí | ELR20 | NO |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.068 |  | kN·m | 1.024 | NO | ELR08 | NO |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | VEd(cara) <= VRd,max | 63.072 | 294.84 | kN | 0.214 | sí | ELR08 | sí |
| VBT | tramo 6 cara izq. (X=32.75) | 32.984 | VEd(d) <= VRd,s | 61.811 | 112.916 | kN | 0.547 | sí | ELR08 | sí |
| VBT | tramo 6 cara izq. (X=32.75) | 32.984 | VEd(d) <= VRd,c (info: links needed?) | 61.811 | 39.001 | kN | 1.585 | NO | ELR08 | NO |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | TEd/TRd,max + VEd/VRd,max <= 1 | 3.577 | 25.205 | kN·m | 0.349 | sí | ELR20 | NO |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 3.577 | 7.84 | kN·m | 2.023 | NO | ELR20 | NO |
| VBT | tramo 6 cara izq. (X=32.75) | 32.984 | estribos V + T (por rama del cerco) | 2.814 | 3.351 | cm²/m·rama | 0.84 | sí | ELR20 | NO |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 3.16 |  | kN·m | 1.06 | NO | ELR08 | NO |
| VBT | tramo 6 cara der. (X=38.60) | 38.6 | VEd(cara) <= VRd,max | 56.87 | 294.84 | kN | 0.193 | sí | ELR08 | sí |
| VBT | tramo 6 cara der. (X=38.60) | 38.366 | VEd(d) <= VRd,s | 25.684 | 112.916 | kN | 0.228 | sí | ELR14 | sí |
| VBT | tramo 6 cara der. (X=38.60) | 38.366 | VEd(d) <= VRd,c (info: links needed?) | 25.684 | 39.001 | kN | 0.658 | sí | ELR14 | NO |
| VBT | tramo 6 cara der. (X=38.60) | 38.6 | TEd/TRd,max + VEd/VRd,max <= 1 | 8.146 | 25.205 | kN·m | 0.515 | sí | ELR14 | NO |
| VBT | tramo 6 cara der. (X=38.60) | 38.6 | TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?) | 8.146 | 7.84 | kN·m | 2.489 | NO | ELR14 | NO |
| VBT | tramo 6 cara der. (X=38.60) | 38.366 | estribos V + T (por rama del cerco) | 2.277 | 3.351 | cm²/m·rama | 0.679 | sí | ELR14 | NO |
| VBT | tramo 6 cara der. (X=38.60) | 38.6 | M/MRd + ΣAsl,T(cordón)/As <= 1 | 8.146 |  | kN·m | 0.806 | sí | ELR14 | NO |

## Anexo: Disposiciones (caso final CE-ROM)

| member | section | pos_m | check | demand | capacity | unit | eta | ok | combo | in_verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | todas |  | As(top) >= As,min (z 0.8h) | 7.418 | 15.708 | cm² | 0.472 | sí |  | sí |
| VT1 | todas |  | As(top) >= As,min (z 0.9d) | 7.555 | 15.708 | cm² | 0.481 | sí |  | NO |
| VT1 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 194 | cm² | 0.081 | sí |  | sí |
| VT1 | todas |  | separación libre (top) >= smin | 25 | 145 | mm | 0.172 | sí |  | sí |
| VT1 | todas |  | separación (top) <= 350 mm | 165 | 350 | mm | 0.471 | sí |  | sí |
| VT1 | todas |  | As(bottom) >= As,min (z 0.8h) | 8.071 | 18.85 | cm² | 0.428 | sí |  | sí |
| VT1 | todas |  | As(bottom) >= As,min (z 0.9d) | 8.221 | 18.85 | cm² | 0.436 | sí |  | NO |
| VT1 | todas |  | As(bottom) <= As,max = 0.04 Ac | 18.85 | 194 | cm² | 0.097 | sí |  | sí |
| VT1 | todas |  | separación libre (bottom) >= smin | 25 | 130 | mm | 0.192 | sí |  | sí |
| VT1 | todas |  | separación (bottom) <= 350 mm | 165 | 350 | mm | 0.471 | sí |  | sí |
| VT1 | todas |  | rho_w >= rho_w,min | 7.573 | 23.562 | cm²/m | 0.321 | sí |  | sí |
| VT1 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT1 | todas |  | st <= st,max = 0.75d <= 600 | 345 | 360 | mm | 0.958 | sí |  | sí |
| VT1 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 256.019 | mm | 0.391 | sí |  | sí |
| VT2 | todas |  | As(top) >= As,min (z 0.8h) | 4.993 | 15.708 | cm² | 0.318 | sí |  | sí |
| VT2 | todas |  | As(top) >= As,min (z 0.9d) | 5.085 | 15.708 | cm² | 0.324 | sí |  | NO |
| VT2 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 146 | cm² | 0.108 | sí |  | sí |
| VT2 | todas |  | separación libre (top) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT2 | todas |  | separación (top) <= 350 mm | 97.5 | 350 | mm | 0.279 | sí |  | sí |
| VT2 | todas |  | As(bottom) >= As,min (z 0.8h) | 6.253 | 21.991 | cm² | 0.284 | sí |  | sí |
| VT2 | todas |  | As(bottom) >= As,min (z 0.9d) | 6.369 | 21.991 | cm² | 0.29 | sí |  | NO |
| VT2 | todas |  | As(bottom) <= As,max = 0.04 Ac | 21.991 | 146 | cm² | 0.151 | sí |  | sí |
| VT2 | todas |  | separación libre (bottom) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT2 | todas |  | separación (bottom) <= 350 mm | 150 | 350 | mm | 0.429 | sí |  | sí |
| VT2 | todas |  | rho_w >= rho_w,min | 4.733 | 23.562 | cm²/m | 0.201 | sí |  | sí |
| VT2 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT2 | todas |  | st <= st,max = 0.75d <= 600 | 195 | 360 | mm | 0.542 | sí |  | sí |
| VT2 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 192.5 | mm | 0.519 | sí |  | NO |
| VT3 | todas |  | As(top) >= As,min (z 0.8h) | 4.993 | 15.708 | cm² | 0.318 | sí |  | sí |
| VT3 | todas |  | As(top) >= As,min (z 0.9d) | 5.085 | 15.708 | cm² | 0.324 | sí |  | NO |
| VT3 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 146 | cm² | 0.108 | sí |  | sí |
| VT3 | todas |  | separación libre (top) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT3 | todas |  | separación (top) <= 350 mm | 97.5 | 350 | mm | 0.279 | sí |  | sí |
| VT3 | todas |  | As(bottom) >= As,min (z 0.8h) | 6.253 | 21.991 | cm² | 0.284 | sí |  | sí |
| VT3 | todas |  | As(bottom) >= As,min (z 0.9d) | 6.369 | 21.991 | cm² | 0.29 | sí |  | NO |
| VT3 | todas |  | As(bottom) <= As,max = 0.04 Ac | 21.991 | 146 | cm² | 0.151 | sí |  | sí |
| VT3 | todas |  | separación libre (bottom) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT3 | todas |  | separación (bottom) <= 350 mm | 150 | 350 | mm | 0.429 | sí |  | sí |
| VT3 | todas |  | rho_w >= rho_w,min | 4.733 | 23.562 | cm²/m | 0.201 | sí |  | sí |
| VT3 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT3 | todas |  | st <= st,max = 0.75d <= 600 | 195 | 360 | mm | 0.542 | sí |  | sí |
| VT3 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 192.5 | mm | 0.519 | sí |  | NO |
| VT4 | todas |  | As(top) >= As,min (z 0.8h) | 4.993 | 15.708 | cm² | 0.318 | sí |  | sí |
| VT4 | todas |  | As(top) >= As,min (z 0.9d) | 5.085 | 15.708 | cm² | 0.324 | sí |  | NO |
| VT4 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 146 | cm² | 0.108 | sí |  | sí |
| VT4 | todas |  | separación libre (top) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT4 | todas |  | separación (top) <= 350 mm | 97.5 | 350 | mm | 0.279 | sí |  | sí |
| VT4 | todas |  | As(bottom) >= As,min (z 0.8h) | 6.253 | 21.991 | cm² | 0.284 | sí |  | sí |
| VT4 | todas |  | As(bottom) >= As,min (z 0.9d) | 6.369 | 21.991 | cm² | 0.29 | sí |  | NO |
| VT4 | todas |  | As(bottom) <= As,max = 0.04 Ac | 21.991 | 146 | cm² | 0.151 | sí |  | sí |
| VT4 | todas |  | separación libre (bottom) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT4 | todas |  | separación (bottom) <= 350 mm | 150 | 350 | mm | 0.429 | sí |  | sí |
| VT4 | todas |  | rho_w >= rho_w,min | 4.733 | 23.562 | cm²/m | 0.201 | sí |  | sí |
| VT4 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT4 | todas |  | st <= st,max = 0.75d <= 600 | 195 | 360 | mm | 0.542 | sí |  | sí |
| VT4 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 192.5 | mm | 0.519 | sí |  | NO |
| VT5 | todas |  | As(top) >= As,min (z 0.8h) | 4.993 | 15.708 | cm² | 0.318 | sí |  | sí |
| VT5 | todas |  | As(top) >= As,min (z 0.9d) | 5.085 | 15.708 | cm² | 0.324 | sí |  | NO |
| VT5 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 146 | cm² | 0.108 | sí |  | sí |
| VT5 | todas |  | separación libre (top) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT5 | todas |  | separación (top) <= 350 mm | 97.5 | 350 | mm | 0.279 | sí |  | sí |
| VT5 | todas |  | As(bottom) >= As,min (z 0.8h) | 6.253 | 21.991 | cm² | 0.284 | sí |  | sí |
| VT5 | todas |  | As(bottom) >= As,min (z 0.9d) | 6.369 | 21.991 | cm² | 0.29 | sí |  | NO |
| VT5 | todas |  | As(bottom) <= As,max = 0.04 Ac | 21.991 | 146 | cm² | 0.151 | sí |  | sí |
| VT5 | todas |  | separación libre (bottom) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT5 | todas |  | separación (bottom) <= 350 mm | 150 | 350 | mm | 0.429 | sí |  | sí |
| VT5 | todas |  | rho_w >= rho_w,min | 4.733 | 23.562 | cm²/m | 0.201 | sí |  | sí |
| VT5 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT5 | todas |  | st <= st,max = 0.75d <= 600 | 195 | 360 | mm | 0.542 | sí |  | sí |
| VT5 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 192.5 | mm | 0.519 | sí |  | NO |
| VT6 | todas |  | As(top) >= As,min (z 0.8h) | 4.993 | 15.708 | cm² | 0.318 | sí |  | sí |
| VT6 | todas |  | As(top) >= As,min (z 0.9d) | 5.085 | 15.708 | cm² | 0.324 | sí |  | NO |
| VT6 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 146 | cm² | 0.108 | sí |  | sí |
| VT6 | todas |  | separación libre (top) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT6 | todas |  | separación (top) <= 350 mm | 97.5 | 350 | mm | 0.279 | sí |  | sí |
| VT6 | todas |  | As(bottom) >= As,min (z 0.8h) | 6.253 | 21.991 | cm² | 0.284 | sí |  | sí |
| VT6 | todas |  | As(bottom) >= As,min (z 0.9d) | 6.369 | 21.991 | cm² | 0.29 | sí |  | NO |
| VT6 | todas |  | As(bottom) <= As,max = 0.04 Ac | 21.991 | 146 | cm² | 0.151 | sí |  | sí |
| VT6 | todas |  | separación libre (bottom) >= smin | 25 | 62.5 | mm | 0.4 | sí |  | sí |
| VT6 | todas |  | separación (bottom) <= 350 mm | 150 | 350 | mm | 0.429 | sí |  | sí |
| VT6 | todas |  | rho_w >= rho_w,min | 4.733 | 23.562 | cm²/m | 0.201 | sí |  | sí |
| VT6 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT6 | todas |  | st <= st,max = 0.75d <= 600 | 195 | 360 | mm | 0.542 | sí |  | sí |
| VT6 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 192.5 | mm | 0.519 | sí |  | NO |
| VT7 | todas |  | As(top) >= As,min (z 0.8h) | 7.418 | 15.708 | cm² | 0.472 | sí |  | sí |
| VT7 | todas |  | As(top) >= As,min (z 0.9d) | 7.555 | 15.708 | cm² | 0.481 | sí |  | NO |
| VT7 | todas |  | As(top) <= As,max = 0.04 Ac | 15.708 | 194 | cm² | 0.081 | sí |  | sí |
| VT7 | todas |  | separación libre (top) >= smin | 25 | 145 | mm | 0.172 | sí |  | sí |
| VT7 | todas |  | separación (top) <= 350 mm | 165 | 350 | mm | 0.471 | sí |  | sí |
| VT7 | todas |  | As(bottom) >= As,min (z 0.8h) | 8.071 | 18.85 | cm² | 0.428 | sí |  | sí |
| VT7 | todas |  | As(bottom) >= As,min (z 0.9d) | 8.221 | 18.85 | cm² | 0.436 | sí |  | NO |
| VT7 | todas |  | As(bottom) <= As,max = 0.04 Ac | 18.85 | 194 | cm² | 0.097 | sí |  | sí |
| VT7 | todas |  | separación libre (bottom) >= smin | 25 | 130 | mm | 0.192 | sí |  | sí |
| VT7 | todas |  | separación (bottom) <= 350 mm | 165 | 350 | mm | 0.471 | sí |  | sí |
| VT7 | todas |  | rho_w >= rho_w,min | 7.573 | 23.562 | cm²/m | 0.321 | sí |  | sí |
| VT7 | todas |  | s <= sl,max = 0.75d | 100 | 360 | mm | 0.278 | sí |  | sí |
| VT7 | todas |  | st <= st,max = 0.75d <= 600 | 345 | 360 | mm | 0.958 | sí |  | sí |
| VT7 | todas |  | s <= uk/8, min(b, h) (torsión) | 100 | 256.019 | mm | 0.391 | sí |  | sí |
| VBM | todas |  | As(top) >= As,min (z 0.8h) | 1.5 | 4.021 | cm² | 0.373 | sí |  | sí |
| VBM | todas |  | As(top) >= As,min (z 0.9d) | 1.709 | 4.021 | cm² | 0.425 | sí |  | NO |
| VBM | todas |  | As(top) <= As,max = 0.04 Ac | 4.021 | 30 | cm² | 0.134 | sí |  | sí |
| VBM | todas |  | separación libre (top) >= smin | 25 | 102 | mm | 0.245 | sí |  | sí |
| VBM | todas |  | separación (top) <= 350 mm | 118 | 350 | mm | 0.337 | sí |  | sí |
| VBM | todas |  | As(bottom) >= As,min (z 0.8h) | 1.5 | 4.021 | cm² | 0.373 | sí |  | sí |
| VBM | todas |  | As(bottom) >= As,min (z 0.9d) | 1.709 | 4.021 | cm² | 0.425 | sí |  | NO |
| VBM | todas |  | As(bottom) <= As,max = 0.04 Ac | 4.021 | 30 | cm² | 0.134 | sí |  | sí |
| VBM | todas |  | separación libre (bottom) >= smin | 25 | 102 | mm | 0.245 | sí |  | sí |
| VBM | todas |  | separación (bottom) <= 350 mm | 118 | 350 | mm | 0.337 | sí |  | sí |
| VBM | todas |  | rho_w >= rho_w,min | 2.366 | 6.702 | cm²/m | 0.353 | sí |  | sí |
| VBM | todas |  | s <= sl,max = 0.75d | 150 | 175.5 | mm | 0.855 | sí |  | sí |
| VBM | todas |  | st <= st,max = 0.75d <= 600 | 142 | 175.5 | mm | 0.809 | sí |  | sí |
| VBM | todas |  | s <= uk/8, min(b, h) (torsión) | 150 | 71.5 | mm | 2.098 | NO |  | NO |
| VBT | todas |  | As(top) >= As,min (z 0.8h) | 1.5 | 4.021 | cm² | 0.373 | sí |  | sí |
| VBT | todas |  | As(top) >= As,min (z 0.9d) | 1.709 | 4.021 | cm² | 0.425 | sí |  | NO |
| VBT | todas |  | As(top) <= As,max = 0.04 Ac | 4.021 | 30 | cm² | 0.134 | sí |  | sí |
| VBT | todas |  | separación libre (top) >= smin | 25 | 102 | mm | 0.245 | sí |  | sí |
| VBT | todas |  | separación (top) <= 350 mm | 118 | 350 | mm | 0.337 | sí |  | sí |
| VBT | todas |  | As(bottom) >= As,min (z 0.8h) | 1.5 | 4.021 | cm² | 0.373 | sí |  | sí |
| VBT | todas |  | As(bottom) >= As,min (z 0.9d) | 1.709 | 4.021 | cm² | 0.425 | sí |  | NO |
| VBT | todas |  | As(bottom) <= As,max = 0.04 Ac | 4.021 | 30 | cm² | 0.134 | sí |  | sí |
| VBT | todas |  | separación libre (bottom) >= smin | 25 | 102 | mm | 0.245 | sí |  | sí |
| VBT | todas |  | separación (bottom) <= 350 mm | 118 | 350 | mm | 0.337 | sí |  | sí |
| VBT | todas |  | rho_w >= rho_w,min | 2.366 | 6.702 | cm²/m | 0.353 | sí |  | sí |
| VBT | todas |  | s <= sl,max = 0.75d | 150 | 175.5 | mm | 0.855 | sí |  | sí |
| VBT | todas |  | st <= st,max = 0.75d <= 600 | 142 | 175.5 | mm | 0.809 | sí |  | sí |
| VBT | todas |  | s <= uk/8, min(b, h) (torsión) | 150 | 71.5 | mm | 2.098 | NO |  | NO |

## Anexo: ELS tensiones y fisuración (caso final CE-ROM)

| member | section | pos_m | check | demand | capacity | unit | eta | ok | combo | in_verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | sag | 1.725 | sigma_ct <= fctm (QP) | 1.556 | 3.21 | MPa | 0.485 | sí | QP(psi2=0.8) | NO |
| VT1 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT1 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.042 | 3.21 | MPa | 0.013 | sí | QP(psi2=0.8) | NO |
| VT1 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT1 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.065 | 3.21 | MPa | 0.643 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT1 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT1 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.358 | 3.21 | MPa | 0.735 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT1 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT1 | sag | 3.25 | sigma_c <= 0.6 fck (característica ELS01-08) | 9.211 | 21 | MPa | 0.439 | sí | ELS04 | sí |
| VT1 | sag | 3.25 | sigma_s <= 0.8 fyk (característica ELS01-08) | 203.563 | 400 | MPa | 0.509 | sí | ELS04 | sí |
| VT1 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 10.545 | 21 | MPa | 0.502 | sí | ELS04 | sí |
| VT1 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 285.828 | 400 | MPa | 0.715 | sí | ELS04 | sí |
| VT1 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 1.698 | 15.75 | MPa | 0.108 | sí | QP(psi2=0.8) | NO |
| VT1 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.038 | 15.75 | MPa | 0.002 | sí | QP(psi2=0.8) | NO |
| VT2 | sag | 1.725 | sigma_ct <= fctm (QP) | 3.893 | 3.21 | MPa | 1.213 | NO | QP(psi2=0.8) | NO |
| VT2 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0.172 | 0.1 | mm | 1.72 | NO | QP(psi2=0.8) | sí |
| VT2 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.191 | 3.21 | MPa | 0.059 | sí | QP(psi2=0.8) | NO |
| VT2 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT2 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 4.204 | 3.21 | MPa | 1.31 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT2 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.186 | 0.1 | mm | 1.858 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT2 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.881 | 3.21 | MPa | 0.898 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT2 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT2 | sag | 2.462 | sigma_c <= 0.6 fck (característica ELS01-08) | 13.059 | 21 | MPa | 0.622 | sí | ELS04 | sí |
| VT2 | sag | 2.462 | sigma_s <= 0.8 fyk (característica ELS01-08) | 215.413 | 400 | MPa | 0.538 | sí | ELS04 | sí |
| VT2 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 9.518 | 21 | MPa | 0.453 | sí | ELS04 | sí |
| VT2 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 243.399 | 400 | MPa | 0.609 | sí | ELS04 | sí |
| VT2 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 9.278 | 15.75 | MPa | 0.589 | sí | QP(psi2=0.8) | NO |
| VT2 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.152 | 15.75 | MPa | 0.01 | sí | QP(psi2=0.8) | NO |
| VT3 | sag | 1.725 | sigma_ct <= fctm (QP) | 3.508 | 3.21 | MPa | 1.093 | NO | QP(psi2=0.8) | NO |
| VT3 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0.155 | 0.1 | mm | 1.55 | NO | QP(psi2=0.8) | sí |
| VT3 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.17 | 3.21 | MPa | 0.053 | sí | QP(psi2=0.8) | NO |
| VT3 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT3 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 3.741 | 3.21 | MPa | 1.166 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT3 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.165 | 0.1 | mm | 1.653 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT3 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 3.277 | 3.21 | MPa | 1.021 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT3 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.156 | 0.1 | mm | 1.56 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT3 | sag | 2.708 | sigma_c <= 0.6 fck (característica ELS01-08) | 12.095 | 21 | MPa | 0.576 | sí | ELS04 | sí |
| VT3 | sag | 2.708 | sigma_s <= 0.8 fyk (característica ELS01-08) | 199.502 | 400 | MPa | 0.499 | sí | ELS04 | sí |
| VT3 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 10.878 | 21 | MPa | 0.518 | sí | ELS04 | sí |
| VT3 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 278.204 | 400 | MPa | 0.696 | sí | ELS04 | sí |
| VT3 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 8.359 | 15.75 | MPa | 0.531 | sí | QP(psi2=0.8) | NO |
| VT3 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.136 | 15.75 | MPa | 0.009 | sí | QP(psi2=0.8) | NO |
| VT4 | sag | 1.725 | sigma_ct <= fctm (QP) | 3.584 | 3.21 | MPa | 1.117 | NO | QP(psi2=0.8) | NO |
| VT4 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0.158 | 0.1 | mm | 1.584 | NO | QP(psi2=0.8) | sí |
| VT4 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.182 | 3.21 | MPa | 0.057 | sí | QP(psi2=0.8) | NO |
| VT4 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT4 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 3.903 | 3.21 | MPa | 1.216 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT4 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.172 | 0.1 | mm | 1.724 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT4 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.784 | 3.21 | MPa | 0.867 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT4 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT4 | sag | 2.708 | sigma_c <= 0.6 fck (característica ELS01-08) | 12.333 | 21 | MPa | 0.587 | sí | ELS04 | sí |
| VT4 | sag | 2.708 | sigma_s <= 0.8 fyk (característica ELS01-08) | 203.433 | 400 | MPa | 0.509 | sí | ELS04 | sí |
| VT4 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 9.198 | 21 | MPa | 0.438 | sí | ELS04 | sí |
| VT4 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 235.219 | 400 | MPa | 0.588 | sí | ELS04 | sí |
| VT4 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 8.541 | 15.75 | MPa | 0.542 | sí | QP(psi2=0.8) | NO |
| VT4 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.145 | 15.75 | MPa | 0.009 | sí | QP(psi2=0.8) | NO |
| VT5 | sag | 1.725 | sigma_ct <= fctm (QP) | 3.508 | 3.21 | MPa | 1.093 | NO | QP(psi2=0.8) | NO |
| VT5 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0.155 | 0.1 | mm | 1.55 | NO | QP(psi2=0.8) | sí |
| VT5 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.17 | 3.21 | MPa | 0.053 | sí | QP(psi2=0.8) | NO |
| VT5 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT5 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 3.717 | 3.21 | MPa | 1.158 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT5 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.164 | 0.1 | mm | 1.642 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT5 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 3.183 | 3.21 | MPa | 0.992 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT5 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT5 | sag | 2.708 | sigma_c <= 0.6 fck (característica ELS01-08) | 11.865 | 21 | MPa | 0.565 | sí | ELS04 | sí |
| VT5 | sag | 2.708 | sigma_s <= 0.8 fyk (característica ELS01-08) | 195.718 | 400 | MPa | 0.489 | sí | ELS04 | sí |
| VT5 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 10.561 | 21 | MPa | 0.503 | sí | ELS04 | sí |
| VT5 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 270.076 | 400 | MPa | 0.675 | sí | ELS04 | sí |
| VT5 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 8.359 | 15.75 | MPa | 0.531 | sí | QP(psi2=0.8) | NO |
| VT5 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.136 | 15.75 | MPa | 0.009 | sí | QP(psi2=0.8) | NO |
| VT6 | sag | 1.725 | sigma_ct <= fctm (QP) | 3.893 | 3.21 | MPa | 1.213 | NO | QP(psi2=0.8) | NO |
| VT6 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0.172 | 0.1 | mm | 1.72 | NO | QP(psi2=0.8) | sí |
| VT6 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.191 | 3.21 | MPa | 0.059 | sí | QP(psi2=0.8) | NO |
| VT6 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT6 | sag | 2.217 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 4.156 | 3.21 | MPa | 1.295 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT6 | sag | 2.217 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.184 | 0.1 | mm | 1.836 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VT6 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.693 | 3.21 | MPa | 0.839 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT6 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT6 | sag | 2.217 | sigma_c <= 0.6 fck (característica ELS01-08) | 12.796 | 21 | MPa | 0.609 | sí | ELS04 | sí |
| VT6 | sag | 2.217 | sigma_s <= 0.8 fyk (característica ELS01-08) | 211.077 | 400 | MPa | 0.528 | sí | ELS04 | sí |
| VT6 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 8.882 | 21 | MPa | 0.423 | sí | ELS04 | sí |
| VT6 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 227.145 | 400 | MPa | 0.568 | sí | ELS04 | sí |
| VT6 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 9.278 | 15.75 | MPa | 0.589 | sí | QP(psi2=0.8) | NO |
| VT6 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.152 | 15.75 | MPa | 0.01 | sí | QP(psi2=0.8) | NO |
| VT7 | sag | 1.725 | sigma_ct <= fctm (QP) | 1.556 | 3.21 | MPa | 0.485 | sí | QP(psi2=0.8) | NO |
| VT7 | sag | 1.725 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT7 | hog | -0.2 | sigma_ct <= fctm (QP) | 0.042 | 3.21 | MPa | 0.013 | sí | QP(psi2=0.8) | NO |
| VT7 | hog | -0.2 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VT7 | sag | 2.708 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 1.947 | 3.21 | MPa | 0.607 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT7 | sag | 2.708 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT7 | hog | 0.2 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.158 | 3.21 | MPa | 0.672 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT7 | hog | 0.2 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VT7 | sag | 3.25 | sigma_c <= 0.6 fck (característica ELS01-08) | 8.313 | 21 | MPa | 0.396 | sí | ELS04 | sí |
| VT7 | sag | 3.25 | sigma_s <= 0.8 fyk (característica ELS01-08) | 183.718 | 400 | MPa | 0.459 | sí | ELS04 | sí |
| VT7 | hog | 0.2 | sigma_c <= 0.6 fck (característica ELS01-08) | 9.647 | 21 | MPa | 0.459 | sí | ELS04 | sí |
| VT7 | hog | 0.2 | sigma_s <= 0.8 fyk (característica ELS01-08) | 261.497 | 400 | MPa | 0.654 | sí | ELS04 | sí |
| VT7 | sag | 1.725 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 1.698 | 15.75 | MPa | 0.108 | sí | QP(psi2=0.8) | NO |
| VT7 | hog | -0.2 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 0.038 | 15.75 | MPa | 0.002 | sí | QP(psi2=0.8) | NO |
| VBM | sag | 3 | sigma_ct <= fctm (QP) | 2.778 | 3.21 | MPa | 0.865 | sí | QP(psi2=0.8) | NO |
| VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VBM | hog | 6.25 | sigma_ct <= fctm (QP) | 5.601 | 3.21 | MPa | 1.745 | NO | QP(psi2=0.8) | NO |
| VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | 0.306 | 0.1 | mm | 3.063 | NO | QP(psi2=0.8) | sí |
| VBM | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.778 | 3.21 | MPa | 0.866 | sí | QP(psi2=0.8,TB3=0.5) | NO |
| VBM | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB3=0.5) | NO |
| VBM | hog | 6.25 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 5.629 | 3.21 | MPa | 1.754 | NO | QP(psi2=0.8,TB2=0.5) | NO |
| VBM | hog | 6.25 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.308 | 0.1 | mm | 3.084 | NO | QP(psi2=0.8,TB2=0.5) | NO |
| VBM | sag | 3 | sigma_c <= 0.6 fck (característica ELS01-08) | 7.996 | 21 | MPa | 0.381 | sí | ELS08 | sí |
| VBM | sag | 3 | sigma_s <= 0.8 fyk (característica ELS01-08) | 147.624 | 400 | MPa | 0.369 | sí | ELS08 | sí |
| VBM | hog | 6.25 | sigma_c <= 0.6 fck (característica ELS01-08) | 16.201 | 21 | MPa | 0.771 | sí | ELS06 | sí |
| VBM | hog | 6.25 | sigma_s <= 0.8 fyk (característica ELS01-08) | 299.099 | 400 | MPa | 0.748 | sí | ELS06 | sí |
| VBM | sag | 3 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 2.778 | 15.75 | MPa | 0.176 | sí | QP(psi2=0.8) | NO |
| VBM | hog | 6.25 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 13.897 | 15.75 | MPa | 0.882 | sí | QP(psi2=0.8) | NO |
| VBT | sag | 3 | sigma_ct <= fctm (QP) | 2.778 | 3.21 | MPa | 0.865 | sí | QP(psi2=0.8) | NO |
| VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8) | sí |
| VBT | hog | 6.25 | sigma_ct <= fctm (QP) | 5.628 | 3.21 | MPa | 1.753 | NO | QP(psi2=0.8) | NO |
| VBT | hog | 6.25 | wk <= 0.1 mm (XS3, QP) | 0.308 | 0.1 | mm | 3.083 | NO | QP(psi2=0.8) | sí |
| VBT | sag | 3 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 2.786 | 3.21 | MPa | 0.868 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VBT | sag | 3 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0 | 0.1 | mm | 0 | sí | QP(psi2=0.8,TB1=0.5) | NO |
| VBT | hog | 32.75 | sigma_ct <= fctm (QP) [sensibilidad TB psi2 = 0.5] | 5.715 | 3.21 | MPa | 1.78 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VBT | hog | 32.75 | wk <= 0.1 mm (XS3, QP) [sensibilidad TB psi2 = 0.5] | 0.315 | 0.1 | mm | 3.15 | NO | QP(psi2=0.8,TB1=0.5) | NO |
| VBT | sag | 3 | sigma_c <= 0.6 fck (característica ELS01-08) | 8.032 | 21 | MPa | 0.383 | sí | ELS04 | sí |
| VBT | sag | 3 | sigma_s <= 0.8 fyk (característica ELS01-08) | 148.29 | 400 | MPa | 0.371 | sí | ELS04 | sí |
| VBT | hog | 32.75 | sigma_c <= 0.6 fck (característica ELS01-08) | 16.571 | 21 | MPa | 0.789 | sí | ELS04 | sí |
| VBT | hog | 32.75 | sigma_s <= 0.8 fyk (característica ELS01-08) | 305.93 | 400 | MPa | 0.765 | sí | ELS04 | sí |
| VBT | sag | 3 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 2.778 | 15.75 | MPa | 0.176 | sí | QP(psi2=0.8) | NO |
| VBT | hog | 6.25 | sigma_c <= 0.45 fck (QP, fluencia lineal) | 13.962 | 15.75 | MPa | 0.886 | sí | QP(psi2=0.8) | NO |

## Anexo: Flechas (caso final CE-ROM)

| member | section | pos_m | check | demand | capacity | unit | eta | ok | combo | in_verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 0.479 | 12.2 | mm | 0.039 | sí | QP(psi2=0.8) | sí |
| VT1 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 0.42 | 6.1 | mm | 0.069 | sí | QP(psi2=0.8) | sí |
| VT1 | vano |  | L/d <= (L/d)lim | 6.354 | 30.492 | - | 0.208 | sí |  | NO |
| VT2 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 1.214 | 12.2 | mm | 0.1 | sí | QP(psi2=0.8) | sí |
| VT2 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 1.088 | 6.1 | mm | 0.178 | sí | QP(psi2=0.8) | sí |
| VT2 | vano |  | L/d <= (L/d)lim | 6.354 | 41.044 | - | 0.155 | sí |  | NO |
| VT3 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 1.095 | 12.2 | mm | 0.09 | sí | QP(psi2=0.8) | sí |
| VT3 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 0.98 | 6.1 | mm | 0.161 | sí | QP(psi2=0.8) | sí |
| VT3 | vano |  | L/d <= (L/d)lim | 6.354 | 41.044 | - | 0.155 | sí |  | NO |
| VT4 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 1.118 | 12.2 | mm | 0.092 | sí | QP(psi2=0.8) | sí |
| VT4 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 1.001 | 6.1 | mm | 0.164 | sí | QP(psi2=0.8) | sí |
| VT4 | vano |  | L/d <= (L/d)lim | 6.354 | 41.044 | - | 0.155 | sí |  | NO |
| VT5 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 1.095 | 12.2 | mm | 0.09 | sí | QP(psi2=0.8) | sí |
| VT5 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 0.98 | 6.1 | mm | 0.161 | sí | QP(psi2=0.8) | sí |
| VT5 | vano |  | L/d <= (L/d)lim | 6.354 | 41.044 | - | 0.155 | sí |  | NO |
| VT6 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 1.214 | 12.2 | mm | 0.1 | sí | QP(psi2=0.8) | sí |
| VT6 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 1.088 | 6.1 | mm | 0.178 | sí | QP(psi2=0.8) | sí |
| VT6 | vano |  | L/d <= (L/d)lim | 6.354 | 41.044 | - | 0.155 | sí |  | NO |
| VT7 | vano | 1.725 | f total (QP, fluencia) <= L/250 | 0.479 | 12.2 | mm | 0.039 | sí | QP(psi2=0.8) | sí |
| VT7 | vano | 1.725 | f activa (f total - f inst. PP) <= L/500 | 0.42 | 6.1 | mm | 0.069 | sí | QP(psi2=0.8) | sí |
| VT7 | vano |  | L/d <= (L/d)lim | 6.354 | 30.492 | - | 0.208 | sí |  | NO |
| VBM | tramo 1 | 3 | f total (QP, fluencia) <= L/250 | 4.268 | 23.4 | mm | 0.182 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 1 | 3 | f activa (f total - f inst. PP) <= L/500 | 3.841 | 11.7 | mm | 0.328 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 1 |  | L/d <= (L/d)lim | 25 | 24.92 | - | 1.003 | NO |  | NO |
| VBM | tramo 2 | 10 | f total (QP, fluencia) <= L/250 | 1.761 | 24 | mm | 0.073 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 2 | 10 | f activa (f total - f inst. PP) <= L/500 | 1.563 | 12 | mm | 0.13 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 2 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBM | tramo 3 | 16 | f total (QP, fluencia) <= L/250 | 2.327 | 24 | mm | 0.097 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 3 | 16 | f activa (f total - f inst. PP) <= L/500 | 2.079 | 12 | mm | 0.173 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 3 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBM | tramo 4 | 23 | f total (QP, fluencia) <= L/250 | 2.327 | 24 | mm | 0.097 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 4 | 23 | f activa (f total - f inst. PP) <= L/500 | 2.079 | 12 | mm | 0.173 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 4 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBM | tramo 5 | 29 | f total (QP, fluencia) <= L/250 | 1.761 | 24 | mm | 0.073 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 5 | 29 | f activa (f total - f inst. PP) <= L/500 | 1.563 | 12 | mm | 0.13 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 5 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBM | tramo 6 | 36 | f total (QP, fluencia) <= L/250 | 4.268 | 23.4 | mm | 0.182 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 6 | 36 | f activa (f total - f inst. PP) <= L/500 | 3.841 | 11.7 | mm | 0.328 | sí | QP(psi2=0.8) | sí |
| VBM | tramo 6 |  | L/d <= (L/d)lim | 25 | 24.92 | - | 1.003 | NO |  | NO |
| VBT | tramo 1 | 3 | f total (QP, fluencia) <= L/250 | 4.264 | 23.4 | mm | 0.182 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 1 | 3 | f activa (f total - f inst. PP) <= L/500 | 3.837 | 11.7 | mm | 0.328 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 1 |  | L/d <= (L/d)lim | 25 | 24.92 | - | 1.003 | NO |  | NO |
| VBT | tramo 2 | 10 | f total (QP, fluencia) <= L/250 | 1.784 | 24 | mm | 0.074 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 2 | 10 | f activa (f total - f inst. PP) <= L/500 | 1.583 | 12 | mm | 0.132 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 2 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBT | tramo 3 | 16 | f total (QP, fluencia) <= L/250 | 2.338 | 24 | mm | 0.097 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 3 | 16 | f activa (f total - f inst. PP) <= L/500 | 2.088 | 12 | mm | 0.174 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 3 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBT | tramo 4 | 23 | f total (QP, fluencia) <= L/250 | 2.338 | 24 | mm | 0.097 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 4 | 23 | f activa (f total - f inst. PP) <= L/500 | 2.088 | 12 | mm | 0.174 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 4 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBT | tramo 5 | 29 | f total (QP, fluencia) <= L/250 | 1.784 | 24 | mm | 0.074 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 5 | 29 | f activa (f total - f inst. PP) <= L/500 | 1.583 | 12 | mm | 0.132 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 5 |  | L/d <= (L/d)lim | 25.641 | 24.92 | - | 1.029 | NO |  | NO |
| VBT | tramo 6 | 36 | f total (QP, fluencia) <= L/250 | 4.264 | 23.4 | mm | 0.182 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 6 | 36 | f activa (f total - f inst. PP) <= L/500 | 3.837 | 11.7 | mm | 0.328 | sí | QP(psi2=0.8) | sí |
| VBT | tramo 6 |  | L/d <= (L/d)lim | 25 | 24.92 | - | 1.003 | NO |  | NO |

## Supuestos

- Forces: SAP2000 v27.1 (sap2000/resultados_sap), CYPE convention; ULS ELU01-22 (CYPE) / ELR01-22 (ROM).
- Design sections: pile faces y = +-0.20 / 3.25 / 3.65 (A19.5.3.2.2(3)); pile-axis moments reported as info (rigid node: CYPE's 'P3' -273.71 lies between the face and the axis, C20).
- Shift rule / (6.18): at the pile faces MEd,max = the face moment (A19.5.3.2.2(3), monolithic support), so M/z + dFtd is capped there and adds nothing; the shift al = z·cot/2 (0.43 m at cot 2) only governs curtailment (not modelled: full-length bars). If the rigid-node pile-axis moment were taken as MEd,max instead, the sea-face hogging chord would be at the axis rows' eta (1.03-1.18 for VT1-VT6, CE-ROM): see the 'eje pilote mar (info)' rows.
- Bending about the horizontal axis with a horizontal neutral axis (laterally restrained beams; L sections: My of the resultant carried by the slab).
- Bars run the full length (hooked ends): no anchorage reduction of the area (CYPE reduces it in the 0.10 m cantilevers, 'Área Real' 11.28/13.42).
- Shear: z = 0.9d, fywd = 400 MPa with nu1 = 0.6; V at the face for VRd,max and at d for VRd,s (cantilevers shorter than d: V at the face).
- Torsion (A19.6.3) with the SAP torque on every member; in the verdict for the end frames (axes 1, 7, as required); for the inner frames and edge beams the SAP torque is compatibility torsion (gravity rotations imposed by the neighbouring members, A19.6.3.1(2)) and is reported as information. Links per leg of the hoop: Asw,V/(n·s) + T/(2·Ak·fyd·cot); longitudinal (6.28) added to the tension chord.
- Suspension (A19.6.2.1(9)): the hollow-core plates bear on the ledges, i.e. the load is applied near the bottom of the section; the web links carry the ULS plate reaction q·Lp/2 per ledge (inner beams both ledges, end beams one) at fyd in addition to V/(z·fywd·cot), wherever plates bear (Y -0.306 to 3.603). In the verdict of the CE cases; information in case CYPE (CYPE does not check it).
- Sensitivity (not in the verdict): equilibrium torque of the hollow-core plates bearing on the single ledge of the end beams (e = 0.42 m from the pile axis; 56 kN·m at the pile faces for 1.35G + 1.5Qa), modelled neither in SAP nor in CYPE (P437).
- Case CYPE: cot(theta) = 1 and nu(torsion) = 0.6 (CYPE); CE cases: largest cot(theta) in [0.5, 2] allowed by (6.29) at the face and nu = 0.6(1 - fck/250) = 0.516 (A19.6.3.2(4)).
- SLS: alpha_e = Es/Ecm = 6.52 for stresses and wk; kt = 0.4, k1 0.8, k2 0.5, k3 3.4, k4 0.425, c = 50 + stirrup Ø; characteristic combinations = SAP ELS01-08 (all psi = 1, upper bound).
- Deflection: curvature integration between the pile faces, phi = 2.0 (assumed), beta 0.5; 'activa' = f(QP, inf) - f(PP, inst).
- Reinforcement search (final case, one layout per group inner / end / edge, only where the provided component fails): single row per face, web bars inside the web hoop + ledge bars (equal or one size smaller), Ø16-Ø25 (edge beams Ø12-Ø25), CE clear spacing max(Ø, dg + 5, 20), bars <= 350 mm apart; links Ø8-12, 2-4 legs, s 50-300; objective As·(1 + 0.002·n_bars) (weight, fewer bars on ties).
