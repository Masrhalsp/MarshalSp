# Valores propios esperados en las estaciones de diseño de SAP (base CYPE; no son resultados de SAP)

Fuente: diseno/output/pilotes.json, diseno/output/vigas.json, sap2000/resultados_sap/SAP27_Element_Forces_Frames.xlsx (sap_est_*)  ·  base de combinaciones: **CYPE**  ·  filas: 14 pilotes, 136 vigas

## Resumen

```
{
 "base": "CYPE"
}
```

## Notas

- Valores propios (Código Estructural) en las estaciones que SAP reporta; no son resultados de SAP.  Vigas: As_uls = armadura de tracción ELU (SAP no añade As,min del Código en la misma forma); Asw/s con V a d de la cara; 'Asw_s_req_cot1' = el mismo valor con cot θ = 1 (SAP con TanTheta = 1; SAP usa además V en la cara y fywd = 434.8 MPa).
- Pilotes: SAP (sin análisis P-Delta, como este modelo) aplica el método de la curvatura nominal con M0e = 0.6·M02 + 0.4·M01 >= 0.4·M02 (manual CFD-EC-2-2004 §3.4.2.2).  Los pilotes flectan en doble curvatura (traslacionales), así que M0e = 0.4·M02 y gobierna la comprobación de 1er orden en los extremos + Mi = N·max(ei, emin): el momento de 2º orden del pilote traslacional en cabeza/pie NO se comprueba (SAP lo espera de un análisis P-Delta).  Valor esperado en SAP = 'sap_est_M0e' (≈ nm1 propio + 1-6 %), no nm2.  Si los detalles de SAP muestran MEd = M02 + Mi + M2, el valor esperado es 'sap_est_estacion' (≈ nm2 con e2 de c = 8 y el Kφ del overwrite).  El pilote se verifica con nm2 (diseno/output/pilotes.md), no con SAP.
- SAP e2 = Kr·Kφ·εyd/(0.45 d)·l0²/8 con d = 327.5 mm: Kφ 1.1129 da e2 = 92.1 mm = CYPE; el e2 estricto del Código (d = h/2 + is = 307 mm) es 98.3 mm (Kφ 'ce_is' = 1.1874).

Procedimiento SAP usado en `sap_est_*` (nuestras fuerzas): ei_mm = 20.0, e2_mm = 92.12, d_mm = 327.5, Kphi = 1.1129, c = 8

## Pilotes: ratio P-M-M (SAP) / η N-M propia / Aprov. CYPE

| pile | nm1[CYPE,codigo] | nm2[CYPE,codigo] | nm1[CYPE,cype] | nm2[CYPE,cype] | sap_est_M0e | combo_M0e | gov_M0e | sap_est_estacion | combo_estacion | cype_aprov_fuste | cype_aprov_arranque |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.704 | 0.882 | 0.699 | 0.872 | 0.728 | ELU08 | 1er orden + Mi, cabeza | 0.881 | ELU08 | 0.857 | 0.847 |
| P2 | 0.815 | 0.777 | 0.811 | - | 0.823 | ELU05 | 1er orden + Mi, pie | 0.823 | ELU05 | 0.843 | 0.819 |
| P3 | 0.679 | 0.933 | 0.672 | 0.920 | 0.714 | ELU08 | 1er orden + Mi, cabeza | 0.931 | ELU08 | 0.925 | 0.907 |
| P4 | 0.764 | 0.674 | 0.760 | 0.447 | 0.770 | ELU05 | 1er orden + Mi, pie | 0.770 | ELU05 | 0.771 | 0.764 |
| P5 | 0.652 | 0.879 | 0.644 | 0.865 | 0.670 | ELU05 | 1er orden + Mi, pie | 0.877 | ELU08 | 0.880 | 0.869 |
| P6 | 0.763 | 0.680 | 0.760 | 0.255 | 0.770 | ELU05 | 1er orden + Mi, pie | 0.770 | ELU05 | 0.772 | 0.765 |
| P7 | 0.655 | 0.878 | 0.648 | 0.866 | 0.673 | ELU08 | 1er orden + Mi, cabeza | 0.877 | ELU08 | 0.882 | 0.869 |
| P8 | 0.739 | 0.655 | 0.736 | 0.420 | 0.746 | ELU05 | 1er orden + Mi, pie | 0.746 | ELU05 | 0.746 | 0.740 |
| P13 | 0.627 | 0.855 | 0.620 | 0.842 | 0.645 | ELU05 | 1er orden + Mi, pie | 0.854 | ELU08 | 0.855 | 0.844 |
| P14 | 0.735 | 0.651 | 0.732 | 0.255 | 0.742 | ELU05 | 1er orden + Mi, pie | 0.742 | ELU05 | 0.743 | 0.737 |
| P15 | 0.633 | 0.881 | 0.626 | 0.868 | 0.667 | ELU08 | 1er orden + Mi, cabeza | 0.879 | ELU08 | 0.874 | 0.853 |
| P16 | 0.644 | 0.804 | 0.639 | 0.795 | 0.665 | ELU08 | 1er orden + Mi, cabeza | 0.803 | ELU08 | 0.775 | 0.765 |
| P17 | 0.710 | 0.621 | 0.707 | 0.426 | 0.715 | ELU05 | 1er orden + Mi, pie | 0.715 | ELU05 | 0.715 | 0.709 |
| P18 | 0.730 | 0.693 | 0.727 | - | 0.738 | ELU05 | 1er orden + Mi, pie | 0.738 | ELU05 | 0.742 | 0.733 |

## Vigas: As a flexión (cm²)

| member | section | pos | face | combo | MEd_kNm | As_uls_cm2 | As_min_cm2 | As_prov_cm2 |
|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.200 | bottom | ELU17 | 12.38 | 0.594 | 8.070 | 18.85 |
| VT1 | cara pilote mar - voladizo | -0.200 | top | ELU08 | -58.28 | 2.809 | 7.420 | 15.71 |
| VT1 | cara pilote mar - vano | 0.200 | bottom | ELU17 | 23.45 | 1.127 | 8.070 | 18.85 |
| VT1 | cara pilote mar - vano | 0.200 | top | ELU08 | -316.20 | 15.67 | 7.420 | 15.71 |
| VT1 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 274.25 | 13.60 | 8.070 | 18.85 |
| VT1 | cara pilote tierra - vuelo | 3.650 | bottom | ELU16 | 6.894 | 0.331 | 8.070 | 18.85 |
| VT1 | vano: máx. positivo | 3.250 | bottom | ELU08 | 274.01 | 13.59 | 8.070 | 18.85 |
| VT2 | cara pilote mar - voladizo | -0.200 | top | ELU16 | -9.893 | 0.475 | 4.990 | 15.71 |
| VT2 | cara pilote mar - vano | 0.200 | top | ELU08 | -263.95 | 13.07 | 4.990 | 15.71 |
| VT2 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 259.70 | 13.13 | 6.250 | 21.99 |
| VT2 | cara pilote tierra - vano | 3.250 | top | ELU17 | -0.517 | 0.025 | 4.990 | 15.71 |
| VT2 | cara pilote tierra - vuelo | 3.650 | bottom | ELU22 | 5.131 | 0.246 | 6.250 | 21.99 |
| VT2 | vano: máx. positivo | 2.708 | bottom | ELU08 | 283.00 | 14.39 | 6.250 | 21.99 |
| VT3 | cara pilote mar - voladizo | -0.200 | bottom | ELU17 | 10.59 | 0.509 | 6.250 | 21.99 |
| VT3 | cara pilote mar - voladizo | -0.200 | top | ELU08 | -62.00 | 2.993 | 4.990 | 15.71 |
| VT3 | cara pilote mar - vano | 0.200 | bottom | ELU17 | 20.35 | 0.979 | 6.250 | 21.99 |
| VT3 | cara pilote mar - vano | 0.200 | top | ELU08 | -301.72 | 15.02 | 4.990 | 15.71 |
| VT3 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 256.61 | 12.97 | 6.250 | 21.99 |
| VT3 | cara pilote tierra - vano | 3.250 | top | ELU17 | -0.524 | 0.025 | 4.990 | 15.71 |
| VT3 | cara pilote tierra - vuelo | 3.650 | bottom | ELU16 | 4.189 | 0.201 | 6.250 | 21.99 |
| VT3 | vano: máx. positivo | 2.708 | bottom | ELU08 | 263.05 | 13.31 | 6.250 | 21.99 |
| VT4 | cara pilote mar - voladizo | -0.200 | top | ELU16 | -9.432 | 0.453 | 4.990 | 15.71 |
| VT4 | cara pilote mar - vano | 0.200 | top | ELU08 | -255.05 | 12.62 | 4.990 | 15.71 |
| VT4 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 250.70 | 12.65 | 6.250 | 21.99 |
| VT4 | cara pilote tierra - vano | 3.250 | top | ELU17 | -0.554 | 0.026 | 4.990 | 15.71 |
| VT4 | cara pilote tierra - vuelo | 3.650 | bottom | ELU22 | 4.204 | 0.202 | 6.250 | 21.99 |
| VT4 | vano: máx. positivo | 2.708 | bottom | ELU08 | 268.15 | 13.59 | 6.250 | 21.99 |
| VT5 | cara pilote mar - voladizo | -0.200 | bottom | ELU17 | 10.59 | 0.509 | 6.250 | 21.99 |
| VT5 | cara pilote mar - voladizo | -0.200 | top | ELU08 | -62.02 | 2.994 | 4.990 | 15.71 |
| VT5 | cara pilote mar - vano | 0.200 | bottom | ELU17 | 20.35 | 0.979 | 6.250 | 21.99 |
| VT5 | cara pilote mar - vano | 0.200 | top | ELU08 | -292.91 | 14.56 | 4.990 | 15.71 |
| VT5 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 247.83 | 12.50 | 6.250 | 21.99 |
| VT5 | cara pilote tierra - vano | 3.250 | top | ELU17 | -0.524 | 0.025 | 4.990 | 15.71 |
| VT5 | cara pilote tierra - vuelo | 3.650 | bottom | ELU16 | 4.189 | 0.201 | 6.250 | 21.99 |
| VT5 | vano: máx. positivo | 2.708 | bottom | ELU08 | 257.41 | 13.01 | 6.250 | 21.99 |
| VT6 | cara pilote mar - voladizo | -0.200 | top | ELU16 | -9.893 | 0.475 | 4.990 | 15.71 |
| VT6 | cara pilote mar - vano | 0.200 | top | ELU08 | -246.33 | 12.17 | 4.990 | 15.71 |
| VT6 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 242.15 | 12.20 | 6.250 | 21.99 |
| VT6 | cara pilote tierra - vano | 3.250 | top | ELU17 | -0.517 | 0.025 | 4.990 | 15.71 |
| VT6 | cara pilote tierra - vuelo | 3.650 | bottom | ELU22 | 5.131 | 0.246 | 6.250 | 21.99 |
| VT6 | vano: máx. positivo | 2.217 | bottom | ELU10 | 276.78 | 14.05 | 6.250 | 21.99 |
| VT7 | cara pilote mar - voladizo | -0.200 | bottom | ELU17 | 12.38 | 0.594 | 8.070 | 18.85 |
| VT7 | cara pilote mar - voladizo | -0.200 | top | ELU08 | -58.33 | 2.812 | 7.420 | 15.71 |
| VT7 | cara pilote mar - vano | 0.200 | bottom | ELU17 | 23.45 | 1.127 | 8.070 | 18.85 |
| VT7 | cara pilote mar - vano | 0.200 | top | ELU08 | -289.29 | 14.29 | 7.420 | 15.71 |
| VT7 | cara pilote tierra - vano | 3.250 | bottom | ELU08 | 247.31 | 12.22 | 8.070 | 18.85 |
| VT7 | cara pilote tierra - vuelo | 3.650 | bottom | ELU16 | 6.894 | 0.331 | 8.070 | 18.85 |
| VT7 | vano: máx. positivo | 3.250 | bottom | ELU08 | 247.12 | 12.21 | 8.070 | 18.85 |
| VBM | tramo 1 cara izq. (X=0.40) | 0.400 | top | ELU22 | -20.81 | 2.119 | 1.500 | 4.021 |
| VBM | tramo 1 cara der. (X=6.25) | 6.250 | top | ELU16 | -37.39 | 3.928 | 1.500 | 4.021 |
| VBM | tramo 2 cara izq. (X=6.75) | 6.750 | top | ELU16 | -36.38 | 3.813 | 1.500 | 4.021 |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | top | ELU22 | -28.82 | 2.978 | 1.500 | 4.021 |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | top | ELU22 | -29.65 | 3.068 | 1.500 | 4.021 |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | top | ELU16 | -31.39 | 3.259 | 1.500 | 4.021 |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | top | ELU16 | -31.39 | 3.259 | 1.500 | 4.021 |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | top | ELU22 | -29.65 | 3.068 | 1.500 | 4.021 |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | top | ELU22 | -28.82 | 2.978 | 1.500 | 4.021 |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | top | ELU16 | -36.38 | 3.813 | 1.500 | 4.021 |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | top | ELU16 | -37.39 | 3.928 | 1.500 | 4.021 |
| VBM | tramo 6 cara der. (X=38.60) | 38.60 | top | ELU22 | -20.81 | 2.119 | 1.500 | 4.021 |
| VBM | tramo 1: máx. positivo | 3.000 | bottom | ELU22 | 18.54 | 1.880 | 1.500 | 4.021 |
| VBM | tramo 2: máx. positivo | 10.00 | bottom | ELU16 | 10.77 | 1.078 | 1.500 | 4.021 |
| VBM | tramo 3: máx. positivo | 16.00 | bottom | ELU16 | 12.14 | 1.218 | 1.500 | 4.021 |
| VBM | tramo 4: máx. positivo | 23.00 | bottom | ELU16 | 12.14 | 1.218 | 1.500 | 4.021 |
| VBM | tramo 5: máx. positivo | 29.00 | bottom | ELU16 | 10.77 | 1.078 | 1.500 | 4.021 |
| VBM | tramo 6: máx. positivo | 36.00 | bottom | ELU22 | 18.54 | 1.880 | 1.500 | 4.021 |
| VBT | tramo 1 cara izq. (X=0.40) | 0.400 | top | ELU10 | -21.43 | 2.185 | 1.500 | 4.021 |
| VBT | tramo 1 cara der. (X=6.25) | 6.250 | top | ELU10 | -37.90 | 3.985 | 1.500 | 4.021 |
| VBT | tramo 2 cara izq. (X=6.75) | 6.750 | top | ELU10 | -36.91 | 3.874 | 1.500 | 4.021 |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | top | ELU10 | -29.26 | 3.026 | 1.500 | 4.021 |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | top | ELU10 | -30.16 | 3.124 | 1.500 | 4.021 |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | top | ELU10 | -31.91 | 3.317 | 1.500 | 4.021 |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | top | ELU10 | -32.04 | 3.331 | 1.500 | 4.021 |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | top | ELU10 | -30.02 | 3.108 | 1.500 | 4.021 |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | top | ELU10 | -29.37 | 3.038 | 1.500 | 4.021 |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | top | ELU10 | -36.74 | 3.855 | 1.500 | 4.021 |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | top | ELU10 | -37.99 | 3.995 | 1.500 | 4.021 |
| VBT | tramo 6 cara der. (X=38.60) | 38.60 | top | ELU16 | -21.27 | 2.168 | 1.500 | 4.021 |
| VBT | tramo 1: máx. positivo | 3.000 | bottom | ELU10 | 18.59 | 1.886 | 1.500 | 4.021 |
| VBT | tramo 2: máx. positivo | 10.00 | bottom | ELU10 | 10.96 | 1.097 | 1.500 | 4.021 |
| VBT | tramo 3: máx. positivo | 16.00 | bottom | ELU10 | 12.31 | 1.235 | 1.500 | 4.021 |
| VBT | tramo 4: máx. positivo | 23.00 | bottom | ELU10 | 12.32 | 1.236 | 1.500 | 4.021 |
| VBT | tramo 5: máx. positivo | 29.00 | bottom | ELU10 | 10.95 | 1.096 | 1.500 | 4.021 |
| VBT | tramo 6: máx. positivo | 36.00 | bottom | ELU10 | 18.59 | 1.885 | 1.500 | 4.021 |

## Vigas: Asw/s (cm²/m)

| member | section | face_pos | pos_d | combo | cot_theta | Asw_s_req_cm2_m | Asw_s_req_cot1_cm2_m | V_face_kN | combo_face | sap_est_Asw_s_face_cm2_m | Asw_s_prov_cm2_m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU14 | 1.000 | 7.701 | 7.701 | 133.08 | ELU14 | 7.085 | 23.56 |
| VT1 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 16.99 | 16.99 | 325.40 | ELU08 | 17.32 | 23.56 |
| VT1 | cara pilote tierra - vano | 3.250 | 2.770 | ELU05 | 1.000 | 9.379 | 9.379 | 158.61 | ELU22 | 8.445 | 23.56 |
| VT1 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 3.669 | 3.669 | 63.40 | ELU10 | 3.376 | 23.56 |
| VT2 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU16 | 1.000 | 6.113 | 6.113 | 105.63 | ELU16 | 5.624 | 23.56 |
| VT2 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 22.23 | 22.23 | 469.57 | ELU10 | 25.00 | 23.56 |
| VT2 | cara pilote tierra - vano | 3.250 | 2.770 | ELU22 | 1.000 | 15.33 | 15.33 | 354.95 | ELU22 | 18.90 | 23.56 |
| VT2 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 5.849 | 5.849 | 101.08 | ELU10 | 5.381 | 23.56 |
| VT3 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU14 | 1.000 | 8.931 | 8.931 | 154.33 | ELU14 | 8.217 | 23.56 |
| VT3 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 21.74 | 21.74 | 446.78 | ELU08 | 23.79 | 23.56 |
| VT3 | cara pilote tierra - vano | 3.250 | 2.770 | ELU22 | 1.000 | 14.04 | 14.04 | 324.35 | ELU22 | 17.27 | 23.56 |
| VT3 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 5.061 | 5.061 | 87.45 | ELU10 | 4.656 | 23.56 |
| VT4 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU16 | 1.000 | 5.660 | 5.660 | 97.81 | ELU16 | 5.208 | 23.56 |
| VT4 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 20.91 | 20.91 | 437.77 | ELU10 | 23.31 | 23.56 |
| VT4 | cara pilote tierra - vano | 3.250 | 2.770 | ELU22 | 1.000 | 14.13 | 14.13 | 328.03 | ELU22 | 17.46 | 23.56 |
| VT4 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 5.310 | 5.310 | 91.76 | ELU10 | 4.885 | 23.56 |
| VT5 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU14 | 1.000 | 8.931 | 8.931 | 154.33 | ELU14 | 8.217 | 23.56 |
| VT5 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 21.40 | 21.40 | 440.79 | ELU08 | 23.47 | 23.56 |
| VT5 | cara pilote tierra - vano | 3.250 | 2.770 | ELU22 | 1.000 | 14.04 | 14.04 | 324.35 | ELU22 | 17.27 | 23.56 |
| VT5 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 5.057 | 5.057 | 87.39 | ELU10 | 4.653 | 23.56 |
| VT6 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU16 | 1.000 | 6.113 | 6.113 | 105.63 | ELU16 | 5.624 | 23.56 |
| VT6 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 21.56 | 21.56 | 462.36 | ELU10 | 24.62 | 23.56 |
| VT6 | cara pilote tierra - vano | 3.250 | 2.770 | ELU22 | 1.000 | 15.33 | 15.33 | 354.95 | ELU22 | 18.90 | 23.56 |
| VT6 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 5.841 | 5.841 | 100.93 | ELU10 | 5.374 | 23.56 |
| VT7 | cara pilote mar - voladizo | -0.200 | -0.200 | ELU14 | 1.000 | 7.701 | 7.701 | 133.08 | ELU14 | 7.085 | 23.56 |
| VT7 | cara pilote mar - vano | 0.200 | 0.680 | ELU08 | 1.000 | 15.97 | 15.97 | 307.62 | ELU08 | 16.38 | 23.56 |
| VT7 | cara pilote tierra - vano | 3.250 | 2.770 | ELU05 | 1.000 | 8.355 | 8.355 | 158.61 | ELU22 | 8.445 | 23.56 |
| VT7 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELU10 | 1.000 | 3.659 | 3.659 | 63.22 | ELU10 | 3.366 | 23.56 |
| VBM | tramo 1 cara izq. (X=0.40) | 0.400 | 0.634 | ELU22 | 1.000 | 3.230 | 3.230 | 56.43 | ELU22 | 6.162 | 6.702 |
| VBM | tramo 1 cara der. (X=6.25) | 6.250 | 6.016 | ELU16 | 1.000 | 6.979 | 6.979 | 60.05 | ELU16 | 6.559 | 6.702 |
| VBM | tramo 2 cara izq. (X=6.75) | 6.750 | 6.984 | ELU16 | 1.000 | 6.586 | 6.586 | 56.74 | ELU16 | 6.197 | 6.702 |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | 12.52 | ELU22 | 1.000 | 5.533 | 5.533 | 47.88 | ELU22 | 5.229 | 6.702 |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | 13.48 | ELU22 | 1.000 | 5.721 | 5.721 | 49.46 | ELU22 | 5.401 | 6.702 |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | 19.02 | ELU16 | 1.000 | 5.941 | 5.941 | 51.31 | ELU16 | 5.604 | 6.702 |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | 19.98 | ELU16 | 1.000 | 5.941 | 5.941 | 51.31 | ELU16 | 5.604 | 6.702 |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | 25.52 | ELU22 | 1.000 | 5.721 | 5.721 | 49.46 | ELU22 | 5.401 | 6.702 |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | 26.48 | ELU22 | 1.000 | 5.533 | 5.533 | 47.88 | ELU22 | 5.229 | 6.702 |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | 32.02 | ELU16 | 1.000 | 6.586 | 6.586 | 56.74 | ELU16 | 6.197 | 6.702 |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | 32.98 | ELU16 | 1.000 | 6.979 | 6.979 | 60.05 | ELU16 | 6.559 | 6.702 |
| VBM | tramo 6 cara der. (X=38.60) | 38.60 | 38.37 | ELU22 | 1.000 | 3.230 | 3.230 | 56.43 | ELU22 | 6.162 | 6.702 |
| VBT | tramo 1 cara izq. (X=0.40) | 0.400 | 0.634 | ELU10 | 1.000 | 3.063 | 3.063 | 56.92 | ELU10 | 6.217 | 6.702 |
| VBT | tramo 1 cara der. (X=6.25) | 6.250 | 6.016 | ELU10 | 1.000 | 7.235 | 7.235 | 62.21 | ELU10 | 6.794 | 6.702 |
| VBT | tramo 2 cara izq. (X=6.75) | 6.750 | 6.984 | ELU10 | 1.000 | 6.848 | 6.848 | 58.95 | ELU10 | 6.438 | 6.702 |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | 12.52 | ELU10 | 1.000 | 5.713 | 5.713 | 49.38 | ELU10 | 5.393 | 6.702 |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | 13.48 | ELU10 | 1.000 | 5.907 | 5.907 | 51.03 | ELU10 | 5.573 | 6.702 |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | 19.02 | ELU10 | 1.000 | 6.178 | 6.178 | 53.30 | ELU10 | 5.821 | 6.702 |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | 19.98 | ELU10 | 1.000 | 6.195 | 6.195 | 53.45 | ELU10 | 5.837 | 6.702 |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | 25.52 | ELU10 | 1.000 | 5.886 | 5.886 | 50.85 | ELU10 | 5.553 | 6.702 |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | 26.48 | ELU10 | 1.000 | 5.726 | 5.726 | 49.50 | ELU10 | 5.406 | 6.702 |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | 32.02 | ELU10 | 1.000 | 6.822 | 6.822 | 58.73 | ELU10 | 6.414 | 6.702 |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | 32.98 | ELU10 | 1.000 | 7.244 | 7.244 | 62.28 | ELU10 | 6.802 | 6.702 |
| VBT | tramo 6 cara der. (X=38.60) | 38.60 | 38.37 | ELU16 | 1.000 | 3.047 | 3.047 | 56.73 | ELU10 | 6.196 | 6.702 |
