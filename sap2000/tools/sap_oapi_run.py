"""Build, run and post-process the Muelle de Trasmallo model in SAP2000 through the CSI OAPI.

Runs on Windows with SAP2000 (v21 or later) installed:

    pip install comtypes openpyxl
    python tools\\sap_oapi_run.py                      # new SAP2000 instance, build + run
    python tools\\sap_oapi_run.py --attach             # use the SAP2000 window already open
    python tools\\sap_oapi_run.py --from-s2k output\\Muelle_Trasmallo_40m.$2k   # import instead

The model is built from exactly the same data as the .$2k file (model/trasmallo.py).  After the
analysis the script extracts pile base reactions, pile end forces, beam envelopes and deck
displacements for every load pattern and combination and writes

    output/resultados_SAP2000.xlsx      (all results + comparison sheets with Anejo 10 / CYPE)
    output/resultados_SAP2000.json

SAP2000 sign conventions are kept in the raw sheets; the comparison sheets convert the pile
base reactions to the CYPE "arranques" convention (see README, section 6).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "model"))

import trasmallo as tm  # noqa: E402

KN_M_C = 6          # eUnits.kN_m_C
DIR_GRAVITY = 10    # load direction "Gravity"


def check(ret, what: str):
    """OAPI calls return 0 on success; with comtypes a call that has ByRef outputs returns a
    list whose LAST item is the return code."""
    code = ret[-1] if isinstance(ret, (list, tuple)) else ret
    if code != 0:
        raise RuntimeError(f"SAP2000 OAPI call failed ({code}): {what}")
    return ret


# ------------------------------------------------------------------------------------------
# connection
# ------------------------------------------------------------------------------------------
def connect(attach: bool, visible: bool = True):
    import comtypes.client

    if attach:
        sap = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    else:
        helper = comtypes.client.CreateObject("SAP2000v1.Helper")
        helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
        sap = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
        sap.ApplicationStart(KN_M_C, visible, "")
    model = sap.SapModel
    return sap, model


# ------------------------------------------------------------------------------------------
# model definition through the API
# ------------------------------------------------------------------------------------------
def define_model(m, model: dict) -> None:
    check(m.InitializeNewModel(KN_M_C), "InitializeNewModel")
    check(m.File.NewBlank(), "NewBlank")
    check(m.SetPresentUnits(KN_M_C), "SetPresentUnits")

    # materials: eMatType Concrete = 2, Rebar = 6
    for mat in model["materials"]:
        mtype = 2 if mat.kind == "Concrete" else 6
        check(m.PropMaterial.SetMaterial(mat.name, mtype), f"SetMaterial {mat.name}")
        check(m.PropMaterial.SetMPIsotropic(mat.name, mat.E, mat.nu, mat.alpha), f"SetMPIsotropic {mat.name}")
        check(m.PropMaterial.SetWeightAndMass(mat.name, 1, mat.unit_weight), f"SetWeightAndMass {mat.name}")
        if mat.kind == "Concrete":
            # (name, Fc, IsLightweight, FcsFactor, SSType=1 parametric simple, SSHysType=4 Takeda,
            #  StrainAtFc, StrainUltimate, FinalSlope, FrictionAngle, DilatationalAngle)
            check(m.PropMaterial.SetOConcrete_1(mat.name, mat.fc, False, 0, 1, 4, 0.002, 0.0035,
                                                -0.1, 0, 0), f"SetOConcrete_1 {mat.name}")
        else:
            # (name, Fy, Fu, EFy, EFu, SSType=1 simple, SSHysType=1 kinematic, StrainAtHardening,
            #  StrainUltimate, FinalSlope, UseCaltransSSDefaults)
            check(m.PropMaterial.SetORebar_1(mat.name, mat.fy, mat.fu, mat.fy, mat.fu, 1, 1, 0.01,
                                             0.09, -0.1, False), f"SetORebar_1 {mat.name}")

    # frame sections
    for fs in model["sections"].values():
        p = fs.section.props
        if fs.shape == "Rectangular":
            check(m.PropFrame.SetRectangle(fs.name, fs.material, p["t3"], p["t2"]), f"SetRectangle {fs.name}")
        else:
            check(m.PropFrame.SetGeneral(fs.name, fs.material, p["t3"], p["t2"], p["Area"], p["AS2"],
                                         p["AS3"], p["TorsConst"], p["I22"], p["I33"], p["S33"],
                                         p["S22"], p["Z33"], p["Z22"], p["R33"], p["R22"]),
                  f"SetGeneral {fs.name}")
        mods = [fs.modifiers.get(k, 1.0) for k in ("AMod", "A2Mod", "A3Mod", "JMod", "I2Mod",
                                                   "I3Mod", "MMod", "WMod")]
        check(m.PropFrame.SetModifiers(fs.name, mods), f"PropFrame.SetModifiers {fs.name}")

    # slab: thin shell (ShellType 1 = shell-thin), orthotropic behaviour via modifiers
    slab = model["slab"]
    check(m.PropArea.SetShell_1(slab["name"], 1, True, slab["material"], 0.0, slab["thickness"],
                                slab["thickness"]), "SetShell_1")
    # [f11, f22, f12, m11, m22, m12, v13, v23, mass, weight]
    check(m.PropArea.SetModifiers(slab["name"], [1, 1, 1, slab["m11"], slab["m22"], slab["m12"],
                                                 1, 1, slab["mass_mod"], slab["weight_mod"]]),
          "PropArea.SetModifiers")

    # joints
    for name, (x, y, z) in model["joints"].items():
        ret = m.PointObj.AddCartesian(x, y, z, "", name, "Global", True)
        check(ret, f"AddCartesian {name}")
    for name, r in model["restraints"].items():
        check(m.PointObj.SetRestraint(name, list(r)), f"SetRestraint {name}")

    # frames
    for f in model["frames"]:
        check(m.FrameObj.AddByPoint(f["i"], f["j"], "", f["section"], f["name"]), f"AddByPoint {f['name']}")
        if f.get("angle"):
            check(m.FrameObj.SetLocalAxes(f["name"], f["angle"]), f"SetLocalAxes {f['name']}")
        # output stations: type 1 = max segment size
        check(m.FrameObj.SetOutputStations(f["name"], 1, f["station_max"], 2, True, True),
              f"SetOutputStations {f['name']}")
        if f.get("offsets") and any(f["offsets"]):
            # user-defined rigid end zones (AutoOffset=False, Length1, Length2, RZ=1)
            check(m.FrameObj.SetEndLengthOffset(f["name"], False, f["offsets"][0],
                                                f["offsets"][1], 1.0),
                  f"SetEndLengthOffset {f['name']}")

    # areas
    for a in model["areas"]:
        ret = m.AreaObj.AddByPoint(4, a["joints"], "", a["section"], a["name"])
        check(ret, f"AreaObj.AddByPoint {a['name']}")

    # deck diaphragm
    d = model["diaphragm"]
    check(m.ConstraintDef.SetDiaphragm(d["name"], 3, "Global"), "SetDiaphragm")   # 3 = Z axis
    for j in d["joints"]:
        check(m.PointObj.SetConstraint(j, d["name"]), f"SetConstraint {j}")

    # groups
    for g, objs in model["groups"].items():
        check(m.GroupDef.SetGroup(g), f"SetGroup {g}")
        for kind, name in objs:
            obj = {"Joint": m.PointObj, "Frame": m.FrameObj, "Area": m.AreaObj}[kind]
            check(obj.SetGroupAssign(name, g), f"SetGroupAssign {name}")

    # load patterns (eLoadPatternType: Dead 1, SuperDead 2, Live 3, Other 8)
    ptype = {"Dead": 1, "Super Dead": 2, "Live": 3, "Other": 8}
    for name, dt, sw, _ in tm.LOAD_PATTERNS:
        check(m.LoadPatterns.Add(name, ptype[dt], sw, True), f"LoadPatterns.Add {name}")
    # the default DEAD pattern/case created by NewBlank is not used
    try:
        m.LoadPatterns.Delete("DEAD")
    except Exception:
        pass
    try:
        m.LoadCases.Delete("MODAL")
    except Exception:
        pass

    for jl in model["joint_loads"]:
        check(m.PointObj.SetLoadForce(jl["joint"], jl["pattern"], list(jl["F"]), False, "Global"),
              f"SetLoadForce {jl['joint']}")
    for fl in model["frame_loads"]:
        # MyType 1 = force/length, Dir 10 = gravity, RelDist 0..1, values, CSys, RelDist=True
        check(m.FrameObj.SetLoadDistributed(fl["frame"], fl["pattern"], 1, DIR_GRAVITY, 0.0, 1.0,
                                            fl["w"], fl["w"], "Global", True, False),
              f"SetLoadDistributed {fl['frame']}")
    for al in model["area_loads"]:
        check(m.AreaObj.SetLoadUniform(al["area"], al["pattern"], al["q"], DIR_GRAVITY, False,
                                       "Global"), f"SetLoadUniform {al['area']}")

    # combinations (eCNameType: LoadCase 0, LoadCombo 1); combo type 0 linear add, 1 envelope
    for fam, combos in tm.COMBOS.items():
        for k, fac in enumerate(combos, start=1):
            cname = f"{fam}{k:02d}"
            check(m.RespCombo.Add(cname, 0), f"RespCombo.Add {cname}")
            for pat, sf in zip(tm.PATTERN_ORDER, fac):
                if sf:
                    check(m.RespCombo.SetCaseList(cname, 0, pat, float(sf)), f"SetCaseList {cname}")
        env = f"ENV_{fam}"
        check(m.RespCombo.Add(env, 1), f"RespCombo.Add {env}")
        for k in range(1, len(combos) + 1):
            check(m.RespCombo.SetCaseList(env, 1, f"{fam}{k:02d}", 1.0), f"SetCaseList {env}")


# ------------------------------------------------------------------------------------------
# results
# ------------------------------------------------------------------------------------------
def select_output(m, names: list[str], combos: bool) -> None:
    check(m.Results.Setup.DeselectAllCasesAndCombosForOutput(), "DeselectAll")
    for n in names:
        if combos:
            check(m.Results.Setup.SetComboSelectedForOutput(n), f"SetComboSelected {n}")
        else:
            check(m.Results.Setup.SetCaseSelectedForOutput(n), f"SetCaseSelected {n}")


def joint_reactions(m, joint: str) -> list[dict]:
    ret = m.Results.JointReact(joint, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [])
    check(ret, f"JointReact {joint}")
    n, obj, elm, case, stype, step, f1, f2, f3, m1, m2, m3 = ret[:12]
    return [{"joint": joint, "case": case[k], "stype": stype[k], "F1": f1[k], "F2": f2[k],
             "F3": f3[k], "M1": m1[k], "M2": m2[k], "M3": m3[k]} for k in range(n)]


def joint_displ(m, joint: str) -> list[dict]:
    ret = m.Results.JointDispl(joint, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [])
    check(ret, f"JointDispl {joint}")
    n, obj, elm, case, stype, step, u1, u2, u3, r1, r2, r3 = ret[:12]
    return [{"joint": joint, "case": case[k], "stype": stype[k], "U1": u1[k], "U2": u2[k],
             "U3": u3[k], "R1": r1[k], "R2": r2[k], "R3": r3[k]} for k in range(n)]


def frame_forces(m, frame: str) -> list[dict]:
    ret = m.Results.FrameForce(frame, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [], [], [])
    check(ret, f"FrameForce {frame}")
    n, obj, objsta, elm, elmsta, case, stype, step, p, v2, v3, t, m2, m3 = ret[:14]
    return [{"frame": frame, "station": objsta[k], "case": case[k], "stype": stype[k], "P": p[k],
             "V2": v2[k], "V3": v3[k], "T": t[k], "M2": m2[k], "M3": m3[k]} for k in range(n)]


def to_cype_base(r: dict) -> dict:
    """SAP support reaction at a pile base -> CYPE 'arranque' (action of the pile on the
    foundation, pile local axes = global).  N = F3, Qx = -F1, Qy = -F2, Mx = -M2, My = M1."""
    return {"N": r["F3"], "Mx": -r["M2"], "My": r["M1"], "Qx": -r["F1"], "Qy": -r["F2"], "T": -r["M3"]}


def extract(m, model: dict) -> dict:
    out: dict = {"reactions": [], "pile_forces": [], "beam_forces": [], "deck_displ": []}
    cases = list(tm.PATTERN_ORDER)
    combos = [f"{fam}{k:02d}" for fam, cs in tm.COMBOS.items() for k in range(1, len(cs) + 1)]
    envs = [f"ENV_{fam}" for fam in tm.COMBOS]
    bases = [j for j in model["restraints"]]
    piles = [f["name"] for f in model["frames"] if f["kind"] == "pile"]
    beams = [f["name"] for f in model["frames"] if f["kind"] in ("beam_t", "beam_edge")]
    watch = [j for j, c in model["cype_names"].items() if not j.startswith("B")]

    for names, is_combo in ((cases, False), (combos + envs, True)):
        select_output(m, names, is_combo)
        for j in bases:
            for r in joint_reactions(m, j):
                r["cype"] = model["cype_names"][j]
                r.update({f"cype_{k}": v for k, v in to_cype_base(r).items()})
                out["reactions"].append(r)
        for f in piles:
            out["pile_forces"] += frame_forces(m, f)
        for f in beams:
            out["beam_forces"] += frame_forces(m, f)
        for j in watch:
            for r in joint_displ(m, j):
                r["cype"] = model["cype_names"][j]
                out["deck_displ"].append(r)
    return out


# ------------------------------------------------------------------------------------------
# comparison with the CYPE listing
# ------------------------------------------------------------------------------------------
HYP_REF = {"PP": "Peso propio", "CM": "Cargas muertas", "Qa": "Sobrecarga de uso",
           "TB1": "Tiro bolardo", "TB2": "Tiro Bolardo 2", "TB3": "Tiro bolardo 3"}


def comparison_rows(res: dict, ref: dict) -> list[list]:
    rows = [["Pilote", "Hipótesis", "Esfuerzo", "SAP2000", "CYPE (Anejo 10 §3.4)", "Dif.", "Dif. %"]]
    base = ref["pile_base_forces_arranques_3_4"]["piles"]
    for r in res["reactions"]:
        if r["case"] not in HYP_REF:
            continue
        cy = base.get(r["cype"], {}).get(HYP_REF[r["case"]])
        if not cy:
            continue
        for comp in ("N", "Mx", "My", "Qx", "Qy", "T"):
            s, c = r[f"cype_{comp}"], cy.get(comp)
            if c is None:
                continue
            d = s - c
            pct = 100 * d / c if abs(c) > 1e-6 else None
            rows.append([r["cype"], r["case"], comp, round(s, 2), c, round(d, 2),
                         None if pct is None else round(pct, 1)])
    return rows


def write_outputs(res: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "resultados_SAP2000.json").write_text(json.dumps(res, indent=1, default=str))
    try:
        from openpyxl import Workbook
    except ImportError:
        print("openpyxl not installed: only the JSON file was written")
        return
    wb = Workbook()
    wb.remove(wb.active)
    for key, rows in res.items():
        if not rows or not isinstance(rows, list):
            continue
        ws = wb.create_sheet(key[:31])
        if isinstance(rows[0], dict):
            cols = list(rows[0].keys())
            ws.append(cols)
            for r in rows:
                ws.append([r.get(c) for c in cols])
        else:
            for r in rows:
                ws.append(r)
    wb.save(out_dir / "resultados_SAP2000.xlsx")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attach", action="store_true", help="attach to a running SAP2000")
    ap.add_argument("--from-s2k", type=Path, default=None, help="open/import a .$2k instead of building")
    ap.add_argument("--save", type=Path, default=ROOT / "output" / "Muelle_Trasmallo_40m.sdb")
    ap.add_argument("--ref", type=Path, default=ROOT / "ref" / "cype_reference.json")
    ap.add_argument("--hidden", action="store_true")
    args = ap.parse_args()

    model = tm.build_model()
    sap, m = connect(args.attach, visible=not args.hidden)
    if args.from_s2k:
        check(m.File.OpenFile(str(args.from_s2k.resolve())), "OpenFile .$2k")
    else:
        define_model(m, model)
    args.save.parent.mkdir(parents=True, exist_ok=True)
    check(m.File.Save(str(args.save.resolve())), "File.Save")
    check(m.Analyze.RunAnalysis(), "RunAnalysis")

    res = extract(m, model)
    if args.ref.exists():
        ref = json.loads(args.ref.read_text(encoding="utf-8"))
        res["comparacion_arranques"] = comparison_rows(res, ref)
    write_outputs(res, ROOT / "output")
    print("done:", ROOT / "output" / "resultados_SAP2000.xlsx")


if __name__ == "__main__":
    main()
