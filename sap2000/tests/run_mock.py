"""Run tools/sap_oapi_run.py end-to-end against the strict mock OAPI and compare the resulting
report with the PyNite route (same model data)."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "model"))

import mock_sap  # noqa: E402
from synth import Synth  # noqa: E402

import sap_oapi_run as sor  # noqa: E402
import trasmallo as tm  # noqa: E402
import verify_pynite as vp  # noqa: E402
from compare import build_report, load_ref  # noqa: E402

import tempfile
OUT = Path(tempfile.gettempdir()) / "trasmallo_mock_out"
OUT.mkdir(exist_ok=True)

synth = Synth()
ref = load_ref(ROOT / "ref" / "cype_reference.json")

# ---------------- 1. define_model + extract through the mock ------------------------------
m = mock_sap.SapModel(synth)
model = tm.build_model()
sor.define_model(m, model)
st = m._st
print("define_model OK:", len(st.points), "points,", len(st.frames), "frames,", len(st.areas), "areas,",
      len(st.patterns), "patterns", sorted(st.patterns), "cases", sorted(st.cases), len(st.combos), "combos")
assert set(st.points) == set(model["joints"])
assert set(st.frames) == {f["name"] for f in model["frames"]}
assert set(st.areas) == {a["name"] for a in model["areas"]}
print("frame props:", {k: v["mods"] for k, v in st.frame_props.items()})
print("area props:", {k: [round(x, 4) for x in v.get("mods", [])] for k, v in st.area_props.items()})

print("MODAL run flag call ->", m.Analyze.SetRunCaseFlag("MODAL", False))
mock_sap._count  # noqa
m.File.Save(r"C:\tmp\x.sdb")
m.Analyze.RunAnalysis()
raw = sor.extract(m, model)
print({k: len(v) for k, v in raw.items()})
pile_base, pile_head, beams = sor.to_compare_inputs(raw)
rep_sap = build_report(pile_base, pile_head, beams, ref, "SAP2000 (mock)")

# ---------------- 2. PyNite route (as tools/verify_pynite.py main) --------------------------
model2 = tm.build_model()
res, fe = vp.run(model2, with_fe=True)
pb2 = {p: {pat: vp.to_cype(r) for pat, r in by.items()} for p, by in res.items()}
ph2 = {p: {pat: vp.pile_head_forces(fe, model2, pat, p) for pat in tm.PATTERN_ORDER} for p in res}
bm2 = {a: {pat: vp.beam_line(fe, model2, a, pat) for pat in tm.PATTERN_ORDER} for a in range(1, tm.N_AXES + 1)}
rep_pn = build_report(pb2, ph2, bm2, ref, "PyNite")

# ---------------- 3. compare ---------------------------------------------------------------
def maxdiff(a, b):
    worst = (0.0, None)
    for p in a:
        for pat in a[p]:
            for k in a[p][pat]:
                d = abs(a[p][pat][k] - b[p][pat][k])
                if d > worst[0]:
                    worst = (d, (p, pat, k, a[p][pat][k], b[p][pat][k]))
    return worst

print("pile_base  SAP-route vs PyNite max |diff|:", maxdiff(pile_base, pb2))
print("pile_head  SAP-route vs PyNite max |diff|:", maxdiff(pile_head, ph2))
for comp in ("N", "Mx", "My", "Qx", "Qy", "T"):
    d = max(abs(pile_head[p][pat][comp] - ph2[p][pat][comp]) for p in ph2 for pat in tm.PATTERN_ORDER)
    s = max(abs(pile_head[p][pat][comp] + ph2[p][pat][comp]) for p in ph2 for pat in tm.PATTERN_ORDER)
    print(f"   head {comp:2s}: max|SAP-PyN| = {d:9.4f}   max|SAP+PyN| = {s:9.4f}")

for key in ("totals", "pile_hypotheses", "pile_envelopes", "beam_envelopes"):
    a, b = rep_sap[key], rep_pn[key]
    bad = [(x, y) for x, y in zip(a, b)
           if any(isinstance(x[k], float) and abs(x[k] - y[k]) > 0.15 for k in x)]
    print(f"report[{key}]: {len(a)} rows, {len(bad)} rows differ")
    for x, y in bad[:8]:
        print("   SAP:", {k: x[k] for k in x if k not in ('cype_listing',)})
        print("   PyN:", {k: y[k] for k in y if k not in ('cype_listing',)})

json.dump({"sap": rep_sap, "pynite": rep_pn}, open(OUT / "reports.json", "w"), indent=1, ensure_ascii=False)
print("calls:", json.dumps(mock_sap.CALLS, indent=0))

# ---------------- 4. seismic variant (--sismo) through the mock -----------------------------
import sismo_sap as sis  # noqa: E402

mock_sap.CALLS.clear()
m2 = mock_sap.SapModel(synth)
raw_s = sor.run(sap_model=m2, sismo=True, out_dir=OUT, save=OUT / "x_sismo.sdb")
st2 = m2._st
rs_names = [c["case"] for c in sis.rs_cases(model)]
assert st2.cases["MODAL"]["type"] == "Modal" and st2.cases["MODAL"]["max_modes"] == sis.n_modes(model)
assert all(st2.cases[c]["type"] == "RS" and st2.cases[c]["modal"] == "MODAL" and st2.cases[c]["damp"] == 0.05
           and st2.cases[c]["modal_comb"] == 2 for c in rs_names)
assert [ld[:3] for c in rs_names for ld in st2.cases[c]["loads"]] == \
    [(c["dir"], c["func"], sis.G) for c in sis.rs_cases(model)]
ms = st2.mass_sources["MSSSRC1"]
assert ms["default"] and ms["loads"] and not ms["elements"] and ms["patterns"] == [("PP", 1.0), ("CM", 1.0), ("Qa", 0.8)]
assert set(st2.rs_funcs) >= {"FUNC_H", "FUNC_V"}
assert st2.run_flags["MODAL"], "MODAL must run in the seismic variant"
for c in sis.combos(model):
    assert [(n, sf) for _t, n, sf in st2.combos[c["name"]]["items"]] == [(n, sf) for _k, n, sf in c["items"]]
assert len(raw_s["modal_periods"]) == sis.n_modes(model) and len(raw_s["modal_mass"]) == sis.n_modes(model)
assert {r["case"] for r in raw_s["rs_pile_forces"]} == set(rs_names)
assert {r["step"] for r in raw_s["rs_pile_forces"]} == {"Max"}
assert {r["case"] for r in raw_s["combo_pile_forces"]} == set(sis.combo_names(model))
assert {r["step"] for r in raw_s["combo_reactions"]} == {"Max", "Min"}
for key in ("reactions", "pile_forces", "beam_forces", "deck_displacements"):
    assert raw_s[key] == raw[key], f"static results changed by --sismo: {key}"
for f in ("resultados_SAP2000_sismo.json", "comparacion_SAP2000_sismo.md"):
    assert (OUT / f).exists(), f
print("seismic variant OK:", {k: len(v) for k, v in raw_s.items() if isinstance(v, list)})
print("seismic summary:", {k: v for k, v in raw_s["seismic_summary"].items() if k != "pile_max"})
print("seismic calls:", {k: v for k, v in mock_sap.CALLS.items()
                         if any(t in k for t in ("Modal", "Spectrum", "Mass", "FuncRS", "Combo"))})
