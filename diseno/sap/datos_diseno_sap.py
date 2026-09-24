"""Single source of the SAP2000 v27.1 concrete-frame-design data of the Muelle de Trasmallo
model ("Eurocode 2-2004", CEN Default with the Spanish partial factors), used by

    diseno/sap/write_s2k_diseno.py   -> .$2k text files (model + design tables)
    diseno/sap/sap_oapi_diseno.py    -> OAPI script (settings, analysis, design, results)
    diseno/sap/leer_diseno_sap.py    -> comparison of SAP's design with the Código Estructural checks
    diseno/sap/GUIA_SAP_DISENO.md    -> GUI guide (values quoted from here)

Every value and its reason are taken from diseno/sap/sap_design_spec.md (§0 decisions,
A.2-A.9 OAPI, C.1-C.10 .$2k tables).  Units: kN, m (SAP model units).

Beams: SAP designs only Rectangular / Circular / Tee / Angle concrete sections with rebar data
(spec B.1-B.2), so the composite "General" sections of the analysis model (inverted T
50x55+15x30+15x30, inverted L 80x55+15x30) are re-defined as the **web rectangles** 0.50x0.55 /
0.80x0.55 carrying 8 section property modifiers that restore the composite A, As2, As3, J, I22,
I33, mass and weight (spec A.6/B.3; modifiers act on the analysis only [S18]).  The analysis is
therefore identical to the current model; the design sees the web rectangle (exact for sagging,
slightly conservative for hogging and for torsion, spec B.3).
"""

from __future__ import annotations

import functools
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _p in (ROOT / "sap2000" / "model",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import trasmallo as tm  # noqa: E402

# ============================================================================================
# 1. code and preferences  (spec §0, A.1, A.2, C.1, C.9)
# ============================================================================================
DESIGN_CODE = "Eurocode 2-2004"          # not "EN 1992-1-1:2023" (v27.0 separate code) [S5][S27]


@dataclass(frozen=True)
class Preference:
    """One EC2 design preference: OAPI item number and value [S1], .$2k field and text [G6][G7],
    GUI label, CEN default [S16 App. C/F] and the reason for the value."""
    item: int
    field: str
    value: float
    s2k: object
    gui: str
    default: str
    why: str


PREFERENCES: tuple[Preference, ...] = (
    Preference(1, "Country", 1, "CEN Default", "Country", "CEN Default",
               "SAP has no Spanish annex: CEN Default + explicit gamma/alpha (= CE Anejo 19 / CYPE)"),
    Preference(2, "CombosEq", 1, "Eq. 6.10", "Combinations equation", "Eq. 6.10",
               "only used by auto-generated combos (switched off)"),
    Preference(3, "SOM", 2, "Nominal Curvature", "Second Order Method", "Nominal Curvature",
               "A19.5.8.8 nominal curvature, as CYPE"),
    Preference(4, "NumCurves", 48, 48, "Number of Interaction Curves", "24",
               "biaxial piles near eta = 1: 7.5 deg between curves instead of 15"),
    Preference(5, "NumPoints", 21, 21, "Number of Interaction Points", "11",
               "finer P-M curves (ratios close to 1)"),
    Preference(6, "MinEccen", 1, True, "Consider Minimum Eccentricity?", "Yes",
               "A19.6.1(4): e0 >= max(h/30, 20 mm)"),
    Preference(7, "Theta0", 0.005, 0.005, "Theta0", "0.005", "A19.5.2(5): theta0 = 1/200 (CYPE)"),
    Preference(8, "GammaS", 1.15, 1.15, "Gamma (Steel)", "1.15", "fyd = 500/1.15 = 434.78 MPa"),
    Preference(9, "GammaC", 1.5, 1.5, "Gamma (Concrete)", "1.5", "fcd = fck/1.5"),
    Preference(10, "AlphaCC", 1.0, 1.0, "AlphaCC", "1.0",
               "Spain alpha_cc = 1.0: fcd 33.33 (HA-50) / 23.33 MPa (HA-35) as CYPE"),
    Preference(11, "AlphaCT", 1.0, 1.0, "AlphaCT", "1.0", "Spain alpha_ct = 1.0"),
    Preference(12, "AlphaLCC", 0.85, 0.85, "AlphaLCC", "0.85", "lightweight concrete, unused"),
    Preference(13, "AlphaLCT", 0.85, 0.85, "AlphaLCT", "0.85", "lightweight concrete, unused"),
    Preference(14, "PatLLF", 0.75, 0.75, "Pattern Live Load Factor", "0.75", "auto combos only"),
    Preference(15, "UFLimit", 1.0, 1.0, "Utilization Factor Limit", "0.95",
               "ratio limit 1.0 as CE/CYPE (default 0.95 would flag ratios 0.95-1.0)"),
    Preference(16, "THDesign", 1, "Envelopes", "Multi-Response Case Design", "Envelopes",
               "linear static combinations only"),
    Preference(17, "RelClass", 2, "Class 2", "Reliability Class", "Class 2", "auto combos only"),
)
EC2_PREFS = {p.item: float(p.value) for p in PREFERENCES}
# field order of a real row of the EC2-family preference table (v20.1 NTC 2008 [G6]) + Country [G7]
PREF_FIELD_ORDER = ("THDesign", "NumCurves", "NumPoints", "MinEccen", "PatLLF", "UFLimit", "CombosEq",
                    "RelClass", "SOM", "Theta0", "GammaS", "GammaC", "AlphaCC", "AlphaCT", "AlphaLCC",
                    "AlphaLCT", "Country")


def preference_row() -> dict:
    """Record of ``PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004`` (spec C.9)."""
    by_field = {p.field: p.s2k for p in PREFERENCES}
    return {f: by_field[f] for f in PREF_FIELD_ORDER}


# ============================================================================================
# 2. rebar material and bar sizes  (spec A.4, A.5, C.2, C.4)
# ============================================================================================
@dataclass(frozen=True)
class RebarMaterial:
    name: str
    E: float                 # kN/m2
    unit_weight: float       # kN/m3
    alpha: float
    fy: float                # kN/m2 (fyk: SAP uses Fy as the characteristic yield strength)
    fu: float
    note: str
    expected: float = 1.1    # EffFy = 1.1 Fy, EffFu = 1.1 Fu (hinges/capacity only; not used by EC2 design)
    # SAP 03E defaults: simple parametric curve, kinematic hysteresis
    strain_hardening: float = 0.01
    strain_ultimate: float = 0.09
    final_slope: float = -0.1

    @property
    def unit_mass(self) -> float:
        return self.unit_weight / 9.80665


def _rebar_material() -> RebarMaterial:
    m = next(x for x in tm.MATERIALS if x.kind == "Rebar")
    return RebarMaterial(m.name, m.E, m.unit_weight, m.alpha, m.fy, m.fu, m.note)


REBAR = _rebar_material()
# SAP's default European bar list contains 6d, 8d, 10d, 12d, 14d, 16d, 20d, 25d, 26d, 28d [S29]; values of a
# kN-m model [G3].  Only 25d / 10d are referenced (pile check); beam design uses areas, not bar sizes.
BAR_SIZES = {"10d": (7.85e-05, 0.010), "20d": (3.14e-04, 0.020), "25d": (4.91e-04, 0.025)}


# ============================================================================================
# 3. sections: pile column data, beam rectangles + modifiers, beam rebar data  (A.6, C.3, C.5, C.6)
# ============================================================================================
PILE_SECTION = "PILOTE_40x40"
EDGE_SECTION = "VIGA_BORDE_25x30"
# composite General section -> (t3, t2) of the design rectangle (the web)
DESIGN_RECT = {"VIGA_T50x55_ALAS15x30": (0.55, 0.50),
               "VIGA_L80x55_ALA15x30": (0.55, 0.80),
               "VIGA_L80x55_ALA15x30_M": (0.55, 0.80)}
MOD_KEYS = ("AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod", "MMod", "WMod")   # = SetModifiers order
PROP_KEYS = ("Area", "AS2", "AS3", "TorsConst", "I22", "I33")


def sap_rect_props(t3: float, t2: float) -> dict:
    """Section properties SAP2000 computes for a solid rectangle (depth t3, width t2): A, shear
    areas 5/6 A, St Venant J with the 0.21 correction, I22 = t3 t2^3/12, I33 = t2 t3^3/12.
    Formula checked on the exported TorsConst/AS2 of 7 real rectangles (spec A.6, B.3)."""
    A = t3 * t2
    lo, hi = sorted((t3, t2))
    J = hi * lo**3 * (1.0 / 3.0 - 0.21 * (lo / hi) * (1.0 - lo**4 / (12.0 * hi**4)))
    return {"Area": A, "AS2": 5.0 / 6.0 * A, "AS3": 5.0 / 6.0 * A, "TorsConst": J,
            "I22": t3 * t2**3 / 12.0, "I33": t2 * t3**3 / 12.0}


def rect_modifiers(true: dict, got: dict, existing: dict | None = None) -> dict:
    """The 8 section modifiers making a rectangle with properties ``got`` behave like ``true``
    (A, As2, As3, J, I22, I33; mass and weight = area ratio because SAP computes them as a·m and
    a·w [S17 p.123]), multiplied by the ``existing`` section modifiers.  Object modifiers
    (e.g. the x100 of the rigid segments) multiply these in SAP [S17 p.124] and stay as they are."""
    existing = existing or {}
    ratio = {"AMod": true["Area"] / got["Area"], "A2Mod": true["AS2"] / got["AS2"],
             "A3Mod": true["AS3"] / got["AS3"], "JMod": true["TorsConst"] / got["TorsConst"],
             "I2Mod": true["I22"] / got["I22"], "I3Mod": true["I33"] / got["I33"]}
    ratio["MMod"] = ratio["WMod"] = ratio["AMod"]
    return {k: ratio[k] * float(existing.get(k, 1.0)) for k in MOD_KEYS}


@dataclass
class DesignRect:
    """Stand-in for ``sections.Section`` (``props`` + ``description``) of a SAP rectangle."""
    name: str
    t3: float
    t2: float
    description: str = ""
    props: dict = field(init=False)

    def __post_init__(self) -> None:
        self.props = {"t3": self.t3, "t2": self.t2, **sap_rect_props(self.t3, self.t2)}


@dataclass(frozen=True)
class ColumnRebar:
    """``PropFrame.SetRebarColumn`` arguments [S12] = ``FRAME SECTION PROPERTIES 02`` row (C.5)."""
    section: str
    mat_long: str
    mat_confine: str
    pattern: int              # 1 rectangular
    confine_type: int         # 1 ties
    cover: float              # clear cover to the ties [m]
    n_circ_bars: int          # circular only
    n_r3_bars: int            # bars per face parallel to local 3, corners included
    n_r2_bars: int            # bars per face parallel to local 2
    bar: str
    tie: str
    tie_spacing: float        # [m]
    n_2dir_ties: int          # tie legs per direction
    n_3dir_ties: int
    to_be_designed: bool      # False = check

    def oapi_args(self) -> tuple:
        return (self.section, self.mat_long, self.mat_confine, self.pattern, self.confine_type, self.cover,
                self.n_circ_bars, self.n_r3_bars, self.n_r2_bars, self.bar, self.tie, self.tie_spacing,
                self.n_2dir_ties, self.n_3dir_ties, self.to_be_designed)

    def s2k_row(self) -> dict:
        return {"SectionName": self.section, "RebarMatL": self.mat_long, "RebarMatC": self.mat_confine,
                "ReinfConfig": "Rectangular" if self.pattern == 1 else "Circular",
                "LatReinf": "Ties" if self.confine_type == 1 else "Spiral", "Cover": self.cover,
                "NumBars3Dir": self.n_r3_bars, "NumBars2Dir": self.n_r2_bars, "BarSizeL": self.bar,
                "BarSizeC": self.tie, "SpacingC": self.tie_spacing, "NumCBars2": self.n_2dir_ties,
                "NumCBars3": self.n_3dir_ties, "ReinfType": "Design" if self.to_be_designed else "Check"}

    @property
    def n_bars(self) -> int:
        return 2 * (self.n_r3_bars + self.n_r2_bars) - 4

    @property
    def bar_axis_distance(self) -> float:
        """Centroid-to-corner-bar distance [m] (CYPE +-127.5 mm)."""
        return 0.20 - self.cover - BAR_SIZES[self.tie][1] - BAR_SIZES[self.bar][1] / 2


# 12Ø25 = 4 per face incl. corners, ties '2eØ10+1eØ10' c/15 -> 4 full-depth legs per direction
# (diseno/python/codigo/armado_pilote.py TIES_FUSTE), clear cover 50 mm (XS3), CHECK mode.
PILE_REBAR = ColumnRebar(PILE_SECTION, REBAR.name, REBAR.name, 1, 1, 0.05, 0, 4, 4, "25d", "10d", 0.15,
                         4, 4, False)


@dataclass(frozen=True)
class BeamRebar:
    """``PropFrame.SetRebarBeam`` arguments [S12] = ``FRAME SECTION PROPERTIES 03`` row (C.6).
    Covers are face-to-centroid of the longitudinal bars.  The four areas are SAP's
    'reinforcement overwrites for ductile beams' (capacity shear of DCH/DCM frames, joints,
    default hinges [S19]); with Framing Type = DC Low they do not enter the design, so the
    provided CYPE areas are written there for information."""
    section: str
    cover_top: float          # m
    cover_bot: float
    as_top: float             # provided, m2 (information)
    as_bot: float
    asw_s: float              # provided links, m2/m (information)
    label: str
    src: str

    def oapi_args(self, info_areas: bool = True) -> tuple:
        t, b = (self.as_top, self.as_bot) if info_areas else (0.0, 0.0)
        return (self.section, REBAR.name, REBAR.name, self.cover_top, self.cover_bot, t, t, b, b)

    def s2k_row(self, info_areas: bool = True) -> dict:
        t, b = (self.as_top, self.as_bot) if info_areas else (0.0, 0.0)
        return {"SectionName": self.section, "RebarMatL": REBAR.name, "RebarMatC": REBAR.name,
                "TopCover": self.cover_top, "BotCover": self.cover_bot, "TopLeftArea": t,
                "TopRghtArea": t, "BotLeftArea": b, "BotRghtArea": b}


def _a(n: int, phi_mm: float) -> float:
    return n * math.pi * (phi_mm / 1000.0) ** 2 / 4.0


# covers to bar centroid: 50 mm + stirrup Ø10 + Ø20/2 = 70 mm; edge beams 50 + Ø8 + Ø16/2 = 66 mm
BEAM_REBAR = {
    "VIGA_T50x55_ALAS15x30": BeamRebar(
        "VIGA_T50x55_ALAS15x30", 0.07, 0.07, _a(5, 20), _a(7, 20), _a(3, 10) / 0.10,
        "sup. 5Ø20; inf. 5Ø20 alma + 2Ø20 alas; 3 ramas Ø10 c/10",
        "armado_vigas._inner (P381 table, drawings Pórtico 4)"),
    "VIGA_L80x55_ALA15x30": BeamRebar(
        "VIGA_L80x55_ALA15x30", 0.07, 0.07, _a(5, 20), _a(6, 20), _a(3, 10) / 0.10,
        "sup. 5Ø20; inf. 5Ø20 + 1Ø20 ala; 3 ramas Ø10 c/10",
        "armado_vigas._end (drawing Pórtico 3, listing 15.71 / 18.85)"),
    "VIGA_L80x55_ALA15x30_M": BeamRebar(
        "VIGA_L80x55_ALA15x30_M", 0.07, 0.07, _a(5, 20), _a(6, 20), _a(3, 10) / 0.10,
        "sup. 5Ø20; inf. 5Ø20 + 1Ø20 ala; 3 ramas Ø10 c/10",
        "armado_vigas._end (drawing Pórtico 9, listing 15.71 / 18.85)"),
    EDGE_SECTION: BeamRebar(
        EDGE_SECTION, 0.066, 0.066, _a(2, 16), _a(2, 16), _a(2, 8) / 0.15,
        "sup. 2Ø16; inf. 2Ø16; 1eØ8 c/15", "armado_vigas.provided_edge (drawings image203/211)"),
}


# ============================================================================================
# 4. which frames are designed, overwrites  (A.3, A.7, C.7, C.10)
# ============================================================================================
DESIGN_EDGE_BEAMS = True           # 25x30 edge beams also designed (our vigas.py checks them too)
L_PILE = tm.PILE_LENGTH                                   # 7.25 m joint to joint
L0_PILE = round(tm.PILE_LENGTH - tm.PILE_TOP_RIGID, 6)    # 6.70 m (CYPE l0, beta = 1)
PILE_LENGTH_RATIO = L0_PILE / L_PILE                      # 0.924138 x object length = 6.70 m
BETA_PILE = 1.0
FRAME_TYPE_DC_LOW = 3              # OAPI item 1 since v24.0: 1 DCH, 2 DCM, 3 DCL, 4 Secondary [S23 #7261]
# Kphi: SAP e2 = Kr·Kphi·eps_yd/(0.45 d)·l0²/c with c = 8 fixed and d = 327.5 mm (outer bar row);
# CE/CYPE use c = pi² and Kphi = 1 + beta·phi_ef = 1.373.  1.373·8/pi² reproduces CYPE's e2 = 92.1 mm
# (same d, spec B.4); the CE-strict e2 uses d = h/2 + is = 306.96 mm (A19.5.8.8.3(2)) -> 98.3 mm.
KPHI_CYPE = 1.373
_D_SAP, _D_IS = 327.5, 200.0 + math.sqrt((8 * 127.5**2 + 4 * 42.5**2) / 12)
KPHI_OPTIONS = {"ce": round(KPHI_CYPE * 8.0 / math.pi**2, 4),     # 1.1129 (default): e2 = CYPE (d 327.5)
                "ce_is": round(KPHI_CYPE * 8.0 / math.pi**2 * _D_SAP / _D_IS, 4),   # 1.1874: CE-strict e2
                "cype": KPHI_CYPE,                                # literal CYPE Kphi: SAP e2 x 1.234
                "sap": 0.0}                                       # program default (Kphi = 1)
KPHI_DEFAULT = "ce"
TAN_THETA = 1.0                    # theta = 45 deg (CYPE, CE cot theta = 1); SAP default optimises it


@dataclass(frozen=True)
class FrameDesign:
    frame: str
    kind: str                      # pile | beam_t | beam_edge
    member: str                    # P3 | VT2 | VBM
    section: str
    design: bool                   # concrete design ("From Material") or "No Design"
    design_type: str               # column | beam | -
    reason: str

    @property
    def procedure(self) -> int:
        """``FrameObj.SetDesignProcedure`` MyType: 1 from material, 2 no design [S15]."""
        return 1 if self.design else 2

    @property
    def s2k_procedure(self) -> str:
        return "From Material" if self.design else "No Design"


def frame_designs(model: dict) -> list[FrameDesign]:
    """Design classification of every frame of the model (spec A.7)."""
    out = []
    for f in model["frames"]:
        if f["kind"] == "pile":
            out.append(FrameDesign(f["name"], "pile", f["cype"], f["section"], True, "column",
                                   "pile 40x40 HA-50, 12Ø25 CHECK"))
        elif f["kind"] == "beam_t":
            rigid = bool(f.get("rigid"))
            out.append(FrameDesign(f["name"], "beam_t", f"VT{f['axis']}", f["section"], not rigid,
                                   "-" if rigid else "beam",
                                   "segment inside the pile width (x100 rigid)" if rigid else "transverse beam"))
        elif f["kind"] == "beam_edge":
            out.append(FrameDesign(f["name"], "beam_edge", "VBM" if f["portico"] == 1 else "VBT", f["section"],
                                   DESIGN_EDGE_BEAMS, "beam" if DESIGN_EDGE_BEAMS else "-", "edge beam 25x30"))
    return out


def overwrites(model: dict, kphi: str | float = KPHI_DEFAULT, tan_theta: float = TAN_THETA) -> list[dict]:
    """Per designed frame: OAPI ``SetOverwrite`` items [S3] (documented: 1 framing type, 3/4
    unbraced-length ratios, 5/6 beta) and the ``OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004``
    record (C.10, v20 field names), which also carries the table-only TanTheta and KPhi."""
    kp = KPHI_OPTIONS[kphi] if isinstance(kphi, str) else float(kphi)
    rows = []
    for fd in frame_designs(model):
        if not fd.design:
            continue
        if fd.design_type == "column":
            r = PILE_LENGTH_RATIO
            oapi = {1: float(FRAME_TYPE_DC_LOW), 3: r, 4: r, 5: BETA_PILE, 6: BETA_PILE}
            table = {"Frame": fd.frame, "DesignSect": "Program Determined", "FrameType": "DC Low", "RLLF": 0.0,
                     "XLMajor": r, "XLMinor": r, "BetaMajor": BETA_PILE, "BetaMinor": BETA_PILE,
                     "TanTheta": tan_theta, "Kr": 0.0, "KPhi": kp}
        else:
            oapi = {1: float(FRAME_TYPE_DC_LOW)}
            table = {"Frame": fd.frame, "DesignSect": "Program Determined", "FrameType": "DC Low", "RLLF": 0.0,
                     "XLMajor": 0.0, "XLMinor": 0.0, "TanTheta": tan_theta, "Kr": 0.0, "KPhi": 0.0}
        rows.append({"frame": fd.frame, "kind": fd.kind, "member": fd.member, "oapi": oapi, "table": table,
                     "table_only": {"TanTheta": table["TanTheta"], "KPhi": table["KPhi"]}})
    return rows


def design_groups(model: dict) -> dict[str, list[tuple[str, str]]]:
    """Selection groups for the GUI (Select > Groups): designed piles / beams / edge beams and the
    rigid 'No Design' segments."""
    g: dict[str, list[tuple[str, str]]] = {"DISENO_PILOTES": [], "DISENO_VIGAS_T": [],
                                           "DISENO_VIGAS_BORDE": [], "NO_DISENO_RIGIDOS": []}
    for fd in frame_designs(model):
        key = ("NO_DISENO_RIGIDOS" if not fd.design and fd.kind == "beam_t" else
               {"pile": "DISENO_PILOTES", "beam_t": "DISENO_VIGAS_T", "beam_edge": "DISENO_VIGAS_BORDE"}[fd.kind])
        if fd.kind == "beam_edge" and not fd.design:
            continue
        g[key].append(("Frame", fd.frame))
    return {k: v for k, v in g.items() if v}


# ============================================================================================
# 5. design combinations  (A.8, C.8) - bases of diseno/python/esfuerzos.py (D1)
# ============================================================================================
BASES = {
    "CYPE": {"family": "ELU", "factors": tm.COMBOS["ELU"],
             "title": "ELU rotura hormigon (Anejo 10: psi0,Qa = 0.7, bollard as wind 0.6)"},
    "ROM": {"family": "ELR", "factors": tm._family(1.35, 1.50, 1.0, 0.6),
            "title": "ELU rotura hormigon ROM 2.0-11 (psi0,Qa = 1.0)"},
}


def combos(base: str) -> dict[str, tuple]:
    b = BASES[base]
    return {f"{b['family']}{k:02d}": tuple(fac) for k, fac in enumerate(b["factors"], start=1)}


# Seismic variant (``--sismo`` of write_s2k_diseno.py / sap_oapi_diseno.py): the Rover seismic
# combinations SIS{X,Y,Z}[Q] = PP + CM [+ 0.8 Qa] + 1.0/0.3/0.3 (EQX, EQY, EQZ) of
# sap2000/model/trasmallo.py (Linear Add; SAP takes each RS case with + and -) are design
# combinations too.  SAP's "Eurocode 2-2004" has ONE gamma_c / gamma_s pair (preferences 8/9 =
# 1.5 / 1.15, persistent-transient) applied to every design combination, SIS* included; the
# Código Estructural checks of diseno/python use the accidental factors 1.3 / 1.0 (CE Anejo 19,
# Table 2.1N with the Spanish NA) for the seismic situation, so SAP's SIS* design is conservative
# (HA-50: fcd = 50/1.5 = 33.3 instead of 50/1.3 = 38.5 MPa; fyd = 434.8 instead of 500 MPa).
# The framing type is overwritten to DC Low (no EC8 capacity design; the Rover spectrum is
# elastic, q = 1) and SAP takes theta = 45 deg in combos with seismic load (manual
# CFD-EC-2-2004, beam shear design), equal to our TanTheta = 1 overwrite.
SEISMIC_COMBOS = tuple(tm.seismic_combos())            # SISXQ, SISX, SISYQ, SISY, SISZQ, SISZ
SEISMIC_GAMMA = {"SAP (persistent, all combos)": {"gamma_c": 1.5, "gamma_s": 1.15},
                 "Codigo Estructural accidental (diseno/python)": {"gamma_c": 1.3, "gamma_s": 1.0}}


def design_combo_names(base: str, seismic: bool = False) -> list[str]:
    return list(combos(base)) + (list(SEISMIC_COMBOS) if seismic else [])


# ============================================================================================
# 6. the design model (analysis-identical)
# ============================================================================================
@functools.lru_cache(maxsize=1)
def base_model() -> dict:
    """``trasmallo.build_model()`` (cached: the FD torsion constants take a few seconds)."""
    return tm.build_model()


def design_sections(sections: dict) -> dict:
    """Analysis sections with the composite beams replaced by the design rectangles + modifiers."""
    out = {}
    for name, fs in sections.items():
        if name not in DESIGN_RECT:
            out[name] = fs
            continue
        t3, t2 = DESIGN_RECT[name]
        br = BEAM_REBAR[name]
        desc = (f"Diseno: rectangulo {t2 * 100:.0f}x{t3 * 100:.0f} (alma); modificadores = seccion compuesta "
                f"{fs.section.description.split(':')[0]}; armado CYPE {br.label}").replace("Ø", "phi")
        rect = DesignRect(name, t3, t2, desc)
        mods = rect_modifiers(fs.section.props, rect.props, fs.modifiers)
        out[name] = tm.FrameSection(name, fs.material, rect, "Rectangular", modifiers=mods,
                                    note=f"design rectangle {t2:g}x{t3:g}; {fs.note}")
    return out


def design_model(model: dict | None = None, groups: bool = True) -> dict:
    """Shallow copy of the analysis model with the design sections (and, if ``groups``, the
    selection groups of :func:`design_groups`).  Geometry, loads and combinations are shared."""
    model = model or base_model()
    dm = dict(model)
    dm["sections"] = design_sections(model["sections"])
    if groups:
        dm["groups"] = {**model["groups"], **design_groups(model)}
    return dm


def effective_props(fs, frame_modifiers: dict | None = None) -> dict:
    """Stiffness/weight terms the analysis uses for a frame section: A, As2, As3, J, I22, I33,
    weight and mass per unit length factors, including section and object modifiers."""
    p = fs.section.props
    m = {k: float(fs.modifiers.get(k, 1.0)) * float((frame_modifiers or {}).get(k, 1.0)) for k in MOD_KEYS}
    out = {"Area": p["Area"] * m["AMod"], "AS2": p["AS2"] * m["A2Mod"], "AS3": p["AS3"] * m["A3Mod"],
           "TorsConst": p["TorsConst"] * m["JMod"], "I22": p["I22"] * m["I2Mod"], "I33": p["I33"] * m["I3Mod"],
           "weight_area": p["Area"] * m["WMod"], "mass_area": p["Area"] * m["MMod"]}
    return out


def provided_summary() -> dict:
    """Provided reinforcement per section (cm², cm²/m) for reports."""
    out = {PILE_SECTION: {"label": "12Ø25 (4 por cara), cercos 2eØ10+1eØ10 c/15 (4 ramas por dirección)",
                          "As_cm2": round(PILE_REBAR.n_bars * BAR_SIZES["25d"][0] * 1e4, 2),
                          "Asw_s_cm2_m": round(4 * BAR_SIZES["10d"][0] / 0.15 * 1e4, 2)}}
    for name, br in BEAM_REBAR.items():
        out[name] = {"label": br.label, "As_top_cm2": round(br.as_top * 1e4, 2),
                     "As_bot_cm2": round(br.as_bot * 1e4, 2), "Asw_s_cm2_m": round(br.asw_s * 1e4, 2)}
    return out


if __name__ == "__main__":
    dm = design_model()
    base = base_model()
    print(f"{DESIGN_CODE}: l0 ratio {PILE_LENGTH_RATIO:.6f} -> l0 = {PILE_LENGTH_RATIO * L_PILE:.3f} m, "
          f"Kphi {KPHI_OPTIONS}")
    for name in DESIGN_RECT:
        fs = dm["sections"][name]
        print(name, {k: round(v, 6) for k, v in fs.modifiers.items()})
        eff = effective_props(fs)
        comp = base["sections"][name].section.props
        print("   max rel diff vs composite:",
              max(abs(eff[k] / comp[k] - 1) for k in PROP_KEYS), abs(eff["weight_area"] / comp["Area"] - 1))
    fds = frame_designs(base)
    print({k: sum(1 for f in fds if f.kind == k and f.design) for k in ("pile", "beam_t", "beam_edge")},
          "designed;", sum(1 for f in fds if not f.design), "No Design")
    print({k: len(v) for k, v in design_groups(base).items()})
