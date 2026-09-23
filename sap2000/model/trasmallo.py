"""Single source of truth for the SAP2000 model of one 40 m module of the Muelle de Trasmallo
(Puerto de Cullera, Valencia), rebuilt from Anejo 10 "Cálculo de estructuras" (CYPECAD 2023
listing, Apéndice 1 "Listados de cálculo muelle de trasmallo").

Everything the emitters need (``tools/write_s2k.py`` -> SAP2000 .$2k text file,
``tools/sap_oapi_run.py`` -> SAP2000 OAPI, ``tools/verify_pynite.py`` -> independent check)
is produced by :func:`build_model` as plain Python data, so every route builds exactly the
same model.

Units: kN, m, C.
Global axes: X along the pier (axes 1..7 at X = 0 ... 39 m), Y across the pier (berthing /
bollard edge at Y = -0.45, seaward pile row Y = 0, landward pile row Y = 3.45), Z up (pile
fixity at Z = 0, deck "Forjado 1" at Z = 7.00 as in CYPECAD).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sections import Section, inverted_l, inverted_tee, rectangle

# ============================================================================================
# 1. GEOMETRY  (Apéndice 1 §1.7 "grupos y plantas", §1.8 "pilares")
# ============================================================================================
N_AXES = 7
AXIS_SPACING = 6.50                                    # 7 amarres every 6.5 m
AXES_X = [round(i * AXIS_SPACING, 6) for i in range(N_AXES)]   # 0.0 ... 39.0
Y_SEA = -0.45                                          # P9..P12, P19..P21 (bollard line)
Y_PILE_SEA = 0.00                                      # P1, P3, P5, P7, P13, P15, P16
Y_PILE_LAND = 3.45                                     # P2, P4, P6, P8, P14, P17, P18
Z_DECK = 7.00                                          # Forjado 1, cota 7.00 (CYPE §1.7)
# Pile length between the fixity and the deck node.  The main text says the fixity is taken
# 7.00 m below the deck, but the CYPECAD run whose results are listed in Apéndice 1 uses
# 'Forjado 1 (0 - 7.25 m)': pile tramo 0.00/7.25, pile head output at 6.70 (= beam soffit,
# 7.25 - 0.55) and the head loads act 7.25 m above the base (equilibrium of §3.7).  7.25 is
# therefore used to reproduce the listing; set 7.00 to follow the text of §9.1.
PILE_LENGTH = 7.25
Z_BASE = round(Z_DECK - PILE_LENGTH, 6)                # empotramiento (cota -0.25)

# Deck mesh (slab shells): X step ~0.5 m, Y lines at the edge, both pile rows and 5 between
MESH_DX_TARGET = 0.50
MESH_NY_BETWEEN_PILES = 6

# Rigid end zones (CYPECAD "nudos con dimensión finita"): the top 0.55 m of every pile lies
# inside the beam depth (altura libre 6.70 m) and the beams are rigid inside the pile width.
PILE_TOP_RIGID = 0.55
BEAM_RIGID_AT_PILE = 0.20

# Physical widths used to split the surface loads exactly like CYPE
EDGE_BEAM_W = 0.25                                     # 25x30 perimeter beams
END_BEAM_W = 0.80                                      # 80x55+15x30 end beams (axes 1 and 7)
INNER_BEAM_W = 0.50                                    # 50x55+15x30+15x30 web width

# ============================================================================================
# 2. MATERIALS  (Anejo 10 §6, Apéndice 1 §1.11 - CYPE Ec values)
# ============================================================================================
@dataclass
class Material:
    name: str
    kind: str            # "Concrete" | "Rebar"
    E: float             # kN/m2
    nu: float
    unit_weight: float   # kN/m3
    alpha: float
    fc: float = 0.0      # kN/m2
    fy: float = 0.0      # kN/m2
    fu: float = 0.0      # kN/m2
    note: str = ""


# Concrete unit weight: the text says 25 kN/m3; CYPECAD works with 2.5 t/m3 x 9.81 =
# 24.525 kN/m3 (pile self weight between base and head in §3.3 = 26.2 kN over 6.70 m, and the
# §3.7 total of 1343.9 kN is reproduced only with this value).  Use 25.0 for a design check.
GAMMA_CONCRETE = 24.525

MATERIALS = [
    Material("HA-50", "Concrete", 33550e3, 0.2, GAMMA_CONCRETE, 1.0e-5, fc=50e3,
             note="Pilotes prefabricados HA-50/F/12/XS3 - Ec = 33550 MPa (CYPE)"),
    Material("HA-35", "Concrete", 30669e3, 0.2, GAMMA_CONCRETE, 1.0e-5, fc=35e3,
             note="Vigas / hormigón in situ HA-35/F/20/XS3 - Ec = 30669 MPa (CYPE)"),
    Material("B500SD", "Rebar", 200e6, 0.3, 76.97, 1.17e-5, fy=500e3, fu=575e3,
             note="Acero para armaduras B 500 SD"),
]

# ============================================================================================
# 3. SECTIONS
# ============================================================================================
@dataclass
class FrameSection:
    name: str
    material: str
    section: Section
    shape: str                               # "Rectangular" | "General"
    modifiers: dict = field(default_factory=dict)
    note: str = ""


def frame_sections() -> dict[str, FrameSection]:
    pile = rectangle("PIL40x40", 0.40, 0.40, "Pilote hincado 40x40 HA-50")
    vt = inverted_tee("VT50x55+15x30+15x30", 0.50, 0.55, 0.15, 0.30,
                      "Viga T invertida: alma 50x55 + ala inferior 15x30 a cada lado")
    vl = inverted_l("VL80x55+15x30", 0.80, 0.55, 0.15, 0.30, wing_side=+1,
                    description="Viga extrema: alma 80x55 + un ala inferior 15x30 (lado del vano)")
    vb = rectangle("VB25x30", 0.25, 0.30, "Viga de borde longitudinal 25x30")
    return {
        "PIL40x40": FrameSection(
            "PIL40x40", "HA-50", pile, "Rectangular", modifiers={"AMod": 2.0},
            note="CYPE 'coeficiente de rigidez axil' = 2.00 -> AMod = 2 (sólo rigidez axial)"),
        "VT50x55+15x30+15x30": FrameSection(
            "VT50x55+15x30+15x30", "HA-35", vt, "General",
            note="Propiedades calculadas de la sección compuesta (no un rectángulo 50x55)"),
        "VL80x55+15x30": FrameSection(
            "VL80x55+15x30", "HA-35", vl, "General",
            note="Propiedades calculadas de la sección compuesta en L invertida"),
        "VB25x30": FrameSection("VB25x30", "HA-35", vb, "Rectangular"),
    }


# Hollow-core slab PRENOR P-25+5/120 (Apéndice 1 §1.10): canto total 30 cm, capa 5 cm,
# peso propio 4.1 kN/m2, rigidez total (P25-1) EI = 63550 kN m2/m.  CYPE analyses the plates
# as one-way members continuous over the beams, so the deck is an orthotropic thin shell:
# full bending stiffness along X (span), negligible across the plates and in twist.
SLAB_SECTION = {
    "name": "ALVEO_P25+5",
    "material": "HA-35",
    "thickness": 0.30,
    "EI_span": 63550.0,                 # kN m2 / m
    "m22": 0.01,                        # transverse bending (joints between plates)
    "m12": 0.01,                        # twisting
    "weight_mod": 0.0,                  # weight applied as the 4.10 kN/m2 surface load
    "mass_mod": 0.0,
}


def slab_m11() -> float:
    E = next(m.E for m in MATERIALS if m.name == SLAB_SECTION["material"])
    t = SLAB_SECTION["thickness"]
    return SLAB_SECTION["EI_span"] / (E * t**3 / 12.0)


# ============================================================================================
# 4. LOADS  (Anejo 10 §7, Apéndice 1 §1.4)
# ============================================================================================
Q_SLAB_PP = 4.10     # kN/m2 alveoplaca + capa (part of CYPE "Peso propio")
Q_CM = 1.80          # kN/m2 cargas muertas (pavimento + 0.50 adherencias marinas)
Q_SCU = 15.0         # kN/m2 sobrecarga de uso

# Apéndice 1 §1.4.5 "Cargas en cabeza de pilar" - CYPE sign convention:
#   N > 0 compression (downward); Qx, Qy along +X/+Y; My pairs with Qy (My = Qy * lever).
# (ref, x, y): {hypothesis: (N, Mx, My, Qx, Qy, T)}   [kN, kN m]
PILE_HEAD_LOADS = {
    ("P1", 0.0, 0.00): {"TB1": (17.0, 0, 0, 0, -17.0, 0)},
    ("P2", 0.0, 3.45): {"TB1": (-17.0, 0, 0, 0, -17.0, 0)},
    ("P3", 6.5, 0.00): {"TB1": (34.0, 0, 0, 0, -34.0, 0)},
    ("P4", 6.5, 3.45): {"TB1": (-34.0, 0, 0, 0, -34.0, 0)},
    ("P5", 13.0, 0.00): {"TB1": (34.0, 0, 0, 0, -34.0, 0)},
    ("P6", 13.0, 3.45): {"TB1": (-34.0, 0, 0, 0, -34.0, 0)},
    ("P7", 19.5, 0.00): {"TB1": (34.0, 0, 0, 0, -34.0, 0)},
    ("P8", 19.5, 3.45): {"TB1": (-34.0, 0, 0, 0, -34.0, 0)},
    ("P9", 0.0, -0.45): {"TB1": (0.0, 0, -37.5, 0, -75.0, 0),
                         "TB2": (53.0, 0, 0, 0, 0, 0), "TB3": (-53.0, 0, 0, 0, 0, 0)},
    ("P11", 13.0, -0.45): {"TB1": (0.0, 0, -37.5, 0, -75.0, 0),
                           "TB2": (53.0, 0, 0, 0, 0, 0), "TB3": (-53.0, 0, 0, 0, 0, 0)},
    ("P13", 26.0, 0.00): {"TB1": (34.0, 0, 0, 0, -34.0, 0)},
    ("P14", 26.0, 3.45): {"TB1": (-34.0, 0, 0, 0, -34.0, 0)},
    ("P15", 32.5, 0.00): {"TB1": (34.0, 0, 0, 0, -34.0, 0)},
    ("P17", 32.5, 3.45): {"TB1": (-34.0, 0, 0, 0, -34.0, 0)},
    ("P18", 39.0, 3.45): {"TB1": (-17.0, 0, 0, 0, -17.0, 0)},
    ("P19", 26.0, -0.45): {"TB1": (0.0, 0, -37.5, 0, -75.0, 0),
                           "TB2": (53.0, 0, 0, 0, 0, 0), "TB3": (-53.0, 0, 0, 0, 0, 0)},
    ("P20", 39.0, -0.45): {"TB1": (0.0, 0, -37.5, 0, -75.0, 0),
                           "TB2": (53.0, 0, 0, 0, 0, 0), "TB3": (-53.0, 0, 0, 0, 0, 0)},
}
# The CYPE listing has no 'Tiro bolardo' head load on P16 (X=39, Y=0) although its mirror P1
# has N=+17, Qy=-17 (consistent with the §3.7 totals: sum Qy = -691 kN, sum N = -17 kN).
# Keep False to reproduce CYPE; True adds the (probably intended) symmetric load on P16.
ADD_MISSING_P16_LOAD = False


def cype_to_global(N, Mx, My, Qx, Qy, T):
    """CYPE pile-head load (pile local axes = global, angle 0) -> SAP global joint load
    (F1, F2, F3, M1, M2, M3).

    N > 0 is compression -> F3 = -N.   Qx, Qy -> F1, F2.
    CYPE My goes with Qy (My = Qy x lever: -75 kN x 0.50 m = -37.5 kN m), i.e. it is the
    moment of Qy acting 'lever' above the node; in global axes that moment is
    M1 = -lever x F2 = -My.  Likewise Mx goes with Qx: M2 = +lever x F1 = +Mx.  T -> M3.
    """
    return (Qx, Qy, -N, -My, Mx, T)


# name, SAP design type, self-weight multiplier, description
LOAD_PATTERNS = [
    ("PP", "Dead", 1.0, "Peso propio: vigas y pilotes (25 kN/m3) + alveoplaca 4.10 kN/m2"),
    ("CM", "Super Dead", 0.0, "Cargas muertas 1.80 kN/m2"),
    ("Qa", "Live", 0.0, "Sobrecarga de uso 15 kN/m2"),
    ("TB1", "Other", 0.0, "Tiro bolardo: 75 kN en P9/P11/P19/P20 + cargas en cabeza de pilotes"),
    ("TB2", "Other", 0.0, "Tiro Bolardo 2: +53 kN vertical (hacia abajo) en los bolardos"),
    ("TB3", "Other", 0.0, "Tiro bolardo 3: -53 kN vertical (hacia arriba) en los bolardos"),
]
PATTERN_ORDER = [p[0] for p in LOAD_PATTERNS]


# ============================================================================================
# 5. COMBINATIONS  (Apéndice 1 §1.6.2) - factors for (PP, CM, Qa, TB1, TB2, TB3)
# ============================================================================================
def _family(g: float, q: float, psi_q: float, psi_w: float) -> list[tuple]:
    """The 22 CYPE combinations of one family, in the order of the listing."""
    rows = [(1.0, 0.0, None), (g, 0.0, None), (1.0, q, None), (g, q, None)]
    for k in range(3):
        rows += [(1.0, 0.0, (k, q)), (g, 0.0, (k, q)),
                 (1.0, q * psi_q, (k, q)), (g, q * psi_q, (k, q)),
                 (1.0, q, (k, q * psi_w)), (g, q, (k, q * psi_w))]
    out = []
    for gg, qa, w in rows:
        tb = [0.0, 0.0, 0.0]
        if w:
            tb[w[0]] = round(w[1], 6)
        out.append((gg, gg, round(qa, 6), *tb))
    return out


COMBOS = {
    # E.L.U. de rotura. Hormigón (Código Estructural): G 1.35/1.00, Q 1.50, psi 0.7 / 0.6
    "ELU": _family(1.35, 1.50, 0.70, 0.60),
    # E.L.U. de rotura. Hormigón en cimentaciones: G 1.60/1.00, Q 1.60, psi 0.7 / 0.6
    "CIM": _family(1.60, 1.60, 0.70, 0.60),
    # Desplazamientos (acciones características)
    "ELS": [(1, 1, 0, 0, 0, 0), (1, 1, 1, 0, 0, 0), (1, 1, 0, 1, 0, 0), (1, 1, 1, 1, 0, 0),
            (1, 1, 0, 0, 1, 0), (1, 1, 1, 0, 1, 0), (1, 1, 0, 0, 0, 1), (1, 1, 1, 0, 0, 1)],
}


# ============================================================================================
# 6. MODEL ASSEMBLY
# ============================================================================================
def _r(v: float, nd: int = 6) -> float:
    v = round(v, nd)
    return 0.0 if v == 0 else v


def mesh_lines() -> tuple[list[float], list[float]]:
    xs: list[float] = []
    for a, b in zip(AXES_X[:-1], AXES_X[1:]):
        n = max(1, round((b - a) / MESH_DX_TARGET))
        xs += [a + (b - a) * k / n for k in range(n)]
    xs.append(AXES_X[-1])
    ys = [Y_SEA, Y_PILE_SEA]
    n = MESH_NY_BETWEEN_PILES
    ys += [Y_PILE_SEA + (Y_PILE_LAND - Y_PILE_SEA) * k / n for k in range(1, n + 1)]
    return [_r(x) for x in xs], [_r(y) for y in ys]


def _net_fraction(x0, x1, y0, y1, holes, n=40) -> float:
    """Fraction of rectangle [x0,x1]x[y0,y1] NOT covered by any rectangle in ``holes``."""
    free = 0
    for a in range(n):
        x = x0 + (a + 0.5) * (x1 - x0) / n
        for b in range(n):
            y = y0 + (b + 0.5) * (y1 - y0) / n
            if not any(h[0] <= x <= h[1] and h[2] <= y <= h[3] for h in holes):
                free += 1
    return free / (n * n)


def build_model() -> dict:
    secs = frame_sections()
    xs, ys = mesh_lines()
    ix_axis = {x: xs.index(x) for x in AXES_X}
    iy_sea, iy_ps, iy_pl = ys.index(Y_SEA), ys.index(Y_PILE_SEA), ys.index(Y_PILE_LAND)

    joints: dict[str, tuple[float, float, float]] = {}
    frames: list[dict] = []
    areas: list[dict] = []
    restraints: dict[str, tuple[bool, ...]] = {}
    joint_loads: list[dict] = []
    frame_loads: list[dict] = []
    area_loads: list[dict] = []
    groups: dict[str, list[tuple[str, str]]] = {}
    cype_names: dict[str, str] = {}

    def grp(g: str, kind: str, name: str) -> None:
        groups.setdefault(g, []).append((kind, name))

    def dj(ix: int, iy: int) -> str:            # deck joint name
        return f"D{ix:02d}_{iy}"

    # ---- joints ------------------------------------------------------------------------------
    for ix, x in enumerate(xs):
        for iy, y in enumerate(ys):
            joints[dj(ix, iy)] = (x, y, Z_DECK)
    pile_sea = ["P1", "P3", "P5", "P7", "P13", "P15", "P16"]
    pile_land = ["P2", "P4", "P6", "P8", "P14", "P17", "P18"]
    edge_pts = ["P9", "P10", "P11", "P12", "P19", "P21", "P20"]
    for a, x in enumerate(AXES_X, start=1):
        for row, y, cn in (("S", Y_PILE_SEA, pile_sea[a - 1]), ("L", Y_PILE_LAND, pile_land[a - 1])):
            b = f"B{a}{row}"
            joints[b] = (x, y, Z_BASE)
            restraints[b] = (True,) * 6
            cype_names[b] = cn
        cype_names[dj(ix_axis[x], iy_ps)] = pile_sea[a - 1]
        cype_names[dj(ix_axis[x], iy_pl)] = pile_land[a - 1]
        cype_names[dj(ix_axis[x], iy_sea)] = edge_pts[a - 1]

    # ---- piles ---------------------------------------------------------------------------------
    for a, x in enumerate(AXES_X, start=1):
        for row, iy, cn in (("S", iy_ps, pile_sea[a - 1]), ("L", iy_pl, pile_land[a - 1])):
            name = f"PIL_{cn}"
            frames.append({"name": name, "i": f"B{a}{row}", "j": dj(ix_axis[x], iy),
                           "section": "PIL40x40", "kind": "pile", "cype": cn, "angle": 0.0,
                           "station_max": 0.25, "offsets": (0.0, PILE_TOP_RIGID)})
            grp("PILOTES", "Frame", name)

    # ---- transverse beams (CYPE pórticos 3..9), split at every deck mesh line ------------------
    portico_of_axis = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9}
    for a, x in enumerate(AXES_X, start=1):
        sec = "VL80x55+15x30" if a in (1, N_AXES) else "VT50x55+15x30+15x30"
        ix = ix_axis[x]
        for iy in range(len(ys) - 1):
            name = f"VT{a}_{iy + 1}"
            off_i = BEAM_RIGID_AT_PILE if iy in (iy_ps, iy_pl) else 0.0
            off_j = BEAM_RIGID_AT_PILE if iy + 1 in (iy_ps, iy_pl) else 0.0
            frames.append({"name": name, "i": dj(ix, iy), "j": dj(ix, iy + 1), "section": sec,
                           "kind": "beam_t", "axis": a, "portico": portico_of_axis[a],
                           "angle": 0.0, "station_max": 0.25, "offsets": (off_i, off_j)})
            grp("VIGAS_TRANSVERSALES", "Frame", name)
            grp(f"PORTICO_{portico_of_axis[a]}", "Frame", name)

    # ---- longitudinal edge beams 25x30 (CYPE pórtico 1 at Y=-0.45, pórtico 10 at Y=3.45) ------
    for tag, iy, por in (("M", iy_sea, 1), ("T", iy_pl, 10)):
        for ix in range(len(xs) - 1):
            name = f"VB{tag}_{ix + 1:02d}"
            def half_web(xv: float) -> float:
                if xv in (AXES_X[0], AXES_X[-1]):
                    return END_BEAM_W / 2
                return INNER_BEAM_W / 2 if xv in AXES_X else 0.0
            frames.append({"name": name, "i": dj(ix, iy), "j": dj(ix + 1, iy),
                           "section": "VB25x30", "kind": "beam_edge", "portico": por,
                           "angle": 0.0, "station_max": 0.5,
                           "offsets": (half_web(xs[ix]), half_web(xs[ix + 1]))})
            grp("VIGAS_BORDE", "Frame", name)
            grp(f"PORTICO_{por}", "Frame", name)

    # ---- slab shells (alveoplacas): one quad per mesh cell ---------------------------------
    # beam footprints (plan) used to put the slab self weight only on the net panel
    holes = []
    for a, x in enumerate(AXES_X, start=1):
        w = END_BEAM_W if a in (1, N_AXES) else INNER_BEAM_W
        holes.append((x - w / 2, x + w / 2, Y_SEA - EDGE_BEAM_W / 2, Y_PILE_LAND + EDGE_BEAM_W / 2))
    for y in (Y_SEA, Y_PILE_LAND):
        holes.append((AXES_X[0] - END_BEAM_W / 2, AXES_X[-1] + END_BEAM_W / 2,
                      y - EDGE_BEAM_W / 2, y + EDGE_BEAM_W / 2))
    for ix in range(len(xs) - 1):
        span_idx = next(k for k in range(N_AXES - 1) if AXES_X[k] - 1e-9 <= xs[ix] < AXES_X[k + 1] - 1e-9)
        for iy in range(len(ys) - 1):
            name = f"LOSA_{ix + 1:02d}_{iy + 1}"
            # counter-clockwise seen from +Z, first edge along +X -> local 1 = +X (span)
            areas.append({"name": name, "section": SLAB_SECTION["name"], "span": span_idx + 1,
                          "joints": [dj(ix, iy), dj(ix + 1, iy), dj(ix + 1, iy + 1), dj(ix, iy + 1)]})
            grp("ALVEOPLACAS", "Area", name)
            grp(f"VANO_{span_idx + 1}", "Area", name)
            f_net = _net_fraction(xs[ix], xs[ix + 1], ys[iy], ys[iy + 1], holes)
            if f_net > 0:
                area_loads.append({"area": name, "pattern": "PP", "q": _r(Q_SLAB_PP * f_net, 5)})
            area_loads.append({"area": name, "pattern": "CM", "q": Q_CM})
            area_loads.append({"area": name, "pattern": "Qa", "q": Q_SCU})

    # ---- deck strips outside the axis rectangle (outer half of the perimeter beams) ----------
    width_axes = Y_PILE_LAND - Y_SEA                           # 3.90
    for fr in frames:
        if fr["kind"] == "beam_edge":                          # outer 12.5 cm of the 25 cm beam
            for pat, q in (("CM", Q_CM), ("Qa", Q_SCU)):
                frame_loads.append({"frame": fr["name"], "pattern": pat, "w": _r(q * EDGE_BEAM_W / 2)})
        if fr["kind"] == "beam_t" and fr["axis"] in (1, N_AXES):
            # outer 40 cm of the 80 cm end beam over the full deck width (4.15 m incl. corners)
            strip = (END_BEAM_W / 2) * (width_axes + EDGE_BEAM_W) / width_axes
            for pat, q in (("CM", Q_CM), ("Qa", Q_SCU)):
                frame_loads.append({"frame": fr["name"], "pattern": pat, "w": _r(q * strip)})

    # ---- concentrated loads (CYPE "cargas en cabeza de pilar") ----------------------------
    pos = {(round(x, 3), round(y, 3)): j for j, (x, y, z) in joints.items() if abs(z - Z_DECK) < 1e-9}
    head = dict(PILE_HEAD_LOADS)
    if ADD_MISSING_P16_LOAD:
        head[("P16", 39.0, 0.00)] = {"TB1": (17.0, 0, 0, 0, -17.0, 0)}
    for (ref, x, y), by_hyp in head.items():
        jn = pos[(round(x, 3), round(y, 3))]
        for hyp, vals in by_hyp.items():
            F = tuple(_r(v) for v in cype_to_global(*vals))
            joint_loads.append({"joint": jn, "pattern": hyp, "F": F, "cype": ref})

    deck = sorted(j for j, (_, _, z) in joints.items() if abs(z - Z_DECK) < 1e-9)
    for j in joints:
        grp("NUDOS_BASE" if j.startswith("B") else "NUDOS_TABLERO", "Joint", j)
    for j, cn in cype_names.items():
        grp("CYPE_PILARES", "Joint", j)

    return {
        "joints": joints, "frames": frames, "areas": areas, "restraints": restraints,
        "joint_loads": joint_loads, "frame_loads": frame_loads, "area_loads": area_loads,
        "groups": groups, "sections": secs, "slab": dict(SLAB_SECTION, m11=slab_m11()),
        "materials": MATERIALS, "cype_names": cype_names, "mesh": {"xs": xs, "ys": ys},
        "diaphragm": {"name": "TABLERO", "joints": deck},
    }


def load_totals(model: dict) -> dict[str, float]:
    """Total vertical load per pattern (kN, downward positive) - for checks."""
    tot = {p: 0.0 for p in PATTERN_ORDER}
    L = {}
    for fr in model["frames"]:
        (x1, y1, z1), (x2, y2, z2) = model["joints"][fr["i"]], model["joints"][fr["j"]]
        L[fr["name"]] = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
        fs = model["sections"][fr["section"]]
        gamma = next(m.unit_weight for m in model["materials"] if m.name == fs.material)
        tot["PP"] += fs.section.props["Area"] * gamma * L[fr["name"]]
    A = {}
    for ar in model["areas"]:
        (x1, y1, _), _, (x3, y3, _), _ = (model["joints"][j] for j in ar["joints"])
        A[ar["name"]] = abs((x3 - x1) * (y3 - y1))
    for al in model["area_loads"]:
        tot[al["pattern"]] += al["q"] * A[al["area"]]
    for fl in model["frame_loads"]:
        tot[fl["pattern"]] += fl["w"] * L[fl["frame"]]
    for jl in model["joint_loads"]:
        tot[jl["pattern"]] += -jl["F"][2]
    return tot


if __name__ == "__main__":
    m = build_model()
    print(f"{len(m['joints'])} joints, {len(m['frames'])} frames, {len(m['areas'])} shells")
    print(f"slab m11 modifier = {m['slab']['m11']:.4f}")
    for p, v in load_totals(m).items():
        print(f"  total {p:4s} = {v:9.1f} kN")
