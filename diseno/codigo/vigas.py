"""Transverse beams (CYPE pórticos 3-9 = model axes 1-7) and 25x30 edge beams (pórticos 1, 10)
of one 40 m module of the Muelle de Trasmallo: design checks to the Código Estructural,
Anejo 19 (EN 1992-1-1 with the Spanish nationally determined parameters).

Forces: SAP2000 v27.1 (``esfuerzos.load_stations``), CYPE sign convention (M sagging +,
V = dM/dy, T), combined per basis ("CYPE" = Anejo 10 psi factors, "ROM" = ROM 2.0-11,
psi0,Qa = 1.0 and psi2,Qa = 0.8).  Sections: ``armado_vigas`` (provided CYPE reinforcement),
``seccion`` (fibre model: Mode.CYPE reproduces CYPECAD, Mode.CODIGO is code-strict).

Checks (clause of A19 unless noted):

* ULS bending 6.1 at the pile faces (5.3.2.2(3)), the span (max sagging), the cantilever faces;
  pile-axis moments as information (CYPE's 'P3' node moment, C20).  'Área Nec.' =
  singly-reinforced tension steel (C20).
* detailing 9.2.1.1 (As,min (9.1) with z = 0.9d (CYPE, C14) and z = 0.8h (CE), As,max 0.04Ac),
  8.2(2) clear spacing, 9.2.3(4) 350 mm (C17), 9.2.2 links (rho_w,min, sl,max, st,max).
* shear 6.2: VRd,max with V at the face, VRd,s with V at d from the face (6.2.1(8)),
  fywd = 0.8·fywk = 400 MPa with nu1 = 0.6 ((6.10.a) + NOTA, C13); cot(theta) = 1 (CYPE) or the
  largest value in 0.5..2.0 (6.7N) allowed by the strut check; shift rule 9.2.1.3(2) / (6.18):
  al and dFtd reported per face, not added to the face moment (MEd,max = face moment, see meta).
* torsion 6.3 (thin-walled web rectangle): (6.29) interaction, (6.31) TRd,c, links (V + T per
  leg of the hoop) and longitudinal steel (6.28) added to the bending tension chord.
* suspension 6.2.1(9): the hollow-core plates bear on the ledges (load applied near the bottom),
  so the web links carry q·Lp/2 per ledge in addition to the shear steel (CE cases).
* SLS (CE Art. 27, 7.1-7.4): quasi-permanent QP = G + psi2·Qa (bollard psi2 = 0; 0.5 as a
  sensitivity), uncracked criterion sigma_ct <= fctm (7.1(2)), else wk (7.3.4) <= 0.1 mm (XS3,
  Tabla 27.2); characteristic ELS01-08: sigma_c <= 0.6 fck, sigma_s <= 0.8 fyk (7.2);
  deflection 7.4 (span/depth (7.16) and a cracked-section estimate with creep, L/250, L/500).

``run()`` returns the JSON-ready result (meta / tables / cype_comparison / summary / proposal);
``python3 diseno/codigo/vigas.py`` writes diseno/output/vigas.json and vigas.md.
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
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
DISENO = HERE.parent
for _p in (HERE, DISENO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import esfuerzos as E  # noqa: E402
import armado_vigas as AV  # noqa: E402
from armado_vigas import BarGroup, BeamReinforcement, BeamSection  # noqa: E402
from seccion import (B500SD, HA35, KNM, Bar, Mode, crack_width, cracked_stresses,  # noqa: E402
                     cracking_moment, homogenised, uncracked_stresses)

OUT_DIR = DISENO / "output"
REF = json.loads(AV.REF_JSON.read_text(encoding="utf-8"))

CONC, STEEL = HA35, B500SD
FYD = STEEL.fyd
FYWD = 0.8 * STEEL.fyk               # 400 MPa: NOTA to A19.6.2.3(3) when (6.10.a) nu1 = 0.6 is used
NU1 = 0.6                            # (6.10.a), fck <= 60
NU_T_CE = 0.6 * (1 - CONC.fck / 250)  # A19.6.3.2(4) -> 6.2.2(6): 0.516 (CYPE uses 0.6)
COT_MIN, COT_MAX = 0.5, 2.0          # (6.7N), Spanish values
W_MAX = 0.1                          # CE Art. 27 Tabla 27.2, XS3, RC, quasi-permanent
K1_SIGC, K2_SIGC, K3_SIGS = 0.6, 0.45, 0.8   # A19.7.2(2), (3), (5)
PHI_CREEP = 2.0                      # phi(inf, 28 d) assumed (Figura A19.3.1, outdoor, h0 ~ 300 mm)
S_LONG_MAX = 350.0                   # A19.9.2.3(4) (CYPE applies it to every beam, C17)
BAR_PENALTY = 0.002                  # search objective: As·(1 + 0.002·n_bars): weight, fewer bars on ties
ALPHA_E = STEEL.Es / CONC.Ecm        # 6.52 (HA-35 limestone)
EDGE_HW = {0: 0.40, 6: 0.40}         # half widths of the supports of the edge beams (end beams)
INNER_HW = 0.25


# ============================================================================================
# cases
# ============================================================================================
@dataclass(frozen=True)
class Case:
    name: str
    basis: str                       # "CYPE" | "ROM" (esfuerzos.BASES)
    mode: Mode
    psi2_qa: float
    tb_psi2: float = 0.0
    cot: str = "opt"                 # "1": theta = 45 deg (CYPE) | "opt": largest cot in [0.5, 2]
    nu_torsion: float = NU_T_CE
    hanger: bool = True              # links also carry the plates hung from the ledges (A19.6.2.1(9))
    final: bool = False
    note: str = ""


CASES = (
    Case("CYPE", "CYPE", Mode.CYPE, 0.3, cot="1", nu_torsion=0.6, hanger=False,
         note="parity with Anejo 10: Mode.CYPE, psi0,Qa = 0.7, psi2,Qa = 0.3, theta = 45 deg "
              "(suspension steel A19.6.2.1(9) reported as information, CYPE does not check it)"),
    Case("CE-CYPE", "CYPE", Mode.CODIGO, 0.3,
         note="code-strict section with the Anejo 10 load assumptions (psi2,Qa = 0.3)"),
    Case("CE-ROM", "ROM", Mode.CODIGO, 0.8, final=True,
         note="FINAL DESIGN: code-strict, ROM 2.0-11 (psi0,Qa = 1.0, psi2,Qa = 0.8, bollard psi2 = 0), XS3 0.1 mm"),
)


def case_combos(case: Case) -> dict:
    return {"uls": E.uls(case.basis), "qp": E.quasi_permanent(case.psi2_qa, case.tb_psi2),
            "qp_sens": E.quasi_permanent(case.psi2_qa, 0.5) if case.tb_psi2 == 0 else {},
            "char": {k: v for k, v in E.combos(False, "CYPE").items() if k.startswith("ELS")},
            "pp": {"PP": (1.0, 0, 0, 0, 0, 0)}}


# ============================================================================================
# helpers
# ============================================================================================
def _f(x, nd: int = 3):
    if x is None:
        return None
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    x = float(x)
    if math.isinf(x) or math.isnan(x):
        return None
    return round(x, nd)


def _eta(demand: float, capacity: float) -> float:
    return abs(demand) / capacity if capacity > 0 else math.inf


def _row(case: Case, member: str, section: str, pos, check: str, clause: str, demand, capacity, eta,
         combo: str = "", unit: str = "", in_verdict: bool = True, **extra) -> dict:
    ok = None if eta is None else bool(eta <= 1.0 + 1e-9)
    r = {"case": case.name, "member": member, "section": section, "pos_m": _f(pos, 3), "check": check,
         "clause": clause, "demand": _f(demand, 3), "capacity": _f(capacity, 3), "unit": unit,
         "eta": _f(eta, 4), "ok": ok, "combo": combo, "in_verdict": in_verdict}
    r.update({k: (_f(v, 4) if isinstance(v, (float, np.floating)) else v) for k, v in extra.items()})
    return r


# ============================================================================================
# members and stations
# ============================================================================================
@dataclass
class Face:
    name: str
    pos: float                       # m (global y for transverse beams, x for edge beams)
    dir: int                         # direction into the member region (for 'd from the face')
    limit: float                     # far end of the region (other face or free end)
    kind: str                        # "support" (span side) | "cantilever"


@dataclass
class Member:
    key: str
    kind: str                        # "transverse" | "edge"
    label: str
    group: str                       # "inner" | "end" | "edge"
    stations: list
    faces: list
    spans: list                      # (name, a, b) regions between faces for the max sagging / deflection
    axis_pos: list                   # (name, pos) pile axes (information)
    torsion_verdict: bool = True     # False: compatibility torsion (A19.6.3.1(2)), reported as information


def transverse_member(axis: int, stations: list) -> Member:
    r = AV.provided(axis)
    faces = [Face("cara pilote mar - voladizo", -0.20, -1, -0.50, "cantilever"),
             Face("cara pilote mar - vano", 0.20, +1, 3.25, "support"),
             Face("cara pilote tierra - vano", 3.25, -1, 0.20, "support"),
             Face("cara pilote tierra - vuelo", 3.65, +1, 3.80, "cantilever")]
    end = axis in (1, 7)
    return Member(r.member, "transverse", r.label, "end" if end else "inner", stations, faces,
                  [("vano", 0.20, 3.25)], [("eje pilote mar", 0.0), ("eje pilote tierra", 3.45)],
                  torsion_verdict=end)


def edge_member(portico: int, stations: list) -> Member:
    r = AV.provided_edge(portico)
    xs = E.tm.AXES_X
    faces, spans = [], []
    for k in range(len(xs) - 1):
        a = xs[k] + (0.40 if k == 0 else INNER_HW)
        b = xs[k + 1] - (0.40 if k == len(xs) - 2 else INNER_HW)
        faces += [Face(f"tramo {k + 1} cara izq. (X={a:.2f})", a, +1, b, "support"),
                  Face(f"tramo {k + 1} cara der. (X={b:.2f})", b, -1, a, "support")]
        spans.append((f"tramo {k + 1}", a, b))
    return Member(r.member, "edge", r.label, "edge", stations, faces, spans, [], torsion_verdict=False)


def build_members(data: dict | None = None) -> tuple[list[Member], dict]:
    data = data or E.load_stations()
    members = [transverse_member(a, data["beams"][a]) for a in range(1, 8)]
    members += [edge_member(p, data["edges"][p]) for p in (1, 10)]
    reinf = {m.key: (AV.provided(int(m.key[2:])) if m.kind == "transverse"
                     else AV.provided_edge(1 if m.key == "VBM" else 10)) for m in members}
    for m in members:                  # a face without an output station would be skipped silently
        for f in m.faces + [Face(n, p, 0, p, "axis") for n, p in m.axis_pos]:
            if not at(m.stations, f.pos):
                raise ValueError(f"{m.key}: no SAP output station at {f.name} (pos {f.pos})")
    return members, reinf


def at(stations: list, pos: float, tol: float = 1e-4, rigid: bool | None = None) -> list:
    return [s for s in stations if abs(s.pos - pos) <= tol and (rigid is None or s.rigid == rigid)]


def interp(stations: list, pos: float) -> list[dict]:
    """Pattern values interpolated at ``pos`` inside every non-rigid frame that spans it."""
    out = []
    frames: dict = {}
    for s in stations:
        if not s.rigid:
            frames.setdefault(s.frame, []).append(s)
    for sts in frames.values():
        sts = sorted(sts, key=lambda s: s.pos)
        if not (sts[0].pos - 1e-9 <= pos <= sts[-1].pos + 1e-9):
            continue
        for a, b in zip(sts[:-1], sts[1:]):
            if a.pos - 1e-9 <= pos <= b.pos + 1e-9:
                t = 0.0 if b.pos == a.pos else (pos - a.pos) / (b.pos - a.pos)
                out.append({p: {c: a.values[p][c] + t * (b.values[p][c] - a.values[p][c]) for c in E.COMPS_BEAM}
                            for p in E.PATTERNS})
                break
    return out


def combos_on(values_list: list[dict], combos: dict) -> list[tuple[str, dict]]:
    return [(name, E.combine(v, fac, E.COMPS_BEAM)) for v in values_list for name, fac in combos.items()]


def env(values_list: list[dict], combos: dict, comp: str, sign: int) -> tuple[float, str]:
    """Largest value of sign·comp (sign +1: max, -1: min, 0: max |comp|) -> (value, combo)."""
    best, name = 0.0, ""
    for nm, r in combos_on(values_list, combos):
        v = r[comp]
        key = abs(v) if sign == 0 else sign * v
        if key > (abs(best) if sign == 0 else sign * best) or not name:
            best, name = v, nm
    return best, name


def member_values(member: Member, a: float | None = None, b: float | None = None) -> list[tuple[float, dict]]:
    """(pos, values) of the non-rigid stations with a <= pos <= b."""
    out = []
    for s in member.stations:
        if s.rigid:
            continue
        if (a is not None and s.pos < a - 1e-6) or (b is not None and s.pos > b + 1e-6):
            continue
        out.append((s.pos, s.values))
    return out


def region_limits(member: Member) -> tuple[float, float]:
    return (-0.50, 3.80) if member.kind == "transverse" else (0.0, 39.0)


# ============================================================================================
# section resistance (cached)
# ============================================================================================
_CACHE: dict = {}


def _sig(r: BeamReinforcement) -> tuple:
    return (r.geom, tuple(r.groups))


def mrd(r: BeamReinforcement, mode: Mode, face: str) -> dict:
    """MRd [N·mm, positive] with ``face`` in tension (N = 0, horizontal neutral axis)."""
    key = ("mrd", _sig(r), mode, face)
    if key not in _CACHE:
        sec = r.section(mode)
        d = sec.capacity_uniaxial(0.0, +1 if face == "bottom" else -1)
        yv = sec.vy
        e0, kx, ky = d["plane"]
        x = (yv.max() - (-e0 / ky)) if face == "bottom" else ((-e0 / ky) - yv.min())
        _CACHE[key] = {"MRd": abs(d["Mx"]), "x": float(x), "eps_c": d["eps_c_max"], "Cc": d["Cc"],
                       "T": d["T"], "eps_s": d["eps_s_min"], "My": d["My"]}
    return _CACHE[key]


def as_required(r: BeamReinforcement, mode: Mode, face: str, M: float) -> float:
    """'Área Nec.' [mm2]: area of the ``face`` bar group alone (singly reinforced, CYPE C20)
    with MRd = |M| [N·mm]."""
    M = abs(M)
    if M < 1e3:
        return 0.0
    key = ("asreq", r.geom, tuple((g.xs, g.y) for g in r.face_groups(face)), mode, face, round(M, -3))
    if key in _CACHE:
        return _CACHE[key]
    xy = [r.geom.to_centroid(x, g.y) for g in r.face_groups(face) for x in g.xs]
    side = +1 if face == "bottom" else -1

    def mrd_of(As: float) -> float:
        bars = [Bar(x, y, 2 * math.sqrt(As / len(xy) / math.pi)) for x, y in xy]
        s = BeamSection("req", r.geom.rects, bars, r.concrete, r.steel, mode)
        return abs(s.capacity_uniaxial(0.0, side)["Mx"])
    lo, hi = 1.0, 3.0e4
    if mrd_of(lo) >= M:
        val = M / (0.9 * r.d(face) * FYD)
    elif mrd_of(hi) < M:
        val = math.inf
    else:
        val = brentq(lambda a: mrd_of(a) - M, lo, hi, xtol=0.01)
    _CACHE[key] = val
    return val


def as_min(r: BeamReinforcement, face: str, z_rule: str = "CE") -> float:
    """A19.9.2.1.1(1) (9.1): W/z · fctm,fl/fyd; z = 0.8h (CE) or 0.9d (CYPE, C14)."""
    z = 0.8 * r.geom.h if z_rule == "CE" else 0.9 * r.d(face)
    return r.geom.W(face) * CONC.fctm_fl(r.geom.h) / (z * FYD)


# ============================================================================================
# shear and torsion (A19.6.2, A19.6.3)
# ============================================================================================
def vrd_c(bw: float, d: float, Asl: float) -> dict:
    """(6.2.a/b), (6.3), sigma_cp = 0: CRd,c = 0.18/gc, k <= 2, rho_l <= 0.02, vmin = 0.035 k^1.5 fck^0.5."""
    k = min(1 + math.sqrt(200 / d), 2.0)
    rho = min(Asl / (bw * d), 0.02)
    v1 = 0.18 / CONC.gamma_c * k * (100 * rho * CONC.fck) ** (1 / 3) * bw * d
    vmin = 0.035 * k ** 1.5 * math.sqrt(CONC.fck) * bw * d
    return {"VRd_c": max(v1, vmin), "k": k, "rho_l": rho, "V1": v1, "Vmin": vmin}


def vrd_max(bw: float, z: float, cot: float, nu1: float = NU1) -> float:
    """(6.9): acw·bw·z·nu1·fcd/(cot + tan), acw = 1."""
    return bw * z * nu1 * CONC.fcd * cot / (1 + cot * cot)


def vrd_s(asw_s: float, z: float, cot: float, fywd: float = FYWD) -> float:
    """(6.8): Asw/s·z·fywd·cot(theta)."""
    return asw_s * z * fywd * cot


def thin_wall(r: BeamReinforcement) -> dict:
    """A19.6.3.2(1) on the web rectangle bw x h (ledges ignored, as CYPE): tef = A/u >= 2·(face to
    bar axis); Ak, uk of the wall centre line; TRd,c = 2·Ak·tef·fctd (tau = fctd)."""
    b, h = r.geom.bw, r.geom.h
    c_ax = min(r.cover_axis("top"), r.cover_axis("bottom"))
    tef = max(b * h / (2 * (b + h)), 2 * c_ax)
    Ak = (b - tef) * (h - tef)
    uk = 2 * ((b - tef) + (h - tef))
    return {"tef": tef, "Ak": Ak, "uk": uk, "TRd_c": 2 * Ak * tef * CONC.fctd, "bk": b - tef, "hk": h - tef}


def trd_max(tw: dict, cot: float, nu: float) -> float:
    """(6.30): 2·nu·acw·fcd·Ak·tef·sin(theta)·cos(theta)."""
    return 2 * nu * CONC.fcd * tw["Ak"] * tw["tef"] * cot / (1 + cot * cot)


def cot_theta(case: Case, bw: float, z: float, tw: dict, pairs: list[tuple[float, float]]) -> tuple[float, float]:
    """cot(theta) of the case: 1.0, or the largest value in [0.5, 2] with
    max(T/TRd,max + V/VRd,max) <= 1 over the (V [kN], T [kN·m]) pairs at the face.  Returns
    (cot, K) with K = max(T/(2 nu fcd Ak tef) + V/(bw z nu1 fcd)), interaction = K·(cot + 1/cot)."""
    K = max((abs(t) * KNM / (2 * case.nu_torsion * CONC.fcd * tw["Ak"] * tw["tef"])
             + abs(v) * 1e3 / (bw * z * NU1 * CONC.fcd)) for v, t in pairs) if pairs else 0.0
    if case.cot == "1":
        return 1.0, K
    if K <= 0:
        return COT_MAX, K
    inv = 1 / K
    if inv < 2:                               # crushing even at 45 deg: keep 45 deg (fails)
        return 1.0, K
    return min(COT_MAX, (inv + math.sqrt(inv * inv - 4)) / 2), K


# ============================================================================================
# serviceability (A19.7)
# ============================================================================================
def sls_section(r: BeamReinforcement, faces: tuple | None = None) -> BeamSection:
    return r.section(Mode.CODIGO, faces)


def mcr(r: BeamReinforcement, sagging: bool, fct: float | None = None, faces: tuple | None = None,
        alpha_e: float = ALPHA_E) -> float:
    return cracking_moment(sls_section(r, faces), alpha_e, CONC.fctm if fct is None else fct, sagging)


def crack_check(r: BeamReinforcement, M: float) -> dict:
    """Uncracked criterion (7.1(2)) and, if cracked, wk (7.3.4) for M [N·mm] (sagging +)."""
    sec = sls_section(r)
    face = "bottom" if M > 0 else "top"
    un = uncracked_stresses(sec, ALPHA_E, M)
    sig_ct = -min(un["top"], un["bot"])
    out = {"face": face, "M_kNm": M / KNM, "sigma_ct": sig_ct, "fctm": CONC.fctm,
           "fctm_fl": CONC.fctm_fl(r.geom.h), "cracked": sig_ct > CONC.fctm, "wk": 0.0}
    if not out["cracked"] or abs(M) < 1e3:
        return out
    cr = cracked_stresses(sec, ALPHA_E, M)
    names = {g.name for g in r.face_groups(face)}
    sig_s = max(-s for s, b in zip(cr["sig_s"], sec.bars) if b.tag in names)
    h, x = r.geom.h, cr["x"]
    hcef = min(2.5 * r.cover_axis(face), (h - x) / 3, h / 2)
    b_eff = r.geom.b_bottom if face == "bottom" else r.geom.b_top
    gs = r.face_groups(face)
    As = r.As(face)
    phi_eq = sum(g.n * g.phi ** 2 for g in gs) / sum(g.n * g.phi for g in gs)
    c = AV.COVER + r.stirrups.phi
    w = crack_width(sig_s, CONC, STEEL, As, b_eff * hcef, c, phi_eq, spacing=r.max_spacing(face), h=h, x=x)
    out.update({"x": x, "sigma_s": sig_s, "sigma_c": cr["sig_c"], "hc_ef": hcef, "Ac_eff": b_eff * hcef,
                "c": c, "phi_eq": phi_eq, "Icr": cr["Icr"], **w})
    return out


def stresses(r: BeamReinforcement, M: float) -> dict:
    """sigma_c (max compression) and sigma_s (max tension) under M [N·mm]; cracked section if
    the uncracked tension exceeds fctm."""
    sec = sls_section(r)
    un = uncracked_stresses(sec, ALPHA_E, M)
    if -min(un["top"], un["bot"]) <= CONC.fctm:
        return {"cracked": False, "sigma_c": max(un["top"], un["bot"]),
                "sigma_s": max(0.0, -min(un["bars"]))}
    cr = cracked_stresses(sec, ALPHA_E, M)
    return {"cracked": True, "sigma_c": cr["sig_c"], "sigma_s": max(0.0, -min(cr["sig_s"]))}


def curvature_props(r: BeamReinforcement, sagging: bool, E_eff: float) -> dict:
    ae = STEEL.Es / E_eff
    sec = sls_section(r)
    h = homogenised(sec, ae)
    Mcr = cracking_moment(sec, ae, CONC.fctm, sagging)
    cr = cracked_stresses(sec, ae, (1.0 if sagging else -1.0) * KNM)
    return {"I1": h["I"], "I2": cr["Icr"], "Mcr": Mcr, "E": E_eff}


def deflection(member: Member, r: BeamReinforcement, a: float, b: float, factors: tuple,
               phi: float, beta: float) -> dict:
    """Deflection relative to the chord between the faces a..b (A19.7.4.3 (7.18) interpolation,
    creep through Ec,eff = Ecm/(1 + phi)); M(y) from the SAP stations."""
    pts: dict = {}
    for pos, vals in member_values(member, a, b):
        pts.setdefault(round(pos, 4), []).append(E.combine(vals, factors, ("M",))["M"])
    ys = np.array(sorted(pts))
    Ms = np.array([np.mean(pts[y]) for y in sorted(pts)]) * KNM
    E_eff = CONC.Ecm / (1 + phi)
    props = {s: curvature_props(r, s, E_eff) for s in (True, False)}
    kap = []
    for M in Ms:
        p = props[M >= 0]
        k1, k2 = M / (p["E"] * p["I1"]), M / (p["E"] * p["I2"])
        zeta = 1 - beta * (p["Mcr"] / abs(M)) ** 2 if abs(M) > p["Mcr"] else 0.0
        kap.append(zeta * k2 + (1 - zeta) * k1)
    kap = np.array(kap)                               # 1/mm, sagging +
    y_mm = ys * 1000.0
    th = np.concatenate([[0.0], np.cumsum(np.diff(y_mm) * (kap[1:] + kap[:-1]) / 2)])
    w = np.concatenate([[0.0], np.cumsum(np.diff(y_mm) * (th[1:] + th[:-1]) / 2)])
    w_rel = w - (w[0] + (w[-1] - w[0]) * (y_mm - y_mm[0]) / (y_mm[-1] - y_mm[0]))
    i = int(np.argmin(w_rel))
    return {"f_mm": float(-w_rel[i]), "pos": float(ys[i]), "M_max_kNm": float(Ms.max() / KNM)}


def span_depth_limit(r: BeamReinforcement, K: float = 1.3) -> dict:
    """A19.7.4.2 (7.16.a/b), K = 1.3 (end span of a continuous member), sigma_s factor = 1."""
    d = r.d("bottom")
    rho0 = math.sqrt(CONC.fck) * 1e-3
    rho = r.As("bottom") / (r.geom.bw * d)
    rho_p = r.As("top") / (r.geom.bw * d)
    f = math.sqrt(CONC.fck)
    if rho <= rho0:
        lim = K * (11 + 1.5 * f * rho0 / rho + 3.2 * f * (rho0 / rho - 1) ** 1.5)
    else:
        net = rho - rho_p if rho - rho_p > 1e-4 else rho          # rho' >= rho: ignore rho' (conservative)
        lim = K * (11 + 1.5 * f * rho0 / net + f / 12 * math.sqrt(rho_p / rho0))
    return {"limit": lim, "rho": rho, "rho_p": rho_p, "d": d}


# ============================================================================================
# member checks
# ============================================================================================
def face_values(member: Member, f: Face, d_m: float) -> dict:
    """Station values at the face (all frames meeting there) and at d from the face."""
    at_face = [s.values for s in at(member.stations, f.pos)]
    y_d = f.pos + f.dir * d_m
    if f.kind == "cantilever" or (y_d - f.limit) * f.dir > 0:      # cantilevers shorter than d
        vals_d, y_used = at_face, f.pos
    else:
        vals_d, y_used = interp(member.stations, y_d), y_d
    return {"face": at_face, "d": vals_d, "y_d": y_used}


def bending_rows(case: Case, member: Member, r: BeamReinforcement, uls: dict) -> list[dict]:
    rows = []
    sections = [(f.name, f.pos, [s.values for s in at(member.stations, f.pos)], True) for f in member.faces]
    for name, a, b in member.spans:
        best = max(((E.combine(v, fac, ("M",))["M"], pos, v) for pos, v in member_values(member, a, b)
                    for fac in uls.values()), key=lambda t: t[0])
        sections.append((f"{name}: máx. positivo", best[1], [best[2]], True))
    for name, pos in member.axis_pos:
        sections.append((name + " (info, nudo rígido)", pos, [s.values for s in at(member.stations, pos)], False))
    for name, pos, vals, verdict in sections:
        for face, sign in (("bottom", +1), ("top", -1)):
            M, combo = env(vals, uls, "M", sign)
            if sign * M <= 0.5:
                continue
            cap = mrd(r, case.mode, face)
            As_req = as_required(r, case.mode, face, M * KNM)
            rows.append(_row(case, member.key, name, pos, f"MEd <= MRd ({'sag' if sign > 0 else 'hog'})",
                             "A19.6.1", M, cap["MRd"] / KNM, _eta(M * KNM, cap["MRd"]), combo, "kN·m",
                             in_verdict=verdict, face=face, As_req_cm2=As_req / 100,
                             As_prov_cm2=r.As(face) / 100, x_mm=cap["x"]))
    return rows


def shear_torsion_rows(case: Case, member: Member, r: BeamReinforcement, uls: dict) -> list[dict]:
    rows = []
    d = min(r.d("top"), r.d("bottom"))
    z = 0.9 * d
    bw = r.geom.bw
    tw = thin_wall(r)
    st = r.stirrups
    Asl = min(r.As("top"), r.As("bottom"))
    vc = vrd_c(bw, d, Asl)
    for f in member.faces:
        fv = face_values(member, f, d / 1000.0)
        cf = combos_on(fv["face"], uls)
        cd = combos_on(fv["d"], uls)
        cot, K = cot_theta(case, bw, z, tw, [(v["V"], v["T"]) for _, v in cf])
        vmax = vrd_max(bw, z, cot)
        tmax = trd_max(tw, cot, case.nu_torsion)
        # V at the face vs VRd,max
        nm, vf = max(cf, key=lambda t: abs(t[1]["V"]))
        rows.append(_row(case, member.key, f.name, f.pos, "VEd(cara) <= VRd,max", "A19.6.2.3(3) (6.9)",
                         abs(vf["V"]), vmax / 1e3, _eta(vf["V"] * 1e3, vmax), nm, "kN", cot_theta=cot, z_mm=z))
        # V at d vs VRd,s (shear only)
        nm_d, vd = max(cd, key=lambda t: abs(t[1]["V"]))
        vs = vrd_s(st.asw_s, z, cot)
        rows.append(_row(case, member.key, f.name, fv["y_d"], "VEd(d) <= VRd,s", "A19.6.2.3(3) (6.8), 6.2.1(8)",
                         abs(vd["V"]), vs / 1e3, _eta(vd["V"] * 1e3, vs), nm_d, "kN", cot_theta=cot,
                         Asw_s_req_cm2_m=abs(vd["V"]) * 1e3 / (z * FYWD * cot) * 10,
                         Asw_s_prov_cm2_m=st.asw_s * 10, VRd_c=vc["VRd_c"] / 1e3,
                         al_mm=z * cot / 2, dFtd_kN=0.5 * abs(vd["V"]) * cot))
        rows.append(_row(case, member.key, f.name, fv["y_d"], "VEd(d) <= VRd,c (info: links needed?)",
                         "A19.6.2.2(1) (6.2)", abs(vd["V"]), vc["VRd_c"] / 1e3, _eta(vd["V"] * 1e3, vc["VRd_c"]),
                         nm_d, "kN", in_verdict=False))
        # V at d + suspension of the plates bearing on the ledges (A19.6.2.1(9)), all links
        if member.kind == "transverse":
            def need_vh(t):
                return abs(t[1]["V"]) * 1e3 / (z * FYWD * cot) + hanger_asw(member, uls[t[0]], fv["y_d"])
            nm_h, vh = max(cd, key=need_vh)
            ash = hanger_asw(member, uls[nm_h], fv["y_d"])
            req = need_vh((nm_h, vh))
            rows.append(_row(case, member.key, f.name, fv["y_d"], "estribos V + suspensión alveoplaca (todas las ramas)",
                             "A19.6.2.3(3) (6.8) + A19.6.2.1(9)", req * 10, st.asw_s * 10, req / st.asw_s, nm_h,
                             "cm²/m", in_verdict=case.hanger, V_kN=vh["V"], Asw_V_cm2_m=(req - ash) * 10,
                             Asw_hanger_cm2_m=ash * 10, hanger_kN_m=ash * FYD, cot_theta=cot))
        # torsion: interaction at the face (6.29)
        best = max(cf, key=lambda t: abs(t[1]["T"]) * 1e6 / tmax + abs(t[1]["V"]) * 1e3 / vmax)
        eta29 = abs(best[1]["T"]) * KNM / tmax + abs(best[1]["V"]) * 1e3 / vmax
        tv = member.torsion_verdict
        rows.append(_row(case, member.key, f.name, f.pos, "TEd/TRd,max + VEd/VRd,max <= 1", "A19.6.3.2(4) (6.29)",
                         abs(best[1]["T"]), tmax / KNM, eta29, best[0], "kN·m", in_verdict=tv, cot_theta=cot,
                         nu=case.nu_torsion, V_kN=best[1]["V"], T_over_TRdmax=abs(best[1]["T"]) * KNM / tmax))
        best = max(cf, key=lambda t: abs(t[1]["T"]) * KNM / tw["TRd_c"] + abs(t[1]["V"]) * 1e3 / vc["VRd_c"])
        e31 = abs(best[1]["T"]) * KNM / tw["TRd_c"] + abs(best[1]["V"]) * 1e3 / vc["VRd_c"]
        rows.append(_row(case, member.key, f.name, f.pos, "TEd/TRd,c + VEd/VRd,c <= 1 (info: only min. links?)",
                         "A19.6.3.2(5) (6.31)", abs(best[1]["T"]), tw["TRd_c"] / KNM, e31, best[0], "kN·m",
                         in_verdict=False, T_over_TRdc=abs(best[1]["T"]) * KNM / tw["TRd_c"]))
        # links: V (+ suspension, CE cases) + T per leg of the hoop at the section d
        def need(t):
            nm_, v = t
            asw_v = abs(v["V"]) * 1e3 / (z * FYWD * cot)
            if case.hanger:
                asw_v += hanger_asw(member, uls[nm_], fv["y_d"])
            ast = abs(v["T"]) * KNM / (2 * tw["Ak"] * FYD * cot)
            return asw_v, ast
        nm_l, vl = max(cd, key=lambda t: need(t)[0] / st.legs + need(t)[1])
        asw_v, ast = need((nm_l, vl))
        rows.append(_row(case, member.key, f.name, fv["y_d"], "estribos V + T (por rama del cerco)",
                         "A19.6.2.3(3) (6.8) + A19.6.3.2(3)" + (" + A19.6.2.1(9)" if case.hanger else ""),
                         (asw_v / st.legs + ast) * 1e3 / 100,
                         st.leg_s * 1e3 / 100, (asw_v / st.legs + ast) / st.leg_s, nm_l, "cm²/m·rama",
                         in_verdict=tv, total_req_cm2_m=(asw_v + 2 * ast) * 10, total_prov_cm2_m=st.asw_s * 10,
                         eta_total_cype=(asw_v + 2 * ast) / st.asw_s, T_kNm=vl["T"], V_kN=vl["V"]))
        # longitudinal torsion steel added to the bending tension chord (6.28)
        worst = None
        for nm, v in cf:
            if abs(v["T"]) < 1e-6:
                continue
            face = "bottom" if v["M"] > 0 else "top"
            sAsl = abs(v["T"]) * KNM * tw["uk"] * cot / (2 * tw["Ak"] * FYD)
            e = abs(v["M"]) * KNM / mrd(r, case.mode, face)["MRd"] + sAsl * tw["bk"] / tw["uk"] / r.As(face)
            if worst is None or e > worst[0]:
                worst = (e, nm, v, sAsl, face)
        if worst:
            e, nm, v, sAsl, face = worst
            rows.append(_row(case, member.key, f.name, f.pos, "M/MRd + ΣAsl,T(cordón)/As <= 1",
                             "A19.6.3.2(3) (6.28)", abs(v["T"]), None, e, nm, "kN·m", in_verdict=tv, face=face,
                             sum_Asl_T_cm2=sAsl / 100, M_kNm=v["M"],
                             Tsl_ratio_cype=sAsl / sum(g.As for g in r.groups)))
        if member.group == "end" and f.kind == "support":
            rows += ledge_torsion_rows(case, member, r, f, cf, cd, uls, cot, z, tw, vmax)
    return rows


# Plates bearing on the single ledge of the end beams (not modelled in SAP nor, per P437, in CYPE)
PLATE_SPAN_END = E.tm.AXIS_SPACING - E.tm.PLATE_X_END - E.tm.PLATE_GAP_INNER        # 5.787 m
LEDGE_BEARING_X = (E.tm.PLATE_X_END + E.tm.END_WEB_INSIDE + 0.15) / 2              # 0.4175 m from the pile axis
PLATE_LOADS = {"PP": E.tm.Q_SLAB_PP, "CM": E.tm.Q_CM, "Qa": E.tm.Q_SCU}           # kN/m2


def plate_spans(axis: int) -> list[float]:
    """Spans [m] of the hollow-core plates bearing on the ledge(s) of the beam of ``axis``: one
    bay each side (5.854 m inner bays, 5.787 m end bays); end frames one side only."""
    regs = E.tm.plate_regions()
    k = axis - 1
    return [regs[i][1] - regs[i][0] for i in (k - 1, k) if 0 <= i < len(regs)]


def hanger_load(axis: int, factors: tuple) -> float:
    """Plate reactions on the ledges of the beam of ``axis`` [kN/m] for one combination:
    q·Lp/2 per bearing ledge, q = factored PP(plates) + CM + Qa on the plates."""
    q = sum(f * PLATE_LOADS[p] for f, p in zip(factors, E.PATTERNS) if p in PLATE_LOADS)
    return q * sum(plate_spans(axis)) / 2


def hanger_asw(member: "Member", factors: tuple, y: float) -> float:
    """A19.6.2.1(9): vertical steel [mm2/mm] carrying the ledge load to the top of the section,
    'in addition to any reinforcement required to resist shear' (fyd, pure tension).  Zero for
    the edge beams and outside the plates (land cantilever beyond Y = 3.603)."""
    if member.kind != "transverse" or not (E.tm.PLATE_Y[0] - 1e-9 <= y <= E.tm.PLATE_Y[1] + 1e-9):
        return 0.0
    return hanger_load(int(member.key[2:]), factors) / FYD          # kN/m = N/mm


def ledge_torsion(factors: tuple, span: float = 3.05) -> float:
    """Equilibrium torque [kN·m] at a pile face of an end beam from the hollow-core plates bearing
    on the ledge: r = q·Lp/2 per m at e = 0.4175 m from the beam axis (pile axis), t = r·e
    resisted by the two piles: T = t·L/2 (L = clear span between pile faces)."""
    q = sum(f * PLATE_LOADS[p] for f, p in zip(factors, E.PATTERNS) if p in PLATE_LOADS)
    return q * PLATE_SPAN_END / 2 * LEDGE_BEARING_X * span / 2


def ledge_torsion_rows(case: Case, member: Member, r: BeamReinforcement, f: Face, cf: list, cd: list,
                       uls: dict, cot: float, z: float, tw: dict, vmax: float) -> list[dict]:
    """Sensitivity (not in the verdict): SAP torque + ledge-bearing torque of the same combination."""
    rows, tag = [], " [sensibilidad: alveoplaca apoyada en el ala, e = 0.42 m]"
    st = r.stirrups
    tmax = trd_max(tw, cot, case.nu_torsion)
    worst = [None, None, None]
    dmap: dict = {}
    for nm, vd in cd:
        if nm not in dmap or abs(vd["V"]) > abs(dmap[nm]["V"]):
            dmap[nm] = vd
    for nm, v in cf:
        vd = dmap.get(nm, v)
        Tadd = ledge_torsion(uls[nm])
        Tf = abs(v["T"]) + Tadd
        Td = abs(vd["T"]) + Tadd
        e29 = Tf * KNM / tmax + abs(v["V"]) * 1e3 / vmax
        asw_v = abs(vd["V"]) * 1e3 / (z * FYWD * cot)
        if case.hanger:
            asw_v += hanger_asw(member, uls[nm], f.pos)
        ast = Td * KNM / (2 * tw["Ak"] * FYD * cot)
        eleg = (asw_v / st.legs + ast) / st.leg_s
        face = "bottom" if v["M"] > 0 else "top"
        sAsl = Tf * KNM * tw["uk"] * cot / (2 * tw["Ak"] * FYD)
        ech = abs(v["M"]) * KNM / mrd(r, case.mode, face)["MRd"] + sAsl * tw["bk"] / tw["uk"] / r.As(face)
        for i, (e, extra) in enumerate(((e29, {"T_kNm": Tf, "T_add_kNm": Tadd}), (eleg, {"T_kNm": Td, "T_add_kNm": Tadd}),
                                        (ech, {"T_kNm": Tf, "T_add_kNm": Tadd, "sum_Asl_T_cm2": sAsl / 100,
                                               "face": face, "M_kNm": v["M"]}))):
            if worst[i] is None or e > worst[i][0]:
                worst[i] = (e, nm, extra)
    for (e, nm, extra), chk, cl in zip(worst, ("TEd/TRd,max + VEd/VRd,max <= 1", "estribos V + T (por rama del cerco)",
                                               "M/MRd + ΣAsl,T(cordón)/As <= 1"),
                                       ("A19.6.3.2(4) (6.29)", "A19.6.2.3(3) + A19.6.3.2(3)", "A19.6.3.2(3) (6.28)")):
        rows.append(_row(case, member.key, f.name, f.pos, chk + tag, cl, extra["T_kNm"], None, e, nm, "kN·m",
                         in_verdict=False, cot_theta=cot, **extra))
    return rows


def detailing_rows(case: Case, member: Member, r: BeamReinforcement) -> list[dict]:
    rows = []
    g = r.geom
    for face in ("top", "bottom"):
        As = r.As(face)
        for rule in ("CE", "CYPE"):
            amin = as_min(r, face, rule)
            rows.append(_row(case, member.key, "todas", None, f"As({face}) >= As,min (z {'0.8h' if rule == 'CE' else '0.9d'})",
                             "A19.9.2.1.1(1) (9.1)", amin / 100, As / 100, amin / As, "", "cm²",
                             in_verdict=(rule == "CE"), W_cm3=g.W(face) / 1e3))
        rows.append(_row(case, member.key, "todas", None, f"As({face}) <= As,max = 0.04 Ac", "A19.9.2.1.1(3)",
                         As / 100, 0.04 * g.Ac / 100, As / (0.04 * g.Ac), "", "cm²"))
        smin = AV.smin_clear(r.phi_max(face))
        sc = r.clear_spacing(face)
        rows.append(_row(case, member.key, "todas", None, f"separación libre ({face}) >= smin", "A19.8.2(2)",
                         smin, sc, smin / sc, "", "mm"))
        sm = r.max_spacing(face)
        rows.append(_row(case, member.key, "todas", None, f"separación ({face}) <= 350 mm", "A19.9.2.3(4) (C17)",
                         sm, S_LONG_MAX, sm / S_LONG_MAX, "", "mm"))
    st = r.stirrups
    d = min(r.d("top"), r.d("bottom"))
    rho_min = 0.08 * math.sqrt(CONC.fck) / STEEL.fyk
    rho_w = st.asw_s / g.bw
    tw = thin_wall(r)
    rows += [
        _row(case, member.key, "todas", None, "rho_w >= rho_w,min", "A19.9.2.2(5) (9.4)(9.5)",
             rho_min * g.bw * 10, st.asw_s * 10, rho_min / rho_w, "", "cm²/m"),
        _row(case, member.key, "todas", None, "s <= sl,max = 0.75d", "A19.9.2.2(6) (9.6)",
             st.s, 0.75 * d, st.s / (0.75 * d), "", "mm"),
        _row(case, member.key, "todas", None, "st <= st,max = 0.75d <= 600", "A19.9.2.2(8) (9.8)",
             st.st(g), min(0.75 * d, 600.0), st.st(g) / min(0.75 * d, 600.0), "", "mm"),
        _row(case, member.key, "todas", None, "s <= uk/8, min(b, h) (torsión)", "A19.9.2.3(3)",
             st.s, min(tw["uk"] / 8, g.bw, g.h), st.s / min(tw["uk"] / 8, g.bw, g.h), "", "mm",
             in_verdict=member.torsion_verdict),
    ]
    return rows


def sls_rows(case: Case, member: Member, r: BeamReinforcement, cc: dict) -> list[dict]:
    rows = []
    a, b = region_limits(member)
    vals = member_values(member, a, b)

    def worst(combos, sign):
        best = None
        for pos, v in vals:
            for nm, fac in combos.items():
                M = E.combine(v, fac, ("M",))["M"]
                if best is None or sign * M > sign * best[0]:
                    best = (M, pos, nm)
        return best
    for sens, combos in ((False, cc["qp"]), (True, cc["qp_sens"])):
        if not combos:
            continue
        for sign in (+1, -1):
            M, pos, nm = worst(combos, sign)
            if sign * M <= 0.1:
                continue
            ck = crack_check(r, M * KNM)
            tag = " [sensibilidad TB psi2 = 0.5]" if sens else ""
            rows.append(_row(case, member.key, "sag" if sign > 0 else "hog", pos,
                             "sigma_ct <= fctm (QP)" + tag, "A19.7.1(2)", ck["sigma_ct"], ck["fctm"],
                             ck["sigma_ct"] / ck["fctm"], nm, "MPa", in_verdict=False, M_kNm=M,
                             sigma_ct_over_fctm_fl=ck["sigma_ct"] / ck["fctm_fl"]))
            rows.append(_row(case, member.key, "sag" if sign > 0 else "hog", pos, "wk <= 0.1 mm (XS3, QP)" + tag,
                             "A19.7.3.4 + CE Art. 27 Tabla 27.2", ck["wk"], W_MAX, ck["wk"] / W_MAX, nm, "mm",
                             in_verdict=not sens, M_kNm=M, cracked=ck["cracked"],
                             sigma_s=ck.get("sigma_s"), sr_max=ck.get("sr_max"), x_mm=ck.get("x"),
                             rho_p_eff=ck.get("rho_p_eff"), rule=ck.get("rule")))
    # stresses: characteristic (ELS01-08) and quasi-permanent concrete
    for label, combos, checks in (("característica ELS01-08", cc["char"], ("c", "s")), ("QP", cc["qp"], ("cqp",))):
        for sign in (+1, -1):
            M, pos, nm = worst(combos, sign)
            if sign * M <= 0.1:
                continue
            s = stresses(r, M * KNM)
            for c in checks:
                if c == "c":
                    rows.append(_row(case, member.key, "sag" if sign > 0 else "hog", pos, "sigma_c <= 0.6 fck (" + label + ")",
                                     "A19.7.2(2)", s["sigma_c"], K1_SIGC * CONC.fck, s["sigma_c"] / (K1_SIGC * CONC.fck),
                                     nm, "MPa", M_kNm=M, cracked=s["cracked"]))
                elif c == "s":
                    rows.append(_row(case, member.key, "sag" if sign > 0 else "hog", pos, "sigma_s <= 0.8 fyk (" + label + ")",
                                     "A19.7.2(5)", s["sigma_s"], K3_SIGS * STEEL.fyk, s["sigma_s"] / (K3_SIGS * STEEL.fyk),
                                     nm, "MPa", M_kNm=M, cracked=s["cracked"]))
                else:
                    rows.append(_row(case, member.key, "sag" if sign > 0 else "hog", pos,
                                     "sigma_c <= 0.45 fck (QP, fluencia lineal)", "A19.7.2(3)", s["sigma_c"],
                                     K2_SIGC * CONC.fck, s["sigma_c"] / (K2_SIGC * CONC.fck), nm, "MPa",
                                     in_verdict=False, M_kNm=M))
    return rows


def deflection_rows(case: Case, member: Member, r: BeamReinforcement, cc: dict) -> list[dict]:
    rows = []
    qp_name, qp = next(iter(cc["qp"].items()))
    for name, a, b in member.spans:
        L = (b - a) * 1000.0
        fT = deflection(member, r, a, b, qp, PHI_CREEP, 0.5)
        f0 = deflection(member, r, a, b, qp, 0.0, 1.0)
        fg = deflection(member, r, a, b, cc["pp"]["PP"], 0.0, 1.0)
        fA = fT["f_mm"] - fg["f_mm"]
        rows.append(_row(case, member.key, name, fT["pos"], "f total (QP, fluencia) <= L/250", "A19.7.4.1(4)",
                         fT["f_mm"], L / 250, fT["f_mm"] / (L / 250), qp_name, "mm", L_m=L / 1000,
                         f_inst_QP=f0["f_mm"], phi=PHI_CREEP))
        rows.append(_row(case, member.key, name, fT["pos"], "f activa (f total - f inst. PP) <= L/500", "A19.7.4.1(5)",
                         fA, L / 500, fA / (L / 500), qp_name, "mm", L_m=L / 1000))
        sd = span_depth_limit(r)
        rows.append(_row(case, member.key, name, None, "L/d <= (L/d)lim", "A19.7.4.2 (7.16), K = 1.3",
                         L / sd["d"], sd["limit"], L / sd["d"] / sd["limit"], "", "-", in_verdict=False, rho=sd["rho"]))
    return rows


def as_table_rows(case: Case, member: Member, r: BeamReinforcement, bending: list[dict]) -> list[dict]:
    rows = []
    for b in bending:
        if b["member"] != member.key or b["case"] != case.name:
            continue
        face = b["face"]
        amin = as_min(r, face, "CE") / 100
        As_uls = b["As_req_cm2"] if b["As_req_cm2"] is not None else math.inf
        req = max(As_uls, amin) if b["in_verdict"] else As_uls
        rows.append({"case": case.name, "member": member.key, "section": b["section"], "pos_m": b["pos_m"],
                     "face": face, "MEd_kNm": b["demand"], "combo": b["combo"], "As_uls_cm2": b["As_req_cm2"],
                     "As_min_cm2": _f(amin, 2), "As_req_cm2": _f(req, 2), "As_prov_cm2": b["As_prov_cm2"],
                     "req_over_prov": _f(req / b["As_prov_cm2"], 3), "in_verdict": b["in_verdict"]})
    return rows


def check_member(case: Case, member: Member, r: BeamReinforcement, cc: dict | None = None) -> dict:
    cc = cc or case_combos(case)
    t = {"bending": bending_rows(case, member, r, cc["uls"]),
         "shear_torsion": shear_torsion_rows(case, member, r, cc["uls"]),
         "detailing": detailing_rows(case, member, r),
         "sls": sls_rows(case, member, r, cc),
         "deflection": deflection_rows(case, member, r, cc)}
    t["as_required"] = as_table_rows(case, member, r, t["bending"])
    return t


FAMILIES = {
    "flexión ELU": ("MEd <= MRd",),
    "cortante": ("VEd(cara) <= VRd,max", "VEd(d) <= VRd,s", "estribos V + suspensión"),
    "torsión": ("TEd/TRd,max", "estribos V + T", "M/MRd + ΣAsl"),
    "disposiciones": ("As(", "separación", "rho_w", "s <= ", "st <= "),
    "fisuración ELS": ("wk <=",),
    "tensiones ELS": ("sigma_c <= 0.6", "sigma_s <="),
    "flecha": ("f total", "f activa"),
}


FAMILIES_INFO = {   # reported, not in the verdict
    "torsión [info]": (("TEd/TRd,max", "estribos V + T", "M/MRd + ΣAsl"), False),
    "torsión ala [sensib.]": (("TEd/TRd,max", "estribos V + T", "M/MRd + ΣAsl"), True),
    "fisuración TB 0.5 [sensib.]": (("wk <=",), True),
}


def summarise(rows: list[dict]) -> dict:
    out = {}
    for fam, keys in FAMILIES.items():
        sel = [r for r in rows if r["in_verdict"] and r["eta"] is not None and any(r["check"].startswith(k) for k in keys)]
        if not sel:
            continue
        w = max(sel, key=lambda r: r["eta"])
        out[fam] = {"eta": w["eta"], "ok": w["eta"] <= 1 + 1e-9, "check": w["check"], "section": w["section"],
                    "combo": w["combo"]}
    out["verdict"] = "CUMPLE" if all(v["ok"] for v in out.values()) else "NO CUMPLE"
    for fam, (keys, sens) in FAMILIES_INFO.items():
        sel = [r for r in rows if not r["in_verdict"] and r["eta"] is not None and (("sensibilidad" in r["check"]) == sens)
               and any(r["check"].startswith(k) for k in keys)]
        if sel:
            w = max(sel, key=lambda r: r["eta"])
            out[fam] = {"eta": w["eta"], "ok": None, "check": w["check"], "section": w["section"], "combo": w["combo"],
                        "info": True}
    return out


# ============================================================================================
# psi2 threshold (quasi-permanent Qa factor at which the provided layout stops passing)
# ============================================================================================
def psi2_threshold(member: Member, r: BeamReinforcement, sign: int) -> dict:
    """psi2,Qa (bollard psi2 = 0) at which the ``sign`` face first cracks (fctm, fctm,fl) and
    first fails wk <= 0.1 mm; None if it still passes at psi2 = 1."""
    a, b = region_limits(member)
    vals = member_values(member, a, b)

    def Mq(psi):
        return max(sign * E.combine(v, (1.0, 1.0, psi, 0.0, 0.0, 0.0), ("M",))["M"] for _, v in vals) * sign

    def cracked(psi):
        return crack_check(r, Mq(psi) * KNM)["sigma_ct"] > CONC.fctm

    def fails(psi):
        return crack_check(r, Mq(psi) * KNM)["wk"] > W_MAX

    def fl(psi):
        return crack_check(r, Mq(psi) * KNM)["sigma_ct"] > CONC.fctm_fl(r.geom.h)

    def bis(fun):
        if fun(0.0):
            return 0.0
        if not fun(1.0):
            return None
        return _bisect(fun)
    return {"member": member.key, "face": "bottom" if sign > 0 else "top", "psi2_crack_fctm": _f(bis(cracked), 3),
            "psi2_crack_fctm_fl": _f(bis(fl), 3), "psi2_wk_fail": _f(bis(fails), 3),
            "M_qp_03": _f(Mq(0.3), 2), "M_qp_08": _f(Mq(0.8), 2),
            "Mcr_kNm": _f(mcr(r, sign > 0) / KNM, 2)}


def _bisect(fun, lo: float = 0.0, hi: float = 1.0, tol: float = 1e-4) -> float:
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if fun(mid) else (mid, hi)
    return (lo + hi) / 2


# ============================================================================================
# reinforcement search (D5)
# ============================================================================================
def _group_demands(members: list[Member], case: Case, cc: dict) -> dict:
    """Envelope demands of a group of members sharing one reinforcement layout."""
    dem = {"bottom": {"uls": 0.0, "qp": 0.0, "char": 0.0}, "top": {"uls": 0.0, "qp": 0.0, "char": 0.0}}
    for m in members:
        a, b = region_limits(m)
        vals = [v for _, v in member_values(m, a, b)]
        faces = [s.values for f in m.faces for s in at(m.stations, f.pos)]     # + rigid side (ULS only)
        for key in ("uls", "qp", "char"):
            for v in vals + (faces if key == "uls" else []):
                for fac in cc[key].values():
                    M = E.combine(v, fac, ("M",))["M"]
                    f = "bottom" if M > 0 else "top"
                    dem[f][key] = max(dem[f][key], abs(M))
    return dem


def _face_ok(r: BeamReinforcement, face: str, dem: dict, case: Case, members: list[Member], cc: dict,
             ledge: bool = False) -> dict:
    """All checks governed by the bars of ``face`` for the group demands."""
    etas = {}
    etas["uls"] = dem[face]["uls"] * KNM / mrd(r, case.mode, face)["MRd"]
    etas["as_min"] = as_min(r, face, "CE") / r.As(face)
    etas["spacing"] = r.max_spacing(face) / S_LONG_MAX
    etas["clear"] = AV.smin_clear(r.phi_max(face)) / r.clear_spacing(face)
    ck = crack_check(r, (1 if face == "bottom" else -1) * dem[face]["qp"] * KNM)
    etas["wk"] = ck["wk"] / W_MAX
    s = stresses(r, (1 if face == "bottom" else -1) * dem[face]["char"] * KNM)
    etas["sigma_s"] = s["sigma_s"] / (K3_SIGS * STEEL.fyk)
    etas["sigma_c"] = s["sigma_c"] / (K1_SIGC * CONC.fck)
    # torsion + bending tension chord at the faces
    ch = 0.0
    for m in members:
        if not m.torsion_verdict:
            continue
        rows = [x for x in shear_torsion_rows_chord(case, m, r, cc["uls"], ledge) if x[0] == face]
        ch = max([ch] + [x[1] for x in rows])
    etas["chord"] = ch
    return {"eta": max(etas.values()), "etas": etas, "wk": ck["wk"], "cracked": ck["cracked"]}


def shear_torsion_rows_chord(case: Case, member: Member, r: BeamReinforcement, uls: dict,
                             ledge: bool = False) -> list[tuple]:
    """(face, eta) of the M + T tension-chord check at every face section of the member
    (``ledge``: + the ledge-bearing torque of the end beams at the span faces)."""
    out = []
    d = min(r.d("top"), r.d("bottom"))
    z, bw, tw = 0.9 * d, r.geom.bw, thin_wall(r)
    for f in member.faces:
        cf = combos_on([s.values for s in at(member.stations, f.pos)], uls)
        cot, _ = cot_theta(case, bw, z, tw, [(v["V"], v["T"]) for _, v in cf])
        add = ledge and member.group == "end" and f.kind == "support"
        for nm, v in cf:
            face = "bottom" if v["M"] > 0 else "top"
            T = abs(v["T"]) + (ledge_torsion(uls[nm]) if add else 0.0)
            sAsl = T * KNM * tw["uk"] * cot / (2 * tw["Ak"] * FYD)
            out.append((face, abs(v["M"]) * KNM / mrd(r, case.mode, face)["MRd"]
                        + sAsl * tw["bk"] / tw["uk"] / r.As(face)))
    return out


def _stirrups_ok(r: BeamReinforcement, members: list[Member], case: Case, cc: dict, ledge: bool = False) -> dict:
    etas = {"per_leg": 0.0, "VRd_s": 0.0}
    for m in members:
        for row in shear_torsion_rows(case, m, r, cc["uls"]):
            if not (row["in_verdict"] or (ledge and "sensibilidad" in row["check"])):
                continue
            if row["check"].startswith("estribos V + suspensión"):
                etas["V_hanger"] = max(etas.get("V_hanger", 0.0), row["eta"])
            elif row["check"].startswith("estribos"):
                etas["per_leg"] = max(etas["per_leg"], row["eta"])
            elif row["check"].startswith("VEd(d) <= VRd,s"):
                etas["VRd_s"] = max(etas["VRd_s"], row["eta"])
    st, g = r.stirrups, r.geom
    d = min(r.d("top"), r.d("bottom"))
    etas["rho_w"] = 0.08 * math.sqrt(CONC.fck) / STEEL.fyk / (st.asw_s / g.bw)
    etas["sl"] = st.s / (0.75 * d)
    etas["st"] = st.st(g) / min(0.75 * d, 600.0)
    if any(m.torsion_verdict for m in members):
        tw = thin_wall(r)
        etas["torsion_s"] = st.s / min(tw["uk"] / 8, g.bw, g.h)
    return {"eta": max(etas.values()), "etas": etas}


def _quick_stirrup_etas(r: BeamReinforcement, pre: list, case: Case) -> float:
    """Fast per-leg / all-links utilisation from precomputed (V_d, T_d, cot, z, Ak, Asw_hanger)
    tuples (Asw_hanger [mm2/mm], A19.6.2.1(9))."""
    st = r.stirrups
    e = 0.0
    for V, T, cot, z, Ak, H in pre:
        asw_v = V * 1e3 / (z * FYWD * cot) + H
        ast = T * KNM / (2 * Ak * FYD * cot)
        e = max(e, (asw_v / st.legs + ast) / st.leg_s, asw_v / st.asw_s)
    return e


def search(members: list[Member], r0: BeamReinforcement, case: Case, cc: dict, ledge: bool = False) -> dict:
    """Lightest practical layout per component (bottom bars, top bars, links) that passes every
    check for all ``members`` (they share one layout), keeping the provided component when it
    already passes.  ``ledge``: end beams with the ledge-bearing torque added (sensitivity)."""
    dem = _group_demands(members, case, cc)
    r = r0
    result = {"members": [m.key for m in members], "demands_kNm": {f: {k: _f(v, 2) for k, v in dem[f].items()}
                                                                   for f in ("bottom", "top")}}
    for face in ("bottom", "top"):
        base = _face_ok(r, face, dem, case, members, cc, ledge)
        entry = {"provided": r.describe(face), "provided_As_cm2": _f(r.As(face) / 100, 2),
                 "provided_eta": _f(base["eta"], 3), "provided_etas": {k: _f(v, 3) for k, v in base["etas"].items()}}
        if base["eta"] <= 1.0:
            entry.update({"change": False, "proposed": r.describe(face), "proposed_As_cm2": _f(r.As(face) / 100, 2)})
        else:
            cands = []
            phis = (12.0, 16.0, 20.0, 25.0) if r.geom.kind == "R" else (16.0, 20.0, 25.0)
            for label, groups in AV.row_layouts(r.geom, face, phis=phis, stirrup_phi=r.stirrups.phi):
                rc = r.with_face(face, groups)
                if rc.As(face) < 0.8 * min(r.As(face), dem[face]["uls"] * KNM / (0.9 * rc.d(face) * FYD)):
                    continue
                ev = _face_ok(rc, face, dem, case, members, cc, ledge)
                n = sum(g.n for g in groups)
                cands.append((rc.As(face), ev["eta"], label, rc, ev, rc.As(face) * (1 + BAR_PENALTY * n)))
            ok = sorted([c for c in cands if c[1] <= 1.0], key=lambda c: (c[5], c[1]))
            tried = len(cands)
            if ok:
                As, eta, label, rc, ev, _ = ok[0]
                r = rc
                entry.update({"change": True, "proposed": label, "proposed_As_cm2": _f(As / 100, 2),
                              "proposed_eta": _f(eta, 3), "proposed_etas": {k: _f(v, 3) for k, v in ev["etas"].items()},
                              "wk_mm": _f(ev["wk"], 3), "candidates_tried": tried,
                              "alternatives": [{"layout": c[2], "As_cm2": _f(c[0] / 100, 2), "eta": _f(c[1], 3)}
                                               for c in ok[1:6]]})
            else:
                best = min(cands, key=lambda c: c[1])
                entry.update({"change": True, "feasible": False, "proposed": None,
                              "best_infeasible": best[2], "best_eta": _f(best[1], 3),
                              "best_etas": {k: _f(v, 3) for k, v in best[4]["etas"].items()},
                              "candidates_tried": tried,
                              "note": "no single-row layout of one diameter passes: change the section"})
        result[face] = entry
    # links
    base = _stirrups_ok(r, members, case, cc, ledge)
    entry = {"provided": r.stirrups.label, "provided_eta": _f(base["eta"], 3),
             "provided_etas": {k: _f(v, 3) for k, v in base["etas"].items()}}
    if base["eta"] <= 1.0:
        entry.update({"change": False, "proposed": r.stirrups.label})
    else:
        d = min(r.d("top"), r.d("bottom"))
        z, bw, tw = 0.9 * d, r.geom.bw, thin_wall(r)
        pre = []
        for m in members:
            for f in m.faces:
                fv = face_values(m, f, d / 1000.0)
                cot, _ = cot_theta(case, bw, z, tw, [(v["V"], v["T"]) for _, v in combos_on(fv["face"], cc["uls"])])
                add = ledge and m.group == "end" and f.kind == "support"
                for nm, v in combos_on(fv["d"], cc["uls"]):
                    T = (abs(v["T"]) + (ledge_torsion(cc["uls"][nm]) if add else 0.0)) if m.torsion_verdict else 0.0
                    H = hanger_asw(m, cc["uls"][nm], fv["y_d"]) if case.hanger else 0.0
                    pre.append((abs(v["V"]), T, cot, z, tw["Ak"], H))
        cands = []
        for st in AV.stirrup_options(r.geom):
            rc = r.with_stirrups(st)
            s_max = min(0.75 * d, tw["uk"] / 8, bw, r.geom.h) if any(m.torsion_verdict for m in members) else 0.75 * d
            if st.s > s_max or st.st(r.geom) > min(0.75 * d, 600.0):
                continue
            if 0.08 * math.sqrt(CONC.fck) / STEEL.fyk > st.asw_s / bw:
                continue
            e = _quick_stirrup_etas(rc, pre, case)
            if e <= 1.0:
                cands.append((st.weight(r.geom), e, st))
        cands.sort(key=lambda c: (c[0], c[1]))
        if cands:
            w, e, st = cands[0]
            r = r.with_stirrups(st)
            ev = _stirrups_ok(r, members, case, cc, ledge)
            entry.update({"change": True, "proposed": st.label, "proposed_eta": _f(ev["eta"], 3),
                          "proposed_etas": {k: _f(v, 3) for k, v in ev["etas"].items()},
                          "weight_kg_m": _f(w, 2), "provided_weight_kg_m": _f(r0.stirrups.weight(r0.geom), 2),
                          "alternatives": [{"links": c[2].label, "kg_m": _f(c[0], 2), "eta": _f(c[1], 3)}
                                           for c in cands[1:6]]})
        else:
            entry.update({"change": True, "feasible": False, "proposed": None})
    result["stirrups"] = entry
    result["reinforcement"] = r
    result["weight_long_kg_m"] = {"provided": _f(r0.weight_long(), 2), "proposed": _f(r.weight_long(), 2)}
    return result


# ============================================================================================
# CYPE parity
# ============================================================================================
def _cmp(quantity: str, ours, cype, src: str, tol_pct: float | None = 0.5, note: str = "", **extra) -> dict:
    diff = None if (ours is None or cype in (None, 0)) else (ours / cype - 1) * 100
    if tol_pct is None or diff is None:
        status = "INFO"
    else:
        status = "PASS" if abs(diff) <= tol_pct else "DIFF"
    row = {"quantity": quantity, "ours": _f(ours, 4), "cype": _f(cype, 4) if isinstance(cype, float) else cype,
           "diff_pct": _f(diff, 2), "status": status,
           "src": src, "note": note}
    row.update(extra)
    return row


def parity_body_check() -> list[dict]:
    """Beam P3-P4 (Pórtico 4) body check of Anejo 10 with CYPE's printed design forces."""
    bc = REF["beams"]["body_check_P3_P4"]
    neg = bc["section_negativos_P3_1448"]
    r = AV.provided(2)
    rows = []
    cap = mrd(r, Mode.CYPE, "top")
    rows.append(_cmp("P3-P4 MRd,x (hogging, Mode.CYPE)", -cap["MRd"] / KNM, neg["bending"]["MRd_x"]["value"],
                     neg["bending"]["MRd_x"]["src"]))
    rows.append(_cmp("P3-P4 neutral-axis depth x (figure image112)", cap["x"], 68.52, "P381 figure image112"))
    rows.append(_cmp("P3-P4 Cc at ultimate", cap["Cc"] / 1e3, 767.00, "P384 table"))
    rows.append(_cmp("P3-P4 eta N,M = 273.71/MRd", 273.71 * KNM / cap["MRd"], neg["bending"]["eta"]["value"],
                     neg["bending"]["eta"]["src"], tol_pct=0.1))
    sh = neg["shear"]
    z = 0.9 * r.d("top")
    rows.append(_cmp("P3-P4 z = 0.9 d", z, 432.0, sh["compression_strut_dir_Y"]["z"]["src"]))
    vmax = vrd_max(r.geom.bw, z, 1.0)
    rows.append(_cmp("P3-P4 VRd,max (theta 45)", vmax / 1e3, sh["VRd_max_Vy"]["value"], sh["VRd_max_Vy"]["src"]))
    vs = vrd_s(r.stirrups.asw_s, z, 1.0)
    rows.append(_cmp("P3-P4 VRd,s (3 legs Ø10/100, fywd 400)", vs / 1e3, sh["VRd_s_Vy"]["value"], sh["VRd_s_Vy"]["src"]))
    rows.append(_cmp("P3-P4 eta VEd/VRd,s (VEd = 390.18)", 390.18e3 / vs, sh["eta_2_VRds"]["value"],
                     sh["eta_2_VRds"]["src"], tol_pct=0.1))
    rows.append(_cmp("P3-P4 eta VEd/VRd,max", 390.18e3 / vmax, sh["eta_1_VRdmax"]["value"], sh["eta_1_VRdmax"]["src"],
                     tol_pct=0.2))
    rows.append(_cmp("P3-P4 'Área Transv. Nec.' = VEd/(z fywd) [cm2/m]", 390.18e3 / (z * FYWD) * 10, 22.58,
                     "listing P1620 table, Pórtico 4 P3-P4 1/3L"))
    mn = neg["min_reinforcement"]
    rows.append(_cmp("As,min top (z = 0.9d = 432, CYPE C14) [cm2]", as_min(r, "top", "CYPE") / 100, mn["As_min"]["value"],
                     mn["As_min"]["src"], tol_pct=0.2))
    rows.append(_cmp("W top (gross) [cm3]", r.geom.W("top") / 1e3, mn["W"]["value"], mn["W"]["src"], tol_pct=0.01))
    rows.append(_cmp("As,min top with z = 0.8h (CE text) [cm2]", as_min(r, "top", "CE") / 100, mn["As_min"]["value"],
                     "A19.9.2.1.1(1)", tol_pct=None, note="code-strict alternative (-1.8 %)"))
    rows.append(_cmp("As,min bottom (z = 0.9d) [cm2]", as_min(r, "bottom", "CYPE") / 100, 6.37,
                     "listing P1626 table, Pórtico 5 P11-P5 As_bot_nec (M > 0 exists, As,min governs)", tol_pct=0.2))
    rows.append(_cmp("'Área Inf. Nec.' Mmax = 294.61 [cm2]", as_required(r, Mode.CYPE, "bottom", 294.61 * KNM) / 100,
                     15.10, "listing P1620 table 2/3L", tol_pct=0.2))
    rows.append(_cmp("'Área Sup. Nec.' M(P3) = -273.71 [cm2]", as_required(r, Mode.CYPE, "top", 273.71 * KNM) / 100,
                     13.72, "listing P1620 table 1/3L (node moment, C20)", tol_pct=0.2))
    rows.append(_cmp("rho_w,min·bw (50 cm web) [cm2/m]", 0.08 * math.sqrt(35) / 500 * 500 * 10, 4.73,
                     "listing 'Nec.' minimum links", tol_pct=0.2))
    rows.append(_cmp("rho_w,min·bw (25 cm edge beam) [cm2/m]", 0.08 * math.sqrt(35) / 500 * 250 * 10, 2.37,
                     "listing Pórtico 10 'Nec.'", tol_pct=0.3))
    rows.append(_cmp("sl,max = 0.75 d [mm]", 0.75 * r.d("top"), 360, sh["spacing"]["checks"][0]["limit"]["src"]))
    rows.append(_cmp("st,max = 0.75 d [mm]", min(0.75 * r.d("top"), 600), 360, sh["spacing"]["checks"][1]["limit"]["src"]))
    rows.append(_cmp("clear spacing top bars [mm]", r.clear_spacing("top"), 63, "P352 table", tol_pct=1.0))
    rows.append(_cmp("max bar spacing bottom [mm]", r.max_spacing("bottom"), 150, "P352 table (sb)"))
    # SLS: engineer's hand check (P570-P575), bars 5Ø20 + 7Ø20 as in the figure
    sec = sls_section(r, faces=("top", "bottom"))
    un = uncracked_stresses(sec, ALPHA_E, 86.0 * KNM)
    rows.append(_cmp("sigma_ct bottom at M_qp = 86 kN·m (hand check) [MPa]", un["bot"], -2.20, "P575 / image118",
                     tol_pct=0.5, note="homogenised n = Es/Ecm = 6.52, bars 5Ø20 + 7Ø20"))
    rows.append(_cmp("Mcr,sag (fctm, homogenised) [kN·m]", mcr(r, True, faces=("top", "bottom")) / KNM, 125.21,
                     "validate_codigo K.05 (no CYPE print)", tol_pct=0.1))
    rows.append(_cmp("Mcr,hog (fctm, homogenised) [kN·m]", mcr(r, False, faces=("top", "bottom")) / KNM, 99.84,
                     "validate_codigo K.06 (no CYPE print)", tol_pct=0.1))
    rows.append(_cmp("fT,lim = L/250 (L = 3.05) [mm]", 3050 / 250, 12.20, "P583 table"))
    rows.append(_cmp("fA,lim = L/500 [mm]", 3050 / 500, 6.10, "P581 table"))
    # crack width demonstration of the research (K.12-K.18)
    ck = crack_check(r.with_face("side", []), 151.9 * KNM)
    rows.append(_cmp("wk at M = 151.9 (psi2 0.8, SAP) [mm], bars 5Ø20+7Ø20", ck["wk"], 0.1802,
                     "validate_codigo K.17 (research, no CYPE print)", tol_pct=1.0))
    ck = crack_check(r.with_face("side", []), mcr(r, True, faces=("top", "bottom")) * 1.0000001)
    rows.append(_cmp("wk at M = Mcr,sag [mm]", ck["wk"], 0.1486, "validate_codigo K.18", tol_pct=1.0))
    # end frames: listing Nec with the drawing (node) moments, L section
    for axis, lab in ((1, "Pórtico 3"), (7, "Pórtico 9")):
        re_ = AV.provided(axis)
        env_ = REF["beams"]["drawings_bar_layout"][lab]["envelope_labels"]
        span = list(REF["beams"]["listing_armado_vigas_2"]["porticos"][lab]["tramos"].values())[1]
        rows.append(_cmp(f"{lab} 'Área Sup. Nec.' node M = {env_['My_min']} [cm2]",
                         as_required(re_, Mode.CYPE, "top", abs(env_["My_min"]) * KNM) / 100,
                         span["zones"][0]["As_top_nec"], span["zones"][0]["src"], tol_pct=0.2))
        rows.append(_cmp(f"{lab} 'Área Inf. Nec.' M = {env_['My_max']} [cm2]",
                         as_required(re_, Mode.CYPE, "bottom", abs(env_["My_max"]) * KNM) / 100,
                         span["zones"][2]["As_bot_nec"], span["zones"][2]["src"], tol_pct=0.2))
        cap = mrd(re_, Mode.CYPE, "top")
        ap = [x for x in REF["beams"]["appendix_checks_4_3"]["resistance"]["rows"]
              if x["viga"] == ("P1 - P2" if axis == 1 else "P16 - P18")][0]
        rows.append(_cmp(f"{lab} §4.3 N,M eta at the node (M = {env_['My_min']}) [%]",
                         abs(env_["My_min"]) * KNM / cap["MRd"] * 100, ap["N,M"]["eta_pct"], ap["N,M"]["src"],
                         tol_pct=0.3, note="calibrates the end-frame bars at 235 mm (Ø20 active, 2Ø10 inactive)"))
    # end-frame cantilever torsion (CYPE: nu = 0.6, fyd for torsion links, tef = A/u of 800x550)
    re_ = AV.provided(1)
    tw = thin_wall(re_)
    tmax = trd_max(tw, 1.0, 0.6)
    rows.append(_cmp("Pórtico 3 P9-P1 Tc = T/TRd,max (T = 25.79, nu 0.6) [%]", 25.79 * KNM / tmax * 100, 4.6,
                     "P1813 table P9 - P1 Tc", tol_pct=2.0))
    rows.append(_cmp("Pórtico 3 P1-P2 Tc (T = 27.43) [%]", 27.43 * KNM / tmax * 100, 4.9, "P1813 table P1 - P2 Tc",
                     tol_pct=2.0))
    rows.append(_cmp("Pórtico 3 P9-P1 Tst = (T/(2 Ak fyd))/(Ø10/100) [%]",
                     25.79 * KNM / (2 * tw["Ak"] * FYD) / re_.stirrups.leg_s * 100, 15.3, "P1813 table P9 - P1 Tst",
                     tol_pct=1.0))
    rows.append(_cmp("Pórtico 3 P9-P1 'Área Transv. Nec.' 1/3L = V/(z fywd) + 2 T/(2 Ak fyd) [cm2/m]",
                     (101.53e3 / (432 * FYWD) + 25.79 * KNM / (tw["Ak"] * FYD)) * 10, 8.28, "listing P1614 table",
                     tol_pct=0.5))
    rows.append(_cmp("Pórtico 3 P9-P1 TRd,max with nu = 0.6(1 - fck/250) (CE) [kN·m]",
                     trd_max(tw, 1.0, NU_T_CE) / KNM, tmax / KNM, "A19.6.3.2(4)", tol_pct=None,
                     note="code-strict nu = 0.516: TRd,max -14 %"))
    return rows


def _zone_bounds(L: float) -> list[tuple[float, float]]:
    return [(L * k / 3, L * (k + 1) / 3) for k in range(3)]


def parity_listing(members: list[Member], reinf: dict, case: Case) -> list[dict]:
    """Listing §2 per pórtico/tramo/zone: zone envelopes and 'Área Nec.' from the SAP forces
    (Mode.CYPE, basis CYPE, shift al = 0.45 d) and from CYPE's own zone moments."""
    uls = E.uls(case.basis)
    por = REF["beams"]["listing_armado_vigas_2"]["porticos"]
    rows = []
    drw = REF["beams"]["drawings_bar_layout"]
    for m in members:
        r = reinf[m.key]
        d = min(r.d("top"), r.d("bottom"))
        z = 0.9 * d
        al = z / 2
        tw = thin_wall(r)
        if m.kind == "transverse":
            lab = f"Pórtico {int(m.key[2:]) + 2}"
            tramos = list(por[lab]["tramos"].items())
            node = drw[lab]["envelope_labels"]["My_min"]
            z1 = tramos[1][1]["zones"][0]
            rows.append(_cmp(f"{lab} {tramos[1][0]} 1/3L As_top_nec from the drawing node moment {node} [cm2]",
                             as_required(r, Mode.CYPE, "top", abs(node) * KNM) / 100, z1["As_top_nec"], z1["src"],
                             tol_pct=0.3, kind="As_node",
                             note="CYPE sizes the support steel with the node moment (C20), not the zone value"))
            geo = [(tramos[0], -0.30, 0.10, "cantilever"), (tramos[1], 0.20, 3.05, "span")]
        else:
            lab = "Pórtico 1" if m.key == "VBM" else "Pórtico 10"
            tramos = list(por[lab]["tramos"].items())
            if m.key == "VBM":
                geo = [(tramos[0], 0.0, 39.0, "edge_long")]
            else:
                geo = [(t, E.tm.AXES_X[k] + 0.2, 6.10, "span") for k, t in enumerate(tramos)]
        for (tname, tdata), y0, L, kind in geo:
            for (xa, xb), zone in zip(_zone_bounds(L), tdata["zones"]):
                ya, yb = y0 + xa, y0 + xb
                lo, hi = region_limits(m)
                vals = [v for p, v in member_values(m, max(ya, lo), min(yb, hi))]
                vals += interp(m.stations, max(ya, lo)) + interp(m.stations, min(yb, hi))
                vals += [s.values for s in at(m.stations, ya) + at(m.stations, yb)]
                if kind == "span":
                    ext = [v for p, v in member_values(m, max(ya - al / 1000, y0), min(yb + al / 1000, y0 + L))]
                    ext += [s.values for s in at(m.stations, y0) + at(m.stations, y0 + L)
                            if ya - al / 1000 <= s.pos <= yb + al / 1000]
                    ext += interp(m.stations, max(ya - al / 1000, y0)) + interp(m.stations, min(yb + al / 1000, y0 + L))
                    vv = [v for p, v in member_values(m, max(ya, y0 + d / 1000), min(yb, y0 + L - d / 1000))]
                    vv += interp(m.stations, max(ya, y0 + d / 1000)) + interp(m.stations, min(yb, y0 + L - d / 1000))
                else:
                    ext, vv = vals, vals
                Mmin, _ = env(vals, uls, "M", -1)
                Mmax, _ = env(vals, uls, "M", +1)
                Mmin_e, _ = env(ext, uls, "M", -1)
                Mmax_e, _ = env(ext, uls, "M", +1)
                V, _ = env(vv or vals, uls, "V", 0)
                T, _ = env(vals, uls, "T", 0)
                src = zone["src"]
                q = f"{lab} {tname} {zone['zone']}"
                rows.append(_cmp(q + " M_min [kN·m]", Mmin if Mmin < 0 else None, zone["M_min"], src, None, kind="M"))
                rows.append(_cmp(q + " M_max [kN·m]", Mmax if Mmax > 0 else None, zone["M_max"], src, None, kind="M"))
                vc = max(abs(zone["V_min"] or 0), abs(zone["V_max"] or 0))
                rows.append(_cmp(q + " |V|max [kN]", abs(env(vals, uls, "V", 0)[0]), vc or None, src, None, kind="V"))
                for face, Mz, Mze, key, cM in (("top", Mmin, Mmin_e, "As_top_nec", zone["M_min"]),
                                               ("bottom", Mmax, Mmax_e, "As_bot_nec", zone["M_max"])):
                    has = (Mz < -1.0) if face == "top" else (Mz > 1.0)
                    amin = as_min(r, face, "CYPE") if has else 0.0
                    Me = abs(Mze) if ((Mze < 0) if face == "top" else (Mze > 0)) else 0.0
                    ours = max(as_required(r, Mode.CYPE, face, Me * KNM), amin) / 100
                    cyM = None
                    if cM is not None:
                        cyM = max(as_required(r, Mode.CYPE, face, abs(cM) * KNM), as_min(r, face, "CYPE")) / 100
                    rows.append(_cmp(q + f" {key} [cm2]", ours, zone[key], src, None, kind="As",
                                     ours_from_cype_M=_f(cyM, 2),
                                     diff_cypeM_pct=_f((cyM / zone[key] - 1) * 100, 2) if (cyM and zone[key]) else None))
                asw = abs(V) * 1e3 / (z * FYWD) * 10
                if m.group == "end" and kind == "cantilever":
                    asw += abs(T) * KNM / (tw["Ak"] * FYD) * 10
                asw = max(asw, 0.08 * math.sqrt(CONC.fck) / STEEL.fyk * r.geom.bw * 10)
                rows.append(_cmp(q + " Asw_per_m_nec [cm2/m]", asw, zone["Asw_per_m_nec"], src, None, kind="Asw"))
    return rows


def parity_utilisation(members: list[Member], reinf: dict, case: Case, st_rows: list[dict],
                       defl_rows: list[dict]) -> list[dict]:
    """§4.3 'N,M' and 'Q' utilisations per tramo (SAP forces, Mode.CYPE, basis CYPE, theta 45)."""
    ap = {x["viga"].replace(" ", ""): x for x in REF["beams"]["appendix_checks_4_3"]["resistance"]["rows"]}
    dfl = {x["viga"].replace(" ", ""): x for x in REF["beams"]["appendix_checks_4_3"]["deflection"]["rows"]}
    uls = E.uls(case.basis)
    rows = []
    names = {1: ("P9-P1", "P1-P2"), 2: ("P10-P3", "P3-P4"), 3: ("P11-P5", "P5-P6"), 4: ("P12-P7", "P7-P8"),
             5: ("P19-P13", "P13-P14"), 6: ("P21-P15", "P15-P17"), 7: ("P20-P16", "P16-P18")}
    for m in members:
        if m.kind != "transverse":
            continue
        r = reinf[m.key]
        axis = int(m.key[2:])
        cant, span = names[axis]
        for tram, a, b, faces in ((cant, -0.50, -0.20, [0]), (span, 0.20, 3.25, [1, 2])):
            vals = [v for _, v in member_values(m, a, b)]
            best = 0.0
            for face, sign in (("bottom", 1), ("top", -1)):
                M, _ = env(vals, uls, "M", sign)
                if sign * M > 0:
                    best = max(best, abs(M) * KNM / mrd(r, Mode.CYPE, face)["MRd"])
            c = ap.get(tram)
            rows.append(_cmp(f"§4.3 {tram} N,M eta [%]", best * 100, c["N,M"]["eta_pct"], c["N,M"]["src"], None,
                             note="ours: max over the tramo at the faces; CYPE: node 'Pn' (cantilevers: reduced "
                                  "anchorage area near the bar ends, not modelled)"))
            q = max((x["eta"] for x in st_rows if x["member"] == m.key and x["check"].startswith("VEd(d) <= VRd,s")
                     and any(x["section"] == m.faces[i].name for i in faces)), default=None)
            rows.append(_cmp(f"§4.3 {tram} Q eta [%]", None if q is None else q * 100, c["Q"]["eta_pct"], c["Q"]["src"],
                             None))
            if isinstance(c.get("Tc"), dict):
                t = max((x["T_over_TRdmax"] for x in st_rows if x["member"] == m.key and x["check"] == "TEd/TRd,max + VEd/VRd,max <= 1"
                         and any(x["section"] == m.faces[i].name for i in faces)), default=None)
                rows.append(_cmp(f"§4.3 {tram} Tc eta [%]", None if t is None else t * 100, c["Tc"]["eta_pct"],
                                 c["Tc"]["src"], None, note="SAP torsion is larger than CYPE's (edge-beam continuity)"))
            if isinstance(c.get("TVy"), dict):
                t = max((x["eta"] for x in st_rows if x["member"] == m.key and x["check"] == "TEd/TRd,max + VEd/VRd,max <= 1"
                         and any(x["section"] == m.faces[i].name for i in faces)), default=None)
                rows.append(_cmp(f"§4.3 {tram} TVy eta [%]", None if t is None else t * 100, c["TVy"]["eta_pct"],
                                 c["TVy"]["src"], None))
            if tram == span:
                fr = [x for x in defl_rows if x["member"] == m.key and x["check"].startswith("f total")]
                dc = dfl.get(tram)
                if fr and dc:
                    rows.append(_cmp(f"§4.3 {tram} fT,max [mm]", fr[0]["demand"], dc["fT,max"], dc["src"], None,
                                     note=f"ours: cracked-section integration, phi = {PHI_CREEP}, beta = 0.5"))
    for m in members:
        if m.kind != "edge":
            continue
        r = reinf[m.key]
        tramos = ["P9-P20"] if m.key == "VBM" else ["P2-P4", "P4-P6", "P6-P8", "P8-P14", "P14-P17", "P17-P18"]
        spans = [(0.0, 39.0)] if m.key == "VBM" else [(a, b) for _, a, b in m.spans]
        for tram, (a, b) in zip(tramos, spans):
            vals = [v for _, v in member_values(m, a - 0.3, b + 0.3)]
            best = 0.0
            for face, sign in (("bottom", 1), ("top", -1)):
                M, _ = env(vals, uls, "M", sign)
                if sign * M > 0:
                    best = max(best, abs(M) * KNM / mrd(r, Mode.CYPE, face)["MRd"])
            c = ap.get(tram)
            if c:
                rows.append(_cmp(f"§4.3 {tram} N,M eta [%]", best * 100, c["N,M"]["eta_pct"], c["N,M"]["src"], None))
                q = max((x["eta"] for x in st_rows if x["member"] == m.key and x["check"].startswith("VEd(d) <= VRd,s")
                         and a - 0.5 <= (x["pos_m"] or 0) <= b + 0.5), default=None)
                rows.append(_cmp(f"§4.3 {tram} Q eta [%]", None if q is None else q * 100, c["Q"]["eta_pct"],
                                 c["Q"]["src"], None))
    return rows


def parity_cracking(sls: list[dict]) -> list[dict]:
    """CYPE prints 'N.P.(1)' (sigma_ct < fct) for every beam face: compare our state under QP03."""
    rows = []
    for x in sls:
        if x["case"] == "CYPE" and x["check"] == "sigma_ct <= fctm (QP)":
            rows.append(_cmp(f"{x['member']} {x['section']} sigma_ct/fctm (QP psi2 0.3) < 1 -> 'N.P.(1)'",
                             x["eta"], None, "P1818-P1827 tables (all faces N.P.(1))", None,
                             note="uncracked" if x["eta"] <= 1 else "CRACKED (CYPE: not cracked)"))
    return rows


# ============================================================================================
# run
# ============================================================================================
def run(cases: tuple = CASES, do_search: bool = True, data: dict | None = None, verbose: bool = False) -> dict:
    t0 = time.time()
    members, reinf = build_members(data)
    tables: dict = {k: [] for k in ("bending", "shear_torsion", "detailing", "sls", "deflection", "as_required")}
    summary: dict = {}
    for case in cases:
        cc = case_combos(case)
        for m in members:
            t = check_member(case, m, reinf[m.key], cc)
            for k, v in t.items():
                tables[k] += v
            rows = [x for k in ("bending", "shear_torsion", "detailing", "sls", "deflection") for x in t[k]]
            summary.setdefault(m.key, {"label": reinf[m.key].label, "cases": {}})["cases"][case.name] = summarise(rows)
        if verbose:
            print(f"  case {case.name}: {time.time() - t0:.1f} s", file=sys.stderr)
    final = next(c for c in cases if c.final) if any(c.final for c in cases) else cases[-1]
    for k, v in summary.items():
        v["verdict"] = v["cases"][final.name]["verdict"]
        v["governing"] = {f: x for f, x in v["cases"][final.name].items() if f != "verdict" and not x.get("info")}
        v["information"] = {f: x for f, x in v["cases"][final.name].items() if f != "verdict" and x.get("info")}
    tables["reinforcement_provided"] = [row for m in members for row in reinf[m.key].table()]
    # psi2 threshold (provided layouts)
    thr = []
    for m in members:
        for sign in (+1, -1):
            thr.append(psi2_threshold(m, reinf[m.key], sign))
    tables["psi2_threshold"] = thr
    # CYPE parity
    cy = next((c for c in cases if c.name == "CYPE"), None)
    comparison = parity_body_check() + AV_reference_rows() + parity_research(thr)
    if cy is not None:
        st_rows = [x for x in tables["shear_torsion"] if x["case"] == "CYPE"]
        df_rows = [x for x in tables["deflection"] if x["case"] == "CYPE"]
        tables["cype_listing_nec"] = parity_listing(members, reinf, cy)
        tables["cype_utilisation_4_3"] = parity_utilisation(members, reinf, cy, st_rows, df_rows)
        comparison += parity_cracking(tables["sls"])
        comparison += [x for x in tables["cype_listing_nec"] if x.get("kind") == "As_node"]
        comparison += _listing_digest(tables["cype_listing_nec"])
        comparison += tables["cype_utilisation_4_3"]
    if verbose:
        print(f"  parity: {time.time() - t0:.1f} s", file=sys.stderr)
    proposal = {}
    if do_search:
        cc = case_combos(final)
        groups = {"inner (ejes 2-6, pórticos 4-8)": [m for m in members if m.group == "inner"],
                  "end (ejes 1 y 7, pórticos 3 y 9)": [m for m in members if m.group == "end"],
                  "edge (pórticos 1 y 10)": [m for m in members if m.group == "edge"]}
        for gname, ms in groups.items():
            # one layout per group; the L end frames are mirror images -> search on axis 1 geometry,
            # verification per member with its own geometry
            base = reinf[ms[0].key]
            res = search(ms, base, final, cc)
            rnew = res.pop("reinforcement")
            verif = {}
            prop_rows = []
            for m in ms:
                rm = _apply_layout(reinf[m.key], rnew)
                t = check_member(final, m, rm, cc)
                rows = [x for k in ("bending", "shear_torsion", "detailing", "sls", "deflection") for x in t[k]]
                verif[m.key] = summarise(rows)
                prop_rows += t["as_required"]
            res["verification"] = verif
            res["as_required_proposed"] = prop_rows
            thr_g = [x["psi2_wk_fail"] for x in thr if x["member"] in {m.key for m in ms} and x["psi2_wk_fail"] is not None]
            res["psi2_threshold_provided"] = min(thr_g) if thr_g else None
            res["layout"] = [row for row in rnew.table()]
            proposal[gname] = res
            if ms[0].group == "end":
                rl = search(ms, base, final, cc, ledge=True)
                rnl = rl.pop("reinforcement")
                sens = {}
                for m in ms:
                    rows = shear_torsion_rows(final, m, _apply_layout(reinf[m.key], rnl), cc["uls"])
                    sens[m.key] = _f(max(x["eta"] for x in rows if "sensibilidad" in x["check"]), 3)
                rl["ledge_sensitivity_max_eta"] = sens
                rl["layout"] = [row for row in rnl.table()]
                rl["note"] = ("sensitivity, not the verdict: SAP torque + equilibrium torque of the hollow-core "
                              "plates bearing on the single ledge (e = 0.42 m from the pile axis, T = q·Lp/2·e·L/2 "
                              "= 56 kN·m at the pile faces for 1.35G + 1.5Qa); CYPE P437 assumes no torsion")
                proposal[gname + " + torsión del ala (sensibilidad)"] = rl
        if verbose:
            print(f"  search: {time.time() - t0:.1f} s", file=sys.stderr)
    meta = {
        "module": "diseno/codigo/vigas.py",
        "members": {m.key: {"label": reinf[m.key].label, "section": reinf[m.key].geom.name, "group": m.group}
                    for m in members},
        "cases": [{"name": c.name, "basis": c.basis, "mode": c.mode.value, "psi2_Qa": c.psi2_qa,
                   "psi2_TB": c.tb_psi2, "cot_theta": c.cot, "nu_torsion": round(c.nu_torsion, 3),
                   "hanger_in_verdict": c.hanger, "final": c.final, "note": c.note} for c in cases],
        "final_case": final.name,
        "materials": {"fck": CONC.fck, "fcd": round(CONC.fcd, 3), "fctm": round(CONC.fctm, 3),
                      "fctd": round(CONC.fctd, 3), "Ecm": round(CONC.Ecm, 1), "alpha_e": round(ALPHA_E, 3),
                      "fyd": round(FYD, 2), "fywd_shear": FYWD, "nu1": NU1},
        "assumptions": [
            "Forces: SAP2000 v27.1 (sap2000/resultados_sap), CYPE convention; ULS ELU01-22 (CYPE) / ELR01-22 (ROM).",
            "Design sections: pile faces y = +-0.20 / 3.25 / 3.65 (A19.5.3.2.2(3)); pile-axis moments reported as info "
            "(rigid node: CYPE's 'P3' -273.71 lies between the face and the axis, C20).",
            "Shift rule / (6.18): at the pile faces MEd,max = the face moment (A19.5.3.2.2(3), monolithic "
            "support), so M/z + dFtd is capped there and adds nothing; the shift al = z·cot/2 (0.43 m at cot 2) "
            "only governs curtailment (not modelled: full-length bars). If the rigid-node pile-axis moment were "
            "taken as MEd,max instead, the sea-face hogging chord would be at the axis rows' eta (1.03-1.18 for "
            "VT1-VT6, CE-ROM): see the 'eje pilote mar (info)' rows.",
            "Bending about the horizontal axis with a horizontal neutral axis (laterally restrained beams; "
            "L sections: My of the resultant carried by the slab).",
            "Bars run the full length (hooked ends): no anchorage reduction of the area (CYPE reduces it in the "
            "0.10 m cantilevers, 'Área Real' 11.28/13.42).",
            "Shear: z = 0.9d, fywd = 400 MPa with nu1 = 0.6; V at the face for VRd,max and at d for VRd,s "
            "(cantilevers shorter than d: V at the face).",
            "Torsion (A19.6.3) with the SAP torque on every member; in the verdict for the end frames (axes 1, 7, "
            "as required); for the inner frames and edge beams the SAP torque is compatibility torsion (gravity "
            "rotations imposed by the neighbouring members, A19.6.3.1(2)) and is reported as information. Links "
            "per leg of the hoop: Asw,V/(n·s) + T/(2·Ak·fyd·cot); longitudinal (6.28) added to the tension chord.",
            "Suspension (A19.6.2.1(9)): the hollow-core plates bear on the ledges, i.e. the load is applied near "
            "the bottom of the section; the web links carry the ULS plate reaction q·Lp/2 per ledge (inner beams "
            "both ledges, end beams one) at fyd in addition to V/(z·fywd·cot), wherever plates bear (Y -0.306 to "
            "3.603). In the verdict of the CE cases; information in case CYPE (CYPE does not check it).",
            "Sensitivity (not in the verdict): equilibrium torque of the hollow-core plates bearing on the single "
            "ledge of the end beams (e = 0.42 m from the pile axis; 56 kN·m at the pile faces for 1.35G + 1.5Qa), "
            "modelled neither in SAP nor in CYPE (P437).",
            "Case CYPE: cot(theta) = 1 and nu(torsion) = 0.6 (CYPE); CE cases: largest cot(theta) in [0.5, 2] "
            "allowed by (6.29) at the face and nu = 0.6(1 - fck/250) = 0.516 (A19.6.3.2(4)).",
            "SLS: alpha_e = Es/Ecm = 6.52 for stresses and wk; kt = 0.4, k1 0.8, k2 0.5, k3 3.4, k4 0.425, "
            "c = 50 + stirrup Ø; characteristic combinations = SAP ELS01-08 (all psi = 1, upper bound).",
            f"Deflection: curvature integration between the pile faces, phi = {PHI_CREEP} (assumed), beta 0.5; "
            "'activa' = f(QP, inf) - f(PP, inst).",
            "Reinforcement search (final case, one layout per group inner / end / edge, only where the provided "
            "component fails): single row per face, web bars inside the web hoop + ledge bars (equal or one size "
            "smaller), Ø16-Ø25 (edge beams Ø12-Ø25), CE clear spacing max(Ø, dg + 5, 20), bars <= 350 mm apart; "
            "links Ø8-12, 2-4 legs, s 50-300; objective As·(1 + 0.002·n_bars) (weight, fewer bars on ties).",
        ],
        "clauses": {"bending": "A19.6.1", "As_min": "A19.9.2.1.1(1) (9.1)", "As_max": "A19.9.2.1.1(3)",
                    "spacing": "A19.8.2(2), A19.9.2.3(4)", "shear": "A19.6.2.2, A19.6.2.3 (6.7N)-(6.10)",
                    "suspension": "A19.6.2.1(9)",
                    "links": "A19.9.2.2 (9.4)-(9.8)", "torsion": "A19.6.3.2 (6.26)-(6.31), A19.9.2.3",
                    "cracking": "A19.7.1(2), A19.7.3.4, CE Art. 27 Tabla 27.2",
                    "stresses": "A19.7.2", "deflection": "A19.7.4"},
        "runtime_s": round(time.time() - t0, 1),
    }
    return _jsonable({"meta": meta, "tables": tables, "cype_comparison": comparison, "summary": summary,
                      "proposal": proposal})


def parity_research(thr: list[dict]) -> list[dict]:
    """SAP quasi-permanent moments and the psi2 threshold vs the research validation
    (validate_codigo P.01-P.06) and the CYPE hand-check figure (Pórtico 6, 86.66 kN·m)."""
    inner = [x for x in thr if x["member"] in ("VT2", "VT3", "VT4", "VT5", "VT6") and x["face"] == "bottom"]
    vt4 = next(x for x in inner if x["member"] == "VT4")
    gov = min(inner, key=lambda x: x["psi2_crack_fctm"] if x["psi2_crack_fctm"] is not None else 9)
    return [
        _cmp("inner beams M_qp,max sag (psi2 0.3, SAP) [kN·m]", max(x["M_qp_03"] for x in inner), 90.41,
             "validate_codigo P.01", tol_pct=0.1),
        _cmp("inner beams M_qp,max sag (psi2 0.8, SAP) [kN·m]", max(x["M_qp_08"] for x in inner), 151.90,
             "validate_codigo P.03", tol_pct=0.1),
        _cmp("Pórtico 6 (VT4) M_qp,max (psi2 0.3) vs CYPE figure [kN·m]", vt4["M_qp_03"], 86.66,
             "P569 image117 (CYPE)", tol_pct=None, note="SAP vs CYPE model (-3.7 %)"),
        _cmp(f"psi2,Qa at which the inner beams crack ({gov['member']}, fctm)", gov["psi2_crack_fctm"], 0.583,
             "validate_codigo P.06", tol_pct=1.0, note="with 7Ø20 any cracked state fails wk <= 0.1 mm"),
        _cmp("idem with fct,eff = fctm,fl", gov["psi2_crack_fctm_fl"], 0.63, "validate_codigo P.06 note",
             tol_pct=1.0),
    ]


def AV_reference_rows() -> list[dict]:
    return [_cmp(f"{x['member']} {x['quantity']} (Área Real)", x["ours"], x["cype"], x["src"], tol_pct=0.2)
            for x in AV.reference_areas()]


def _listing_digest(rows: list[dict]) -> list[dict]:
    """Summary of the listing comparison: mean / max |diff| per quantity kind."""
    out = []
    for kind in ("M", "V", "As", "Asw"):
        d = [abs(x["diff_pct"]) for x in rows if x.get("kind") == kind and x["diff_pct"] is not None]
        if d:
            out.append(_cmp(f"listing §2 {kind}: mean |diff| over {len(d)} zone values [%]", float(np.mean(d)), None,
                            "tables.cype_listing_nec", None, note=f"median {np.median(d):.1f} %, max {max(d):.1f} %"))
    d = [abs(x["diff_cypeM_pct"]) for x in rows if x.get("diff_cypeM_pct") is not None]
    if d:
        out.append(_cmp(f"listing §2 As Nec from CYPE's own zone M: mean |diff| over {len(d)} [%]", float(np.mean(d)),
                        None, "tables.cype_listing_nec", None,
                        note=f"median {np.median(d):.2f} %; exact where CYPE sizes with the zone moment"))
    return out


def _apply_layout(r_member: BeamReinforcement, r_new: BeamReinforcement) -> BeamReinforcement:
    """Proposed layout of the group applied to one member (mirrors the ledge side of L beams)."""
    if r_member.geom == r_new.geom:
        return r_new.__class__(r_member.member, r_member.label, r_member.geom, list(r_new.groups), r_new.stirrups,
                               notes=r_member.notes)
    flip = r_member.geom.ledge_side * r_new.geom.ledge_side
    groups = [BarGroup(g.name, g.phi, tuple(flip * x for x in g.xs), g.y, g.face, g.active_cype,
                       g.active_codigo, g.src) for g in r_new.groups]
    return r_new.__class__(r_member.member, r_member.label, r_member.geom, groups, r_new.stirrups,
                           notes=r_member.notes)


# ============================================================================================
# report
# ============================================================================================
def _md_table(rows: list[dict], cols: list[str], heads: list[str] | None = None) -> str:
    heads = heads or cols
    out = ["| " + " | ".join(heads) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, bool):
                v = "sí" if v else "NO"
            elif isinstance(v, float):
                v = f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:.1f}"
            cells.append("" if v is None else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def write_md(res: dict, path: Path) -> None:
    meta, T = res["meta"], res["tables"]
    fin = meta["final_case"]
    L = [f"# Vigas transversales y vigas de borde: comprobación Código Estructural (Anejo 19)", "",
         f"Generado por `{meta['module']}` en {meta['runtime_s']} s. Casos:", ""]
    for c in meta["cases"]:
        L.append(f"- **{c['name']}**: base {c['basis']}, modo {c['mode']}, psi2,Qa = {c['psi2_Qa']}, "
                 f"cot(theta) = {c['cot_theta']}, nu(torsión) = {c['nu_torsion']}, "
                 f"suspensión en veredicto = {c['hanger_in_verdict']}. {c['note']}")
    L += ["", "## 1. Veredicto por elemento", ""]
    fams = list(FAMILIES) + list(FAMILIES_INFO)
    rows = []
    for k, v in res["summary"].items():
        for cname, s in v["cases"].items():
            row = {"member": k, "label": v["label"], "case": cname, "verdict": s["verdict"]}
            for f in fams:
                row[f] = s.get(f, {}).get("eta")
            rows.append(row)
    L.append(_md_table(rows, ["member", "label", "case"] + fams + ["verdict"]))
    L += ["", f"## 2. Comprobaciones determinantes, caso final {fin}", ""]
    rows = []
    for k, v in res["summary"].items():
        for f, g in v["governing"].items():
            rows.append({"member": k, "family": f, "eta": g["eta"], "ok": g["ok"], "check": g["check"],
                         "section": g["section"], "combo": g["combo"]})
    L.append(_md_table(rows, ["member", "family", "eta", "ok", "check", "section", "combo"]))
    L += ["", f"## 3. Armadura necesaria / dispuesta (ELU, caso {fin})", "",
          "As,uls = armadura de tracción de cálculo (simple, CYPE 'Área Nec.'); As,req = max(As,uls, As,min CE).", ""]
    rows = [x for x in T["as_required"] if x["case"] == fin]
    L.append(_md_table(rows, ["member", "section", "face", "MEd_kNm", "As_uls_cm2", "As_min_cm2", "As_req_cm2",
                              "As_prov_cm2", "req_over_prov", "combo"]))
    L += ["", "## 4. Fisuración (QP) y umbral de psi2", ""]
    rows = [x for x in T["sls"] if x["check"].startswith("wk") or x["check"].startswith("sigma_ct")]
    L.append(_md_table(rows, ["case", "member", "section", "pos_m", "check", "M_kNm", "demand", "capacity", "eta",
                              "ok", "sigma_s", "sr_max"]))
    L += ["", "Umbral de psi2,Qa con la armadura dispuesta (TB psi2 = 0):", ""]
    L.append(_md_table(T["psi2_threshold"], ["member", "face", "Mcr_kNm", "M_qp_03", "M_qp_08", "psi2_crack_fctm",
                                             "psi2_crack_fctm_fl", "psi2_wk_fail"]))
    L += ["", "## 5. Propuesta de armado (caso final)", ""]
    for g, p in res["proposal"].items():
        L.append(f"### {g}")
        L.append("")
        for comp in ("bottom", "top", "stirrups"):
            e = p[comp]
            txt = (f"- **{comp}**: dispuesto {e['provided']} (eta {e['provided_eta']})"
                   + (f" -> **{e['proposed']}** (eta {e.get('proposed_eta')})" if e.get("change") else " -> sin cambio"))
            if e.get("feasible") is False:
                txt += f" -> SIN SOLUCIÓN en el rango buscado (mejor {e.get('best_infeasible')}, eta {e.get('best_eta')})"
            if e.get("wk_mm") is not None:
                txt += f", wk = {e['wk_mm']} mm"
            L.append(txt)
        L.append(f"- peso armadura longitudinal: {p['weight_long_kg_m']['provided']} -> {p['weight_long_kg_m']['proposed']} kg/m")
        if "verification" in p:
            L.append("- verificación con la propuesta: " + ", ".join(f"{k}: {v['verdict']}" for k, v in p["verification"].items()))
        if "ledge_sensitivity_max_eta" in p:
            L.append(f"- eta máx. de las filas de sensibilidad con la propuesta: {p['ledge_sensitivity_max_eta']}")
            L.append(f"- nota: {p['note']}")
        L.append("")
    L += ["## 6. Comparación con CYPE (Anejo 10)", ""]
    rows = [x for x in res["cype_comparison"] if not x["quantity"].startswith("listing §2 ") or "mean" in x["quantity"]]
    L.append(_md_table(rows, ["quantity", "ours", "cype", "diff_pct", "status", "src", "note"]))
    L += ["", "### Listado §2 por zona (fuerzas SAP, Mode.CYPE, base CYPE)", ""]
    L.append(_md_table([x for x in T.get("cype_listing_nec", []) if x.get("kind") in ("As", "Asw")],
                       ["quantity", "ours", "ours_from_cype_M", "cype", "diff_pct", "diff_cypeM_pct"]))
    for key, title in (("bending", "Flexión ELU"), ("shear_torsion", "Cortante y torsión"), ("detailing", "Disposiciones"),
                       ("sls", "ELS tensiones y fisuración"), ("deflection", "Flechas")):
        L += ["", f"## Anexo: {title} (caso final {fin})", ""]
        rows = [x for x in T[key] if x["case"] == fin]
        L.append(_md_table(rows, ["member", "section", "pos_m", "check", "demand", "capacity", "unit", "eta", "ok",
                                  "combo", "in_verdict"]))
    L += ["", "## Supuestos", ""] + [f"- {a}" for a in meta["assumptions"]]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return _f(o, 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, Mode):
        return o.value
    return o


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--no-search", action="store_true", help="skip the reinforcement search")
    ap.add_argument("--out", default=str(OUT_DIR), help="output directory")
    a = ap.parse_args(argv)
    res = run(do_search=not a.no_search, verbose=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "vigas.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    write_md(res, out / "vigas.md")
    print(f"written {out / 'vigas.json'} and {out / 'vigas.md'} ({res['meta']['runtime_s']} s)")
    for k, v in res["summary"].items():
        print(f"  {k:4s} {v['label']:28s} {v['verdict']:10s} " + "  ".join(
            f"{c}:{s['verdict']}" for c, s in v["cases"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
