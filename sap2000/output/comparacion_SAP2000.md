# Comparación con Anejo 10 (CYPECAD) — SAP2000 v27.1 (tablas exportadas)

## Totales por hipótesis (suma de arranques vs §3.7)

| hyp | comp | model | cype | diff_% |
|---|---|---|---|---|
| PP | sum N | 1355.2 | 1343.9 | 0.8 |
| PP | sum Qy | 0.0 | 0.0 |  |
| CM | sum N | 301.0 | 297.5 | 1.2 |
| CM | sum Qy | 0.0 | 0.0 |  |
| Qa | sum N | 2580.0 | 2550.1 | 1.2 |
| Qa | sum Qy | -0.0 | 0.0 |  |
| TB1 | sum N | -17.0 | -17.0 | -0.0 |
| TB1 | sum Qy | -691.0 | -691.0 | 0.0 |
| TB2 | sum N | 212.0 | 212.0 | -0.0 |
| TB2 | sum Qy | -0.0 | 0.0 |  |
| TB3 | sum N | -212.0 | -212.0 | 0.0 |
| TB3 | sum Qy | 0.0 | 0.0 |  |

## Envolventes de pilotes (primer orden)

| family | what | pile | model | model_comb | cype | cype_comb | diff_% |
|---|---|---|---|---|---|---|---|
| ELU | N max | P3 | 680.7 | 10 | 673.9 | 10 | 1.0 |
| ELU | N min | P2 | -131.7 | 5 | -136.1 | 5 | -3.2 |
| ELU | |My| max | P3 | -281.9 | 8 | -283.4 | 8 | -0.5 |
| ELU | |Mx| max | P16 | 36.1 | 10 | 20.9 | 22 | 72.5 |
| CIM | N max | P3 | 748.5 | 10 | 741.2 | 10 | 1.0 |
| CIM | N min | P2 | -146.1 | 5 | -150.7 | 5 | -3.0 |
| CIM | |My| max | P3 | -301.5 | 8 | -303.2 | 8 | -0.5 |
| CIM | |Mx| max | P16 | 39.7 | 10 | 23.1 | 22 | 72.1 |
| ELS | N max | P3 | 526.6 | 4 | 521.7 | 4 | 0.9 |
| ELS | N min | P2 | -59.4 | 3 | -63.3 | 3 | -6.2 |
| ELS | |My| max | P3 | -192.1 | 4 | -193.4 | 4 | -0.7 |
| ELS | |Mx| max | P16 | 25.1 | 4 | 14.7 | 8 | 70.8 |

## Vigas transversales — envolvente E.L.U. (tramo entre caras de pilotes)

| portico | section | what | model | cype_listing | cype_drawing | diff_% |
|---|---|---|---|---|---|---|
| Pórtico 3 | 80x55+15x30 | M- cara pilote mar | -316.2 | -315.48 | -318.8 | 0.8 |
| Pórtico 3 | 80x55+15x30 | M- cara pilote tierra | 1.2 |  |  |  |
| Pórtico 3 | 80x55+15x30 | M+ vano | 274.0 | 275.15 | 275.15 | -0.4 |
| Pórtico 3 | 80x55+15x30 | V cara mar | 325.4 | 333.92 |  | -2.6 |
| Pórtico 3 | 80x55+15x30 | V cara tierra | -158.6 | -165.91 |  | 4.4 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote mar | -264.0 | -266.03 | -273.71 | 3.6 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.2 |  |  |  |
| Pórtico 4 | 50x55+15x30+15x30 | M+ vano | 283.0 | 294.61 | 294.6 | -3.9 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara mar | 469.6 | 471.19 |  | -0.3 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara tierra | -354.9 | -333.66 |  | -6.4 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote mar | -301.7 | -305.42 | -312.87 | 3.6 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.2 |  |  |  |
| Pórtico 5 | 50x55+15x30+15x30 | M+ vano | 263.0 | 270.09 | 270.09 | -2.6 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara mar | 446.8 | 440.82 |  | 1.4 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara tierra | -324.3 | -298.84 |  | -8.5 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote mar | -255.1 | -256.9 | -264.0 | 3.4 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.2 |  |  |  |
| Pórtico 6 | 50x55+15x30+15x30 | M+ vano | 268.1 | 275.5 | 275.49 | -2.7 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara mar | 437.8 | 438.61 |  | -0.2 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara tierra | -328.0 | -306.21 |  | -7.1 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote mar | -292.9 | -296.38 | -303.83 | 3.6 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.2 |  |  |  |
| Pórtico 7 | 50x55+15x30+15x30 | M+ vano | 257.4 | 262.67 | 262.67 | -2.0 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara mar | 440.8 | 434.91 |  | 1.4 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara tierra | -324.3 | -298.84 |  | -8.5 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote mar | -246.3 | -247.96 | -255.61 | 3.6 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.2 |  |  |  |
| Pórtico 8 | 50x55+15x30+15x30 | M+ vano | 276.8 | 291.11 | 291.09 | -4.9 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara mar | 462.4 | 464.06 |  | -0.4 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara tierra | -354.9 | -333.66 |  | -6.4 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote mar | -289.3 | -287.95 | -291.23 | 0.7 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote tierra | 1.2 |  |  |  |
| Pórtico 9 | 80x55+15x30 | M+ vano | 247.1 | 247.61 | 247.61 | -0.2 |
| Pórtico 9 | 80x55+15x30 | V cara mar | 307.6 | 315.96 |  | -2.6 |
| Pórtico 9 | 80x55+15x30 | V cara tierra | -158.6 | -165.91 |  | 4.4 |

## Arranques (base, §3.4) por hipótesis: máxima diferencia (con signo) por componente

| hyp | comp | pile | model | cype | diff |
|---|---|---|---|---|---|
| PP | N | P1 | 77.81 | 75.2 | 2.61 |
| PP | Mx | P1 | -5.39 | -3.5 | -1.89 |
| PP | My | P4 | 3.76 | 3.9 | -0.14 |
| PP | Qx | P1 | -2.26 | -1.5 | -0.76 |
| PP | Qy | P4 | 1.59 | 1.7 | -0.1 |
| PP | T | P1 | 0.0 | 0.0 | 0.0 |
| CM | N | P3 | 27.9 | 27.5 | 0.4 |
| CM | Mx | P1 | -1.98 | -1.1 | -0.88 |
| CM | My | P8 | 1.28 | 1.4 | -0.12 |
| CM | Qx | P1 | -0.83 | -0.5 | -0.33 |
| CM | Qy | P5 | -0.53 | -0.6 | 0.07 |
| CM | T | P1 | 0.0 | 0.0 | 0.0 |
| Qa | N | P2 | 100.21 | 96.7 | 3.51 |
| Qa | Mx | P1 | -16.99 | -9.4 | -7.59 |
| Qa | My | P3 | -12.04 | -13.0 | 0.96 |
| Qa | Qx | P1 | -7.14 | -4.0 | -3.14 |
| Qa | Qy | P4 | 5.06 | 5.5 | -0.44 |
| Qa | T | P1 | 0.0 | 0.0 | 0.0 |
| TB1 | N | P17 | -139.69 | -138.5 | -1.19 |
| TB1 | Mx | P1 | 0.79 | 5.2 | -4.41 |
| TB1 | My | P16 | -159.75 | -159.5 | -0.25 |
| TB1 | Qx | P1 | 0.23 | 2.1 | -1.87 |
| TB1 | Qy | P3 | -50.99 | -51.1 | 0.11 |
| TB1 | T | P1 | 0.36 | 0.1 | 0.26 |
| TB2 | N | P7 | 0.64 | 0.4 | 0.24 |
| TB2 | Mx | P1 | 0.08 | 0.7 | -0.62 |
| TB2 | My | P6 | -0.94 | -1.0 | 0.06 |
| TB2 | Qx | P1 | 0.04 | 0.3 | -0.27 |
| TB2 | Qy | P1 | 0.46 | 0.5 | -0.04 |
| TB2 | T | P1 | 0.0 | 0.0 | 0.0 |
| TB3 | N | P7 | -0.64 | -0.4 | -0.24 |
| TB3 | Mx | P1 | -0.08 | -0.7 | 0.62 |
| TB3 | My | P6 | 0.94 | 1.0 | -0.06 |
| TB3 | Qx | P1 | -0.04 | -0.3 | 0.27 |
| TB3 | Qy | P1 | -0.46 | -0.5 | 0.04 |
| TB3 | T | P1 | -0.0 | 0.0 | -0.0 |

## Cabeza de pilotes (z = 6.70, §3.3) por hipótesis: máxima diferencia (con signo) por componente

| hyp | comp | pile | model | cype | diff |
|---|---|---|---|---|---|
| PP | N | P1 | 53.52 | 49.0 | 4.52 |
| PP | Mx | P1 | 9.78 | 6.3 | 3.48 |
| PP | My | P4 | -6.92 | -7.2 | 0.28 |
| PP | Qx | P1 | -2.26 | -1.5 | -0.76 |
| PP | Qy | P4 | 1.59 | 1.7 | -0.1 |
| PP | T | P1 | 0.0 | 0.0 | 0.0 |
| CM | N | P3 | 27.9 | 27.5 | 0.4 |
| CM | Mx | P1 | 3.6 | 2.0 | 1.6 |
| CM | My | P4 | -2.56 | -2.8 | 0.24 |
| CM | Qx | P1 | -0.83 | -0.5 | -0.33 |
| CM | Qy | P5 | -0.53 | -0.6 | 0.07 |
| CM | T | P1 | 0.0 | 0.0 | 0.0 |
| Qa | N | P2 | 100.21 | 96.7 | 3.51 |
| Qa | Mx | P1 | 30.83 | 17.1 | 13.73 |
| Qa | My | P3 | 21.62 | 23.4 | -1.78 |
| Qa | Qx | P1 | -7.14 | -4.0 | -3.14 |
| Qa | Qy | P4 | 5.06 | 5.5 | -0.44 |
| Qa | T | P1 | 0.0 | 0.0 | 0.0 |
| TB1 | N | P17 | -139.69 | -138.5 | -1.19 |
| TB1 | Mx | P16 | -0.68 | 7.3 | -7.98 |
| TB1 | My | P16 | 152.35 | 152.0 | 0.35 |
| TB1 | Qx | P1 | 0.23 | 2.1 | -1.87 |
| TB1 | Qy | P3 | -50.99 | -51.1 | 0.11 |
| TB1 | T | P1 | 0.36 | 0.1 | 0.26 |
| TB2 | N | P7 | 0.64 | 0.4 | 0.24 |
| TB2 | Mx | P1 | -0.15 | -1.3 | 1.15 |
| TB2 | My | P7 | 0.43 | 0.5 | -0.07 |
| TB2 | Qx | P1 | 0.04 | 0.3 | -0.27 |
| TB2 | Qy | P1 | 0.46 | 0.5 | -0.04 |
| TB2 | T | P1 | 0.0 | 0.0 | 0.0 |
| TB3 | N | P7 | -0.64 | -0.4 | -0.24 |
| TB3 | Mx | P1 | 0.15 | 1.3 | -1.15 |
| TB3 | My | P7 | -0.43 | -0.5 | 0.07 |
| TB3 | Qx | P1 | -0.04 | -0.3 | 0.27 |
| TB3 | Qy | P1 | -0.46 | -0.5 | 0.04 |
| TB3 | T | P1 | -0.0 | 0.0 | -0.0 |
