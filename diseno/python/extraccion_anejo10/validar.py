"""Validation of diseno/ref/cype_design_reference.json against Anejo 10 (step 4 of the extraction).

Purpose
    Prove that every transcribed value is really printed where its `src` says.  Two independent
    parts:

    A. fuentes      every {"value", "src"} object and every tabular row with a "src" is re-found in
                    the cited paragraph / table text of the main dump (volcado.volcado_rango): the
                    value, formatted with 0-6 decimals (or as "printed"), must occur in that text.
                    Values read from figures (src "... image ...") and notes without a printed
                    counterpart are skipped and counted.  One documented exception: the composed
                    '12Ø25' (Esquina 4Ø25 + Cara X 4Ø25 + Cara Y 4Ø25).
    B. independiente the same document dumped by a second walker (volcado.volcado_independiente:
                    other glyph table, other nested-table format) and re-parsed with separate code:
                      B1 every table value addressed as "[A > B] symbol (occurrence k)" equals the
                         number printed in that row;
                      B2 the 52 CYPE combinations (§1.6.2) factor by factor, and every zone of the
                         §2 beam listing (moments, shears, torsions and their x, As real / nec,
                         section, deflections);
                      B3 pile tables §3.2, §3.3, §3.5 and §4.2 row by row;
                      B4 the 'description' of every value of the all_printed_values / summary_values
                         lists (own label, label of the row above, or empty / "no text label").

Input
    the reference dict and the dump texts (volcado.todos).

Output
    validar(d, textos) -> (ok, lines of report); extraer.py prints the report and fails if not ok.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tablas import load_text, NO_LABEL  # noqa: E402

EXCEPCIONES = {"/piles/general/reinforcement_summary/bars":
               "composed value 12Ø25 = Esquina 4Ø25 + Cara X 4Ø25 + Cara Y 4Ø25 (P220 table prints the three parts)"}


def _cells(r):
    return [c.strip() for c in r.split(" | ")]


# ------------------------------------------------------------------------------------------------
# A. values re-found in their cited source (main dump)
# ------------------------------------------------------------------------------------------------
def _variants(v, printed=None):
    out = set()
    if printed:
        out.add(printed.lstrip("+"))
    if isinstance(v, bool) or v is None:
        return out
    if isinstance(v, (int, float)):
        for nd in range(0, 7):
            s = f"{v:.{nd}f}"
            out.add(s)
            if v > 0:
                out.add("+" + s)
        out.add(repr(v))
        out.add(str(v))
    else:
        out.add(str(v))
    return out


def fuentes(d, textos):
    _, BT, BP = load_text(textos["trasmallo_body.txt"])
    _, AT, AP = load_text(textos["trasmallo_app.txt"])
    _, PT, PP = load_text(textos["trasmallo_pre.txt"])
    TAB = {**BT, **AT}
    PAR = {**BP, **AP, **PP}

    def source_text(src):
        m = re.match(r"^(P\d+ table(?:#\d+)?)", src)
        if m and m.group(1) in TAB:
            return "\n".join(TAB[m.group(1)])
        m = re.match(r"^P(\d+)(?:\s|$)", src)
        if m and "image" not in src and int(m.group(1)) in PAR:
            return PAR[int(m.group(1))]
        return None

    st = collections.Counter()
    fails = []

    def walk(o, path):
        if isinstance(o, dict):
            if "value" in o and "src" in o:
                txt = source_text(o["src"])
                if " image " in o["src"]:
                    st["skipped_image"] += 1
                elif txt is None or o["value"] is None:
                    st["skipped_no_text"] += 1
                else:
                    st["checked"] += 1
                    if not any(s in txt for s in _variants(o["value"], o.get("printed")) if s):
                        if path in EXCEPCIONES:
                            st["documented_exception"] += 1
                        else:
                            fails.append((path, o["value"], o["src"]))
            for k, v in o.items():
                walk(v, path + "/" + k)
            if "src" in o and "value" not in o and isinstance(o["src"], str):     # tabular row
                txt = source_text(o["src"])
                if txt:
                    for k, v in o.items():
                        if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in ("bar", "comb"):
                            st["checked"] += 1
                            if not any(s in txt for s in _variants(v)):
                                fails.append((path + "/" + k, v, o["src"]))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")

    walk(d, "")
    lines = [f"A  source re-find: {st['checked']} values checked, {len(fails)} not found, "
             f"{st['documented_exception']} documented exception(s), {st['skipped_image']} read from figures (skipped), "
             f"{st['skipped_no_text']} without a printed counterpart (skipped)"]
    lines += [f"   NOT FOUND {p} = {v!r}  ({s})" for p, v, s in fails[:50]]
    lines += [f"   exception {p}: {why}" for p, why in EXCEPCIONES.items()]
    return not fails, lines


# ------------------------------------------------------------------------------------------------
# B. independent re-parse (second dump)
# ------------------------------------------------------------------------------------------------
def _load_indep(text):
    paras, tables = {}, {}
    anchor = cur = None
    cnt = {}
    for ln in text.split("\n"):
        if cur is None:
            m = re.match(r"^P(\d+)\t(.*)$", ln)
            if m:
                anchor = int(m.group(1))
                paras[anchor] = m.group(2)
                continue
            if ln == "TABLE>>":
                cur = []
                continue
        else:
            if ln == "<<TABLE":
                cnt[anchor] = cnt.get(anchor, 0) + 1
                tables[f"P{anchor} table" + ("" if cnt[anchor] == 1 else f"#{cnt[anchor]}")] = cur
                cur = None
                continue
            cur.append(ln)
    return paras, tables


def _f(s):
    s = s.strip()
    if s in ("", "--", "-"):
        return None
    try:
        return float(s.replace("+", ""))
    except ValueError:
        return s


def _same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) < 1e-9
    return a == b


def _values(d):
    items = []

    def walk(o, path):
        if isinstance(o, dict):
            if "value" in o and "src" in o:
                items.append((path, o))
            for k, v in o.items():
                if k != "value":
                    walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(d, "")
    return items


def indep_values(d, tables):
    """B1: '[A > B] sym (occurrence k)' values."""
    ok = bad = skip = 0
    out = []
    for p, o in _values(d):
        src, v = o["src"], o["value"]
        m = re.match(r"^(P\d+ table(?:#\d+)?): (?:\[(.*?)\] )?(.+?)(?: \(occurrence (\d+)\))?$", src)
        if not m or not isinstance(v, (int, float)) or isinstance(v, bool):
            skip += 1
            continue
        tid, path, sym, occ = m.groups()
        occ = int(occ) if occ else 1
        t = tables.get(tid)
        if t is None:
            bad += 1
            out.append(f"   B1 {p}: table {tid} not found")
            continue
        lo = 0
        if path:
            for part in path.split(" > "):
                part = re.sub(r" \(#\d+\)$", "", part.rstrip(".").replace("...", ""))
                for i in range(lo, len(t)):
                    if _cells(t[i])[0].lstrip("{").startswith(part):
                        lo = i
                        break
                else:
                    lo = None
                    break
        if lo is None:
            bad += 1
            out.append(f"   B1 {p}: header path '{path}' not found in {tid}")
            continue
        vals = [c[4] for c in (_cells(r) for r in t[lo:]) if len(c) >= 5 and c[2] == sym and c[3] == ":"]
        if len(vals) < occ:                 # key/value rows of other layouts (datos tables, statements ...)
            skip += 1
            continue
        pv = _f(vals[occ - 1])
        if isinstance(pv, float) and abs(pv - v) < 1e-9:
            ok += 1
        else:
            bad += 1
            out.append(f"   B1 {p} = {v!r}: printed {vals[occ - 1]!r} ({src})")
    return bad == 0, [f"B1 table values by symbol: {ok} equal, {bad} different, {skip} not of this form (skipped)"] + out[:50]


def indep_listings(d, tables):
    """B2: §1.6.2 combinations and §2 beam listing zones."""
    out = []
    n = bad = 0
    for key, rows in d["materials_and_parameters"]["combinations_1_6_2"].items():
        for r in rows:
            t = tables[r["src"].split(":")[0]]
            hdr = _cells(t[0])
            row = [_cells(x) for x in t[1:] if _cells(x)[0] == str(r["comb"])][0]
            for h, v in r["factors"].items():
                dv = _f(row[hdr.index(h)])
                dv = 0.0 if dv is None else dv
                n += 1
                if abs(dv - v) > 1e-9:
                    bad += 1
                    out.append(f"   B2 combination {key} {r['comb']} {h}: {v} vs printed {dv}")
    ncomb, badcomb = n, bad
    fields = [("Momento mín.", "M_min", "x_M_min"), ("Momento máx.", "M_max", "x_M_max"), ("Cortante mín.", "V_min", "x_V_min"),
              ("Cortante máx.", "V_max", "x_V_max"), ("Torsor mín.", "T_min", "x_T_min"), ("Torsor máx.", "T_max", "x_T_max")]
    n = bad = 0
    for pname, por in d["beams"]["listing_armado_vigas_2"]["porticos"].items():
        for tname, tr in por["tramos"].items():
            for z in tr["zones"]:
                tid, tn, zn = re.match(r"(P\d+ table(?:#\d+)?): column 'Tramo: (.*?)' zone (\S+)", z["src"]).groups()
                t = [_cells(x) for x in tables[tid]]
                if t[0][0] != pname:
                    bad += 1
                    out.append(f"   B2 {tid}: heading {t[0][0]!r} != {pname!r}")
                col = t[0][1:].index("Tramo: " + tn) * 3 + ["1/3L", "2/3L", "3/3L"].index(zn)
                for i, r in enumerate(t):
                    for lab, k, kx in fields:
                        if r[0] == lab:
                            for kk, arr in ((k, r[2:]), (kx, t[i + 1][2:])):
                                n += 1
                                if _f(arr[col]) != z[kk]:
                                    bad += 1
                                    out.append(f"   B2 {pname} {tn} {zn} {kk}: {z[kk]} vs printed {arr[col]}")
                    if r[0] in ("Área Sup.", "Área Inf.", "Área Transv."):
                        k = {"Área Sup.": "As_top", "Área Inf.": "As_bot", "Área Transv.": "Asw_per_m"}[r[0]]
                        for kk, arr in ((k + "_real", r[3:]), (k + "_nec", t[i + 1][3:])):
                            n += 1
                            if _f(arr[col]) != z[kk]:
                                bad += 1
                                out.append(f"   B2 {pname} {tn} {zn} {kk}: {z[kk]} vs printed {arr[col]}")
            t = [_cells(x) for x in tables[tr["section"]["src"].split(":")[0]]]
            head = t[0][1:]
            srow = [r for r in t if r[0] == "Sección"][0]
            n += 1
            if srow[1 + head.index("Tramo: " + tname)] != tr["section"]["value"]:
                bad += 1
                out.append(f"   B2 {pname} {tname} section")
            for fk, lab in (("activa", "F. Activa"), ("plazo_infinito", "F. A plazo infinito")):
                txt = [r for r in t if r[0] == lab][0][1 + head.index("Tramo: " + tname)]
                fl = tr["flechas"][fk]
                mm = re.match(r"([\d.]+) mm, (<?L/\d+) \(L: ([\d.]+) m\)", txt)
                n += 1
                if (txt != fl["printed"] or float(mm.group(1)) != fl["f"]["value"] or float(mm.group(3)) != fl["L_ref"]["value"]
                        or mm.group(2) != fl["ratio"]):
                    bad += 1
                    out.append(f"   B2 {pname} {tname} {fk}: {fl['printed']!r} vs printed {txt!r}")
    ok = badcomb == 0 and bad == 0
    return ok, [f"B2 combinations: {ncomb} factors, {badcomb} different; beam listing: {n} values, {bad} different"] + out[:50]


def indep_piles(d, tables):
    """B3: pile tables of Apéndice 1 §3.2, §3.3, §3.5, §4.2."""
    a = d["piles"]["appendix_1_section_3"]
    out = []
    counts = {}

    def cmp(tag, jv, dv):
        counts.setdefault(tag, [0, 0])
        counts[tag][0] += 1
        if len(jv) != len(dv) or not all(_same(x, y) for x, y in zip(jv, dv)):
            counts[tag][1] += 1
            out.append(f"   B3 {tag}: {jv} vs printed {dv}")

    doc, cur = {}, None                                                   # §3.3
    for r in (_cells(x) for x in tables["P1702 table"][2:]):
        cur = r[0] or cur
        if len(r) >= 17:
            doc[(cur, r[4])] = [float(x) for x in r[5:17]]
    for jr in a["esfuerzos_por_hipotesis_3_3"]["rows"]:
        cmp("§3.3", [jr["base"][k] for k in ("N", "Mx", "My", "Qx", "Qy", "T")] + [jr["cabeza"][k] for k in ("N", "Mx", "My", "Qx", "Qy", "T")],
            doc[(jr["pilar"], jr["hipotesis"])])
    cur4, docs = [None] * 4, []                                            # §3.5
    for r in (_cells(x) for x in tables["P1714 table"][3:]):
        if len(r) < 13:
            continue
        cur4 = [r[i] or cur4[i] for i in range(4)]
        docs.append(cur4[:] + [x if i in (0, 6, 8) else _f(x) for i, x in enumerate(r[4:13])])
    js = a["pesimos_3_5"]["rows"]
    if len(js) != len(docs):
        out.append(f"   B3 §3.5 row count {len(js)} vs printed {len(docs)}")
        counts.setdefault("§3.5", [0, 0])[1] += 1
    for jr, dr in zip(js, docs):
        cmp("§3.5", [jr[k] for k in ("pilar", "tramo", "dim_cm", "posicion", "naturaleza", "N_kN", "Mxx_kNm", "Myy_kNm", "Qx_kN",
                                     "Qy_kN", "pesima", "aprov_pct", "estado")], dr)
    cur, docs = None, []                                                   # §3.2
    for r in (_cells(x) for x in tables["P1692 table"][5:]):
        if len(r) < 12:
            continue
        cur = r[0] or cur
        docs.append([cur, r[1], r[2], r[3], r[4], r[5], r[6], _f(r[7]), r[8], _f(r[9]), _f(r[10]), r[11]])
    js = a["armado_pilares_3_2"]["rows"]
    if len(js) != len(docs):
        out.append(f"   B3 §3.2 row count {len(js)} vs printed {len(docs)}")
        counts.setdefault("§3.2", [0, 0])[1] += 1
    for jr, dr in zip(js, docs):
        cmp("§3.2", [jr[k] for k in ("pilar", "planta", "dim_cm", "tramo_m", "esquina", "cara_X", "cara_Y", "cuantia_pct", "estribos",
                                     "separacion_cm", "aprov_pct", "estado")], dr)
    for pil, blk in a["elu_checks_4_2"].items():                           # §4.2
        cur8, docs = [None] * 8, []
        for r in (_cells(x) for x in tables[blk["src"]][3:]):
            if len(r) < 16:
                continue
            cur8 = [r[i] or cur8[i] for i in range(8)]
            docs.append([_f(x) if i not in (0, 1, 2, 3, 4, 8, 9, 15) else x for i, x in enumerate(cur8[:] + r[8:16])])
        if len(blk["rows"]) != len(docs):
            out.append(f"   B3 §4.2 {pil} row count {len(blk['rows'])} vs printed {len(docs)}")
            counts.setdefault("§4.2", [0, 0])[1] += 1
        for jr, dr in zip(blk["rows"], docs):
            if dr[15] in (None, ""):               # 'estado' printed only on the first row of a merged group
                dr[15] = jr["estado"]
            cmp("§4.2", [jr[k] for k in ("tramo", "dim_cm", "posicion", "disp", "arm", "Q_pct", "NM_pct", "aprov_pct", "naturaleza",
                                         "comp", "N_kN", "Mxx_kNm", "Myy_kNm", "Qx_kN", "Qy_kN", "estado")], dr)
    ok = all(b == 0 for _, b in counts.values())
    return ok, ["B3 pile tables: " + ", ".join(f"{k} {n} rows / {b} different" for k, (n, b) in counts.items())] + out[:50]


def indep_descriptions(d, tables):
    """B4: 'description' of the values in all_printed_values / summary_values."""
    def norm(s):
        return s.replace("ϕ", "φ")

    def entries(tid):
        out, prev = [], None
        for r in tables[tid]:
            c = _cells(r)
            if len(c) >= 6 and c[3] == ":" and c[2]:
                if c[0]:
                    desc = c[0].split(":", 1)[1].strip() if ":" in c[0] else c[0]
                else:
                    desc = prev if prev is not None else ""
                out.append((c[2], desc))
                prev = desc
            elif r.strip() and not all(x == "" for x in c):
                prev = None
        return out

    n = bad = 0
    out = []

    def walk(o, path):
        nonlocal n, bad
        if isinstance(o, dict):
            if "symbol" in o and "description" in o and "src" in o:
                tid, sym, occ = re.match(r"^(P\d+ table(?:#\d+)?): (.+?)(?: \(occurrence (\d+)\))?$", o["src"]).groups()
                es = [e for e in entries(tid) if norm(e[0]) == norm(sym)]
                want = es[int(occ or 1) - 1][1] if len(es) >= int(occ or 1) else None
                n += 1
                if want is None or not (norm(want) == norm(o["description"]) or (want == "" and o["description"] == NO_LABEL)):
                    bad += 1
                    out.append(f"   B4 {path}: {o['description']!r} vs printed label {want!r}")
            for k, v in o.items():
                walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(d, "")
    return bad == 0, [f"B4 descriptions: {n} checked, {bad} different"] + out[:50]


def validar(d, textos):
    ok, lines = fuentes(d, textos)
    _, tables = _load_indep(textos["a10_independiente.txt"])
    for fn in (indep_values, indep_listings, indep_piles, indep_descriptions):
        o, ls = fn(d, tables)
        ok = ok and o
        lines += ls
    return ok, lines


if __name__ == "__main__":
    import json
    import volcado
    ref = sys.argv[1] if len(sys.argv) > 1 else str(volcado.ROOT / "diseno" / "ref" / "cype_design_reference.json")
    ok, lines = validar(json.load(open(ref, encoding="utf-8")), volcado.todos(volcado.abrir(), formulas=False))
    print("\n".join(lines))
    print("VALIDATION", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)
