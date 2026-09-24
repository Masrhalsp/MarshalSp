"""Seismic design checks (accidental situation) of the piles and the transverse beams of one 40 m
module of the Muelle de Trasmallo, with the response-spectrum envelopes of ``sismo/modal.py`` and
the static SAP2000 forces of ``esfuerzos.py``.

Combinations (trasmallo.seismic_combos(), Código Estructural Anejo 18, Rover §5.1.3.4):

    SIS{L}Q = PP + CM + 0.8·Qa ± (1.0·E_L + 0.3·E_other1 + 0.3·E_other2)       L = X, Y, Z
    SIS{L}  = PP + CM          ± (...)                                        (Qa not critical)

E_d = SRSS envelope of the RS case of direction d (positive); the directional sum is taken per
component (as SAP2000 adds RS cases in a linear combination).  Every sign corner of the seismic
part is checked, the same sign along the member ('consistent'):
    piles N-M:   (N±, MEd,x±, MEd,y±)            8 corners x 6 combinations
    piles shear: (N±, VEd,x±, VEd,y±)            8 corners x 6
    beams:       M ± E_M, V ± E_V (T ± E_T information)
This is the usual envelope design (independent signs, conservative with respect to the modal
correlation of N and M).

Materials: accidental partial factors, CE Anejo 19 Tabla A19.2.1: γc = 1.3, γs = 1.0 (fcd = fck/1.3,
fyd = fyk); the shear links keep fywd = 0.8·fywk = 400 MPa (NOTA of A19.6.2.3(3) with ν1 = 0.6),
the hanger steel of the ledges fyd = 500 MPa.

Engines reused unchanged: ``pilotes.uls_nm`` (N-Mx-My first order with emin and second order by
nominal curvature, exact ray utilisation) and ``pilotes.uls_shear`` with Mode.CODIGO rules on the
provided 12Ø25 layout carrying the accidental Concrete/Steel; beam bending with
``RCSection.capacity_uniaxial`` of the provided / proposed layouts (vigas.json proposal) and shear
with the formulas of vigas.py ((6.8), (6.9), (6.2)) evaluated with the accidental fcd.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DISENO = HERE.parent
for _p in (str(HERE), str(DISENO / "codigo"), str(DISENO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import esfuerzos as E  # noqa: E402
import modal as S  # noqa: E402
import pilotes  # noqa: E402
import vigas  # noqa: E402
import armado_vigas as AV  # noqa: E402
from armado_pilote import PROVIDED  # noqa: E402
from seccion import KN, KNM, Concrete, Mode, Steel  # noqa: E402

tm = S.tm
OUT = DISENO / "output"
GAMMA_C_ACC, GAMMA_S_ACC = 1.3, 1.0                      # CE Anejo 19 Tabla A19.2.1 (accidental)
STEEL_ACC = Steel(gamma_s=GAMMA_S_ACC)
FYWD = 0.8 * STEEL_ACC.fyk                               # 400 MPa (NOTA A19.6.2.3(3), ν1 = 0.6)
NU1 = 0.6
DIRS = S.DIRS
PILE_SECTION_COMPS = (0, 2, 1, 3, 4)                     # env (N, Mx, My, Qx, Qy, T) -> (N, MEd,x=My, MEd,y=Mx, VEd,x, VEd,y)


def concrete_acc(c: Concrete) -> Concrete:
    return replace(c, gamma_c=GAMMA_C_ACC)


def pile_layouts_acc() -> dict:
    return {z: lay.with_(concrete=concrete_acc(lay.concrete), steel=STEEL_ACC) for z, lay in PROVIDED.items()}


def seismic_combos() -> dict:
    """name -> (static factors on E.PATTERNS, {direction: factor})"""
    out = {}
    for name, c in tm.seismic_combos().items():
        st = tuple(c["static"].get(p, 0.0) for p in E.PATTERNS)
        out[name] = (st, {d: c["rs"][S.CASE_OF[d]] for d in DIRS})
    return out


def _sgn(s: int) -> str:
    return "+" if s > 0 else "-"


# =============================================================================================
# piles
# =============================================================================================
def pile_forces_ext(static: dict, env: dict, scale: float = 1.0) -> dict:
    """PileForces with 6 static + 15 seismic 'patterns' (direction x component, one non-zero
    component each) at the static stations."""
    out = {}
    for pile, pf in static.items():
        ns = len(pf.z)
        ext = np.zeros((ns, 6 + 15, 5))
        ext[:, :6, :] = pf.vals
        for i, d in enumerate(DIRS):
            e = env[pile][d][:, PILE_SECTION_COMPS] * scale
            for c in range(5):
                ext[:, 6 + 5 * i + c, c] = e[:, c]
        out[pile] = pilotes.PileForces(pile, pf.z, ext)
    return out


def pile_combos(kind: str) -> dict[str, tuple]:
    """Factor tuples on the 21 patterns for 'nm' (N, MEd,x, MEd,y corners) or 'v' (N, VEd,x, VEd,y)."""
    out = {}
    comps = (0, 1, 2) if kind == "nm" else (0, 3, 4)
    labels = ("N", "Mx", "My") if kind == "nm" else ("N", "Vx", "Vy")
    for name, (st, fd) in seismic_combos().items():
        for signs in itertools.product((1, -1), repeat=3):
            fac = list(st)
            for d in DIRS:
                per = [0.0] * 5
                for c, s in zip(comps, signs):
                    per[c] = fd[d] * s
                fac += per
            tag = ",".join(f"{l}{_sgn(s)}" for l, s in zip(labels, signs))
            out[f"{name}[{tag}]"] = tuple(fac)
    return out


def static_pile_etas(P: dict | None = None) -> dict:
    """Governing static η per pile from pilotes.json (final basis ROM / Mode.CODIGO)."""
    P = P or json.loads((OUT / "pilotes.json").read_text(encoding="utf-8"))
    out = {}
    for r in P["tables"]["uls_nm"]:
        if r.get("eta") is None:
            continue
        o = out.setdefault(r["pile"], {"nm": 0.0, "nm_where": "", "v": 0.0})
        if r["eta"] > o["nm"]:
            o["nm"], o["nm_where"] = r["eta"], f"{r['position']} {r['check']} {r['combo']}"
    for r in P["tables"]["shear"]:
        if r.get("key") == "verdict" and r["pile"] in out:
            out[r["pile"]]["v"] = max(out[r["pile"]]["v"], r["eta"])
    return out


def check_piles(rs: S.RSResult, scale: float = 1.0, static=None) -> dict:
    static = static or pilotes.load_forces()
    env = S.pile_envelopes(rs, {p: pf.z for p, pf in static.items()})
    forces = pile_forces_ext(static, env, scale)
    lays = pile_layouts_acc()
    rules = pilotes.RULES[Mode.CODIGO]
    nm = pilotes.uls_nm(forces, pile_combos("nm"), lays, rules, exact="governing", screening=False)
    v = pilotes.uls_shear(forces, pile_combos("v"), lays, rules)
    for r in nm["rows"] + v["rows"]:
        r.pop("combo_desc", None)
    return {"nm": nm["rows"], "shear": v["rows"], "env": env}


def pile_summary(res: dict, static_eta: dict) -> list[dict]:
    rows = []
    for pile in pilotes.PILES:
        nm = [r for r in res["nm"] if r["pile"] == pile and r.get("eta") is not None]
        g = max(nm, key=lambda r: r["eta"])
        g1 = max((r for r in nm if r["check"] == "nm1"), key=lambda r: r["eta"])
        vv = [r for r in res["shear"] if r["pile"] == pile and r["key"] == "verdict"]
        gv = max(vv, key=lambda r: r["eta"])
        s = static_eta.get(pile, {})
        rows.append({"pile": pile, "eta_nm1": g1["eta"], "eta_nm": g["eta"], "check": g["check"],
                     "position": g["position"], "combo": g["combo"], "N": g["N"], "MEd_x": g["MEd_x"],
                     "MEd_y": g["MEd_y"], "MRd_x": g.get("MRd_x"), "MRd_y": g.get("MRd_y"),
                     "eta_v": gv["eta"], "v_position": gv["position"], "v_combo": gv["combo"],
                     "VEd": gv["demand"], "eta_nm_static": s.get("nm"), "eta_v_static": s.get("v"),
                     "static_where": s.get("nm_where")})
    return rows


# =============================================================================================
# transverse beams
# =============================================================================================
def proposed_beam(axis: int, V: dict | None = None):
    """Proposed reinforcement of diseno_final (vigas.json 'proposal'): inner beams 8Ø20 + 4Ø16
    bottom; end beams unchanged."""
    r = AV.provided(axis)
    if axis in (1, tm.N_AXES):
        return r
    V = V or json.loads((OUT / "vigas.json").read_text(encoding="utf-8"))
    key = next(k for k in V["proposal"] if k.startswith("inner"))
    rows = [x for x in V["proposal"][key]["layout"] if x["member"] == "VT2"]
    groups, st = [], r.stirrups
    for x in rows:
        if x["face"] == "stirrups":
            continue
        groups.append(AV.BarGroup(x["group"], float(x["phi"]), tuple(float(v) for v in x["x_mm"]),
                                  float(x["y_soffit_mm"]), x["face"], bool(x.get("active_cype", True)),
                                  bool(x.get("active_codigo", True)), x.get("src", "")))
    new = replace(r, groups=groups)
    return vigas._apply_layout(r, new)


def _acc(r):
    return replace(r, concrete=concrete_acc(r.concrete), steel=STEEL_ACC)


_MRD: dict = {}


def mrd_acc(r, face: str) -> float:
    """MRd [kN·m] with the ``face`` in tension, N = 0, accidental materials, Mode.CODIGO."""
    key = (r.geom, tuple(r.groups), face)
    if key not in _MRD:
        sec = _acc(r).section(Mode.CODIGO)
        _MRD[key] = abs(sec.capacity_uniaxial(0.0, +1 if face == "bottom" else -1)["Mx"]) / KNM
    return _MRD[key]


def _station_env(rs: S.RSResult, frame: str, y: float) -> dict:
    return {d: S.srss([rs.rec.beam_frame(D, frame, y) for D in rs.modal_disp[d]]) for d in DIRS}


def beam_seismic_stations(rs: S.RSResult, members: list) -> dict:
    """{member key: [(station, {d: (M, V, T)})]} for every non-rigid SAP station."""
    out = {}
    for m in members:
        lst = []
        for s in m.stations:
            lst.append((s, _station_env(rs, s.frame, s.pos)))
        out[m.key] = lst
    return out


def _static(values: dict, fac: tuple) -> dict:
    return E.combine(values, fac, E.COMPS_BEAM)


def _cot_opt(V_kN: float, bw: float, z: float, fcd: float) -> float:
    K = abs(V_kN) * 1e3 / (bw * z * NU1 * fcd)
    if K <= 0:
        return 2.0
    inv = 1 / K
    if inv < 2:
        return 1.0
    return min(2.0, (inv + math.sqrt(inv * inv - 4)) / 2)


def check_beams(rs: S.RSResult, scale: float = 1.0, data: dict | None = None, V: dict | None = None) -> dict:
    data = data or E.load_stations()
    members = [vigas.transverse_member(a, data["beams"][a]) for a in range(1, tm.N_AXES + 1)]
    senv = beam_seismic_stations(rs, members)
    combos = seismic_combos()
    rows, env_rows = [], []
    for m in members:
        axis = int(m.key[2:])
        variants = [("dispuesto", AV.provided(axis))]
        if axis not in (1, tm.N_AXES):
            variants.append(("propuesto", proposed_beam(axis, V)))
        by_pos = senv[m.key]
        # seismic envelope table (information)
        for f in m.faces:
            at = [(s, e) for s, e in by_pos if abs(s.pos - f.pos) < 1e-4 and not s.rigid]
            if at:
                env_rows.append({"member": m.key, "section": f.name, "y": f.pos,
                                 **{f"{c}_{d}": float(max(e[d][k] for _, e in at)) * scale
                                    for d in DIRS for k, c in enumerate(("M", "V", "T"))}})

        def demands(sel):
            """max sagging / hogging M and max |V|, |T| over the stations ``sel`` and the combos."""
            best = {"sag": (0.0, ""), "hog": (0.0, ""), "V": (0.0, ""), "T": (0.0, "", 0.0)}
            for s, e in sel:
                for name, (fac, fd) in combos.items():
                    st = _static(s.values, fac)
                    Ed = sum(fd[d] * e[d] for d in DIRS) * scale
                    for sg in (1, -1):
                        M = st["M"] + sg * Ed[0]
                        if M > best["sag"][0]:
                            best["sag"] = (M, f"{name}[E{_sgn(sg)}]")
                        if -M > best["hog"][0]:
                            best["hog"] = (-M, f"{name}[E{_sgn(sg)}]")
                        Vv = abs(st["V"]) + Ed[1]
                        if Vv > best["V"][0]:
                            best["V"] = (Vv, name)
                        Tt = abs(st["T"]) + Ed[2]
                        if Tt > best["T"][0]:
                            best["T"] = (Tt, name, Vv)
            return best

        sections = [(f.name, f.pos, [(s, e) for s, e in by_pos if abs(s.pos - f.pos) < 1e-4]) for f in m.faces]
        span = [(s, e) for s, e in by_pos if not s.rigid and 0.20 - 1e-6 <= s.pos <= 3.25 + 1e-6]
        sections.append(("vano (todas las estaciones)", None, span))
        for vname, r in variants:
            for sname, pos, sel in sections:
                dm = demands(sel)
                for face, key in (("bottom", "sag"), ("top", "hog")):
                    M, cmb = dm[key]
                    if M <= 0.5:
                        continue
                    cap = mrd_acc(r, face)
                    rows.append({"member": m.key, "variant": vname, "section": sname, "y": pos,
                                 "check": f"MEd <= MRd ({'sag' if face == 'bottom' else 'hog'})",
                                 "clause": "A19.6.1 (γc 1.3, γs 1.0)", "demand": M, "capacity": cap,
                                 "eta": M / cap, "combo": cmb, "As_cm2": r.As(face) / 100})
            # shear at the support faces
            d_mm = min(r.d("top"), r.d("bottom"))
            z = 0.9 * d_mm
            bw = r.geom.bw
            fcd = concrete_acc(r.concrete).fcd
            st_ = r.stirrups
            tw = vigas.thin_wall(r)
            for f in m.faces:
                sel = [(s, e) for s, e in by_pos if abs(s.pos - f.pos) < 1e-4]
                dm = demands(sel)
                Vf, cmb = dm["V"]
                cot = _cot_opt(Vf, bw, z, fcd)
                vmax = bw * z * NU1 * fcd * cot / (1 + cot * cot) / 1e3
                rows.append({"member": m.key, "variant": vname, "section": f.name, "y": f.pos,
                             "check": "VEd(cara) <= VRd,max", "clause": "A19.6.2.3(3) (6.9)", "demand": Vf,
                             "capacity": vmax, "eta": Vf / vmax, "combo": cmb, "cot_theta": cot})
                # at d from the face (cantilevers: at the face)
                y_d = f.pos + f.dir * d_mm / 1000.0
                if f.kind == "cantilever" or (y_d - f.limit) * f.dir > 0:
                    y_d = f.pos
                    seld = sel
                else:
                    vals = vigas.interp(m.stations, y_d)
                    e = {dd: S.srss([rs.rec.beam(D, axis, [y_d], rigid_ok=False)[0] for D in rs.modal_disp[dd]])
                         for dd in DIRS}
                    seld = [(type("St", (), {"values": v})(), e) for v in vals]
                best = (0.0, "", 0.0)
                for s, e in seld:
                    for name, (fac, fd) in combos.items():
                        Vv = abs(_static(s.values, fac)["V"]) + sum(fd[dd] * e[dd][1] for dd in DIRS) * scale
                        cot_d = _cot_opt(Vv, bw, z, fcd)
                        hang = 0.0
                        if E.tm.PLATE_Y[0] - 1e-9 <= y_d <= E.tm.PLATE_Y[1] + 1e-9:
                            hang = vigas.hanger_load(axis, fac) / STEEL_ACC.fyd          # N/mm = mm2/mm
                        need = Vv * 1e3 / (z * FYWD * cot_d) + hang
                        if need > best[0]:
                            best = (need, name, Vv, cot_d, hang)
                need, name, Vv, cot_d, hang = best
                rows.append({"member": m.key, "variant": vname, "section": f.name, "y": y_d,
                             "check": "estribos V(d) + suspensión alveoplaca", "clause": "A19.6.2.3(3) (6.8) + A19.6.2.1(9)",
                             "demand": need * 10, "capacity": st_.asw_s * 10, "eta": need / st_.asw_s,
                             "combo": name, "V_kN": Vv, "cot_theta": cot_d, "unit": "cm²/m"})
                # torsion + shear interaction (information: not in the bending/shear verdict)
                T, cmbT, VT = dm["T"]
                trdmax = 2 * vigas.NU_T_CE * fcd * tw["Ak"] * tw["tef"] * 0.5 / KNM
                vmax1 = bw * z * NU1 * fcd * 0.5 / 1e3
                rows.append({"member": m.key, "variant": vname, "section": f.name, "y": f.pos,
                             "check": "TEd/TRd,max + VEd/VRd,max (info)", "clause": "A19.6.3.2(4) (6.29)",
                             "demand": T, "capacity": trdmax, "eta": T / trdmax + VT / vmax1, "combo": cmbT,
                             "info": True})
    return {"rows": rows, "env": env_rows}


def static_beam_etas(V: dict | None = None) -> dict:
    """Static governing η per transverse beam (final case CE-ROM): bending, V at face, links."""
    V = V or json.loads((OUT / "vigas.json").read_text(encoding="utf-8"))
    out = {}
    for r in V["tables"]["bending"]:
        if r["case"] == "CE-ROM" and r["member"].startswith("VT") and r.get("in_verdict"):
            o = out.setdefault(r["member"], {"M": 0.0, "Vmax": 0.0, "links": 0.0})
            o["M"] = max(o["M"], r["eta"] or 0.0)
    for r in V["tables"]["shear_torsion"]:
        if r["case"] != "CE-ROM" or not r["member"].startswith("VT"):
            continue
        o = out.setdefault(r["member"], {"M": 0.0, "Vmax": 0.0, "links": 0.0})
        if r["check"] == "VEd(cara) <= VRd,max":
            o["Vmax"] = max(o["Vmax"], r["eta"] or 0.0)
        if r["check"].startswith("estribos V + suspensión"):
            o["links"] = max(o["links"], r["eta"] or 0.0)
    prop = next(v for k, v in V["proposal"].items() if k.startswith("inner"))
    for mkey, ver in prop["verification"].items():
        if mkey in out and "flexión ELU" in ver:
            out[mkey]["M_proposed"] = ver["flexión ELU"]["eta"]
    return out


def beam_summary(res: dict, static_eta: dict) -> list[dict]:
    rows = []
    for a in range(1, tm.N_AXES + 1):
        key = f"VT{a}"
        for vname in ("dispuesto", "propuesto"):
            rr = [r for r in res["rows"] if r["member"] == key and r["variant"] == vname]
            if not rr:
                continue

            def g(pred):
                sel = [r for r in rr if pred(r)]
                return max(sel, key=lambda r: r["eta"]) if sel else None
            b = g(lambda r: r["check"].startswith("MEd"))
            vm = g(lambda r: r["check"].startswith("VEd(cara)"))
            ln = g(lambda r: r["check"].startswith("estribos"))
            t = g(lambda r: r.get("info"))
            s = static_eta.get(key, {})
            rows.append({"member": key, "variant": vname, "eta_M": b["eta"], "M_section": b["section"],
                         "M_check": b["check"], "M_combo": b["combo"], "MEd": b["demand"], "MRd": b["capacity"],
                         "eta_Vmax": vm["eta"], "eta_links": ln["eta"], "links_section": ln["section"],
                         "eta_T_info": t["eta"] if t else None, "TEd_info": t["demand"] if t else None,
                         "eta_M_static": s.get("M_proposed", s.get("M")) if vname == "propuesto" else s.get("M"),
                         "eta_Vmax_static": s.get("Vmax"), "eta_links_static": s.get("links")})
    return rows
