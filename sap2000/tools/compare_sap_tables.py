"""Compare SAP2000 results exported from the GUI (Display > Show Tables > Export to Excel) with
Anejo 10 / CYPECAD, without running the OAPI.

    python tools/compare_sap_tables.py <Joint_Reactions.xlsx> <Element_Forces_Frames.xlsx>

Both tables must contain at least the load cases PP, CM, Qa, TB1, TB2, TB3.  Writes
output/comparacion_SAP2000.md (+ .csv / .json), exactly as tools/sap_oapi_run.py does.
"""

from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(HERE))

import trasmallo as tm  # noqa: E402
from compare import build_report, load_ref, write_report  # noqa: E402
from sap_oapi_run import to_compare_inputs  # noqa: E402


def read_table(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    next(rows)                       # "TABLE:  ..."
    header = list(next(rows))
    next(rows)                       # units
    return [dict(zip(header, r)) for r in rows if r and r[0] is not None]


def main() -> None:
    react_path, force_path = Path(sys.argv[1]), Path(sys.argv[2])
    model = tm.build_model()
    frames = {f["name"]: f for f in model["frames"]}
    pats = set(tm.PATTERN_ORDER)
    raw = {"reactions": [], "pile_forces": [], "beam_forces": []}
    for r in read_table(react_path):
        if r["OutputCase"] in pats and r["Joint"] in model["restraints"]:
            raw["reactions"].append({"joint": r["Joint"], "case": r["OutputCase"],
                                     "cype": model["cype_names"][r["Joint"]],
                                     **{k: float(r[k]) for k in ("F1", "F2", "F3", "M1", "M2", "M3")}})
    for r in read_table(force_path):
        f = frames.get(r["Frame"])
        if f is None or r["OutputCase"] not in pats:
            continue
        row = {"frame": f["name"], "station": float(r["Station"]), "case": r["OutputCase"],
               **{k: float(r[k]) for k in ("P", "V2", "V3", "T", "M2", "M3")}}
        if f["kind"] == "pile":
            row["cype"] = f["cype"]
            raw["pile_forces"].append(row)
        elif f["kind"] == "beam_t":
            row.update(axis=f["axis"], y=model["joints"][f["i"]][1] + row["station"],
                       rigid=bool(f.get("rigid")))
            raw["beam_forces"].append(row)
    print(f"read {len(raw['reactions'])} reactions, {len(raw['pile_forces'])} pile and "
          f"{len(raw['beam_forces'])} beam force rows")
    pile_base, pile_head, beams = to_compare_inputs(raw)
    rep = build_report(pile_base, pile_head, beams, load_ref(ROOT / "ref" / "cype_reference.json"),
                       "SAP2000 v27.1 (tablas exportadas)")
    path = write_report(rep, ROOT / "output", "comparacion_SAP2000")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
