"""Tests of diseno/python/codigo/pilotes.py (+ armado_pilote.py): CYPE parity (Mode.CYPE, basis CYPE) with
the tolerances of diseno/python/investigacion/validate_codigo.py and sanity checks of the code-strict
rules, the SLS section solver and the output contract.

Run:  python3 -m pytest diseno/python/tests/test_pilotes.py -q
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "codigo"))
sys.path.insert(0, str(HERE.parent))

import pilotes as P  # noqa: E402
from armado_pilote import PROVIDED, PileLayout, practical_layouts  # noqa: E402
from seccion import HA50, Mode, cracked_stresses  # noqa: E402

FUSTE, ARRANQUE = PROVIDED["fuste"], PROVIDED["arranque"]


def close(ours: float, cype: str, tol: float = 0.005) -> bool:
    """validate_codigo.py rule: within max(0.5 %, half a unit of the last printed digit)."""
    return P._tol_ok(ours, cype, tol)


@pytest.fixture(scope="module")
def forces():
    return P.load_forces()


@pytest.fixture(scope="module")
def res_cype(forces):
    return P.check_piles(forces, "CYPE", Mode.CYPE)


@pytest.fixture(scope="module")
def res_final(forces):
    return P.check_piles(forces, "ROM", Mode.CODIGO)


# ------------------------------------------------------------------------------------------------
# reinforcement definition
# ------------------------------------------------------------------------------------------------
def test_provided_layouts_match_cype_bar_tables():
    assert FUSTE.coords()[0] == (-127.5, 127.5) and FUSTE.coords()[6] == (127.5, -127.5)      # P257 bars 1, 7
    assert FUSTE.coords()[1] == (-42.5, 127.5)
    assert ARRANQUE.c == pytest.approx(129.5) and ARRANQUE.coords()[1][0] == pytest.approx(-43.1667, abs=1e-3)
    assert FUSTE.As / 100 == pytest.approx(58.91, abs=0.01)
    assert FUSTE.clear_spacing == pytest.approx(60.0)
    Asl, d = FUSTE.shear_group()
    assert Asl / 100 == pytest.approx(39.27, abs=0.01) and d == pytest.approx(263.75)
    assert FUSTE.i_s() == pytest.approx(106.96, abs=0.01)
    assert ARRANQUE.b / 2 + ARRANQUE.i_s() == pytest.approx(308.6, abs=0.05)                 # spec S.29
    # tie weight ~ CYPE measurement 1309 kg Ø10 for 14 piles x 6.70 m
    assert FUSTE.weight_per_m()["ties"] * 6.70 * 14 == pytest.approx(1309.0, rel=0.02)


def test_practical_layouts_respect_spacing():
    for cand in practical_layouts():
        lay = cand["fuste"]
        assert lay.clear_spacing >= max(lay.phi, 25.0)
        assert lay.ties.phi >= max(6.0, lay.phi / 4)
        assert lay.ties.spacing <= 0.6 * min(15 * lay.phi, 300.0, 400.0) + 1e-9


# ------------------------------------------------------------------------------------------------
# exact solver = seccion.RCSection.capacity_ray / capacity_constant_N
# ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("S", [(620.06, 353.51, -68.95), (655.55, -352.07, 71.29), (-136.2, -269.6, -12.1)])
def test_exact_solver_equals_seccion(S):
    m = P.section_model(FUSTE, Mode.CYPE)
    SI = P._SI(S)
    r = m.exact.ray(SI)
    r0 = m.sec.capacity_ray(SI)
    assert r["eta"] == pytest.approx(r0["eta"], rel=1e-9)
    assert r["N"] == pytest.approx(r0["N"], rel=1e-9)
    e, _ = m.exact.constant_N(SI, r)
    e0, _ = m.sec.capacity_constant_N(SI)
    assert e == pytest.approx(e0, rel=1e-7)
    assert m.eta_fast(SI)[0] == pytest.approx(r["eta"], rel=2e-3)


# ------------------------------------------------------------------------------------------------
# parity with every value CYPE printed for P3 (Mode.CYPE, CYPE's own design forces)
# ------------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def p3_rows():
    return P.parity_p3_printed()


def test_p3_all_printed_values_within_tolerance(p3_rows):
    bad = [(r["quantity"], r["ours"], r["cype"]) for r in p3_rows if not r["ok"]]
    assert not bad, bad
    assert len(p3_rows) >= 100


def _row(rows, text):
    return next(r for r in rows if r["quantity"].startswith(text))


@pytest.mark.parametrize("quantity,cype", [
    ("P3 Cabeza (CYPE forces) η1 section resistance", "0.670"),
    ("P3 Cabeza (CYPE forces) η2 instability", "0.913"),
    ("P3 Cabeza (CYPE forces) lambda (eje x)", "58.02"),
    ("P3 Cabeza (CYPE forces) lambda_inf_lim (eje x)", "42.58"),
    ("P3 Cabeza (CYPE forces) e_i (eje x)", "12.94"),
    ("P3 Cabeza (CYPE forces) e2 (eje x)", "92.12"),
    ("P3 Cabeza (CYPE forces) MSd,x", "353.51"),
    ("P3 Cabeza (CYPE forces) MSd,y", "-68.95"),
    ("P3 Cabeza (CYPE forces) 2nd order NRd", "679.16"),
    ("P3 Cabeza (CYPE forces) 2nd order MRd,x", "387.20"),
    ("P3 Cabeza (CYPE forces) 2nd order MRd,y", "-75.52"),
    ("P3 Cabeza (CYPE forces) 1st order NRd", "925.83"),
    ("P3 Cabeza (CYPE forces) VRd,c (CYPE label VRd,s)", "142.85"),
    ("P3 Cabeza (CYPE forces) η VRd,c", "0.552"),
    ("P3 Cabeza (CYPE forces) VRd,max (z CYPE 249.16)", "996.63"),
    ("P3 Arranque (CYPE forces) η1 section resistance", "0.642"),
    ("P3 Arranque (CYPE forces) η2 instability", "0.894"),
    ("P3 Arranque (CYPE forces) lambda_inf_lim (eje x)", "41.42"),
    ("P3 Arranque (CYPE forces) e2 (eje x)", "91.56"),
    ("P3 Arranque (CYPE forces) MSd,x", "-352.07"),
    ("P3 Arranque (CYPE forces) MSd,y", "71.29"),
    ("P3 Arranque (CYPE forces) 2nd order NRd", "733.05"),
    ("P3 Arranque (CYPE forces) 2nd order MRd,x", "-393.69"),
    ("P3 Arranque (CYPE forces) 2nd order MRd,y", "79.72"),
    ("P3 Arranque (CYPE forces) VRd,max (z CYPE 251.34)", "1005.35"),
    ("P3 As,min = 0.004·Ac (AN)", "6.40"),
    ("P3 As,max = fcd·Ac/fyd (AN)", "122.67"),
    ("P3 A's,min = 0.10·NEd/fyd", "1.55"),
    ("P3 scl,max", "300"),
])
def test_p3_pinned_values(p3_rows, quantity, cype):
    r = _row(p3_rows, quantity)
    assert close(r["ours"], cype), (quantity, r["ours"], cype)


def test_p3_listing_aprov_constant_N(p3_rows):
    # spec C4 / U.34-U.35: the constant-N definition reproduces 90.7 exactly, 92.5 within 0.2 points
    assert _row(p3_rows, "P3 Arranque (CYPE forces) listing")["ours"] == pytest.approx(90.70, abs=0.05)
    assert _row(p3_rows, "P3 Cabeza (CYPE forces) listing")["ours"] == pytest.approx(92.30, abs=0.05)


# ------------------------------------------------------------------------------------------------
# CYPE listing 'Aprov.' for the 14 piles (Apéndice §4.2)
# ------------------------------------------------------------------------------------------------
def test_listing_all_piles(forces, res_cype):
    rows, stats = P.aprov_listing(forces, res_cype)
    assert len(rows) == 42
    for r in rows:
        # shear 'Aprov.' reproduced within 0.15 points with CYPE's listed forces (VRd,c / VRd,max)
        assert r["Q_cypeforces"] == pytest.approx(r["cype_Q"], abs=0.15), r
        # N,M: CYPE's summary = 1.008-1.018 x exact ray η (systematic, documented)
        assert 1.005 <= r["cype_NM"] / r["NM_ray_cypeforces"] <= 1.02, r
        # our SAP forces: -2.0...-0.5 % for 38 rows (listing factor 1.014 minus SAP/CYPE force
        # differences); up to +4.5 % at the heads of the end-axis piles P1/P16, where SAP gives larger
        # minor-axis moments than CYPE
        assert abs(r["diff_NM_sap_pct"]) < 5.0, r
        if r["pile"] not in ("P1", "P16"):
            assert -2.5 < r["diff_NM_sap_pct"] < 0.0, r
        assert abs(r["diff_Q_sap_pct"]) < 1.5, r
    assert stats["sd"] < 0.003


def test_p3_sap_forces_parity(forces, res_cype):
    rows = P.parity_p3_sap(forces, res_cype)
    assert all(r["ok"] for r in rows), [r["quantity"] for r in rows if not r["ok"]]
    eta2_head = _row(rows, "P3 Cabeza (SAP forces, ELU08) η2")["ours"]
    eta2_fix = _row(rows, "P3 Arranque (SAP forces, ELU08) η2")["ours"]
    assert eta2_head == pytest.approx(0.913, rel=0.015)
    assert eta2_fix == pytest.approx(0.894, rel=0.015)
    assert _row(rows, "P3 Arranque (SAP forces, ELU08) NEd")["ours"] == pytest.approx(661.26, abs=0.05)


# ------------------------------------------------------------------------------------------------
# rules
# ------------------------------------------------------------------------------------------------
def test_codigo_rules_second_order():
    rules = P.RULES[Mode.CODIGO]
    dp = P.design_points(655.55, -283.56, 2.79, ARRANQUE, rules)
    assert len(dp["first"]) == 2 and len(dp["second"]) == 2               # emin / ei per direction
    assert dp["sl"]["d"] == pytest.approx(308.63, abs=0.05)
    assert dp["e2_applied"] == pytest.approx(97.75, abs=0.02)             # spec S.29
    x_case = dp["second"][0]                                              # ei in the major axis
    assert abs(x_case[1]) == pytest.approx(655.55 * (432.56 + 12.94 + 97.75) / 1000, rel=1e-3)
    assert abs(x_case[2]) == pytest.approx(655.55 * (4.256 + 97.75) / 1000, rel=1e-3)
    y_case = dp["second"][1]
    assert abs(y_case[2]) == pytest.approx(655.55 * (4.256 + 12.94 + 97.75) / 1000, rel=1e-3)


def test_cype_rules_tension_and_low_compression():
    rules = P.RULES[Mode.CYPE]
    dp = P.design_points(-136.2, -269.6, -12.1, FUSTE, rules)
    assert dp["tension"] and dp["second"] == []
    dp = P.design_points(279.6, 258.9, -4.6, FUSTE, rules)                # P1 head G+1.5TB: λ < λlim
    assert not dp["sl"]["second_order"] and dp["second"] == []
    assert dp["sl"]["lam_lim"] > dp["sl"]["lam"]


def test_shear_formulas():
    vc = P.vrd_c(332.81, FUSTE)
    assert vc["V1"] == pytest.approx(142.85, abs=0.01) and vc["Vmin"] == pytest.approx(99.73, abs=0.01)
    assert P.vrd_c(-136.2, FUSTE)["V"] < vc["V"]                          # tension lowers VRd,c
    assert P.vrd_max(FUSTE, 0.9 * 263.75) == pytest.approx(949.5, abs=0.1)     # spec V.08
    v, cot = P.shear_best_with_ties(FUSTE, 0.9 * 263.75)
    assert cot == pytest.approx(2.0) and v == pytest.approx(P.vrd_s(FUSTE, 0.9 * 263.75, 2.0))


# ------------------------------------------------------------------------------------------------
# SLS section solver
# ------------------------------------------------------------------------------------------------
def test_elastic_uncracked_matches_closed_form():
    es = P.elastic(FUSTE)
    ae = FUSTE.steel.Es / FUSTE.concrete.Ecm
    A = 400.0 ** 2 + (ae - 1) * FUSTE.As
    I = 400.0 ** 4 / 12 + (ae - 1) * sum(FUSTE.bars()[0].area * y * y for _, y in FUSTE.coords())
    st = es.solve(500.0, 50.0, 20.0, cracked=False)
    corner = 500e3 / A - 50e6 * 200 / I - 20e6 * 200 / I
    assert -st["sig_ct"] == pytest.approx(corner, rel=2e-3)
    assert st["residual"] < 1e-6


def test_elastic_cracked_matches_seccion_uniaxial():
    es = P.elastic(FUSTE)
    st = es.solve(0.0, 150.0, 0.0, cracked=True)
    assert st["residual"] < 1e-6
    sec = FUSTE.section(Mode.CYPE)
    ref = cracked_stresses(sec, FUSTE.steel.Es / HA50.Ecm, 150e6)
    assert st["sig_c_max"] == pytest.approx(ref["sig_c"], rel=0.02)      # seccion counts A's with αe
    assert st["sig_s_t"] == pytest.approx(-min(ref["sig_s"]), rel=0.02)


def test_elastic_cracked_biaxial_independent():
    """P1 head, ELS04: fixed-point no-tension solution = direct least squares on a 1 mm mesh."""
    from scipy.optimize import least_squares
    es = P.elastic(FUSTE)
    N, Mx, My = 320.3, 181.2, 43.4
    st = es.solve(N, Mx, My, cracked=True)
    Ec, Es = FUSTE.concrete.Ecm, FUSTE.steel.Es
    xs = -200 + (np.arange(400) + 0.5)
    X, Y = np.meshgrid(xs, xs)
    fx, fy = X.ravel(), Y.ravel()
    xy = np.array(FUSTE.coords())
    ba = FUSTE.bars()[0].area
    F = np.array([N * 1e3, Mx * 1e6, My * 1e6])

    def res(p):
        e0, kx, ky = p[0] * 1e-3, p[1] * 1e-5, p[2] * 1e-5
        sc = Ec * np.maximum(e0 + kx * fx + ky * fy, 0)
        eb = e0 + kx * xy[:, 0] + ky * xy[:, 1]
        sb = (Es * eb - Ec * np.maximum(eb, 0)) * ba
        R = np.array([sc.sum() + sb.sum(), (sc * fy).sum() + (sb * xy[:, 1]).sum(),
                      (sc * fx).sum() + (sb * xy[:, 0]).sum()])
        return (R - F) / np.array([1e3, 1e6, 1e6])
    p0 = np.array(st["plane"]) * np.array([1e3, 1e5, 1e5]) * 0.7
    sol = least_squares(res, p0, xtol=1e-14, ftol=1e-14)
    e0, kx, ky = sol.x * np.array([1e-3, 1e-5, 1e-5])
    sig_c = max(Ec * (e0 + kx * x + ky * y) for x in (-200, 200) for y in (-200, 200))
    assert st["sig_c_max"] == pytest.approx(sig_c, rel=2e-3)
    assert st["sig_c_max"] == pytest.approx(33.27, abs=0.05)              # > 0.6·fck = 30 MPa


def test_sls_targets_spec(forces):
    """spec P.04 / P.05: gross corner σct 3.58 MPa (ψ2 0.8, TB 0; P2 head) and 11.01 MPa (TB 0.5, P1 head)."""
    es = P.elastic(FUSTE)
    pf2, pf1 = forces["P2"], forces["P1"]
    N, Mx, My = pf2.combine((1, 1, 0.8, 0, 0, 0))[pf2.station(6.70), :3]
    assert es.gross_sigma_ct(N, Mx, My) == pytest.approx(3.58, abs=0.01)
    N, Mx, My = pf1.combine((1, 1, 0.8, 0.5, 0, 0))[pf1.station(6.70), :3]
    assert es.gross_sigma_ct(N, Mx, My) == pytest.approx(11.01, abs=0.01)


def test_crack_width_uniaxial_consistency():
    es = P.elastic(FUSTE)
    st = es.solve(100.0, 120.0, 0.0, cracked=True)
    w = es.crack(st)
    assert w["rule"] == "(7.11)" and w["k2"] == 0.5
    assert w["As_eff"] == pytest.approx(4 * math.pi * 25 ** 2 / 4)       # face row only
    assert w["hc_ef"] == pytest.approx((400 - w["x"]) / 3, rel=1e-6)
    assert w["wk"] == pytest.approx(w["sr_max"] * w["d_eps"], rel=1e-9)


def test_crack_width_gross_ac_eff():
    """Ac,eff = b·hc,ef (gross, spec §5.5 / vigas.py), not b·hc,ef - As."""
    es = P.elastic(FUSTE)
    w = es.crack(es.solve(100.0, 120.0, 0.0, cracked=True))
    assert w["Ac_eff"] == pytest.approx(400.0 * w["hc_ef"], rel=0.03)      # 4 mm fibre grid
    assert w["rho_p_eff"] == pytest.approx(w["As_eff"] / w["Ac_eff"], rel=1e-9)


@pytest.mark.parametrize("pile,fac,wk", [
    ("P2", (1, 1, 0.3, 0.5, 0, 0), 0.1663),     # worst case of the ψ2,TB = 0.5 sensitivity
    ("P1", (1, 1, 0.8, 0.5, 0, 0), 0.1288),     # ROM ψ2,Qa = 0.8 with ψ2,TB = 0.5
])
def test_crack_width_hand_checks(forces, pile, fac, wk):
    """Independent review hand check (1 mm grid, own no-tension solver, gross Ac,eff)."""
    es = P.elastic(FUSTE)
    pf = forces[pile]
    N, Mx, My = pf.combine(fac)[pf.station(6.70), :3]
    w = es.crack(es.solve(N, Mx, My, cracked=True))
    assert w["wk"] == pytest.approx(wk, abs=0.002)


# ------------------------------------------------------------------------------------------------
# global results (sanity)
# ------------------------------------------------------------------------------------------------
def test_cype_variant_governing(res_cype):
    s = res_cype["summary"]
    assert max(v["nm2"] or 0 for v in s.values()) == pytest.approx(0.920, abs=0.01)      # P3, CYPE 0.913
    assert max(s, key=lambda p: s[p]["nm2"] or 0) == "P3"
    assert max(v["shear_vrdc"] for v in s.values()) == pytest.approx(0.837, abs=0.01)   # P2, CYPE 0.843
    for p, v in s.items():                                                              # intermediate stations never govern
        assert v["nm_stations"] <= max(v["nm1"] or 0, v["nm2"] or 0) + 1e-9, p


def test_final_design(res_final):
    s = res_final["summary"]
    assert all((v["nm2"] or 0) <= 1.0 and v["nm1"] <= 1.0 and v["shear"] <= 1.0 for v in s.values())
    assert s["P3"]["nm2"] == pytest.approx(0.987, abs=0.01)                 # ROM ψ0,Qa = 1: tight
    assert all(v["sls_crack_ok"] and not v["sls_crack_cracked"] for v in s.values())   # ψ2,TB = 0: uncracked
    assert max(v["sls_sigma_c"] for v in s.values()) > 1.0                  # σc ≤ 0.6 fck fails at P1 head
    assert s["P1"]["sls_sigma_c"] == pytest.approx(33.27 / 30.0, abs=0.003)
    # information: sustained share on Ec,eff = Ecm/(1 + 1.75·Mqp/Mk) -> 28.98 MPa at the P1 head (hand check)
    assert s["P1"]["sls_sigma_c_Ec_eff"] == pytest.approx(28.98 / 30.0, abs=0.004)
    assert max(v["sls_sigma_c_Ec_eff"] for v in s.values()) < 1.0
    assert {p for p, v in s.items() if v["verdict"] != "CUMPLE"} == {"P1", "P2", "P3", "P16"}


def test_run_contract_subset():
    res = P.run("ROM", Mode.CODIGO, parity=False, options=False, variants=True, piles=("P3", "P4"))
    assert set(res) == {"meta", "tables", "cype_comparison", "summary", "proposal"}
    assert set(res["summary"]) == {"P3", "P4"}
    for name, rows in res["tables"].items():
        for r in rows:
            assert all(not isinstance(v, (np.floating, np.integer, np.bool_)) for v in r.values()), name
    for r in res["tables"]["uls_nm"]:
        assert {"check", "clause", "combo", "eta", "ok"} <= set(r)
    for r in res["tables"]["shear"]:
        assert {"check", "clause", "demand", "capacity", "eta", "ok", "combo"} <= set(r)
    As = {(r["pile"], r["zone"]): r for r in res["tables"]["as_required"]}
    assert As[("P3", "fuste")]["As_req_cm2"] == pytest.approx(58.4, abs=1.0)
    assert As[("P4", "fuste")]["As_req_cm2"] < As[("P3", "fuste")]["As_req_cm2"]
