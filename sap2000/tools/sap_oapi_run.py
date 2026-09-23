"""Build, run and post-process the Muelle de Trasmallo model in SAP2000 through the CSI OAPI.

Runs on Windows with SAP2000 v20 or later installed (Python 3.9+):

    pip install comtypes openpyxl
    python tools\\sap_oapi_run.py                    # start SAP2000, build the model, run, compare
    python tools\\sap_oapi_run.py --attach           # use the SAP2000 window that is already open
    python tools\\sap_oapi_run.py --from-s2k output\\Muelle_Trasmallo_40m.$2k   # import the .$2k

The model is built from the same data as the .$2k file (model/trasmallo.py).  After the
analysis the script reads, for every load pattern, the pile base reactions, the pile forces
and the transverse-beam forces, and writes

    output/resultados_SAP2000.xlsx     raw SAP2000 results (SAP2000 sign conventions)
    output/comparacion_SAP2000.md      comparison with Anejo 10 / CYPECAD (+ .csv / .json)

Combinations are compared by superposition of the load-pattern results with the CYPE factors
(identical to the ELU/CIM/ELS combinations defined in the model).

OAPI conventions used (CSI OAPI documentation): every call returns 0 on success; with
comtypes, a call with ByRef arguments returns a list whose LAST element is the return code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(HERE))

import trasmallo as tm  # noqa: E402
from compare import build_report, load_ref, write_report  # noqa: E402

KN_M_C = 6            # eUnits.kN_m_C
DIR_GRAVITY = 10      # load direction "Gravity" (positive downwards)
PATTERN_TYPE = {"Dead": 1, "Super Dead": 2, "Live": 3, "Other": 8}   # eLoadPatternType


def rc(ret):
    return ret[-1] if isinstance(ret, (list, tuple)) else ret


def check(ret, what: str):
    code = rc(ret)
    if code != 0:
        raise RuntimeError(f"SAP2000 OAPI call failed (return code {code}): {what}")
    return ret


# ------------------------------------------------------------------------------------------
def connect(attach: bool):
    import comtypes.client

    helper = comtypes.client.CreateObject("SAP2000v1.Helper")
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    if attach:
        sap = helper.GetObject("CSI.SAP2000.API.SapObject")
    else:
        sap = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
        sap.ApplicationStart()
    return sap, sap.SapModel


def define_model(m, model: dict) -> None:
    check(m.InitializeNewModel(KN_M_C), "InitializeNewModel")
    check(m.File.NewBlank(), "File.NewBlank")
    check(m.SetPresentUnits(KN_M_C), "SetPresentUnits")

    # ---- materials (eMatType Concrete = 2) --------------------------------------------------
    for mat in model["materials"]:
        if mat.kind != "Concrete":
            continue          # the rebar grade does not enter a linear analysis
        check(m.PropMaterial.SetMaterial(mat.name, 2), f"SetMaterial {mat.name}")
        check(m.PropMaterial.SetMPIsotropic(mat.name, mat.E, mat.nu, mat.alpha), f"SetMPIsotropic {mat.name}")
        check(m.PropMaterial.SetWeightAndMass(mat.name, 1, mat.unit_weight), f"SetWeightAndMass {mat.name}")
        # Fc, IsLightweight, FcsFactor, SSType 1 (parametric simple), SSHysType 2 (Takeda),
        # StrainAtFc, StrainUltimate, FinalSlope
        check(m.PropMaterial.SetOConcrete_1(mat.name, mat.fc, False, 0, 1, 2, 0.002, 0.0035, -0.1),
              f"SetOConcrete_1 {mat.name}")

    # ---- frame sections -----------------------------------------------------------------------
    for fs in model["sections"].values():
        p = fs.section.props
        if fs.shape == "Rectangular":
            check(m.PropFrame.SetRectangle(fs.name, fs.material, p["t3"], p["t2"]), f"SetRectangle {fs.name}")
        else:
            # order: T3, T2, Area, As2, As3, Torsion, I22, I33, S22, S33, Z22, Z33, R22, R33
            check(m.PropFrame.SetGeneral(fs.name, fs.material, p["t3"], p["t2"], p["Area"], p["AS2"],
                                         p["AS3"], p["TorsConst"], p["I22"], p["I33"], p["S22"],
                                         p["S33"], p["Z22"], p["Z33"], p["R22"], p["R33"]),
                  f"SetGeneral {fs.name}")
        mods = [float(fs.modifiers.get(k, 1.0)) for k in
                ("AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod", "MMod", "WMod")]
        check(m.PropFrame.SetModifiers(fs.name, mods), f"PropFrame.SetModifiers {fs.name}")

    # ---- slab shells: ShellType 1 = shell-thin; orthotropic through stiffness modifiers --------
    for sl in model["slab_sections"].values():
        check(m.PropArea.SetShell_1(sl["name"], 1, True, sl["material"], 0.0, sl["thickness"],
                                    sl["thickness"]), f"SetShell_1 {sl['name']}")
        # f11, f22, f12, m11, m22, m12, v13, v23, mass, weight
        check(m.PropArea.SetModifiers(sl["name"], [1.0, 1.0, 1.0, sl["m11"], sl["m22"], sl["m12"],
                                                   1.0, 1.0, sl["mass_mod"], sl["weight_mod"]]),
              f"PropArea.SetModifiers {sl['name']}")

    # ---- joints -------------------------------------------------------------------------------
    for name, (x, y, z) in model["joints"].items():
        got = check(m.PointObj.AddCartesian(x, y, z, "", name, "Global"), f"AddCartesian {name}")[0]
        if got != name:
            raise RuntimeError(f"joint {name} was created as {got} (duplicate position?)")
    for name, r in model["restraints"].items():
        check(m.PointObj.SetRestraint(name, list(r)), f"SetRestraint {name}")

    # ---- frames -------------------------------------------------------------------------------
    for f in model["frames"]:
        got = check(m.FrameObj.AddByPoint(f["i"], f["j"], "", f["section"], f["name"]),
                    f"FrameObj.AddByPoint {f['name']}")[0]
        if got != f["name"]:
            raise RuntimeError(f"frame {f['name']} was created as {got}")
        if f.get("angle"):
            check(m.FrameObj.SetLocalAxes(f["name"], f["angle"]), f"SetLocalAxes {f['name']}")
        # MyType 1 = maximum segment size, MinSections, output at element ends and point loads
        check(m.FrameObj.SetOutputStations(f["name"], 1, f["station_max"], 2, False, False),
              f"SetOutputStations {f['name']}")
        if f.get("offsets") and any(f["offsets"]):
            # user-defined rigid end zones: AutoOffset False, Length1, Length2, RZ = 1
            check(m.FrameObj.SetEndLengthOffset(f["name"], False, f["offsets"][0], f["offsets"][1], 1.0),
                  f"SetEndLengthOffset {f['name']}")

    # ---- shells -------------------------------------------------------------------------------
    for a in model["areas"]:
        ret = check(m.AreaObj.AddByPoint(4, list(a["joints"]), "", a["section"], a["name"]),
                    f"AreaObj.AddByPoint {a['name']}")
        if ret[-2] != a["name"]:
            raise RuntimeError(f"area {a['name']} was created as {ret[-2]}")

    # ---- rigid deck diaphragm (constraint axis Z = 3) ----------------------------------------
    d = model["diaphragm"]
    check(m.ConstraintDef.SetDiaphragm(d["name"], 3, "Global"), "SetDiaphragm")
    for j in d["joints"]:
        check(m.PointObj.SetConstraint(j, d["name"]), f"SetConstraint {j}")

    # ---- groups -------------------------------------------------------------------------------
    for g, objs in model["groups"].items():
        check(m.GroupDef.SetGroup(g), f"SetGroup {g}")
        for kind, name in objs:
            obj = {"Joint": m.PointObj, "Frame": m.FrameObj, "Area": m.AreaObj}[kind]
            check(obj.SetGroupAssign(name, g), f"SetGroupAssign {name} -> {g}")

    # ---- load patterns (each creates its linear static case) ----------------------------------
    for name, dt, sw, _ in tm.LOAD_PATTERNS:
        check(m.LoadPatterns.Add(name, PATTERN_TYPE[dt], float(sw), True), f"LoadPatterns.Add {name}")
    for fn, arg in ((m.LoadCases.Delete, "DEAD"), (m.LoadPatterns.Delete, "DEAD"),
                    (m.LoadCases.Delete, "MODAL")):
        try:                                   # default objects of a blank model, not used
            fn(arg)
        except Exception:
            pass

    for jl in model["joint_loads"]:
        check(m.PointObj.SetLoadForce(jl["joint"], jl["pattern"], list(jl["F"]), False, "Global"),
              f"SetLoadForce {jl['joint']} {jl['pattern']}")
    for fl in model["frame_loads"]:
        # MyType 1 = force per length, Dir 10 = gravity, relative distances 0 -> 1
        check(m.FrameObj.SetLoadDistributed(fl["frame"], fl["pattern"], 1, DIR_GRAVITY, 0.0, 1.0,
                                            fl["w"], fl["w"], "Global", True, False),
              f"SetLoadDistributed {fl['frame']} {fl['pattern']}")
    for al in model["area_loads"]:
        check(m.AreaObj.SetLoadUniform(al["area"], al["pattern"], al["q"], DIR_GRAVITY, False, "Global"),
              f"SetLoadUniform {al['area']} {al['pattern']}")

    # ---- combinations (ComboType 0 = linear additive, 1 = envelope; CNameType 0 case, 1 combo)
    for fam, combos in tm.COMBOS.items():
        for k, fac in enumerate(combos, start=1):
            cname = f"{fam}{k:02d}"
            check(m.RespCombo.Add(cname, 0), f"RespCombo.Add {cname}")
            for pat, sf in zip(tm.PATTERN_ORDER, fac):
                if sf:
                    check(m.RespCombo.SetCaseList(cname, 0, pat, float(sf)), f"SetCaseList {cname} {pat}")
        env = f"ENV_{fam}"
        check(m.RespCombo.Add(env, 1), f"RespCombo.Add {env}")
        for k in range(1, len(combos) + 1):
            check(m.RespCombo.SetCaseList(env, 1, f"{fam}{k:02d}", 1.0), f"SetCaseList {env}")


# ------------------------------------------------------------------------------------------
# results
# ------------------------------------------------------------------------------------------
def select_cases(m, cases: list[str]) -> None:
    check(m.Results.Setup.DeselectAllCasesAndCombosForOutput(), "DeselectAllCasesAndCombosForOutput")
    for c in cases:
        check(m.Results.Setup.SetCaseSelectedForOutput(c), f"SetCaseSelectedForOutput {c}")


def joint_react(m, joint: str) -> list[dict]:
    r = check(m.Results.JointReact(joint, 0, 0, [], [], [], [], [], [], [], [], [], [], []),
              f"JointReact {joint}")
    n, _obj, _elm, case, _stype, _step, f1, f2, f3, m1, m2, m3 = r[:12]
    return [{"joint": joint, "case": case[k], "F1": f1[k], "F2": f2[k], "F3": f3[k],
             "M1": m1[k], "M2": m2[k], "M3": m3[k]} for k in range(n)]


def joint_displ(m, joint: str) -> list[dict]:
    r = check(m.Results.JointDispl(joint, 0, 0, [], [], [], [], [], [], [], [], [], [], []),
              f"JointDispl {joint}")
    n, _obj, _elm, case, _stype, _step, u1, u2, u3, r1, r2, r3 = r[:12]
    return [{"joint": joint, "case": case[k], "U1": u1[k], "U2": u2[k], "U3": u3[k],
             "R1": r1[k], "R2": r2[k], "R3": r3[k]} for k in range(n)]


def frame_force(m, frame: str) -> list[dict]:
    r = check(m.Results.FrameForce(frame, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [], []),
              f"FrameForce {frame}")
    n, _obj, objsta, _elm, _elmsta, case, _stype, _step, p, v2, v3, t, m2, m3 = r[:14]
    return [{"frame": frame, "station": objsta[k], "case": case[k], "P": p[k], "V2": v2[k],
             "V3": v3[k], "T": t[k], "M2": m2[k], "M3": m3[k]} for k in range(n)]


def base_to_cype(r: dict) -> dict:
    """Support reaction -> CYPE 'arranque' (action of the pile on the foundation)."""
    return {"N": r["F3"], "Mx": -r["M2"], "My": r["M1"], "Qx": -r["F1"], "Qy": -r["F2"], "T": -r["M3"]}


def pile_to_cype(r: dict) -> dict:
    """Pile frame forces (local 1 = +Z, 2 = +X, 3 = +Y) -> CYPE pile forces."""
    return {"N": -r["P"], "Mx": r["M3"], "My": -r["M2"], "Qx": r["V2"], "Qy": r["V3"], "T": r["T"]}


def _interp(rows: list[dict], x: float, key: str) -> float:
    rows = sorted(rows, key=lambda r: r["station"])
    for a, b in zip(rows, rows[1:]):
        if a["station"] - 1e-9 <= x <= b["station"] + 1e-9 and b["station"] > a["station"]:
            t = (x - a["station"]) / (b["station"] - a["station"])
            return a[key] + t * (b[key] - a[key])
    return min(rows, key=lambda r: abs(r["station"] - x))[key]


def extract(m, model: dict) -> dict:
    raw = {"reactions": [], "pile_forces": [], "beam_forces": [], "deck_displacements": []}
    select_cases(m, list(tm.PATTERN_ORDER))
    for j in model["restraints"]:
        for r in joint_react(m, j):
            r["cype"] = model["cype_names"][j]
            raw["reactions"].append(r)
    for f in model["frames"]:
        if f["kind"] == "pile":
            for r in frame_force(m, f["name"]):
                r["cype"] = f["cype"]
                raw["pile_forces"].append(r)
        elif f["kind"] == "beam_t":
            y0 = model["joints"][f["i"]][1]
            for r in frame_force(m, f["name"]):
                r["axis"], r["y"] = f["axis"], y0 + r["station"]
                raw["beam_forces"].append(r)
    for j in model["cype_names"]:
        if not j.startswith("B"):
            for r in joint_displ(m, j):
                r["cype"] = model["cype_names"][j]
                raw["deck_displacements"].append(r)
    return raw


def to_compare_inputs(raw: dict) -> tuple[dict, dict, dict]:
    pile_base: dict = {}
    for r in raw["reactions"]:
        pile_base.setdefault(r["cype"], {})[r["case"]] = base_to_cype(r)
    head_z = tm.PILE_LENGTH - tm.PILE_TOP_RIGID          # pile section at the beam soffit
    pile_head: dict = {}
    for pile in pile_base:
        for pat in tm.PATTERN_ORDER:
            rows = [r for r in raw["pile_forces"] if r["cype"] == pile and r["case"] == pat]
            vals = {k: _interp(rows, head_z, k) for k in ("P", "V2", "V3", "T", "M2", "M3")}
            pile_head.setdefault(pile, {})[pat] = pile_to_cype(vals)
    beams: dict = {}
    for r in raw["beam_forces"]:
        beams.setdefault(r["axis"], {}).setdefault(r["case"], []).append((r["y"], r["M3"], -r["V2"]))
    return pile_base, pile_head, beams


def write_raw(raw: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "resultados_SAP2000.json").write_text(json.dumps(raw, indent=1, default=str))
    try:
        from openpyxl import Workbook
    except ImportError:
        print("openpyxl not installed: raw results written only as JSON")
        return
    wb = Workbook()
    wb.remove(wb.active)
    for key, rows in raw.items():
        if not rows:
            continue
        ws = wb.create_sheet(key[:31])
        cols = list(rows[0].keys())
        ws.append(cols)
        for r in rows:
            ws.append([r.get(c) for c in cols])
    wb.save(out_dir / "resultados_SAP2000.xlsx")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attach", action="store_true", help="attach to the SAP2000 instance already open")
    ap.add_argument("--from-s2k", type=Path, default=None, help="import this .$2k instead of building")
    ap.add_argument("--save", type=Path, default=ROOT / "output" / "Muelle_Trasmallo_40m.sdb")
    ap.add_argument("--ref", type=Path, default=ROOT / "ref" / "cype_reference.json")
    args = ap.parse_args()

    model = tm.build_model()
    sap, m = connect(args.attach)
    if args.from_s2k:
        check(m.File.OpenFile(str(args.from_s2k.resolve())), "File.OpenFile (.$2k import)")
    else:
        define_model(m, model)
    args.save.parent.mkdir(parents=True, exist_ok=True)
    check(m.File.Save(str(args.save.resolve())), "File.Save")
    try:
        m.Analyze.SetRunCaseFlag("MODAL", False)
    except Exception:
        pass
    check(m.Analyze.RunAnalysis(), "Analyze.RunAnalysis")

    raw = extract(m, model)
    write_raw(raw, ROOT / "output")
    pile_base, pile_head, beams = to_compare_inputs(raw)
    rep = build_report(pile_base, pile_head, beams, load_ref(args.ref), "SAP2000")
    path = write_report(rep, ROOT / "output", "comparacion_SAP2000")
    print(f"SAP2000 model saved: {args.save}")
    print(f"comparison with Anejo 10: {path}")


if __name__ == "__main__":
    main()
