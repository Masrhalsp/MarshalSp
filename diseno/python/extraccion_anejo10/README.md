# Anejo 10 extraction: CYPE design reference

These scripts rebuild `diseno/ref/cype_design_reference.json` and `.md` from `report/A10_CALC_ESTRUCTURAS.docx`. The two reference files hold every CYPECAD design value of the Trasmallo module, each with its source paragraph or table. The rebuilt files are byte-identical to the committed ones.

```
python3 diseno/python/extraccion_anejo10/extraer.py                 # ~7 s: dumps -> JSON -> MD -> validation
python3 diseno/python/extraccion_anejo10/extraer.py --salida DIR    # write to DIR and compare with diseno/ref
python3 -m pytest diseno/python/tests/test_extraccion.py -q         # same pipeline in a temp dir (~7 s)
python3 diseno/python/extraccion_anejo10/datos_imagenes.py          # list of the values read by eye from figures
```

Requirement: `python-docx`. Only the standard library is needed apart from that. No LibreOffice is needed, because the WMF formulas are decoded in Python.

## Pipeline

| step | script | input | output |
| --- | --- | --- | --- |
| 1 | `volcado.py` | the .docx | text dumps in `trabajo/` (git-ignored, ~1.4 MB) |
| 1b | `wmftext.py` (called by `volcado.py`) | WMF equation images inside the .docx | formula text, e.g. `VRd,max=αcw·bw·z·ν1·fcd·...` |
| 2 | `construir.py` + `tablas.py` + `datos_imagenes.py` | `trasmallo_body/app/pre.txt` | `cype_design_reference.json` |
| 3 | `generar_md.py` | the JSON | `cype_design_reference.md` |
| 4 | `validar.py` | the JSON + the dumps | `trabajo/validacion.txt` (exit code 1 on failure) |

Dumps in `trabajo/`:

| file | content |
| --- | --- |
| `trasmallo_body.txt` | body P215–P609 |
| `trasmallo_app.txt` | Apéndice 1, P1449–P1835 |
| `trasmallo_pre.txt` | project text, P100–P214 |
| `a10_full.txt` | the whole document as python-docx `.text`. `investigacion/codigo_estructural_spec.md` and `sap/sap_design_spec.md` quote its line numbers. |
| `a10_independiente.txt` | the whole document through a second parser, used by validation step B |
| `trasmallo_body_formulas.txt`, `trasmallo_app_formulas.txt` | the same ranges with each WMF formula written as `«text»` |
| `formulas_unicas.txt` | the distinct formulas |

Paragraph numbers `P<n>` are indices in python-docx `Document.paragraphs`. `"P<n> table"` is the table that follows P<n> in document order.

## Validation

**A. Source check.** Every `{value, src}` object and every tabular row is searched for in its cited paragraph or table text:

- 3744 values are found.
- 1 documented exception: the composed `12Ø25`, which the document prints as `4Ø25` in three separate cells.
- 62 are skipped: 54 were read from figures and 8 have no printed counterpart.

**B. Independent re-parse.** The second dump is parsed by separate code and compared with the JSON:

| check | result |
| --- | --- |
| B1 values located by table symbol | 932 equal |
| B2 CYPE combination factors | 312 equal |
| B2 values of the beam listing | 1197 equal |
| B3 pile tables §3.2, §3.3, §3.5 and §4.2 | 224 rows equal |
| B4 value descriptions | 451 equal |

## Values read by eye from figures (`datos_imagenes.py`)

These values cannot be scripted. Each one keeps `src = "P<n> image imageNN.png"`, where `imageNN.png` is the file `word/media/imageNN.png` inside the .docx.

- **Piles:**
  - image16 (P220): section sketch.
  - image50 (P245) and image94 (P300): N–M interaction labels, 6 each.
  - image84 (P257), image88 (P265), image95 (P312) and image96 (P320): equilibrium diagrams. Each gives x, ε max, ε min and σ max.
  - image92 (P275): CEB ψ tables 5.9 and 5.10.
- **Beam P3–P4 (body):**
  - image97 (P336): bar drawing labels.
  - image112 (P381) and image113 (P389): equilibrium diagrams.
  - image117 (P569): quasi-permanent moments −8.47, 86.66 and −12.21 kN·m.
  - image118 (P571): crack hand check with 12 strains and stresses, including wk = 0.00.
  - image120 (P586): deflection history.
- **Apéndice 1 beam drawings, image203–image212 (P1607–P1660):** bar schedules, laps and envelope labels for each pórtico. Confidence is recorded per drawing:
  - high for Pórticos 3–9;
  - low for Pórtico 1;
  - medium for Pórtico 10.
- **Slab:**
  - image121 (P593): 1 m band envelope and bar labels.
  - image122 (P595): alveoplaca properties.
  - image123 (P600): negative-bar plan, cropped after PL3.
  - image124 (P603): negative bending table.

## Provenance

These scripts are cleaned copies of the session scripts that first produced the reference:

| session script | now |
| --- | --- |
| `full.py` | `volcado.volcado_rango` |
| a one-off dump | `volcado.volcado_a10_full` |
| `mydump.py` | `volcado.volcado_independiente` |
| `research/wmf/dumpform.py` and `wmftext.py` | `volcado.volcado_formulas` and `wmftext.py` |
| `lib.py` | `tablas.py` |
| `build.py` | `construir.py` |
| `md_gen.py` | `generar_md.py` |
| `validate.py`, `vcheck.py`, `zcheck.py`, `pcheck.py`, `desccheck.py` | `validar.py` |

The corrections that `apply_fixes.py` applied after the independent check, and the later manual edits of caveats C1 and C16, are now part of `construir.py` and `tablas.py`:

- the empty or "no text label" descriptions of values printed under an equation image;
- the verbatim P276 quote;
- the viga cantil arithmetic (C15);
- the image97 labels;
- the note on the section-2 position;
- caveats C1, C15 and C16.

`meta.generated` is fixed at `2026-09-23`, the date of the committed reference, so that the output stays byte-identical.
