"""Design forces for the Código Estructural checks, read from the SAP2000 v27.1 tables exported
from the GUI (Display > Show Tables > Export to Excel):

    sap2000/resultados_sap/SAP27_Element_Forces_Frames.xlsx   (load cases PP, CM, Qa, TB1-3)

Everything is converted to the CYPECAD sign convention used in Anejo 10 (same conversion as
sap2000/tools/sap_oapi_run.py and README §5):

    piles (frame forces, z measured up from the fixed base):
        N = -P (compression +), Qx = V2, Qy = V3, Mx = M3, My = M2, T = T
    transverse beams (frames drawn from the sea side to the land side, along +Y):
        M = M3 (sagging +, i.e. tension in the bottom fibre), V = -V2 (= dM/dy), T = T
    edge beams (frames along +X):
        M = M3 (sagging +), V = -V2, T = T

Combinations are built by linear superposition of the six load cases with the factors of
sap2000/model/trasmallo.py (identical to Apéndice 1 §1.6.2 and to the combinations of the SAP
model).  Serviceability combinations for crack control are added here:

    QP(psi2) = PP + CM + psi2·Qa          (bollard / wind psi2 = 0, Código Estructural Anejo 18)

with psi2 = 0.3 (value used by CYPE, Anejo 10 P584) and psi2 = 0.8 (storage areas, category E,
conservative alternative).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "sap2000" / "model"))

import trasmallo as tm  # noqa: E402

SAP_FRAMES_XLSX = ROOT / "sap2000" / "resultados_sap" / "SAP27_Element_Forces_Frames.xlsx"
PATTERNS = tuple(tm.PATTERN_ORDER)                     # PP, CM, Qa, TB1, TB2, TB3
PILE_FREE_LENGTH = round(tm.PILE_LENGTH - tm.PILE_TOP_RIGID, 6)   # 6.70 m (head = beam soffit)
PSI2_QA_CYPE = 0.3
PSI2_QA_STORAGE = 0.8
COMPS_PILE = ("N", "Mx", "My", "Qx", "Qy", "T")
COMPS_BEAM = ("M", "V", "T")


def read_table(path: Path) -> list[dict]:
    """Rows of the first sheet of a SAP2000 table exported to Excel (title, header, units)."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    next(rows)
    header = list(next(rows))
    next(rows)
    return [dict(zip(header, r)) for r in rows if r and r[0] is not None]


@dataclass
class Station:
    """One output station of one frame; ``pos`` is z (piles, from the base), y (transverse
    beams) or x (edge beams), global, in m."""
    frame: str
    pos: float
    rigid: bool
    values: dict          # pattern -> {component: value}


def _pile_cype(r: dict) -> dict:
    return {"N": -r["P"], "Mx": r["M3"], "My": r["M2"], "Qx": r["V2"], "Qy": r["V3"], "T": r["T"]}


def _beam_cype(r: dict) -> dict:
    return {"M": r["M3"], "V": -r["V2"], "T": r["T"]}


def load_stations(path: Path = SAP_FRAMES_XLSX) -> dict:
    """{'piles': {P1: [Station...]}, 'beams': {axis: [Station...]}, 'edges': {portico: [...]}}

    Stations are keyed by (frame, station) so both ends of adjacent frames are kept (the
    shear and moment jump at load points is preserved)."""
    model = tm.build_model()
    frames = {f["name"]: f for f in model["frames"]}
    joints = model["joints"]
    acc: dict = {}
    for r in read_table(path):
        f = frames.get(r["Frame"])
        case = r["OutputCase"]
        if f is None or case not in PATTERNS:
            continue
        st = float(r["Station"])
        vals = {k: float(r[k]) for k in ("P", "V2", "V3", "T", "M2", "M3")}
        xi, yi, zi = joints[f["i"]]
        if f["kind"] == "pile":
            key, pos, conv = ("piles", f["cype"]), zi + st, _pile_cype(vals)
        elif f["kind"] == "beam_t":
            key, pos, conv = ("beams", f["axis"]), yi + st, _beam_cype(vals)
        elif f["kind"] == "beam_edge":
            key, pos, conv = ("edges", f["portico"]), xi + st, _beam_cype(vals)
        else:
            continue
        s = acc.setdefault(key, {}).setdefault((f["name"], round(st, 6)),
                                              Station(f["name"], round(pos, 6), bool(f.get("rigid")), {}))
        s.values[case] = conv
    out: dict = {"piles": {}, "beams": {}, "edges": {}}
    for (group, member), stations in acc.items():
        lst = sorted(stations.values(), key=lambda s: (s.pos, s.frame))
        missing = [s for s in lst if set(s.values) != set(PATTERNS)]
        if missing:
            raise ValueError(f"{group} {member}: stations without all load cases, e.g. "
                             f"{missing[0].frame} @ {missing[0].pos}")
        out[group][member] = lst
    return out


# --------------------------------------------------------------------------------------------
# combinations
# --------------------------------------------------------------------------------------------
def combos(include_els_qp: bool = True) -> dict[str, tuple]:
    """name -> factors on (PP, CM, Qa, TB1, TB2, TB3)."""
    out = {}
    for fam in ("ELU", "CIM", "ELS"):
        for i, fac in enumerate(tm.COMBOS[fam], 1):
            out[f"{fam}{i:02d}"] = tuple(fac)
    if include_els_qp:
        out["QP03"] = (1.0, 1.0, PSI2_QA_CYPE, 0.0, 0.0, 0.0)
        out["QP08"] = (1.0, 1.0, PSI2_QA_STORAGE, 0.0, 0.0, 0.0)
    return out


def combine(values: dict, factors: tuple, comps: tuple) -> dict:
    return {c: sum(f * values[p][c] for f, p in zip(factors, PATTERNS) if f) for c in comps}


def describe(factors: tuple) -> str:
    """'1.35·PP+1.35·CM+1.05·Qa+1.5·TB1' (CYPE style)."""
    parts = []
    for f, p in zip(factors, PATTERNS):
        if f:
            parts.append(p if abs(f - 1) < 1e-9 else f"{f:g}·{p}")
    return "+".join(parts)


def family(prefix: str) -> dict[str, tuple]:
    return {k: v for k, v in combos().items() if k.startswith(prefix)}


if __name__ == "__main__":
    data = load_stations()
    for g in ("piles", "beams", "edges"):
        print(g, {k: len(v) for k, v in data[g].items()})
    p3 = data["piles"]["P3"]
    fac = combos()["ELU08"]
    print("ELU08", describe(fac))
    for s in (p3[0], min(p3, key=lambda s: abs(s.pos - PILE_FREE_LENGTH))):
        print("P3 z=%.3f" % s.pos, {k: round(v, 2) for k, v in combine(s.values, fac, COMPS_PILE).items()})
