"""Text recovery from the CYPE / MathType equation images (WMF metafiles) of Anejo 10.

Purpose
    CYPECAD prints every formula of its check listings as a Windows Metafile (WMF) image, so the
    .docx text holds only the numbers.  A WMF is a list of drawing records; the formula text is in
    its ExtTextOut records (0x0A32) together with the font selected at that moment
    (CreateFontIndirect 0x02FB / SelectObject 0x012D) and the text position (MoveTo 0x0214,
    SetTextAlign 0x012E with TA_UPDATECP, per-character dx arrays).  This module replays those
    records, maps the Symbol font to Unicode (a -> α, h -> η, \\xa3 -> ≤ ...) and prints a linear
    formula: characters smaller than the main font are marked `_` (subscript) or `^`
    (superscript) and characters far above / below the baseline `{num}` / `{den}` (fraction).
    The result is readable but not a verbatim transcription (fraction bars and radicals are
    lines, not text, and are lost).

Input
    the WMF bytes (from the .docx, see volcado.py) or a .wmf file path.

Output
    render(...) -> one-line string, e.g. 'VRd,max=αcw·bw·z·ν1·fcd·( _cotθ+cotα)( _1+cot ^2 _θ)'.

Run (stand-alone, on extracted .wmf files)
    python3 diseno/python/extraccion_anejo10/wmftext.py image17.wmf image19.wmf
"""

from __future__ import annotations

import struct
import sys

SYM = {'a': 'α', 'b': 'β', 'c': 'χ', 'd': 'δ', 'e': 'ε', 'f': 'φ', 'g': 'γ', 'h': 'η', 'i': 'ι', 'j': 'ϕ', 'k': 'κ',
       'l': 'λ', 'm': 'μ', 'n': 'ν', 'o': 'ο', 'p': 'π', 'q': 'θ', 'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'w': 'ω',
       'x': 'ξ', 'y': 'ψ', 'z': 'ζ', 'D': 'Δ', 'F': 'Φ', 'G': 'Γ', 'L': 'Λ', 'P': 'Π', 'Q': 'Θ', 'S': 'Σ', 'W': 'Ω', 'Y': 'Ψ',
       '\xb3': '≥', '\xa3': '≤', '\xd7': '·', '\xb4': '×', '\xa5': '∞', '\xd6': '√', '\xb1': '±', '\xe5': 'Σ', '\xb9': '≠',
       '\xae': '→', '\xba': '≡', '\xbb': '≈', '\xa2': '′', '\xe6': '(', '\xe8': '(', '\xe7': '', '\xf6': ')', '\xf8': ')', '\xf7': '',
       '\xe9': '[', '\xeb': '[', '\xea': '', '\xf9': ']', '\xfb': ']', '\xfa': '', '\xec': '{', '\xed': '{', '\xee': '{', '\xfc': '}',
       '\xfd': '}', '\xfe': '}', '\xef': '', '\xe0': '◊', '-': '−', '\xbe': '—', '\xd0': '∠', '\xf2': '∫', '\xa4': '/', '\xb6': '∂',
       '\xce': '∈'}


def parse(src):
    """WMF bytes (or a file path) -> list of (x, y, char, font_height) in drawing order."""
    b = src if isinstance(src, (bytes, bytearray)) else open(src, 'rb').read()
    off = 0
    if struct.unpack_from('<I', b, 0)[0] == 0x9AC6CDD7:     # Aldus placeable header
        off = 22
    off += struct.unpack_from('<H', b, off + 2)[0] * 2        # standard header (size in words)
    objs = {}
    sel = ('font', '', 0)
    chars = []
    cp = [0, 0]
    align = 0

    def slot():
        i = 0
        while i in objs:
            i += 1
        return i

    while off + 6 <= len(b):
        size, fn = struct.unpack_from('<IH', b, off)
        if size < 3:
            break
        p = off + 6
        if fn == 0x02FB:                                       # CreateFontIndirect
            h = struct.unpack_from('<h', b, p)[0]
            face = b[p + 18:p + 18 + 32].split(b'\0')[0].decode('latin1')
            objs[slot()] = ('font', face, abs(h))
        elif fn in (0x00F7, 0x02FA, 0x02FC, 0x06FF, 0x0142, 0x01F9):   # other GDI objects take a slot
            objs[slot()] = ('other',)
        elif fn == 0x012D:                                     # SelectObject
            i = struct.unpack_from('<H', b, p)[0]
            if i in objs and objs[i][0] == 'font':
                sel = objs[i]
        elif fn == 0x01F0:                                     # DeleteObject
            objs.pop(struct.unpack_from('<H', b, p)[0], None)
        elif fn == 0x012E:                                     # SetTextAlign
            align = struct.unpack_from('<H', b, p)[0]
        elif fn == 0x0214:                                     # MoveTo
            y, x = struct.unpack_from('<hh', b, p)
            cp = [x, y]
        elif fn == 0x0A32:                                     # ExtTextOut
            y, x, cnt, opts = struct.unpack_from('<hhhH', b, p)
            q = p + 8
            if opts & 0x6:
                q += 8
            s = b[q:q + cnt].decode('cp1252', 'replace')
            q += cnt + (cnt & 1)
            dx = list(struct.unpack_from('<%dh' % cnt, b, q)) if q + 2 * cnt <= off + size * 2 else [0] * cnt
            if align & 1:
                x0, y0 = cp
            else:
                x0, y0 = x, y
            xx = x0
            for c, d in zip(s, dx):
                if 'Symbol' in sel[1]:
                    c = SYM.get(c, c)
                chars.append((xx, y0, c, sel[2]))
                xx += d
            if align & 1:
                cp = [xx, y0]
        off += size * 2
    return chars


def render(src):
    """WMF bytes (or a file path) -> linear formula text ('' if the image holds no text)."""
    ch = [c for c in parse(src) if c[2].strip()]
    if not ch:
        return ''
    hmax = max(c[3] for c in ch)
    big = [c for c in ch if c[3] >= hmax * 0.85]
    ys = sorted(c[1] for c in big)
    base = ys[len(ys) // 2]
    out = []
    mode = ''
    for x, y, c, h in sorted(ch, key=lambda t: (t[0], t[1])):
        if h < hmax * 0.85:
            m = '_' if y > base - h * 0.3 else '^'
            if abs(y - base) > hmax * 0.9:
                m = '{' + ('num' if y < base else 'den') + '}' + m
        else:
            m = '' if abs(y - base) < hmax * 0.5 else ('{num}' if y < base else '{den}')
        if m != mode:
            out.append(('' if m == '' else ' ' + m))
            mode = m
        out.append(c)
    return ''.join(out)


if __name__ == '__main__':
    for fp in sys.argv[1:]:
        print(fp.split('/')[-1], '=>', render(fp))
