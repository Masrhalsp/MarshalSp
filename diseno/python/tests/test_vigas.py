"""Tests of diseno/python/codigo/vigas.py and armado_vigas.py: CYPE parity (Anejo 10, Mode.CYPE,
basis CYPE; tolerances as in diseno/python/investigacion/validate_codigo.py: 0.5 % or half a unit of the
last printed digit) and sanity checks of the final design (Mode.CODIGO, basis ROM, XS3)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CODIGO = Path(__file__).resolve().parents[1] / "codigo"
if str(CODIGO) not in sys.path:
    sys.path.insert(0, str(CODIGO))

import armado_vigas as AV  # noqa: E402
import vigas as V  # noqa: E402
from seccion import KNM, Mode, RCSection  # noqa: E402


def rel(a: float, b: float) -> float:
    return abs(a / b - 1)


# --------------------------------------------------------------------------------------------
# provided reinforcement and sections
# --------------------------------------------------------------------------------------------
def test_geometry():
    t, l1, r = AV.geometry_T(), AV.geometry_L(+1), AV.geometry_R()
    assert t.Ac == pytest.approx(365000.0)                      # 3650 cm2 (P364 table)
    assert t.yc == pytest.approx(244.18, abs=0.01)
    assert t.W("top") / 1e3 == pytest.approx(28339.35, rel=1e-6)  # P359 table
    assert l1.Ac == pytest.approx(485000.0)
    assert l1.yc == pytest.approx(263.40, abs=0.01)
    assert AV.geometry_L(-1).xc == pytest.approx(-l1.xc)
    assert r.Ac == pytest.approx(75000.0)


def test_areas_match_cype_listing():
    rows = AV.reference_areas()
    assert len(rows) == 27
    for x in rows:
        assert x["ours"] == pytest.approx(x["cype"], abs=0.006), x


def test_strip_mesh_equals_square_mesh():
    r = AV.provided(2)
    strip = r.section(Mode.CYPE).capacity_uniaxial(0.0, -1)["Mx"]
    sq = RCSection("sq", r.geom.rects, r.bars(Mode.CYPE), r.concrete, mode=Mode.CYPE).capacity_uniaxial(0.0, -1)["Mx"]
    assert rel(strip, sq) < 1e-4


# --------------------------------------------------------------------------------------------
# CYPE parity: body check P3-P4 (CYPE printed forces)
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def body():
    return {x["quantity"]: x for x in V.parity_body_check()}


@pytest.mark.parametrize("key, cype, tol", [
    ("P3-P4 MRd,x (hogging, Mode.CYPE)", -325.78, 5e-4),
    ("P3-P4 neutral-axis depth x (figure image112)", 68.52, 5e-4),
    ("P3-P4 Cc at ultimate", 767.00, 5e-4),
    ("P3-P4 eta N,M = 273.71/MRd", 0.840, 6e-4),
    ("P3-P4 VRd,max (theta 45)", 1512.00, 5e-4),
    ("P3-P4 VRd,s (3 legs Ø10/100, fywd 400)", 407.15, 5e-4),
    ("P3-P4 eta VEd/VRd,s (VEd = 390.18)", 0.958, 6e-4),
    ("P3-P4 eta VEd/VRd,max", 0.258, 2e-3),
    ("P3-P4 'Área Transv. Nec.' = VEd/(z fywd) [cm2/m]", 22.58, 5e-4),
    ("As,min top (z = 0.9d = 432, CYPE C14) [cm2]", 5.09, 1.1e-3),
    ("As,min bottom (z = 0.9d) [cm2]", 6.37, 1e-3),
    ("'Área Inf. Nec.' Mmax = 294.61 [cm2]", 15.10, 1e-3),
    ("'Área Sup. Nec.' M(P3) = -273.71 [cm2]", 13.72, 1e-3),
    ("rho_w,min·bw (50 cm web) [cm2/m]", 4.73, 1.1e-3),
    ("rho_w,min·bw (25 cm edge beam) [cm2/m]", 2.37, 2.2e-3),
    ("sl,max = 0.75 d [mm]", 360, 1e-9),
    ("st,max = 0.75 d [mm]", 360, 1e-9),
    ("sigma_ct bottom at M_qp = 86 kN·m (hand check) [MPa]", -2.20, 2.3e-3),
    ("Mcr,sag (fctm, homogenised) [kN·m]", 125.21, 1e-3),
    ("wk at M = 151.9 (psi2 0.8, SAP) [mm], bars 5Ø20+7Ø20", 0.1802, 5e-3),
    ("wk at M = Mcr,sag [mm]", 0.1486, 5e-3),
    ("Pórtico 3 'Área Sup. Nec.' node M = -318.8 [cm2]", 15.98, 1e-3),
    ("Pórtico 3 'Área Inf. Nec.' M = 275.15 [cm2]", 13.80, 1e-3),
    ("Pórtico 9 'Área Sup. Nec.' node M = -291.23 [cm2]", 14.56, 1e-3),
    ("Pórtico 9 'Área Inf. Nec.' M = 247.61 [cm2]", 12.38, 1e-3),
    ("Pórtico 3 P9-P1 Tst = (T/(2 Ak fyd))/(Ø10/100) [%]", 15.3, 4e-3),
    ("Pórtico 3 P9-P1 'Área Transv. Nec.' 1/3L = V/(z fywd) + 2 T/(2 Ak fyd) [cm2/m]", 8.28, 1e-3),
])
def test_body_check_parity(body, key, cype, tol):
    x = body[key]
    assert x["cype"] == pytest.approx(cype)
    assert rel(x["ours"], cype) <= tol, x


def test_body_check_all_pass(body):
    bad = [x for x in body.values() if x["status"] == "DIFF"]
    assert not bad, bad


def test_end_frame_calibration(body):
    """Ledge-top Ø20 active and 2Ø10 inactive reproduce CYPE §4.3 N,M within 0.3 points."""
    assert abs(body["Pórtico 3 §4.3 N,M eta at the node (M = -318.8) [%]"]["ours"] - 93.4) < 0.3
    assert abs(body["Pórtico 9 §4.3 N,M eta at the node (M = -291.23) [%]"]["ours"] - 85.4) < 0.3
    assert abs(body["Pórtico 3 P9-P1 Tc = T/TRd,max (T = 25.79, nu 0.6) [%]"]["ours"] - 4.6) < 0.05
    assert abs(body["Pórtico 3 P1-P2 Tc (T = 27.43) [%]"]["ours"] - 4.9) < 0.05


def test_code_strict_capacity():
    """U.54: no 10 permil steel limit -> -332.78 (skin bars inactive); all bars active -> larger."""
    r = AV.provided(2)
    strict_c3 = r.with_face("side", [g for g in r.face_groups("side") if g.active_cype])
    assert V.mrd(strict_c3, Mode.CODIGO, "top")["MRd"] / KNM == pytest.approx(332.78, rel=1e-3)
    assert V.mrd(r, Mode.CODIGO, "top")["MRd"] > V.mrd(r, Mode.CYPE, "top")["MRd"]


def test_shear_and_torsion_formulas():
    assert V.vrd_max(500, 432, 1.0) / 1e3 == pytest.approx(1512.0)
    assert V.vrd_max(500, 432, 2.0) == pytest.approx(0.8 * V.vrd_max(500, 432, 1.0))
    assert V.vrd_s(AV.provided(2).stirrups.asw_s, 432, 1.0) / 1e3 == pytest.approx(407.15, abs=0.01)
    tw = V.thin_wall(AV.provided(1))
    assert tw["tef"] == pytest.approx(440000 / 2700)
    assert V.trd_max(tw, 1.0, 0.6) / KNM == pytest.approx(562.5, abs=0.1)
    # cot(theta) never outside 0.5..2 and never gives crushing
    case = V.CASES[2]
    tw2 = V.thin_wall(AV.provided(2))
    cot, K = V.cot_theta(case, 500, 432, tw2, [(540.0, 17.5)])          # kN, kN·m
    K_ref = 17.5e6 / V.trd_max(tw2, 1.0, V.NU_T_CE) / 2 + 540e3 / V.vrd_max(500, 432, 1.0) / 2
    assert K == pytest.approx(K_ref) and K == pytest.approx(0.213, abs=0.002)
    assert cot == 2.0
    cot, K = V.cot_theta(case, 500, 432, tw2, [(1200.0, 17.5)])         # strut governs: 1 < cot < 2
    assert 1.0 < cot < 2.0 and K * (cot + 1 / cot) == pytest.approx(1.0)
    cot, K = V.cot_theta(case, 500, 432, tw2, [(2400.0, 17.5)])         # crushing at any angle
    assert cot == 1.0 and K * 2 > 1.0
    # plate bearing on the end-beam ledge: 1.35G + 1.5Qa -> 56 kN·m at the pile faces
    assert V.ledge_torsion((1.35, 1.35, 1.5, 0, 0, 0)) == pytest.approx(56.0, abs=0.5)


def test_hanger_load():
    """A19.6.2.1(9): plate reactions hung from the ledges (hand check: q = 1.35·(4.10 + 1.75) +
    1.5·15 = 30.40 kN/m2; Lp = 6.5 - 2·0.323 = 5.854 m inner bays, 6.5 - 0.39 - 0.323 = 5.787 m
    end bays)."""
    fac = (1.35, 1.35, 1.5, 1.5, 0.0, 0.0)
    assert V.plate_spans(1) == pytest.approx([5.787])
    assert V.plate_spans(2) == pytest.approx([5.787, 5.854])
    assert V.plate_spans(4) == pytest.approx([5.854, 5.854])
    assert V.hanger_load(4, fac) == pytest.approx(30.3975 * 5.854, rel=1e-4)       # 177.9 kN/m
    assert V.hanger_load(1, fac) == pytest.approx(30.3975 * 5.787 / 2, rel=1e-4)   # 88.0 kN/m
    members, _ = V.build_members()
    m2 = next(m for m in members if m.key == "VT2")
    assert V.hanger_asw(m2, fac, 0.68) * 10 == pytest.approx(4.07, abs=0.01)       # cm2/m at fyd
    assert V.hanger_asw(m2, fac, 3.65) == 0.0                                       # beyond the plates
    edge = next(m for m in members if m.key == "VBM")
    assert V.hanger_asw(edge, fac, 3.0) == 0.0


# --------------------------------------------------------------------------------------------
# full run (SAP forces)
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def res():
    return V.run(verbose=False)


def test_output_contract(res):
    assert set(res) == {"meta", "tables", "cype_comparison", "summary", "proposal"}
    json.dumps(res)                                                   # JSON-serialisable
    for name in ("bending", "shear_torsion", "detailing", "sls", "deflection"):
        for row in res["tables"][name][:50]:
            for k in ("check", "clause", "demand", "capacity", "eta", "ok", "combo"):
                assert k in row
    for row in res["cype_comparison"]:
        for k in ("quantity", "ours", "cype", "diff_pct", "src"):
            assert k in row
    assert res["meta"]["final_case"] == "CE-ROM"
    assert res["meta"]["runtime_s"] < 180


def test_research_values(res):
    cmp = {x["quantity"]: x for x in res["cype_comparison"]}
    assert cmp["inner beams M_qp,max sag (psi2 0.3, SAP) [kN·m]"]["ours"] == pytest.approx(90.41, abs=0.02)
    assert cmp["inner beams M_qp,max sag (psi2 0.8, SAP) [kN·m]"]["ours"] == pytest.approx(151.90, abs=0.02)
    thr = {(x["member"], x["face"]): x for x in res["tables"]["psi2_threshold"]}
    assert thr[("VT2", "bottom")]["psi2_crack_fctm"] == pytest.approx(0.583, abs=0.003)     # P.06
    assert thr[("VT2", "bottom")]["psi2_crack_fctm_fl"] == pytest.approx(0.63, abs=0.006)
    assert thr[("VT2", "bottom")]["psi2_wk_fail"] == pytest.approx(0.583, abs=0.003)


def test_node_moment_nec_all_porticos(res):
    rows = [x for x in res["cype_comparison"] if "from the drawing node moment" in x["quantity"]]
    assert len(rows) == 7
    for x in rows:
        assert abs(x["diff_pct"]) <= 0.3, x


def test_listing_section_model(res):
    """'Área Nec.' from CYPE's own zone moments: median |diff| small (the rest is CYPE's shift / node rules)."""
    import statistics
    d = [abs(x["diff_cypeM_pct"]) for x in res["tables"]["cype_listing_nec"] if x.get("diff_cypeM_pct") is not None]
    assert len(d) > 80 and statistics.median(d) < 3.0


def test_cype_4_3_shear_utilisation(res):
    """Span tramos: Q eta with the SAP forces within 2.5 % of CYPE (theta 45, 3 legs Ø10/100)."""
    q = [x for x in res["tables"]["cype_utilisation_4_3"] if x["quantity"].endswith("Q eta [%]")
         and x["quantity"].split()[1] in ("P1-P2", "P3-P4", "P5-P6", "P7-P8", "P13-P14", "P15-P17", "P16-P18")]
    assert len(q) == 7
    for x in q:
        assert abs(x["diff_pct"]) < 2.5, x


def test_parity_case_verdicts(res):
    """Anejo 10 assumptions (Mode.CYPE, psi2 0.3, theta 45): transverse beams pass, uncracked."""
    for k in ("VT1", "VT2", "VT3", "VT4", "VT5", "VT6", "VT7"):
        s = res["summary"][k]["cases"]["CYPE"]
        assert s["verdict"] == "CUMPLE", (k, s)
        assert s["fisuración ELS"]["eta"] == 0.0


def test_final_verdict(res):
    summ = res["summary"]
    for k in ("VT2", "VT3", "VT4", "VT5", "VT6"):          # inner frames crack at psi2 0.8
        assert summ[k]["verdict"] == "NO CUMPLE"
        assert summ[k]["governing"]["fisuración ELS"]["eta"] > 1.5
        others = [v["eta"] for f, v in summ[k]["governing"].items() if f != "fisuración ELS"]
        assert max(others) <= 1.0
    for k in ("VT1", "VT7"):
        assert summ[k]["verdict"] == "CUMPLE"
    for k in ("VBM", "VBT"):
        assert summ[k]["governing"]["fisuración ELS"]["eta"] > 1.0


def test_hanger_rows(res):
    """Links: V at d + suspension (CE cases in the verdict; CYPE case information).  VT2 sea face,
    CE-ROM: 12.82 (V = 443.2 kN, cot 2) + 4.07 = 16.89 cm2/m of 23.56 -> 0.717 (hand check)."""
    st = res["tables"]["shear_torsion"]
    rows = [x for x in st if x["check"].startswith("estribos V + suspensión")]
    assert rows and all(x["in_verdict"] == (x["case"] != "CYPE") for x in rows)
    x = next(x for x in rows if x["case"] == "CE-ROM" and x["member"] == "VT2" and x["pos_m"] == pytest.approx(0.68))
    assert x["Asw_hanger_cm2_m"] == pytest.approx(4.07, abs=0.01)
    assert x["eta"] == pytest.approx(0.717, abs=0.002)
    assert not any(x["member"].startswith("VB") for x in rows)
    for k in ("VT2", "VT3", "VT4", "VT5", "VT6", "VT1", "VT7"):
        assert res["summary"][k]["governing"]["cortante"]["eta"] < 1.0


def test_proposal(res):
    p = res["proposal"]
    inner = p["inner (ejes 2-6, pórticos 4-8)"]
    assert inner["bottom"]["change"] and inner["bottom"]["proposed_As_cm2"] > 21.99
    assert inner["bottom"]["wk_mm"] <= 0.1
    assert inner["psi2_threshold_provided"] == pytest.approx(0.583, abs=0.003)
    for g in p.values():
        for comp in ("bottom", "top", "stirrups"):
            assert g[comp].get("feasible", True)
        for m, v in g.get("verification", {}).items():
            assert v["verdict"] == "CUMPLE", (m, v)
    sens = p["end (ejes 1 y 7, pórticos 3 y 9) + torsión del ala (sensibilidad)"]
    assert max(sens["ledge_sensitivity_max_eta"].values()) <= 1.0


def test_sls_sanity(res):
    sls = [x for x in res["tables"]["sls"] if x["case"] == "CE-ROM" and x["check"] == "wk <= 0.1 mm (XS3, QP)"]
    for x in sls:
        if x["cracked"]:
            assert x["demand"] > 0 and x["sigma_s"] > 0
        else:
            assert x["demand"] == 0.0
    defl = [x for x in res["tables"]["deflection"] if x["check"].startswith("f total")]
    assert all(x["eta"] < 0.5 for x in defl)
