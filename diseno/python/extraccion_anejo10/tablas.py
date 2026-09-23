"""Parsing helpers for the Anejo 10 text dumps (volcado.py format), used by construir.py.

Purpose
    Turn the 'P<n>\t...' / 'TABLE>>' ... '<<TABLE' dump into tables addressable by the id used in
    every `src` of the CYPE reference ("P<n> table" = the table that follows paragraph P<n> in
    document order, "#k" when several tables follow the same paragraph) and read CYPE's check
    listings, whose rows look like

        'Esfuerzo cortante efectivo: |  | VEd,y |  : | 390.18 | kN'      -> entry  (label, symbol, value, unit)
        ' |  | 390.18 kN | ≤ | 407.15 kN | [IMG image18.png]'          -> check  (lhs, operator, rhs, ✓ mark)

    Every scalar returned by the getters is {"value", "unit", "src"[, "printed"][, "note"]};
    "printed" keeps the literal text when the float would print differently (e.g. '1.000').
    Tab.seg("Header A", "Header B") narrows a table to the rows between two header rows, which
    gives sources such as "P245 table: [Comprobación de resistencia de la sección] NEd".

Input
    the dump text (volcado.volcado_rango).

Output
    Python objects (tables, paragraphs, value dicts).
"""
import re

IMG_RE = re.compile(r"\[IMG [^\]]*\]")
NO_LABEL = "(no text label: value printed under an equation image)"


def num(s):
    s = s.strip()
    if s in ("", "--", "-"):
        return None
    t = s[1:] if s.startswith("+") else s
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+\.\d*|-?\.\d+", t):
        return float(t)
    return s


def split_vu(s):
    """'60 mm' -> (60, 'mm');  '58.91 cm²' -> (58.91, 'cm²')."""
    s = s.strip()
    m = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)(?:\s+(\S.*))?", s)
    if not m:
        return s, "-"
    return num(m.group(1)), ((m.group(2) or "").strip() or "-")


def V(value, unit, src, note=None, printed=None):
    d = {"value": value, "unit": unit if unit not in (None, "") else "-", "src": src}
    if printed is not None and isinstance(value, float):
        p = printed.strip().lstrip("+")
        if p != repr(value):
            d["printed"] = printed.strip()
    if note:
        d["note"] = note
    return d


def load_text(text):
    """Dump text -> (items in order, {table id: rows}, {paragraph number: text})."""
    items, tables, paras = [], {}, {}
    anchor, cur, cnt = None, None, {}
    for ln in text.split("\n"):
        if cur is None:
            m = re.match(r"^P(\d+)\t(.*)$", ln)
            if m:
                anchor = int(m.group(1))
                paras[anchor] = m.group(2)
                items.append(("P", anchor, m.group(2)))
                continue
            if ln == "TABLE>>":
                cur = []
                continue
        else:
            if ln == "<<TABLE":
                cnt[anchor] = cnt.get(anchor, 0) + 1
                tid = f"P{anchor} table" + ("" if cnt[anchor] == 1 else f"#{cnt[anchor]}")
                tables[tid] = cur
                items.append(("T", tid, cur))
                cur = None
                continue
            cur.append(ln)
    return items, tables, paras


def load(path):
    return load_text(open(path, encoding="utf-8").read())


def cells_of(row):
    return [c.strip() for c in row.split(" | ")]


class Tab:
    def __init__(self, tid, rows):
        self.tid, self.rows = tid, rows
        self.entries, self.checks, self.texts = [], [], []
        # description of an entry: its own label ('Esfuerzo cortante efectivo: ...' -> text after the
        # colon); an unlabelled entry inherits the description of the entry right above it, but only
        # while no other non-empty row intervenes (an equation-image row, a check or a text row
        # breaks the chain: the value is then printed under an equation image -> NO_LABEL).  Entries
        # before the first labelled row of the table (e.g. NRd / MRd,x / MRd,y under an equilibrium
        # diagram, the first η of a shear table) keep an empty description.
        prev = None
        last_label = ""
        for i, row in enumerate(rows):
            c = cells_of(row)
            if len(c) == 6 and c[3] == ":" and c[2]:
                if c[0]:
                    last_label = c[0]
                    desc = c[0].split(":", 1)[1].strip() if ":" in c[0] else c[0]
                else:
                    desc = prev if prev is not None else ""
                prev = desc
                first = last_label.split(":", 1)[-1].strip() if ":" in last_label else last_label
                unit = IMG_RE.sub("", c[5]).strip()
                self.entries.append(dict(i=i, desc=desc or (NO_LABEL if first else ""), sym=c[2], raw=c[4], unit=unit))
                continue
            if row.strip() and not all(x == "" for x in c):
                prev = None
            if len(c) == 6 and c[3] in ("≤", "≥") and c[2]:
                self.checks.append(dict(i=i, lhs=c[2], op=c[3], rhs=c[4], ok="image18" in c[5]))
            else:
                t = IMG_RE.sub("", " ".join(x for x in c if x)).strip(" {}")
                if t:
                    self.texts.append((i, t))

    # ---- segments ------------------------------------------------------------------------
    def seg(self, start=None, end=None, k=1):
        return Seg(self, 0, len(self.rows), []).seg(start, end, k)

    def all(self):
        return Seg(self, 0, len(self.rows), [])


class Seg:
    def __init__(self, tab, lo, hi, path):
        self.tab, self.lo, self.hi, self.path = tab, lo, hi, path

    def _find(self, text, frm, k=1):
        n = 0
        for i in range(frm, self.hi):
            if cells_of(self.tab.rows[i])[0].lstrip("{").startswith(text):
                n += 1
                if n == k:
                    return i
        raise KeyError(f"{self.tab.tid}: '{text}' not found (k={k}) in rows {frm}..{self.hi}")

    def seg(self, start=None, end=None, k=1):
        lo = self._find(start, self.lo, k) if start else self.lo
        hi = self._find(end, lo + 1) if end else self.hi
        label = start.rstrip(":") if start else ""
        if label and len(label) > 60:
            label = label[:57] + "..."
        if k > 1 and label:
            label += f" (#{k})"
        return Seg(self.tab, lo, hi, self.path + ([label] if label else []))

    def _src(self, sym, k, total):
        p = " > ".join(self.path)
        q = f" (occurrence {k})" if total > 1 else ""
        return f"{self.tab.tid}: " + (f"[{p}] " if p else "") + sym + q

    def entries(self):
        return [e for e in self.tab.entries if self.lo <= e["i"] < self.hi]

    def get(self, sym, k=1, note=None):
        es = [e for e in self.entries() if e["sym"] == sym]
        if len(es) < k:
            raise KeyError(f"{self.tab.tid} {self.path}: sym '{sym}' #{k} not found; have {[e['sym'] for e in self.entries()]}")
        e = es[k - 1]
        return V(num(e["raw"]), e["unit"] or "-", self._src(sym, k, len(es)), note, printed=e["raw"])

    def dump(self):
        out, seen = [], {}
        allsyms = [e["sym"] for e in self.entries()]
        for e in self.entries():
            seen[e["sym"]] = seen.get(e["sym"], 0) + 1
            d = V(num(e["raw"]), e["unit"] or "-", self._src(e["sym"], seen[e["sym"]], allsyms.count(e["sym"])), printed=e["raw"])
            d = {"symbol": e["sym"], "description": e["desc"], **d}
            out.append(d)
        return out

    def checks(self):
        out = []
        cs = [c for c in self.tab.checks if self.lo <= c["i"] < self.hi]
        for n, c in enumerate(cs, 1):
            lv, lu = split_vu(c["lhs"])
            rv, ru = split_vu(c["rhs"])
            # description = nearest preceding text row
            desc = ""
            for i, t in self.tab.texts:
                if i < c["i"]:
                    desc = t
            if desc.startswith("Cortante en la dirección") or desc in ("Donde:", "Siendo:"):
                nxt = [t for i, t in self.tab.texts if i > c["i"]]
                if nxt:
                    desc = desc + " " + nxt[0]
            out.append({"check": desc, "provided": V(lv, lu, f"{self.tab.tid}: check {n} left"),
                        "operator": c["op"], "limit": V(rv, ru, f"{self.tab.tid}: check {n} right"),
                        "cype_ok_mark": c["ok"]})
        return out

    def statements(self, contains="se producen"):
        return [(i, t) for i, t in self.tab.texts if self.lo <= i < self.hi and contains in t]


COMB_RE = re.compile(r"se producen(?: en '([^']*)')?,? para la combinación de (?:hipótesis|acciones) \"?(.+?)\"?\.?\s*$")


def statement(seg, n, tid_label=None):
    st = seg.statements()
    i, t = st[n - 1]
    m = COMB_RE.search(t)
    src = f"{seg.tab.tid}: statement {n} (row 'Los esfuerzos solicitantes de cálculo pésimos se producen ...')"
    pos = m.group(1) if m else None
    comb = m.group(2) if m else None
    return {"position": V(pos, "-", src), "combination": V(comb, "-", src), "text": t}


def nested_kv(cell):
    """'{Dimensiones | : | 40x40 cm ;; Tramo | : | 0.000/7.250 m}' -> [(key, value_text)]."""
    cell = cell.strip()
    if cell.startswith("{") and cell.endswith("}"):
        cell = cell[1:-1]
    out = []
    for part in cell.split(" ;; "):
        c = [x.strip() for x in part.split(" | ")]
        if len(c) >= 3 and c[1] == ":":
            out.append((c[0], c[2]))
    return out
