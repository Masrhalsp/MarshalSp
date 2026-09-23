"""Comparison of model results with the CYPECAD results of Anejo 10 (Apéndice 1).

Used by ``verify_pynite.py`` (independent check) and ``sap_oapi_run.py`` (SAP2000 results),
so both produce the same tables.  Results are passed per load pattern in the CYPE sign
convention (pile local axes = global axes):

    pile_base[pile][pattern] = {N, Mx, My, Qx, Qy, T}   base (arranque), action on foundation
    pile_head[pile][pattern] = {N, Mx, My, Qx, Qy, T}   pile section 6.70 m above the base
    beams[axis][pattern]     = [(y, M, V), ...]          transverse beam, M > 0 sagging,
                                                         V = dM/dy (CYPE Vz), y global

Combinations are built by linear superposition with the factors of model/trasmallo.py, i.e.
exactly the CYPE tables of §1.6.2 (first-order values; the CYPE design tables §3.5/§4.2 add
second-order eccentricities and are not compared).

SAP2000 -> CYPE conversion (derived in README §6):
    pile base reaction:  N = F3, Qx = -F1, Qy = -F2, Mx = -M2, My = M1, T = -M3
    pile frame forces:   N = -P, Qx = V2, Qy = V3, Mx = M3, My = -M2, T = T
    transverse beams:    M = M3, V = -V2 (frames drawn from the sea side to the land side)
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "model"))

import trasmallo as tm  # noqa: E402

HYP = {"PP": "Peso propio", "CM": "Cargas muertas", "Qa": "Sobrecarga de uso",
       "TB1": "Tiro bolardo", "TB2": "Tiro Bolardo 2", "TB3": "Tiro bolardo 3"}
COMPS = ("N", "Mx", "My", "Qx", "Qy", "T")
FAMILY_NAME = {"ELU": "E.L.U. hormigón", "CIM": "E.L.U. cimentaciones", "ELS": "Desplazamientos"}
PORTICO_OF_AXIS = {a: a + 2 for a in range(1, tm.N_AXES + 1)}
FACE_S = tm.Y_PILE_SEA + tm.BEAM_RIGID_AT_PILE
FACE_L = tm.Y_PILE_LAND - tm.BEAM_RIGID_AT_PILE


def load_ref(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _combine(by_pat: dict, fac: tuple, comp: str) -> float:
    return sum(f * by_pat[p][comp] for f, p in zip(fac, tm.PATTERN_ORDER) if f)


def _cype_hyp(ref_pile: dict) -> dict:
    return {p: ref_pile[HYP[p]] for p in tm.PATTERN_ORDER}


# --------------------------------------------------------------------------------------------
def pile_hypothesis_rows(pile_base: dict, ref: dict) -> list[dict]:
    base = ref["pile_base_forces_arranques_3_4"]["piles"]
    rows = []
    for pile in sorted(pile_base, key=lambda s: int(s[1:])):
        for pat in tm.PATTERN_ORDER:
            cy = base[pile][HYP[pat]]
            for c in COMPS:
                m = pile_base[pile][pat][c]
                rows.append({"pile": pile, "hyp": pat, "comp": c, "model": round(m, 2),
                             "cype": cy[c], "diff": round(m - cy[c], 2)})
    return rows


def pile_envelope_rows(pile_base: dict, pile_head: dict | None, ref: dict) -> list[dict]:
    """Per family and pile: N max / N min / |My| max / |Mx| max at the base (and head)."""
    base = ref["pile_base_forces_arranques_3_4"]["piles"]
    head_ref = ref["pile_forces_by_hypothesis_3_3"]["piles"]
    rows = []
    for fam, combos in tm.COMBOS.items():
        for pile in sorted(pile_base, key=lambda s: int(s[1:])):
            for where, ours_src, cy_src in (
                ("base", pile_base[pile], _cype_hyp(base[pile])),
                ("cabeza", (pile_head or {}).get(pile),
                 {p: head_ref[pile]["hyp"][HYP[p]]["Cabeza"] for p in tm.PATTERN_ORDER}),
            ):
                if ours_src is None:
                    continue
                for key, comp, sign in (("N max", "N", 1), ("N min", "N", -1),
                                        ("|My| max", "My", 0), ("|Mx| max", "Mx", 0)):
                    def val(src, fac):
                        v = _combine(src, fac, comp)
                        return abs(v) if sign == 0 else sign * v
                    k_best = max(range(len(combos)), key=lambda k: val(ours_src, combos[k]))
                    k_cy = max(range(len(combos)), key=lambda k: val(cy_src, combos[k]))
                    m = _combine(ours_src, combos[k_best], comp)
                    c = _combine(cy_src, combos[k_cy], comp)
                    rows.append({"family": fam, "pile": pile, "where": where, "what": key,
                                 "model": round(m, 1), "model_comb": k_best + 1,
                                 "cype": round(c, 1), "cype_comb": k_cy + 1,
                                 "diff_%": round(100 * (abs(m) - abs(c)) / abs(c), 1) if abs(c) > 1 else None})
    return rows


def _at(line: list[tuple[float, float, float]], y: float, idx: int) -> float:
    """Linear interpolation of column ``idx`` (1 = M, 2 = V) at position y, taking the value on
    the span side of a discontinuity."""
    pts = sorted(line)
    for (y0, *a), (y1, *b) in zip(pts, pts[1:]):
        if y0 - 1e-9 <= y <= y1 + 1e-9 and y1 > y0:
            t = (y - y0) / (y1 - y0)
            return a[idx - 1] + t * (b[idx - 1] - a[idx - 1])
    raise ValueError(f"y={y} outside beam line")


def beam_envelope_rows(beams: dict, ref: dict, family: str = "ELU") -> list[dict]:
    """Transverse beams, span between the pile faces: M- at the faces, M+ in the span, V at the
    faces, for the envelope of one combination family, against CYPE §2 (and the peak labels
    of the beam drawings)."""
    combos = tm.COMBOS[family]
    rows = []
    for axis in sorted(beams):
        lines = beams[axis]
        ys = sorted({y for y, _, _ in lines["PP"] if FACE_S - 1e-9 <= y <= FACE_L + 1e-9})
        ys = sorted(set(ys) | {FACE_S, FACE_L})

        def comb(y: float, fac: tuple, idx: int) -> float:
            return sum(f * _at(lines[p], y, idx) for f, p in zip(fac, tm.PATTERN_ORDER) if f)

        m_face_s = min(comb(FACE_S, f, 1) for f in combos)
        m_face_l = min(comb(FACE_L, f, 1) for f in combos)
        m_span = max(comb(y, f, 1) for y in ys for f in combos)
        v_s = max(comb(FACE_S + 1e-6, f, 2) for f in combos)
        v_l = min(comb(FACE_L - 1e-6, f, 2) for f in combos)
        por = f"Pórtico {PORTICO_OF_AXIS[axis]}"
        tramo = ref["beams_listing_2"]["porticos"][por]["tramos"][-1]
        env = tramo["envelope_over_zones"]
        draw = ref["beams_diagram_labels_from_images"].get(por, {})
        for what, m, c, c2 in (
            ("M- cara pilote mar", m_face_s, env["M_min"]["value"], draw.get("My_min")),
            ("M- cara pilote tierra", m_face_l, None, None),
            ("M+ vano", m_span, env["M_max"]["value"], draw.get("My_max")),
            ("V cara mar", v_s, env["V_max"]["value"], None),
            ("V cara tierra", v_l, env["V_min"]["value"], None),
        ):
            ref_v = c2 if c2 is not None else c
            rows.append({"family": family, "portico": por, "tramo": tramo["tramo"],
                         "section": tramo.get("section"), "what": what, "model": round(m, 1),
                         "cype_listing": c, "cype_drawing": c2,
                         "diff_%": round(100 * (m - ref_v) / abs(ref_v), 1) if ref_v else None})
    return rows


def totals_rows(pile_base: dict, ref: dict) -> list[dict]:
    rows = []
    sums = {r["hypothesis"]: r for r in ref["derived_by_extractor"]["equilibrium_vs_3_7"]["rows"]}
    for pat in tm.PATTERN_ORDER:
        for c, key in (("N", "3_7_N"), ("Qy", "3_7_Qy")):
            m = sum(pile_base[p][pat][c] for p in pile_base)
            cy = sums[HYP[pat]][key]
            rows.append({"hyp": pat, "comp": f"sum {c}", "model": round(m, 1), "cype": cy,
                         "diff_%": round(100 * (m - cy) / abs(cy), 1) if abs(cy) > 1 else None})
    return rows


# --------------------------------------------------------------------------------------------
def build_report(pile_base: dict, pile_head: dict | None, beams: dict | None, ref: dict,
                 source: str) -> dict:
    rep = {"source": source,
           "totals": totals_rows(pile_base, ref),
           "pile_hypotheses": pile_hypothesis_rows(pile_base, ref),
           "pile_envelopes": pile_envelope_rows(pile_base, pile_head, ref)}
    if beams:
        rep["beam_envelopes"] = beam_envelope_rows(beams, ref, "ELU")
    return rep


def _md_table(rows: list[dict], cols: list[str]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + " |")
    return out


def write_report(rep: dict, out_dir: Path, stem: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{stem}.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    for key in ("totals", "pile_hypotheses", "pile_envelopes", "beam_envelopes"):
        rows = rep.get(key)
        if rows:
            with open(out_dir / f"{stem}_{key}.csv", "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
    md = [f"# Comparación con Anejo 10 (CYPECAD) — {rep['source']}", ""]
    md += ["## Totales por hipótesis (suma de arranques vs §3.7)", ""]
    md += _md_table(rep["totals"], ["hyp", "comp", "model", "cype", "diff_%"])
    md += ["", "## Envolventes de pilotes (primer orden)", ""]
    env = [r for r in rep["pile_envelopes"] if r["where"] == "base"]
    worst = {}
    for r in env:
        k = (r["family"], r["what"])
        if k not in worst or abs(r["model"]) > abs(worst[k]["model"]):
            worst[k] = r
    md += _md_table(list(worst.values()), ["family", "what", "pile", "model", "model_comb",
                                           "cype", "cype_comb", "diff_%"])
    if rep.get("beam_envelopes"):
        md += ["", "## Vigas transversales — envolvente E.L.U. (tramo entre caras de pilotes)", ""]
        md += _md_table(rep["beam_envelopes"], ["portico", "section", "what", "model",
                                                "cype_listing", "cype_drawing", "diff_%"])
    md += ["", "## Arranques por hipótesis: máxima diferencia por componente", ""]
    worst = {}
    for r in rep["pile_hypotheses"]:
        k = (r["hyp"], r["comp"])
        if k not in worst or abs(r["diff"]) > abs(worst[k]["diff"]):
            worst[k] = r
    md += _md_table(list(worst.values()), ["hyp", "comp", "pile", "model", "cype", "diff"])
    path = out_dir / f"{stem}.md"
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return path
