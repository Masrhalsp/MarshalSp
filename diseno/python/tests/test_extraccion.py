"""Test of the reproducible Anejo 10 extraction (diseno/python/extraccion_anejo10/): runs the whole pipeline
(dumps -> JSON -> MD -> validation) into a temporary directory and checks that the regenerated
cype_design_reference.json / .md are byte-identical to the committed diseno/ref files, that the validation
passes and is not vacuous, and that the WMF formula recovery and the by-eye figure table work.

Run:  python3 -m pytest diseno/python/tests/test_extraccion.py -q      (~10 s; skipped without python-docx)
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

pytest.importorskip("docx")

EXT = Path(__file__).resolve().parents[1] / "extraccion_anejo10"
sys.path.insert(0, str(EXT))

import datos_imagenes  # noqa: E402
import extraer  # noqa: E402
import validar  # noqa: E402
import volcado  # noqa: E402

pytestmark = pytest.mark.skipif(not volcado.DOCX.exists(), reason="report/A10_CALC_ESTRUCTURAS.docx not present")


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("extraccion")
    r = extraer.ejecutar(salida=out / "ref", trabajo=out / "trabajo", formulas=True, log=lambda *a: None)
    return out, r


def test_json_md_byte_identical_to_committed(run):
    out, r = run
    for name in extraer.NOMBRES:
        assert (out / "ref" / name).read_bytes() == (extraer.REF / name).read_bytes(), name
    assert r["identical"] == {n: True for n in extraer.NOMBRES}
    assert r["ok"]


def test_validation_passes(run):
    _, r = run
    assert r["validation_ok"], "\n".join(r["report"])
    rep = "\n".join(r["report"])
    assert " 0 not found" in rep and "B4 descriptions" in rep


def test_dumps_written(run):
    out, _ = run
    w = out / "trabajo"
    names = set(volcado.RANGOS) | set(volcado.RANGOS_FORMULAS) | {"a10_full.txt", "a10_independiente.txt", "formulas_unicas.txt",
                                                                  "validacion.txt"}
    assert names <= {p.name for p in w.iterdir()}
    assert (w / "trasmallo_body.txt").read_text(encoding="utf-8").startswith("P215\tMUELLE DE TRASMALLO.")
    assert (w / "trasmallo_app.txt").read_text(encoding="utf-8").startswith("P1449\tLISTADOS DE CÁLCULO MUELLE DE TRASMALLO.")
    body = (w / "trasmallo_body.txt").read_text(encoding="utf-8")
    assert "VRd,max" in body and "η" in body and "{Dimensiones | : | 40x40 cm" in body   # Symbol glyphs + nested tables


def test_wmf_formula_recovery(run):
    out, _ = run
    f = (out / "trabajo" / "formulas_unicas.txt").read_text(encoding="utf-8")
    assert "VRd,max=αcw·bw·z·ν1·fcd" in f
    assert "A _s,min=0.004·A _c" in f


def test_validation_detects_a_wrong_value(run):
    """The validator must fail when a transcribed number is altered (guards against a vacuous check)."""
    out, _ = run
    import json
    d = json.loads((out / "ref" / "cype_design_reference.json").read_text(encoding="utf-8"))
    textos = {p.name: p.read_text(encoding="utf-8") for p in (out / "trabajo").iterdir() if p.suffix == ".txt"}
    bad = copy.deepcopy(d)
    bad["piles"]["section_1_forjado_cabeza"]["normal_forces"]["section_resistance_first_order"]["NEd"]["value"] = 621.06
    ok, lines = validar.validar(bad, textos)
    assert not ok and any("NEd" in ln and "621.06" in ln for ln in lines)
    bad = copy.deepcopy(d)
    bad["beams"]["listing_armado_vigas_2"]["porticos"]["Pórtico 4"]["tramos"]["P3-P4"]["zones"][0]["M_min"] = -266.0
    ok, _ = validar.validar(bad, textos)
    assert not ok


def test_by_eye_values_are_documented(run):
    import json
    out, _ = run
    rows = datos_imagenes.listar(json.loads((out / "ref" / "cype_design_reference.json").read_text(encoding="utf-8")))
    imgs = {s.split(" image ")[1].split(".")[0] for _, s, _ in rows}
    for n in (97, 112, 117, 118, 121, 123, *range(203, 212)):
        assert f"image{n}" in imgs, n
    assert any("image212" in s for _, s, _ in rows)
