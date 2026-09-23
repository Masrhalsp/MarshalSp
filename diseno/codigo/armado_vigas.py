"""Reinforcement of the transverse beams (CYPE pórticos 3-9 = model axes 1-7) and of the 25x30
edge beams (pórticos 1 and 10) as designed by CYPECAD in Anejo 10, plus the three
cross-sections and a generator of alternative layouts for the reinforcement search of
``vigas.py``.

Coordinates: mm.  ``BarGroup`` positions are given as (x about the web centre, y above the
soffit), which is how the drawings are dimensioned; ``BeamReinforcement.section()`` converts
them to the gross-centroid axes used by ``seccion.RCSection`` (x horizontal = global X, y up).

Sources of every bar group (keys of diseno/ref/cype_design_reference.json):

* inner frames "50x55+15x30+15x30" (axes 2-6): coordinates of the 16 bars of the P3-P4
  equilibrium table (beams.body_check_P3_P4, P381 table), bar marks of the Pórtico 4 drawing
  (beams.drawings_bar_layout['Pórtico 4'], image205; Pórticos 5-8 'same_bars_as' Pórtico 4).
* end frames "80x55+15x30" (axes 1 and 7): drawings of Pórticos 3 and 9 (image204/image210),
  areas of beams.inferred_bar_layouts (top 15.71 = 5Ø20, bottom 18.85 = 5Ø20 + 1Ø20 ledge).
  Bar x positions are not printed (uniform spacing assumed; irrelevant for bending about x).
  The upper-group D1Ø20/I1Ø20 (490) drawn with its legs pointing down is read as the ledge-top
  bar (closing loop with the ledge-bottom bar); with it active and the 2Ø10 'M. Alas' inactive
  the CYPE §4.3 'N,M' utilisations are reproduced to 0.2 points (93.3/85.2 vs 93.4/85.4 %);
  with the Ø10 active they would be 89.9/82.2 %.  Same pattern as the inner beam (C3).
* edge beams 25x30: drawings image203/image211 (2Ø16 top and bottom, 1eØ8/15) and the listing
  'Área Real' 4.02/4.02 cm², 6.70 cm²/m.

Stirrups of the transverse beams: 37x{(1eØ10+1rØ10)+(1eØ10)}/10 = one closed hoop + one single
leg around the web (3 legs Ø10/100, Asw = 2.36 cm², P364 table) plus one hoop around the
ledges, which is not counted as web shear reinforcement (CYPE bw = 50 cm).
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from seccion import B500SD, HA35, Bar, Concrete, Mode, RCSection, Steel, bar_area  # noqa: E402

REF_JSON = HERE.parent / "ref" / "cype_design_reference.json"

COVER = 50.0                  # mm, XS3 (Anejo 10 / CYPE 'recubrimiento geométrico' 5 cm)
DG = 20.0                     # maximum aggregate size, HA-35/F/20/XS3
STEEL_DENSITY = 7850e-9       # kg/mm3


# ============================================================================================
# cross-sections
# ============================================================================================
@dataclass(frozen=True)
class Geometry:
    """Concrete section as rectangles (x0, x1, y0, y1): x about the web centre, y above the soffit."""
    name: str
    kind: str                         # "T" inverted T, "L" inverted L, "R" rectangle
    rects_soffit: tuple
    bw: float                         # web width
    h: float
    ledge_side: int = 0               # L only: +1 ledge toward +X (axis 1), -1 toward -X (axis 7)
    ledge_w: float = 0.0
    ledge_h: float = 0.0

    @property
    def Ac(self) -> float:
        return sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in self.rects_soffit)

    @property
    def xc(self) -> float:
        return sum((x1 - x0) * (y1 - y0) * (x0 + x1) / 2 for x0, x1, y0, y1 in self.rects_soffit) / self.Ac

    @property
    def yc(self) -> float:
        """Gross centroid above the soffit (244.18 mm for the inner T)."""
        return sum((x1 - x0) * (y1 - y0) * (y0 + y1) / 2 for x0, x1, y0, y1 in self.rects_soffit) / self.Ac

    def to_centroid(self, x: float, y: float) -> tuple[float, float]:
        return x - self.xc, y - self.yc

    @property
    def rects(self) -> list:
        xc, yc = self.xc, self.yc
        return [(x0 - xc, x1 - xc, y0 - yc, y1 - yc) for x0, x1, y0, y1 in self.rects_soffit]

    @property
    def b_bottom(self) -> float:
        """Width at the soffit (tension zone of sagging moments)."""
        return max(x1 for x0, x1, y0, y1 in self.rects_soffit if y0 == 0) - \
            min(x0 for x0, x1, y0, y1 in self.rects_soffit if y0 == 0)

    @property
    def b_top(self) -> float:
        return max(x1 for x0, x1, y0, y1 in self.rects_soffit if y1 == self.h) - \
            min(x0 for x0, x1, y0, y1 in self.rects_soffit if y1 == self.h)

    def I_gross(self) -> float:
        yc = self.yc
        return sum((x1 - x0) * (y1 - y0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((y0 + y1) / 2 - yc) ** 2
                   for x0, x1, y0, y1 in self.rects_soffit)

    def W(self, face: str) -> float:
        """Gross elastic modulus about the fibre of ``face`` ('top' | 'bottom')."""
        return self.I_gross() / ((self.h - self.yc) if face == "top" else self.yc)

    # bottom-row zones for bar layouts: web zone half width and ledge zone (inner, outer) --------
    def web_edge(self, stirrup_phi: float) -> float:
        """x of the inner face of the web stirrup leg (bars of the web zone lie inside)."""
        return self.bw / 2 - COVER - stirrup_phi

    def ledge_outer(self, stirrup_phi: float) -> float:
        """x of the inner face of the ledge hoop at the outer face of the ledge."""
        return self.bw / 2 + self.ledge_w - COVER - stirrup_phi


def geometry_T() -> Geometry:
    """Inner frames 'VIGA_T50x55_ALAS15x30' (CYPE '50x55+15x30+15x30')."""
    return Geometry("50x55+15x30+15x30", "T", ((-250.0, 250.0, 300.0, 550.0), (-400.0, 400.0, 0.0, 300.0)),
                    bw=500.0, h=550.0, ledge_side=0, ledge_w=150.0, ledge_h=300.0)


def geometry_L(ledge_side: int) -> Geometry:
    """End frames 'VIGA_L80x55_ALA15x30' (axis 1, ledge toward +X) / '_M' (axis 7, toward -X)."""
    bottom = (-400.0, 550.0, 0.0, 300.0) if ledge_side > 0 else (-550.0, 400.0, 0.0, 300.0)
    return Geometry("80x55+15x30", "L", ((-400.0, 400.0, 300.0, 550.0), bottom),
                    bw=800.0, h=550.0, ledge_side=ledge_side, ledge_w=150.0, ledge_h=300.0)


def geometry_R() -> Geometry:
    """Edge beams 'VIGA_BORDE_25x30'."""
    return Geometry("25x30", "R", ((-125.0, 125.0, 0.0, 300.0),), bw=250.0, h=300.0)


# ============================================================================================
# reinforcement
# ============================================================================================
@dataclass(frozen=True)
class BarGroup:
    name: str
    phi: float
    xs: tuple                         # x about the web centre [mm]
    y: float                          # above the soffit [mm]
    face: str                         # "top" | "bottom" | "side"
    active_cype: bool = True
    active_codigo: bool = True
    src: str = ""

    @property
    def n(self) -> int:
        return len(self.xs)

    @property
    def As(self) -> float:
        return self.n * bar_area(self.phi)

    def active(self, mode: Mode) -> bool:
        return self.active_cype if mode == Mode.CYPE else self.active_codigo


@dataclass(frozen=True)
class Stirrups:
    """Vertical links: one closed hoop around the web (2 legs) + (legs - 2) single legs."""
    phi: float
    legs: int
    s: float
    src: str = ""

    @property
    def Asw(self) -> float:
        return self.legs * bar_area(self.phi)

    @property
    def asw_s(self) -> float:
        """Asw/s [mm2/mm]."""
        return self.Asw / self.s

    @property
    def leg_s(self) -> float:
        """Area of one leg per unit length [mm2/mm] (torsion: outer hoop legs)."""
        return bar_area(self.phi) / self.s

    @property
    def label(self) -> str:
        extra = f"+{self.legs - 2}r" if self.legs > 2 else ""
        return f"{self.legs} ramas Ø{self.phi:g}/{self.s:g} (1e{extra})"

    def st(self, geom: Geometry) -> float:
        """Transverse spacing between legs (A19.9.2.2(8)); legs evenly across the web."""
        span = geom.bw - 2 * (COVER + self.phi / 2)
        return span / (self.legs - 1) if self.legs > 1 else span

    def weight(self, geom: Geometry) -> float:
        """kg per m of beam (hooks 2 x 10Ø per hoop / leg)."""
        b_in = geom.bw - 2 * COVER - self.phi
        h_in = geom.h - 2 * COVER - self.phi
        length = 2 * (b_in + h_in) + 20 * self.phi + (self.legs - 2) * (h_in + 20 * self.phi)
        return length * bar_area(self.phi) * STEEL_DENSITY * 1000.0 / self.s


class BeamSection(RCSection):
    """``RCSection`` meshed in horizontal strips 0.5 mm high.

    Exact for a horizontal neutral axis (bending about x, the only case of these beams:
    ``capacity_uniaxial``, ``equilibrium`` with My = 0 on symmetric sections, SLS helpers) and
    about 25 times faster than the square-cell mesh; not valid for ``capacity_ray`` /
    ``eta_fast`` with an inclined neutral axis.  For the asymmetric L section the horizontal
    neutral axis means a laterally restrained beam (slab + edge beams); the biaxial ray with
    My = 0 differs by -0.03 % (hogging) / -0.8 % (sagging)."""
    strip: float = 0.5

    def set_mesh(self, cell: float) -> None:
        xs, ys, As = [], [], []
        for (x0, x1, y0, y1) in self.rects:
            ny = max(1, int(round((y1 - y0) / self.strip)))
            dy = (y1 - y0) / ny
            y = y0 + (np.arange(ny) + 0.5) * dy
            xs.append(np.full(ny, (x0 + x1) / 2))
            ys.append(y)
            As.append(np.full(ny, (x1 - x0) * dy))
        self.fx, self.fy, self.fa = np.concatenate(xs), np.concatenate(ys), np.concatenate(As)
        self._cell_now = cell


@dataclass
class BeamReinforcement:
    member: str                        # 'VT1'..'VT7' | 'VBM' | 'VBT'
    label: str
    geom: Geometry
    groups: list
    stirrups: Stirrups
    concrete: Concrete = HA35
    steel: Steel = B500SD
    notes: list = field(default_factory=list)

    def bars(self, mode: Mode = Mode.CYPE, faces: tuple | None = None) -> list[Bar]:
        out = []
        for g in self.groups:
            if faces is not None and g.face not in faces:
                continue
            for x in g.xs:
                xc, yc = self.geom.to_centroid(x, g.y)
                out.append(Bar(xc, yc, g.phi, g.active(mode), g.name))
        return out

    def section(self, mode: Mode = Mode.CYPE, faces: tuple | None = None) -> BeamSection:
        return BeamSection(f"{self.member} {self.geom.name}", self.geom.rects, self.bars(mode, faces),
                           self.concrete, self.steel, mode)

    def face_groups(self, face: str) -> list[BarGroup]:
        return [g for g in self.groups if g.face == face]

    def As(self, face: str) -> float:
        return sum(g.As for g in self.face_groups(face))

    def y_face(self, face: str) -> float:
        gs = self.face_groups(face)
        return sum(g.As * g.y for g in gs) / sum(g.As for g in gs)

    def d(self, face: str) -> float:
        """Effective depth of the ``face`` group (tension face) [mm]."""
        return self.y_face("top") if face == "top" else self.geom.h - self.y_face("bottom")

    def cover_axis(self, face: str) -> float:
        """Distance from the ``face`` fibre to the centroid of its bars."""
        return self.geom.h - self.d(face)

    def phi_max(self, face: str) -> float:
        return max(g.phi for g in self.face_groups(face))

    def describe(self, face: str) -> str:
        gs = self.face_groups(face)
        by_phi: dict = {}
        for g in gs:
            by_phi[g.phi] = by_phi.get(g.phi, 0) + g.n
        return " + ".join(f"{n}Ø{p:g}" for p, n in sorted(by_phi.items(), reverse=True))

    def row_x(self, face: str) -> list[tuple[float, float]]:
        """(x, phi) of the bars of a face row, sorted."""
        return sorted((x, g.phi) for g in self.face_groups(face) for x in g.xs)

    def clear_spacing(self, face: str) -> float:
        row = self.row_x(face)
        return min(b[0] - a[0] - (a[1] + b[1]) / 2 for a, b in zip(row[:-1], row[1:]))

    def max_spacing(self, face: str) -> float:
        row = self.row_x(face)
        return max(b[0] - a[0] for a, b in zip(row[:-1], row[1:]))

    def weight_long(self) -> float:
        """kg per m of beam of all longitudinal bars."""
        return sum(g.As for g in self.groups) * STEEL_DENSITY * 1000.0

    def with_face(self, face: str, groups: list) -> "BeamReinforcement":
        return replace(self, groups=[g for g in self.groups if g.face != face] + list(groups))

    def with_stirrups(self, st: Stirrups) -> "BeamReinforcement":
        return replace(self, stirrups=st)

    def table(self) -> list[dict]:
        rows = []
        for g in self.groups:
            rows.append({"member": self.member, "group": g.name, "face": g.face, "n": g.n, "phi": g.phi,
                         "As_cm2": round(g.As / 100, 2), "y_soffit_mm": g.y,
                         "x_mm": [round(x, 1) for x in g.xs],
                         "active_cype": g.active_cype, "active_codigo": g.active_codigo, "src": g.src})
        st = self.stirrups
        rows.append({"member": self.member, "group": st.label, "face": "stirrups", "n": st.legs, "phi": st.phi,
                     "As_cm2": round(st.Asw / 100, 3), "s_mm": st.s,
                     "Asw_s_cm2_m": round(st.asw_s * 10, 2), "src": st.src})
        return rows


# --------------------------------------------------------------------------------------------
# provided reinforcement (CYPE, Anejo 10)
# --------------------------------------------------------------------------------------------
PORTICO_OF_AXIS = {a: a + 2 for a in range(1, 8)}
STIRRUP_SRC_T = ("beams.body_check_P3_P4 P364 table (Asw 2.36 cm² at s = 100 mm, 3 legs Ø10); drawings "
                 "'37x{(1eØ10+1rØ10)+(1eØ10)} /10' (the second hoop encloses the ledges, not counted)")


def _inner(axis: int) -> BeamReinforcement:
    g = geometry_T()
    top_y, bot_y, side_y = 550.0 - 70.0, 70.0, 235.0
    xs5 = (-180.0, -97.5, 0.0, 97.5, 180.0)
    groups = [
        BarGroup("5Ø20 sup.", 20.0, xs5, top_y, "top",
                 src="P381 table bars 1-5 (y = +235.82 about the centroid); drawing '5Ø20 (471)' "
                     "(beams.drawings_bar_layout['Pórtico 4'].upper)"),
        BarGroup("5Ø20 inf. alma", 20.0, xs5, bot_y, "bottom",
                 src="P381 table bars 9-13 (y = -174.18); drawing '5Ø20 (471)' (lower)"),
        BarGroup("I1Ø20+D1Ø20 inf. alas", 20.0, (-330.0, 330.0), bot_y, "bottom",
                 src="P381 table bars 8, 14; drawing 'I1Ø20+D1Ø20 (490)' (lower)"),
        BarGroup("2Ø10 a 235 (x = ±335)", 10.0, (-335.0, 335.0), side_y, "side",
                 src="P381 table bars 7, 15 (σs = -434.78, counted by CYPE); drawing Ø10 marks "
                     "'I1Ø10+D1Ø10 (470)' / 'M. Alas (421)'"),
        BarGroup("2Ø10 a 235 (x = ±185)", 10.0, (-185.0, 185.0), side_y, "side", active_cype=False,
                 src="P381 table bars 6, 16: σs = 0.00 although strained (CYPE C3 / caveat C7); "
                     "inactive in Mode.CYPE, active in Mode.CODIGO"),
    ]
    st = Stirrups(10.0, 3, 100.0, STIRRUP_SRC_T)
    por = PORTICO_OF_AXIS[axis]
    same = "" if axis == 2 else f" (drawing of Pórtico {por}: 'same_bars_as' Pórtico 4)"
    return BeamReinforcement(f"VT{axis}", f"Pórtico {por} (eje {axis})", g, groups, st,
                             notes=["bar coordinates of the P3-P4 body check (P381)" + same])


def _end(axis: int) -> BeamReinforcement:
    side = +1 if axis == 1 else -1
    g = geometry_L(side)
    por = PORTICO_OF_AXIS[axis]
    img = "image204 (Pórtico 3)" if axis == 1 else "image210 (Pórtico 9)"
    lbl = "D" if side > 0 else "I"
    xs5 = (-330.0, -165.0, 0.0, 165.0, 330.0)
    groups = [
        BarGroup("5Ø20 sup.", 20.0, xs5, 480.0, "top",
                 src=f"drawing {img} '5Ø20 (474)/(472)'; listing As_top_real 15.71; x uniform (assumed)"),
        BarGroup("5Ø20 inf. alma", 20.0, xs5, 70.0, "bottom",
                 src=f"drawing {img} '5Ø20 (471)'; x uniform (assumed)"),
        BarGroup(f"{lbl}1Ø20 inf. ala", 20.0, (side * 480.0,), 70.0, "bottom",
                 src=f"drawing {img} lower '{lbl}1Ø20 (490)'; listing As_bot_real 18.85 = 6Ø20 "
                     "(beams.inferred_bar_layouts)"),
        BarGroup(f"{lbl}1Ø20 sup. ala (a 235)", 20.0, (side * 485.0,), 235.0, "side",
                 src=f"drawing {img} upper-group '{lbl}1Ø20 (490)' (legs 17 pointing down): ledge-top bar "
                     "(INFERENCE); active: reproduces CYPE §4.3 η 93.4/85.4 % to 0.2 pt"),
        BarGroup(f"{lbl}2Ø10 M. Alas (a 235)", 10.0, (side * 335.0, side * 420.0), 235.0, "side",
                 active_cype=False,
                 src=f"drawing {img} '{lbl}2Ø10 M. Alas (421)'; x assumed; inactive in Mode.CYPE (with them "
                     "CYPE's §4.3 η would be 89.9/82.2 %, cf. C3), active in Mode.CODIGO"),
    ]
    st = Stirrups(10.0, 3, 100.0, "drawings '37x{(1eØ10+1rØ10)+(1eØ10)} /10'; listing Asw real 23.56 cm²/m")
    return BeamReinforcement(f"VT{axis}", f"Pórtico {por} (eje {axis})", g, groups, st,
                             notes=["end frame; ledge toward " + ("+X" if side > 0 else "-X")])


def provided(axis: int) -> BeamReinforcement:
    """Reinforcement of the transverse beam of model axis 1..7 (CYPE pórtico axis + 2)."""
    return _end(axis) if axis in (1, 7) else _inner(axis)


EDGE_MEMBERS = {1: "VBM", 10: "VBT"}


def provided_edge(portico: int) -> BeamReinforcement:
    """Edge beams 25x30: pórtico 1 (sea, VBM_*) and pórtico 10 (land, VBT_*)."""
    g = geometry_R()
    img = "image203 (confidence low)" if portico == 1 else "image211/212 (confidence medium)"
    c = COVER + 8.0 + 8.0
    groups = [
        BarGroup("2Ø16 sup.", 16.0, (-125.0 + c, 125.0 - c), 300.0 - c, "top",
                 src=f"drawing {img} 2Ø16 top bars (lapped); listing As_top_real 4.02"),
        BarGroup("2Ø16 inf.", 16.0, (-125.0 + c, 125.0 - c), c, "bottom",
                 src=f"drawing {img} 2Ø16 bottom bars (lapped); listing As_bot_real 4.02"),
    ]
    st = Stirrups(8.0, 2, 150.0, f"drawing {img} '1eØ8 /15'; listing Asw real 6.70 cm²/m")
    return BeamReinforcement(EDGE_MEMBERS[portico], f"Pórtico {portico} (viga de borde)", g, groups, st,
                             notes=["d = 234 mm (CYPE As,min 1.71 cm² reproduced)"])


# ============================================================================================
# layouts for the reinforcement search
# ============================================================================================
def smin_clear(phi: float) -> float:
    """A19.8.2(2): max(k1·Ø, dg + k2, 20 mm), k1 = 1, k2 = 5 mm."""
    return max(phi, DG + 5.0, 20.0)


def _even(n: int, lo: float, hi: float) -> tuple:
    if n == 1:
        return ((lo + hi) / 2,)
    return tuple(lo + (hi - lo) * k / (n - 1) for k in range(n))


def row_layouts(geom: Geometry, face: str, phis=(12.0, 16.0, 20.0, 25.0), stirrup_phi: float = 10.0,
                n_min: int = 2, mixed: bool = True) -> list[tuple[str, list[BarGroup]]]:
    """Single-row layouts that fit the face with the CE clear spacing: a web zone inside the web
    hoop (even spacing, corner bars included) + for the bottom face of T/L sections 0..n bars in
    each ledge zone, at least smin clear from the outer face of the web-hoop leg (the outer web
    bar touches the inside of that leg, so a bar-to-bar smin alone would leave only smin - Ø_link
    for the aggregate between the ledge bar and the leg).  ``mixed``: the ledge bars may be one
    size smaller than the web bars (e.g. Ø20 web + Ø16 ledges)."""
    out = []
    y0 = (geom.h - COVER - stirrup_phi) if face == "top" else (COVER + stirrup_phi)

    def yb(phi):
        return y0 - phi / 2 if face == "top" else y0 + phi / 2
    ledges = face == "bottom" and geom.kind in ("T", "L")
    sides = (+1, -1) if geom.kind == "T" else (geom.ledge_side,)
    for phi in phis:
        pitch = phi + smin_clear(phi)
        a = geom.web_edge(stirrup_phi) - phi / 2
        n_web_max = 1 + int(math.floor(2 * a / pitch + 1e-9))
        for nw in range(max(2, n_min), n_web_max + 1):
            web = _even(nw, -a, a)
            wg = BarGroup(f"{nw}Ø{phi:g} {'sup.' if face == 'top' else 'inf. alma'}", phi, web, yb(phi), face,
                          src="proposal")
            out.append((f"{nw}Ø{phi:g}", [wg]))
            if not ledges:
                continue
            for phl in (phis if mixed else (phi,)):
                if phl > phi or phi / phl > 1.34:          # ledge bars equal or one size smaller
                    continue
                lo = geom.web_edge(stirrup_phi) + stirrup_phi + smin_clear(max(phi, phl)) + phl / 2
                hi = geom.ledge_outer(stirrup_phi) - phl / 2
                if hi < lo:
                    continue
                pl = phl + smin_clear(phl)
                for nl in range(1, 2 + int(math.floor((hi - lo) / pl + 1e-9))):
                    xs = _even(nl, lo, hi) if nl > 1 else (hi,)
                    xl = tuple(sd * x for sd in sides for x in xs)
                    lg = BarGroup(f"{len(xl)}Ø{phl:g} inf. alas", phl, xl, yb(phl), face, src="proposal")
                    if phl == phi:
                        label = f"{nw + len(xl)}Ø{phi:g} ({nw} alma + {len(xl)} alas)"
                    else:
                        label = f"{nw}Ø{phi:g} alma + {len(xl)}Ø{phl:g} alas"
                    out.append((label, [wg, lg]))
    return out


def stirrup_options(geom: Geometry, phis=(8.0, 10.0, 12.0), legs=(2, 3, 4),
                    spacings=(50.0, 60.0, 75.0, 80.0, 100.0, 120.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0)
                    ) -> list[Stirrups]:
    return [Stirrups(p, n, s, "proposal") for p in phis for n in legs for s in spacings]


# ============================================================================================
# consistency with the CYPE listing
# ============================================================================================
def reference_areas() -> list[dict]:
    """'Área Real' of the CYPE listing (zone 3/3L of the span tramo, full bars) vs our layouts."""
    import json
    ref = json.loads(REF_JSON.read_text())
    por = ref["beams"]["listing_armado_vigas_2"]["porticos"]
    rows = []
    for axis in range(1, 8):
        r = provided(axis)
        p = por[f"Pórtico {axis + 2}"]
        z = list(p["tramos"].values())[-1]["zones"][2]          # span tramo, zone 3/3L
        for key, ours in (("As_top_real", r.As("top") / 100), ("As_bot_real", r.As("bottom") / 100),
                          ("Asw_per_m_real", r.stirrups.asw_s * 10)):
            rows.append({"member": r.member, "quantity": key, "ours": round(ours, 2), "cype": z[key],
                         "src": z["src"]})
    for portico in (1, 10):
        r = provided_edge(portico)
        z = next(iter(por[f"Pórtico {portico}"]["tramos"].values()))["zones"][0]
        for key, ours in (("As_top_real", r.As("top") / 100), ("As_bot_real", r.As("bottom") / 100),
                          ("Asw_per_m_real", r.stirrups.asw_s * 10)):
            rows.append({"member": r.member, "quantity": key, "ours": round(ours, 2), "cype": z[key],
                         "src": z["src"]})
    return rows


if __name__ == "__main__":
    for a in (1, 2, 7):
        r = provided(a)
        print(r.member, r.label, r.geom.name, f"yc = {r.geom.yc:.2f}", f"Ac = {r.geom.Ac / 100:.0f} cm2",
              "top", r.describe("top"), "bottom", r.describe("bottom"), r.stirrups.label)
    for row in reference_areas():
        print(row["member"], row["quantity"], row["ours"], row["cype"])
    print(len(row_layouts(geometry_T(), "bottom")), "bottom layouts (T)")
