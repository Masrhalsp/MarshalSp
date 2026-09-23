"""Reproducible extraction of the CYPE design reference from Anejo 10: one command.

    python3 diseno/python/extraccion_anejo10/extraer.py                  # dumps -> JSON/MD in diseno/ref -> validation (~7 s)
    python3 diseno/python/extraccion_anejo10/extraer.py --salida DIR     # write JSON/MD to DIR and compare with diseno/ref
    python3 diseno/python/extraccion_anejo10/extraer.py --sin-formulas   # skip the WMF formula dumps (faster)

Steps
    1. volcado.py       report/A10_CALC_ESTRUCTURAS.docx -> text dumps in the work directory
                        (default diseno/python/extraccion_anejo10/trabajo/, git-ignored, ~1.4 MB):
                          trasmallo_body.txt  P215-P609   Trasmallo results (body)       } input of step 2
                          trasmallo_app.txt   P1449-P1835 Apéndice 1 listings            }
                          trasmallo_pre.txt   P100-P214   project text (codes, materials) }
                          a10_full.txt                    whole document, python-docx .text (line numbers quoted
                                                          in investigacion/ and sap/sap_design_spec.md)
                          a10_independiente.txt           whole document, second parser (step 4 B)
                          trasmallo_body_formulas.txt / trasmallo_app_formulas.txt / formulas_unicas.txt
                                                          same ranges with the WMF equations as text (wmftext.py)
    2. construir.py     dumps -> cype_design_reference.json (+ datos_imagenes.py: values read by eye from figures)
    3. generar_md.py    JSON -> cype_design_reference.md
    4. validar.py       every value re-found in its cited source + independent re-parse; report in
                        <trabajo>/validacion.txt
    5. comparison       byte comparison with the committed diseno/ref files (when --salida is given) or
                        report whether diseno/ref changed.

Exit code 0 only if the validation passes (and, with --salida, the output equals diseno/ref).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import construir  # noqa: E402
import datos_imagenes  # noqa: E402
import generar_md  # noqa: E402
import validar  # noqa: E402
import volcado  # noqa: E402

REF = volcado.ROOT / "diseno" / "ref"
NOMBRES = ("cype_design_reference.json", "cype_design_reference.md")
TRABAJO = HERE / "trabajo"


def ejecutar(salida=REF, trabajo=TRABAJO, formulas=True, docx_path=volcado.DOCX, log=print):
    """Run the whole pipeline; returns {"ok", "validation_ok", "identical" ({name: bool} vs diseno/ref), "report"}."""
    t0 = time.time()
    salida, trabajo = Path(salida), Path(trabajo)
    trabajo.mkdir(parents=True, exist_ok=True)
    salida.mkdir(parents=True, exist_ok=True)

    doc = volcado.abrir(docx_path)
    textos = volcado.todos(doc, formulas=formulas)
    for name, txt in textos.items():
        (trabajo / name).write_text(txt, encoding="utf-8")
    log(f"[1] {len(textos)} dumps written to {trabajo}  ({time.time() - t0:.1f} s)")

    d = construir.construir(textos)
    md = generar_md.render(d)
    antes = {n: (REF / n).read_bytes() if (REF / n).exists() else None for n in NOMBRES}
    construir.escribir_json(d, salida / NOMBRES[0])
    (salida / NOMBRES[1]).write_text(md, encoding="utf-8")
    log(f"[2-3] {salida / NOMBRES[0]}\n      {salida / NOMBRES[1]}")
    log(f"      {len(datos_imagenes.listar(d))} entries read by eye from figures (python3 {HERE.name}/datos_imagenes.py lists them)")

    ok, lines = validar.validar(d, textos)
    (trabajo / "validacion.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("[4] validation " + ("PASSED" if ok else "FAILED"))
    for ln in lines:
        log("    " + ln)

    ident = {n: antes[n] == (salida / n).read_bytes() for n in NOMBRES}
    same_dir = salida.resolve() == REF.resolve()
    for n, same in ident.items():
        if same_dir:
            log(f"[5] diseno/ref/{n}: " + ("unchanged (byte-identical to the previous file)" if same else "CHANGED - review with git diff"))
        else:
            log(f"[5] {n}: " + ("byte-identical to diseno/ref" if same else "DIFFERS from diseno/ref"))
    log(f"done in {time.time() - t0:.1f} s")
    return {"ok": ok and (same_dir or all(ident.values())), "validation_ok": ok, "identical": ident, "report": lines}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--salida", default=str(REF), help="directory for the JSON / MD (default diseno/ref)")
    ap.add_argument("--trabajo", default=str(TRABAJO), help="directory for the text dumps (default: git-ignored trabajo/)")
    ap.add_argument("--sin-formulas", action="store_true", help="skip the WMF formula dumps")
    a = ap.parse_args(argv)
    r = ejecutar(a.salida, a.trabajo, formulas=not a.sin_formulas)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
