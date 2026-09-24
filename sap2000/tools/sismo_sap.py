"""Seismic (response-spectrum) definition of the Muelle de Trasmallo model, shared by the two
SAP2000 routes (``write_s2k.py --sismo`` and ``sap_oapi_run.py --sismo``) and by the design files
(``diseno/sap``).  All data come from ``model/trasmallo.py`` (``build_model()['seismic']``:
Rover CP2406 §3.4.1.5, §5.1.2.6, §5.1.3.4); this module only maps them to SAP2000 objects:

* mass source ``MSSSRC1`` (the default one, redefined): PP 1.0 + CM 1.0 + Qa 0.8 from the
  load patterns.  Element self mass is NOT switched on although ``SEISMIC['mass_source']``
  asks for "self mass": the PP pattern already carries the frame self weight (SelfWtMult = 1)
  and the CSI Analysis Reference Manual (Mass Source, p. 335) warns "Be careful not to
  double-count the self-mass by specifying both Element Self mass and a load pattern that
  contains self-weight".  PP (self weight + 4.10 kN/m2 plates) + CM + 0.8 Qa = 3720 kN = 379 t
  is exactly the intended mass G + psi2 Qa.
* modal case ``MODAL``: eigenvectors, 30 modes.
* user response-spectrum functions ``FUNC_H`` / ``FUNC_V`` (Sa/g vs T, NCSE-02 elastic shape,
  5 % damping); the RS cases scale them by g = 9.80665 m/s2 (model units kN, m).
* RS cases ``EQX`` (U1, FUNC_H), ``EQY`` (U2, FUNC_H), ``EQZ`` (U3, FUNC_V): one direction per
  case, SRSS modal combination, constant damping 0.05.
* combinations ``SIS{X,Y,Z}[Q]`` = PP + CM [+ 0.8 Qa] + 1.0/0.3/0.3 x (EQX, EQY, EQZ), Linear
  Add, and their envelope ``ENV_SIS``.  RS results are positive envelopes; in a Linear Add combo
  SAP2000 takes each RS case with both signs: combo max = static + sum(sf x RS), combo min =
  static - sum(sf x RS) (CSI Analysis Reference Manual, Load Combinations, "Response-spectrum
  cases provide two values: the maximum value used is the positive computed value, and the
  minimum value is just the negative of the maximum"; example GRAVEQ "automatically accounts
  for the positive and negative senses of the earthquake load").  With all three RS terms of
  the same sign this is the envelope of every sign permutation of the 1.0/0.3/0.3 rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "model") not in sys.path:
    sys.path.insert(0, str(ROOT / "model"))

import trasmallo as tm  # noqa: E402

G = 9.80665                  # m/s2: RS functions are in Sa/g, model length unit m
MODAL_CASE = "MODAL"
MASS_SOURCE = "MSSSRC1"      # the default mass source of every SAP2000 model
FUNC = {"H": "FUNC_H", "V": "FUNC_V"}
ENVELOPE = "ENV_SIS"
MODAL_COMB = "SRSS"          # Rover: SRSS per direction
DIRECTIONS = ("U1", "U2", "U3", "R1", "R2", "R3")


def data(model: dict) -> dict:
    return model["seismic"]


def mass_source(model: dict) -> dict:
    """{name, elements, masses, loads, patterns [(pattern, factor)]} - see module docstring."""
    ms = data(model)["mass_source"]
    pats = [(p, float(f)) for p, f in ms["patterns"].items() if f]
    selfwt = {n: float(sw) for n, _, sw, _ in tm.LOAD_PATTERNS}
    carries_self_weight = any(selfwt.get(p, 0.0) for p, _ in pats)
    elements = bool(ms["self_mass"]) and not carries_self_weight
    return {"name": MASS_SOURCE, "elements": elements, "masses": elements, "loads": bool(pats),
            "patterns": pats}


def functions(model: dict) -> dict[str, list[tuple[float, float]]]:
    """{function name: [(T, Sa/g), ...]}"""
    return {FUNC[k]: list(v) for k, v in data(model)["spectra"].items()}


def rs_cases(model: dict) -> list[dict]:
    """[{case, dir, func, sf, damping, modal_comb}] in the order of SEISMIC_CASES."""
    s = data(model)
    return [{"case": c, "dir": d, "func": FUNC[spec], "sf": G, "damping": float(s["damping"]),
             "modal_comb": s["modal_combination"]} for c, d, spec in s["cases"]]


def n_modes(model: dict) -> int:
    return int(data(model)["n_modes"])


def combos(model: dict) -> list[dict]:
    """[{name, items [(kind 'static'|'rs', case, sf)], notes}] (Linear Add), in SEISMIC order."""
    out = []
    for name, c in data(model)["combos"].items():
        items = [("static", p, float(f)) for p, f in c["static"].items() if f]
        items += [("rs", k, float(f)) for k, f in c["rs"].items() if f]
        q = c["static"].get("Qa", 0.0)
        lead = name[3]
        notes = (f"Sismo {lead} (Rover 1.0/0.3/0.3): PP + CM" + (f" + {q:g} Qa" if q else "")
                 + f" + EQ{lead} 1.0 + resto 0.3; RS con signo +/- automatico")
        out.append({"name": name, "items": items, "notes": notes})
    return out


def combo_names(model: dict) -> list[str]:
    return [c["name"] for c in combos(model)]


def seismic_mass_kN(totals: dict[str, float], model: dict) -> float:
    """Seismic weight (kN) from :func:`trasmallo.load_totals` (PP includes the self weight)."""
    ms = mass_source(model)
    return sum(f * totals[p] for p, f in ms["patterns"])
