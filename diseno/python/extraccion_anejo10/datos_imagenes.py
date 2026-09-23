"""Values of the CYPE reference that were READ BY EYE from figures of Anejo 10 (not scriptable).

Purpose
    Some reference data exist only inside raster figures of report/A10_CALC_ESTRUCTURAS.docx (CYPE
    screenshots: stress/strain diagrams, N-M interaction surfaces, bar drawings, envelopes, slab
    plans).  They were read on the rendered images (zoomed where needed) and are kept here as a
    documented data table, so that construir.py stays a pure parser for everything else.  Each
    value carries src = "P<n> image imageNN.png" (anchor paragraph + Word media file name; the file
    is word/media/imageNN.png inside the .docx) and, where the reading is not certain, a confidence
    or a note.  validar.py skips these values (they cannot be re-found in the text).

    image16   P220   pile section sketch (bars, ties)                       description
    image50   P245   pile head N-M interaction diagram labels               6 values
    image84   P257   pile head equilibrium at ultimate: x, ε, σ             4 values
    image88   P265   pile head equilibrium at design forces                 4 values
    image92   P275   CEB tables 5.9 / 5.10 (ψ coefficients)                 2 small tables
    image94   P300   pile base N-M interaction diagram labels               6 values
    image95   P312   pile base equilibrium at ultimate                      4 values
    image96   P320   pile base equilibrium at design forces                 4 values
    image97   P336   beam P3-P4 bar drawing (body)                          6 labels
    image112  P381   beam equilibrium at ultimate                           4 values
    image113  P389   beam equilibrium at design forces                      4 values
    image117  P569   quasi-permanent moments (Pórtico 6 plan)               3 values + labels
    image118  P571   crack hand check: strains / stresses / wk              12 values
    image120  P586   deflection history plot                                text
    image121  P593   slab envelope (per 1 m band)                           ~40 values, bar labels
    image122  P595   alveoplaca characteristics                             7 values
    image123  P600   slab negative-bar plan (axes 1-3)                      labels
    image124  P603   slab negative bending table                            6 rows
    image203-image212  P1607-P1660  Apéndice 1 beam drawings (bar schedules, envelope labels)

Input
    none (literal data).

Output
    functions returning the JSON fragments inserted by construir.py; listar(d) lists every
    by-eye value of a built reference.

Run
    python3 diseno/python/extraccion_anejo10/datos_imagenes.py    # prints the list of by-eye values
                                                                   # found in diseno/ref/cype_design_reference.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tablas import V  # noqa: E402


def IMG(n, img, value, unit="-", note=None, conf=None):
    d = V(value, unit, f"P{n} image {img}", note)
    if conf:
        d["confidence"] = conf
    return d


def _labels(n, img, rows):
    """rows = [(key, value, unit[, note]), ...] -> {key: IMG(...)} in the given order."""
    return {r[0]: IMG(n, img, *r[1:]) for r in rows}


# ------------------------------------------------------------------------------------------------
# PILES (body, pile P3)
# ------------------------------------------------------------------------------------------------
# equilibrium diagrams (neutral-axis depth, extreme strains, maximum concrete stress)
EQUILIBRIUM_PILE = {
    "image84.png": (257, [("x_neutral_axis", 181.04, "mm"), ("eps_max", 3.48, "‰"), ("eps_min", -5.66, "‰"), ("sigma_max", 33.33, "MPa")]),
    "image88.png": (265, [("x_neutral_axis", 188.19, "mm"), ("eps_max", 2.56, "‰"), ("eps_min", -3.90, "‰"), ("sigma_max", 33.33, "MPa")]),
    "image95.png": (312, [("x_neutral_axis", 184.36, "mm"), ("eps_max", 3.48, "‰"), ("eps_min", -5.54, "‰"), ("sigma_max", 33.33, "MPa")]),
    "image96.png": (320, [("x_neutral_axis", 191.03, "mm"), ("eps_max", 2.46, "‰"), ("eps_min", -3.69, "‰"), ("sigma_max", 33.33, "MPa")]),
}

# N-M interaction diagram labels, printed as (Myy;Mxx;N)
CAPACITY_PILE = {
    "image50.png": (245, [
        ("N_max_compression", 7689.61, "kN", "label (0;0;7689.61) = (Myy;Mxx;N)"),
        ("N_max_tension", -2561.11, "kN", "label (0;0;-2561.11)"),
        ("M_max_at_N_2098_3", 473.52, "kN·m", "labels (±473.52;0;2098.3), (0;±473.52;2098.3): uniaxial moment capacity at N = 2098.3 kN"),
        ("N_at_M_max", 2098.3, "kN"),
        ("design_point", "(-68.95;353.51;620.06)", "(kN·m;kN·m;kN)"),
        ("capacity_point", "(-75.52;387.2;679.16)", "(kN·m;kN·m;kN)")]),
    "image94.png": (300, [
        ("N_max_compression", 7689.61, "kN"),
        ("N_max_tension", -2561.11, "kN"),
        ("M_max_at_N_2098_3", 477.19, "kN·m", "labels (±477.19;0;2098.3), (0;±477.19;2098.3) — bars at ±129.5 mm (Ø8 ties) give a larger lever arm than at forjado (±127.5)"),
        ("N_at_M_max", 2098.3, "kN"),
        ("design_point", "(71.29;-352.07;655.55)", "(kN·m;kN·m;kN)"),
        ("capacity_point", "(79.72;-393.69;733.05)", "(kN·m;kN·m;kN)")]),
}


def equilibrium_pile(img):
    n, rows = EQUILIBRIUM_PILE[img]
    return _labels(n, img, rows)


def capacity_pile(img):
    n, rows = CAPACITY_PILE[img]
    return _labels(n, img, rows)


def section_sketch_image16():
    return IMG(220, "image16.png", "40x40 square, 12 bars (4 per face incl. corners); 3 closed ties drawn: one perimeter tie, "
               "one inner tie around the two middle columns of bars and one inner tie around the two middle rows", note="visual description of the sketch")


def psi_table_image92():
    return {
        "src": "P275 image image92.png",
        "note": "CEB (1976) Tablas 5.9/5.10 inserted before the crack statement; quasi-permanent coefficient = C",
        "tabla_5_9": [{"estado": "Último", "carga": "Fundamental", "psi_1": "1.0", "psi_i": "A"},
                      {"estado": "Último", "carga": "Accidental", "psi_1": "B", "psi_i": "C"},
                      {"estado": "Último", "carga": "Infrecuente", "psi_1": "1.0", "psi_i": "B"},
                      {"estado": "de Servicio", "carga": "Cuasi-permanente", "psi_1": "C", "psi_i": "C"},
                      {"estado": "de Servicio", "carga": "Frecuente", "psi_1": "B", "psi_i": "B"}],
        "tabla_5_10": {"Viviendas": [0.5, 0.7, 0.4], "Oficinas": [0.5, 0.8, 0.4], "Otros Edificios": [0.5, 0.9, 0.4],
                       "Aparcamientos": [0.6, 0.7, 0.6], "Viento": [0.55, 0.2, 0.0], "Nieve": [0.55, None, None],
                       "Viento y Nieve": ["0.55 y 0.4", None, None], "columns": ["A", "B", "C"]}}


# ------------------------------------------------------------------------------------------------
# BEAM P3-P4 (body)
# ------------------------------------------------------------------------------------------------
def bar_layout_image97():
    """Literal reading of the cropped body drawing (legs drawn at the right end only)."""
    return {
        "src": "P336 table image image97.png",
        "labels": ["top: 5Ø20 (471), leg 25 drawn at the right (P4) end only",
                   "side (piel) web: I1Ø10+D1Ø10 (470), right end leg 17 + return 8",
                   "section tag: 50x55+15x30+15x30",
                   "ledges: I1Ø10+D1Ø10 M. Alas (421), straight",
                   "bottom web: 5Ø20 (471), leg 25 drawn at the right end only",
                   "bottom ledges: I1Ø20+D1Ø20 (490), leg 17 at the right end, marks 18 at both ends"],
        "note": ("lengths in cm; I = izquierda, D = derecha; drawing of P3-P4 (Pórtico 4). The body image shows the end legs "
                 "only at the right end; the full listing drawing of Pórtico 4 (image205) shows them at both ends "
                 "(5Ø20 legs 25/25, I1Ø10+D1Ø10 legs 17/17 + 8/8, I1Ø20+D1Ø20 legs 17/17 + marks 18/18) — use image205 for the bar shapes.")}


EQUILIBRIUM_BEAM = {
    "image112.png": (381, [("x_neutral_axis", 68.52, "mm"), ("eps_min_top", -11.64, "‰"), ("eps_max_bottom", 1.66, "‰"), ("sigma_max", 22.65, "MPa")]),
    "image113.png": (389, [("x_neutral_axis", 110.25, "mm"), ("eps_min_top", -2.33, "‰"), ("eps_max_bottom", 0.59, "‰"), ("sigma_max", 11.65, "MPa")]),
}


def equilibrium_beam(img):
    n, rows = EQUILIBRIUM_BEAM[img]
    return _labels(n, img, rows)


def qp_moments_image117():
    return {
        "src": "P569 image image117.png",
        "labels": _labels(569, "image117.png", [("M_at_P8", -8.47, "kN·m"), ("M_span_max", 86.66, "kN·m"), ("M_at_P7", -12.21, "kN·m")]),
        "other_labels": ["80x30 + 50x55 (section tag)", "Ø10/1?(325) (slab negative bar label, partly hidden)", "380", "(162)",
                         "Pórtico 6", "P7 (40x40)", "P8 (40x40)", "P12 (CHS 159.0x5.0)"],
        "note": "Plan view of Pórtico 6 (P12-P7-P8) although the heading says P5 - P6."}


def crack_stress_image118():
    return {
        "src": "P571 image image118.png",
        **_labels(571, "image118.png", [
            ("NEd", 0.0, "kN"), ("MEd_x", 86.0, "kN·m"), ("MEd_y", 0.0, "kN·m"),
            ("strain_top_fibre", 0.000082, "-"), ("strain_top_bars", 0.000069, "-"),
            ("strain_bottom_bars", -0.000051, "-"), ("strain_bottom_fibre", -0.000065, "-"),
            ("stress_top_fibre", 2.73, "MPa"), ("stress_top_bars", 13.75, "MPa"),
            ("stress_bottom_bars", -10.27, "MPa"), ("stress_bottom_fibre", -2.20, "MPa"),
            ("wk", 0.00, "mm", "'Abertura de fisura, wk = 0.00 mm'")]),
        "note": "Uncracked (gross) section; sign + = compression. Section drawn web up / ledges down (inverted T 50x55+15x30+15x30) with 5 top bars and 7 bottom bars."}


def deflection_history_image120():
    return V("image120.png: same points (28,0.00) (28,0.15) (90,0.21) (90,0.23) (120,0.24) (120,0.27) (360,0.34) (360,1.01) (...,1.53)",
             "-", "P586 image image120.png")


# ------------------------------------------------------------------------------------------------
# APÉNDICE 1 §2 beam drawings (images 203-212)
# ------------------------------------------------------------------------------------------------
def drawings():
    return {
        "note": "Bar schedules read from the CYPE beam drawings (Apéndice 1 §2, images 203-212). Lengths in cm; hook/anchor legs "
                "in cm; I = izquierda, D = derecha, e = estribo, r = rama; 'M. Alas' = bars in the ledges. Upper/lower group = "
                "position of the label in the drawing (upper group = top and web-side bars, lower group = bottom and ledge bars).",
        "Pórtico 3": {"src": "P1613 image image204.png", "confidence": "high",
                      "upper": ["5Ø20 (474) legs 29 / 25", "D1Ø20 (490) legs 17 / 17, marks 18 / 18"],
                      "stirrups": "37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40",
                      "lower": ["D1Ø20 (490) legs 17 / 17, marks 18 / 18", "5Ø20 (471) legs 25 / 25", "D2Ø10 M. Alas (421)"],
                      "section": "80x55+15x30",
                      "envelope_labels": {"My_min": -318.80, "My_max": 275.15, "My_end": -8.28, "Vz": [70.73, -104.85, 333.92, -165.91]}},
        "Pórtico 4": {"src": "P1619 image image205.png", "confidence": "high",
                      "upper": ["I1Ø10+D1Ø10 (470) legs 17 / 17, 8 / 8", "5Ø20 (471) legs 25 / 25"],
                      "stirrups": "37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40",
                      "lower": ["I1Ø20+D1Ø20 (490) legs 17 / 17, marks 18 / 18", "5Ø20 (471) legs 25 / 25", "I1Ø10+D1Ø10 M. Alas (421)"],
                      "section": "50x55+15x30+15x30",
                      "envelope_labels": {"My_min": -273.71, "My_max": 294.60, "My_end": -25.04, "Vz": [-67.98, 471.19, -333.66]}},
        "Pórtico 5": {"src": "P1625 image image206.png", "confidence": "high", "same_bars_as": "Pórtico 4",
                      "envelope_labels": {"My_min": -312.87, "My_max": 270.09, "My_end": -22.53, "Vz": [60.99, -131.33, 440.82, -298.84]}},
        "Pórtico 6": {"src": "P1631 image image207.png", "confidence": "high", "same_bars_as": "Pórtico 4",
                      "envelope_labels": {"My_min": -264.00, "My_max": 275.49, "My_end": -23.03, "Vz": [-64.31, 438.61, -306.21]}},
        "Pórtico 7": {"src": "P1637 image image208.png", "confidence": "high", "same_bars_as": "Pórtico 4",
                      "envelope_labels": {"My_min": -303.83, "My_max": 262.67, "My_end": -22.53, "Vz": [60.99, -131.33, 434.91, -298.84]}},
        "Pórtico 8": {"src": "P1643 image image209.png", "confidence": "high", "same_bars_as": "Pórtico 4",
                      "envelope_labels": {"My_min": -255.61, "My_max": 291.09, "My_end": -25.04, "Vz": [-67.98, 464.06, -333.66]}},
        "Pórtico 9": {"src": "P1649 image image210.png", "confidence": "high",
                      "upper": ["5Ø20 (472) legs 27 / 25", "I1Ø20 (490) legs 17 / 17, marks 18 / 18"],
                      "stirrups": "37x{(1eØ10+1rØ10)+(1eØ10)} /10 over 369, plus 40",
                      "lower": ["I1Ø20 (490) legs 17 / 17, marks 18 / 18", "5Ø20 (471) legs 25 / 25", "I2Ø10 M. Alas (421)"],
                      "section": "80x55+15x30",
                      "envelope_labels": {"My_min": -291.23, "My_max": 247.61, "My_end": -8.28, "Vz": [70.73, -104.85, 315.96, -165.91]}},
        "Pórtico 1": {"src": "P1607 image image203.png", "confidence": "low (small raster labels)",
                      "section": "25x30",
                      "top_bars": ["2Ø16 (450)", "2Ø16 (745)", "2Ø16 (800)", "2Ø16 (755)", "2Ø16 (885)", "2Ø16 (600)?", "2Ø16 (485)"],
                      "top_laps": [115.9, 116.4, 116.1, 115.2, 115.6, 117.1],
                      "bottom_bars": ["2Ø16 (765)", "2Ø16 (735)", "2Ø16 (735)", "2Ø16 (715)", "2Ø16 (740)", "2Ø16 (765)"],
                      "bottom_laps": [81.5, 81.5, 82, 82, "8?.2"],
                      "stirrups": "261x1eØ8 /15 over 3914",
                      "envelope_labels": {"support_My": {"P9": -16.68, "P10": -32.84, "P11": -27.93, "P12": -28.85, "P19": -27.93, "P21": -32.84, "P20": -16.83},
                                          "span_My_max": [25.61, 20.22, 21.05, 21.05, 20.23, 25.61]}},
        "Pórtico 10": {"src": "P1655 image image211.png + P1660 image image212.png", "confidence": "medium",
                       "section": "25x30",
                       "top_bars": ["2Ø16 (460) leg 12", "2Ø16 (820)", "2Ø16 (690)", "2Ø16 (835)", "2Ø16 (695)", "2Ø16 (810)", "2Ø16 (435) leg 12"],
                       "top_laps": [119.3, 117.5, 115.2, 114.9, 115, 115.6],
                       "bottom_bars": ["2Ø16 (765) leg 12", "2Ø16 (725)", "2Ø16 (745)", "2Ø16 (725)", "2Ø16 (730)", "2Ø16 (765) leg 12"],
                       "bottom_laps": [81.8, 80.7, 80.7, 81.6, 82.7],
                       "stirrups": "128x1eØ8 /15 over 1910 (P2-P8, plus 40 / 20) and 128x1eØ8 /15 over 1910 (P8-P18, plus 20 / 40)",
                       "envelope_labels": {"support_My": {"P2": -17.86, "P4": -31.36, "P6": -27.81, "P8": -28.34, "P14": -27.81, "P17": -31.40, "P18": -17.86},
                                           "span_My_max": {"P2-P4": 22.49, "P4-P6": 18.94, "P6-P8": 19.38, "P8-P14": 19.38, "P14-P17": 18.94, "P17-P18": 22.48}}},
    }


# ------------------------------------------------------------------------------------------------
# SLAB (alveoplacas, body P593-P603)
# ------------------------------------------------------------------------------------------------
def slab_envelope_image121():
    return {
        "src": "P593 image image121.png", "confidence": "high (zoomed)",
        "span_M_pos": {"PL1": 100.08, "PL2": 70.79, "PL3": 77.06, "PL4": 77.06, "PL5": 70.79, "PL6": 100.08},
        "support_M_neg_by_axis": {"axis2 (P3-P4, Pórtico 4)": -100.32, "axis3 (P5-P6)": -74.16, "axis4 (P7-P8)": -82.07,
                                  "axis5 (P13-P14)": -74.16, "axis6 (P15-P17)": -100.32, "axis1/axis7": "M = -0.00 kN*m tooltip at P2"},
        "span_V_start_end": {"PL1": [71.90, -105.52], "PL2": [93.18, -84.87], "PL3": [87.77, -90.28], "PL4": [90.28, -87.77],
                             "PL5": [84.87, -93.18], "PL6": [105.52, -71.90]},
        "negative_bars_labels": {"axis1": "Ø8/13 (165) = (150) + 15", "axis2": "Ø12/13 (390) = (197)+(193)", "axis3": "Ø10/12 (325) = (162)+(163)",
                                 "axis4": "Ø10/12 (325) = (162)+(163)", "axis5": "Ø10/12 (325) = (162)+(163)",
                                 "axis6": "Ø1?/13 (390) = (192)+(198) (partly hidden; Ø12 by symmetry — INFERENCE)", "axis7": "Ø8/13 (165) = (150) + 15"},
        "units": "kN·m/m and kN/m (per 1 m band, §1.10 'Esfuerzos por bandas de 1 m')"}


def plate_image122():
    return {
        "src": "P595 image image122.png", "title": "DEFINICIÓN ALVEOPLACA / A. POSITIVA FORJADO (POR M)",
        "referencia": "P25-1", "M_ult": 158.7, "M_fis": 55.9, "rig_tot": 63550, "rig_fis": 63550, "M_ser_1": 71.9, "M_ser_2": 104.4,
        "units": "kN·m/m ; rigidez kN·m²/m"}


def plan_image123():
    return {"src": "P600 image image123.png", "confidence": "medium",
            "axis1_P1_P2_B0": "17Ø8/13 (165), segment (150), distribution width 211",
            "axis2_P3_P4_B1": "17Ø12/13 (3?0) segments (197) + (163) -> 360 (image121 prints (390) = 197+193: CONFLICT)",
            "axis3_P5_P6_B2": "18Ø10/12 (325) segments (162) + (163)",
            "plates": "PL1, PL2, PL3 = P25-1, h=25+5; edge beams 25x30",
            "note": "image cropped after PL3 (axes 4-7 not shown)"}


def table_image124():
    return {"src": "P603 image image124.png", "title": "Fl. negativa forjado (por m)",
            "columns": ["DIAM.", "SEPAR.", "M.SEC.T", "M.SEC.M", "M.fis."],
            "rows": [["Ø8", 130, 45.3, 45.3, 40.4], ["Ø8", 120, 59.2, 59.2, 40.4], ["Ø10", 130, 70.3, 70.3, 40.4],
                     ["Ø10", 120, 87.1, 87.1, 40.4], ["Ø12", 130, 100.5, 100.4, 40.4], ["Ø16", 200, 118.4, 118.3, 40.4]]}


# ------------------------------------------------------------------------------------------------
def listar(d):
    """Every block / value of a built reference whose src is an image: [(json path, src, value or '(block)')]."""
    out = []

    def walk(o, path):
        if isinstance(o, dict):
            src = o.get("src")
            if isinstance(src, str) and " image " in src:
                out.append((path, src, o["value"] if "value" in o else "(block)"))
                if "value" in o:
                    return
            for k, v in o.items():
                walk(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(d, "")
    return out


if __name__ == "__main__":
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ref", "cype_design_reference.json")
    rows = listar(json.load(open(sys.argv[1] if len(sys.argv) > 1 else ref, encoding="utf-8")))
    for p, s, v in rows:
        print(f"{s:45s} {p}  =  {v}")
    print(len(rows), "entries")
