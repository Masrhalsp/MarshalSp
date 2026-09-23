"""Write the SAP2000 v27.1 text import files (.$2k) for the concrete frame design
("Eurocode 2-2004") of the Muelle de Trasmallo model.

    python3 diseno/sap/write_s2k_diseno.py [--base CYPE|ROM] [--kphi ce|cype|sap] [--areas-cero]
                                           [--decimal ,] [-o diseno/sap/output]

The model itself is produced by ``sap2000/tools/write_s2k.build_tables`` (so geometry, loads and
combinations are byte-identical to ``sap2000/output/Muelle_Trasmallo_40m.$2k``) from the design
model of ``datos_diseno_sap`` (beam sections = web rectangles + modifiers, analysis-identical),
and the design tables are then added or edited record by record.  Three files are written:

``Muelle_Trasmallo_40m_diseno.$2k``   (use this one)
    model + every design table whose title and fields were seen in real SAP2000 v21-v26 exports
    (spec VERIFIED): PROGRAM CONTROL ``ConcCode``, rebar material B500SD (01/02/03E), beam
    sections Rectangular + modifiers (01), ``02 - CONCRETE COLUMN`` (pile, check), ``03 - CONCRETE
    BEAM`` (beams), ``FRAME DESIGN PROCEDURES``, ``ConcDesign=Strength`` on ELU01-22 (or ELR01-22),
    ``AUTO COMBINATION OPTION DATA 01`` (auto combos off), the ROM combinations ELR01-22 and the
    selection groups DISENO_*, plus the one-record ``PREFERENCES - CONCRETE DESIGN - EUROCODE
    2-2004`` (fields of a real v20.1 export of the EC2-family table + [G7], VERIFIED-3P; a single
    record cannot reach the 20-error import abort).
``Muelle_Trasmallo_40m_diseno_overwrites.$2k``   (optional)
    the same + ``OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004`` (one record per designed frame,
    254 records, field names of real v20 rows [G7], not seen in a v24+ export).  v27 already
    rejected one v20 field once (``CaseType``) and aborted after 20 errors, so this table is kept
    out of the main file; the overwrites are applied by the OAPI script or in the GUI instead.
``Muelle_Trasmallo_40m_rect.$2k``   (analysis check)
    only the beam-section change (rectangle + modifiers), no design table: proves in SAP that the
    analysis is unchanged (compare with sap2000/resultados_sap) independently of any design table.

The files pass ``sap2000/tools/check_s2k.py``.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _p in (HERE, ROOT / "sap2000" / "tools", ROOT / "sap2000" / "model"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos_diseno_sap as D  # noqa: E402
import write_s2k as W  # noqa: E402

OUT_DIR = HERE / "output"
STEM = "Muelle_Trasmallo_40m"
VARIANTS = ("diseno", "overwrites", "rect")

T_PROGRAM = "PROGRAM CONTROL"
T_MAT1 = "MATERIAL PROPERTIES 01 - GENERAL"
T_MAT2 = "MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES"
T_MAT3B = "MATERIAL PROPERTIES 03B - CONCRETE DATA"
T_MAT3E = "MATERIAL PROPERTIES 03E - REBAR DATA"
T_FSEC1 = "FRAME SECTION PROPERTIES 01 - GENERAL"
T_FSEC2 = "FRAME SECTION PROPERTIES 02 - CONCRETE COLUMN"
T_FSEC3 = "FRAME SECTION PROPERTIES 03 - CONCRETE BEAM"
T_OFFSETS = "FRAME OFFSET ALONG LENGTH ASSIGNMENTS"
T_PROC = "FRAME DESIGN PROCEDURES"
T_COMBO = "COMBINATION DEFINITIONS"
T_AUTO = "AUTO COMBINATION OPTION DATA 01 - GENERAL"
T_PREF = "PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004"
T_OVER = "OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004"

Record = list          # [(field, token)] with token = the exact text after '=' (quotes kept)


# ============================================================================================
# token-level table editing (round-trip exact with write_s2k.S2K)
# ============================================================================================
_PAIR = re.compile(r'([A-Za-z0-9_]+)=("[^"]*"|\S+)')


def parse_lines(lines: list[str]) -> tuple[list[str], list[list]]:
    """``S2K.lines`` -> (header lines, [[title, [Record, ...]], ...]).  Wrapped records
    (`` _`` continuation) are joined; tokens keep their exact text."""
    header: list[str] = []
    tables: list[list] = []
    pending = ""
    for line in lines:
        m = re.match(r'^TABLE:\s+"(.+)"\s*$', line)
        if m:
            tables.append([m.group(1), []])
            continue
        if not tables:
            header.append(line)
            continue
        if not line.strip():
            continue
        if line.rstrip().endswith(" _"):
            pending += line.rstrip()[:-2] + " "
            continue
        tables[-1][1].append(_PAIR.findall(pending + line))
        pending = ""
    return header, tables


def render(header: list[str], tables: list[list]) -> W.S2K:
    """Inverse of :func:`parse_lines`, with the wrapping rule of ``write_s2k.S2K.record``."""
    s = W.S2K()
    s.lines = list(header)
    for title, records in tables:
        if not records:
            continue
        s.lines.append(f'TABLE:  "{title}"')
        for rec in records:
            line = "   "
            for k, tok in rec:
                pair = f"{k}={tok}"
                cand = pair if not line.strip() else "   " + pair
                if line.strip() and len(line) + len(cand) > W.LINE_LEN:
                    s.lines.append(line + " _")
                    line = "        " + pair
                else:
                    line += cand
            s.lines.append(line)
        s.lines.append(" ")
    return s


def rec(row: dict) -> Record:
    """dict of Python values -> Record, formatted by ``write_s2k.fmt`` (None values skipped)."""
    return [(k, W.fmt(v)) for k, v in row.items() if v is not None]


def get(record: Record, key: str) -> str | None:
    return next((t for k, t in record if k == key), None)


def put(record: Record, key: str, value, after: str | None = None) -> None:
    """Set ``key`` (formatted value) in place, or insert it after ``after`` / at the end."""
    tok = W.fmt(value)
    for i, (k, _) in enumerate(record):
        if k == key:
            record[i] = (k, tok)
            return
    idx = next((i + 1 for i, (k, _) in enumerate(record) if k == after), len(record))
    record.insert(idx, (key, tok))


def table(tables: list[list], title: str) -> list[Record]:
    for t, records in tables:
        if t == title:
            return records
    raise KeyError(title)


def insert_after(tables: list[list], anchor: str, title: str, records: list[Record]) -> None:
    idx = next(i for i, (t, _) in enumerate(tables) if t == anchor)
    tables.insert(idx + 1, [title, records])


# ============================================================================================
# design tables
# ============================================================================================
def combo_records(base: str, strength: bool) -> list[Record]:
    """Linear-add rows + envelope of one D.BASES family, formatted exactly like
    ``write_s2k.build_tables`` (v23+ layout: no CaseType)."""
    b = D.BASES[base]
    fam = b["family"]
    out: list[Record] = []

    def combo(name: str, ctype: str, items: list[tuple[str, float]], notes: str, conc: str) -> None:
        for k, (case, sf) in enumerate(items):
            row = {"ComboName": name}
            if k == 0:
                row.update({"ComboType": ctype, "AutoDesign": False})
            row.update({"CaseName": case, "ScaleFactor": float(sf)})
            if k == 0:
                row.update({"SteelDesign": "None", "ConcDesign": conc, "AlumDesign": "None",
                            "ColdDesign": "None", "Notes": notes})
            out.append(rec(row))

    names = []
    for name, fac in D.combos(base).items():
        combo(name, "Linear Add", [(p, sf) for p, sf in zip(W.tm.PATTERN_ORDER, fac) if sf],
              f"{b['title']} comb. {int(name[-2:])}", "Strength" if strength else "None")
        names.append(name)
    combo(f"ENV_{fam}", "Envelope", [(n, 1.0) for n in names], f"Envolvente {b['title']}", "None")
    return out


def rebar_material_records() -> tuple[Record, Record, Record]:
    r = D.REBAR
    m1 = rec({"Material": r.name, "Type": "Rebar", "SymType": "Uniaxial", "TempDepend": False,
              "Color": "White", "Notes": r.note})
    m2 = rec({"Material": r.name, "UnitWeight": r.unit_weight, "UnitMass": r.unit_mass, "E1": r.E, "A1": r.alpha})
    m3 = rec({"Material": r.name, "Fy": r.fy, "Fu": r.fu, "EffFy": r.expected * r.fy, "EffFu": r.expected * r.fu,
              "SSCurveOpt": "Simple", "SSHysType": "Kinematic", "SHard": r.strain_hardening,
              "SCap": r.strain_ultimate, "FinalSlope": r.final_slope, "UseCTDef": False})
    return m1, m2, m3


def build_design_tables(variant: str = "diseno", base: str = "CYPE", kphi: str | float = D.KPHI_DEFAULT,
                        info_areas: bool = True, model: dict | None = None,
                        when: datetime.datetime | None = None) -> W.S2K:
    """The .$2k of one variant (see the module docstring)."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    model = model or D.base_model()
    dm = D.design_model(model, groups=variant != "rect")
    header, tables = parse_lines(W.build_tables(dm, when).lines)
    header[0] = header[0].replace(f"{STEM}.$2k", f"{file_stem(variant, base)}.$2k")
    if variant == "rect":
        return render(header, tables)

    # 1. PROGRAM CONTROL: design code (C.1)
    put(table(tables, T_PROGRAM)[0], "ConcCode", D.DESIGN_CODE, after="CurrUnits")
    # 2. rebar material (C.2)
    m1, m2, m3 = rebar_material_records()
    table(tables, T_MAT1).append(m1)
    table(tables, T_MAT2).append(m2)
    insert_after(tables, T_MAT3B, T_MAT3E, [m3])
    # 3. column / beam reinforcement data (C.5, C.6)
    insert_after(tables, T_FSEC1, T_FSEC2, [rec(D.PILE_REBAR.s2k_row())])
    insert_after(tables, T_FSEC2, T_FSEC3,
                 [rec(br.s2k_row(info_areas)) for br in D.BEAM_REBAR.values()])
    # 4. design procedures (C.7)
    insert_after(tables, T_OFFSETS, T_PROC,
                 [rec({"Frame": fd.frame, "DesignProc": fd.s2k_procedure}) for fd in D.frame_designs(model)])
    # 5. combinations: strength flags, ROM family, auto combos off (C.8)
    fam = D.BASES[base]["family"]
    combos = table(tables, T_COMBO)
    for r in combos:
        cname = get(r, "ComboName")
        if get(r, "ConcDesign") is not None and re.fullmatch(fr"{fam}\d\d", cname or ""):
            put(r, "ConcDesign", "Strength")
    combos.extend(combo_records("ROM", strength=base == "ROM"))
    insert_after(tables, T_COMBO, T_AUTO, [rec({"DesignType": "Concrete", "AutoGen": False})])
    # 6. preferences (C.9), one record
    insert_after(tables, T_PROGRAM, T_PREF, [rec(D.preference_row())])
    # 7. overwrites (C.10), optional variant only
    if variant == "overwrites":
        tables.append([T_OVER, [rec(o["table"]) for o in D.overwrites(model, kphi)]])
    return render(header, tables)


def file_stem(variant: str, base: str = "CYPE") -> str:
    suffix = "" if base == "CYPE" else f"_{base}"
    return {"diseno": f"{STEM}_diseno{suffix}", "overwrites": f"{STEM}_diseno{suffix}_overwrites",
            "rect": f"{STEM}_rect"}[variant]


def write_all(out_dir: Path = OUT_DIR, base: str = "CYPE", kphi: str | float = D.KPHI_DEFAULT,
              info_areas: bool = True, variants: tuple = VARIANTS) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for v in variants:
        s = build_design_tables(v, base, kphi, info_areas)
        p = out_dir / f"{file_stem(v, base)}.$2k"
        p.write_bytes(s.text().encode("ascii"))
        paths[v] = p
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("-o", "--out", type=Path, default=OUT_DIR)
    ap.add_argument("--base", choices=tuple(D.BASES), default="CYPE",
                    help="design combinations flagged Strength: CYPE = ELU01-22, ROM = ELR01-22")
    ap.add_argument("--kphi", default=D.KPHI_DEFAULT,
                    help="pile Kphi overwrite (overwrites variant): ce (1.1129, CYPE e2 with SAP c = 8), "
                         "ce_is (1.1874, CE-strict e2 with d = h/2 + is), cype (1.373) or sap (0 = program, "
                         "1.0) or a number")
    ap.add_argument("--areas-cero", action="store_true",
                    help="write 0 instead of the provided beam areas in FRAME SECTION PROPERTIES 03")
    ap.add_argument("--decimal", choices=[".", ","], default=".")
    ap.add_argument("--variantes", nargs="+", choices=VARIANTS, default=list(VARIANTS))
    args = ap.parse_args()
    W.DECIMAL = args.decimal
    kphi = args.kphi if args.kphi in D.KPHI_OPTIONS else float(args.kphi)
    paths = write_all(args.out, args.base, kphi, not args.areas_cero, tuple(args.variantes))
    for v, p in paths.items():
        n = len(p.read_bytes().splitlines())
        print(f"{v:10s} {p}  ({n} lines)")


if __name__ == "__main__":
    main()
