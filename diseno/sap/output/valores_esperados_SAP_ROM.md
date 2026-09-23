# Valores propios esperados en las estaciones de diseño de SAP (base ROM; no son resultados de SAP)

Fuente: diseno/output/pilotes.json, diseno/output/vigas.json, sap2000/resultados_sap/SAP27_Element_Forces_Frames.xlsx (sap_est_*)  ·  base de combinaciones: **ROM**  ·  filas: 14 pilotes, 136 vigas

## Resumen

```
{
 "base": "ROM"
}
```

## Notas

- Valores propios (Código Estructural) en las estaciones que SAP reporta; no son resultados de SAP.  Vigas: As_uls = armadura de tracción ELU (SAP no añade As,min del Código en la misma forma); Asw/s con V a d de la cara; 'Asw_s_req_cot1' = el mismo valor con cot θ = 1 (SAP con TanTheta = 1; SAP usa además V en la cara y fywd = 434.8 MPa).
- Pilotes: SAP (sin análisis P-Delta, como este modelo) aplica el método de la curvatura nominal con M0e = 0.6·M02 + 0.4·M01 >= 0.4·M02 (manual CFD-EC-2-2004 §3.4.2.2).  Los pilotes flectan en doble curvatura (traslacionales), así que M0e = 0.4·M02 y gobierna la comprobación de 1er orden en los extremos + Mi = N·max(ei, emin): el momento de 2º orden del pilote traslacional en cabeza/pie NO se comprueba (SAP lo espera de un análisis P-Delta).  Valor esperado en SAP = 'sap_est_M0e' (≈ nm1 propio + 1-6 %), no nm2.  Si los detalles de SAP muestran MEd = M02 + Mi + M2, el valor esperado es 'sap_est_estacion' (≈ nm2 con e2 de c = 8 y el Kφ del overwrite).  El pilote se verifica con nm2 (diseno/output/pilotes.md), no con SAP.
- SAP e2 = Kr·Kφ·εyd/(0.45 d)·l0²/8 con d = 327.5 mm: Kφ 1.1129 da e2 = 92.1 mm = CYPE; el e2 estricto del Código (d = h/2 + is = 307 mm) es 98.3 mm (Kφ 'ce_is' = 1.1874).

Procedimiento SAP usado en `sap_est_*` (nuestras fuerzas): ei_mm = 20.0, e2_mm = 92.12, d_mm = 327.5, Kphi = 1.1129, c = 8

## Pilotes: ratio P-M-M (SAP) / η N-M propia / Aprov. CYPE

| pile | nm1[ROM,codigo] | nm2[ROM,codigo] | sap_est_M0e | combo_M0e | gov_M0e | sap_est_estacion | combo_estacion | cype_aprov_fuste | cype_aprov_arranque |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.719 | 0.919 | 0.745 | ELR08 | 1er orden + Mi, cabeza | 0.918 | ELR08 | 0.857 | 0.847 |
| P2 | 0.815 | 0.774 | 0.823 | ELR05 | 1er orden + Mi, pie | 0.823 | ELR05 | 0.843 | 0.819 |
| P3 | 0.695 | 0.987 | 0.734 | ELR08 | 1er orden + Mi, cabeza | 0.984 | ELR08 | 0.925 | 0.907 |
| P4 | 0.764 | 0.638 | 0.770 | ELR05 | 1er orden + Mi, pie | 0.770 | ELR05 | 0.771 | 0.764 |
| P5 | 0.652 | 0.915 | 0.679 | ELR08 | 1er orden + Mi, cabeza | 0.914 | ELR08 | 0.880 | 0.869 |
| P6 | 0.763 | 0.646 | 0.770 | ELR05 | 1er orden + Mi, pie | 0.770 | ELR05 | 0.772 | 0.765 |
| P7 | 0.663 | 0.924 | 0.688 | ELR08 | 1er orden + Mi, cabeza | 0.922 | ELR08 | 0.882 | 0.869 |
| P8 | 0.739 | 0.620 | 0.746 | ELR05 | 1er orden + Mi, pie | 0.746 | ELR05 | 0.746 | 0.740 |
| P13 | 0.630 | 0.893 | 0.658 | ELR08 | 1er orden + Mi, cabeza | 0.891 | ELR08 | 0.855 | 0.844 |
| P14 | 0.735 | 0.618 | 0.742 | ELR05 | 1er orden + Mi, pie | 0.742 | ELR05 | 0.743 | 0.737 |
| P15 | 0.649 | 0.937 | 0.688 | ELR08 | 1er orden + Mi, cabeza | 0.933 | ELR08 | 0.874 | 0.853 |
| P16 | 0.659 | 0.843 | 0.683 | ELR08 | 1er orden + Mi, cabeza | 0.842 | ELR08 | 0.775 | 0.765 |
| P17 | 0.710 | 0.585 | 0.715 | ELR05 | 1er orden + Mi, pie | 0.715 | ELR05 | 0.715 | 0.709 |
| P18 | 0.730 | 0.690 | 0.738 | ELR05 | 1er orden + Mi, pie | 0.738 | ELR05 | 0.742 | 0.733 |

## Vigas: As a flexión (cm²)

| member | section | pos | face | combo | MEd_kNm | As_uls_cm2 | As_min_cm2 | As_prov_cm2 |
|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.200 | bottom | ELR17 | 12.38 | 0.594 | 8.070 | 18.85 |
| VT1 | cara pilote mar - voladizo | -0.200 | top | ELR08 | -58.57 | 2.823 | 7.420 | 15.71 |
| VT1 | cara pilote mar - vano | 0.200 | bottom | ELR17 | 23.45 | 1.127 | 8.070 | 18.85 |
| VT1 | cara pilote mar - vano | 0.200 | top | ELR08 | -316.33 | 15.67 | 7.420 | 15.71 |
| VT1 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 275.78 | 13.68 | 8.070 | 18.85 |
| VT1 | cara pilote tierra - vuelo | 3.650 | bottom | ELR14 | 6.906 | 0.331 | 8.070 | 18.85 |
| VT1 | vano: máx. positivo | 3.250 | bottom | ELR08 | 275.61 | 13.67 | 8.070 | 18.85 |
| VT2 | cara pilote mar - voladizo | -0.200 | top | ELR14 | -10.01 | 0.480 | 4.990 | 15.71 |
| VT2 | cara pilote mar - vano | 0.200 | top | ELR08 | -265.23 | 13.14 | 4.990 | 15.71 |
| VT2 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 261.39 | 13.22 | 6.250 | 21.99 |
| VT2 | cara pilote tierra - vano | 3.250 | top | ELR17 | -0.517 | 0.025 | 4.990 | 15.71 |
| VT2 | cara pilote tierra - vuelo | 3.650 | bottom | ELR20 | 5.150 | 0.247 | 6.250 | 21.99 |
| VT2 | vano: máx. positivo | 2.708 | bottom | ELR08 | 315.95 | 16.18 | 6.250 | 21.99 |
| VT3 | cara pilote mar - voladizo | -0.200 | bottom | ELR17 | 10.59 | 0.509 | 6.250 | 21.99 |
| VT3 | cara pilote mar - voladizo | -0.200 | top | ELR08 | -63.43 | 3.063 | 4.990 | 15.71 |
| VT3 | cara pilote mar - vano | 0.200 | bottom | ELR17 | 20.35 | 0.979 | 6.250 | 21.99 |
| VT3 | cara pilote mar - vano | 0.200 | top | ELR08 | -302.77 | 15.07 | 4.990 | 15.71 |
| VT3 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 258.23 | 13.05 | 6.250 | 21.99 |
| VT3 | cara pilote tierra - vano | 3.250 | top | ELR17 | -0.524 | 0.025 | 4.990 | 15.71 |
| VT3 | cara pilote tierra - vuelo | 3.650 | bottom | ELR14 | 4.209 | 0.202 | 6.250 | 21.99 |
| VT3 | vano: máx. positivo | 2.708 | bottom | ELR08 | 292.70 | 14.91 | 6.250 | 21.99 |
| VT4 | cara pilote mar - voladizo | -0.200 | top | ELR14 | -9.561 | 0.459 | 4.990 | 15.71 |
| VT4 | cara pilote mar - vano | 0.200 | top | ELR08 | -256.24 | 12.68 | 4.990 | 15.71 |
| VT4 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 252.28 | 12.74 | 6.250 | 21.99 |
| VT4 | cara pilote tierra - vano | 3.250 | top | ELR17 | -0.554 | 0.026 | 4.990 | 15.71 |
| VT4 | cara pilote tierra - vuelo | 3.650 | bottom | ELR20 | 4.228 | 0.203 | 6.250 | 21.99 |
| VT4 | vano: máx. positivo | 2.708 | bottom | ELR08 | 298.46 | 15.23 | 6.250 | 21.99 |
| VT5 | cara pilote mar - voladizo | -0.200 | bottom | ELR17 | 10.59 | 0.509 | 6.250 | 21.99 |
| VT5 | cara pilote mar - voladizo | -0.200 | top | ELR08 | -63.45 | 3.064 | 4.990 | 15.71 |
| VT5 | cara pilote mar - vano | 0.200 | bottom | ELR17 | 20.35 | 0.979 | 6.250 | 21.99 |
| VT5 | cara pilote mar - vano | 0.200 | top | ELR08 | -293.96 | 14.62 | 4.990 | 15.71 |
| VT5 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 249.45 | 12.58 | 6.250 | 21.99 |
| VT5 | cara pilote tierra - vano | 3.250 | top | ELR17 | -0.524 | 0.025 | 4.990 | 15.71 |
| VT5 | cara pilote tierra - vuelo | 3.650 | bottom | ELR14 | 4.209 | 0.202 | 6.250 | 21.99 |
| VT5 | vano: máx. positivo | 2.708 | bottom | ELR08 | 287.06 | 14.61 | 6.250 | 21.99 |
| VT6 | cara pilote mar - voladizo | -0.200 | top | ELR14 | -10.01 | 0.480 | 4.990 | 15.71 |
| VT6 | cara pilote mar - vano | 0.200 | top | ELR08 | -247.61 | 12.24 | 4.990 | 15.71 |
| VT6 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 243.84 | 12.29 | 6.250 | 21.99 |
| VT6 | cara pilote tierra - vano | 3.250 | top | ELR17 | -0.517 | 0.025 | 4.990 | 15.71 |
| VT6 | cara pilote tierra - vuelo | 3.650 | bottom | ELR20 | 5.150 | 0.247 | 6.250 | 21.99 |
| VT6 | vano: máx. positivo | 2.217 | bottom | ELR08 | 307.01 | 15.69 | 6.250 | 21.99 |
| VT7 | cara pilote mar - voladizo | -0.200 | bottom | ELR17 | 12.38 | 0.594 | 8.070 | 18.85 |
| VT7 | cara pilote mar - voladizo | -0.200 | top | ELR08 | -58.62 | 2.826 | 7.420 | 15.71 |
| VT7 | cara pilote mar - vano | 0.200 | bottom | ELR17 | 23.45 | 1.127 | 8.070 | 18.85 |
| VT7 | cara pilote mar - vano | 0.200 | top | ELR08 | -289.42 | 14.30 | 7.420 | 15.71 |
| VT7 | cara pilote tierra - vano | 3.250 | bottom | ELR08 | 248.84 | 12.30 | 8.070 | 18.85 |
| VT7 | cara pilote tierra - vuelo | 3.650 | bottom | ELR14 | 6.906 | 0.331 | 8.070 | 18.85 |
| VT7 | vano: máx. positivo | 3.250 | bottom | ELR08 | 248.72 | 12.29 | 8.070 | 18.85 |
| VBM | tramo 1 cara izq. (X=0.40) | 0.400 | top | ELR20 | -20.98 | 2.137 | 1.500 | 4.021 |
| VBM | tramo 1 cara der. (X=6.25) | 6.250 | top | ELR14 | -37.52 | 3.943 | 1.500 | 4.021 |
| VBM | tramo 2 cara izq. (X=6.75) | 6.750 | top | ELR14 | -36.54 | 3.832 | 1.500 | 4.021 |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | top | ELR20 | -29.06 | 3.004 | 1.500 | 4.021 |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | top | ELR20 | -29.89 | 3.094 | 1.500 | 4.021 |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | top | ELR14 | -31.55 | 3.276 | 1.500 | 4.021 |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | top | ELR14 | -31.55 | 3.276 | 1.500 | 4.021 |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | top | ELR20 | -29.89 | 3.094 | 1.500 | 4.021 |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | top | ELR20 | -29.06 | 3.004 | 1.500 | 4.021 |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | top | ELR14 | -36.54 | 3.832 | 1.500 | 4.021 |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | top | ELR14 | -37.52 | 3.943 | 1.500 | 4.021 |
| VBM | tramo 6 cara der. (X=38.60) | 38.60 | top | ELR20 | -20.98 | 2.137 | 1.500 | 4.021 |
| VBM | tramo 1: máx. positivo | 3.000 | bottom | ELR20 | 18.54 | 1.881 | 1.500 | 4.021 |
| VBM | tramo 2: máx. positivo | 10.00 | bottom | ELR14 | 10.77 | 1.078 | 1.500 | 4.021 |
| VBM | tramo 3: máx. positivo | 16.00 | bottom | ELR14 | 12.14 | 1.218 | 1.500 | 4.021 |
| VBM | tramo 4: máx. positivo | 23.00 | bottom | ELR14 | 12.14 | 1.218 | 1.500 | 4.021 |
| VBM | tramo 5: máx. positivo | 29.00 | bottom | ELR14 | 10.77 | 1.078 | 1.500 | 4.021 |
| VBM | tramo 6: máx. positivo | 36.00 | bottom | ELR20 | 18.54 | 1.881 | 1.500 | 4.021 |
| VBT | tramo 1 cara izq. (X=0.40) | 0.400 | top | ELR08 | -21.57 | 2.200 | 1.500 | 4.021 |
| VBT | tramo 1 cara der. (X=6.25) | 6.250 | top | ELR08 | -38.25 | 4.025 | 1.500 | 4.021 |
| VBT | tramo 2 cara izq. (X=6.75) | 6.750 | top | ELR08 | -37.34 | 3.922 | 1.500 | 4.021 |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | top | ELR08 | -29.54 | 3.056 | 1.500 | 4.021 |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | top | ELR08 | -30.52 | 3.164 | 1.500 | 4.021 |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | top | ELR08 | -32.23 | 3.352 | 1.500 | 4.021 |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | top | ELR08 | -32.45 | 3.376 | 1.500 | 4.021 |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | top | ELR08 | -30.28 | 3.138 | 1.500 | 4.021 |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | top | ELR08 | -29.72 | 3.076 | 1.500 | 4.021 |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | top | ELR08 | -37.06 | 3.890 | 1.500 | 4.021 |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | top | ELR08 | -38.41 | 4.042 | 1.500 | 4.021 |
| VBT | tramo 6 cara der. (X=38.60) | 38.60 | top | ELR14 | -21.30 | 2.171 | 1.500 | 4.021 |
| VBT | tramo 1: máx. positivo | 3.000 | bottom | ELR08 | 18.63 | 1.890 | 1.500 | 4.021 |
| VBT | tramo 2: máx. positivo | 10.00 | bottom | ELR08 | 11.04 | 1.105 | 1.500 | 4.021 |
| VBT | tramo 3: máx. positivo | 16.00 | bottom | ELR08 | 12.38 | 1.242 | 1.500 | 4.021 |
| VBT | tramo 4: máx. positivo | 23.00 | bottom | ELR08 | 12.39 | 1.243 | 1.500 | 4.021 |
| VBT | tramo 5: máx. positivo | 29.00 | bottom | ELR08 | 11.02 | 1.103 | 1.500 | 4.021 |
| VBT | tramo 6: máx. positivo | 36.00 | bottom | ELR08 | 18.62 | 1.889 | 1.500 | 4.021 |

## Vigas: Asw/s (cm²/m)

| member | section | face_pos | pos_d | combo | cot_theta | Asw_s_req_cm2_m | Asw_s_req_cot1_cm2_m | V_face_kN | combo_face | sap_est_Asw_s_face_cm2_m | Asw_s_prov_cm2_m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VT1 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 4.240 | 8.481 | 146.55 | ELR14 | 7.802 | 23.56 |
| VT1 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 9.240 | 18.48 | 358.31 | ELR08 | 19.08 | 23.56 |
| VT1 | cara pilote tierra - vano | 3.250 | 2.770 | ELR05 | 2.000 | 4.689 | 9.379 | 161.83 | ELR20 | 8.616 | 23.56 |
| VT1 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 1.843 | 3.686 | 63.70 | ELR08 | 3.391 | 23.56 |
| VT2 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 3.062 | 6.123 | 105.81 | ELR14 | 5.633 | 23.56 |
| VT2 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 12.82 | 25.65 | 539.24 | ELR08 | 28.71 | 23.56 |
| VT2 | cara pilote tierra - vano | 3.250 | 2.770 | ELR20 | 2.000 | 7.675 | 15.35 | 355.26 | ELR20 | 18.91 | 23.56 |
| VT2 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 2.968 | 5.936 | 102.57 | ELR08 | 5.461 | 23.56 |
| VT3 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 5.010 | 10.02 | 173.13 | ELR14 | 9.218 | 23.56 |
| VT3 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 12.40 | 24.80 | 516.83 | ELR08 | 27.52 | 23.56 |
| VT3 | cara pilote tierra - vano | 3.250 | 2.770 | ELR20 | 2.000 | 7.105 | 14.21 | 327.38 | ELR20 | 17.43 | 23.56 |
| VT3 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 2.566 | 5.131 | 88.67 | ELR08 | 4.721 | 23.56 |
| VT4 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 2.836 | 5.672 | 98.01 | ELR14 | 5.218 | 23.56 |
| VT4 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 12.02 | 24.05 | 504.89 | ELR08 | 26.88 | 23.56 |
| VT4 | cara pilote tierra - vano | 3.250 | 2.770 | ELR20 | 2.000 | 7.075 | 14.15 | 328.38 | ELR20 | 17.48 | 23.56 |
| VT4 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 2.696 | 5.391 | 93.16 | ELR08 | 4.960 | 23.56 |
| VT5 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 5.010 | 10.02 | 173.13 | ELR14 | 9.218 | 23.56 |
| VT5 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 12.23 | 24.46 | 510.84 | ELR08 | 27.20 | 23.56 |
| VT5 | cara pilote tierra - vano | 3.250 | 2.770 | ELR20 | 2.000 | 7.105 | 14.21 | 327.38 | ELR20 | 17.43 | 23.56 |
| VT5 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 2.562 | 5.125 | 88.56 | ELR08 | 4.715 | 23.56 |
| VT6 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 3.062 | 6.123 | 105.81 | ELR14 | 5.633 | 23.56 |
| VT6 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 12.49 | 24.97 | 527.22 | ELR08 | 28.07 | 23.56 |
| VT6 | cara pilote tierra - vano | 3.250 | 2.770 | ELR20 | 2.000 | 7.675 | 15.35 | 355.26 | ELR20 | 18.91 | 23.56 |
| VT6 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 2.961 | 5.922 | 102.33 | ELR08 | 5.448 | 23.56 |
| VT7 | cara pilote mar - voladizo | -0.200 | -0.200 | ELR14 | 2.000 | 4.240 | 8.481 | 146.55 | ELR14 | 7.802 | 23.56 |
| VT7 | cara pilote mar - vano | 0.200 | 0.680 | ELR08 | 2.000 | 8.729 | 17.46 | 340.54 | ELR08 | 18.13 | 23.56 |
| VT7 | cara pilote tierra - vano | 3.250 | 2.770 | ELR05 | 2.000 | 4.178 | 8.355 | 161.83 | ELR20 | 8.616 | 23.56 |
| VT7 | cara pilote tierra - vuelo | 3.650 | 3.650 | ELR08 | 2.000 | 1.834 | 3.669 | 63.40 | ELR08 | 3.375 | 23.56 |
| VBM | tramo 1 cara izq. (X=0.40) | 0.400 | 0.634 | ELR20 | 2.000 | 1.622 | 3.244 | 56.59 | ELR20 | 6.180 | 6.702 |
| VBM | tramo 1 cara der. (X=6.25) | 6.250 | 6.016 | ELR14 | 2.000 | 3.501 | 7.001 | 60.24 | ELR14 | 6.579 | 6.702 |
| VBM | tramo 2 cara izq. (X=6.75) | 6.750 | 6.984 | ELR14 | 2.000 | 3.307 | 6.613 | 56.97 | ELR14 | 6.222 | 6.702 |
| VBM | tramo 2 cara der. (X=12.75) | 12.75 | 12.52 | ELR20 | 2.000 | 2.796 | 5.592 | 48.37 | ELR20 | 5.283 | 6.702 |
| VBM | tramo 3 cara izq. (X=13.25) | 13.25 | 13.48 | ELR20 | 2.000 | 2.890 | 5.780 | 49.95 | ELR20 | 5.456 | 6.702 |
| VBM | tramo 3 cara der. (X=19.25) | 19.25 | 19.02 | ELR14 | 2.000 | 2.984 | 5.968 | 51.54 | ELR14 | 5.629 | 6.702 |
| VBM | tramo 4 cara izq. (X=19.75) | 19.75 | 19.98 | ELR14 | 2.000 | 2.984 | 5.968 | 51.54 | ELR14 | 5.629 | 6.702 |
| VBM | tramo 4 cara der. (X=25.75) | 25.75 | 25.52 | ELR20 | 2.000 | 2.890 | 5.780 | 49.95 | ELR20 | 5.456 | 6.702 |
| VBM | tramo 5 cara izq. (X=26.25) | 26.25 | 26.48 | ELR20 | 2.000 | 2.796 | 5.592 | 48.37 | ELR20 | 5.283 | 6.702 |
| VBM | tramo 5 cara der. (X=32.25) | 32.25 | 32.02 | ELR14 | 2.000 | 3.307 | 6.613 | 56.97 | ELR14 | 6.222 | 6.702 |
| VBM | tramo 6 cara izq. (X=32.75) | 32.75 | 32.98 | ELR14 | 2.000 | 3.501 | 7.001 | 60.24 | ELR14 | 6.579 | 6.702 |
| VBM | tramo 6 cara der. (X=38.60) | 38.60 | 38.37 | ELR20 | 2.000 | 1.622 | 3.244 | 56.59 | ELR20 | 6.180 | 6.702 |
| VBT | tramo 1 cara izq. (X=0.40) | 0.400 | 0.634 | ELR08 | 2.000 | 1.538 | 3.077 | 57.19 | ELR08 | 6.245 | 6.702 |
| VBT | tramo 1 cara der. (X=6.25) | 6.250 | 6.016 | ELR08 | 2.000 | 3.662 | 7.324 | 62.95 | ELR08 | 6.875 | 6.702 |
| VBT | tramo 2 cara izq. (X=6.75) | 6.750 | 6.984 | ELR08 | 2.000 | 3.472 | 6.943 | 59.75 | ELR08 | 6.526 | 6.702 |
| VBT | tramo 2 cara der. (X=12.75) | 12.75 | 12.52 | ELR08 | 2.000 | 2.890 | 5.780 | 49.95 | ELR08 | 5.455 | 6.702 |
| VBT | tramo 3 cara izq. (X=13.25) | 13.25 | 13.48 | ELR08 | 2.000 | 2.993 | 5.986 | 51.69 | ELR08 | 5.645 | 6.702 |
| VBT | tramo 3 cara der. (X=19.25) | 19.25 | 19.02 | ELR08 | 2.000 | 3.128 | 6.257 | 53.97 | ELR08 | 5.894 | 6.702 |
| VBT | tramo 4 cara izq. (X=19.75) | 19.75 | 19.98 | ELR08 | 2.000 | 3.143 | 6.286 | 54.21 | ELR08 | 5.921 | 6.702 |
| VBT | tramo 4 cara der. (X=25.75) | 25.75 | 25.52 | ELR08 | 2.000 | 2.975 | 5.951 | 51.39 | ELR08 | 5.612 | 6.702 |
| VBT | tramo 5 cara izq. (X=26.25) | 26.25 | 26.48 | ELR08 | 2.000 | 2.901 | 5.802 | 50.14 | ELR08 | 5.476 | 6.702 |
| VBT | tramo 5 cara der. (X=32.25) | 32.25 | 32.02 | ELR08 | 2.000 | 3.450 | 6.900 | 59.39 | ELR08 | 6.486 | 6.702 |
| VBT | tramo 6 cara izq. (X=32.75) | 32.75 | 32.98 | ELR08 | 2.000 | 3.669 | 7.337 | 63.07 | ELR08 | 6.888 | 6.702 |
| VBT | tramo 6 cara der. (X=38.60) | 38.60 | 38.37 | ELR14 | 2.000 | 1.524 | 3.049 | 56.87 | ELR08 | 6.211 | 6.702 |
