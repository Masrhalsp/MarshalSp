"""Seismic variant of the SAP2000 routes (``write_s2k.py --sismo``, ``sap_oapi_run.py --sismo``):
the static files stay byte-identical, the seismic file only adds records, check_s2k validates the
new tables, and the OAPI definition goes through the strict mock.

    python3 -m pytest sap2000/tests -q
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (ROOT / "tests", ROOT / "tools", ROOT / "model"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import mock_sap  # noqa: E402
import sap_oapi_run as sor  # noqa: E402
import sismo_sap as sis  # noqa: E402
import trasmallo as tm  # noqa: E402
import write_s2k as W  # noqa: E402

OUT = ROOT / "output"
CHECK = ROOT / "tools" / "check_s2k.py"
NEW_TABLES = ["MASS SOURCE", "FUNCTION - RESPONSE SPECTRUM - USER", "CASE - MODAL 1 - GENERAL",
              "CASE - RESPONSE SPECTRUM 1 - GENERAL", "CASE - RESPONSE SPECTRUM 2 - LOAD ASSIGNMENTS"]


@pytest.fixture(scope="module")
def model():
    return tm.build_model()


def _text(model, version: str, seismic: bool, name: str) -> bytes:
    old = W.SAP_VERSION
    W.SAP_VERSION = version
    try:
        s = W.build_tables(model, seismic=seismic)
    finally:
        W.SAP_VERSION = old
    if seismic:
        s.lines[0] = s.lines[0].replace("Muelle_Trasmallo_40m.$2k", name)
    return s.text().encode("ascii")


def tables(raw: bytes) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur = None
    for line in raw.decode("ascii").split("\r\n"):
        m = re.match(r'^TABLE:\s+"(.+)"$', line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur and line.strip() and line != "END TABLE DATA":
            out[cur].append(line)
    return out


@pytest.mark.parametrize("version,static,seismic", [
    ("27.1.0", "Muelle_Trasmallo_40m.$2k", "Muelle_Trasmallo_40m_sismo.$2k"),
    ("20.1.0", "Muelle_Trasmallo_40m_v20.$2k", "Muelle_Trasmallo_40m_v20_sismo.$2k")])
def test_files_on_disk_and_static_unchanged(model, version, static, seismic):
    assert _text(model, version, False, static) == (OUT / static).read_bytes()
    assert _text(model, version, True, seismic) == (OUT / seismic).read_bytes()
    a, b = tables((OUT / static).read_bytes()), tables((OUT / seismic).read_bytes())
    assert [t for t in b if t not in a] == NEW_TABLES
    for t, recs in a.items():                       # every static record kept, in place
        assert b[t][:len(recs)] == recs, t
        if t not in ("LOAD CASE DEFINITIONS", "COMBINATION DEFINITIONS"):
            assert b[t] == recs, t


def test_seismic_records(model):
    t = tables((OUT / "Muelle_Trasmallo_40m_sismo.$2k").read_bytes())
    assert t["MASS SOURCE"] == [
        "   MassSource=MSSSRC1   Elements=No   Masses=No   Loads=Yes   IsDefault=Yes   LoadPat=PP   Multiplier=1",
        "   MassSource=MSSSRC1   LoadPat=CM   Multiplier=1",
        "   MassSource=MSSSRC1   LoadPat=Qa   Multiplier=0.8"]
    assert t["CASE - MODAL 1 - GENERAL"] == ["   Case=MODAL   ModeType=Eigen   MaxNumModes=30   MinNumModes=1   "
                                             "EigenShift=0   EigenCutoff=0   EigenTol=1E-09   AutoShift=Yes"]
    assert t["CASE - RESPONSE SPECTRUM 2 - LOAD ASSIGNMENTS"][2] == (
        "   Case=EQZ   LoadName=U3   CoordSys=GLOBAL   Function=FUNC_V   Angle=0   TransAccSF=9.80665")
    assert all("ModalCombo=SRSS" in r and "ConstDamp=0.05" in r for r in t["CASE - RESPONSE SPECTRUM 1 - GENERAL"])
    fh = [r for r in t["FUNCTION - RESPONSE SPECTRUM - USER"] if "Name=FUNC_H " in r]
    assert fh[0].endswith("FuncDamp=0.05") and sum("FuncDamp" in r for r in fh) == 1
    assert "Period=0.22   Accel=0.608812" in " ".join(fh) and "Period=0.88   Accel=0.608812" in " ".join(fh)
    v27 = [r for r in t["COMBINATION DEFINITIONS"] if "ComboName=SISXQ " in r]
    assert len(v27) == 6 and not any("CaseType" in r for r in v27)
    v20 = [r for r in tables((OUT / "Muelle_Trasmallo_40m_v20_sismo.$2k").read_bytes())["COMBINATION DEFINITIONS"]
           if "ComboName=SISXQ " in r]
    assert sum('CaseType="Response Spectrum"' in r for r in v20) == 3


def test_mass_source_no_double_count(model):
    ms = sis.mass_source(model)
    assert not tm.SEISMIC["mass_source"]["self_mass"] and not ms["elements"]     # PP carries the self weight
    assert ms["patterns"] == [("PP", 1.0), ("CM", 1.0), ("Qa", 0.8)]
    assert sis.seismic_mass_kN(tm.load_totals(model), model) == pytest.approx(3720.16, abs=0.05)


def test_check_s2k_seismic(tmp_path):
    res = subprocess.run([sys.executable, str(CHECK), str(OUT / "Muelle_Trasmallo_40m_sismo.$2k")],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout
    assert "weight 3720.2 kN = mass 379.4 t" in res.stdout and "MODAL (Eigen, 30 modes)" in res.stdout
    text = (OUT / "Muelle_Trasmallo_40m_sismo.$2k").read_bytes().decode("ascii")
    bad = (text.replace("Elements=No   Masses=No", "Elements=Yes   Masses=Yes")
               .replace("Function=FUNC_V", "Function=FUNC_Q")
               .replace("Case=EQY   Type=LinRespSpec   ModalCase=MODAL", "Case=EQY   Type=LinRespSpec   ModalCase=PP"))
    p = tmp_path / "bad.$2k"
    p.write_bytes(bad.encode("ascii"))
    res = subprocess.run([sys.executable, str(CHECK), str(p)], capture_output=True, text=True)
    assert res.returncode == 1
    for msg in ("self mass counted twice", "undefined function FUNC_Q", "RS case EQY: ModalCase PP is not modal"):
        assert msg in res.stdout, res.stdout


def test_oapi_define_seismic_on_mock(model):
    m = mock_sap.SapModel()
    sor.define_model(m, model, seismic=True)
    st = m._st
    assert st.cases["MODAL"]["max_modes"] == 30
    assert {c: st.cases[c]["loads"][0][:3] for c in ("EQX", "EQY", "EQZ")} == {
        "EQX": ("U1", "FUNC_H", sis.G), "EQY": ("U2", "FUNC_H", sis.G), "EQZ": ("U3", "FUNC_V", sis.G)}
    assert st.mass_sources["MSSSRC1"]["patterns"] == [("PP", 1.0), ("CM", 1.0), ("Qa", 0.8)]
    assert st.rs_funcs["FUNC_V"]["Sa"][0] == pytest.approx(0.7 * 0.243525, abs=1e-6)
    assert [x[1:] for x in st.combos["SISYQ"]["items"]] == [("PP", 1.0), ("CM", 1.0), ("Qa", 0.8), ("EQX", 0.3),
                                                           ("EQY", 1.0), ("EQZ", 0.3)]
    assert st.combos[sis.ENVELOPE]["type"] == 1
    # static part identical to the default route
    m0 = mock_sap.SapModel()
    sor.define_model(m0, model)
    assert {k: v for k, v in st.combos.items() if k in m0._st.combos} == m0._st.combos
    assert set(st.cases) - set(m0._st.cases) == {"MODAL", "EQX", "EQY", "EQZ"}
    with pytest.raises(TypeError):                   # strict signatures
        m.LoadCases.ResponseSpectrum.SetLoads("EQX", 1, ["U1"], ["FUNC_H"], [9.8], ["Global"])
