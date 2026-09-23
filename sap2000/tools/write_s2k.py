"""Write the SAP2000 text import file (.$2k) of the Muelle de Trasmallo model.

    python tools/write_s2k.py [-o output/Muelle_Trasmallo_40m.$2k] [--decimal ,]

In SAP2000:  File > Import > SAP2000 .s2k Text File (New Model), select the file, review the
import log, save the model (.sdb) and run the analysis (F5).  Units of the file: kN, m, C.

The file follows the database-table text format exported by SAP2000 v20.1 (table titles and
field names checked against real exported files, see README): 3-space indentation and
separators, "Yes"/"No" booleans, quoted values containing spaces, records longer than 240
characters wrapped with " _", CRLF line endings, pure ASCII, "END TABLE DATA" terminator.
Newer SAP2000 versions import this format as well.

Decimal separator: SAP2000 reads numbers with the Windows regional decimal symbol.  The file
is written with "." (default); if Windows uses "," as decimal symbol either change it to "."
before importing (Control Panel > Region > Additional settings) or write the file with
``--decimal ,``.  The OAPI route (tools/sap_oapi_run.py) is independent of this setting.
"""

from __future__ import annotations

import argparse
import datetime
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "model"))

import trasmallo as tm  # noqa: E402

SAP_VERSION = "27.1.0"     # --version 20.1.0 writes the older (v20) field names
LINE_LEN = 240
DECIMAL = "."

FAMILY_TITLE = {"ELU": "ELU rotura hormigon", "CIM": "ELU hormigon en cimentaciones",
                "ELS": "Desplazamientos (caracteristicas)"}


def ascii_text(s: str) -> str:
    """SAP2000 reads the text file as ANSI: keep it pure ASCII (drop accents)."""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def fmt(v) -> str:
    """Format one value the way SAP2000 writes it."""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == 0:
            return "0"
        s = f"{v:.12G}"
        return s.replace(".", DECIMAL) if DECIMAL != "." else s
    s = ascii_text(str(v)).replace('"', "'")
    if any(c in s for c in " ,") or s == "":
        return f'"{s}"'
    return s


class S2K:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def record(self, row: dict) -> None:
        line = "   "
        for k, v in row.items():
            if v is None:
                continue
            pair = f"{k}={fmt(v)}"
            cand = pair if not line.strip() else "   " + pair
            if line.strip() and len(line) + len(cand) > LINE_LEN:
                self.lines.append(line + " _")
                line = "        " + pair
            else:
                line += cand
        self.lines.append(line)

    def table(self, title: str, rows: list[dict]) -> None:
        if not rows:
            return
        self.lines.append(f'TABLE:  "{title}"')
        for row in rows:
            self.record(row)
        self.lines.append(" ")

    def text(self) -> str:
        return "\r\n".join(self.lines + ["END TABLE DATA", ""])


def _modern() -> bool:
    return int(SAP_VERSION.split(".")[0]) >= 23


def _moduli(p: dict) -> dict:
    """Elastic section moduli: S33/S22 (v20) or S33Top/S33Bot/S22Left/S22Right (v23+)."""
    if not _modern():
        return {"S33": p["S33"], "S22": p["S22"]}
    return {"S33Top": p["I33"] / p["centroid_from_top"], "S33Bot": p["I33"] / p["centroid_from_bottom"],
            "S22Left": p["S22"], "S22Right": p["S22"]}


def _length(model: dict, f: dict) -> float:
    (x1, y1, z1), (x2, y2, z2) = model["joints"][f["i"]], model["joints"][f["j"]]
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5


def build_tables(model: dict, when: datetime.datetime | None = None) -> S2K:
    s = S2K()
    when = when or datetime.datetime(2026, 9, 23, 12, 0, 0)
    s.lines += [f"File Muelle_Trasmallo_40m.$2k was saved on {when.month}/{when.day}/"
                f"{when.year % 100:02d} at {when.hour}:{when.minute:02d}:{when.second:02d}", " "]

    s.table("PROGRAM CONTROL", [{
        "ProgramName": "SAP2000", "Version": SAP_VERSION, "ProgLevel": "Ultimate",
        "CurrUnits": "KN, m, C", "RegenHinge": True}])
    s.table("ACTIVE DEGREES OF FREEDOM", [{
        "UX": True, "UY": True, "UZ": True, "RX": True, "RY": True, "RZ": True}])
    s.table("ANALYSIS OPTIONS", [{"Solver": "Advanced", "SolverProc": "Auto", "Force32Bit": False,
                                  "StiffCase": "None", "GeomMod": "None"}])
    s.table("COORDINATE SYSTEMS", [{
        "Name": "GLOBAL", "Type": "Cartesian", "X": 0.0, "Y": 0.0, "Z": 0.0,
        "AboutZ": 0.0, "AboutY": 0.0, "AboutX": 0.0}])

    # ---- materials (concrete only: the rebar grade does not enter a linear analysis) -------
    concretes = [m for m in model["materials"] if m.kind == "Concrete"]
    s.table("MATERIAL PROPERTIES 01 - GENERAL", [
        {"Material": m.name, "Type": "Concrete", "SymType": "Isotropic", "TempDepend": False,
         "Color": "Gray8Dark", "Notes": m.note} for m in concretes])
    s.table("MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES", [
        {"Material": m.name, "UnitWeight": m.unit_weight, "UnitMass": m.unit_weight / 9.80665,
         "E1": m.E, "G12": m.E / (2 * (1 + m.nu)), "U12": m.nu, "A1": m.alpha}
        for m in concretes])
    s.table("MATERIAL PROPERTIES 03B - CONCRETE DATA", [
        {"Material": m.name, "Fc": m.fc, "eFc": m.fc, "LtWtConc": False, "SSCurveOpt": "Mander",
         "SSHysType": "Takeda", "SFc": 0.002, "SCap": 0.0035, "FinalSlope": -0.1,
         "FAngle": 0.0, "DAngle": 0.0} for m in concretes])

    # ---- frame sections ------------------------------------------------------------------------
    rows = []
    for fs in model["sections"].values():
        p = fs.section.props
        row = {"SectionName": fs.name, "Material": fs.material, "Shape": fs.shape,
               "t3": p["t3"], "t2": p["t2"]}
        if fs.shape == "General":
            row.update({"Area": p["Area"], "TorsConst": p["TorsConst"], "I33": p["I33"],
                        "I22": p["I22"], "I23": 0.0,       # principal axes (L-shape I23 neglected)
                        "AS2": p["AS2"], "AS3": p["AS3"], **_moduli(p),
                        "Z33": p["Z33"], "Z22": p["Z22"], "R33": p["R33"], "R22": p["R22"]})
        row.update({"Color": "Cyan" if fs.name.startswith("PILOTE") else "Green", "FromFile": False})
        mods = {"AMod": 1.0, "A2Mod": 1.0, "A3Mod": 1.0, "JMod": 1.0, "I2Mod": 1.0,
                "I3Mod": 1.0, "MMod": 1.0, "WMod": 1.0}
        mods.update({k: float(v) for k, v in fs.modifiers.items()})
        row.update(mods)
        row["Notes"] = fs.section.description
        rows.append(row)
    s.table("FRAME SECTION PROPERTIES 01 - GENERAL", rows)

    s.table("AREA SECTION PROPERTIES", [{
        "Section": sl["name"], "Material": sl["material"], "MatAngle": 0.0,
        "AreaType": "Shell", "Type": "Shell-Thin", "DrillDOF": True,
        "Thickness": sl["thickness"], "BendThick": sl["thickness"],
        "Color": "Yellow" if sl["factor"] == 1 else "Red",
        "F11Mod": 1.0, "F22Mod": 1.0, "F12Mod": 1.0,
        "M11Mod": round(sl["m11"], 6), "M22Mod": sl["m22"], "M12Mod": sl["m12"],
        "V13Mod": 1.0, "V23Mod": 1.0, "MMod": sl["mass_mod"], "WMod": sl["weight_mod"],
        "Notes": sl["note"]} for sl in model["slab_sections"].values()])

    # ---- geometry ------------------------------------------------------------------------------
    s.table("JOINT COORDINATES", [
        {"Joint": j, "CoordSys": "GLOBAL", "CoordType": "Cartesian", "XorR": x, "Y": y, "Z": z,
         "SpecialJt": False} for j, (x, y, z) in model["joints"].items()])
    s.table("CONNECTIVITY - FRAME", [
        {"Frame": f["name"], "JointI": f["i"], "JointJ": f["j"], "IsCurved": False}
        for f in model["frames"]])
    s.table("CONNECTIVITY - AREA", [
        {"Area": a["name"], "NumJoints": 4, "Joint1": a["joints"][0], "Joint2": a["joints"][1],
         "Joint3": a["joints"][2], "Joint4": a["joints"][3]} for a in model["areas"]])

    s.table("JOINT RESTRAINT ASSIGNMENTS", [
        {"Joint": j, "U1": r[0], "U2": r[1], "U3": r[2], "R1": r[3], "R2": r[4], "R3": r[5]}
        for j, r in model["restraints"].items()])
    d = model["diaphragm"]
    s.table("CONSTRAINT DEFINITIONS - DIAPHRAGM", [
        {"Name": d["name"], "CoordSys": "GLOBAL", "Axis": "Z", "MultiLevel": False}])
    s.table("JOINT CONSTRAINT ASSIGNMENTS", [
        {"Joint": j, "Constraint": d["name"], "Type": "Diaphragm"} for j in d["joints"]])

    s.table("FRAME SECTION ASSIGNMENTS", [
        {"Frame": f["name"], "SectionType": model["sections"][f["section"]].shape,
         "AutoSelect": "N.A.", "AnalSect": f["section"], "DesignSect": f["section"],
         "MatProp": "Default"} for f in model["frames"]])
    s.table("FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL", [
        {"Frame": f["name"], "Angle": f["angle"], "AdvanceAxes": False}
        for f in model["frames"] if f.get("angle")])
    obj_mod = [("AMod", "AMod"), ("A2Mod", "AS2Mod"), ("A3Mod", "AS3Mod"), ("JMod", "JMod"),
               ("I2Mod", "I22Mod"), ("I3Mod", "I33Mod"), ("MMod", "MassMod"), ("WMod", "WeightMod")]
    s.table("FRAME PROPERTY MODIFIERS", [
        {"Frame": f["name"], **{fld: float(f["modifiers"].get(k, 1.0)) for k, fld in obj_mod}}
        for f in model["frames"] if f.get("modifiers")])
    s.table("FRAME OUTPUT STATION ASSIGNMENTS", [
        {"Frame": f["name"], "StationType": "MaxStaSpcg", "MaxStaSpcg": f["station_max"],
         "AddAtElmInt": True, "AddAtPtLoad": True} for f in model["frames"]])
    s.table("FRAME OFFSET ALONG LENGTH ASSIGNMENTS", [
        {"Frame": f["name"], "Type": "User", "LengthI": f["offsets"][0],
         "LengthJ": f["offsets"][1], "RigidFactor": 1.0}
        for f in model["frames"] if f.get("offsets") and any(f["offsets"])])
    s.table("AREA SECTION ASSIGNMENTS", [
        {"Area": a["name"], "Section": a["section"], "MatProp": "Default"} for a in model["areas"]])

    # ---- groups --------------------------------------------------------------------------------
    s.table("GROUPS 1 - DEFINITIONS", [
        {"GroupName": g, "Selection": True, "SectionCut": True, "Steel": True, "Concrete": True,
         "Aluminum": True, "ColdFormed": True, "Stage": True, "Bridge": True,
         "AutoSeismic": False, "AutoWind": False, "SelDesSteel": False, "SelDesAlum": False,
         "SelDesCold": False, "MassWeight": True, "Color": "Blue"}
        for g in ["ALL"] + list(model["groups"])])
    s.table("GROUPS 2 - ASSIGNMENTS", [
        {"GroupName": g, "ObjectType": kind, "ObjectLabel": name}
        for g, objs in model["groups"].items() for kind, name in objs])

    # ---- load patterns, cases, combinations --------------------------------------------------
    design_act = {"Dead": "Non-Composite", "Live": "Short-Term Composite", "Other": "Other"}
    s.table("LOAD PATTERN DEFINITIONS", [
        {"LoadPat": n, "DesignType": dt, "SelfWtMult": float(sw)}
        for n, dt, sw, _ in tm.LOAD_PATTERNS])
    s.table("LOAD CASE DEFINITIONS", [
        {"Case": n, "Type": "LinStatic", "InitialCond": "Zero", "DesTypeOpt": "Prog Det",
         "DesignType": dt, "DesActOpt": "Prog Det", "DesignAct": design_act[dt],
         "AutoType": "None", "RunCase": True, "Notes": note}
        for n, dt, _, note in tm.LOAD_PATTERNS])
    s.table("CASE - STATIC 1 - LOAD ASSIGNMENTS", [
        {"Case": n, "LoadType": "Load pattern", "LoadName": n, "LoadSF": 1.0}
        for n, *_ in tm.LOAD_PATTERNS])

    rows = []

    def combo(name: str, ctype: str, items: list[tuple[str, str, float]], notes: str) -> None:
        for k, (case_type, case, sf) in enumerate(items):
            row = {"ComboName": name}
            if k == 0:
                row.update({"ComboType": ctype, "AutoDesign": False})
            if not _modern():          # v23+ exports resolve cases/combos by name
                row["CaseType"] = case_type
            row.update({"CaseName": case, "ScaleFactor": float(sf)})
            if k == 0:
                row.update({"SteelDesign": "None", "ConcDesign": "None", "AlumDesign": "None",
                            "ColdDesign": "None", "Notes": notes})
            rows.append(row)

    for fam, combos in tm.COMBOS.items():
        for k, fac in enumerate(combos, start=1):
            combo(f"{fam}{k:02d}", "Linear Add",
                  [("Linear Static", pat, sf) for pat, sf in zip(tm.PATTERN_ORDER, fac) if sf],
                  f"CYPE {FAMILY_TITLE[fam]} comb. {k}")
        combo(f"ENV_{fam}", "Envelope",
              [("Response Combo", f"{fam}{k:02d}", 1.0) for k in range(1, len(combos) + 1)],
              f"Envolvente {FAMILY_TITLE[fam]}")
    s.table("COMBINATION DEFINITIONS", rows)

    # ---- loads ---------------------------------------------------------------------------------
    s.table("JOINT LOADS - FORCE", [
        {"Joint": jl["joint"], "LoadPat": jl["pattern"], "CoordSys": "GLOBAL",
         "F1": jl["F"][0], "F2": jl["F"][1], "F3": jl["F"][2],
         "M1": jl["F"][3], "M2": jl["F"][4], "M3": jl["F"][5]} for jl in model["joint_loads"]])
    lengths = {f["name"]: _length(model, f) for f in model["frames"]}
    s.table("FRAME LOADS - DISTRIBUTED", [
        {"Frame": fl["frame"], "LoadPat": fl["pattern"], "CoordSys": "GLOBAL", "Type": "Force",
         "Dir": "Gravity", "DistType": "RelDist", "RelDistA": 0.0, "RelDistB": 1.0,
         "AbsDistA": 0.0, "AbsDistB": round(lengths[fl["frame"]], 6),
         "FOverLA": fl["w"], "FOverLB": fl["w"]} for fl in model["frame_loads"]])
    s.table("AREA LOADS - UNIFORM", [
        {"Area": al["area"], "LoadPat": al["pattern"], "CoordSys": "GLOBAL", "Dir": "Gravity",
         "UnifLoad": al["q"]} for al in model["area_loads"]])
    return s


def main() -> None:
    global DECIMAL, SAP_VERSION
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "output" / "Muelle_Trasmallo_40m.$2k")
    ap.add_argument("--version", default=SAP_VERSION,
                    help="SAP2000 version written in PROGRAM CONTROL (e.g. 27.1.0, 20.1.0)")
    ap.add_argument("--decimal", choices=[".", ","], default=".",
                    help="decimal symbol of the Windows machine that will import the file")
    args = ap.parse_args()
    DECIMAL = args.decimal
    SAP_VERSION = args.version
    model = tm.build_model()
    s = build_tables(model)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(s.text().encode("ascii"))
    print(f"written {args.out}  ({len(s.lines)} lines, decimal '{DECIMAL}')")


if __name__ == "__main__":
    main()
