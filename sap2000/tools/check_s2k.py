"""Consistency check of a SAP2000 .$2k text file (no SAP2000 needed).

    python tools/check_s2k.py [output/Muelle_Trasmallo_40m.$2k]

Parses every table, then checks that all joints / frames / areas / sections / materials /
load patterns / cases / combinations referenced in the file are defined, that the file is
pure ASCII and properly terminated, and prints the load totals per pattern.
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
            pending += line.rstrip()[:-1]
            continue
        line = pending + line
        pending = ""
        row = {}
        for tok in shlex.split(line, posix=True):
            k, _, v = tok.partition("=")
            row[k] = v
        tables[current].append(row)
    return tables


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
    for r in t["CASE - STATIC 1 - LOAD ASSIGNMENTS"]:
        need(r["Case"] in cases and r["LoadName"] in pats, f"case load assignment {r}")
    for r in t["COMBINATION DEFINITIONS"]:
        ok = r["CaseName"] in cases if r["CaseType"] != "Response Combo" else r["CaseName"] in combos
        need(ok, f"combo {r['ComboName']}: unknown {r['CaseType']} {r['CaseName']}")
    for r in t.get("GROUPS 2 - ASSIGNMENTS", []):
        pool = {"Joint": joints, "Frame": frames, "Area": areas}[r["ObjectType"]]
        need(r["GroupName"] in groups and r["ObjectLabel"] in pool, f"group assignment {r}")

    # load totals (vertical, kN, downward positive)
    xyz = {r["Joint"]: tuple(float(r[k]) for k in ("XorR", "Y", "Z")) for r in t["JOINT COORDINATES"]}
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
        tot[r["LoadPat"]] += float(r["UnifLoad"]) * aarea[r["Area"]]
    for r in t.get("FRAME LOADS - DISTRIBUTED", []):
        tot[r["LoadPat"]] += float(r["FOverLA"]) * flen[r["Frame"]]
    for r in t.get("JOINT LOADS - FORCE", []):
        tot[r["LoadPat"]] -= float(r["F3"])
    sec_area = {r["SectionName"]: (float(r["Area"]) if "Area" in r else float(r["t3"]) * float(r["t2"]),
                                   r["Material"]) for r in t["FRAME SECTION PROPERTIES 01 - GENERAL"]}
    gamma = {r["Material"]: float(r["UnitWeight"]) for r in t["MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES"]}
    for r in t["FRAME SECTION ASSIGNMENTS"]:
        A, mat = sec_area[r["AnalSect"]]
        tot["PP (self weight)"] += A * gamma[mat] * flen[r["Frame"]]

    print(f"{path.name}: {len(joints)} joints, {len(frames)} frames, {len(areas)} areas, "
          f"{len(pats)} load patterns, {len(combos)} combinations, {len(t)} tables")
    for k in sorted(tot):
        print(f"  vertical load {k:18s} {tot[k]:10.1f} kN")
    if errors:
        print(f"{len(errors)} ERRORS")
        for e in errors[:50]:
            print("  ", e)
        raise SystemExit(1)
    print("OK - all references resolved")


if __name__ == "__main__":
    main()
