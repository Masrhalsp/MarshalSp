"""Tests of the SAP2000 concrete-design inputs (diseno/sap): design data, the .$2k writer (passes
sap2000/tools/check_s2k.py, unchanged tables byte-identical, rectangle + modifiers = composite
section to 1e-9), the OAPI script end to end on the strict mock (mock_sap_diseno.py) and the reader
of SAP's design tables."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parents[2]
for _p in (TESTS, ROOT / "diseno" / "sap", ROOT / "diseno" / "python" / "codigo", ROOT / "diseno" / "python",
           ROOT / "sap2000" / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos_diseno_sap as D  # noqa: E402
import leer_diseno_sap as L  # noqa: E402
import mock_sap_diseno as MD  # noqa: E402
import sap_oapi_diseno as S  # noqa: E402
import write_s2k_diseno as WD  # noqa: E402

CHECK_S2K = ROOT / "sap2000" / "tools" / "check_s2k.py"
COMPOSITE = ("VIGA_T50x55_ALAS15x30", "VIGA_L80x55_ALA15x30", "VIGA_L80x55_ALA15x30_M")


def rel(a: float, b: float) -> float:
    return abs(a / b - 1)


@pytest.fixture(scope="module")
def model():
    return D.base_model()


@pytest.fixture(scope="module")
def s2k_files(tmp_path_factory, model):
    out = tmp_path_factory.mktemp("s2k")
    paths = WD.write_all(out)
    paths.update({f"rom_{k}": v for k, v in WD.write_all(out, base="ROM", variants=("diseno",)).items()})
    return paths


def parsed(path: Path) -> tuple[list[str], list[list]]:
    return WD.parse_lines(path.read_bytes().decode("ascii").split("\r\n")[:-2])


def records(path: Path, title: str) -> list[dict]:
    _, tables = parsed(path)
    for t, recs in tables:
        if t == title:
            return [{k: v.strip('"') for k, v in r} for r in recs]
    return []


# --------------------------------------------------------------------------------------------
# design data
# --------------------------------------------------------------------------------------------
def test_sap_rectangle_formula():
    p = D.sap_rect_props(0.5, 0.5)
    assert p["TorsConst"] == pytest.approx(8.80208e-03, rel=1e-5)        # real export [G10] (spec A.6)
    assert p["AS2"] == pytest.approx(5 / 6 * 0.25)
    r = D.sap_rect_props(0.55, 0.50)
    assert r["I33"] == pytest.approx(0.5 * 0.55**3 / 12) and r["I22"] == pytest.approx(0.55 * 0.5**3 / 12)


def test_modifiers_match_spec_table(model):
    """Values of the spec table A.6 (rounded to 6 decimals there)."""
    spec = {"VIGA_T50x55_ALAS15x30": (1.327273, 1.313245, 1.433600, 1.467072, 2.688727, 1.250206),
            "VIGA_L80x55_ALA15x30": (1.102273, 1.105216, 1.135065, 1.107293, 1.396113, 1.087939),
            "VIGA_L80x55_ALA15x30_M": (1.102273, 1.105216, 1.134641, 1.107293, 1.396113, 1.087939)}
    dm = D.design_model(model)
    for name, vals in spec.items():
        m = dm["sections"][name].modifiers
        got = (m["AMod"], m["A2Mod"], m["A3Mod"], m["JMod"], m["I2Mod"], m["I3Mod"])
        assert got == pytest.approx(vals, abs=6e-7)
        assert m["MMod"] == m["WMod"] == m["AMod"]


def test_rectangle_plus_modifiers_reproduce_composite(model):
    """A, As2, As3, J, I22, I33, weight and mass of the analysis equal the composite section (1e-9),
    also with the x100 object modifiers of the rigid segments; piles / edge beams untouched."""
    dm = D.design_model(model)
    for name in COMPOSITE:
        comp = model["sections"][name]
        eff = D.effective_props(dm["sections"][name])
        base = D.effective_props(comp)
        for k in D.PROP_KEYS:
            assert rel(eff[k], comp.section.props[k]) < 1e-9, (name, k)
        assert rel(eff["weight_area"], base["weight_area"]) < 1e-9
        assert rel(eff["mass_area"], base["mass_area"]) < 1e-9
        assert dm["sections"][name].shape == "Rectangular"
        assert (dm["sections"][name].section.t3, dm["sections"][name].section.t2) == D.DESIGN_RECT[name]
    rigid = [f for f in model["frames"] if f.get("rigid")]
    assert len(rigid) == 21
    for f in rigid:
        new = D.effective_props(dm["sections"][f["section"]], f["modifiers"])
        old = D.effective_props(model["sections"][f["section"]], f["modifiers"])
        for k in (*D.PROP_KEYS, "weight_area", "mass_area"):
            assert rel(new[k], old[k]) < 1e-9, (f["name"], k)
        assert new["I33"] == pytest.approx(100 * model["sections"][f["section"]].section.props["I33"], rel=1e-12)
    for name in (D.PILE_SECTION, D.EDGE_SECTION):
        assert dm["sections"][name] is model["sections"][name]


def test_s2k_rectangles_reproduce_composite(s2k_files, model):
    """The same, read back from the text written in the .$2k files (12 significant digits)."""
    for key in ("rect", "diseno", "overwrites"):
        rows = {r["SectionName"]: r for r in records(s2k_files[key], WD.T_FSEC1)}
        for name in COMPOSITE:
            r = rows[name]
            assert r["Shape"] == "Rectangular" and "Area" not in r
            got = D.sap_rect_props(float(r["t3"]), float(r["t2"]))
            comp = model["sections"][name].section.props
            for k, mk in zip(D.PROP_KEYS, ("AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod")):
                assert rel(got[k] * float(r[mk]), comp[k]) < 1e-9, (key, name, k)
            for mk in ("MMod", "WMod"):
                assert rel(got["Area"] * float(r[mk]), comp["Area"]) < 1e-9
        assert rows[D.PILE_SECTION]["AMod"] == "2" and rows[D.EDGE_SECTION]["Shape"] == "Rectangular"


def test_design_data_consistent_with_codigo_modules():
    import armado_pilote as AP
    import armado_vigas as AV
    import esfuerzos as E
    assert D.PILE_REBAR.n_bars == 12
    assert D.PILE_REBAR.bar_axis_distance * 1000 == pytest.approx(AP.PileLayout().c)            # 127.5 mm
    assert D.PILE_REBAR.n_2dir_ties == D.PILE_REBAR.n_3dir_ties == AP.TIES_FUSTE.legs
    assert D.PILE_REBAR.tie_spacing * 1000 == AP.TIES_FUSTE.spacing and not D.PILE_REBAR.to_be_designed
    for axis, sec in ((2, "VIGA_T50x55_ALAS15x30"), (1, "VIGA_L80x55_ALA15x30"), (7, "VIGA_L80x55_ALA15x30_M")):
        pr, br = AV.provided(axis), D.BEAM_REBAR[sec]
        assert br.as_top * 1e6 == pytest.approx(pr.As("top"))
        assert br.as_bot * 1e6 == pytest.approx(pr.As("bottom"))
        assert br.asw_s * 1e3 == pytest.approx(pr.stirrups.asw_s)
        assert br.cover_top * 1000 == pytest.approx(pr.cover_axis("top"))
        assert br.cover_bot * 1000 == pytest.approx(pr.cover_axis("bottom"))
    pe, be = AV.provided_edge(1), D.BEAM_REBAR[D.EDGE_SECTION]
    assert be.cover_top * 1000 == pytest.approx(pe.cover_axis("top"))
    assert be.as_top * 1e6 == pytest.approx(pe.As("top"))
    assert D.combos("ROM") == {k: tuple(v) for k, v in E.uls("ROM").items()}
    assert D.combos("CYPE") == {k: tuple(v) for k, v in E.uls("CYPE").items()}
    assert D.PILE_LENGTH_RATIO * D.L_PILE == pytest.approx(6.70)
    assert D.KPHI_OPTIONS["ce"] == pytest.approx(1.373 * 8 / math.pi**2, abs=5e-5)
    assert {p.item for p in D.PREFERENCES} == set(range(1, 18))
    assert D.EC2_PREFS[3] == 2 and D.EC2_PREFS[9] == 1.5 and D.EC2_PREFS[10] == 1.0 and D.EC2_PREFS[15] == 1.0


def test_frame_classification(model):
    fds = D.frame_designs(model)
    assert sum(fd.design for fd in fds) == 254 and sum(not fd.design for fd in fds) == 21
    assert all(fd.design == (not f.get("rigid", False)) for fd, f in zip(fds, model["frames"]))
    ows = D.overwrites(model)
    assert len(ows) == 254
    pile = next(o for o in ows if o["frame"] == "PIL_P3")
    assert pile["oapi"] == {1: 3.0, 3: D.PILE_LENGTH_RATIO, 4: D.PILE_LENGTH_RATIO, 5: 1.0, 6: 1.0}
    assert pile["table"]["KPhi"] == D.KPHI_OPTIONS["ce"] and pile["table"]["TanTheta"] == 1.0
    beam = next(o for o in ows if o["frame"] == "VT2_5")
    assert beam["oapi"] == {1: 3.0} and "BetaMajor" not in beam["table"]


# --------------------------------------------------------------------------------------------
# .$2k writer
# --------------------------------------------------------------------------------------------
def test_parse_render_roundtrip(model):
    s = WD.W.build_tables(model)
    header, tables = WD.parse_lines(s.lines)
    assert WD.render(header, tables).lines == s.lines


@pytest.mark.parametrize("key", ["diseno", "overwrites", "rect", "rom_diseno"])
def test_s2k_passes_check_s2k(s2k_files, key):
    res = subprocess.run([sys.executable, str(CHECK_S2K), str(s2k_files[key])], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "OK - all references resolved" in res.stdout
    assert "PP (self weight)" in res.stdout and "794.9 kN" in res.stdout
    if key != "rect":
        assert "254 concrete-designed frames (14 columns, 240 beams), 21 'No Design'" in res.stdout


def test_check_s2k_catches_design_errors(s2k_files, tmp_path):
    text = s2k_files["diseno"].read_bytes().decode("ascii")
    bad = (text.replace("Frame=VT2_3   DesignProc=", "Frame=XX_9   DesignProc=")
               .replace("SectionName=VIGA_BORDE_25x30   RebarMatL=B500SD", "SectionName=NOPE   RebarMatL=B500SD")
               .replace("ComboName=ENV_ELU   ComboType=Envelope   AutoDesign=No   CaseName=ELU01   ScaleFactor=1   "
                        "SteelDesign=None   ConcDesign=None",
                        "ComboName=ENV_ELU   ComboType=Envelope   AutoDesign=No   CaseName=ELU01   ScaleFactor=1   "
                        "SteelDesign=None   ConcDesign=Strength"))
    assert bad != text
    p = tmp_path / "bad.$2k"
    p.write_bytes(bad.encode("ascii"))
    res = subprocess.run([sys.executable, str(CHECK_S2K), str(p)], capture_output=True, text=True)
    assert res.returncode == 1
    for msg in ("unknown frame XX_9", "03: unknown section NOPE", "Strength flag on a Envelope combo"):
        assert msg in res.stdout, res.stdout


def test_unchanged_tables_byte_identical(s2k_files, model):
    """Geometry, loads, combinations etc. are the records of sap2000/tools/write_s2k.build_tables."""
    _, orig = WD.parse_lines(WD.W.build_tables(model).lines)
    orig = dict((t, r) for t, r in orig)
    _, rect = parsed(s2k_files["rect"])
    changed = {t for t, r in rect if orig.get(t) != r}
    assert changed == {WD.T_FSEC1, "FRAME SECTION ASSIGNMENTS"}
    _, des = parsed(s2k_files["diseno"])
    des = dict((t, r) for t, r in des)
    same = [t for t in orig if t not in {WD.T_PROGRAM, WD.T_MAT1, WD.T_MAT2, WD.T_FSEC1, "FRAME SECTION ASSIGNMENTS",
                                         WD.T_COMBO, "GROUPS 1 - DEFINITIONS", "GROUPS 2 - ASSIGNMENTS"}]
    assert len(same) == 21
    for t in same:
        assert des[t] == orig[t], t
    # modified tables keep every original record in place (prefix), only additions / flag changes
    for t in (WD.T_MAT1, WD.T_MAT2, "GROUPS 1 - DEFINITIONS", "GROUPS 2 - ASSIGNMENTS"):
        assert des[t][:len(orig[t])] == orig[t], t
    for a, b in zip(orig[WD.T_COMBO], des[WD.T_COMBO]):
        assert [x for x in a if x[0] != "ConcDesign"] == [x for x in b if x[0] != "ConcDesign"]
    # the original file on disk is what build_tables writes
    committed = (ROOT / "sap2000" / "output" / "Muelle_Trasmallo_40m.$2k").read_bytes()
    assert WD.W.build_tables(model).text().encode("ascii") == committed


def test_design_tables_content(s2k_files):
    f = s2k_files["diseno"]
    assert records(f, WD.T_PROGRAM)[0]["ConcCode"] == "Eurocode 2-2004"
    assert records(f, WD.T_MAT3E)[0] == {"Material": "B500SD", "Fy": "500000", "Fu": "575000", "EffFy": "550000",
                                         "EffFu": "632500", "SSCurveOpt": "Simple", "SSHysType": "Kinematic",
                                         "SHard": "0.01", "SCap": "0.09", "FinalSlope": "-0.1", "UseCTDef": "No"}
    col = records(f, WD.T_FSEC2)
    assert col == [{"SectionName": "PILOTE_40x40", "RebarMatL": "B500SD", "RebarMatC": "B500SD",
                    "ReinfConfig": "Rectangular", "LatReinf": "Ties", "Cover": "0.05", "NumBars3Dir": "4",
                    "NumBars2Dir": "4", "BarSizeL": "25d", "BarSizeC": "10d", "SpacingC": "0.15", "NumCBars2": "4",
                    "NumCBars3": "4", "ReinfType": "Check"}]
    beams = {r["SectionName"]: r for r in records(f, WD.T_FSEC3)}
    assert set(beams) == {*COMPOSITE, D.EDGE_SECTION}
    assert beams["VIGA_T50x55_ALAS15x30"]["TopCover"] == "0.07" and beams[D.EDGE_SECTION]["BotCover"] == "0.066"
    assert float(beams["VIGA_T50x55_ALAS15x30"]["BotLeftArea"]) * 1e4 == pytest.approx(21.99, abs=0.01)
    proc = records(f, WD.T_PROC)
    assert len(proc) == 275 and sum(r["DesignProc"] == "No Design" for r in proc) == 21
    first = {}
    for r in records(f, WD.T_COMBO):
        first.setdefault(r["ComboName"], r)
    strength = sorted(c for c, r in first.items() if r.get("ConcDesign") == "Strength")
    assert strength == [f"ELU{k:02d}" for k in range(1, 23)]
    assert {f"ELR{k:02d}" for k in range(1, 23)} <= set(first) and "ENV_ELR" in first
    assert first["ELR08"]["Notes"].startswith("ELU rotura hormigon ROM")
    assert records(f, WD.T_AUTO) == [{"DesignType": "Concrete", "AutoGen": "No"}]
    pref = records(f, WD.T_PREF)[0]
    assert (pref["SOM"], pref["Country"], pref["GammaC"], pref["AlphaCC"], pref["UFLimit"], pref["Theta0"]) == \
        ("Nominal Curvature", "CEN Default", "1.5", "1", "1", "0.005")
    assert records(f, WD.T_OVER) == []
    groups = {r["GroupName"] for r in records(f, "GROUPS 1 - DEFINITIONS")}
    assert {"DISENO_PILOTES", "DISENO_VIGAS_T", "DISENO_VIGAS_BORDE", "NO_DISENO_RIGIDOS"} <= groups
    # optional variant: one EC2 overwrite record per designed frame
    ow = {r["Frame"]: r for r in records(s2k_files["overwrites"], WD.T_OVER)}
    assert len(ow) == 254 and "VT2_3" not in ow
    assert ow["PIL_P1"]["FrameType"] == "DC Low" and float(ow["PIL_P1"]["XLMajor"]) * 7.25 == pytest.approx(6.70)
    assert ow["PIL_P1"]["KPhi"] == "1.1129" and ow["VT2_5"]["TanTheta"] == "1" and "BetaMajor" not in ow["VT2_5"]
    # ROM basis: ELR flagged, ELU not
    first = {}
    for r in records(s2k_files["rom_diseno"], WD.T_COMBO):
        first.setdefault(r["ComboName"], r)
    assert sorted(c for c, r in first.items() if r.get("ConcDesign") == "Strength") == \
        [f"ELR{k:02d}" for k in range(1, 23)]
    # rect variant: no design table at all
    _, rect = parsed(s2k_files["rect"])
    titles = {t for t, _ in rect}
    assert not titles & {WD.T_FSEC2, WD.T_FSEC3, WD.T_PROC, WD.T_PREF, WD.T_OVER, WD.T_AUTO, WD.T_MAT3E}


def test_elr_combo_records_match_writer_format(model):
    """combo_records() formats a family exactly like write_s2k.build_tables (checked on ELU)."""
    _, orig = WD.parse_lines(WD.W.build_tables(model).lines)
    combos = dict(orig)[WD.T_COMBO]
    elu = [r for r in combos if WD.get(r, "ComboName").startswith(("ELU", "ENV_ELU"))]
    mine = WD.combo_records("CYPE", strength=False)
    strip = lambda recs: [[x for x in r if x[0] != "Notes"] for r in recs]   # noqa: E731
    assert strip(mine) == strip(elu)


# --------------------------------------------------------------------------------------------
# OAPI script on the mock
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def synth():
    return MD.XlsxSynth()


@pytest.fixture(scope="module")
def oapi(tmp_path_factory, synth):
    out = tmp_path_factory.mktemp("oapi")
    m = MD.SapModel(synth)
    res = S.run(m, out_dir=out, save_path=out / "x.sdb")
    return m, res, out


def test_oapi_settings(oapi):
    m, res, _ = oapi
    st = m._st
    d = st.design
    assert d.code == "Eurocode 2-2004"
    assert d.prefs == {k: float(v) for k, v in D.EC2_PREFS.items()}
    assert not d.auto_combos and d.strength == [f"ELU{k:02d}" for k in range(1, 23)]
    assert not any(c.startswith("DCon") for c in st.combos)
    assert {f"ELR{k:02d}" for k in range(1, 23)} <= set(st.combos)
    assert st.materials["B500SD"]["type"] == 6 and st.materials["B500SD"]["Fy"] == 500e3
    # sections: rectangles, modifiers from GetSectProps, rebar data
    for name in COMPOSITE:
        sec = st.frame_props[name]
        assert sec["shape"] == "Rect" and (sec["t3"], sec["t2"]) == D.DESIGN_RECT[name]
        mods = res["meta"]["beam_sections"][name]["modifiers"]
        assert sec["mods"] == [mods[k] for k in D.MOD_KEYS]
        assert res["meta"]["beam_sections"][name]["max_rel_dev_vs_formula"] < 1e-12
        assert sec["rebar"]["type"] == "beam" and sec["rebar"]["args"][2:4] == [0.07, 0.07]
    pile = st.frame_props["PILOTE_40x40"]
    assert pile["mods"][0] == 2.0 and pile["rebar"]["args"][6:9] == [4, 4, "25d"] and pile["rebar"]["args"][13] is False
    assert st.frame_props[D.EDGE_SECTION]["rebar"]["args"][2] == 0.066
    # procedures and overwrites
    assert st.frames["VT2_3"]["design_proc"] == 2 and st.frames["VT2_5"]["design_proc"] == 1
    assert d.overwrites["PIL_P1"] == {1: 3.0, 3: D.PILE_LENGTH_RATIO, 4: D.PILE_LENGTH_RATIO, 5: 1.0, 6: 1.0}
    assert d.overwrites["VBM_01"] == {1: 3.0} and "VT2_3" not in d.overwrites
    assert res["meta"]["table_overwrites"]["applied"] and res["meta"]["table_overwrites"]["rows_changed"] == 254
    assert d.table_overwrites["PIL_P3"] == {"TanTheta": "1", "KPhi": "1.1129"}
    assert d.table_overwrites["VT4_8"] == {"TanTheta": "1", "KPhi": "0"}
    assert res["meta"]["to_do"] == []
    assert {"DISENO_PILOTES", "NO_DISENO_RIGIDOS"} <= set(st.groups)
    assert st.saved_path.endswith("x.sdb")


def test_oapi_results_and_outputs(oapi, model):
    _, res, out = oapi
    assert (out / "diseno_SAP2000.json").exists() and (out / "diseno_SAP2000.xlsx").exists()
    js = json.loads((out / "diseno_SAP2000.json").read_text(encoding="utf-8"))
    assert set(js) == {"meta", "summary", "analysis_identity", "piles", "beams"}
    piles, beams = res["piles"], res["beams"]
    assert len({r["member"] for r in piles}) == 14 and len(piles) == 14 * 28
    p1 = [r for r in piles if r["member"] == "P1"]
    assert min(r["z"] for r in p1) == 0.0 and max(r["z"] for r in p1) == pytest.approx(6.70)
    assert all(r["option"] == "check" for r in piles)
    frames = {r["frame"] for r in beams}
    assert "VT2_3" not in frames and "VT2_5" in frames and any(f.startswith("VBM_") for f in frames)
    assert min(r["pos"] for r in beams if r["frame"] == "VT2_14") == pytest.approx(3.65)
    assert max(r["pos"] for r in beams if r["frame"] == "VT2_2") == pytest.approx(-0.20)
    assert min(r["pos"] for r in beams if r["frame"] == "VBM_01") == pytest.approx(0.40)
    sec = {s["section"]: s for s in res["summary"]["beams"]["VT2"]["sections"]}
    assert set(sec) == {"cara pilote mar - voladizo", "cara pilote mar - vano", "cara pilote tierra - vano",
                        "cara pilote tierra - vuelo", "vano: máx. positivo"}
    assert res["meta"]["verify_passed"]["failed"] == 0
    ident = res["analysis_identity"]
    assert ident["ok"] and ident["rows_compared"] > 3000


def test_oapi_fallback_and_options(tmp_path, synth):
    """No DatabaseTables overwrite table -> reported as a GUI to-do, run completes; a missing bar
    size is added with PropRebar.SetProp; ROM basis selects ELR01-22."""
    m = MD.SapModel(synth, missing_bars=("25d",), tables_available=False)
    res = S.run(m, base="ROM", kphi="cype", out_dir=tmp_path, save_path=tmp_path / "y.sdb", verify_analysis=False)
    assert not res["meta"]["table_overwrites"]["applied"]
    assert "K phi = 1.373" in res["meta"]["to_do"][0]
    assert res["meta"]["bar_sizes_added"] == ["25d"] and "25d" in m._st.design.bars
    assert m._st.design.strength == [f"ELR{k:02d}" for k in range(1, 23)]
    assert res["analysis_identity"] is None
    assert {r["pmm_combo"][:3] for r in res["piles"]} == {"ELR"}


def test_mock_strictness(synth):
    m = MD.SapModel(synth)
    import sap_oapi_run as sor
    sor.define_model(m, D.design_model())
    S.define_rebar(m)
    with pytest.raises(TypeError):                                    # 14 instead of 15 arguments
        m.PropFrame.SetRebarColumn("PILOTE_40x40", "B500SD", "B500SD", 1, 1, 0.05, 0, 4, 4, "25d", "10d", 0.15, 4, 4)
    with pytest.raises(MD.MockError):                                 # General sections cannot get rebar data
        m2 = MD.SapModel(synth)
        sor.define_model(m2, D.base_model())
        S.define_rebar(m2)
        m2.PropFrame.SetRebarBeam("VIGA_T50x55_ALAS15x30", "B500SD", "B500SD", 0.07, 0.07, 0, 0, 0, 0)
    ec2 = m.DesignConcrete.Eurocode_2_2004
    m.FrameObj.SetDesignProcedure("VT2_5", 1)
    m.PropFrame.SetRebarBeam(*D.BEAM_REBAR["VIGA_T50x55_ALAS15x30"].oapi_args())
    assert ec2.SetOverwrite("VT2_5", 5, 1.0) == 1                     # beta on a beam
    assert ec2.SetOverwrite("VT2_5", 7, 1.0) == 1                     # items 7-12 return 1 since v24.0
    assert ec2.SetOverwrite("VT2_5", 1, 3.0) == 0
    assert ec2.SetPreference(4, 30.0) == 1                            # not a multiple of 4


# --------------------------------------------------------------------------------------------
# reader
# --------------------------------------------------------------------------------------------
def test_units():
    assert L.area_to_cm2("m2") == 1e4 and L.area_to_cm2("mm²") == pytest.approx(0.01)
    assert L.area_to_cm2("cm2") == pytest.approx(1.0)
    assert L.per_length_to_cm2_m("m2/m") == 1e4 and L.per_length_to_cm2_m("mm2/mm") == pytest.approx(10.0)
    assert L.per_length_to_cm2_m("cm2/m") == pytest.approx(1.0) and L.per_length_to_cm2_m("mm2/m") == pytest.approx(0.01)
    assert L.length_to_m("mm") == 0.001
    with pytest.raises(ValueError):
        L.area_to_cm2("kN")


def _write_gui_export(path: Path, res: dict) -> None:
    """A SAP-like Excel export (title / fields / units / data) from the OAPI rows: column table in
    kN-m units, beam table in N-mm units (mm, mm2, mm2/mm) with the v20.1 beam field keys."""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Concrete Design 1 - Column Summ"
    ws.append(["TABLE:  Concrete Design 1 - Column Summary Data - Eurocode 2-2004"])
    ws.append(["Frame", "DesignSect", "DesignType", "DesignOpt", "Status", "Location", "PMMCombo", "PMMArea",
               "PMMRatio", "VMajCombo", "VMajRebar", "VMinCombo", "VMinRebar", "ErrMsg", "WarnMsg"])
    ws.append(["Text", "Text", "Text", "Text", "Text", "m", "Text", "m2", "Unitless", "Text", "m2/m", "Text", "m2/m",
               "Text", "Text"])
    for r in res["piles"]:
        ws.append([r["frame"], "PILOTE_40x40", "Column", "Check", "No Messages", r["loc"], r["pmm_combo"],
                   r["pmm_area_cm2"] / 1e4, r["pmm_ratio"], r["vmaj_combo"], r["av_major_cm2_m"] / 1e4,
                   r["vmin_combo"], r["av_minor_cm2_m"] / 1e4, "No Messages" if False else None, None])
    ws = wb.create_sheet("Concrete Design 2 - Beam Summar")
    ws.append(["TABLE:  Concrete Design 2 - Beam Summary Data - Eurocode 2-2004"])
    ws.append(["Frame", "DesignSect", "DesignType", "Status", "Location", "FTopCombo", "FTopArea", "FBotCombo",
               "FBotArea", "VCombo", "VRebar", "TLngCombo", "TLngArea", "TTrnCombo", "TTrnRebar", "ErrMsg", "WarnMsg"])
    ws.append(["Text", "Text", "Text", "Text", "mm", "Text", "mm2", "Text", "mm2", "Text", "mm2/mm", "Text", "mm2",
               "Text", "mm2/mm", "Text", "Text"])
    for r in res["beams"]:
        ws.append([r["frame"], "x", "Beam", "No Messages", r["loc"] * 1000, r["top_combo"], r["as_top_cm2"] * 100,
                   r["bot_combo"], r["as_bot_cm2"] * 100, r["v_combo"], r["asw_s_cm2_m"] / 10, r["tl_combo"],
                   r["asl_t_cm2"] * 100, r["tt_combo"], r["ast_s_cm2_m"] / 10, None, None])
    wb.save(path)


def test_reader_gui_export_equals_oapi_rows(oapi, tmp_path, model):
    """Positions: the OAPI rows add the unrounded station, the export carries it rounded to 0.1 mm."""
    def same(x, y):
        return x == pytest.approx(y, abs=1.1e-4) if isinstance(y, float) else x == y

    _, res, _ = oapi
    xl = tmp_path / "export.xlsx"
    _write_gui_export(xl, res)
    piles, beams, meta = L.from_gui_export([xl], model)
    assert len(meta["tables"]) == 2
    assert len(piles) == len(res["piles"]) and len(beams) == len(res["beams"])
    for a, b in zip(piles, res["piles"]):
        for k in ("frame", "member", "z", "pmm_combo", "pmm_ratio", "av_major_cm2_m", "pmm_area_cm2"):
            assert same(a[k], b[k]), (k, a[k], b[k])
    for a, b in zip(beams, res["beams"]):
        for k in ("frame", "member", "pos", "as_top_cm2", "as_bot_cm2", "asw_s_cm2_m", "asl_t_cm2", "ast_s_cm2_m"):
            assert same(a[k], b[k]), (k, a[k], b[k])
    assert L.detect_base(piles, beams) == "CYPE"


def test_reader_comparison(oapi, tmp_path):
    _, _, out = oapi
    res = L.run([out / "diseno_SAP2000.json"])
    assert res["meta"]["base"] == "CYPE"
    t = res["tables"]
    assert len(t["sap_pilotes"]) == 14 and len(t["sap_vigas"]) == 9
    paths = L.write_report(res, tmp_path)
    assert paths["md"].read_text(encoding="utf-8").startswith("# Diseño SAP2000")
    if res["meta"]["ours"]["pilotes"]:
        assert len(t["pilotes"]) == 14 and all("cype_aprov_fuste" in r for r in t["pilotes"])
        p3 = next(r for r in t["pilotes"] if r["pile"] == "P3")
        assert p3["cype_aprov_fuste"] == pytest.approx(0.925)
    if res["meta"]["ours"]["vigas"]:
        flex = t["vigas_flexion"]
        face = [r for r in flex if r["member"] == "VT2" and r["section"] == "cara pilote mar - vano" and r["face"] == "top"]
        assert face and face[0]["sap_As_cm2"] is not None and face[0]["sap_pos"] == pytest.approx(0.20)
        axis = [r for r in flex if r["section"].startswith("eje pilote")]
        assert axis and all(r["sap_As_cm2"] is None for r in axis)
        shear = [r for r in t["vigas_cortante"] if r["member"] == "VT2" and r["section"] == "cara pilote mar - vano"]
        assert shear and shear[0]["face_pos"] == 0.20 and shear[0]["sap_Asw_s_face_cm2_m"] is not None
        edge = [r for r in flex if r["member"] == "VBM"]
        assert edge and all(r["sap_As_cm2"] is not None for r in edge)
        for r in t["vigas_cortante"]:                  # SAP runs with TanTheta = 1: compare at cot theta = 1
            assert r["ours_Asw_s_cot1_cm2_m"] == pytest.approx(r["ours_Asw_s_req_cm2_m"] * (r["ours_cot_theta"] or 1),
                                                               abs=1e-3)
    assert set(res) >= {"meta", "tables", "summary", "cype_comparison", "proposal"}
    assert len(res["cype_comparison"]) == 14 and all("diff_pct" in r for r in res["cype_comparison"])


def test_kphi_options_e2():
    """SAP e2 = Kphi·eps_yd/(0.45·327.5)·l0²/8: 'ce' = CYPE e2 92.12 mm (A10 dump), 'ce_is' = CE-strict
    e2 with d = h/2 + is = 306.96 mm (pilotes.json 98.29 mm), 'cype' = 113.6 mm."""
    e2 = {k: D.KPHI_OPTIONS[k] * (500 / 1.15 / 200000) / (0.45 * 327.5) * 6700**2 / 8 for k in ("ce", "ce_is", "cype")}
    assert e2["ce"] == pytest.approx(92.12, abs=0.02)
    assert e2["ce_is"] == pytest.approx(98.29, abs=0.02)
    assert e2["cype"] == pytest.approx(113.64, abs=0.02)


def test_sap_procedure_estimate_piles():
    """Our forces through SAP's EC2 column procedure (manual 3.4.2): with M0e the sway piles are
    governed by the first-order end check + Mi = N·emin (P3 ~0.71, nm1 0.679), with M2 added to the
    end moment ~ our nm2 (0.933); hand check of P3 ELU08 head: N 628.5, M 285.5 + 628.5·0.020 kNm."""
    rows, meta = L.sap_pile_estimates("CYPE")
    assert meta["e2_mm"] == pytest.approx(92.12, abs=0.02) and meta["ei_mm"] == 20.0 and meta["c"] == 8
    p3 = next(r for r in rows if r["pile"] == "P3")
    assert p3["sap_est_M0e"] == pytest.approx(0.714, abs=0.01) and p3["combo_M0e"] == "ELU08"
    assert p3["gov_M0e"].startswith("1er orden") and p3["gov_M0e"].endswith("cabeza")
    assert p3["sap_est_estacion"] == pytest.approx(0.93, abs=0.015)
    assert len(rows) == 14 and all(r["sap_est_estacion"] >= r["sap_est_M0e"] - 1e-9 for r in rows)
