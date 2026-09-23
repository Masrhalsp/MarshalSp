# Comparación con Anejo 10 (CYPECAD) — PyNite (verificación)

## Totales por hipótesis (suma de arranques vs §3.7)

| hyp | comp | model | cype | diff_% |
|---|---|---|---|---|
| PP | sum N | 1355.8 | 1343.9 | 0.9 |
| PP | sum Qy | 0.0 | 0.0 |  |
| CM | sum N | 301.0 | 297.5 | 1.2 |
| CM | sum Qy | 0.0 | 0.0 |  |
| Qa | sum N | 2580.0 | 2550.1 | 1.2 |
| Qa | sum Qy | 0.0 | 0.0 |  |
| TB1 | sum N | -17.0 | -17.0 | 0.0 |
| TB1 | sum Qy | -690.9 | -691.0 | 0.0 |
| TB2 | sum N | 212.0 | 212.0 | 0.0 |
| TB2 | sum Qy | 0.0 | 0.0 |  |
| TB3 | sum N | -212.0 | -212.0 | -0.0 |
| TB3 | sum Qy | -0.0 | 0.0 |  |

## Envolventes de pilotes (primer orden)

| family | what | pile | model | model_comb | cype | cype_comb | diff_% |
|---|---|---|---|---|---|---|---|
| ELU | N max | P3 | 684.5 | 10 | 673.9 | 10 | 1.6 |
| ELU | N min | P2 | -129.7 | 5 | -136.1 | 5 | -4.7 |
| ELU | |My| max | P3 | -281.2 | 8 | -283.4 | 8 | -0.8 |
| ELU | |Mx| max | P16 | 29.6 | 10 | 20.9 | 22 | 41.4 |
| CIM | N max | P3 | 752.7 | 10 | 741.2 | 10 | 1.6 |
| CIM | N min | P2 | -144.0 | 5 | -150.7 | 5 | -4.4 |
| CIM | |My| max | P3 | -300.8 | 8 | -303.2 | 8 | -0.8 |
| CIM | |Mx| max | P16 | 32.6 | 10 | 23.1 | 22 | 41.3 |
| ELS | N max | P3 | 529.1 | 4 | 521.7 | 4 | 1.4 |
| ELS | N min | P2 | -58.3 | 3 | -63.3 | 3 | -7.9 |
| ELS | |My| max | P3 | -191.7 | 4 | -193.4 | 4 | -0.9 |
| ELS | |Mx| max | P16 | 21.0 | 4 | 14.7 | 8 | 42.7 |

## Vigas transversales — envolvente E.L.U. (tramo entre caras de pilotes)

| portico | section | what | model | cype_listing | cype_drawing | diff_% |
|---|---|---|---|---|---|---|
| Pórtico 3 | 80x55+15x30 | M- cara pilote mar | -312.3 | -315.48 | -318.8 | 2.0 |
| Pórtico 3 | 80x55+15x30 | M- cara pilote tierra | 0.9 |  |  |  |
| Pórtico 3 | 80x55+15x30 | M+ vano | 269.8 | 275.15 | 275.15 | -1.9 |
| Pórtico 3 | 80x55+15x30 | V cara mar | 316.7 | 333.92 |  | -5.1 |
| Pórtico 3 | 80x55+15x30 | V cara tierra | -159.2 | -165.91 |  | 4.1 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote mar | -271.8 | -266.03 | -273.71 | 0.7 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote tierra | -3.5 |  |  |  |
| Pórtico 4 | 50x55+15x30+15x30 | M+ vano | 285.9 | 294.61 | 294.6 | -2.9 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara mar | 433.1 | 471.19 |  | -8.1 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara tierra | -323.6 | -333.66 |  | 3.0 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote mar | -312.7 | -305.42 | -312.87 | 0.1 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote tierra | -2.6 |  |  |  |
| Pórtico 5 | 50x55+15x30+15x30 | M+ vano | 272.6 | 270.09 | 270.09 | 0.9 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara mar | 417.3 | 440.82 |  | -5.3 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara tierra | -292.2 | -298.84 |  | 2.2 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote mar | -267.3 | -256.9 | -264.0 | -1.2 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote tierra | -2.7 |  |  |  |
| Pórtico 6 | 50x55+15x30+15x30 | M+ vano | 275.6 | 275.5 | 275.49 | 0.1 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara mar | 405.5 | 438.61 |  | -7.6 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara tierra | -295.7 | -306.21 |  | 3.4 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote mar | -304.3 | -296.38 | -303.83 | -0.2 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote tierra | -2.6 |  |  |  |
| Pórtico 7 | 50x55+15x30+15x30 | M+ vano | 266.3 | 262.67 | 262.67 | 1.4 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara mar | 411.8 | 434.91 |  | -5.3 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara tierra | -292.2 | -298.84 |  | 2.2 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote mar | -254.4 | -247.96 | -255.61 | 0.5 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote tierra | -3.5 |  |  |  |
| Pórtico 8 | 50x55+15x30+15x30 | M+ vano | 281.4 | 291.11 | 291.09 | -3.3 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara mar | 426.3 | 464.06 |  | -8.1 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara tierra | -323.6 | -333.66 |  | 3.0 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote mar | -284.9 | -287.95 | -291.23 | 2.2 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote tierra | 0.9 |  |  |  |
| Pórtico 9 | 80x55+15x30 | M+ vano | 242.4 | 247.61 | 247.61 | -2.1 |
| Pórtico 9 | 80x55+15x30 | V cara mar | 298.8 | 315.96 |  | -5.4 |
| Pórtico 9 | 80x55+15x30 | V cara tierra | -159.2 | -165.91 |  | 4.1 |

## Arranques por hipótesis: máxima diferencia por componente

| hyp | comp | pile | model | cype | diff |
|---|---|---|---|---|---|
| PP | N | P1 | 77.57 | 75.2 | 2.37 |
| PP | Mx | P1 | -4.8 | -3.5 | -1.3 |
| PP | My | P6 | 3.48 | 3.4 | 0.08 |
| PP | Qx | P1 | -2.02 | -1.5 | -0.52 |
| PP | Qy | P4 | 1.62 | 1.7 | -0.08 |
| PP | T | P1 | -0.01 | 0.0 | -0.01 |
| CM | N | P3 | 28.14 | 27.5 | 0.64 |
| CM | Mx | P3 | 0.67 | 0.1 | 0.57 |
| CM | My | P8 | 1.31 | 1.4 | -0.09 |
| CM | Qx | P3 | 0.28 | 0.1 | 0.18 |
| CM | Qy | P5 | -0.54 | -0.6 | 0.06 |
| CM | T | P1 | -0.0 | 0.0 | -0.0 |
| Qa | N | P3 | 241.18 | 235.7 | 5.48 |
| Qa | Mx | P3 | 5.74 | 1.2 | 4.54 |
| Qa | My | P3 | -12.38 | -13.0 | 0.62 |
| Qa | Qx | P3 | 2.38 | 0.5 | 1.88 |
| Qa | Qy | P4 | 5.19 | 5.5 | -0.31 |
| Qa | T | P1 | -0.03 | 0.0 | -0.03 |
| TB1 | N | P2 | -142.86 | -145.6 | 2.74 |
| TB1 | Mx | P1 | 0.13 | 5.2 | -5.07 |
| TB1 | My | P2 | -177.67 | -181.2 | 3.53 |
| TB1 | Qx | P1 | 0.04 | 2.1 | -2.06 |
| TB1 | Qy | P2 | -52.33 | -53.3 | 0.97 |
| TB1 | T | P16 | 0.77 | 0.1 | 0.67 |
| TB2 | N | P1 | 58.33 | 58.1 | 0.23 |
| TB2 | Mx | P1 | 0.07 | 0.7 | -0.63 |
| TB2 | My | P7 | -0.43 | -0.5 | 0.07 |
| TB2 | Qx | P1 | 0.03 | 0.3 | -0.27 |
| TB2 | Qy | P1 | 0.45 | 0.5 | -0.05 |
| TB2 | T | P1 | 0.0 | 0.0 | 0.0 |
| TB3 | N | P1 | -58.33 | -58.1 | -0.23 |
| TB3 | Mx | P1 | -0.07 | -0.7 | 0.63 |
| TB3 | My | P7 | 0.43 | 0.5 | -0.07 |
| TB3 | Qx | P1 | -0.03 | -0.3 | 0.27 |
| TB3 | Qy | P1 | -0.45 | -0.5 | 0.05 |
| TB3 | T | P1 | -0.0 | 0.0 | -0.0 |
