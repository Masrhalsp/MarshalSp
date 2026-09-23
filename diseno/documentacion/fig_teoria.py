"""Theory figure for the Persian design explanation (01_توضیح_کامل_طراحی.md):
material diagrams of A19.3.1.7 / A19.3.2.7 and the ultimate strain domains (pivots A, B, C of
A19.6.1, Figura 6.1).  Same style and palette as the d1-d8 figures of run_diseno.py.

    python3 diseno/documentacion/fig_teoria.py      # -> diseno/documentacion/figuras/d0_diagramas_pivotes.png

Values: HA-35 / HA-50 with alpha_cc = 1.0 and gamma_c = 1.5 (fcd 23.33 / 33.33 MPa), eps_c2 = 2.0 per
mil, eps_cu2 = 3.5 per mil, n = 2 (fck <= 50); B500SD fyd = 434.78 MPa, Es = 200 GPa; CYPE's steel
limit 10 per mil and its 99.5 % factor (convention C1) are drawn as dashed marks.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import run_diseno as RD  # noqa: E402  (style + palette of the d1-d8 figures)

OUT = HERE / "figuras" / "d0_diagramas_pivotes.png"

EC2, ECU2, ESU = 2.0, 3.5, 10.0            # per mil
FYD, ES = 500 / 1.15, 200_000.0
EYD = FYD / ES * 1000                       # 2.174 per mil


def main(path: Path = OUT) -> Path:
    plt = RD._mpl()
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.5, 4.9), gridspec_kw={"width_ratios": [1, 1, 1.15]})

    # (a) parabola-rectangle, A19.3.1.7 (3.17)-(3.18)
    e = np.linspace(0, ECU2, 300)
    for fck, col in ((50, RD.C_ROM), (35, RD.C_CECY)):
        fcd = fck / 1.5
        s = np.where(e <= EC2, fcd * (1 - (1 - e / EC2) ** 2), fcd)
        a1.plot(e, s, color=col, lw=2.0, label=f"HA-{fck}: fcd = {fcd:.2f} MPa")
        a1.text(ECU2 + 0.05, fcd, f"{fcd:.2f}", color=RD.INK2, fontsize=8.5, va="center")
    for x, t in ((EC2, "εc2 = 2.0 ‰"), (ECU2, "εcu2 = 3.5 ‰")):
        a1.axvline(x, color=RD.MUTED, lw=0.8, ls=(0, (4, 3)))
        a1.text(x - 0.05, 39.0, t, rotation=90, ha="right", va="top", fontsize=8.5, color=RD.INK2)
    a1.text(0.1, 36.5, "parábola n = 2", fontsize=8.5, color=RD.INK2)
    a1.set_xlim(0, 4.1)
    a1.set_ylim(0, 40)
    a1.set_xlabel("εc (‰, compresión)")
    a1.set_ylabel("σc (MPa)")
    a1.set_title("Hormigón: parábola-rectángulo (A19.3.1.7)", loc="left")
    a1.legend(loc="lower right")

    # (b) steel, horizontal top branch (A19.3.2.7(2)b)
    a2.plot([0, EYD, 14.0], [0, FYD, FYD], color=RD.C_ROM, lw=2.0, label="Código (rama horizontal, sin límite)")
    a2.plot([ESU * 0.995], [FYD], marker="o", ms=8, ls="none", color=RD.C_CECY, mec="white", mew=2, zorder=5,
            label="CYPE: fin en 0.995·10 ‰ (C1)")
    a2.annotate("", (14.6, FYD), (13.2, FYD), arrowprops=dict(arrowstyle="->", color=RD.C_ROM, lw=1.2))
    a2.axvline(EYD, color=RD.MUTED, lw=0.8, ls=(0, (4, 3)))
    a2.text(EYD + 0.2, 125, f"εyd = fyd/Es = {EYD:.2f} ‰", fontsize=8.5, color=RD.INK2, rotation=90, va="bottom")
    a2.text(5.0, FYD + 14, f"fyd = 500/1.15 = {FYD:.2f} MPa", fontsize=8.5, color=RD.INK2)
    a2.text(0.3, 470, "Es = 200 000 MPa", fontsize=8.5, color=RD.INK2)
    a2.set_xlim(0, 15)
    a2.set_ylim(0, 520)
    a2.set_xlabel("εs (‰, tracción o compresión)")
    a2.set_ylabel("σs (MPa)")
    a2.set_title("Acero B500SD (A19.3.2.7)", loc="left")
    a2.legend(loc="lower right")

    # (c) strain domains: depth 0 (compressed fibre) .. h; bars at d = 0.875 h
    h, d = 1.0, 0.875
    yC = (1 - EC2 / ECU2) * h
    # domain A: pivot at the tension bars, -eps_su (CYPE limit; the code-strict model has none)
    for et in np.linspace(-ESU, ECU2, 6):
        k = (et + ESU) / d
        a3.plot([et, et - k * h], [0, h], color=RD.C_CECY, lw=1.1, alpha=0.9)
    # domain B: pivot at the top fibre +eps_cu2
    xs = np.linspace(ECU2 / (ECU2 + ESU) * d, h, 6)
    for x in xs:
        a3.plot([ECU2, ECU2 - ECU2 / x * h], [0, h], color=RD.C_ROM, lw=1.1, alpha=0.9)
    # domain C: pivot at depth (1 - eps_c2/eps_cu2)·h with eps_c2, top strain eps_cu2 -> eps_c2
    for et in np.linspace(ECU2, EC2, 5):
        k = (et - EC2) / yC
        a3.plot([et, EC2 - k * (h - yC)], [0, h], color=RD.C_CYPE, lw=1.1, alpha=0.9)
    a3.axvline(0, color=RD.INK2, lw=0.9)
    a3.axhline(d, color=RD.MUTED, lw=0.8, ls=(0, (4, 3)))
    a3.text(3.0, d - 0.02, "armadura traccionada (d)", fontsize=8, color=RD.INK2, va="bottom")
    for (x, y, t, col, ha, dy) in ((-ESU, d, "A", RD.C_CECY, "right", -0.08), (ECU2, 0, "B", RD.C_ROM, "left", 0),
                                   (EC2, yC, "C", RD.C_CYPE, "left", 0)):
        a3.plot([x], [y], marker="o", ms=9, color=col, mec="white", mew=2, zorder=6)
        a3.text(x + (0.45 if ha == "left" else -0.45), y + dy, f"pivote {t}", fontsize=9, fontweight="bold",
                color=RD.INK, ha=ha, va="center")
    a3.text(-ESU - 0.45, d - 0.17, "εs = −10 ‰ (CYPE)", fontsize=8, color=RD.INK2, ha="right", va="center")
    a3.text(ECU2 + 0.3, 0.07, "εc = 3.5 ‰", fontsize=8, color=RD.INK2)
    a3.text(EC2 + 0.45, yC + 0.08, "εc = 2 ‰ a (3/7)·h", fontsize=8, color=RD.INK2)
    a3.set_xlim(-17, 14)
    a3.set_ylim(1.08, -0.08)
    a3.set_xlabel("ε (‰)   tracción ←  0  → compresión")
    a3.set_ylabel("profundidad / h (0 = fibra más comprimida)")
    a3.set_title("Dominios de rotura: pivotes A, B, C (A19.6.1)", loc="left")
    a3.grid(axis="x", color=RD.GRID, lw=0.8)
    from matplotlib.lines import Line2D
    a3.legend(handles=[Line2D([], [], color=RD.C_CECY, lw=2, label="dominio A (acero)"),
                       Line2D([], [], color=RD.C_ROM, lw=2, label="dominio B (hormigón)"),
                       Line2D([], [], color=RD.C_CYPE, lw=2, label="dominio C (compresión)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=8, handlelength=1.6)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(main())
