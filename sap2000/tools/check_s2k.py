"""Consistency check of a SAP2000 .$2k text file (no SAP2000 needed).

    python tools/check_s2k.py [output/Muelle_Trasmallo_40m.$2k]

Parses every table, then checks that all joints / frames / areas / sections / materials /
load patterns / cases / combinations referenced in the file are defined, that the file is
pure ASCII and properly terminated, and prints the load totals per pattern.  Seismic tables
(``write_s2k.py --sismo``: MASS SOURCE, FUNCTION - RESPONSE SPECTRUM - USER, LinModal /
LinRespSpec cases, CASE - MODAL 1, CASE - RESPONSE SPECTRUM 1/2) are checked when present and the
seismic mass of the mass source is printed.
"""

from __future__ import annotations

import re
import shlex
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse(path: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = defaultdict(list)
    current = None
    raw = path.read_bytes()
    try:
        raw.decode("ascii")
    except UnicodeDecodeError as e:
        raise SystemExit(f"non-ASCII byte at offset {e.start}")
    text = raw.decode("ascii")
    too_long = [k for k, ln in enumerate(text.splitlines(), 1) if len(ln) > 245]
    if too_long:
        raise SystemExit(f"{len(too_long)} physical lines longer than 245 characters, e.g. {too_long[:3]}")
    if "\r\n" not in text:
        print("warning: file does not use CRLF line endings")
    if not text.rstrip().endswith("END TABLE DATA"):
        raise SystemExit("file does not end with END TABLE DATA")
    pending = ""
    for line in text.splitlines():
        m = re.match(r'^TABLE:\s+"(.+)"\s*$', line)
        if m:
            current = m.group(1)
            continue
        if not line.strip() or current is None or line.startswith("END TABLE DATA"):
            continue
        if line.rstrip().endswith(" _"):
            pending += line.rstrip()[:-2] + "   "
            continue
        line = pending + line
        pending = ""
        row = {}
        for tok in shlex.split(line, posix=True):
            k, _, v = tok.partition("=")
            row[k] = v
        tables[current].append(row)
    return tables


def num(v: str) -> float:
    return float(v.replace(",", "."))


# default bar list of a new SAP2000 model (SAP2000 help "Reinforcement Bar Sizes")
SAP_DEFAULT_BARS = ({f"{d}d" for d in (6, 8, 10, 12, 14, 16, 20, 25, 26, 28)}
                    | {f"#{k}" for k in range(2, 19)} | {f"{k}M" for k in (10, 15, 20, 25, 30, 35, 45, 55)}
                    | {f"N{k}" for k in (12, 16, 20, 24, 28, 32, 36)})
EC2_PREF = "PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004"
EC2_OVER = "OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004"


def check_design(t: dict, frames: set, need) -> list[str]:
    """Reference checks of the concrete-design tables (diseno/sap/write_s2k_diseno.py); returns
    summary lines.  Tables absent from the file are skipped."""
    mat_type = {r["Material"]: r.get("Type", "") for r in t.get("MATERIAL PROPERTIES 01 - GENERAL", [])}
    fsec = {r["SectionName"]: r for r in t.get("FRAME SECTION PROPERTIES 01 - GENERAL", [])}
    bars = {r["RebarID"] for r in t.get("REBAR SIZES", [])} or SAP_DEFAULT_BARS
    for r in t.get("MATERIAL PROPERTIES 03E - REBAR DATA", []):
        need(mat_type.get(r["Material"]) == "Rebar", f"03E: {r['Material']} is not a Rebar material")
        need(num(r["Fu"]) >= num(r["Fy"]) > 0, f"03E: {r['Material']} Fy/Fu")
    col = {r["SectionName"]: r for r in t.get("FRAME SECTION PROPERTIES 02 - CONCRETE COLUMN", [])}
    beam = {r["SectionName"]: r for r in t.get("FRAME SECTION PROPERTIES 03 - CONCRETE BEAM", [])}
    for kind, rows, shapes in (("02", col, {"Rectangular", "Circle"}),
                               ("03", beam, {"Rectangular", "Tee", "Angle", "Circle"})):
        for name, r in rows.items():
            s = fsec.get(name)
            need(s is not None, f"{kind}: unknown section {name}")
            if s is None:
                continue
            need(s["Shape"] in shapes, f"{kind}: section {name} has shape {s['Shape']}, not {sorted(shapes)}")
            need(mat_type.get(s["Material"]) == "Concrete", f"{kind}: section {name} is not concrete")
            for k in ("RebarMatL", "RebarMatC"):
                need(mat_type.get(r[k]) == "Rebar", f"{kind}: section {name} {k}={r[k]} is not a Rebar material")
            if kind == "02":
                need(r["BarSizeL"] in bars and r["BarSizeC"] in bars, f"02: {name} bar size not defined")
                need(r["ReinfType"] in ("Design", "Check"), f"02: {name} ReinfType {r['ReinfType']}")
                need(0 < num(r["Cover"]) < min(num(s["t2"]), num(s["t3"])) / 2, f"02: {name} cover")
                if r.get("ReinfConfig") == "Rectangular":
                    need(int(r["NumBars3Dir"]) >= 2 and int(r["NumBars2Dir"]) >= 2, f"02: {name} bars per face")
            else:
                need(num(r["TopCover"]) > 0 and num(r["BotCover"]) > 0
                     and num(r["TopCover"]) + num(r["BotCover"]) < num(s["t3"]), f"03: {name} covers")
    for name in set(col) & set(beam):
        need(False, f"section {name} has both column (02) and beam (03) data")

    sec_of = {r["Frame"]: r["AnalSect"] for r in t.get("FRAME SECTION ASSIGNMENTS", [])}
    proc = {r["Frame"]: r["DesignProc"] for r in t.get("FRAME DESIGN PROCEDURES", [])}
    for f, p in proc.items():
        need(f in frames, f"FRAME DESIGN PROCEDURES: unknown frame {f}")
        need(p in ("From Material", "No Design"), f"FRAME DESIGN PROCEDURES: {f} {p}")
    designed = {f for f in frames if proc.get(f, "From Material") == "From Material"
                and mat_type.get(fsec.get(sec_of.get(f), {}).get("Material")) == "Concrete"
                and (sec_of.get(f) in col or sec_of.get(f) in beam)}
    for r in t.get(EC2_OVER, []):
        f = r["Frame"]
        need(f in frames, f"{EC2_OVER}: unknown frame {f}")
        need(f in designed, f"{EC2_OVER}: frame {f} is not concrete-designed")
        need(r.get("FrameType", "Program Determined") in
             ("Program Determined", "DC High", "DC Medium", "DC Low", "Secondary"), f"{EC2_OVER}: {f} FrameType")
        if "BetaMajor" in r:
            need(sec_of.get(f) in col, f"{EC2_OVER}: beta overwrite on non-column frame {f}")
    first: dict[str, dict] = {}
    for r in t.get("COMBINATION DEFINITIONS", []):
        first.setdefault(r["ComboName"], r)
    strength = sorted(c for c, r in first.items() if r.get("ConcDesign") == "Strength")
    for c, r in first.items():
        need(r.get("ConcDesign", "None") in ("None", "Strength"), f"combo {c}: ConcDesign {r.get('ConcDesign')}")
        if r.get("ConcDesign") == "Strength":
            need(r.get("ComboType") == "Linear Add", f"combo {c}: Strength flag on a {r.get('ComboType')} combo")
    for r in t.get("AUTO COMBINATION OPTION DATA 01 - GENERAL", []):
        need(r.get("AutoGen") in ("Yes", "No"), f"AUTO COMBINATION OPTION DATA: AutoGen {r.get('AutoGen')}")
    for r in t.get(EC2_PREF, []):
        need(r.get("SOM", "Nominal Curvature") in ("Nominal Stiffness", "Nominal Curvature", "None"), "EC2 SOM")
        need(r.get("Country", "CEN Default") in ("CEN Default", "Denmark", "Finland", "Germany", "Ireland",
                                                 "Norway", "Poland", "Portugal", "Singapore", "Slovenia",
                                                 "Sweden", "United Kingdom"), "EC2 Country")
        need(int(r.get("NumCurves", "24")) % 4 == 0 and int(r.get("NumPoints", "11")) % 2 == 1,
             "EC2 NumCurves (multiple of 4) / NumPoints (odd)")
    if not (col or beam or proc or strength):
        return []
    ptype = {f: ("column" if sec_of.get(f) in col else "beam") for f in designed}
    return [f"design: {len(designed)} concrete-designed frames ({sum(v == 'column' for v in ptype.values())} "
            f"columns, {sum(v == 'beam' for v in ptype.values())} beams), "
            f"{sum(1 for p in proc.values() if p == 'No Design')} 'No Design', "
            f"{len(t.get(EC2_OVER, []))} EC2 overwrite records",
            f"design: {len(strength)} Strength combos " + (f"{strength[0]}..{strength[-1]}" if strength else "")]

G = 9.80665
RS_MODAL_COMBOS = {"CQC", "SRSS", "ABS", "GMC", "10 Percent", "Double Sum"}   # values of real exports


def check_seismic(t: dict, pats: set, cases: set, tot: dict, need) -> list[str]:
    """Reference and value checks of the seismic tables; returns summary lines (none if the file
    has no modal / response-spectrum data)."""
    ctype = {r["Case"]: r.get("Type", "") for r in t.get("LOAD CASE DEFINITIONS", [])}
    modal = {c for c, ty in ctype.items() if ty == "LinModal"}
    rsc = {c for c, ty in ctype.items() if ty == "LinRespSpec"}
    ms_rows = t.get("MASS SOURCE", [])
    funcs: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for r in t.get("FUNCTION - RESPONSE SPECTRUM - USER", []):
        funcs[r["Name"]].append((num(r["Period"]), num(r["Accel"])))
    if not (modal or rsc or ms_rows or funcs):
        return []
    lines = []
    # mass source: pattern rows, one default, no double-counted self weight
    selfwt = {r["LoadPat"]: num(r.get("SelfWtMult", "0")) for r in t.get("LOAD PATTERN DEFINITIONS", [])}
    heads = [r for r in ms_rows if "Elements" in r]
    need(len({r["MassSource"] for r in ms_rows}) == len(heads), "MASS SOURCE: one header record per source")
    need(sum(r.get("IsDefault") == "Yes" for r in heads) <= 1, "MASS SOURCE: more than one default")
    for h in heads:
        rows = [r for r in ms_rows if r["MassSource"] == h["MassSource"]]
        for r in rows:
            if "LoadPat" in r:
                need(h.get("Loads") == "Yes", f"MASS SOURCE {h['MassSource']}: LoadPat with Loads=No")
                need(r["LoadPat"] in pats, f"MASS SOURCE: unknown pattern {r['LoadPat']}")
                if h.get("Elements") == "Yes":
                    need(not selfwt.get(r["LoadPat"]), f"MASS SOURCE {h['MassSource']}: element self mass and "
                         f"pattern {r['LoadPat']} with self weight -> self mass counted twice")
        if h.get("IsDefault") == "Yes":
            w = sum(num(r["Multiplier"]) * (tot.get(r["LoadPat"], 0.0)
                                            + (tot.get("PP (self weight)", 0.0) if selfwt.get(r["LoadPat"]) else 0.0))
                    for r in rows if "LoadPat" in r)
            if h.get("Elements") == "Yes":
                w += tot.get("PP (self weight)", 0.0)
            lines.append(f"seismic: mass source {h['MassSource']} (Elements={h.get('Elements')}, "
                         f"Loads={h.get('Loads')}): weight {w:.1f} kN = mass {w / G:.1f} t")
    # response-spectrum functions
    for name, pts in funcs.items():
        T = [p[0] for p in pts]
        need(T == sorted(T) and len(set(T)) == len(T), f"RS function {name}: periods not increasing")
        need(all(a >= 0 for _, a in pts), f"RS function {name}: negative ordinate")
    for r in t.get("FUNCTION - RESPONSE SPECTRUM - USER", []):
        if "FuncDamp" in r:
            need(0 <= num(r["FuncDamp"]) < 1, f"RS function {r['Name']}: FuncDamp")
    # modal cases
    mrows = {r["Case"]: r for r in t.get("CASE - MODAL 1 - GENERAL", [])}
    for c in modal:
        need(c in mrows, f"modal case {c} without CASE - MODAL 1 - GENERAL record")
    for c, r in mrows.items():
        need(c in modal, f"CASE - MODAL 1: {c} is not a LinModal case")
        need(r.get("ModeType") in ("Eigen", "Ritz"), f"CASE - MODAL 1: {c} ModeType")
        need(int(r["MaxNumModes"]) >= int(r.get("MinNumModes", "1")) >= 1, f"CASE - MODAL 1: {c} number of modes")
    # response-spectrum cases
    for r in t.get("LOAD CASE DEFINITIONS", []):
        if r.get("Type") == "LinRespSpec":
            need(r.get("ModalCase") in modal, f"RS case {r['Case']}: ModalCase {r.get('ModalCase')} is not modal")
    g1 = {r["Case"]: r for r in t.get("CASE - RESPONSE SPECTRUM 1 - GENERAL", [])}
    g2 = defaultdict(list)
    for r in t.get("CASE - RESPONSE SPECTRUM 2 - LOAD ASSIGNMENTS", []):
        g2[r["Case"]].append(r)
    for c in rsc:
        need(c in g1, f"RS case {c} without CASE - RESPONSE SPECTRUM 1 record")
        need(bool(g2.get(c)), f"RS case {c} without load assignments")
    for c, r in g1.items():
        need(c in rsc, f"CASE - RESPONSE SPECTRUM 1: {c} is not a LinRespSpec case")
        need(r.get("ModalCombo") in RS_MODAL_COMBOS, f"RS case {c}: ModalCombo {r.get('ModalCombo')}")
        if "ConstDamp" in r:
            need(0 <= num(r["ConstDamp"]) < 1, f"RS case {c}: ConstDamp")
    for c, rows in g2.items():
        need(c in rsc, f"CASE - RESPONSE SPECTRUM 2: {c} is not a LinRespSpec case")
        for r in rows:
            need(r["LoadName"] in ("U1", "U2", "U3", "R1", "R2", "R3"), f"RS case {c}: LoadName {r['LoadName']}")
            need(r["Function"] in funcs, f"RS case {c}: undefined function {r['Function']}")
            need(num(r.get("TransAccSF", "1")) > 0, f"RS case {c}: TransAccSF")
    if modal:
        lines.append("seismic: modal " + ", ".join(f"{c} ({mrows[c]['ModeType']}, {mrows[c]['MaxNumModes']} modes)"
                                                    for c in sorted(modal) if c in mrows))
    for c in sorted(rsc):
        if c in g1:
            lines.append(f"seismic: RS {c} {g1[c]['ModalCombo']} damping {g1[c].get('ConstDamp', '-')}: " + ", ".join(
                f"{r['LoadName']} {r['Function']} x {r.get('TransAccSF', '1')} "
                f"(Sa max {max(a for _, a in funcs.get(r['Function'], [(0, 0)])):.4f} g)" for r in g2.get(c, [])))
    rs_in_combos = sorted({r["ComboName"] for r in t.get("COMBINATION DEFINITIONS", []) if r["CaseName"] in rsc})
    if rs_in_combos:
        lines.append(f"seismic: {len(rs_in_combos)} combinations with RS cases: {', '.join(rs_in_combos)}")
    return lines


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output" / "Muelle_Trasmallo_40m.$2k"
    t = parse(path)
    errors: list[str] = []

    def names(table: str, key: str) -> set[str]:
        return {r[key] for r in t.get(table, [])}

    joints = names("JOINT COORDINATES", "Joint")
    frames = names("CONNECTIVITY - FRAME", "Frame")
    areas = names("CONNECTIVITY - AREA", "Area")
    mats = names("MATERIAL PROPERTIES 01 - GENERAL", "Material")
    fsecs = names("FRAME SECTION PROPERTIES 01 - GENERAL", "SectionName")
    asecs = names("AREA SECTION PROPERTIES", "Section") | {"None"}
    pats = names("LOAD PATTERN DEFINITIONS", "LoadPat")
    cases = names("LOAD CASE DEFINITIONS", "Case")
    combos = {r["ComboName"] for r in t.get("COMBINATION DEFINITIONS", [])}
    groups = names("GROUPS 1 - DEFINITIONS", "GroupName")

    def need(cond: bool, msg: str) -> None:
        if not cond:
            errors.append(msg)

    for r in t["CONNECTIVITY - FRAME"]:
        need(r["JointI"] in joints and r["JointJ"] in joints, f"frame {r['Frame']}: unknown joint")
    for r in t["CONNECTIVITY - AREA"]:
        for k in range(1, int(r["NumJoints"]) + 1):
            need(r[f"Joint{k}"] in joints, f"area {r['Area']}: unknown joint {r[f'Joint{k}']}")
    for r in t["FRAME SECTION PROPERTIES 01 - GENERAL"]:
        need(r["Material"] in mats, f"section {r['SectionName']}: unknown material")
    for r in t["FRAME SECTION ASSIGNMENTS"]:
        need(r["Frame"] in frames and r["AnalSect"] in fsecs, f"frame section assignment {r}")
    for r in t["AREA SECTION ASSIGNMENTS"]:
        need(r["Area"] in areas and r["Section"] in asecs, f"area section assignment {r}")
    need(names("FRAME SECTION ASSIGNMENTS", "Frame") == frames, "frames without section")
    need(names("AREA SECTION ASSIGNMENTS", "Area") == areas, "areas without section")
    for tb, key in (("JOINT RESTRAINT ASSIGNMENTS", "Joint"), ("JOINT CONSTRAINT ASSIGNMENTS", "Joint"),
                    ("JOINT LOADS - FORCE", "Joint")):
        for r in t.get(tb, []):
            need(r[key] in joints, f"{tb}: unknown joint {r[key]}")
    for tb in ("FRAME LOADS - DISTRIBUTED", "FRAME OUTPUT STATION ASSIGNMENTS",
               "FRAME OFFSET ALONG LENGTH ASSIGNMENTS", "FRAME LOCAL AXES ASSIGNMENTS 1 - TYPICAL"):
        for r in t.get(tb, []):
            need(r["Frame"] in frames, f"{tb}: unknown frame {r['Frame']}")
    for r in t.get("AREA LOADS - UNIFORM", []):
        need(r["Area"] in areas, f"area load: unknown area {r['Area']}")
    for tb in ("JOINT LOADS - FORCE", "FRAME LOADS - DISTRIBUTED", "AREA LOADS - UNIFORM"):
        for r in t.get(tb, []):
            need(r["LoadPat"] in pats, f"{tb}: unknown pattern {r['LoadPat']}")
    for r in t.get("CASE - STATIC 1 - LOAD ASSIGNMENTS", []):
        need(r["Case"] in cases and r["LoadName"] in pats, f"case load assignment {r}")
    for r in t["COMBINATION DEFINITIONS"]:
        ok = r["CaseName"] in (combos if r.get("CaseType") == "Response Combo" else cases | combos)
        need(ok, f"combo {r['ComboName']}: unknown {r.get('CaseType', '')} {r['CaseName']}")
    for r in t.get("GROUPS 2 - ASSIGNMENTS", []):
        pool = {"Joint": joints, "Frame": frames, "Area": areas}[r["ObjectType"]]
        need(r["GroupName"] in groups and r["ObjectLabel"] in pool, f"group assignment {r}")

    # load totals (vertical, kN, downward positive)
    xyz = {r["Joint"]: tuple(num(r[k]) for k in ("XorR", "Y", "Z")) for r in t["JOINT COORDINATES"]}
    flen = {}
    for r in t["CONNECTIVITY - FRAME"]:
        a, b = xyz[r["JointI"]], xyz[r["JointJ"]]
        flen[r["Frame"]] = sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5
    aarea = {}
    for r in t["CONNECTIVITY - AREA"]:
        p = [xyz[r[f"Joint{k}"]] for k in range(1, 5)]
        aarea[r["Area"]] = 0.5 * abs(sum(p[k][0] * p[(k + 1) % 4][1] - p[(k + 1) % 4][0] * p[k][1]
                                         for k in range(4)))
    tot: dict[str, float] = defaultdict(float)
    for r in t.get("AREA LOADS - UNIFORM", []):
        tot[r["LoadPat"]] += num(r["UnifLoad"]) * aarea[r["Area"]]
    for r in t.get("FRAME LOADS - DISTRIBUTED", []):
        tot[r["LoadPat"]] += num(r["FOverLA"]) * flen[r["Frame"]]
    for r in t.get("JOINT LOADS - FORCE", []):
        tot[r["LoadPat"]] -= num(r["F3"])
    sec_area = {r["SectionName"]: (num(r["Area"]) if "Area" in r else num(r["t3"]) * num(r["t2"]),
                                   r["Material"], num(r.get("WMod", "1")))
                for r in t["FRAME SECTION PROPERTIES 01 - GENERAL"]}
    gamma = {r["Material"]: num(r["UnitWeight"]) for r in t["MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES"]}
    for r in t["FRAME SECTION ASSIGNMENTS"]:
        A, mat, wmod = sec_area[r["AnalSect"]]
        tot["PP (self weight)"] += A * gamma[mat] * flen[r["Frame"]] * wmod

    design_lines = check_design(t, frames, need)
    seismic_lines = check_seismic(t, pats, cases, tot, need)

    print(f"{path.name}: {len(joints)} joints, {len(frames)} frames, {len(areas)} areas, "
          f"{len(pats)} load patterns, {len(combos)} combinations, {len(t)} tables")
    for k in sorted(tot):
        print(f"  vertical load {k:18s} {tot[k]:10.1f} kN")
    for line in design_lines + seismic_lines:
        print("  " + line)
    if errors:
        print(f"{len(errors)} ERRORS")
        for e in errors[:50]:
            print("  ", e)
        raise SystemExit(1)
    print("OK - all references resolved")


if __name__ == "__main__":
    main()
