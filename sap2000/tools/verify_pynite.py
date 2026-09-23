"""Independent check of the SAP2000 model data with an open-source 3D frame solver (PyNite).

SAP2000 does not run on Linux, so this script re-analyses the same model data
(``model/trasmallo.py``) with PyNiteFEA and compares the pile base reactions with the CYPECAD
listing (Anejo 10, Apéndice 1 §3.4 "Arranques de pilares por hipótesis").  It validates the
geometry, the loads and their signs and the slab idealisation before the model is run in
SAP2000; it does not replace the SAP2000 analysis.

Idealisation differences with respect to the SAP2000 model (all minor):
  * the orthotropic slab shell (bending along X only) is represented by beam strips along
    every deck mesh line Y = const with EI = 63550 kN m2/m x tributary width;
  * the rigid deck diaphragm is emulated with stiff pin-ended diagonals in every mesh cell;
  * surface loads are lumped to the four corner joints of each cell;
  * rigid end zones are modelled as very stiff sub-members (SAP2000: end length offsets, RZ=1,
    and stiffness modifiers x100 on beam segments lying wholly inside a pile).

Usage:  python tools/verify_pynite.py [--json out.json] [--ref ref/cype_reference.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "model"))

from Pynite import FEModel3D  # noqa: E402

import trasmallo as tm  # noqa: E402


# Our axes (X along pier, Y across, Z up) -> PyNite axes with Y up: (x, y, z) -> (x, z, -y)
def P(x: float, y: float, z: float) -> tuple[float, float, float]:
    return (x, z, -y)


def vecP(vx: float, vy: float, vz: float) -> tuple[float, float, float]:
    return (vx, vz, -vy)


def segments(model: dict, fr: dict) -> list[tuple[str, str, str, bool]]:
    """Split a frame with rigid end zones into (name, node_a, node_b, is_rigid) pieces."""
    if fr.get("rigid"):
        return [(fr["name"], fr["i"], fr["j"], True)]
    li, lj = fr.get("offsets") or (0.0, 0.0)
    if li <= 0 and lj <= 0:
        return [(fr["name"], fr["i"], fr["j"], False)]
    extra = model.setdefault("_extra_nodes", {})
    (x1, y1, z1), (x2, y2, z2) = model["joints"][fr["i"]], model["joints"][fr["j"]]
    L = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5

    def at(d: float) -> tuple[float, float, float]:
        t = d / L
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1), z1 + t * (z2 - z1))

    out, a = [], fr["i"]
    if li > 0:
        n = f"{fr['name']}_RI"
        extra[n] = at(li)
        out.append((f"{fr['name']}_ZI", a, n, True))
        a = n
    b = fr["j"]
    if lj > 0:
        n = f"{fr['name']}_RJ"
        extra[n] = at(L - lj)
        out.append((fr["name"], a, n, False))
        out.append((f"{fr['name']}_ZJ", n, b, True))
    else:
        out.append((fr["name"], a, b, False))
    return out


def build(model: dict) -> FEModel3D:
    fe = FEModel3D()
    for name, (x, y, z) in model["joints"].items():
        fe.add_node(name, *P(x, y, z))
    for mat in model["materials"]:
        if mat.kind == "Concrete":
            fe.add_material(mat.name, mat.E, mat.E / (2 * (1 + mat.nu)), mat.nu, mat.unit_weight)
    fe.add_material("RIGID", 1e11, 4e10, 0.25, 0.0)
    fe.add_section("BRACE", 1.0, 1e-9, 1e-9, 1e-9)

    for sname, fs in model["sections"].items():
        p = fs.section.props
        fe.add_section(sname, p["Area"] * fs.modifiers.get("AMod", 1.0), p["I22"], p["I33"],
                       p["TorsConst"])
    fe.add_section("RIGIDZONE", 10.0, 10.0, 10.0, 10.0)
    for fr in model["frames"]:
        fs = model["sections"][fr["section"]]
        for seg, a, b, rigid in segments(model, fr):
            if a not in fe.nodes:
                fe.add_node(a, *P(*model["_extra_nodes"][a]))
            if b not in fe.nodes:
                fe.add_node(b, *P(*model["_extra_nodes"][b]))
            fe.add_member(seg, a, b, "RIGID" if rigid else fs.material,
                          "RIGIDZONE" if rigid else fr["section"])

    # slab strips along X on every mesh line (one-way bending stiffness of the plates)
    xs, ys = model["mesh"]["xs"], model["mesh"]["ys"]
    slab = model["slab"]
    E_slab = next(m.E for m in model["materials"] if m.name == slab["material"])
    for iy, y in enumerate(ys):
        lo = (y - ys[iy - 1]) / 2 if iy > 0 else 0.0
        hi = (ys[iy + 1] - y) / 2 if iy < len(ys) - 1 else 0.0
        trib = lo + hi
        for tag, fac in (("", 1.0), ("E", model["slab_sections"][tm.SLAB_END_SECTION]["factor"])):
            fe.add_section(f"STRIP{tag}_{iy}", 1e-6, 1e-9, slab["EI_span"] * trib * fac / E_slab, 1e-9)
        for ix in range(len(xs) - 1):
            tag = "E" if ix in (0, len(xs) - 2) else ""
            fe.add_member(f"S_{ix}_{iy}", f"D{ix:02d}_{iy}", f"D{ix + 1:02d}_{iy}",
                          slab["material"], f"STRIP{tag}_{iy}")

    # diaphragm emulation: pin-ended stiff diagonals in every slab cell
    for ar in model["areas"]:
        j1, j2, j3, j4 = ar["joints"]
        for k, (a, b) in enumerate(((j1, j3), (j2, j4))):
            mn = f"DG_{ar['name']}_{k}"
            fe.add_member(mn, a, b, "RIGID", "BRACE")
            fe.def_releases(mn, Ryi=True, Rzi=True, Rxj=True, Ryj=True, Rzj=True)

    for name, rs in model["restraints"].items():
        fe.def_support(name, *rs)
    return fe


def apply_loads(fe: FEModel3D, model: dict) -> None:
    frames = {f["name"]: f for f in model["frames"]}
    for fr in model["frames"]:                               # self weight (pattern PP)
        fs = model["sections"][fr["section"]]
        gamma = next(m.unit_weight for m in model["materials"] if m.name == fs.material)
        w = fs.section.props["Area"] * gamma * fs.modifiers.get("WMod", 1.0)
        for seg, *_ in segments(model, fr):
            fe.add_member_dist_load(seg, "FY", -w, -w, case="PP")
    for fl in model["frame_loads"]:
        for seg, *_ in segments(model, frames[fl["frame"]]):
            fe.add_member_dist_load(seg, "FY", -fl["w"], -fl["w"], case=fl["pattern"])
    areas = {a["name"]: a for a in model["areas"]}
    nodal: dict[tuple[str, str], float] = {}
    for al in model["area_loads"]:
        js = areas[al["area"]]["joints"]
        (x1, y1, _), (x3, y3) = model["joints"][js[0]], model["joints"][js[2]][:2]
        F = al["q"] * abs((x3 - x1) * (y3 - y1)) / 4.0
        for j in js:
            nodal[(j, al["pattern"])] = nodal.get((j, al["pattern"]), 0.0) + F
    for (j, pat), F in nodal.items():
        fe.add_node_load(j, "FY", -F, case=pat)
    for jl in model["joint_loads"]:
        f1, f2, f3, m1, m2, m3 = jl["F"]
        fx, fy, fz = vecP(f1, f2, f3)
        mx, my, mz = vecP(m1, m2, m3)
        for d, v in (("FX", fx), ("FY", fy), ("FZ", fz), ("MX", mx), ("MY", my), ("MZ", mz)):
            if abs(v) > 0:
                fe.add_node_load(jl["joint"], d, v, case=jl["pattern"])


def beam_line(fe: FEModel3D, model: dict, axis: int, pat: str, n: int = 6) -> list[tuple[float, float, float]]:
    """(y, M, V, segment) along the transverse beam of an axis for one pattern; M > 0 sagging.
    Rigid sub-members (inside the piles) are included: their shear at the pile face is the
    total shear delivered to the pile, including the slab load at the face node."""
    out = []
    for fr in model["frames"]:
        if fr["kind"] != "beam_t" or fr["axis"] != axis:
            continue
        for seg, a, b, rigid in segments(model, fr):
            mem = fe.members[seg]
            ya = model["joints"].get(a, model.get("_extra_nodes", {}).get(a))[1]
            yb = model["joints"].get(b, model.get("_extra_nodes", {}).get(b))[1]
            L = mem.L()
            for k in range(n + 1):
                x = L * k / n
                y = ya + (yb - ya) * k / n
                out.append((y, -mem.moment("Mz", x, pat), mem.shear("Fy", x, pat), seg))
    out.sort()
    return out


def run(model: dict, with_fe: bool = False):
    fe = build(model)
    apply_loads(fe, model)
    for pat in tm.PATTERN_ORDER:
        fe.add_load_combo(pat, {pat: 1.0})
    fe.analyze(check_statics=False, log=False, check_stability=False)
    out = {}
    for b, cname in model["cype_names"].items():
        if not b.startswith("B"):
            continue
        n = fe.nodes[b]
        out[cname] = {}
        for pat in tm.PATTERN_ORDER:
            # reactions back to our axes: X = X_P, Y = -Z_P, Z = Y_P
            out[cname][pat] = {
                "FX": n.RxnFX[pat], "FY": -n.RxnFZ[pat], "FZ": n.RxnFY[pat],
                "MX": n.RxnMX[pat], "MY": -n.RxnMZ[pat], "MZ": n.RxnMY[pat],
            }
    return (out, fe) if with_fe else out


def to_cype(r: dict) -> dict:
    """SAP/global base reaction -> CYPE 'arranque' components (pile local axes = global).
    N = FZ; Qx = -FX; Qy = -FY; Mx = -MY; My = MX   (sign mapping derived in README)."""
    return {"N": r["FZ"], "Mx": -r["MY"], "My": r["MX"], "Qx": -r["FX"], "Qy": -r["FY"],
            "T": -r["MZ"]}


def pile_head_forces(fe: FEModel3D, model: dict, pat: str, pile: str) -> dict:
    """CYPE-convention forces in a pile 6.70 m above the base (end of the flexible part)."""
    fr = next(f for f in model["frames"] if f["kind"] == "pile" and f["cype"] == pile)
    seg = next(sg for sg, a, b, rigid in segments(model, fr) if not rigid)
    mem = fe.members[seg]
    L = mem.L()
    # PyNite local axes of a vertical member (i at the base): take global quantities from the
    # base reaction and statics instead of relying on the local-axis orientation.
    base = fe.nodes[fr["i"]]
    FX, FY, FZ = base.RxnFX[pat], -base.RxnFZ[pat], base.RxnFY[pat]
    MX, MY, MZ = base.RxnMX[pat], -base.RxnMZ[pat], base.RxnMY[pat]
    w = model["sections"]["PILOTE_40x40"].section.props["Area"] * tm.GAMMA_CONCRETE * \
        model["sections"]["PILOTE_40x40"].modifiers.get("WMod", 1.0) if pat == "PP" else 0.0
    z = L
    # internal forces of the part below the cut, CYPE convention (action on the lower part)
    N = FZ - w * z
    Qx, Qy = -FX, -FY
    # moment acting on the lower part at the cut: M_top = -(M_reac + ((-z e3) x F_reac))
    My = MX + FY * z          # My = -M_top,X = MX + z*FY
    Mx = -(MY - FX * z)       # Mx = +M_top,Y = -(MY - z*FX)
    return {"N": N, "Mx": Mx, "My": My, "Qx": Qx, "Qy": Qy, "T": -MZ}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", type=Path, default=ROOT / "ref" / "cype_reference.json")
    ap.add_argument("--out", type=Path, default=ROOT / "output" / "verificacion_pynite")
    args = ap.parse_args()

    from compare import build_report, load_ref, write_report

    model = tm.build_model()
    res, fe = run(model, with_fe=True)
    pile_base = {p: {pat: to_cype(r) for pat, r in by.items()} for p, by in res.items()}
    pile_head = {p: {pat: pile_head_forces(fe, model, pat, p) for pat in tm.PATTERN_ORDER}
                 for p in res}
    beams = {a: {pat: beam_line(fe, model, a, pat) for pat in tm.PATTERN_ORDER}
             for a in range(1, tm.N_AXES + 1)}
    rep = build_report(pile_base, pile_head, beams, load_ref(args.ref), "PyNite (verificación)")
    path = write_report(rep, args.out.parent, args.out.name)
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
