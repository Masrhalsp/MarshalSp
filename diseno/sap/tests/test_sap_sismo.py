"""Seismic variant of the design files and of the OAPI design script (``--sismo``): the static
design files stay byte-identical, the ``_sismo`` files add the RS analysis and flag SIS* as
design combinations, and the OAPI run designs with them on the mock.

    python3 -m pytest diseno/sap/tests -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for _p in (HERE, HERE.parent, ROOT / "sap2000" / "tools", ROOT / "sap2000" / "model"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos_diseno_sap as D  # noqa: E402
import mock_sap_diseno as MD  # noqa: E402
import sap_oapi_diseno as S  # noqa: E402
import write_s2k_diseno as WD  # noqa: E402

OUT = HERE.parent / "output"
CHECK_S2K = ROOT / "sap2000" / "tools" / "check_s2k.py"
SIS = ["SISXQ", "SISX", "SISYQ", "SISY", "SISZQ", "SISZ"]


@pytest.fixture(scope="module")
def files(tmp_path_factory):
    out = tmp_path_factory.mktemp("s2k_sismo")
    return WD.write_all(out), WD.write_all(out, seismic=True)


def test_static_files_unchanged_and_seismic_files_current(files):
    static, seismic = files
    for v, p in static.items():
        assert p.read_bytes() == (OUT / p.name).read_bytes(), p.name
    for v, p in seismic.items():
        assert p.name == f"{WD.file_stem(v, 'CYPE', True)}.$2k" and "_sismo" in p.name
        assert p.read_bytes() == (OUT / p.name).read_bytes(), p.name


def test_seismic_design_file_is_static_plus_additions(files):
    static, seismic = files
    _, a = WD.parse_lines(static["diseno"].read_bytes().decode("ascii").split("\r\n")[:-2])
    _, b = WD.parse_lines(seismic["diseno"].read_bytes().decode("ascii").split("\r\n")[:-2])
    a, b = dict((t, r) for t, r in a), dict((t, r) for t, r in b)
    assert sorted(set(b) - set(a)) == sorted(["MASS SOURCE", "FUNCTION - RESPONSE SPECTRUM - USER",
                                              "CASE - MODAL 1 - GENERAL", "CASE - RESPONSE SPECTRUM 1 - GENERAL",
                                              "CASE - RESPONSE SPECTRUM 2 - LOAD ASSIGNMENTS"])
    for t, recs in a.items():
        if t == WD.T_COMBO:          # SIS* / ENV_SIS sit before the ELR family appended by the design writer
            assert [r for r in b[t] if WD.get(r, "ComboName") not in SIS + ["ENV_SIS"]] == recs
            continue
        assert b[t][:len(recs)] == recs, t
        if t != "LOAD CASE DEFINITIONS":
            assert b[t] == recs, t
    first = {}
    for r in b[WD.T_COMBO]:
        first.setdefault(WD.get(r, "ComboName"), r)
    strength = [c for c, r in first.items() if WD.get(r, "ConcDesign") == "Strength"]
    assert strength == [f"ELU{k:02d}" for k in range(1, 23)] + SIS
    assert WD.get(first["ENV_SIS"], "ConcDesign") == "None"


@pytest.mark.parametrize("variant", ["diseno", "overwrites", "rect"])
def test_seismic_files_pass_check_s2k(files, variant):
    res = subprocess.run([sys.executable, str(CHECK_S2K), str(files[1][variant])], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "mass 379.4 t" in res.stdout and "6 combinations with RS cases" in res.stdout
    if variant != "rect":
        assert "28 Strength combos ELU01..SISZQ" in res.stdout


def test_design_combo_names():
    assert D.design_combo_names("CYPE") == [f"ELU{k:02d}" for k in range(1, 23)]
    assert D.design_combo_names("ROM", seismic=True)[-6:] == SIS
    assert D.SEISMIC_GAMMA["SAP (persistent, all combos)"] == {"gamma_c": 1.5, "gamma_s": 1.15}


def test_oapi_design_seismic_on_mock(tmp_path):
    m = MD.SapModel(MD.XlsxSynth())
    res = S.run(m, out_dir=tmp_path, save_path=tmp_path / "s.sdb", sismo=True)
    st = m._st
    assert st.design.strength == [f"ELU{k:02d}" for k in range(1, 23)] + SIS
    assert res["meta"]["design_combos"] == sorted(st.design.strength)
    assert st.run_flags["MODAL"] and st.cases["EQX"]["type"] == "RS"
    assert res["meta"]["sismo"] and res["meta"]["gamma_seismic_combos"] == D.SEISMIC_GAMMA
    assert res["analysis_identity"]["ok"]
    js = tmp_path / "diseno_SAP2000_sismo.json"
    assert js.exists() and (tmp_path / "diseno_SAP2000_sismo.xlsx").exists()
    assert not (tmp_path / "diseno_SAP2000.json").exists()
    assert set(json.loads(js.read_text(encoding="utf-8"))) == {"meta", "summary", "analysis_identity", "piles", "beams"}
