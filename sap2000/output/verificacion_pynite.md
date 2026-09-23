# Comparación con Anejo 10 (CYPECAD) — PyNite (verificación)

## Totales por hipótesis (suma de arranques vs §3.7)

| hyp | comp | model | cype | diff_% |
|---|---|---|---|---|
| PP | sum N | 1355.2 | 1343.9 | 0.8 |
| PP | sum Qy | 0.0 | 0.0 |  |
| CM | sum N | 301.0 | 297.5 | 1.2 |
| CM | sum Qy | 0.0 | 0.0 |  |
| Qa | sum N | 2580.0 | 2550.1 | 1.2 |
| Qa | sum Qy | 0.0 | 0.0 |  |
| TB1 | sum N | -17.0 | -17.0 | 0.0 |
| TB1 | sum Qy | -691.0 | -691.0 | -0.0 |
| TB2 | sum N | 212.0 | 212.0 | 0.0 |
| TB2 | sum Qy | -0.0 | 0.0 |  |
| TB3 | sum N | -212.0 | -212.0 | -0.0 |
| TB3 | sum Qy | 0.0 | 0.0 |  |

## Envolventes de pilotes (primer orden)

| family | what | pile | model | model_comb | cype | cype_comb | diff_% |
|---|---|---|---|---|---|---|---|
| ELU | N max | P3 | 685.3 | 10 | 673.9 | 10 | 1.7 |
| ELU | N min | P2 | -131.6 | 5 | -136.1 | 5 | -3.3 |
| ELU | |My| max | P3 | -281.9 | 8 | -283.4 | 8 | -0.5 |
| ELU | |Mx| max | P16 | 28.3 | 10 | 20.9 | 22 | 35.4 |
| CIM | N max | P3 | 753.6 | 10 | 741.2 | 10 | 1.7 |
| CIM | N min | P2 | -146.0 | 5 | -150.7 | 5 | -3.1 |
| CIM | |My| max | P3 | -301.6 | 8 | -303.2 | 8 | -0.5 |
| CIM | |Mx| max | P16 | 31.2 | 10 | 23.1 | 22 | 35.4 |
| ELS | N max | P3 | 529.8 | 4 | 521.7 | 4 | 1.5 |
| ELS | N min | P2 | -59.5 | 3 | -63.3 | 3 | -6.0 |
| ELS | |My| max | P3 | -192.2 | 4 | -193.4 | 4 | -0.6 |
| ELS | |Mx| max | P16 | 19.9 | 4 | 14.7 | 8 | 35.6 |

## Vigas transversales — envolvente E.L.U. (tramo entre caras de pilotes)

| portico | section | what | model | cype_listing | cype_drawing | diff_% |
|---|---|---|---|---|---|---|
| Pórtico 3 | 80x55+15x30 | M- cara pilote mar | -314.4 | -315.48 | -318.8 | 1.4 |
| Pórtico 3 | 80x55+15x30 | M- cara pilote tierra | 1.4 |  |  |  |
| Pórtico 3 | 80x55+15x30 | M+ vano | 275.0 | 275.15 | 275.15 | -0.1 |
| Pórtico 3 | 80x55+15x30 | V cara mar | 330.0 | 333.92 |  | -1.2 |
| Pórtico 3 | 80x55+15x30 | V cara tierra | -174.0 | -165.91 |  | -4.9 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote mar | -266.5 | -266.03 | -273.71 | 2.6 |
| Pórtico 4 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.6 |  |  |  |
| Pórtico 4 | 50x55+15x30+15x30 | M+ vano | 288.8 | 294.61 | 294.6 | -2.0 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara mar | 473.7 | 471.19 |  | 0.5 |
| Pórtico 4 | 50x55+15x30+15x30 | V cara tierra | -364.0 | -333.66 |  | -9.1 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote mar | -305.4 | -305.42 | -312.87 | 2.4 |
| Pórtico 5 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.7 |  |  |  |
| Pórtico 5 | 50x55+15x30+15x30 | M+ vano | 268.4 | 270.09 | 270.09 | -0.6 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara mar | 443.6 | 440.82 |  | 0.6 |
| Pórtico 5 | 50x55+15x30+15x30 | V cara tierra | -328.0 | -298.84 |  | -9.8 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote mar | -259.0 | -256.9 | -264.0 | 1.9 |
| Pórtico 6 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.6 |  |  |  |
| Pórtico 6 | 50x55+15x30+15x30 | M+ vano | 274.2 | 275.5 | 275.49 | -0.5 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara mar | 438.8 | 438.61 |  | 0.0 |
| Pórtico 6 | 50x55+15x30+15x30 | V cara tierra | -332.4 | -306.21 |  | -8.6 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote mar | -296.7 | -296.38 | -303.83 | 2.4 |
| Pórtico 7 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.7 |  |  |  |
| Pórtico 7 | 50x55+15x30+15x30 | M+ vano | 262.7 | 262.67 | 262.67 | 0.0 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara mar | 437.8 | 434.91 |  | 0.7 |
| Pórtico 7 | 50x55+15x30+15x30 | V cara tierra | -328.0 | -298.84 |  | -9.8 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote mar | -248.8 | -247.96 | -255.61 | 2.7 |
| Pórtico 8 | 50x55+15x30+15x30 | M- cara pilote tierra | -0.6 |  |  |  |
| Pórtico 8 | 50x55+15x30+15x30 | M+ vano | 282.8 | 291.11 | 291.09 | -2.9 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara mar | 466.8 | 464.06 |  | 0.6 |
| Pórtico 8 | 50x55+15x30+15x30 | V cara tierra | -364.0 | -333.66 |  | -9.1 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote mar | -287.2 | -287.95 | -291.23 | 1.4 |
| Pórtico 9 | 80x55+15x30 | M- cara pilote tierra | 1.4 |  |  |  |
| Pórtico 9 | 80x55+15x30 | M+ vano | 247.8 | 247.61 | 247.61 | 0.1 |
| Pórtico 9 | 80x55+15x30 | V cara mar | 312.2 | 315.96 |  | -1.2 |
| Pórtico 9 | 80x55+15x30 | V cara tierra | -174.0 | -165.91 |  | -4.9 |

## Arranques (base, §3.4) por hipótesis: máxima diferencia (con signo) por componente

| hyp | comp | pile | model | cype | diff |
|---|---|---|---|---|---|
| PP | N | P1 | 77.44 | 75.2 | 2.24 |
| PP | Mx | P1 | -4.76 | -3.5 | -1.26 |
| PP | My | P6 | 3.51 | 3.4 | 0.11 |
| PP | Qx | P1 | -1.99 | -1.5 | -0.49 |
| PP | Qy | P4 | 1.64 | 1.7 | -0.06 |
| PP | T | P1 | -0.01 | 0.0 | -0.01 |
| CM | N | P3 | 28.19 | 27.5 | 0.69 |
| CM | Mx | P3 | 0.67 | 0.1 | 0.57 |
| CM | My | P8 | 1.32 | 1.4 | -0.08 |
| CM | Qx | P3 | 0.28 | 0.1 | 0.18 |
| CM | Qy | P5 | -0.54 | -0.6 | 0.06 |
| CM | T | P1 | -0.0 | 0.0 | -0.0 |
| Qa | N | P3 | 241.65 | 235.7 | 5.95 |
| Qa | Mx | P3 | 5.77 | 1.2 | 4.57 |
| Qa | My | P3 | -12.48 | -13.0 | 0.52 |
| Qa | Qx | P3 | 2.42 | 0.5 | 1.92 |
| Qa | Qy | P4 | 5.23 | 5.5 | -0.27 |
| Qa | T | P1 | -0.02 | 0.0 | -0.02 |
| TB1 | N | P2 | -144.17 | -145.6 | 1.43 |
| TB1 | Mx | P1 | 0.58 | 5.2 | -4.62 |
| TB1 | My | P2 | -179.72 | -181.2 | 1.48 |
| TB1 | Qx | P1 | 0.16 | 2.1 | -1.94 |
| TB1 | Qy | P2 | -52.93 | -53.3 | 0.37 |
| TB1 | T | P16 | 0.53 | 0.1 | 0.43 |
| TB2 | N | P1 | 58.33 | 58.1 | 0.23 |
| TB2 | Mx | P1 | 0.06 | 0.7 | -0.64 |
| TB2 | My | P7 | -0.44 | -0.5 | 0.06 |
| TB2 | Qx | P1 | 0.02 | 0.3 | -0.28 |
| TB2 | Qy | P1 | 0.45 | 0.5 | -0.05 |
| TB2 | T | P1 | 0.0 | 0.0 | 0.0 |
| TB3 | N | P1 | -58.33 | -58.1 | -0.23 |
| TB3 | Mx | P1 | -0.06 | -0.7 | 0.64 |
| TB3 | My | P7 | 0.44 | 0.5 | -0.06 |
| TB3 | Qx | P1 | -0.02 | -0.3 | 0.28 |
| TB3 | Qy | P1 | -0.45 | -0.5 | 0.05 |
| TB3 | T | P1 | -0.0 | 0.0 | -0.0 |

## Cabeza de pilotes (z = 6.70, §3.3) por hipótesis: máxima diferencia (con signo) por componente

| hyp | comp | pile | model | cype | diff |
|---|---|---|---|---|---|
| PP | N | P2 | 48.89 | 44.7 | 4.19 |
| PP | Mx | P1 | 8.57 | 6.3 | 2.27 |
| PP | My | P4 | -7.09 | -7.2 | 0.11 |
| PP | Qx | P1 | -1.99 | -1.5 | -0.49 |
| PP | Qy | P4 | 1.64 | 1.7 | -0.06 |
| PP | T | P1 | -0.01 | 0.0 | -0.01 |
| CM | N | P3 | 28.19 | 27.5 | 0.69 |
| CM | Mx | P3 | -1.21 | -0.3 | -0.91 |
| CM | My | P4 | -2.64 | -2.8 | 0.16 |
| CM | Qx | P3 | 0.28 | 0.1 | 0.18 |
| CM | Qy | P5 | -0.54 | -0.6 | 0.06 |
| CM | T | P1 | -0.0 | 0.0 | -0.0 |
| Qa | N | P3 | 241.65 | 235.7 | 5.95 |
| Qa | Mx | P3 | -10.41 | -2.3 | -8.11 |
| Qa | My | P3 | 22.3 | 23.4 | -1.1 |
| Qa | Qx | P3 | 2.42 | 0.5 | 1.92 |
| Qa | Qy | P4 | 5.23 | 5.5 | -0.27 |
| Qa | T | P1 | -0.02 | 0.0 | -0.02 |
| TB1 | N | P2 | -144.17 | -145.6 | 1.43 |
| TB1 | Mx | P16 | -0.96 | 7.3 | -8.26 |
| TB1 | My | P8 | 162.63 | 161.4 | 1.23 |
| TB1 | Qx | P1 | 0.16 | 2.1 | -1.94 |
| TB1 | Qy | P2 | -52.93 | -53.3 | 0.37 |
| TB1 | T | P16 | 0.53 | 0.1 | 0.43 |
| TB2 | N | P1 | 58.33 | 58.1 | 0.23 |
| TB2 | Mx | P1 | -0.1 | -1.3 | 1.2 |
| TB2 | My | P7 | 0.4 | 0.5 | -0.1 |
| TB2 | Qx | P1 | 0.02 | 0.3 | -0.28 |
| TB2 | Qy | P1 | 0.45 | 0.5 | -0.05 |
| TB2 | T | P1 | 0.0 | 0.0 | 0.0 |
| TB3 | N | P1 | -58.33 | -58.1 | -0.23 |
| TB3 | Mx | P1 | 0.1 | 1.3 | -1.2 |
| TB3 | My | P7 | -0.4 | -0.5 | 0.1 |
| TB3 | Qx | P1 | -0.02 | -0.3 | 0.28 |
| TB3 | Qy | P1 | -0.45 | -0.5 | 0.05 |
| TB3 | T | P1 | -0.0 | 0.0 | -0.0 |
