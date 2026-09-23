"""Design checks of the 14 precast piles 40x40 HA-50 (12Ø25) of one 40 m module of the Muelle de
Trasmallo to the Código Estructural (CE 2021, Anejo 19 = EN 1992-1-1 with the Spanish values),
with the SAP2000 v27.1 forces (diseno/python/esfuerzos.py) and the fibre-section engine (seccion.py).

Checks, for every pile, every ULS combination of the basis and the three CYPE check points
('Cabeza' z = 6.70 = beam soffit and 'Pie' z = 0 with the Ø10-tie shaft section; 'Arranque' z = 0
with the Ø8-tie fixity section), plus a screening of the intermediate stations:

* N-Mx-My, first order (A19.6.1, minimum eccentricity A19.6.1(4)) and second order by nominal
  curvature (A19.5.8.8): λ, λlim (A19.5.8.3.1, B = √(1+2ω)), ei (A19.5.2), e2 = (1/r)·l0²/π²
  with Kr, Kφ (φef = 1.75 as CYPE, conservative), 1/r0 = εyd/(0.45·d).  Utilisation along the
  load ray (CYPE 'mismas excentricidades') and at constant N.
* Shear (A19.6.2): VRd,c with CYPE's C10 convention, VRd,max, VRd,s with the ties (information),
  biaxial η = √((VEd,x/VR)² + (VEd,y/VR)²).
* Detailing (A19.8.2, A19.9.5): bar and tie diameters, spacings, As,min and As,max (CE and AN).
* SLS (A19.7, CE Art. 27 Tabla 27.2, XS3 -> wmax = 0.1 mm, quasi-permanent): uncracked criterion
  σct ≤ fctm on the homogenised section (A19.7.1(2)), otherwise crack width A19.7.3.4 on the
  cracked biaxial section with axial force; stress limits under the characteristic combinations
  ELS01-08 (A19.7.2: σc ≤ 0.6 fck, σs ≤ 0.8 fyk).
* Required steel (same 12-bar layout, area scaled) and practical layouts; final-design verdict
  and proposal (orchestrator decision D5).

Two rule sets (decision D2): ``Mode.CYPE`` reproduces CYPECAD (conventions C5-C7, C10-C12, C15 of
diseno/python/investigacion/codigo_estructural_spec.md) and is used for the parity with Anejo 10;
``Mode.CODIGO`` is code-strict and gives the verdict:

    ============================  ===================================  ===================================
    item                          CYPE (parity)                        CODIGO (verdict)
    ============================  ===================================  ===================================
    section model                 99.5 % strain limits, εsu 10 ‰,      εcu2, no steel strain limit, net
                                  gross concrete (C1, C2)              concrete (A19.3.2.7(2)b, A19.6.1)
    minimum eccentricity          only if e0 < emin in both axes (C6)  in the direction considered
    imperfection ei               both axes, sign of ee (C5)           worst axis only (A19.5.8.9(1))
    d in 1/r0                     extreme bar row, h/2 + c (C7)        h/2 + is (A19 (5.35))
    VRd,max lever arm             CYPE z 249.16 / 251.34 (C12)         z = 0.9·d (A19.6.2.3(1))
    shear at 'Arranque'           VRd,max only (as CYPE)               VRd,c, VRd,max, VRd,s
    As,max                        fcd·Ac/fyd (AN, C15)                 0.04·Ac (A19.9.5.2(3))
    tie spacing                   scl,max                              0.6·scl,max near beam/fixity
    ============================  ===================================  ===================================

CYPE parity: with CYPE's own printed forces every value of the P3 detailed checks (Anejo 10 P218-P324)
is reproduced within validate_codigo.py's tolerance.  The summary 'Aprov.' of the listing (Apéndice
§4.2) is not the constant-N utilisation of spec C4 for all piles: it equals ≈1.014 x the exact ray η
(sd 0.002 over the 42 rows, compression and tension piles); the shear 'Aprov.' is reproduced within
±0.1 points (VRd,c at 'Cabeza'/'Pie', VRd,max only at 'Arranque').

Section forces: esfuerzos.py returns the pile forces in the axes of CYPE's §3.3 table (Mx pairs
with Qx, My with Qy).  The section checks use the axes of CYPE's check listings (§3.5/§4.2 and the
body): MEd,x (moment about x, eccentricity along y) = My(§3.3) and MEd,y = Mx(§3.3), same sign
(sap2000/ref/cype_reference.json 'conventions'); VEd,x = Qx, VEd,y = Qy.  Since the 12-bar
section is doubly symmetric the utilisations do not depend on the moment signs.

Units: kN, kN·m, mm, MPa at the interface; N, N·mm inside the section engine.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
DISENO = HERE.parent
for _p in (str(HERE), str(DISENO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import esfuerzos as E  # noqa: E402
from armado_pilote import PROVIDED, ZONE_LABEL, PileLayout, practical_layouts  # noqa: E402
from seccion import KN, KNM, Mode, RCSection, bar_area, crack_width  # noqa: E402

OUT_DIR = DISENO / "output"
REF_JSON = DISENO.parent / "ref" / "cype_design_reference.json"      # diseno/ref

PILES = ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P13", "P14", "P15", "P16", "P17", "P18")
SEA_PILES = ("P1", "P3", "P5", "P7", "P13", "P15", "P16")

# ---------------------------------------------------------------------------------------------
# parameters (CYPE inputs and CE values)
# ---------------------------------------------------------------------------------------------
L0 = 6700.0                  # mm, effective length: β = 1 on the free length 7.25 - 0.55 (CYPE l0 6.700)
L_ALPHA_H = 6.70             # m, real length in αh = 2/√l (A19.5.2(5))
PHI_EF = 1.75                # CYPE input (C9); A19.5.8.4 would give much less (ψ2 bollard = 0)
C_CURVATURE = math.pi ** 2   # A19.5.8.8.2(4), constant section
THETA_0 = 1 / 200            # A19.5.2(5)
N_BAL = 0.4                  # A19.5.8.8.3(3)
C_LAMBDA = 0.7               # A19.5.8.3.1, rm unknown / unbraced
FYWD = 0.8 * 500.0           # A19.6.2.3(3) NOTA: fywd = 0.8 fywk when ν1 = 0.6 (C13)
NU1 = 0.6                    # (6.10.a), fck ≤ 60
COT_RANGE = (0.5, 2.0)       # A19 (6.7), Spanish values
Z_VRDMAX_CYPE = {"fuste": 249.16, "arranque": 251.34}   # CYPE printed lever arms (C12, P237/P292)
W_MAX = 0.10                 # mm, XS3, RC, quasi-permanent (CE Art. 27 Tabla 27.2)
K1_SIGMA_C = 0.6             # A19.7.2(2), XS
K2_SIGMA_C = 0.45            # A19.7.2(3), linear creep
K3_SIGMA_S = 0.8             # A19.7.2(5)


@dataclass(frozen=True)
class Position:
    name: str
    z: float                 # m from the fixity
    zone: str                # 'fuste' (Ø10 ties) | 'arranque' (Ø8 tie)
    cype: str


POSITIONS = (
    Position("Cabeza", 6.70, "fuste", "Forjado 1 'Cabeza' (body '1. FORJADO 1')"),
    Position("Pie", 0.00, "fuste", "Forjado 1 'Pie'"),
    Position("Arranque", 0.00, "arranque", "Cimentación 'Arranque' (body '2. EMPOTRAMIENTO')"),
)


@dataclass(frozen=True)
class Rules:
    mode: Mode
    min_ecc: str             # 'cype' (C6) | 'direction' (A19.6.1(4))
    imperfection: str        # 'both' (C5) | 'worst' (A19.5.8.9(1))
    d_curvature: str         # 'extreme' (C7) | 'is' (A19 (5.35))
    z_vrdmax: str            # 'cype' (C12) | '0.9d'
    shear_arranque: str      # 'vrdmax' (CYPE) | 'full'
    as_max: str              # 'AN' (C15) | 'CE'
    tie_reduction: bool      # A19.9.5.3(4) 0.6·scl,max in the end zones


RULES = {
    Mode.CYPE: Rules(Mode.CYPE, "cype", "both", "extreme", "cype", "vrdmax", "AN", False),
    Mode.CODIGO: Rules(Mode.CODIGO, "direction", "worst", "is", "0.9d", "full", "CE", True),
}

CLAUSES = {
    "nm1": "A19.6.1 (+ A19.6.1(4) emin)",
    "nm2": "A19.5.2, A19.5.8.3.1, A19.5.8.8, A19.6.1",
    "vrdc": "A19.6.2.2(1) (6.2.a/b)",
    "vrdmax": "A19.6.2.3(3) (6.9)",
    "vrds": "A19.6.2.3(3) (6.8)",
    "v622": "A19.6.2.2(6)",
    "sls_ct": "A19.7.1(2)",
    "wk": "A19.7.3.4 (7.8)-(7.11); CE Art. 27 Tabla 27.2",
    "sig_c": "A19.7.2(2)",
    "sig_s": "A19.7.2(5)",
    "sig_c_qp": "A19.7.2(3)",
}


# =============================================================================================
# forces
# =============================================================================================
@dataclass
class PileForces:
    """Pattern forces of one pile in the section axes: vals[station, pattern, comp] with comp =
    (N, MEd,x, MEd,y, VEd,x, VEd,y) [kN, kN·m]."""
    pile: str
    z: np.ndarray
    vals: np.ndarray

    def station(self, z: float) -> int:
        return int(np.argmin(np.abs(self.z - z)))

    def combine(self, factors: tuple) -> np.ndarray:
        """(n_station, 5) for one combination."""
        return np.einsum("p,spk->sk", np.asarray(factors, float), self.vals)


def load_forces(stations: dict | None = None) -> dict[str, PileForces]:
    """Piles from esfuerzos.load_stations(), mapped to the section axes (see module doc)."""
    data = stations if stations is not None else E.load_stations()
    out = {}
    for pile, sts in data["piles"].items():
        z = np.array([s.pos for s in sts])
        vals = np.array([[[s.values[p]["N"], s.values[p]["My"], s.values[p]["Mx"],
                           s.values[p]["Qx"], s.values[p]["Qy"]] for p in E.PATTERNS] for s in sts])
        out[pile] = PileForces(pile, z, vals)
    return out


def basis_combos(basis: str) -> dict[str, tuple]:
    return E.uls(basis)


def char_combos() -> dict[str, tuple]:
    """Characteristic combinations ELS01-08 (all factors 1.0; conservative for both bases)."""
    return {k: v for k, v in E.combos(True, "CYPE").items() if k.startswith("ELS")}


# =============================================================================================
# section models: hull screening + exact solver (seccion.capacity_ray with the coarse grid cached)
# =============================================================================================
class ExactSolver:
    """Same algorithm and tolerances as ``RCSection.capacity_ray`` / ``capacity_constant_N``; the
    coarse (α, t) search grid (3° x 121 points on the 10 mm mesh) is computed once per section."""

    def __init__(self, sec: RCSection, coarse: float = 10.0):
        self.sec = sec
        L = max(np.ptp(sec.vx), np.ptp(sec.vy))
        self.sc = np.array([1.0, 1 / L, 1 / L])
        fine = sec._cell_now
        sec.set_mesh(coarse)
        self.alphas = np.radians(np.arange(0.0, 360.0, 3.0))
        self.ts = np.linspace(0.0, 3.0, 121)
        pts = np.array([[sec.ult(a, t) for t in self.ts] for a in self.alphas]) * self.sc
        sec.set_mesh(fine)
        nr = np.linalg.norm(pts, axis=-1, keepdims=True)
        self.dirs = np.where(nr > 0, pts / np.where(nr > 0, nr, 1.0), 1e3)

    def ray(self, S) -> dict:
        S = np.asarray(S, float)
        sc = self.sc
        shat = S * sc / np.linalg.norm(S * sc)
        err = np.linalg.norm(self.dirs - shat, axis=-1)
        ia, it = np.unravel_index(int(np.argmin(err)), err.shape)
        sec = self.sec

        def res(p):
            r = sec.ult(p[0], p[1]) * sc
            return r / np.linalg.norm(r) - shat
        sol = least_squares(res, [self.alphas[ia], self.ts[it]], bounds=([-10, 0], [20, 3]),
                            xtol=1e-13, ftol=1e-13)
        d = sec.ult(sol.x[0], sol.x[1], detail=True)
        R = np.array([d["N"], d["Mx"], d["My"]])
        d["eta"] = float(np.linalg.norm(S * sc) / np.linalg.norm(R * sc))
        d["alpha"], d["t"] = float(sol.x[0]), float(sol.x[1])
        d["residual"] = float(np.linalg.norm(res(sol.x)))
        return d

    def constant_N(self, S, ray: dict | None = None) -> tuple[float, np.ndarray]:
        """Utilisation at constant N and constant Mx:My ratio (CYPE summary definition, C4)."""
        S = np.asarray(S, float)
        r0 = ray if ray is not None else self.ray(S)
        ang = math.atan2(S[2], S[1])

        def res(p):
            R = self.sec.ult(p[0], p[1])
            da = (math.atan2(R[2], R[1]) - ang + math.pi) % (2 * math.pi) - math.pi
            return [(R[0] - S[0]) / 1e5, da]
        sol = least_squares(res, [r0["alpha"], r0["t"]], bounds=([-10, 0], [20, 3]), xtol=1e-13)
        R = self.sec.ult(*sol.x)
        return math.hypot(S[1], S[2]) / math.hypot(R[1], R[2]), R


class SectionModel:
    """Fibre section of a pile layout with lazy hull (screening) and exact solver."""

    def __init__(self, layout: PileLayout, mode: Mode, phi: float | None = None, cell: float = 2.0):
        self.layout, self.mode, self.phi = layout, mode, phi
        self.sec = layout.section(mode, cell, phi)
        self._exact: ExactSolver | None = None

    @property
    def As(self) -> float:
        return float(self.sec.ba.sum())

    @property
    def exact(self) -> ExactSolver:
        if self._exact is None:
            self._exact = ExactSolver(self.sec)
        return self._exact

    def eta_fast(self, S: np.ndarray, chunk: int = 400) -> np.ndarray:
        """Vectorised ``RCSection.eta_fast`` for S = (n, 3) in N, N·mm."""
        H, sc = self.sec.hull()
        A, b = H.equations[:, :3], H.equations[:, 3]
        S = np.atleast_2d(np.asarray(S, float))
        out = np.zeros(len(S))
        for i in range(0, len(S), chunk):
            s = S[i:i + chunk] * sc
            nrm = np.linalg.norm(s, axis=1)
            ok = nrm > 0
            d = np.zeros_like(s)
            d[ok] = s[ok] / nrm[ok, None]
            ad = d @ A.T
            with np.errstate(divide="ignore", invalid="ignore"):
                t = np.where(ad > 1e-15, -b / ad, np.inf)
            out[i:i + chunk] = np.where(ok, nrm / t.min(axis=1), 0.0)
        return out


_MODELS: dict = {}


def section_model(layout: PileLayout, mode: Mode, phi: float | None = None) -> SectionModel:
    key = (layout, mode, phi)
    if key not in _MODELS:
        _MODELS[key] = SectionModel(layout, mode, phi)
    return _MODELS[key]


def _SI(S_kn) -> np.ndarray:
    """(N kN, Mx kN·m, My kN·m) -> (N, N·mm, N·mm)."""
    S = np.asarray(S_kn, float)
    return S * np.array([KN, KNM, KNM])


# =============================================================================================
# slenderness and design eccentricities (A19.5.2, A19.5.8, A19.6.1(4))
# =============================================================================================
def slenderness(N: float, layout: PileLayout, rules: Rules, As: float | None = None) -> dict:
    """Second-order parameters for NEd = N [kN] (compression +).  ``As`` overrides the steel area
    (same bar positions)."""
    c, s = layout.concrete, layout.steel
    Ac = layout.Ac
    I = layout.b ** 4 / 12.0
    i = math.sqrt(I / Ac)
    lam = L0 / i
    As = layout.As if As is None else As
    omega = As * s.fyd / (Ac * c.fcd)
    n = N * KN / (Ac * c.fcd)
    A = 1.0 / (1.0 + 0.2 * PHI_EF)
    B = math.sqrt(1.0 + 2.0 * omega)
    lam_lim = 20.0 * A * B * C_LAMBDA / math.sqrt(n) if n > 0 else math.inf
    alpha_h = min(max(2.0 / math.sqrt(L_ALPHA_H), 2.0 / 3.0), 1.0)
    alpha_m = 1.0
    theta_i = THETA_0 * alpha_h * alpha_m
    ei = theta_i * L0 / 2.0
    d_ext = layout.b / 2 + layout.c
    d_is = layout.b / 2 + layout.i_s()
    d = d_ext if rules.d_curvature == "extreme" else d_is
    eps_yd = s.fyd / s.Es
    r0 = eps_yd / (0.45 * d)
    n_u = 1.0 + omega
    Kr = min((n_u - n) / (n_u - N_BAL), 1.0)
    beta = 0.35 + c.fck / 200.0 - lam / 150.0
    Kphi = max(1.0 + beta * PHI_EF, 1.0)
    rinv = Kr * Kphi * r0
    e2 = rinv * L0 ** 2 / C_CURVATURE
    d_alt = d_is if rules.d_curvature == "extreme" else d_ext
    e2_alt = Kr * Kphi * eps_yd / (0.45 * d_alt) * L0 ** 2 / C_CURVATURE
    return dict(i=i, lam=lam, lam_lim=lam_lim, second_order=lam > lam_lim, A=A, B=B, C=C_LAMBDA,
                omega=omega, n=n, alpha_h=alpha_h, alpha_m=alpha_m, theta_i=theta_i, ei=ei, d=d,
                d_extreme=d_ext, d_is=d_is, eps_yd=eps_yd, r0inv_per_m=r0 * 1e3, n_u=n_u, Kr=Kr,
                Kr_raw=(n_u - n) / (n_u - N_BAL), beta=beta, Kphi=Kphi, rinv_per_m=rinv * 1e3, e2=e2,
                e2_other_d=e2_alt)


def _sgn(v: float) -> float:
    return -1.0 if v < 0 else 1.0


def design_points(N: float, Mx: float, My: float, layout: PileLayout, rules: Rules,
                  As: float | None = None) -> dict:
    """First-order and second-order (instability) design points (N, MEd,x, MEd,y) [kN, kN·m].

    Compression: e0 = M/N per axis ('En el eje x' = bending about x, eccentricity along y).
    CYPE: ee = e0 unless both |e0| < emin (C6); second order adds ei and e2 in both axes with the
    sign of ee (C5) when λ > λlim.  CODIGO: emin in the direction considered; e2 in both axes
    (λ > λlim in both), ei only in one axis, both choices checked (A19.5.8.9(1)); with λ ≤ λlim the
    'second-order' point still carries the imperfection (A19.5.2(2))."""
    if N <= 1e-6:
        return dict(first=[(N, Mx, My)], second=[], sl=None, e0=None, tension=True, labels=["-"])
    emin = max(layout.b / 30.0, 20.0)
    e0x, e0y = Mx / N * 1e3, My / N * 1e3
    sx, sy = _sgn(e0x), _sgn(e0y)
    sl = slenderness(N, layout, rules, As)
    e2 = sl["e2"] if sl["second_order"] else 0.0
    ei = sl["ei"]
    if rules.min_ecc == "cype":
        if abs(e0x) < emin and abs(e0y) < emin:
            eex, eey = sx * emin, sy * emin
        else:
            eex, eey = e0x, e0y
        first = [(N, N * eex / 1e3, N * eey / 1e3)]
    else:
        eex, eey = e0x, e0y
        first = [(N, N * sx * max(abs(e0x), emin) / 1e3, My), (N, Mx, N * sy * max(abs(e0y), emin) / 1e3)]
    second, labels, etot = [], [], []
    if rules.imperfection == "both":
        if sl["second_order"]:
            tx, ty = sx * (abs(eex) + ei + e2), sy * (abs(eey) + ei + e2)
            second.append((N, N * tx / 1e3, N * ty / 1e3))
            labels.append("ei, e2 en x e y")
            etot.append((tx, ty))
    else:
        for k in (0, 1):
            tx = abs(e0x) + e2 + (ei if k == 0 else 0.0)
            ty = abs(e0y) + e2 + (ei if k == 1 else 0.0)
            if k == 0:
                tx = max(tx, emin)
            else:
                ty = max(ty, emin)
            second.append((N, N * sx * tx / 1e3, N * sy * ty / 1e3))
            labels.append("ei en eje x" if k == 0 else "ei en eje y")
            etot.append((sx * tx, sy * ty))
    return dict(first=first, second=second, sl=sl, e0=(e0x, e0y), ee=(eex, eey), emin=emin,
                e2_applied=e2, etot=etot, tension=False, labels=labels)


# =============================================================================================
# ULS N-Mx-My
# =============================================================================================
def _combo_desc(factors: tuple) -> str:
    return E.describe(factors).replace("TB1", "Tirobolardo").replace("TB2", "Tirobolardo 2") \
        .replace("TB3", "Tirobolardo 3")


def uls_nm(forces: dict[str, PileForces], combos: dict[str, tuple], layouts: dict, rules: Rules,
           exact: str = "governing", piles=PILES, screening: bool = True, As_override: dict | None = None,
           phi_override: dict | None = None) -> dict:
    """N-M checks at the three positions of every pile for all combinations.

    exact: 'governing' (exact ray + constant N for the governing combination of each check),
    'borderline' (exact only when the screened η is within 3 % of 1) or 'none'."""
    rows, screen_rows, per_pile = [], [], {}
    names = list(combos)
    for pile in piles:
        pf = forces[pile]
        C = np.array([pf.combine(combos[k]) for k in names])          # (n_combo, n_st, 5)
        per_pile[pile] = {}
        for pos in POSITIONS:
            lay = layouts[pos.zone]
            As_ov = None if As_override is None else As_override.get(pos.zone)
            phi_ov = None if phi_override is None else phi_override.get(pos.zone)
            model = section_model(lay, rules.mode, phi_ov)
            ist = pf.station(pos.z)
            pts1, pts2, tag1, tag2, dps = [], [], [], [], []
            for ic, k in enumerate(names):
                N, Mx, My = C[ic, ist, :3]
                dp = design_points(float(N), float(Mx), float(My), lay, rules, As_ov)
                dps.append(dp)
                for j, S in enumerate(dp["first"]):
                    pts1.append(S)
                    tag1.append((ic, j))
                for j, S in enumerate(dp["second"]):
                    pts2.append(S)
                    tag2.append((ic, j))
            res = {}
            for kind, pts, tags in (("nm1", pts1, tag1), ("nm2", pts2, tag2)):
                if not pts:
                    res[kind] = None
                    continue
                eta = model.eta_fast(_SI(pts))
                ig = int(np.argmax(eta))
                ic, j = tags[ig]
                S = np.array(pts[ig])
                r = dict(eta_fast=float(eta[ig]), combo=names[ic], S=S, dp=dps[ic], j=j,
                         n_points=len(pts))
                do_exact = exact == "governing" or (exact == "borderline" and abs(eta[ig] - 1) < 0.03)
                if do_exact:
                    cand = [i for i in np.argsort(-eta)[:4] if eta[i] > eta[ig] - 0.01]
                    best = None
                    for i in cand:
                        rr = model.exact.ray(_SI(pts[i]))
                        if best is None or rr["eta"] > best[1]["eta"]:
                            best = (i, rr)
                    i, rr = best
                    ic, j = tags[i]
                    S = np.array(pts[i])
                    etaN, RN = model.exact.constant_N(_SI(S), rr)
                    r.update(combo=names[ic], S=S, dp=dps[ic], j=j, eta=rr["eta"], eta_N=etaN,
                             R=np.array([rr["N"], rr["Mx"], rr["My"]]) / np.array([KN, KNM, KNM]),
                             exact=True, Cc=rr["Cc"] / KN, Cs=rr["Cs"] / KN, T=rr["T"] / KN,
                             eps_c_max=rr["eps_c_max"], eps_s_min=rr["eps_s_min"])
                else:
                    e = float(eta[ig])
                    r.update(eta=e, eta_N=None, R=S / e if e > 0 else S * np.inf, exact=False)
                res[kind] = r
            per_pile[pile][pos.name] = res
            for kind, r in res.items():
                if r is None:
                    rows.append(dict(pile=pile, position=pos.name, zone=pos.zone, check=kind,
                                     clause=CLAUSES[kind], combo="-", eta=None, ok=True,
                                     note="N.P.: tracción o λ ≤ λlim (efectos de 2º orden despreciables)"))
                    continue
                dp, S, R = r["dp"], r["S"], r["R"]
                row = dict(pile=pile, position=pos.name, zone=pos.zone, check=kind,
                           clause=CLAUSES[kind], combo=r["combo"], combo_desc=_combo_desc(combos[r["combo"]]),
                           N=S[0], MEd_x=S[1], MEd_y=S[2], NRd=R[0], MRd_x=R[1], MRd_y=R[2],
                           demand=float(np.hypot(S[1], S[2])), capacity=float(np.hypot(R[1], R[2])),
                           eta=r["eta"], eta_N=r["eta_N"], eta_fast=r["eta_fast"], exact=r["exact"],
                           ok=r["eta"] <= 1.0 + 1e-9)
                if not dp["tension"]:
                    sl = dp["sl"]
                    row.update(e0_x=dp["e0"][0], e0_y=dp["e0"][1], lam=sl["lam"], lam_lim=sl["lam_lim"],
                               second_order=sl["second_order"])
                    if kind == "nm2":
                        row.update(ei=sl["ei"], e2=dp["e2_applied"], d=sl["d"], Kr=sl["Kr"], Kphi=sl["Kphi"],
                                   e2_other_d=sl["e2_other_d"] if sl["second_order"] else 0.0,
                                   etot_x=dp["etot"][r["j"]][0], etot_y=dp["etot"][r["j"]][1],
                                   case=dp["labels"][r["j"]])
                if r.get("exact"):
                    row.update(Cc=r["Cc"], Cs=r["Cs"], T=r["T"])
                rows.append(row)
        if screening:
            lay = layouts["fuste"]
            model = section_model(lay, rules.mode)
            inner = [i for i, z in enumerate(pf.z) if 1e-6 < z < 6.70 - 1e-6]
            pts, tags = [], []
            for i in inner:
                for ic, k in enumerate(names):
                    N, Mx, My = C[ic, i, :3]
                    dp = design_points(float(N), float(Mx), float(My), lay, rules)
                    for S in dp["first"] + dp["second"]:
                        pts.append(S)
                        tags.append((i, ic))
            eta = model.eta_fast(_SI(pts))
            ig = int(np.argmax(eta))
            i, ic = tags[ig]
            ends = max((per_pile[pile][p.name][k]["eta"] for p in POSITIONS[:2] for k in ("nm1", "nm2")
                        if per_pile[pile][p.name][k] is not None), default=0.0)
            Mg = float(np.hypot(pts[ig][1], pts[ig][2]))
            screen_rows.append(dict(pile=pile, check="N,M estaciones intermedias (cribado)",
                                    clause=CLAUSES["nm2"], z=float(pf.z[i]), combo=names[ic],
                                    N=float(pts[ig][0]), demand=Mg,
                                    capacity=Mg / float(eta[ig]) if eta[ig] > 0 else None,
                                    eta=float(eta[ig]), eta_ends=ends, ok=float(eta[ig]) <= 1.0,
                                    ends_govern=float(eta[ig]) <= ends + 1e-9, n_points=len(pts)))
    return dict(rows=rows, screening=screen_rows, per_pile=per_pile)


# =============================================================================================
# shear (A19.6.2)
# =============================================================================================
def vrd_c(N: float, layout: PileLayout) -> dict:
    """A19.6.2.2(1) (6.2.a/b) with CYPE's C10 Asl/d [kN]; σcp = NEd/Ac ≤ 0.2 fcd (tension -)."""
    c = layout.concrete
    Asl, d = layout.shear_group()
    bw = layout.b
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    rho = min(Asl / (bw * d), 0.02)
    scp = min(N * KN / layout.Ac, 0.2 * c.fcd)
    vmin = 0.035 * k ** 1.5 * math.sqrt(c.fck)
    v1 = (0.18 / c.gamma_c * k * (100.0 * rho * c.fck) ** (1 / 3) + 0.15 * scp) * bw * d / KN
    v2 = (vmin + 0.15 * scp) * bw * d / KN
    return dict(V=max(v1, v2, 0.0), V1=v1, Vmin=v2, k=k, rho_l=rho, sigma_cp=scp, vmin=vmin, d=d,
                Asl=Asl, CRdc=0.18 / c.gamma_c)


def vrd_max(layout: PileLayout, z: float, cot: float = 1.0) -> float:
    """A19.6.2.3(3) (6.9), αcw = 1 (non-prestressed; CYPE C11 gives σcp < 0 -> 1) [kN]."""
    return layout.b * z * NU1 * layout.concrete.fcd * cot / (1.0 + cot ** 2) / KN


def vrd_s(layout: PileLayout, z: float, cot: float = 1.0) -> float | None:
    t = layout.ties
    if not t.spacing:
        return None
    return t.Asw / t.spacing * z * FYWD * cot / KN


def sigma_cp_cype(N: float, layout: PileLayout, direction: str) -> float:
    """CYPE's σcp for αcw: (NEd - A's·fyd)/Ac, A's = all bars (X) or one face row (Y) (C11)."""
    As_c = layout.As if direction == "x" else layout.n_face * bar_area(layout.phi)
    return (N * KN - As_c * layout.steel.fyd) / layout.Ac


def lever_arm(layout: PileLayout, zone: str, rules: Rules) -> float:
    return Z_VRDMAX_CYPE[zone] if rules.z_vrdmax == "cype" and layout == PROVIDED[zone] \
        else 0.9 * layout.shear_group()[1]


def shear_best_with_ties(layout: PileLayout, z: float) -> tuple[float | None, float]:
    """max over 0.5 ≤ cotθ ≤ 2 of min(VRd,s, VRd,max) [kN] and the cot θ used (A19 (6.7))."""
    if not layout.ties.spacing:
        return None, 1.0
    best = (0.0, 1.0)
    for cot in np.arange(COT_RANGE[0], COT_RANGE[1] + 1e-9, 0.01):
        v = min(vrd_s(layout, z, cot), vrd_max(layout, z, cot))
        if v > best[0]:
            best = (v, float(cot))
    return best


def uls_shear(forces: dict[str, PileForces], combos: dict[str, tuple], layouts: dict, rules: Rules,
              piles=PILES) -> dict:
    rows, per_pile = [], {}
    names = list(combos)
    for pile in piles:
        pf = forces[pile]
        C = np.array([pf.combine(combos[k]) for k in names])
        per_pile[pile] = {}
        for pos in POSITIONS:
            lay = layouts[pos.zone]
            ist = pf.station(pos.z)
            z = lever_arm(lay, pos.zone, rules)
            z_ce = 0.9 * lay.shear_group()[1]
            vmax45 = vrd_max(lay, z)
            vs45 = vrd_s(lay, z_ce)
            vbest, cot_best = shear_best_with_ties(lay, z_ce)
            d = lay.shear_group()[1]
            v622 = 0.5 * lay.b * d * 0.6 * (1 - lay.concrete.fck / 250.0) * lay.concrete.fcd / KN
            only_max = pos.name == "Arranque" and rules.shear_arranque == "vrdmax"
            best = {}
            for ic, k in enumerate(names):
                N, _, _, Vx, Vy = C[ic, ist]
                V = math.hypot(Vx, Vy)
                vc = vrd_c(float(N), lay)
                e = {"vrdmax": V / vmax45}
                if not only_max:
                    e["vrdc"] = V / vc["V"] if vc["V"] > 0 else math.inf
                    e["v622"] = V / v622
                    if vs45:
                        e["vrds"] = V / vs45
                        e["vrds_opt"] = V / vbest
                    ec = max(e["vrdc"], e["v622"])
                    ew = max(e.get("vrds_opt", math.inf), V / vmax45 if rules.mode == Mode.CYPE else 0.0)
                    e["verdict"] = max(min(ec, ew), e["vrdmax"]) if rules.mode == Mode.CODIGO \
                        else max(e["vrdc"], e["vrdmax"])
                else:
                    e["verdict"] = e["vrdmax"]
                for key, val in e.items():
                    if key not in best or val > best[key][0]:
                        best[key] = (val, k, float(N), float(Vx), float(Vy), vc)
            per_pile[pile][pos.name] = {k: v[0] for k, v in best.items()}
            spec = [("vrdmax", "VRd,max (bielas, θ = 45°)", vmax45, CLAUSES["vrdmax"]),
                    ("vrdc", "VRd,c (sin armadura de cortante, C10)", None, CLAUSES["vrdc"]),
                    ("v622", "VEd ≤ 0.5·bw·d·ν·fcd", v622, CLAUSES["v622"]),
                    ("vrds", "VRd,s cercos, cotθ = 1 (información)", vs45, CLAUSES["vrds"]),
                    ("vrds_opt", f"min(VRd,s, VRd,max) cercos, cotθ óptimo {cot_best:.2f}", vbest, CLAUSES["vrds"]),
                    ("verdict", "Cortante: veredicto", None, "A19.6.2.1")]
            for key, label, cap, clause in spec:
                if key not in best:
                    continue
                val, k, N, Vx, Vy, vc = best[key]
                V = math.hypot(Vx, Vy)
                if key == "vrdc":
                    cap = vc["V"]
                elif key == "verdict":
                    cap = V / val if val > 0 else math.inf
                row = dict(pile=pile, position=pos.name, zone=pos.zone, check=label, key=key,
                           clause=clause, combo=k, N=N, VEd_x=Vx, VEd_y=Vy, demand=V, capacity=cap,
                           eta=val, ok=val <= 1.0 + 1e-9 if key not in ("vrds", "vrds_opt") else True,
                           info=key in ("vrds", "vrds_opt"))
                if key in ("vrdmax", "vrds", "vrds_opt"):
                    row["z"] = z if key == "vrdmax" else z_ce
                if key == "vrdc":
                    row.update(k=vc["k"], rho_l=vc["rho_l"], sigma_cp=vc["sigma_cp"], vmin=vc["vmin"],
                               d=vc["d"], Asl=vc["Asl"], VRd_c_min=vc["Vmin"])
                rows.append(row)
    return dict(rows=rows, per_pile=per_pile)


# =============================================================================================
# detailing (A19.8.2, A19.9.5 + AN/UNE-EN 1992-1-1)
# =============================================================================================
def detailing(layouts: dict, rules: Rules, N_max: dict[str, float]) -> dict:
    """Rows per zone (geometry) and per pile (As,min depends on NEd,max)."""
    rows = []
    for zone, lay in layouts.items():
        c, s = lay.concrete, lay.steel
        smin = max(lay.phi, 20.0 + 5.0, 20.0)
        t = lay.ties
        scl = min(15 * lay.phi, 300.0, lay.b)
        scl_red = 0.6 * scl if rules.tie_reduction else scl
        As_max_ce, As_max_an = 0.04 * lay.Ac, c.fcd * lay.Ac / s.fyd
        As_max = As_max_ce if rules.as_max == "CE" else As_max_an

        def add(check, clause, demand, capacity, kind, note="", info=False):
            eta = capacity / demand if kind == ">=" else demand / capacity
            rows.append(dict(zone=zone, pile="todos", check=check, clause=clause, demand=demand,
                             capacity=capacity, eta=eta, ok=info or eta <= 1.0 + 1e-9, combo="-", note=note,
                             info=info))
        add("h ≤ 4·b (pilar)", "A19.9.5.1", lay.b, 4 * lay.b, "<=")
        add("Ø longitudinal ≥ 12 mm", "A19.9.5.2(1)", lay.phi, 12.0, ">=")
        add("distancia libre entre barras ≥ max(Ø, dg+5, 20)", "A19.8.2(2)", lay.clear_spacing, smin, ">=",
            "CYPE: s2 = 1.25·dg = 25 (C16)")
        add("Øt ≥ max(6, Ømax/4)", "A19.9.5.3(1)", t.phi, max(6.0, lay.phi / 4), ">=")
        if t.spacing:
            add("st ≤ scl,max = min(15Ømin, 300, b)", "A19.9.5.3(3)", t.spacing, scl, "<=")
            if rules.tie_reduction:
                add("st ≤ 0.6·scl,max junto a viga/empotramiento (l = 400 mm)", "A19.9.5.3(4)", t.spacing,
                    scl_red, "<=", "precast pile without laps: reduction only in the end zones")
            add("distancia libre entre cercos ≥ smin", "A19.8.2(2)", t.spacing - t.phi, max(t.phi, 25.0, 20.0), ">=")
        add("barras sujetas por cercos (≤ 150 mm de una barra sujeta)", "A19.9.5.3(6)", 0.0, 150.0, "<=",
            "every bar is at a tie corner or cross-tie (CYPE sketch P220)")
        add(f"As ≤ As,max ({'0.04·Ac' if rules.as_max == 'CE' else 'fcd·Ac/fyd (AN)'}) [cm2]",
            "A19.9.5.2(3)" if rules.as_max == "CE" else "AN/UNE-EN 1992-1-1 9.5.2(3)", lay.As / 100,
            As_max / 100, "<=",
            "other limit in the next row")
        other = ("fcd·Ac/fyd (AN, CYPE)", "AN/UNE-EN 1992-1-1 9.5.2(3)", As_max_an) if rules.as_max == "CE" \
            else ("0.04·Ac (CE)", "A19.9.5.2(3)", As_max_ce)
        add(f"As ≤ {other[0]} [cm2] (information)", other[1], lay.As / 100, other[2] / 100, "<=",
            "D2: the verdict uses the other limit", info=True)
        add("As ≥ 0.004·Ac (AN, CYPE) [cm2]", "AN/UNE-EN 1992-1-1 9.5.2(2)", lay.As / 100, 0.004 * lay.Ac / 100,
            ">=",
            "not in the CE A19 text (C15)" + ("; information only" if rules.as_max == "CE" else ""),
            info=rules.as_max == "CE")
    lay = layouts["fuste"]
    for pile, N in N_max.items():
        need = 0.10 * max(N, 0.0) * KN / lay.steel.fyd
        per_face = 0.05 * max(N, 0.0) * KN / min(lay.steel.fyd, 400.0)
        rows.append(dict(zone="fuste", pile=pile, check="As ≥ 0.10·NEd/fyd [cm2]", clause="A19.9.5.2(2) (9.12)",
                         demand=lay.As / 100, capacity=need / 100, eta=need / lay.As, ok=need <= lay.As,
                         combo="NEd,max",
                         note=f"NEd,max = {N:.1f} kN; por cara 0.05·NEd/fyc,d = {per_face / 100:.2f} cm2"))
        face = lay.n_face * bar_area(lay.phi)
        rows.append(dict(zone="fuste", pile=pile, check="A's por cara ≥ 0.05·NEd/fyc,d (fyc,d ≤ 400) [cm2]",
                         clause="A19.9.5.2(2)", demand=face / 100, capacity=per_face / 100, eta=per_face / face,
                         ok=per_face <= face, combo="NEd,max", note=""))
    return dict(rows=rows)


# =============================================================================================
# SLS: linear-elastic biaxial section with axial force (uncracked / no concrete tension)
# =============================================================================================
class ElasticSection:
    """Linear-elastic pile section, strain ε = e0 + kx·x + ky·y (seccion convention, compression
    +).  Uncracked: homogenised (bars (Es - Ec)·As).  Cracked: no concrete tension, solved by
    fixed-point iteration on the compressed-fibre mask (converges in a few steps)."""

    def __init__(self, layout: PileLayout, cell: float = 4.0, Ec: float | None = None):
        self.layout = layout
        self.Ec, self.Es = (layout.concrete.Ecm if Ec is None else Ec), layout.steel.Es
        h = layout.b / 2
        n = int(round(layout.b / cell))
        dx = layout.b / n
        xs = -h + (np.arange(n) + 0.5) * dx
        X, Y = np.meshgrid(xs, xs)
        self.fx, self.fy = X.ravel(), Y.ravel()
        self.fa = np.full(self.fx.size, dx * dx)
        self.vx, self.vy = np.array([-h, h, h, -h]), np.array([-h, -h, h, h])
        xy = np.array(layout.coords())
        self.bx, self.by = xy[:, 0], xy[:, 1]
        self.ba = np.full(len(xy), bar_area(layout.phi))

    @staticmethod
    def _K(w, x, y):
        return np.array([[w.sum(), (w * x).sum(), (w * y).sum()],
                         [(w * y).sum(), (w * x * y).sum(), (w * y * y).sum()],
                         [(w * x).sum(), (w * x * x).sum(), (w * x * y).sum()]])

    def _solve(self, conc_on, bar_conc, F):
        wc = self.Ec * self.fa * conc_on
        wb = (self.Es - self.Ec * bar_conc) * self.ba
        K = self._K(wc, self.fx, self.fy) + self._K(wb, self.bx, self.by)
        return np.linalg.solve(K, F)

    def solve(self, N: float, Mx: float, My: float, cracked: bool = True) -> dict:
        """N [kN], Mx, My [kN·m] -> stresses [MPa] (compression +)."""
        F = np.array([N * KN, Mx * KNM, My * KNM])
        on = np.ones(self.fx.size)
        p = self._solve(on, np.ones(self.bx.size), F)
        it = 0
        if cracked:
            for it in range(1, 200):
                ef = p[0] + p[1] * self.fx + p[2] * self.fy
                eb = p[0] + p[1] * self.bx + p[2] * self.by
                on_new, bc_new = (ef > 0).astype(float), (eb > 0).astype(float)
                if it > 1 and np.array_equal(on_new, on):
                    break
                on = on_new
                p = self._solve(on, bc_new, F)
        e0, kx, ky = p
        ev = e0 + kx * self.vx + ky * self.vy
        eb = e0 + kx * self.bx + ky * self.by
        sig_v = self.Ec * (np.maximum(ev, 0.0) if cracked else ev)
        ef = e0 + kx * self.fx + ky * self.fy
        sc = self.Ec * (np.maximum(ef, 0.0) if cracked else ef) * self.fa
        sb = (self.Es * eb - self.Ec * (np.maximum(eb, 0.0) if cracked else eb)) * self.ba
        R = np.array([sc.sum() + sb.sum(), (sc * self.fy).sum() + (sb * self.by).sum(),
                      (sc * self.fx).sum() + (sb * self.bx).sum()])
        residual = float(np.linalg.norm((R - F) / np.array([KN, KNM, KNM])))
        return dict(plane=(float(e0), float(kx), float(ky)), eps_v=ev, sig_v=sig_v, eps_b=eb,
                    sig_b=self.Es * eb, sig_c_max=float(sig_v.max()), sig_ct=float(-(self.Ec * ev).min()),
                    sig_s_t=float(max(-self.Es * eb.min(), 0.0)), sig_s_c=float(self.Es * eb.max()),
                    iterations=it, cracked_model=cracked, residual=residual)

    def gross_sigma_ct(self, N: float, Mx: float, My: float) -> float:
        b = self.layout.b
        W = b ** 3 / 6.0
        return -(N * KN / (b * b) - abs(Mx) * KNM / W - abs(My) * KNM / W)

    def crack(self, st: dict) -> dict:
        """A19.7.3.4 on the cracked state ``st``; depths measured perpendicular to the neutral
        axis (reduces to the usual uniaxial rule for the piles, whose bending is nearly uniaxial)."""
        lay = self.layout
        e0, kx, ky = st["plane"]
        g = math.hypot(kx, ky)
        ux, uy = kx / g, ky / g
        s_v = self.vx * ux + self.vy * uy
        s_top, s_bot = float(s_v.max()), float(s_v.min())
        h = s_top - s_bot
        s_na = -e0 / g
        x = min(max(s_top - s_na, 0.0), h)
        s_b = self.bx * ux + self.by * uy
        ib = int(np.argmin(st["eps_b"]))
        d = s_top - float(s_b[ib])
        full_tension = x <= 0.0
        hcef = min(2.5 * (h - d), h / 2) if full_tension else min(2.5 * (h - d), (h - x) / 3, h / 2)
        s_f = self.fx * ux + self.fy * uy
        in_eff = s_f <= s_bot + hcef
        bars_in = s_b <= s_bot + hcef
        As = float(self.ba[bars_in].sum())
        Ac_eff = float(self.fa[in_eff].sum())         # gross b·hc,ef (A19 Fig. 7.1, spec §5.5)
        if full_tension:
            e1, e2 = -float(st["eps_v"].min()), -float(st["eps_v"].max())
            k2 = (e1 + e2) / (2 * e1)
        else:
            k2 = 0.5
        sig_s = st["sig_s_t"]
        if As <= 0.0:
            # shallow tension zone, (h - x)/3 < h - d: no bonded bar inside Ac,eff -> (7.14), and the
            # tension-stiffening term of (7.9) vanishes (0.6·σs/Es floor)
            d_eps = 0.6 * sig_s / lay.steel.Es
            sr = 1.3 * (h - x)
            cw = dict(wk=sr * d_eps, sr_max=sr, d_eps=d_eps, rho_p_eff=0.0, rule="(7.14)")
        else:
            cw = crack_width(sig_s, lay.concrete, lay.steel, As, Ac_eff, lay.c_clear, lay.phi, kt=0.4,
                             k1=0.8, k2=k2, spacing=lay.step, h=h, x=x)
        return dict(wk=cw["wk"], sr_max=cw["sr_max"], d_eps=cw["d_eps"], rho_p_eff=cw["rho_p_eff"],
                    sig_s=sig_s, x=x, h=h, d=d, hc_ef=hcef, As_eff=As, Ac_eff=Ac_eff, k2=k2, rule=cw["rule"],
                    c=lay.c_clear)


_ELASTIC: dict = {}


def elastic(layout: PileLayout) -> ElasticSection:
    if layout not in _ELASTIC:
        _ELASTIC[layout] = ElasticSection(layout)
    return _ELASTIC[layout]


def sls_cases(basis: str) -> list[tuple[str, float, float, bool]]:
    """(label, ψ2 Qa, ψ2 bollard, primary) - primary: the basis ψ2,Qa with the bollard ψ2 = 0."""
    psi_basis = E.BASES[basis]["psi2_Qa"]
    out = []
    for q in (E.PSI2_QA_CYPE, E.PSI2_QA_STORAGE):
        for tb in (0.0, 0.5):
            out.append((f"QP ψ2,Qa={q:g}, ψ2,TB={tb:g}", q, tb, q == psi_basis and tb == 0.0))
    return out


def sls(forces: dict[str, PileForces], layouts: dict, basis: str, piles=PILES) -> dict:
    """Quasi-permanent crack control and characteristic stress limits at the three positions."""
    qp_rows, ch_rows, per_pile = [], [], {}
    chars = char_combos()
    for pile in piles:
        pf = forces[pile]
        per_pile[pile] = {}
        for pos in POSITIONS:
            lay = layouts[pos.zone]
            es = elastic(lay)
            fctm, fck, fyk = lay.concrete.fctm, lay.concrete.fck, lay.steel.fyk
            ist = pf.station(pos.z)
            res = {}
            for label, q, tb, primary in sls_cases(basis):
                worst = None
                for name, fac in E.quasi_permanent(q, tb).items():
                    N, Mx, My = pf.combine(fac)[ist, :3]
                    un = es.solve(N, Mx, My, cracked=False)
                    r = dict(combo=name, N=float(N), Mx=float(Mx), My=float(My), sig_ct=un["sig_ct"],
                             sig_ct_gross=es.gross_sigma_ct(N, Mx, My), cracked=un["sig_ct"] > fctm)
                    if r["cracked"]:
                        cr = es.solve(N, Mx, My, cracked=True)
                        w = es.crack(cr)
                        r.update(wk=w["wk"], sig_s=w["sig_s"], x=w["x"], hc_ef=w["hc_ef"], rho_p_eff=w["rho_p_eff"],
                                 sr_max=w["sr_max"], d_eps=w["d_eps"], k2=w["k2"], sig_c=cr["sig_c_max"],
                                 eta=w["wk"] / W_MAX)
                    else:
                        r.update(wk=0.0, sig_c=un["sig_c_max"], eta=un["sig_ct"] / fctm)
                    r["ok"] = (not r["cracked"]) or r["wk"] <= W_MAX
                    r["eta_c_qp"] = r["sig_c"] / (K2_SIGMA_C * fck)
                    key = (r["cracked"], r["eta"])
                    if worst is None or key > (worst["cracked"], worst["eta"]):
                        worst = r
                res[label] = worst
                qp_rows.append(dict(pile=pile, position=pos.name, zone=pos.zone, case=label, primary=primary,
                                    check="Fisuración XS3: σct ≤ fctm o wk ≤ 0.1 mm", clause=CLAUSES["wk"],
                                    demand=worst["wk"] if worst["cracked"] else worst["sig_ct"],
                                    capacity=W_MAX if worst["cracked"] else fctm, fctm=fctm, **worst))
            worst_c = worst_s = worst_ce = None
            _, qp_fac = next(iter(E.quasi_permanent(E.BASES[basis]["psi2_Qa"], 0.0).items()))
            Mqp = float(np.hypot(*pf.combine(qp_fac)[ist, 1:3]))
            for name, fac in chars.items():
                N, Mx, My = pf.combine(fac)[ist, :3]
                un = es.solve(N, Mx, My, cracked=False)
                st = es.solve(N, Mx, My, cracked=True) if un["sig_ct"] > fctm else un
                sc, ss = st["sig_c_max"], max(-float(st["sig_b"].min()), 0.0)
                if worst_c is None or sc > worst_c[0]:
                    worst_c = (sc, name, N, Mx, My)
                if worst_s is None or ss > worst_s[0]:
                    worst_s = (ss, name, N, Mx, My)
                # information: sustained share with Ec,eff = Ecm/(1 + φ·Mqp/Mk) (effective-modulus reading
                # of A19.5.8.4 / 7.4.3(5)); the verdict keeps the short-term Ecm (conservative)
                ratio = min(Mqp / max(float(np.hypot(Mx, My)), 1e-9), 1.0)
                ee = ElasticSection(lay, Ec=lay.concrete.Ecm / (1.0 + PHI_EF * ratio))
                ue = ee.solve(N, Mx, My, cracked=False)
                sce = (ee.solve(N, Mx, My, cracked=True) if ue["sig_ct"] > fctm else ue)["sig_c_max"]
                if worst_ce is None or sce > worst_ce[0]:
                    worst_ce = (sce, name, ee.Ec)
            for (val, name, N, Mx, My), check, clause, lim in (
                    (worst_c, "σc ≤ 0.6·fck (característica, XS)", CLAUSES["sig_c"], K1_SIGMA_C * fck),
                    (worst_s, "σs ≤ 0.8·fyk (característica)", CLAUSES["sig_s"], K3_SIGMA_S * fyk)):
                row = dict(pile=pile, position=pos.name, zone=pos.zone, check=check, clause=clause,
                           combo=name, N=float(N), Mx=float(Mx), My=float(My), demand=val, capacity=lim,
                           eta=val / lim, ok=val <= lim)
                if check.startswith("σc"):
                    row.update(sig_c_Ec_eff=worst_ce[0], eta_Ec_eff=worst_ce[0] / lim, Ec_eff=worst_ce[2],
                               combo_Ec_eff=worst_ce[1])
                ch_rows.append(row)
            res["char_c"], res["char_s"] = worst_c[0] / (K1_SIGMA_C * fck), worst_s[0] / (K3_SIGMA_S * fyk)
            res["char_c_Ec_eff"] = worst_ce[0] / (K1_SIGMA_C * fck)
            per_pile[pile][pos.name] = res
    return dict(qp=qp_rows, char=ch_rows, per_pile=per_pile)


# =============================================================================================
# complete check of a layout
# =============================================================================================
def check_piles(forces: dict[str, PileForces], basis: str, mode: Mode, layouts: dict | None = None,
                exact: str = "governing", with_sls: bool = True, screening: bool = True,
                piles=PILES) -> dict:
    layouts = layouts or PROVIDED
    rules = RULES[mode]
    combos = basis_combos(basis)
    nm = uls_nm(forces, combos, layouts, rules, exact=exact, piles=piles, screening=screening)
    sh = uls_shear(forces, combos, layouts, rules, piles=piles)
    N_max = {}
    for pile in piles:
        pf = forces[pile]
        N_max[pile] = max(float(pf.combine(f)[:, 0].max()) for f in combos.values())
    det = detailing(layouts, rules, N_max)
    sl = sls(forces, layouts, basis, piles=piles) if with_sls else None
    summary = {}
    det_zone = [r for r in det["rows"] if r["pile"] == "todos"]
    for pile in piles:
        s = {}
        pp = nm["per_pile"][pile]
        for kind in ("nm1", "nm2"):
            vals = [(pp[p][kind]["eta"], p) for p in pp if pp[p][kind] is not None]
            s[kind] = max(vals)[0] if vals else None
            s[kind + "_at"] = max(vals)[1] if vals else None
        scr = [r for r in nm["screening"] if r["pile"] == pile]
        s["nm_stations"] = scr[0]["eta"] if scr else None
        shp = sh["per_pile"][pile]
        s["shear_vrdc"] = max((v.get("vrdc", 0.0) for v in shp.values()), default=0.0)
        s["shear_vrdmax"] = max(v["vrdmax"] for v in shp.values())
        s["shear"] = max(v["verdict"] for v in shp.values())
        dr = det_zone + [r for r in det["rows"] if r["pile"] == pile]
        s["detailing"] = max(r["eta"] for r in dr if not r.get("info"))
        s["detailing_ok"] = all(r["ok"] for r in dr)
        if sl is not None:
            sp = sl["per_pile"][pile]
            for label, q, tb, primary in sls_cases(basis):
                worst = max((sp[p][label] for p in sp), key=lambda r: (r["cracked"], r["eta"]))
                key = "sls_crack" if primary else f"sls_crack[{label}]"
                s[key] = worst["eta"]
                s[key + "_cracked"] = worst["cracked"]
                s[key + "_ok"] = worst["ok"]
            s["sls_sigma_c_qp"] = max(sp[p][lab]["eta_c_qp"] for p in sp for lab, *_ in sls_cases(basis))
            s["sls_sigma_c"] = max(sp[p]["char_c"] for p in sp)
            s["sls_sigma_c_Ec_eff"] = max(sp[p]["char_c_Ec_eff"] for p in sp)       # information only
            s["sls_sigma_s"] = max(sp[p]["char_s"] for p in sp)
        uls_ok = all(v is None or v <= 1.0 + 1e-9 for v in (s["nm1"], s["nm2"], s["nm_stations"], s["shear"]))
        sls_ok = sl is None or (s["sls_crack_ok"] and s["sls_sigma_c"] <= 1 and s["sls_sigma_s"] <= 1)
        s["verdict"] = "CUMPLE" if uls_ok and s["detailing_ok"] and sls_ok else "NO CUMPLE"
        sens = [k for k in s if k.startswith("sls_crack[") and k.endswith("_ok")]
        s["verdict_sensitivity"] = {k[10:-4]: ("CUMPLE" if s[k] else "NO CUMPLE") for k in sens}
        summary[pile] = s
    return dict(basis=basis, mode=mode.value, nm=nm, shear=sh, detailing=det, sls=sl, summary=summary,
                N_max=N_max, layouts={z: l.label for z, l in layouts.items()})


# =============================================================================================
# required steel and practical layouts
# =============================================================================================
PHI_GRID = (12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 36.0)


def max_eta_nm(forces: dict[str, PileForces], combos: dict, layout: PileLayout, zone_positions,
               rules: Rules, pile: str, phi: float | None = None) -> tuple[float, str, str, tuple]:
    """Max screened η (first and second order) of one pile over the given positions."""
    model = section_model(layout, rules.mode, phi)
    As = model.As
    pf = forces[pile]
    pts, tags = [], []
    for pos in zone_positions:
        ist = pf.station(pos.z)
        for k, fac in combos.items():
            N, Mx, My = pf.combine(fac)[ist, :3]
            dp = design_points(float(N), float(Mx), float(My), layout, rules, As)
            for S in dp["first"] + dp["second"]:
                pts.append(S)
                tags.append((pos.name, k))
    eta = model.eta_fast(_SI(pts))
    i = int(np.argmax(eta))
    return float(eta[i]), tags[i][0], tags[i][1], tuple(pts[i])


def required_steel(forces: dict[str, PileForces], basis: str, mode: Mode, layouts: dict | None = None,
                   piles=PILES) -> list[dict]:
    """Minimum total As of the provided 12-bar layout (bar positions kept, area scaled) with
    η ≤ 1 over all ULS combinations (first and second order), per pile and zone."""
    layouts = layouts or PROVIDED
    rules = RULES[mode]
    combos = basis_combos(basis)
    rows = []
    for pile in piles:
        for zone, lay in layouts.items():
            poss = [p for p in POSITIONS if p.zone == zone]
            etas = [max_eta_nm(forces, combos, lay, poss, rules, pile, phi)[0] for phi in PHI_GRID]
            As_grid = [lay.n_bars * bar_area(p) for p in PHI_GRID]
            As_req = None
            if etas[0] <= 1.0:
                As_req = As_grid[0] * etas[0]            # below the grid: proportional estimate
                note = f"η ≤ 1 already with {lay.n_bars}Ø{PHI_GRID[0]:g}"
            elif etas[-1] > 1.0:
                note = f"η > 1 even with {lay.n_bars}Ø{PHI_GRID[-1]:g}"
            else:
                for (a0, e0), (a1, e1) in zip(zip(As_grid, etas), zip(As_grid[1:], etas[1:])):
                    if e0 > 1.0 >= e1:
                        As_req = a0 + (e0 - 1.0) / (e0 - e1) * (a1 - a0)
                        break
                note = "interpolated on the Ø grid (hull screening)"
            eta_prov, pos_g, combo_g, S_g = max_eta_nm(forces, combos, lay, poss, rules, pile)
            eta_chk = None
            rows.append(dict(pile=pile, zone=zone, check="As necesaria (N-M, 1er y 2º orden)",
                             clause=CLAUSES["nm2"], combo=combo_g, position=pos_g,
                             As_req_cm2=None if As_req is None else As_req / 100, As_prov_cm2=lay.As / 100,
                             ratio=None if As_req is None else As_req / lay.As, eta_prov=eta_prov,
                             eta_at_As_req=eta_chk, demand=None if As_req is None else As_req / 100,
                             capacity=lay.As / 100, eta=None if As_req is None else As_req / lay.As,
                             ok=As_req is not None and As_req <= lay.As, note=note))
    opts = sorted(practical_layouts(), key=lambda c: c["fuste"].weight_per_m()["total"])
    for r in rows:                                # lightest practical layout with η(N,M) ≤ 1 for the pile
        poss = [p for p in POSITIONS if p.zone == r["zone"]]
        for cand in opts:
            lay = cand[r["zone"]]
            if r["As_req_cm2"] is not None and lay.As / 100 < 0.9 * r["As_req_cm2"]:
                continue
            e = max_eta_nm(forces, combos, lay, poss, rules, r["pile"])[0]
            if e <= 1.0:
                r.update(practical=f"{lay.label} {cand['fuste'].ties.label}", practical_As_cm2=lay.As / 100,
                         practical_eta=e)
                break
    for zone, lay in layouts.items():             # confirm the interpolation for the governing pile
        zr = [r for r in rows if r["zone"] == zone and r["As_req_cm2"] is not None]
        if not zr:
            continue
        g = max(zr, key=lambda r: r["As_req_cm2"])
        phi_req = 2 * math.sqrt(g["As_req_cm2"] * 100 / lay.n_bars / math.pi)
        if PHI_GRID[0] < phi_req < PHI_GRID[-1]:
            poss = [p for p in POSITIONS if p.zone == zone]
            g["eta_at_As_req"] = max_eta_nm(forces, combos, lay, poss, rules, g["pile"], round(phi_req, 3))[0]
    return rows


def evaluate_options(forces: dict[str, PileForces], basis: str, mode: Mode, As_req_max: float,
                     candidates: list[dict] | None = None, piles=PILES) -> list[dict]:
    """Full check of the provided and of practical layouts (hull screening, exact only near η = 1).
    'fails' lists the failing check groups; 'fails_sensitivity' the crack check with ψ2,TB = 0.5."""
    rows = []
    cands = [dict(PROVIDED, provided=True)] + (candidates or practical_layouts())
    for cand in cands:
        fu = cand["fuste"]
        w = fu.weight_per_m()
        row = dict(layout=fu.label + (" (provided)" if cand.get("provided") else ""), ties=fu.ties.label,
                   n_face=fu.n_face, phi=fu.phi, As_cm2=fu.As / 100, kg_per_m=w["total"],
                   kg_long=w["longitudinal"], kg_ties=w["ties"], provided=bool(cand.get("provided")))
        if fu.As < 0.9 * As_req_max:
            row.update(status="descartada: As < 0.9·As,nec", ok=False, ok_sensitivity=False, fails=["nm"])
            rows.append(row)
            continue
        layouts = {"fuste": cand["fuste"], "arranque": cand["arranque"]}
        res = check_piles(forces, basis, mode, layouts, exact="borderline", screening=False, piles=piles)
        sm = res["summary"]
        tb05 = [k for k in next(iter(sm.values())) if k.startswith("sls_crack[") and "TB=0.5" in k
                and k.endswith("]") and f"Qa={E.BASES[basis]['psi2_Qa']:g}," in k]
        row.update(
            nm=max(max(s["nm1"] or 0, s["nm2"] or 0) for s in sm.values()),
            shear=max(s["shear"] for s in sm.values()),
            detailing=max(s["detailing"] for s in sm.values()),
            detailing_ok=all(s["detailing_ok"] for s in sm.values()),
            sls_crack=max(s["sls_crack"] for s in sm.values()),
            sls_crack_tb05=max(s[k] for s in sm.values() for k in tb05) if tb05 else None,
            sls_sigma_c=max(s["sls_sigma_c"] for s in sm.values()),
            sls_sigma_s=max(s["sls_sigma_s"] for s in sm.values()),
            ok=all(s["verdict"] == "CUMPLE" for s in sm.values()))
        row["sls_sigma"] = max(row["sls_sigma_c"], row["sls_sigma_s"])
        row["fails"] = [k for k in ("nm", "shear", "detailing", "sls_crack", "sls_sigma_c", "sls_sigma_s")
                        if (row[k] > 1.0 + 1e-9 if k != "detailing" else not row["detailing_ok"])]
        tb05_ok = row["sls_crack_tb05"] is None or all(s[k + "_ok"] for s in sm.values() for k in tb05)
        row["fails_sensitivity"] = [] if tb05_ok else ["sls_crack(ψ2,TB=0.5)"]
        row["ok_sensitivity"] = row["ok"] and tb05_ok
        row["status"] = "cumple" if row["ok"] else "no cumple"
        rows.append(row)
    return rows


def make_proposal(main: dict, opts: list[dict], basis: str, mode: Mode) -> dict:
    """Decision D5: lightest layout passing every check; if none exists, the best compromise and
    what else is needed."""
    S = main["summary"]
    failing = {p: [k for k in ("nm1", "nm2", "nm_stations", "shear") if (s[k] or 0) > 1.0 + 1e-9]
               + ([] if s["detailing_ok"] else ["detailing"])
               + ([] if s["sls_crack_ok"] else ["sls_crack"])
               + [k for k in ("sls_sigma_c", "sls_sigma_s") if s[k] > 1.0 + 1e-9]
               for p, s in S.items()}
    failing = {p: v for p, v in failing.items() if v}
    evald = [o for o in opts if "nm" in o]
    passing = sorted((o for o in evald if o["ok"]), key=lambda o: o["kg_per_m"])
    prov = next(o for o in opts if o.get("provided"))
    out = dict(needed=bool(failing), failing_checks=failing, provided=dict(
        layout="12Ø25 + 2eØ10+1eØ10 c/15", kg_per_m=prov["kg_per_m"], fails=prov.get("fails", [])),
        lightest_passing=passing[0] if passing else None)
    if not failing:
        out.update(proposed=None, reason=f"the provided 12Ø25 passes every check under ({basis}, {mode.value}); "
                                         "the lightest passing layout is given for information")
    elif passing:
        out.update(proposed=passing[0], reason="provided reinforcement fails: " +
                   "; ".join(f"{p}: {', '.join(v)}" for p, v in failing.items()))
    else:
        uls_ok = [o for o in evald if not ({"nm", "shear", "detailing"} & set(o["fails"]))]
        best = min(uls_ok or evald, key=lambda o: (len(o["fails"]), o["kg_per_m"]))
        if set(prov["fails"]) <= set(best["fails"]):
            best = prov                     # a lighter layout that fixes nothing is not a proposal
        unmet = sorted({k for p in failing.values() for k in p})
        rec = []
        if {"sls_sigma_c"} & set(unmet):
            sig = max(r["demand"] for r in main["sls"]["char"] if r["check"].startswith("σc"))
            fck_need = sig / K1_SIGMA_C
            rows_c = [o for o in evald if o["sls_sigma_c"] <= 1.0]
            eta_c = max(s["sls_sigma_c"] for s in S.values())
            eta_ce = max(s.get("sls_sigma_c_Ec_eff", 0.0) for s in S.values())
            rec.append(
                "σc ≤ 0.6·fck (characteristic ELS04 = G + Qa + TB1, i.e. the ROM characteristic combination with "
                f"ψ0,Qa = 1.0) is exceeded at the pile heads/feet by up to {eta_c:.3f} "
                f"(σc,max = {sig:.1f} MPa); within As ≤ 0.04·Ac no bar layout brings it below 0.6·fck "
                f"(only {', '.join(o['layout'] for o in rows_c) or 'none'}, all above As,max). A19.7.2(2) asks for "
                "the limit 'in the absence of other measures, such as ... confinement by transverse reinforcement': "
                "keep 12Ø25 and justify the confinement of the three closed Ø10 ties (recommended: Ø10 c/100 over "
                "0.40 m below the beam soffit and above the fixity), or use a concrete with "
                f"fck ≥ {fck_need:.1f} MPa (HA-{int(math.ceil(fck_need / 5.0) * 5)}).")
            rec.append(
                f"The σc verdict uses the short-term Ecm for the whole characteristic action; with the sustained "
                f"share (G + ψ2·Qa) on Ec,eff = Ecm/(1 + φ·Mqp/Mk), φ = {PHI_EF}, the maximum is "
                f"{eta_ce:.3f} × 0.6·fck ({'passes' if eta_ce <= 1.0 else 'still fails'}); the exceedance "
                "therefore depends on the modulus assumption (bollard + quay load are ~75-85 % of Mk, so Ecm "
                "is the defensible, conservative reading).")
        fails_txt = "; ".join(f"{p}: {', '.join(v)}" for p, v in failing.items())
        out.update(proposed=None, no_feasible_layout=True, best_compromise=best, unmet_checks=unmet,
                   recommendation=rec, reason=f"provided reinforcement fails: {fails_txt}. No practical layout "
                                              "within the search space passes every check.")
    sens_fail = [p for p, s in S.items() if any(v != "CUMPLE" for v in s["verdict_sensitivity"].values()
                                                )]
    tb05_key = [k for k in next(iter(S.values())) if k.startswith("sls_crack[") and "TB=0.5" in k and k.endswith("]")
                and f"Qa={E.BASES[basis]['psi2_Qa']:g}," in k]
    tb05_fail = [p for p, s in S.items() for k in tb05_key if not s[k + "_ok"]]
    cand_s = sorted((o for o in evald if not ({"nm", "shear", "detailing", "sls_crack"} & set(o["fails"]))
                     and not o["fails_sensitivity"]), key=lambda o: o["kg_per_m"])
    out["sensitivity"] = dict(
        note="bollard pull ψ2 = 0.5 (ROM 0.2-90 operational upper bound) with ψ2,Qa of the basis; "
             "σc (characteristic) is independent of ψ2 and is not part of this search",
        case=tb05_key[0][len("sls_crack["):-1] if tb05_key else None,
        failing_piles=tb05_fail, failing_piles_any_case=sens_fail,
        max_wk_ratio=max((S[p][k] for p in S for k in tb05_key), default=None),
        proposed=cand_s[0] if (tb05_fail and cand_s) else None,
        feasible=bool(cand_s))
    if tb05_fail and not cand_s:
        big = sorted((o for o in evald if not o["fails_sensitivity"]), key=lambda o: o["kg_per_m"])
        out["sensitivity"]["recommendation"] = (
            "with ψ2,TB = 0.5 the piles crack under the quasi-permanent combination and wk ≤ 0.1 mm (XS3) is not "
            "reachable within As ≤ 0.04·Ac (sr,max ≥ 3.4·c = 204 mm with c = 60 mm, εsm - εcm ≥ 0.6·σs/Es); "
            + (f"only {', '.join(o['layout'] for o in big)} would meet it. " if big else "")
            + "Keep ψ2,TB = 0 (mooring pull transient, as CYPE and the designer assumed, ROM 2.0-11 50 % "
              "quantile ≈ 0 without recorded mooring loads) and document it, or accept wk ≤ 0.2 mm (XS1/XS2 value) "
              "for this load case.")
    return out


# =============================================================================================
# CYPE parity
# =============================================================================================
def _ref_tree() -> dict:
    return json.loads(REF_JSON.read_text(encoding="utf-8"))


def _ref(tree: dict, path: str) -> tuple[float, str, str]:
    o = tree
    for k in path.split("."):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o["value"], o.get("src", ""), o.get("printed", repr(o["value"]))


def _tol_ok(ours: float, printed: str, tol: float = 0.005) -> bool:
    """validate_codigo.py tolerance: max(0.5 %, half a unit of the last printed digit)."""
    s = printed.strip().lstrip("+-")
    dec = len(s.split(".")[1]) if "." in s else 0
    c = float(printed)
    return abs(ours - c) <= max(tol * abs(c), 0.5 * 10 ** (-dec) + 1e-12)


def _cmp(quantity: str, ours: float, tree: dict, path: str, scale: float = 1.0, absval: bool = False,
         tol: float = 0.005, note: str = "") -> dict:
    v, src, printed = _ref(tree, path)
    cy = float(v) * scale
    o = abs(ours) if absval else ours
    c = abs(cy) if absval else cy
    return dict(quantity=quantity, ours=o, cype=c, diff_pct=(o - c) / abs(c) * 100 if c else 0.0,
                src=src, ok=_tol_ok(o / scale, printed if not absval else printed.lstrip("-"), tol) if scale == 1
                else abs(o - c) <= max(tol * abs(c), 1e-12), note=note,
                info=tol > 0.05)          # loose tolerance: shown for information, not counted as parity


def parity_p3_printed() -> list[dict]:
    """P3 head ('FORJADO 1') and fixity ('EMPOTRAMIENTO') recomputed from CYPE's printed
    first-order design forces with Mode.CYPE (every printed value of Anejo 10 P218-P324)."""
    t = _ref_tree()
    rules = RULES[Mode.CYPE]
    rows = []
    for sec_key, pos in (("section_1_forjado_cabeza", "Cabeza"), ("section_2_empotramiento_arranque", "Arranque")):
        base = f"piles.{sec_key}.normal_forces"
        zone = "fuste" if pos == "Cabeza" else "arranque"
        lay = PROVIDED[zone]
        model = section_model(lay, Mode.CYPE)
        N = _ref(t, f"{base}.section_resistance_first_order.NEd")[0]
        Mx = _ref(t, f"{base}.section_resistance_first_order.MEd_x")[0]
        My = _ref(t, f"{base}.section_resistance_first_order.MEd_y")[0]
        dp = design_points(N, Mx, My, lay, rules)
        lab = f"P3 {pos} (CYPE forces)"
        r1 = model.exact.ray(_SI(dp["first"][0]))
        fo = f"{base}.section_resistance_first_order"
        rows += [_cmp(f"{lab} 1st order ee,y (eje x)", dp["ee"][0], t, f"{fo}.ee_y"),
                 _cmp(f"{lab} 1st order ee,x (eje y)", dp["ee"][1], t, f"{fo}.ee_x"),
                 _cmp(f"{lab} 1st order NRd", r1["N"] / KN, t, f"{fo}.NRd"),
                 _cmp(f"{lab} 1st order MRd,x", r1["Mx"] / KNM, t, f"{fo}.MRd_x"),
                 _cmp(f"{lab} 1st order MRd,y", r1["My"] / KNM, t, f"{fo}.MRd_y", tol=0.01,
                      note="small component: half-unit/1 % tolerance"),
                 _cmp(f"{lab} η1 section resistance", r1["eta"], t, f"{base}.eta_1_section_resistance")]
        so = f"{base}.instability_second_order"
        sl = dp["sl"]
        for key, ours in (("lambda", sl["lam"]), ("i_c", sl["i"] / 10), ("lambda_inf_lim", sl["lam_lim"]),
                          ("A", sl["A"]), ("B", sl["B"]), ("omega", sl["omega"]), ("C", sl["C"]),
                          ("n", sl["n"]), ("e_i", sl["ei"]), ("e2", sl["e2"]), ("one_over_r", sl["rinv_per_m"]),
                          ("one_over_r0", sl["r0inv_per_m"]), ("K_r", sl["Kr"]), ("K_phi", sl["Kphi"]),
                          ("beta", sl["beta"]), ("n_u", sl["n_u"]), ("d", sl["d"])):
            try:
                rows.append(_cmp(f"{lab} {key} (eje x)", ours, t, f"{so}.axis_x.{key}", absval=True))
            except KeyError:
                continue
        for key, ours in (("alpha_h", sl["alpha_h"]), ("theta_i", sl["theta_i"])):
            try:
                rows.append(_cmp(f"{lab} {key}", ours, t, f"{so}.axis_x.{key}"))
            except KeyError:
                pass
        S2 = dp["second"][0]
        rows += [_cmp(f"{lab} etot (eje x)", dp["etot"][0][0], t, f"{so}.axis_x.e_tot"),
                 _cmp(f"{lab} etot (eje y)", dp["etot"][0][1], t, f"{so}.axis_y.e_tot"),
                 _cmp(f"{lab} MSd,x", S2[1], t, f"{so}.MSd_x"),
                 _cmp(f"{lab} MSd,y", S2[2], t, f"{so}.MSd_y")]
        r2 = model.exact.ray(_SI(S2))
        eq = f"{base}.equilibrium_at_ultimate.resultants"
        rows += [_cmp(f"{lab} 2nd order NRd", r2["N"] / KN, t, f"{so}.NRd"),
                 _cmp(f"{lab} 2nd order MRd,x", r2["Mx"] / KNM, t, f"{so}.MRd_x"),
                 _cmp(f"{lab} 2nd order MRd,y", r2["My"] / KNM, t, f"{so}.MRd_y"),
                 _cmp(f"{lab} η2 instability", r2["eta"], t, f"{base}.eta_2_instability"),
                 _cmp(f"{lab} Cc at failure", r2["Cc"] / KN, t, f"{eq}.Cc.resultant"),
                 _cmp(f"{lab} Cs at failure", r2["Cs"] / KN, t, f"{eq}.Cs.resultant"),
                 _cmp(f"{lab} T at failure", r2["T"] / KN, t, f"{eq}.T.resultant")]
        etaN, _ = model.exact.constant_N(_SI(S2))
        aprov = [r for r in t["piles"]["appendix_1_section_3"]["elu_checks_4_2"]["P3"]["rows"]
                 if r["posicion"] == pos and "N,M" in r["comp"]][0]
        rows.append(dict(quantity=f"{lab} listing 'Aprov.' N,M (constant-N definition)", ours=etaN * 100,
                         cype=aprov["NM_pct"], diff_pct=(etaN * 100 - aprov["NM_pct"]) / aprov["NM_pct"] * 100,
                         src=aprov["src"], ok=abs(etaN * 100 - aprov["NM_pct"]) <= 0.5,
                         note="spec C4; the ray definition gives %.2f" % (r2["eta"] * 100)))
        # shear
        shb = f"piles.{sec_key}.shear"
        z = Z_VRDMAX_CYPE[zone]
        vx, vy = _ref(t, f"{shb}.VEd_x_eta1")[0], _ref(t, f"{shb}.VEd_y_eta1")[0]
        vmax = vrd_max(lay, z)
        rows += [_cmp(f"{lab} VRd,max (z CYPE {z})", vmax, t, f"{shb}.VRd_max"),
                 _cmp(f"{lab} η VRd,max", math.hypot(vx, vy) / vmax, t, f"{shb}.eta_1_VRdmax"),
                 _cmp(f"{lab} σcp for αcw, dir X", sigma_cp_cype(N, lay, "x"), t,
                      f"{shb}.compression_strut_dir_X.sigma_cp"),
                 _cmp(f"{lab} σcp for αcw, dir Y", sigma_cp_cype(N, lay, "y"), t,
                      f"{shb}.compression_strut_dir_Y.sigma_cp")]
        rows.append(dict(quantity=f"{lab} VRd,max with z = 0.9·d (CE)", ours=vrd_max(lay, 0.9 * lay.shear_group()[1]),
                         cype=vmax, diff_pct=(vrd_max(lay, 0.9 * lay.shear_group()[1]) / vmax - 1) * 100,
                         src="C12 (INFO)", ok=True, info=True,
                         note="code-strict alternative, used for the verdict"))
        if pos == "Cabeza":
            nb = f"{shb}.concrete_no_shear_reinf_dir_X"
            Nv = _ref(t, f"{nb}.NEd")[0]
            vc = vrd_c(Nv, lay)
            vx2, vy2 = _ref(t, f"{shb}.VEd_x_eta2")[0], _ref(t, f"{shb}.VEd_y_eta2")[0]
            rows += [_cmp(f"{lab} VRd,c (CYPE label VRd,s)", vc["V1"], t, f"{nb}.VRd_c_printed_VRd_s"),
                     _cmp(f"{lab} VRd,c minimum", vc["Vmin"], t, f"{nb}.VRd_c_min_printed_VRd_s"),
                     _cmp(f"{lab} k", vc["k"], t, f"{nb}.k"),
                     _cmp(f"{lab} ρl", vc["rho_l"], t, f"{nb}.rho_l"),
                     _cmp(f"{lab} σcp", vc["sigma_cp"], t, f"{nb}.sigma_cp"),
                     _cmp(f"{lab} vmin", vc["vmin"], t, f"{nb}.v_min"),
                     _cmp(f"{lab} d (VRd,c)", vc["d"], t, f"{nb}.d"),
                     _cmp(f"{lab} Asl (8Ø25)", vc["Asl"] / 100, t, f"{nb}.Asl"),
                     _cmp(f"{lab} η VRd,c", math.hypot(vx2, vy2) / vc["V"], t, f"{shb}.eta_2_VRd")]
            mm = f"piles.{sec_key}.min_max_reinforcement"
            det = f"piles.{sec_key}.detailing"
            Nmax = _ref(t, f"{mm}.As_min_compression.NEd")[0]
            rows += [_cmp("P3 As,min = 0.004·Ac (AN)", 0.004 * lay.Ac / 100, t, f"{mm}.As_min_total.As_min"),
                     _cmp("P3 As,max = fcd·Ac/fyd (AN)", lay.concrete.fcd * lay.Ac / lay.steel.fyd / 100, t,
                          f"{mm}.As_max.As_max"),
                     _cmp("P3 A's,min = 0.10·NEd/fyd", 0.10 * Nmax * KN / lay.steel.fyd / 100, t,
                          f"{mm}.As_min_compression.As_min"),
                     _cmp("P3 As provided", lay.As / 100, t, f"{mm}.As_min_total.As"),
                     _cmp("P3 clear spacing of bars", lay.clear_spacing, t, f"{det}.longitudinal.checks.0.provided"),
                     _cmp("P3 smin (A19.8.2(2))", max(lay.phi, 25.0, 20.0), t, f"{det}.longitudinal.s_min"),
                     _cmp("P3 scl,max", min(15 * lay.phi, 300.0, lay.b), t, f"{det}.ties.spacing_limit.s_cl_max"),
                     _cmp("P3 Øt,min = Ømax/4", max(6.0, lay.phi / 4), t, f"{det}.ties.checks.2.limit", tol=0.01,
                          note="CYPE prints 6.3 (6.25)"),
                     _cmp("P3 clear distance between ties", lay.ties.spacing - lay.ties.phi, t,
                          f"{det}.ties.checks.0.provided")]
    return rows


def aprov_listing(forces: dict[str, PileForces], res_cype: dict) -> tuple[list[dict], dict]:
    """CYPE Apéndice §4.2 'Aprov.' (N,M and Q per pile and position) vs ours: (a) recomputed from
    the forces CYPE prints in the listing, (b) from our SAP forces (governing over ELU01-22)."""
    t = _ref_tree()
    table = t["piles"]["appendix_1_section_3"]["elu_checks_4_2"]
    out, ratios = [], []
    for pile in res_cype["summary"]:
        for pos in POSITIONS:
            lay = PROVIDED[pos.zone]
            model = section_model(lay, Mode.CYPE)
            prow = [r for r in table[pile]["rows"] if r["posicion"] == pos.name]
            nm_row = [r for r in prow if "N,M" in r["comp"]][0]
            q_row = [r for r in prow if r["comp"].startswith("Q")][0]
            S = (nm_row["N_kN"], nm_row["Mxx_kNm"], nm_row["Myy_kNm"])
            rr = model.exact.ray(_SI(S))
            eN, _ = model.exact.constant_N(_SI(S), rr)
            V = math.hypot(q_row["Qx_kN"], q_row["Qy_kN"])
            if pos.name == "Arranque":
                q_ours_cf = V / vrd_max(lay, Z_VRDMAX_CYPE[pos.zone])
            else:
                q_ours_cf = V / vrd_c(q_row["N_kN"], lay)["V"]
            sap = res_cype["nm"]["per_pile"][pile][pos.name]
            nm_sap = max((sap[k] for k in ("nm1", "nm2") if sap[k] is not None), key=lambda r: r["eta"])
            q_sap = res_cype["shear"]["per_pile"][pile][pos.name]
            q_sap_v = q_sap["vrdmax"] if pos.name == "Arranque" else q_sap["vrdc"]
            ratios.append(nm_row["NM_pct"] / (rr["eta"] * 100))
            out.append(dict(pile=pile, position=pos.name, cype_NM=nm_row["NM_pct"], cype_Q=q_row["Q_pct"],
                            cype_forces=f"{S[0]:.1f}/{S[1]:.1f}/{S[2]:.1f}",
                            NM_ray_cypeforces=rr["eta"] * 100, NM_constN_cypeforces=eN * 100,
                            Q_cypeforces=q_ours_cf * 100,
                            NM_ray_sap=nm_sap["eta"] * 100,
                            NM_constN_sap=None if nm_sap["eta_N"] is None else nm_sap["eta_N"] * 100,
                            NM_combo_sap=nm_sap["combo"], Q_sap=q_sap_v * 100,
                            diff_NM_sap_pct=(nm_sap["eta"] * 100 - nm_row["NM_pct"]) / nm_row["NM_pct"] * 100,
                            diff_Q_sap_pct=(q_sap_v * 100 - q_row["Q_pct"]) / q_row["Q_pct"] * 100,
                            src=nm_row["src"]))
    stats = dict(n=len(ratios), mean_cype_over_ray=float(np.mean(ratios)), sd=float(np.std(ratios)),
                 min=float(np.min(ratios)), max=float(np.max(ratios)))
    return out, stats


def parity_p3_sap(forces: dict[str, PileForces], res_cype: dict) -> list[dict]:
    """P3 with our SAP forces (Mode.CYPE, basis CYPE) vs the numbers CYPE printed.  CYPE prints η1
    and η2 of the combination that governs η2 (ELU08 = 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo), so
    the same combination is evaluated here; the governing values over ELU01-22 are added."""
    t = _ref_tree()
    rules = RULES[Mode.CYPE]
    fac = E.uls("CYPE")["ELU08"]
    rows = []
    for sec_key, pos in (("section_1_forjado_cabeza", "Cabeza"), ("section_2_empotramiento_arranque", "Arranque")):
        base = f"piles.{sec_key}.normal_forces"
        position = next(p for p in POSITIONS if p.name == pos)
        lay = PROVIDED[position.zone]
        model = section_model(lay, Mode.CYPE)
        pf = forces["P3"]
        N, Mx, My, Vx, Vy = pf.combine(fac)[pf.station(position.z)]
        dp = design_points(float(N), float(Mx), float(My), lay, rules)
        r1 = model.exact.ray(_SI(dp["first"][0]))
        r2 = model.exact.ray(_SI(dp["second"][0]))
        lab = f"P3 {pos} (SAP forces, ELU08)"
        fo, so = f"{base}.section_resistance_first_order", f"{base}.instability_second_order"
        rows += [
            _cmp(f"{lab} NEd", N, t, f"{fo}.NEd", tol=0.02),
            _cmp(f"{lab} MEd,x 1st order", Mx, t, f"{fo}.MEd_x", tol=0.02),
            _cmp(f"{lab} MEd,y 1st order", My, t, f"{fo}.MEd_y", tol=5.0,
                 note="minor-axis moment: SAP and CYPE differ in the longitudinal stiffness"),
            _cmp(f"{lab} η1", r1["eta"], t, f"{base}.eta_1_section_resistance", tol=0.02),
            _cmp(f"{lab} λlim", dp["sl"]["lam_lim"], t, f"{so}.axis_x.lambda_inf_lim", tol=0.02),
            _cmp(f"{lab} MSd,x", dp["second"][0][1], t, f"{so}.MSd_x", tol=0.02),
            _cmp(f"{lab} MSd,y", dp["second"][0][2], t, f"{so}.MSd_y", tol=0.25,
                 note="minor-axis moment: SAP and CYPE differ in the longitudinal stiffness"),
            _cmp(f"{lab} η2", r2["eta"], t, f"{base}.eta_2_instability", tol=0.02),
            _cmp(f"{lab} η VRd,max", math.hypot(Vx, Vy) / vrd_max(lay, Z_VRDMAX_CYPE[position.zone]), t,
                 f"piles.{sec_key}.shear.eta_1_VRdmax", tol=0.03)]
        pp = res_cype["nm"]["per_pile"]["P3"][pos]
        for kind, key in (("nm1", "eta_1_section_resistance"), ("nm2", "eta_2_instability")):
            rows.append(_cmp(f"P3 {pos} (SAP forces) governing {kind} over ELU01-22 ({pp[kind]['combo']})",
                             pp[kind]["eta"], t, f"{base}.{key}", tol=0.05,
                             note="CYPE prints the η1 of the η2-governing combination" if kind == "nm1" else ""))
        if pos == "Cabeza":
            shp = res_cype["shear"]["per_pile"]["P3"][pos]
            rows.append(_cmp("P3 Cabeza (SAP forces) governing η VRd,c", shp["vrdc"], t,
                             f"piles.{sec_key}.shear.eta_2_VRd", tol=0.03))
    return rows


# =============================================================================================
# run
# =============================================================================================
def _clean(o, nd: int = 4):
    if isinstance(o, dict):
        return {str(k): _clean(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v, nd) for v in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        v = float(o)
        if math.isnan(v) or math.isinf(v):
            return None
        a = abs(v)
        return round(v, 2 if a >= 100 else 3 if a >= 1 else 5 if a >= 1e-3 else 8)
    if isinstance(o, Mode):
        return o.value
    if isinstance(o, np.ndarray):
        return _clean(o.tolist(), nd)
    return o


def run(basis: str = "ROM", mode: Mode = Mode.CODIGO, parity: bool = True, options: bool = True,
        variants: bool = True, stations: dict | None = None, verbose: bool = False, piles=PILES) -> dict:
    """Pile checks.  The main result is (basis, mode) - by default the final design (ROM, CODIGO,
    orchestrator decision D5); the CYPE parity (Mode.CYPE, basis CYPE) and the other variants are
    summarised alongside."""
    t0 = time.time()
    log = (lambda *a: print(f"[{time.time() - t0:6.1f} s]", *a, file=sys.stderr)) if verbose else (lambda *a: None)
    forces = load_forces(stations)
    log("forces loaded")
    main = check_piles(forces, basis, mode, piles=piles)
    log(f"main check ({basis}, {mode.value}) done")
    tables = {
        "uls_nm": main["nm"]["rows"],
        "uls_nm_stations": main["nm"]["screening"],
        "shear": main["shear"]["rows"],
        "detailing": main["detailing"]["rows"],
        "sls_quasi_permanent": main["sls"]["qp"],
        "sls_characteristic": main["sls"]["char"],
    }
    comparison = []
    var_rows = []
    listing_ratio = "≈1.014 (sd 0.002)"
    res_cype = None
    if parity or variants:
        res_cype = main if (basis, mode) == ("CYPE", Mode.CYPE) else \
            check_piles(forces, "CYPE", Mode.CYPE, with_sls=False, piles=piles)
        log("CYPE parity variant done")
    if parity:
        comparison += parity_p3_printed()
        log("P3 parity (printed forces) done")
        comparison += parity_p3_sap(forces, res_cype)
        listing, stats = aprov_listing(forces, res_cype)
        tables["aprov_listado"] = listing
        for r in listing:
            comparison.append(dict(quantity=f"{r['pile']} {r['position']} 'Aprov.' N,M (ray, SAP forces)",
                                   ours=r["NM_ray_sap"], cype=r["cype_NM"], diff_pct=r["diff_NM_sap_pct"],
                                   src=r["src"], ok=abs(r["diff_NM_sap_pct"]) <= 5.0,
                                   note="listing ≈ %.3f × ray η (systematic, see meta)"
                                        % stats["mean_cype_over_ray"]))
            comparison.append(dict(quantity=f"{r['pile']} {r['position']} 'Aprov.' Q (SAP forces)",
                                   ours=r["Q_sap"], cype=r["cype_Q"], diff_pct=r["diff_Q_sap_pct"],
                                   src=r["src"], ok=abs(r["diff_Q_sap_pct"]) <= 5.0, note=""))
        tables["aprov_listado_stats"] = [stats]
        listing_ratio = "%.3f (sd %.3f, range %.3f-%.3f)" % (stats["mean_cype_over_ray"], stats["sd"], stats["min"],
                                                            stats["max"])
        log("listing parity done")
    if variants:
        runs = {("CYPE", "cype"): res_cype}
        if (basis, mode.value) != ("CYPE", "codigo"):
            runs[("CYPE", "codigo")] = check_piles(forces, "CYPE", Mode.CODIGO, exact="governing",
                                                   with_sls=False, screening=False, piles=piles)
        runs[(basis, mode.value)] = main
        for pile in piles:
            row = dict(pile=pile)
            for (b, m), res in runs.items():
                s = res["summary"][pile]
                row[f"nm1[{b},{m}]"] = s["nm1"]
                row[f"nm2[{b},{m}]"] = s["nm2"]
                row[f"shear[{b},{m}]"] = s["shear"]
            var_rows.append(row)
        tables["variants"] = var_rows
        log("variants done")
    As_rows = required_steel(forces, basis, mode, piles=piles)
    tables["as_required"] = As_rows
    log("required steel done")
    proposal = {"needed": any(s["verdict"] != "CUMPLE" for s in main["summary"].values())}
    if options:
        As_req_max = max((r["As_req_cm2"] or 0) for r in As_rows) * 100
        opt = evaluate_options(forces, basis, mode, As_req_max, piles=piles)
        tables["options"] = opt
        proposal = make_proposal(main, opt, basis, mode)
        log("options done")
    summary = {p: {k: v for k, v in s.items()} for p, s in main["summary"].items()}

    def gov(res, key):
        vals = [(s[key], p) for p, s in res["summary"].items() if s.get(key) is not None]
        return max(vals) if vals else (None, None)
    findings = []
    for tag, res in ((f"{basis}/{mode.value} (verdict)", main), ("CYPE/cype (parity)", res_cype)):
        if res is None:
            continue
        n1, n2, sv = gov(res, "nm1"), gov(res, "nm2"), gov(res, "shear")
        findings.append(f"{tag}: max η N,M 1st order {n1[0]:.3f} ({n1[1]}), 2nd order {n2[0]:.3f} ({n2[1]}), "
                        f"shear {sv[0]:.3f} ({sv[1]})")
    sc, cr = gov(main, "sls_sigma_c"), gov(main, "sls_crack")
    findings.append(f"SLS: primary quasi-permanent crack η {cr[0]:.3f} ({cr[1]}, "
                    f"{'cracked' if main['summary'][cr[1]]['sls_crack_cracked'] else 'uncracked'}); "
                    f"characteristic σc/0.6fck {sc[0]:.3f} ({sc[1]})")
    bad = [p for p, s_ in main["summary"].items() if s_["verdict"] != "CUMPLE"]
    findings.append("verdict: " + ("all piles CUMPLE" if not bad else "NO CUMPLE " + ", ".join(bad)))
    if comparison:
        par = [r for r in comparison if not r.get("info")]
        n_ok = sum(1 for r in par if r.get("ok"))
        findings.append(f"CYPE comparison: {n_ok}/{len(par)} parity rows within tolerance (+{len(comparison) - len(par)} "
                        "informational rows: code-strict alternatives and SAP-vs-CYPE minor-axis moments)")
    meta = dict(
        module="pilotes", basis=basis, mode=mode.value, basis_ref=E.BASES[basis]["ref"],
        rules=RULES[mode].__dict__ | {"mode": mode.value},
        provided={z: dict(label=l.label, ties=l.ties.label, c_mm=l.c, As_cm2=l.As / 100) for z, l in PROVIDED.items()},
        positions=[p.__dict__ for p in POSITIONS],
        clauses=CLAUSES,
        assumptions=[
            "Forces: SAP2000 v27.1 (sap2000/resultados_sap), CYPE sign convention; section axes MEd,x = My(§3.3), "
            "MEd,y = Mx(§3.3), VEd,x = Qx, VEd,y = Qy.",
            "l0 = 6.70 m in both axes (β = 1 on the free length), l = 6.70 m in αh, m = 1.",
            "φef = 1.75 (CYPE input, conservative: A19.5.8.4 with ψ2,bollard = 0 would give φef ≈ 0).",
            "λlim with B = √(1+2ω) (BOE erratum), C = 0.7; e2 with c = π² and Kr ≤ 1.",
            "Second order added at every checked section (head, foot, fixity and intermediate stations).",
            "VRd,c: Asl = all bars except the compressed face row, d = their centroid (CYPE C10) in both modes.",
            "fywd = 0.8·fywk = 400 MPa with ν1 = 0.6; VRd,s uses 4 full-depth Ø10 legs per direction (shaft).",
            "SLS: Ecm (limestone) = %.0f MPa, αe = Es/Ecm; uncracked criterion on the homogenised section, corner "
            "fibre, fct,eff = fctm = %.2f MPa; wk with kt = 0.4, k1 = 0.8, k2 = 0.5 (bending), k3 = 3.4, k4 = 0.425, "
            "c = cover + tie; depths measured perpendicular to the neutral axis." % (PROVIDED["fuste"].concrete.Ecm,
                                                                                   PROVIDED["fuste"].concrete.fctm),
            "Characteristic combinations ELS01-08 (all factors 1.0) for both bases; σc with Ecm (verdict) and, for "
            "information, with Ec,eff = Ecm/(1 + φ·Mqp/Mk), φ = %.2f, Mqp from G + ψ2,Qa·Qa of the basis." % PHI_EF,
            "wk: Ac,eff = gross concrete area within hc,ef of the most tensioned fibre (b·hc,ef for uniaxial "
            "bending), ρp,eff = As,eff/Ac,eff with the bars inside it.",
            "Required As: provided bar positions kept, bar area scaled (Ø grid %s, linear interpolation)."
            % (PHI_GRID,),
        ],
        cype_listing_note=("CYPE's summary 'Aprov.' (Apéndice §3.5/§4.2) is reproduced by neither the exact ray "
                           "nor the constant-N utilisation for all piles: with the forces printed in the listing it "
                           "is %s × the exact ray η (42 rows, compression and tension piles), i.e. CYPE's "
                           % listing_ratio +
                           "summary uses a slightly conservative (discretised) interaction surface; the detailed "
                           "body check (η = 0.913 / 0.894) is reproduced exactly by the ray.  The constant-N match "
                           "of spec C4 holds for P3 only.  The shear 'Aprov.' is reproduced within ±0.1 points."),
        findings=findings,
        runtime_s=round(time.time() - t0, 1),
    )
    out = dict(meta=meta, tables=tables, cype_comparison=comparison, summary=summary, proposal=proposal)
    return _clean(out)


# =============================================================================================
# markdown report
# =============================================================================================
def _f(v, nd: int = 3) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "sí" if v else "no"
    if isinstance(v, (int, float)):
        return f"{v:.{nd}f}"
    return str(v)


def _table(rows: list[dict], cols: list[tuple[str, str, int]]) -> str:
    head = "| " + " | ".join(c[1] for c in cols) + " |\n|" + "|".join("---" for _ in cols) + "|\n"
    body = "".join("| " + " | ".join(_f(r.get(c[0]), c[2]) for c in cols) + " |\n" for r in rows)
    return head + body


def to_markdown(res: dict) -> str:
    m, T, S = res["meta"], res["tables"], res["summary"]
    md = [f"# Pilotes 40x40 HA-50: comprobación a Código Estructural (base {m['basis']}, modo {m['mode']})\n",
          "Generated by `python3 diseno/python/codigo/pilotes.py` (diseno/python/codigo/pilotes.py). Forces: SAP2000 v27.1. "
          f"Runtime {m['runtime_s']} s.\n",
          "## Assumptions\n", "".join(f"- {a}\n" for a in m["assumptions"]),
          f"\nRules ({m['mode']}): " + ", ".join(f"{k} = {v}" for k, v in m["rules"].items()) + "\n",
          "\n## Findings\n\n", "".join(f"- {x}\n" for x in m.get("findings", [])),
          "\n## Verdict per pile (final design)\n"]
    rows = []
    for p, s in S.items():
        r = dict(pile=p, **{k: v for k, v in s.items() if not isinstance(v, dict)})
        sens = s.get("verdict_sensitivity", {})
        r["sens"] = "; ".join(f"{k}: {v}" for k, v in sens.items())
        rows.append(r)
    md.append(_table(rows, [("pile", "pile", 0), ("nm1", "η N,M 1er", 3), ("nm1_at", "at", 0),
                            ("nm2", "η N,M 2º", 3),
                            ("nm2_at", "at", 0), ("nm_stations", "η estaciones", 3), ("shear", "η cortante", 3),
                            ("detailing", "η disposiciones", 3), ("sls_crack", "fisuración (primaria)", 3),
                            ("sls_crack_cracked", "fisurado", 0), ("sls_sigma_c_qp", "σc,qp/0.45fck", 3),
                            ("sls_sigma_c", "σc/0.6fck", 3), ("sls_sigma_c_Ec_eff", "σc/0.6fck Ec,eff (info)", 3),
                            ("sls_sigma_s", "σs/0.8fyk", 3), ("verdict", "veredicto", 0)]))
    md.append("\nSensitivity of the crack check (other ψ2 values):\n\n")
    md.append(_table(rows, [("pile", "pile", 0), ("sens", "veredicto por caso", 0)]))
    md.append("\nFisuración: η = σct/fctm when uncracked, wk/0.1 mm when cracked.\n")
    if "variants" in T:
        md.append("\n## Variants (bases D1 / section modes D2): governing η\n\n")
        keys = [k for k in T["variants"][0] if k != "pile"]
        md.append(_table(T["variants"], [("pile", "pile", 0)] + [(k, k, 3) for k in keys]))
    md.append("\n## ULS N-Mx-My (governing combination per position)\n\n")
    md.append(_table(T["uls_nm"], [("pile", "pile", 0), ("position", "pos.", 0), ("check", "check", 0),
                                   ("combo", "combo", 0), ("N", "N", 1), ("MEd_x", "MEd,x", 1), ("MEd_y", "MEd,y", 1),
                                   ("NRd", "NRd", 1), ("MRd_x", "MRd,x", 1), ("MRd_y", "MRd,y", 1),
                                   ("lam_lim", "λlim", 2), ("e2", "e2", 2), ("case", "ei", 0),
                                   ("eta", "η ray", 3), ("eta_N", "η N cte", 3), ("ok", "ok", 0)]))
    md.append("\nIntermediate stations (screening, shaft section, second order added everywhere):\n\n")
    md.append(_table(T["uls_nm_stations"], [("pile", "pile", 0), ("z", "z gov", 2), ("combo", "combo", 0),
                                            ("eta", "η max", 3), ("eta_ends", "η extremos", 3),
                                            ("ends_govern", "extremos gobiernan", 0)]))
    md.append("\n## Shear\n\n")
    md.append(_table([r for r in T["shear"] if r["key"] in ("vrdc", "vrdmax", "vrds_opt", "verdict")],
                     [("pile", "pile", 0), ("position", "pos.", 0), ("check", "check", 0), ("combo", "combo", 0),
                      ("N", "N", 1), ("VEd_x", "VEd,x", 2), ("VEd_y", "VEd,y", 2), ("capacity", "VR", 1),
                      ("eta", "η", 3), ("ok", "ok", 0)]))
    md.append("\n## Detailing\n\n")
    md.append(_table(T["detailing"], [("zone", "zone", 0), ("pile", "pile", 0), ("check", "check", 0),
                                      ("clause", "clause", 0), ("demand", "provided", 2), ("capacity", "limit", 2),
                                      ("eta", "η", 3), ("ok", "ok", 0), ("note", "note", 0)]))
    md.append("\n## SLS: quasi-permanent crack control (XS3, wmax = 0.1 mm)\n\n")
    md.append(_table(T["sls_quasi_permanent"], [("pile", "pile", 0), ("position", "pos.", 0), ("case", "case", 0),
                                                ("N", "N", 1), ("Mx", "Mx", 1), ("My", "My", 1),
                                                ("sig_ct", "σct hom.", 2), ("sig_ct_gross", "σct bruta", 2),
                                                ("fctm", "fctm", 2), ("cracked", "fisura", 0), ("sig_s", "σs", 1),
                                                ("wk", "wk", 3), ("eta", "η", 3), ("ok", "ok", 0)]))
    md.append("\n## SLS: characteristic stresses (ELS01-08)\n\n")
    md.append(_table(T["sls_characteristic"], [("pile", "pile", 0), ("position", "pos.", 0), ("check", "check", 0),
                                               ("combo", "combo", 0), ("demand", "σ", 2), ("capacity", "limit", 1),
                                               ("eta", "η", 3), ("ok", "ok", 0),
                                               ("sig_c_Ec_eff", "σc Ec,eff (info)", 2),
                                               ("eta_Ec_eff", "η Ec,eff (info)", 3)]))
    md.append("\n## Required steel (As required / As provided)\n\n")
    md.append(_table(T["as_required"], [("pile", "pile", 0), ("zone", "zone", 0), ("position", "gov. pos.", 0),
                                        ("combo", "combo", 0), ("As_req_cm2", "As nec (cm2)", 2),
                                        ("As_prov_cm2", "As real (cm2)", 2), ("ratio", "nec/real", 3),
                                        ("eta_prov", "η real", 3), ("eta_at_As_req", "η(As nec)", 3),
                                        ("practical", "práctica mín. (N,M)", 0), ("practical_As_cm2", "As", 2),
                                        ("practical_eta", "η", 3)]))
    if "options" in T:
        md.append("\n## Practical layouts\n\n")
        md.append(_table(T["options"], [("layout", "layout", 0), ("ties", "cercos", 0), ("As_cm2", "As", 2),
                                        ("kg_per_m", "kg/m", 1), ("nm", "η N,M", 3), ("shear", "η V", 3),
                                        ("detailing_ok", "disp.", 0), ("sls_crack", "fisur.", 3),
                                        ("sls_crack_tb05", "fisur. ψ2,TB=0.5", 3), ("sls_sigma_c", "σc/0.6fck", 3),
                                        ("sls_sigma_s", "σs/0.8fyk", 3), ("status", "estado", 0),
                                        ("fails", "falla", 0)]))
    pr = res["proposal"]
    md.append("\n## Proposal (D5)\n\n")
    md.append(f"- needed: {pr['needed']}\n- {pr.get('reason', '')}\n")
    if pr.get("provided"):
        md.append(f"- provided: {pr['provided']['layout']} ({pr['provided']['kg_per_m']:.1f} kg/m); fails: "
                  f"{', '.join(pr['provided']['fails']) or 'none'}\n")

    def _lay(o):
        return f"{o['layout']} + {o['ties']} ({o['kg_per_m']:.1f} kg/m, As {o['As_cm2']:.2f} cm2, fails: " \
               f"{', '.join(o.get('fails') or []) or 'none'})"
    for k in ("proposed", "best_compromise", "lightest_passing"):
        o = pr.get(k)
        md.append(f"- {k}: {_lay(o) if o else '-'}\n")
    for r in pr.get("recommendation", []):
        md.append(f"- recommendation: {r}\n")
    sens = pr.get("sensitivity", {})
    if sens:
        md.append(f"- sensitivity [{sens.get('case')}] ({sens.get('note')}): failing piles "
                  f"{', '.join(sens.get('failing_piles') or []) or 'none'}; max wk/wmax "
                  f"{_f(sens.get('max_wk_ratio'))}; lightest layout passing it (ULS, detailing, crack): "
                  f"{_lay(sens['proposed']) if sens.get('proposed') else '-'}\n")
        if sens.get("recommendation"):
            md.append(f"- sensitivity recommendation: {sens['recommendation']}\n")
    md.append("\n## Comparison with CYPE (Anejo 10)\n\n")
    md.append(m["cype_listing_note"] + "\n\n")
    md.append(_table(res["cype_comparison"], [("quantity", "quantity", 0), ("ours", "ours", 3), ("cype", "CYPE", 3),
                                              ("diff_pct", "diff %", 2), ("ok", "ok", 0), ("info", "info", 0),
                                              ("src", "src", 0),
                                              ("note", "note", 0)]))
    if "aprov_listado" in T:
        md.append("\n### Listing 'Aprov.' per pile\n\n")
        md.append(_table(T["aprov_listado"], [("pile", "pile", 0), ("position", "pos.", 0), ("cype_NM", "CYPE N,M", 1),
                                              ("NM_ray_cypeforces", "ray (CYPE F)", 2),
                                              ("NM_constN_cypeforces", "N cte (CYPE F)", 2),
                                              ("NM_ray_sap", "ray (SAP)", 2), ("NM_constN_sap", "N cte (SAP)", 2),
                                              ("cype_Q", "CYPE Q", 1), ("Q_cypeforces", "Q (CYPE F)", 2),
                                              ("Q_sap", "Q (SAP)", 2)]))
        st = T["aprov_listado_stats"][0]
        md.append(f"\nCYPE 'Aprov.' / ray η (CYPE forces): mean {st['mean_cype_over_ray']:.4f}, sd {st['sd']:.4f}, "
                  f"range {st['min']:.4f}-{st['max']:.4f} ({st['n']} rows).\n")
    return "".join(md)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--basis", default="ROM", choices=("CYPE", "ROM"))
    ap.add_argument("--mode", default="codigo", choices=("cype", "codigo"))
    ap.add_argument("--no-options", action="store_true")
    ap.add_argument("--out", default=str(OUT_DIR))
    a = ap.parse_args(argv)
    res = run(a.basis, Mode(a.mode), options=not a.no_options, verbose=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pilotes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "pilotes.md").write_text(to_markdown(res), encoding="utf-8")
    bad = [p for p, s in res["summary"].items() if s["verdict"] != "CUMPLE"]
    print(f"pilotes: {len(res['summary'])} piles, basis {a.basis}, mode {a.mode}: "
          f"{'all CUMPLE' if not bad else 'NO CUMPLE: ' + ', '.join(bad)}; written to {out}/pilotes.json|.md "
          f"({res['meta']['runtime_s']} s)")


if __name__ == "__main__":
    main()
