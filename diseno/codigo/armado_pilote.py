"""Reinforcement of the precast piles 40x40 HA-50 (armado de pilotes), as provided by CYPECAD in
Anejo 10, plus a generic square layout used for the required-steel search and the proposals.

Provided reinforcement (cype_design_reference.json, piles.*):

* shaft, CYPE tramo 'Forjado 1' (head 'Cabeza' and foot 'Pie'): 12Ø25, 4 per face incl. corners
  ('Esquina 4Ø25 + Cara X 4Ø25 + Cara Y 4Ø25', cuantía 3.68 %), ties '2eØ10+1eØ10' at 15 cm,
  geometric cover 5 cm (P220 table).  Bar centres at ±127.5 / ±42.5 mm = 200 - 50 - 10 - 12.5
  (P257 bar table).  The sketch (P220 image16) draws three closed ties: one perimeter tie, one
  around the two middle bar columns and one around the two middle bar rows.
* fixity, CYPE 'Cimentación' ('Arranque', tramo -0.42/0.00): the same 12Ø25 with one Ø8 tie
  ('1eØ8', no spacing printed, P281 table) -> bar centres at ±129.5 / ±43.17 mm (P312).

Section coordinates are about the gross centroid, x along the quay (global X) and y across it
(global Y, bollard pull direction); CYPE bar numbering 1..12 starts at the (-c, +c) corner and runs
clockwise (top face, right face, bottom face, left face), as in the equilibrium tables P257/P312.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from seccion import B500SD, HA50, Bar, Concrete, Mode, RCSection, Steel, bar_area

STEEL_DENSITY = 7850.0          # kg/m3
PILE_B = 400.0                  # mm (square pile)
COVER = 50.0                    # mm, geometric cover to the ties (XS3, 50 years, Anejo 10 P122)
AGGREGATE_MAX = 20.0            # mm (P220 'Tamaño máximo de árido')


@dataclass(frozen=True)
class Ties:
    """Transverse reinforcement (estribos) of one zone."""
    phi: float                   # mm
    spacing: float | None        # mm along the pile (None: not given, e.g. CYPE 'Arranque')
    legs: int                    # full-depth legs per shear direction (VRd,s)
    n_closed: int                # closed ties per set (weight)
    label: str                   # CYPE designation

    @property
    def Asw(self) -> float:
        """Area of one set in one direction [mm2]."""
        return self.legs * bar_area(self.phi)


# '2eØ10+1eØ10': perimeter tie + one tie round the middle columns + one round the middle rows.
# Per direction the perimeter tie and the tie round the middle bar lines give 4 full-depth legs;
# the 85 mm legs of the third tie are not counted (conservative).
TIES_FUSTE = Ties(10.0, 150.0, 4, 3, "2eØ10+1eØ10 c/15")
TIES_ARRANQUE = Ties(8.0, None, 2, 1, "1eØ8")


@dataclass(frozen=True)
class PileLayout:
    """Square pile with ``n_face`` bars per face (corners included), equally spaced, all of
    diameter ``phi``; every bar is held by a tie corner or a cross-tie (as the CYPE sketch)."""
    n_face: int = 4
    phi: float = 25.0
    ties: Ties = TIES_FUSTE
    b: float = PILE_B
    cover: float = COVER
    name: str = ""
    concrete: Concrete = field(default=HA50, repr=False)
    steel: Steel = field(default=B500SD, repr=False)

    # geometry ----------------------------------------------------------------------------------
    @property
    def c(self) -> float:
        """Distance from the centroid to the centre of the corner bars [mm]."""
        return self.b / 2 - self.cover - self.ties.phi - self.phi / 2

    @property
    def n_bars(self) -> int:
        return 4 * (self.n_face - 1)

    @property
    def step(self) -> float:
        """Centre-to-centre bar spacing along a face [mm]."""
        return 2 * self.c / (self.n_face - 1)

    @property
    def clear_spacing(self) -> float:
        """Clear distance between adjacent bars of a face [mm] (A19.8.2)."""
        return self.step - self.phi

    @property
    def c_clear(self) -> float:
        """Clear cover to the longitudinal bars [mm] (c in A19 (7.11))."""
        return self.cover + self.ties.phi

    @property
    def As(self) -> float:
        return self.n_bars * bar_area(self.phi)

    @property
    def Ac(self) -> float:
        return self.b * self.b

    @property
    def label(self) -> str:
        return self.name or f"{self.n_bars}Ø{self.phi:g}"

    def coords(self) -> list[tuple[float, float]]:
        """Bar centres in CYPE order (1 = (-c, +c), clockwise)."""
        c, n = self.c, self.n_face
        line = [-c + i * self.step for i in range(n)]
        top = [(x, c) for x in line]
        right = [(c, y) for y in reversed(line[:-1])]
        bottom = [(x, -c) for x in reversed(line[:-1])]
        left = [(-c, y) for y in line[1:-1]]
        return [(round(x, 6), round(y, 6)) for x, y in top + right + bottom + left]

    def bars(self, phi: float | None = None) -> list[Bar]:
        return [Bar(x, y, self.phi if phi is None else phi) for x, y in self.coords()]

    def section(self, mode: Mode = Mode.CODIGO, cell: float = 2.0, phi: float | None = None) -> RCSection:
        """Fibre section; ``phi`` overrides the bar diameter keeping the bar positions (used to
        scale the steel area of the same layout)."""
        h = self.b / 2
        return RCSection(f"pile {self.label}", [(-h, h, -h, h)], self.bars(phi), self.concrete,
                         self.steel, mode, cell)

    def i_s(self) -> float:
        """Radius of gyration of the total steel about a centroidal axis [mm] (A19 (5.35))."""
        ys = [y for _, y in self.coords()]
        return math.sqrt(sum(y * y for y in ys) / len(ys))

    def shear_group(self) -> tuple[float, float]:
        """(Asl [mm2], d [mm]) for VRd,c of the piles, CYPE convention C10: every bar except the
        row on the compressed face; d = depth of their centroid (8Ø25, 263.75 mm)."""
        ys = [y for _, y in self.coords() if y < self.c - 1e-6]
        a = bar_area(self.phi)
        return len(ys) * a, self.b / 2 - sum(ys) / len(ys)

    # quantities --------------------------------------------------------------------------------
    def tie_length_per_set(self) -> float:
        """Centre-line length of one set of ties incl. 135° hooks (2 x 10 Øt per tie) [mm].
        Perimeter tie plus inner ties/cross-ties giving ``n_face`` legs per direction."""
        t = self.ties.phi
        side = self.b - 2 * self.cover - t
        inner_legs = max(self.n_face - 2, 0)                  # per direction
        closed, cross = inner_legs // 2, inner_legs % 2       # inner closed ties / cross-ties
        leg = 2 * self.c + self.phi + t
        short = self.step * max(self.n_face - 3, 1) + self.phi + t
        length = 4 * side + 2 * (inner_legs * leg + closed * 2 * short)
        pieces = 1 + 2 * (closed + cross)
        return length + pieces * 20 * t

    def weight_per_m(self) -> dict:
        """Steel weight [kg/m of pile]: longitudinal + ties."""
        long_kg = self.As * 1e-6 * STEEL_DENSITY
        s = self.ties.spacing or 150.0
        ties_kg = self.tie_length_per_set() * 1e-3 * bar_area(self.ties.phi) * 1e-6 * STEEL_DENSITY * 1000.0 / s
        return {"longitudinal": long_kg, "ties": ties_kg, "total": long_kg + ties_kg}

    def with_(self, **kw) -> "PileLayout":
        return replace(self, **kw)


# Provided reinforcement (CYPE): shaft/head section and fixity section
PROVIDED = {
    "fuste": PileLayout(4, 25.0, TIES_FUSTE, name="12Ø25"),
    "arranque": PileLayout(4, 25.0, TIES_ARRANQUE, name="12Ø25"),
}
ZONE_LABEL = {"fuste": "Forjado 1 (cercos Ø10)", "arranque": "Cimentación / arranque (cerco Ø8)"}


def practical_layouts(ties_fuste_phi: float = 8.0) -> list[dict]:
    """Candidate pile layouts for the proposal search: 8/12/16/20 bars of Ø16-Ø32 with ties
    Øt = max(ties_fuste_phi, Ømax/4) at s = min(150, 0.6·scl,max) rounded down to 25 mm in the
    shaft (A19.9.5.3(3)-(4)) and the CYPE Ø8 tie at the fixity."""
    out = []
    for n_face in (3, 4, 5, 6):
        for phi in (16.0, 20.0, 25.0, 32.0):
            t = ties_fuste_phi if ties_fuste_phi >= max(6.0, phi / 4) else 10.0
            s_max = min(15 * phi, 300.0, PILE_B)
            s = min(150.0, math.floor(0.6 * s_max / 25.0) * 25.0)
            ties = Ties(t, s, n_face, 1 + max(n_face - 2, 0), f"Ø{t:g} c/{s / 10:g}")
            fuste = PileLayout(n_face, phi, ties)
            arr = PileLayout(n_face, phi, Ties(8.0, None, 2, 1, "1eØ8"))
            if fuste.clear_spacing < max(phi, AGGREGATE_MAX + 5.0, 20.0):
                continue
            out.append({"fuste": fuste, "arranque": arr})
    return out
