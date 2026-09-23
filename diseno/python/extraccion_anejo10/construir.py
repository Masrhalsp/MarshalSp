"""Build diseno/ref/cype_design_reference.json from the Anejo 10 text dumps (step 2 of the extraction).

Purpose
    Collect every CYPECAD design value of the Muelle de Trasmallo (piles P3 head/base checks,
    transverse beam P3-P4 checks, Apéndice 1 listings of all piles and beams, materials, partial
    factors and combinations, slab and viga cantil) into one JSON where each value carries its
    source ("src") in the document.  Values are PARSED from the dumps (tablas.py); the only
    hand-entered data are
      * the values read by eye from figures           -> datos_imagenes.py (image id + anchor paragraph)
      * explanatory notes, INFERENCE notes, caveats C1-C16 and the 'not in document' list, written
        after reading the document and checked by an independent re-parse (validar.py); they are
        plain text in this file (caveats(), not_in_doc(), mapping(), inferred(), the 'note' fields).
    The corrections of the independent check (descriptions of values printed under an equation
    image, verbatim quotes, viga cantil arithmetic, image97 labels, caveats C1/C15/C16) are part of
    this code, so the output equals the committed JSON byte for byte.

Input
    textos = {"trasmallo_body.txt": ..., "trasmallo_app.txt": ..., "trasmallo_pre.txt": ...}
    (volcado.volcado_rango for the ranges volcado.RANGOS).

Output
    construir(textos) -> dict;  escribir_json(d, path) writes it (UTF-8, indent 2, no final newline).

Run
    python3 diseno/python/extraccion_anejo10/extraer.py          (whole pipeline)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tablas import load_text, Tab, V, num, split_vu, nested_kv, statement, cells_of  # noqa: E402
import datos_imagenes as DI  # noqa: E402

TABLES = {}
PARAS = {}


def cargar(textos):
    """Parse the three dumps into the module tables (body + appendix tables; body + appendix + project paragraphs)."""
    _, BT, BP = load_text(textos["trasmallo_body.txt"])
    _, AT, AP = load_text(textos["trasmallo_app.txt"])
    _, PT, PP = load_text(textos["trasmallo_pre.txt"])
    BP.update(PP)
    TABLES.clear()
    TABLES.update({**BT, **AT})
    PARAS.clear()
    PARAS.update({**BP, **AP})


def T(tid):
    return Tab(tid, TABLES[tid])


def P(n):
    return PARAS[n]


def PV(n, value, unit="-", note=None):
    return V(value, unit, f"P{n}", note)


# ----------------------------------------------------------------------------------------
# generic sub-builders
# ----------------------------------------------------------------------------------------
def datos_table(tid):
    """'Datos del pilar' / 'Datos de la viga' nested table -> {key: V}."""
    out = {}
    for row in TABLES[tid]:
        for cell in re.findall(r"\{[^{}]*\}", row):
            if True:
                for k, v in nested_kv(cell):
                    val, unit = split_vu(v)
                    if not isinstance(val, (int, float)):
                        val, unit = v, "-"
                    if isinstance(val, (int, float)) and unit.startswith("%"):
                        unit = "%"
                    out[k] = V(val, unit, f"{tid}: {k}", printed=v.split()[0] if isinstance(val, float) else None)
    return out


def pick(seg, spec):
    """spec: list of (key, sym[, k])."""
    out = {}
    for it in spec:
        key, sym = it[0], it[1]
        k = it[2] if len(it) > 2 else 1
        out[key] = seg.get(sym, k)
    return out


def bars_table(tid):
    rows = TABLES[tid]
    assert rows[0].startswith("Barra"), rows[0]
    out = []
    for r in rows[1:]:
        c = cells_of(r)
        if len(c) < 6 or not c[0].isdigit():
            continue
        out.append({"bar": int(c[0]), "designation": c[1], "x_mm": num(c[2]), "y_mm": num(c[3]),
                    "sigma_s_MPa": num(c[4]), "eps": num(c[5]), "src": f"{tid}: Barra {c[0]}"})
    return {"columns": {"x_mm": "Coord. X (mm)", "y_mm": "Coord. Y (mm)", "sigma_s_MPa": "σs (MPa), + compression",
                        "eps": "ε, + compression"}, "rows": out}


def resultants_table(tid):
    out = {}
    for r in TABLES[tid][1:]:
        c = cells_of(r)
        if len(c) == 4 and c[0]:
            out[c[0]] = {"resultant": V(num(c[1]), "kN", f"{tid}: {c[0]} Resultante"),
                         "e_x": V(num(c[2]), "mm", f"{tid}: {c[0]} e.x"),
                         "e_y": V(num(c[3]), "mm", f"{tid}: {c[0]} e.y")}
    return out


def equilibrium(bars_tid, res_tid, kv_tid, para, img, img_labels):
    kv = T(kv_tid).all()
    return {"title": V(P(para), "-", f"P{para}"),
            "bars": bars_table(bars_tid),
            "resultants": resultants_table(res_tid),
            "summary_values": kv.dump(),
            "diagram_labels": img_labels}


def materials_hyp(t_conc, t_steel):
    c = T(t_conc).all()
    s = T(t_steel).all()
    return {"concrete": pick(c, [("eps_cu2", "εcu2"), ("eps_c2", "εc2"), ("fcd", "fcd"), ("alpha_cc", "αcc"),
                                 ("fck", "fck"), ("gamma_c", "γc")]),
            "concrete_diagram": V("El diagrama de cálculo tensión-deformación del hormigón es del tipo parábola rectángulo. No se considera la resistencia del hormigón a tracción.", "-", "text row closing the preceding N-M table (P245/P300/P369 table)"),
            "steel": pick(s, [("eps_su", "εsu"), ("fyd", "fyd"), ("fyk", "fyk"), ("gamma_s", "γs")])}


# ----------------------------------------------------------------------------------------
# PILES
# ----------------------------------------------------------------------------------------
def pile_nm_block(tid_eta, tid_main, tid_conc, tid_steel, eq):
    te = T(tid_eta).all()
    stt = statement(te, 1)
    tm = T(tid_main)
    s1 = tm.seg("Comprobación de resistencia de la sección", "Comprobación del estado limite de inestabilidad")
    s2 = tm.seg("Comprobación del estado limite de inestabilidad", "Cálculo de la capacidad resistente")
    blk = {
        "position": stt["position"], "combination": stt["combination"],
        "eta_1_section_resistance": te.get("η", 1), "eta_2_instability": te.get("η", 2),
        "eta_formula_seen_in_render": "η1 = sqrt(NEd²+MEd,x²+MEd,y²)/sqrt(NRd²+MRd,x²+MRd,y²) ≤ 1 ; η2 same with NSd, MSd (second order)",
        "section_resistance_first_order": {
            **pick(s1, [("NEd", "NEd"), ("MEd_x", "MEd,x"), ("MEd_y", "MEd,y"), ("NRd", "NRd"), ("MRd_x", "MRd,x"),
                        ("MRd_y", "MRd,y"), ("ee_x", "ee,x"), ("ee_y", "ee,y")]),
            "axis_x": pick(s1.seg("En el eje x:", "En el eje y:"), [("emin", "emin"), ("h", "h"), ("e0", "e0"), ("Md", "Md"), ("Nd", "Nd")]),
            "axis_y": pick(s1.seg("En el eje y:"), [("emin", "emin"), ("h", "h"), ("e0", "e0"), ("Md", "Md"), ("Nd", "Nd")]),
        },
        "instability_second_order": {
            **pick(s2.seg(None, "En el eje x:"), [("NSd", "NSd"), ("MSd_x", "MSd,x"), ("MSd_y", "MSd,y"), ("NRd", "NRd"),
                                                   ("MRd_x", "MRd,x"), ("MRd_y", "MRd,y")]),
        },
        "all_printed_values": tm.all().dump(),
        "material_hypotheses": materials_hyp(tid_conc, tid_steel),
        "equilibrium_at_ultimate": eq[0],
        "equilibrium_at_design_forces": eq[1],
    }
    spec = [("lambda", "λ"), ("l0", "l0"), ("i_c", "ic"), ("Ac", "Ac"), ("I", "I"), ("lambda_inf_lim", "λinf"),
            ("A", "A"), ("phi_ef_for_A", "ϕef"), ("B", "B"), ("omega", "ω"), ("As", "As"), ("fyd", "fyd"), ("fcd", "fcd"),
            ("C", "C"), ("n", "n"), ("NEd", "NEd"), ("NSd", "NSd"), ("MSd", "MSd"), ("e_tot", "etot"), ("e_e", "ee"),
            ("e_i", "ei"), ("theta_i", "θi"), ("theta_0", "θ0"), ("alpha_h", "αh"), ("l_height", "l"), ("alpha_m", "αm"),
            ("e2", "e2"), ("c_curvature", "c"), ("one_over_r", "1/r"), ("K_r", "Kr"), ("n_u", "nu"), ("omega_Kr", "ω", 2),
            ("n_Kr", "n", 2), ("n_bal", "nbal"), ("K_phi", "Kϕ"), ("beta", "β"), ("phi_ef_for_Kphi", "ϕef", 2),
            ("one_over_r0", "1/r0"), ("eps_yd", "εyd"), ("d", "d")]
    blk["instability_second_order"]["axis_x"] = pick(s2.seg("En el eje x:", "En el eje y:"), spec)
    blk["instability_second_order"]["axis_y"] = pick(s2.seg("En el eje y:"), spec)
    stx = [t for i, t in tm.texts if t.startswith("Los efectos de segundo orden")]
    blk["instability_second_order"]["statement_axes_x_and_y"] = V(stx[0], "-", f"{tid_main}: text row under 'En el eje x:' and 'En el eje y:'")
    blk["instability_second_order"]["formulas_seen_in_render"] = [
        "λ = l0/ic = l0/sqrt(I/Ac)", "λlim = 20·A·B·C/sqrt(n)  (label printed 'λinf')", "A = 1/(1+0.2·ϕef)",
        "B = sqrt(1+2·ω) ('Formulación UNE-EN 1992-1-1:2013')", "ω = As·fyd/(Ac·fcd)", "n = NEd/(Ac·fcd)",
        "NSd = NEd ; MSd = NEd·etot ; etot = ee + ei + e2 (partly legible)", "ei = θi·l0/2 (partly legible)",
        "θi = θ0·αh·αm", "e2 = (1/r)·l0²/c (partly legible)", "1/r = Kr·Kϕ·1/r0", "1/r0 = εyd/(0.45·d)",
        "Kr, Kϕ per A19.5.8.8.3 (nu = 1+ω, nbal = 0.4, Kϕ = 1+β·ϕef)"]
    return blk


def pile_shear_block(tid_title, tid):
    t = T(tid)
    top = t.seg("Se debe satisfacer:", "Esfuerzo cortante de agotamiento por compresión oblicua en el alma")
    blk = {"title": V(TABLES[tid_title][0], "-", tid_title)}
    st = statement(t.all(), 1)
    blk["position_eta1"] = st["position"]
    blk["combination_eta1"] = st["combination"]
    blk["eta_1_VRdmax"] = top.get("η", 1)
    blk["VEd_x_eta1"] = top.get("VEd,x", 1)
    blk["VEd_y_eta1"] = top.get("VEd,y", 1)
    blk["VRd_max"] = top.get("VRd,max", 1)
    try:
        blk["eta_2_VRd"] = top.get("η", 2)
        blk["VEd_x_eta2"] = top.get("VEd,x", 2)
        blk["VEd_y_eta2"] = top.get("VEd,y", 2)
        blk["VRd_s_printed"] = top.get("VRd,s", 1, note="Printed symbol 'VRd,s' but the formula (A19.6.2.2(1), members "
                                       "WITHOUT shear reinforcement) is VRd,c: ties are not counted.")
        st2 = statement(t.all(), 2)
        blk["position_eta2"] = st2["position"]
        blk["combination_eta2"] = st2["combination"]
    except (KeyError, IndexError):
        pass
    blk["eta_formula_seen_in_render"] = "η1 = sqrt((VEd,x/VRd,max,Vx)²+(VEd,y/VRd,max,Vy)²) ≤ 1 ; η2 = sqrt((VEd,x/VRd,s,Vx)²+(VEd,y/VRd,s,Vy)²) ≤ 1"
    strut = [("VRd_max", "VRd,max"), ("alpha_cw", "αcw"), ("sigma_cp", "σcp"), ("NEd", "NEd"), ("As_comp", "A's"),
             ("Ac", "Ac"), ("fyd", "fyd"), ("fcd", "fcd"), ("bw", "bw"), ("z", "z"), ("nu1", "ν1"), ("alpha", "α"), ("theta", "θ")]
    comp = t.seg("Esfuerzo cortante de agotamiento por compresión oblicua en el alma",
                 "Esfuerzo cortante de agotamiento por tracción en el alma" if any(
                     "tracción en el alma" in r for r in TABLES[tid]) else None)
    blk["compression_strut_dir_X"] = pick(comp.seg("Cortante en la dirección X:", "Cortante en la dirección Y:"), strut)
    blk["compression_strut_dir_Y"] = pick(comp.seg("Cortante en la dirección Y:"), strut)
    blk["compression_strut_formulas_seen_in_render"] = [
        "VRd,max = αcw·bw·z·ν1·fcd·(cotθ+cotα)/(1+cot²θ)", "σcp = (NEd - A's·fyd)/Ac", "αcw = 1 for σcp ≤ 0 (printed 1.000)"]
    if any("tracción en el alma" in r for r in TABLES[tid]):
        ten = t.seg("Esfuerzo cortante de agotamiento por tracción en el alma")
        vrc = [("VRd_c_printed_VRd_s", "VRd,s", 1), ("VRd_c_min_printed_VRd_s", "VRd,s", 2), ("CRd_c", "CRd,c"),
               ("gamma_c", "γc"), ("k", "k"), ("rho_l", "ρl"), ("Asl", "Asl"), ("fck", "fck"), ("sigma_cp", "σcp"),
               ("NEd", "NEd"), ("Ac", "Ac"), ("fcd", "fcd"), ("bw", "bw"), ("d", "d"), ("v_min", "Vmin")]
        blk["concrete_no_shear_reinf_dir_X"] = pick(ten.seg("Cortante en la dirección X:", "Cortante en la dirección Y:"), vrc)
        blk["concrete_no_shear_reinf_dir_Y"] = pick(ten.seg("Cortante en la dirección Y:"), vrc)
        blk["concrete_formulas_seen_in_render"] = [
            "VRd,c = [CRd,c·k·(100·ρl·fck)^(1/3) + 0.15·σcp]·bw·d", "VRd,c,min = (vmin + 0.15·σcp)·bw·d",
            "CRd,c = 0.18/γc", "k = 1 + sqrt(200/d) ≤ 2", "ρl = Asl/(bw·d) ≤ 0.02", "σcp = NEd/Ac < 0.2·fcd",
            "vmin = 0.035·k^(3/2)·fck^(1/2)"]
    blk["all_printed_values"] = t.all().dump()
    return blk


def pile_detailing(t223, t225, t227):
    a = T(t223).all()
    b = T(t225)
    c = T(t227)
    return {
        "column_definition": {"checks": a.checks(), **pick(a, [("h", "h"), ("b", "b")])},
        "longitudinal": {"checks": b.all().checks(),
                         **pick(b.seg(None, "Las barras longitudinales"), [("s_min", "smin"), ("s1", "s1"), ("s2", "s2"), ("s3", "s3"),
                                                                           ("phi_max", "Ømax"), ("d_g", "dg")]),
                         "phi_min": b.seg("Las barras longitudinales").get("Ømin")},
        "ties": {"checks": c.all().checks(),
                 **pick(c.seg(None, "La separación de la armadura transversal"),
                        [("s_min", "smin"), ("s1", "s1"), ("s2", "s2"), ("s3", "s3"), ("phi_max_transv", "Ømax"), ("d_g", "dg")]),
                 "spacing_limit": pick(c.seg("La separación de la armadura transversal", "El diámetro de la armadura transversal"),
                                       [("s_cl_max", "scl,max"), ("s1", "s1"), ("s2", "s2"), ("s3", "s3"), ("phi_min_long", "Ømin")]),
                 "diameter": pick(c.seg("El diámetro de la armadura transversal"), [("phi_max_long", "Ømax")])},
        "formulas_note": "The s1/s2/s3 and scl,max formula images (WMF) do not render legibly; only 'φt ≥ 1/4·φmax' is legible. "
                         "Arithmetic observations (INFERENCE, not printed): clear-spacing smin = max(s1, s2, s3) with s1 = Ø (25 bars / 10 ties), "
                         "s2 = dg + 5 = 25, s3 = 20 mm; for scl,max = min(s1, s2, s3): 375 = 15·Ømin(25), 400 = b = 400 mm, 300 = 12·Ømin or a "
                         "fixed 300 mm (cannot be decided from the document).",
    }


def pile_minmax(tid):
    t = T(tid)
    s1 = t.seg(None, "El área de la armadura longitudinal As no debería superar")
    s2 = t.seg("El área de la armadura longitudinal As no debería superar", "El área total de la armadura longitudinal A's")
    s3 = t.seg("El área total de la armadura longitudinal A's")
    return {"checks": t.all().checks(),
            "As_min_total": pick(s1, [("As", "As"), ("As_min", "As,min"), ("Ac", "Ac")]),
            "As_max": {**pick(s2, [("As", "As"), ("As_max", "As,max"), ("Ac", "Ac"), ("fyd", "fyd"), ("fcd", "fcd")]),
                       "formula_seen_in_render": "As,max = (fcd/fyd)·Ac  (122.67 = 33.33/434.78·1600)"},
            "As_min_compression": {**pick(s3, [("As_comp", "A's"), ("As_min", "As,min"), ("NEd", "NEd"), ("fyd", "fyd")]),
                                   "note": "As,min formula image not legible; 1.55 cm² ≈ 0.10·NEd/fyd = 0.1·673.9/434.78 (EC2 9.5.2(2))"},
            "As_min_total_note": "6.40 cm² = 0.004·Ac (Ac = 1600 cm²); formula image not legible"}


def build_piles():
    piles = {}
    # --- general ---------------------------------------------------------------------------
    sup = []
    for r in TABLES["P1549 table"][1:]:
        c = cells_of(r)
        m = re.match(r"\(\s*([-\d.]+),\s*([-\d.]+)\)", c[1])
        sup.append({"ref": c[0], "x_m": float(m.group(1)), "y_m": float(m.group(2)), "GI_GF": c[2], "vinculacion": c[3],
                    "ang_deg": num(c[4]), "punto_fijo": c[5], "canto_apoyo": num(c[6]) if c[6] else None,
                    "src": f"P1549 table: {c[0]}"})
    coef = {}
    for tid in ("P1554 table", "P1557 table"):
        rows = TABLES[tid]
        c = cells_of(rows[3])
        coef[rows[0]] = {"planta": num(c[0]), "dimensiones_cm": c[1], "empotramiento_cabeza": num(c[2]),
                         "empotramiento_pie": num(c[3]), "pandeo_X": num(c[4]), "pandeo_Y": num(c[5]),
                         "rigidez_axil": num(c[6]), "src": f"{tid}: row 1"}
    chs = TABLES["P1560 table"]
    coef[chs[0]] = {"planta": num(cells_of(chs[3])[0]), "dimensiones": cells_of(chs[3])[1], "src": "P1560 table: row 1"}
    piles["general"] = {
        "materials_text": {"concrete": PV(120, "HA-50/F/12/XS3"), "steel": PV(121, "B500 SD"),
                           "cover": PV(122, 5, "cm", "'Recubrimiento ... para una vida útil de 50 años que son 5 cm'")},
        "cype_supports_1_8_1": sup,
        "coefficients_1_9": coef,
        "section_sketch": DI.section_sketch_image16(),
        "reinforcement_summary": {
            "bars": V("12Ø25", "-", "P220 table: Esquina/Cara X/Cara Y", "composed: Esquina 4Ø25 + Cara X 4Ø25 + Cara Y 4Ø25"),
            "As_total": V(58.91, "cm²", "P232 table: As (occurrence 1)"),
            "ties_shaft": V("2eØ10+1eØ10", "-", "P220 table: Estribos"),
            "tie_spacing": V(15, "cm", "P220 table: Separación"),
            "ties_arranque": V("1eØ8", "-", "P281 table: Estribos"),
            "cuantia": V(3.68, "%", "P220 table: Cuantía"),
        },
        "model_mapping": {
            "note": "From sap2000/model/trasmallo.py: axis a = 1..7 at X = 6.5·(a-1); pile_sea (Y=0.00) = "
                    "[P1,P3,P5,P7,P13,P15,P16]; pile_land (Y=3.45) = [P2,P4,P6,P8,P14,P17,P18]; bollard/edge points "
                    "(Y=-0.45 CYPE punto fijo, Y=-0.375 model) = [P9,P10,P11,P12,P19,P21,P20]. Frame names PIL_<CYPE name>.",
            "by_axis": [{"axis": a, "X_m": 6.5 * (a - 1), "pile_sea": s, "pile_land": l, "edge_point": e}
                        for a, (s, l, e) in enumerate(zip(["P1", "P3", "P5", "P7", "P13", "P15", "P16"],
                                                          ["P2", "P4", "P6", "P8", "P14", "P17", "P18"],
                                                          ["P9", "P10", "P11", "P12", "P19", "P21", "P20"]), start=1)],
        },
    }
    # --- section 1: FORJADO 1 --------------------------------------------------------------
    img84, img88 = DI.equilibrium_pile("image84.png"), DI.equilibrium_pile("image88.png")
    img95, img96 = DI.equilibrium_pile("image95.png"), DI.equilibrium_pile("image96.png")
    cap50, cap94 = DI.capacity_pile("image50.png"), DI.capacity_pile("image94.png")
    s1 = {
        "heading": PV(218, P(218)),
        "identification": {"note": "Pile not named in the body; N/M values equal Apéndice 1 §3.5 P3 'Cabeza' row "
                                    "'G, Q, V' (620.1 / 353.5 / -69.0) -> this is pile P3, head section. Heading says 0 - 7.00 M but "
                                    "'Datos del pilar' prints Tramo 0.000/7.250 m and the listing 'Forjado 1 (0 - 7.25 m)'.",
                            "src": "P218 + P1714 table: P3 Cabeza G, Q, V"},
        "datos_del_pilar": datos_table("P220 table"),
        "detailing": pile_detailing("P223 table", "P225 table", "P227 table"),
        "min_max_reinforcement": pile_minmax("P232 table"),
        "shear": pile_shear_block("P236 table", "P237 table"),
        "normal_forces": {"title": V(TABLES["P241 table"][0], "-", "P241 table"),
                          **pile_nm_block("P242 table", "P245 table", "P249 table", "P253 table", [
                              equilibrium("P257 table", "P260 table", "P261 table", 256, "image84.png", img84),
                              equilibrium("P265 table", "P268 table", "P269 table", 264, "image88.png", img88)]),
                          "capacity_diagram_labels": cap50},
        "cracking": PV(276, P(276)),
        "psi_table_image": DI.psi_table_image92(),
    }
    s2 = {
        "heading": PV(279, P(279)),
        "identification": {"note": "Foundation start ('Arranque') of P3: Datos del pilar Tramo -0.420/0.000 m, altura libre 0.00 m, "
                                    "estribos 1eØ8; NSd/MSd equal Apéndice 1 §3.5 P3 'Cimentación / Arranque' (655.6 / -352.1 / 71.3)",
                            "src": "P281 table + P1714 table: P3 Arranque"},
        "datos_del_pilar": datos_table("P281 table"),
        "detailing": PV(285, P(285), note="Disposiciones: 'La comprobación no procede'"),
        "min_max_reinforcement": PV(289, P(289), note="Armadura mínima y máxima: 'La comprobación no procede'"),
        "shear": pile_shear_block("P291 table", "P292 table"),
        "normal_forces": {"title": V(TABLES["P296 table"][0], "-", "P296 table"),
                          **pile_nm_block("P297 table", "P300 table", "P304 table", "P308 table", [
                              equilibrium("P312 table", "P315 table", "P316 table", 311, "image95.png", img95),
                              equilibrium("P320 table", "P323 table", "P324 table", 319, "image96.png", img96)]),
                          "capacity_diagram_labels": cap94},
        "cracking": PV(330, P(330)),
    }
    s2["normal_forces"]["position"]["note"] = ("the P297 statement names no position ('se producen para la combinación ...'); "
                                               "the section is the foundation start (Arranque), see identification")
    piles["section_1_forjado_cabeza"] = s1
    piles["section_2_empotramiento_arranque"] = s2
    piles["appendix_1_section_3"] = build_pile_appendix()
    return piles


def build_pile_appendix():
    out = {}
    # 3.2 armado
    rows = []
    cur = None
    for r in TABLES["P1692 table"][5:]:
        c = cells_of(r)
        if len(c) < 12:
            continue
        if c[0]:
            cur = c[0]
        rows.append({"pilar": cur, "planta": c[1], "dim_cm": c[2], "tramo_m": c[3], "esquina": c[4], "cara_X": c[5],
                     "cara_Y": c[6], "cuantia_pct": num(c[7]), "estribos": c[8], "separacion_cm": num(c[9]),
                     "aprov_pct": num(c[10]), "estado": c[11], "src": f"P1692 table: {cur} {c[1]}"})
    out["armado_pilares_3_2"] = {"title": "Armado de pilares (Hormigón: HA-50, Yc=1.5)", "src": "P1692 table",
                                 "note": "(1) e = estribo, r = rama", "rows": rows}
    # 3.3 esfuerzos por hipótesis
    rows = []
    cur = None
    cols = ["N", "Mx", "My", "Qx", "Qy", "T"]
    for r in TABLES["P1702 table"][2:]:
        c = cells_of(r)
        if len(c) < 17:
            continue
        if c[0]:
            cur = c[0]
        rows.append({"pilar": cur, "hipotesis": c[4],
                     "base": dict(zip(cols, [num(x) for x in c[5:11]])),
                     "cabeza": dict(zip(cols, [num(x) for x in c[11:17]])),
                     "src": f"P1702 table: {cur} {c[4]}"})
    out["esfuerzos_por_hipotesis_3_3"] = {
        "src": "P1702 table", "units": "N, Q in kN; M, T in kN·m; local pile axes (= global, Ang 0)",
        "note": "Tramo 0.00/6.70 m (Base z=0, Cabeza z=6.70). 'Los esfuerzos están referidos a ejes locales del pilar' (P1701). "
                "§3.4 'Arranques' (P1708 table) repeats the Base values. Sign/axis conventions: see sap2000/ref/cype_reference.json 'conventions'.",
        "rows": rows}
    # 3.5 pésimos
    rows = []
    cur = cur_t = cur_pos = cur_dim = None
    for r in TABLES["P1714 table"][3:]:
        c = cells_of(r)
        if len(c) < 13:
            continue
        cur = c[0] or cur
        cur_t = c[1] or cur_t
        cur_pos = c[3] or cur_pos
        cur_dim = c[2] or cur_dim
        rows.append({"pilar": cur, "tramo": cur_t, "dim_cm": cur_dim, "posicion": cur_pos, "naturaleza": c[4],
                     "N_kN": num(c[5]), "Mxx_kNm": num(c[6]), "Myy_kNm": num(c[7]), "Qx_kN": num(c[8]), "Qy_kN": num(c[9]),
                     "pesima": c[10], "aprov_pct": num(c[11]), "estado": c[12],
                     "src": f"P1714 table: {cur} {cur_t} {cur_pos} {c[4]}"})
    out["pesimos_3_5"] = {"src": "P1714 table",
                          "note": "N > 0 compression. 'N,M' rows include second-order amplification (A19.5.8.8). Naturaleza: G permanent, Q use, V 'viento' (= Tiro bolardo).",
                          "rows": rows}
    # 3.6 medición
    c = cells_of(TABLES["P1719 table"][4])
    out["medicion_3_6"] = {"piles": c[0], "dim_cm": c[1],
                           "encofrado": V(num(c[2]), "m²", "P1719 table: Encofrado"),
                           "hormigon_HA50": V(num(c[3]), "m³", "P1719 table: Hormigón"),
                           "long_Ø25": V(num(c[4]), "kg", "P1719 table: Longitudinal Ø25"),
                           "estribos_Ø10": V(num(c[5]), "kg", "P1719 table: Estribos Ø10"),
                           "estribos_Ø8": V(num(c[6]), "kg", "P1719 table: Estribos Ø8"),
                           "total_plus_10pct": V(num(c[7]), "kg", "P1719 table: Total +10 %"),
                           "cuantia": V(num(c[8]), "kg/m³", "P1719 table: Cuantía")}
    # 4.2 per-pile ELU checks
    per = {}
    for tid in sorted([t for t in TABLES if t.startswith("P17") or t.startswith("P18")],
                      key=lambda s: int(s[1:].split()[0])):
        rows_t = TABLES[tid]
        if not rows_t or rows_t[0] != "Sección de hormigón":
            continue
        n = int(tid[1:].split()[0])
        # pile name from the heading paragraph before
        name = None
        for k in range(n, n - 4, -1):
            m = re.match(r"^4\.2\.\d+\. (P\d+)", PARAS.get(k, ""))
            if m:
                name = m.group(1)
                break
        notes = rows_t[-1]
        rr = []
        last = {}
        prev_estado = None
        for r in rows_t[3:-1]:
            c = cells_of(r)
            if len(c) < 16:
                continue
            base = {"tramo": c[0], "dim_cm": c[1], "posicion": c[2], "disp": c[3], "arm": c[4], "Q_pct": num(c[5]),
                    "NM_pct": num(c[6]), "aprov_pct": num(c[7])}
            merged = False
            for k2 in base:
                if base[k2] in ("", None):
                    base[k2] = last.get(k2)
                    merged = True
            last = base
            row = {**base, "naturaleza": c[8], "comp": c[9], "N_kN": num(c[10]), "Mxx_kNm": num(c[11]),
                   "Myy_kNm": num(c[12]), "Qx_kN": num(c[13]), "Qy_kN": num(c[14]), "estado": c[15] or prev_estado,
                   "src": f"{tid}: {base['posicion']} {c[8]}"}
            if merged:
                row["note"] = "merged cells (tramo/posición/checks) carried from the row above"
            prev_estado = row["estado"]
            rr.append(row)
        per[name] = {"src": tid, "notes": notes, "rows": rr}
    out["elu_checks_4_2"] = per
    out["sums_3_7_and_forces_3_4"] = {"note": "not duplicated here: see sap2000/ref/cype_reference.json (pile_base_forces_arranques_3_4, pile_sums_3_7)",
                                      "src": "P1708 table / P1727 table"}
    return out


# ----------------------------------------------------------------------------------------
# BEAMS
# ----------------------------------------------------------------------------------------
def beam_check_cell(s, src):
    s = s.strip()
    out = {"raw": s, "src": src}
    m = re.search(r"'([^']*)'", s)
    if m:
        out["x"] = m.group(1)
    m = re.search(r"η = ([\d.]+)", s)
    if m:
        out["eta_pct"] = float(m.group(1))
    return out


def parse_resistance_table(tid, offset_cols=None):
    rows = TABLES[tid]
    hdr = cells_of(rows[1])[1:]
    out = []
    for r in rows[2:]:
        c = cells_of(r)
        if not re.match(r"^P\d+ - P\d+$", c[0]):
            continue
        d = {"viga": c[0], "src": f"{tid}: {c[0]}"}
        for h, v in zip(hdr + ["Estado"], c[1:]):
            key = h if h else "Estado"
            d[key] = beam_check_cell(v, f"{tid}: {c[0]} {key}") if ("η" in v or "'" in v) else v
        out.append(d)
    return out


def parse_crack_table(tid):
    rows = TABLES[tid]
    hdr = cells_of(rows[1])[1:]
    out = []
    for r in rows[2:]:
        c = cells_of(r)
        if not re.match(r"^P\d+ - P\d+$", c[0]):
            continue
        d = {"viga": c[0], "src": f"{tid}: {c[0]}"}
        for h, v in zip(hdr, c[1:]):
            d[h if h else "Estado"] = v
        out.append(d)
    return out


def parse_flecha_cell(s, raw=False):
    m = re.findall(r"(f[TA],(?:max|lim)): ([\d.]+) mm", s)
    return {k: (v if raw else float(v)) for k, v in m}


def listing_table(tid, portico, img, img_labels):
    rows = TABLES[tid]
    head = cells_of(rows[0])
    tramos = [h.replace("Tramo: ", "") for h in head[1:]]
    secs = cells_of(rows[1])[1:]
    zones = cells_of(rows[2])[1:]
    nz = 3
    data = {t: [{"zone": zones[i * nz + j]} for j in range(nz)] for i, t in enumerate(tramos)}
    keymap = {"Momento mín.": "M_min", "Momento máx.": "M_max", "Cortante mín.": "V_min", "Cortante máx.": "V_max",
              "Torsor mín.": "T_min", "Torsor máx.": "T_max"}
    last_key = None
    area_key = None
    flechas = {}
    for r in rows[3:]:
        c = cells_of(r)
        if c[0] in keymap:
            last_key = keymap[c[0]]
            vals = c[2:]
            for i, t in enumerate(tramos):
                for j in range(nz):
                    data[t][j][last_key] = num(vals[i * nz + j])
        elif c[0] == "x":
            vals = c[2:]
            for i, t in enumerate(tramos):
                for j in range(nz):
                    data[t][j]["x_" + last_key] = num(vals[i * nz + j])
        elif c[0].startswith("Área") or (c[0] == "" and c[2] in ("Real", "Nec.")):
            if c[0]:
                area_key = {"Área Sup.": "As_top", "Área Inf.": "As_bot", "Área Transv.": "Asw_per_m"}[c[0]]
            kind = "real" if c[2] == "Real" else "nec"
            vals = c[3:]
            for i, t in enumerate(tramos):
                for j in range(nz):
                    data[t][j][f"{area_key}_{kind}"] = num(vals[i * nz + j])
        elif c[0] in ("F. Activa", "F. A plazo infinito"):
            for i, t in enumerate(tramos):
                txt = c[1 + i]
                m = re.match(r"([\d.]+) mm, (<?L/\d+) \(L: ([\d.]+) m\)", txt)
                flechas.setdefault(t, {})["activa" if c[0] == "F. Activa" else "plazo_infinito"] = {
                    "f": V(float(m.group(1)), "mm", f"{tid}: {c[0]} {t}"), "ratio": m.group(2),
                    "L_ref": V(float(m.group(3)), "m", f"{tid}: {c[0]} {t}"), "printed": txt}
    out = {}
    for i, t in enumerate(tramos):
        zs = data[t]
        for z in zs:
            z["src"] = f"{tid}: column 'Tramo: {t}' zone {z['zone']}"
        out[t] = {"section": V(secs[i], "-", f"{tid}: Sección {t}"), "zones": zs, "flechas": flechas.get(t, {})}
    return out


def build_beams():
    beams = {}
    # ---------------- body check P3-P4 -----------------------------------------------------
    body = {}
    body["heading"] = PV(333, P(333))
    body["datos_de_la_viga"] = datos_table("P336 table")
    body["bar_layout_drawing_image97"] = DI.bar_layout_image97()
    # summary tables
    beams_sum = parse_resistance_table("P340 table")
    body["summary_resistance"] = {"src": "P340 table", "rows": beams_sum,
                                  "notes": cells_of(TABLES["P340 table"][-2])[0][:400] + " ..."}
    body["summary_cracking"] = {"src": "P342 table", "rows": parse_crack_table("P342 table"),
                                "note_NP1": "La comprobación no procede, ya que la tensión de tracción máxima en el hormigón no supera la resistencia a tracción del mismo."}
    fl = cells_of(TABLES["P345 table"][1])
    body["summary_deflection"] = {"viga": fl[0], "long_term": {k: V(float(v), "mm", f"P345 table: {k}", printed=v) for k, v in parse_flecha_cell(fl[1], True).items()},
                                  "active": {k: V(float(v), "mm", f"P345 table: {k}", printed=v) for k, v in parse_flecha_cell(fl[2], True).items()},
                                  "limits": {"fT,lim": "L/250", "fA,lim": "L/500"}, "estado": fl[3]}
    # section: Negativos
    neg = {"heading": PV(351, P(351)), "section_x_range": V("P3 - 1.448 m", "-", "P351")}
    t = T("P352 table")
    neg["detailing_longitudinal"] = {"checks": t.all().checks(),
                                     **pick(t.seg(None, "Las barras longitudinales"), [("s_min", "smin"), ("s1", "s1"), ("s2", "s2"),
                                                                                    ("s3", "s3"), ("phi_max", "Ømax"), ("d_g", "dg")]),
                                     "s_b_max_spacing": t.seg("Las barras longitudinales").get("sb")}
    t = T("P354 table")
    neg["detailing_stirrups"] = {"checks": t.all().checks(),
                                 **pick(t.all(), [("s_min", "smin"), ("s1", "s1"), ("s2", "s2"), ("s3", "s3"),
                                                  ("phi_max_transv", "Ømax"), ("d_g", "dg")])}
    t = T("P359 table")
    neg["min_reinforcement"] = {"case": V("Flexión negativa alrededor del eje x", "-", "P359 table: row 1"),
                                "checks": t.all().checks(),
                                **pick(t.all(), [("As", "As"), ("As_min", "As,min"), ("z", "z"), ("W", "W"),
                                                 ("fct_m_fl", "fct,m,fl"), ("fyd", "fyd")]),
                                "note": "As,min formula image not legible; 5.09 cm² = W·fct,m,fl/(z·fyd) = 28339.35e3·3.37/(432·434.78) mm² (consistent)"}
    t = T("P364 table")
    top = t.seg("Se debe satisfacer:", "Esfuerzo cortante de agotamiento por compresión oblicua en el alma")
    st1 = statement(t.all(), 1)
    comp = t.seg("Esfuerzo cortante de agotamiento por compresión oblicua en el alma", "Esfuerzo cortante de agotamiento por tracción en el alma")
    ten = t.seg("Esfuerzo cortante de agotamiento por tracción en el alma", "Separación de las armaduras transversales")
    sep = t.seg("Separación de las armaduras transversales", "Cuantía mecánica mínima")
    cua = t.seg("Cuantía mecánica mínima")
    neg["shear"] = {
        "title": V(TABLES["P363 table"][0], "-", "P363 table"),
        "position": st1["position"], "combination": st1["combination"],
        "eta_1_VRdmax": top.get("η", 1), "VEd_y": top.get("VEd,y", 1), "VRd_max_Vy": top.get("VRd,max,Vy"),
        "eta_2_VRds": top.get("η", 2), "VRd_s_Vy": top.get("VRd,s,Vy"),
        "compression_strut_dir_Y": pick(comp, [("VRd_max", "VRd,max"), ("alpha_cw", "αcw"), ("sigma_cp", "σcp"), ("NEd", "NEd"),
                                               ("As_comp", "A's"), ("Ac", "Ac"), ("fyd", "fyd"), ("fcd", "fcd"), ("bw", "bw"),
                                               ("z", "z"), ("nu1", "ν1"), ("alpha", "α"), ("theta", "θ")]),
        "stirrups_dir_Y": pick(ten, [("VRd_s", "VRd,s"), ("Asw", "Asw"), ("s", "s"), ("z", "z"), ("fywd", "fywd"),
                                     ("fywk", "fywk"), ("alpha", "α"), ("theta", "θ")]),
        "stirrups_note": "fywd printed 400 MPa (= min(fywk/γs, 400)); symbol text for fywk says 'Límite elástico de cálculo' (sic). "
                         "VRd,s = Asw/s·z·fywd·(cotθ+cotα)·sinα",
        "spacing": {"checks": sep.checks(),
                    "longitudinal": pick(sep.seg(None, "La separación transversal"), [("s", "s"), ("s_l_max", "sl,max"), ("d", "d"), ("alpha", "α")]),
                    "transverse_legs": pick(sep.seg("La separación transversal"), [("s_t_max", "st,max"), ("d", "d")]),
                    "note": "st,trans = 180 mm is the left side of check 2 (not printed as a separate value). Formula images not legible; the printed limits are consistent with EC2 9.2.2(6)/(8): sl,max = 0.75·d·(1+cotα) = 360 and st,max = min(0.75·d, 600) = 360 (INFERENCE)"},
        "min_shear_ratio": {"checks": cua.checks(),
                            **pick(cua, [("rho_w", "ρw"), ("Asw", "Asw"), ("s", "s"), ("bw", "bw"), ("alpha", "α"),
                                         ("rho_w_min", "ρw,min"), ("fctm", "fctm"), ("fck", "fck"), ("fyk", "fyk")]),
                            "formulas_seen_in_render": ["ρw = Asw/(s·bw·sinα)", "ρw,min = 0.08·sqrt(fck)/fyk", "fck ≤ 50 MPa → fctm = 0.30·fck^(2/3)"]},
        "all_printed_values": t.all().dump(),
    }
    t = T("P369 table")
    s1 = t.all()
    st = statement(s1, 1)
    neg["bending"] = {
        "title": V(TABLES["P368 table"][0], "-", "P368 table"),
        "position": st["position"], "combination": st["combination"],
        "eta": s1.get("η"),
        **pick(s1, [("NEd", "NEd"), ("MEd_x", "MEd,x"), ("MEd_y", "MEd,y"), ("NRd", "NRd"), ("MRd_x", "MRd,x"), ("MRd_y", "MRd,y")]),
        "eta_formula_seen_in_render": "η1 = sqrt(NEd²+MEd,x²+MEd,y²)/sqrt(NRd²+MRd,x²+MRd,y²) ≤ 1",
        "material_hypotheses": materials_hyp("P373 table", "P377 table"),
        "equilibrium_at_ultimate": equilibrium("P381 table", "P384 table", "P385 table", 380, "image112.png",
                                               DI.equilibrium_beam("image112.png")),
        "equilibrium_at_design_forces": equilibrium("P389 table", "P392 table", "P393 table", 388, "image113.png",
                                                    DI.equilibrium_beam("image113.png")),
        "bar_notes": ("INFERENCE (geometry, not printed): coordinates are relative to the gross-section centroid, which lies "
                      "244.18 mm above the soffit for 50x55 + 2x(15x30) (Ac = 3650 cm² printed); hence y = +235.82 -> top bars 70 mm "
                      "below the top face, y = -174.18 -> bottom bars 70 mm above the soffit, y = -9.18 -> side bars 235 mm above the "
                      "soffit. x = ±185 is 65 mm inside the 50 cm web faces (web 'piel' bars I1Ø10+D1Ø10 (470)); x = ±335 is 65 mm inside "
                      "the 80 cm ledge faces ('M. Alas (421)'). PRINTED fact: bars 6/16 (x = ±185) carry σs = 0.00 although their strain "
                      "equals that of bars 7/15 (x = ±335) — reason not printed."),
    }
    torsion = []
    for n in (397, 401, 405, 409, 413, 417, 421, 425, 429, 433):
        torsion.append({"check": TABLES[f"P{n} table"][0], "result": PV(n + 2, P(n + 2))})
    neg["torsion"] = torsion
    neg["torsion_comment"] = PV(437, P(437))
    body["section_negativos_P3_1448"] = neg
    body["section_positivos_P3_P4"] = {
        "heading": PV(440, P(440)),
        "note": {"note": "The 'Positivos' block (P440-P529) is a verbatim copy of the 'Negativos' block (P351-P437): same tables, "
                          "MEd,x = -273.71 at 'P3', η = 0.840, same bars and stresses. No positive-moment (sagging) section check is printed.",
                 "src": "P440-P529 vs P351-P437 (text diff: identical)"},
        "eta_bending": T("P458 table").all().get("η"),
        "MEd_x": T("P458 table").all().get("MEd,x"),
        "eta_shear_VRds": T("P453 table").all().get("η", 2),
    }
    # cracking body
    crack = {"heading": PV(531, P(531)), "beam_named": PV(532, P(532),
             note="Heading names P5 - P6 while the summary table (P342) is for P3 - P4 and image117 shows Pórtico 6 (P7-P8)."),
             "faces": []}
    for n in (532, 536, 540, 544, 548, 552, 556, 560, 564):
        crack["faces"].append({"check": TABLES[f"P{n} table"][0], "result": PV(n + 2, P(n + 2))})
    crack["hand_check"] = {
        "text_1": PV(568, P(568)),
        "quasi_permanent_moments_image117": DI.qp_moments_image117(),
        "text_2": PV(570, P(570)),
        "stress_check_image118": DI.crack_stress_image118(),
        "conclusion": PV(575, P(575)),
        "fct": PV(575, 3.2, "MPa", "'La resistencia a tracción del C35 es de 3.2 Mpa' (fctm printed 3.21 in P364 table)"),
        "max_tension_quasi_permanent": V(2.20, "MPa", "P575", printed="2.20"),
    }
    body["cracking"] = crack
    # deflection
    t = T("P583 table").all()
    defl = {"summary": {"long_term": {k: V(float(v), "mm", f"P581 table: {k}", printed=v) for k, v in parse_flecha_cell(cells_of(TABLES["P581 table"][1])[0], True).items()},
                        "active": {k: V(float(v), "mm", f"P581 table: {k}", printed=v) for k, v in parse_flecha_cell(cells_of(TABLES["P581 table"][1])[1], True).items()}},
            "statement": V(t.tab.texts[1][1], "-", "P583 table: row 3"),
            "position": V(1.45, "m", "P583 table: 'La flecha máxima se produce en la sección \"1.45 m\"'", printed="1.45"),
            "combination": V("Peso propio+Cargas muertas - Tabiquería+Cargas muertas - Pavimento+0.3Sobrecarga de uso", "-", "P583 table"),
            "checks": t.checks(),
            **pick(t, [("fT_lim", "fT,lim"), ("L_ref", "L"), ("fT_max", "fT,max")]),
            "history": [], "history_plot": DI.deflection_history_image120()}
    for r in TABLES["P588 table"][1:]:
        c = cells_of(r)
        defl["history"].append({"escalon": c[0], "ti_dias": num(c[1]), "tf_dias": num(c[2]) if c[2] != "∞" else "∞",
                                "f0_ti_mm": num(c[3]), "dfi_ti_mm": num(c[4]), "f_ti_mm": num(c[5]), "fdif_mm": num(c[6]),
                                "ftot_mm": num(c[7]), "ftot_max_mm": num(c[8]), "src": f"P588 table: {c[0]}"})
    body["deflection"] = defl
    beams["body_check_P3_P4"] = body

    # ---------------- appendix §2 listing ---------------------------------------------------
    listing = {}
    spec = [("Pórtico 1", ["P1608 table"], "image203.png", 1607), ("Pórtico 3", ["P1614 table"], "image204.png", 1613),
            ("Pórtico 4", ["P1620 table"], "image205.png", 1619), ("Pórtico 5", ["P1626 table"], "image206.png", 1625),
            ("Pórtico 6", ["P1632 table"], "image207.png", 1631), ("Pórtico 7", ["P1638 table"], "image208.png", 1637),
            ("Pórtico 8", ["P1644 table"], "image209.png", 1643), ("Pórtico 9", ["P1650 table"], "image210.png", 1649),
            ("Pórtico 10", ["P1656 table", "P1661 table"], "image211.png + image212.png", 1655)]
    for name, tids, img, pn in spec:
        tr = {}
        for tid in tids:
            tr.update(listing_table(tid, name, img, None))
        listing[name] = {"src": ", ".join(tids), "drawing": f"P{pn} image {img}", "tramos": tr}
    beams["listing_armado_vigas_2"] = {
        "heading": PV(1602, P(1602)),
        "units": {"M": "kN·m", "V": "kN", "T": "kN·m (printed '[kN]', sic)", "x": "m (distance from the origin of the tramo)",
                  "As_top/As_bot": "cm²", "Asw_per_m": "cm²/m"},
        "null_meaning": "null = '--' in the listing",
        "porticos": listing}
    beams["drawings_bar_layout"] = DI.drawings()
    beams["model_mapping"] = mapping()
    beams["inferred_bar_layouts"] = inferred()

    # ---------------- appendix §4.3 checks --------------------------------------------------
    res = parse_resistance_table("P1813 table") + parse_resistance_table("P1815 table")
    crk = []
    for tid in ("P1818 table", "P1820 table", "P1822 table", "P1824 table", "P1826 table"):
        crk += parse_crack_table(tid)
    defl = []
    for r in TABLES["P1830 table"][2:]:
        c = cells_of(r)
        defl.append({"viga": c[0], **{k: v for k, v in parse_flecha_cell(c[1]).items()},
                     **{k: v for k, v in parse_flecha_cell(c[2]).items()}, "estado": c[3], "units": "mm",
                     "src": f"P1830 table: {c[0]}"})
    beams["appendix_checks_4_3"] = {
        "resistance": {"src": "P1813 table + P1815 table", "rows": res,
                       "notes": {"N.P.(1)": "no hay momento torsor", "N.P.(2)": "no hay interacción entre torsión y esfuerzos normales",
                                 "N.P.(3)": "No hay interacción entre torsión y cortante para ninguna combinación",
                                 "N.P.(4)": "No hay esfuerzos que produzcan tensiones normales para ninguna combinación",
                                 "src": "P1816 table"}},
        "cracking": {"src": "P1818..P1826 tables", "rows": crk,
                     "notes": {"N.P.(1)": "la tensión de tracción máxima en el hormigón no supera la resistencia a tracción del mismo",
                               "N.P.(2)": "No hay esfuerzos que produzcan tensiones normales para ninguna combinación", "src": "P1827 table"}},
        "deflection": {"src": "P1830 table", "limits": {"fT,lim": "L/250 (Cuasipermanente, a plazo infinito)",
                                                         "fA,lim": "L/500 (Cuasipermanente, activa)"}, "rows": defl},
    }
    return beams


def mapping():
    rows = []
    for a in range(1, 8):
        sea = ["P1", "P3", "P5", "P7", "P13", "P15", "P16"][a - 1]
        land = ["P2", "P4", "P6", "P8", "P14", "P17", "P18"][a - 1]
        edge = ["P9", "P10", "P11", "P12", "P19", "P21", "P20"][a - 1]
        rows.append({"axis": a, "X_m": 6.5 * (a - 1), "portico": f"Pórtico {a + 2}",
                     "section": "80x55+15x30 (inverted L; model VIGA_L80x55_ALA15x30" + ("_M" if a == 7 else "") + ")" if a in (1, 7)
                     else "50x55+15x30+15x30 (inverted T; model VIGA_T50x55_ALAS15x30)",
                     "tramo_cantilever_sea": f"{edge}-{sea}",
                     "tramo_cantilever_note": f"from the sea-edge/bollard point {edge} (CYPE punto fijo Y=-0.45, 'mitad inferior'; model Y=-0.375) to pile {sea} (Y=0.00); CYPE L = 0.10 m (clear length between the CHS and the pile face)",
                     "tramo_span": f"{sea}-{land}",
                     "tramo_span_note": f"between sea pile {sea} (Y=0.00) and land pile {land} (Y=3.45); c/c 3.45 m, CYPE L = 3.05 m (clear span between pile faces)",
                     "model_frames": f"VT{a}_* (group PORTICO_{a + 2})"})
    return {
        "src": "sap2000/model/trasmallo.py (pile_sea, pile_land, edge_pts, portico_of_axis = a + 2) + P1549 table (CYPE coordinates)",
        "transverse_beams": rows,
        "edge_beams": [
            {"portico": "Pórtico 1", "tramo": "P9-P20", "section": "25x30", "line": "sea edge (bollard line) Y=-0.45 CYPE / -0.375 model",
             "supports_along": ["P9", "P10", "P11", "P12", "P19", "P21", "P20"], "X_m": "0 -> 39", "model_frames": "VBM_* (group PORTICO_1)",
             "note": "CYPE lists ONE tramo P9-P20 over the full 39 m; zone 1/3L, 2/3L, 3/3L split the whole beam; x up to 36.00 m"},
            {"portico": "Pórtico 10", "tramos": ["P2-P4", "P4-P6", "P6-P8", "P8-P14", "P14-P17", "P17-P18"], "section": "25x30",
             "line": "land edge; CYPE runs it through the land piles (Y=3.45); model Y=3.675", "L_each_m": 6.10,
             "model_frames": "VBT_* (group PORTICO_10)",
             "note": "L = 6.10 m = 6.50 - 0.40 (clear between pile faces)"}],
        "no_portico_2": "No 'Pórtico 2' appears in the listing (numbering jumps 1 -> 3).",
        "x_origin_note": "Listing 'x' = 'Distancia al origen de la barra' (P340 notation). For P1-P2-type tramos x = 0.00 .. 3.05 m, i.e. "
                         "measured from the face of the sea pile (model Y ≈ 0.20 + x) — INFERENCE from L = 3.05 = 3.45 - 0.40; for the cantilevers x = 0.00 .. 0.10 m. "
                         "Caveat C16: the body/drawing hogging moment at 'P3' (-273.71) exceeds the listing value at x = 0.00 (-266.03), "
                         "so the section called 'P3' is not the listing x = 0.00.",
        "body_positions_note": "Body check positions '0.488 m' (shear) and 'P3' (bending) refer to tramo P3-P4 of Pórtico 4 (axis 2, X = 6.5 m).",
    }


def inferred():
    return {
        "WARNING": "INFERENCE (not transcribed): bar counts deduced from 'Área Real' values (Ø20 = 3.1416 cm², Ø16 = 2.0106 cm², Ø10 = 0.7854 cm², Ø8 = 0.5027 cm²) and cross-checked with the drawings.",
        "15.71 cm²": "5Ø20 (15.708) — top of all transverse beams (drawings: 5Ø20 (471)/(472)/(474))",
        "21.99 cm²": "7Ø20 (21.99) — bottom of inner beams P3-P4 type = 5Ø20 web + I1Ø20+D1Ø20 ledges; confirmed by P381 table (bars 8-14)",
        "18.85 cm²": "6Ø20 (18.85) — bottom of end beams (Pórticos 3, 9) = 5Ø20 + 1Ø20 in the single ledge (D1Ø20 / I1Ø20)",
        "4.02 cm²": "2Ø16 (4.02) — top and bottom of edge beams 25x30 (drawings 2Ø16)",
        "23.56 cm²/m": "3 legs Ø10 at 10 cm (3·0.7854/0.10) — equals Asw 2.36 cm² @ 100 mm of P364 table; drawings 37x{(1eØ10+1rØ10)+(1eØ10)}/10",
        "6.70 cm²/m": "2 legs Ø8 at 15 cm (2·0.5027/0.15) — edge beams 1eØ8/15",
        "non_integer_values": {"values": [11.28, 13.42, 19.01, 12.47, 13.58, 15.86, 11.82],
                               "interpretation": "cantilever zones (L = 0.10 m) next to the bar ends: CYPE counts a reduced effective area of partially anchored bars — not a bar count. INFERENCE."},
        "pile": "12Ø25 = 58.91 cm² (printed), 4 per face; A's = 19.64 cm² = 4Ø25 (one face) used in σcp for the Y direction (P237 table)",
        "pile_Asl_39_27": "39.27 cm² = 8Ø25 used as Asl for VRd,c (P237 table) — INFERENCE (2 faces?)",
    }


# ----------------------------------------------------------------------------------------
# MATERIALS / PARAMETERS
# ----------------------------------------------------------------------------------------
def build_materials():
    m = {}
    m["code"] = PV(1462, P(1462).split(": ", 1)[1])
    m["program"] = {"version": PV(1454, P(1454).split(": ")[1]), "licence": PV(1455, P(1455).split(": ")[1]),
                    "project": PV(1458, P(1458).split(": ")[1].strip()), "clave": PV(1459, P(1459).split(": ")[1])}
    m["categoria_de_uso"] = PV(1465, P(1465).split(": ")[1])
    conc = []
    for r in TABLES["P1583 table"][2:]:
        c = cells_of(r)
        conc.append({"elemento": c[0], "hormigon": c[1], "fck_MPa": num(c[2]), "gamma_c": num(c[3]), "arido": c[4],
                     "arido_max_mm": num(c[5]), "Ec_MPa": num(c[6]), "src": f"P1583 table: {c[0]}"})
    m["concretes_1_11_1"] = conc
    c = cells_of(TABLES["P1591 table"][1])
    m["steel_bars_1_11_2_1"] = {"elemento": c[0], "acero": c[1], "fyk_MPa": num(c[2]), "gamma_s": num(c[3]), "src": "P1591 table: Todos"}
    m["project_materials_text"] = {
        "in_situ_beams": [PV(111, P(111)), PV(112, P(112)), PV(113, 5, "cm", "recubrimiento 5 cm (vida útil 50 años)")],
        "alveoplacas": [PV(115, P(115)), PV(116, P(116)), PV(117, P(117)), PV(118, 5, "cm")],
        "piles": [PV(120, P(120)), PV(121, P(121)), PV(122, 5, "cm")],
        "note": "Project text: exposure XS3, steel 'B500 SD'; CYPE listings print steel 'B 500 S'.",
    }
    m["HA50_piles_as_used_by_CYPE"] = {
        **pick(T("P249 table").all(), [("fck", "fck"), ("gamma_c", "γc"), ("alpha_cc", "αcc"), ("fcd", "fcd"), ("eps_c2", "εc2"), ("eps_cu2", "εcu2")]),
        "Ec": V(33550, "MPa", "P1583 table: Pilares y pantallas"),
        "aggregate_max": V(20, "mm", "P220 table: Tamaño máximo de árido"),
        "cover_geometric": V(5.0, "cm", "P220 table: Recubrimiento geométrico"),
        "fctm": V(None, "MPa", "not printed", "fctm / fct,m,fl are not printed for HA-50 (no crack or As,min-bending check for piles)"),
        "phi_ef_lambda_lim": T("P245 table").seg("Comprobación del estado limite de inestabilidad").seg("En el eje x:", "En el eje y:").get("ϕef", 1),
        "phi_ef_K_phi": T("P245 table").seg("Comprobación del estado limite de inestabilidad").seg("En el eje x:", "En el eje y:").get("ϕef", 2),
        "phi_ef_note": "Two printed values: 1.8 (in A = 1/(1+0.2ϕef)) and 1.750 (in Kϕ = 1+β·ϕef) — same parameter, different rounding.",
    }
    m["HA35_beams_as_used_by_CYPE"] = {
        **pick(T("P373 table").all(), [("fck", "fck"), ("gamma_c", "γc"), ("alpha_cc", "αcc"), ("fcd", "fcd"), ("eps_c2", "εc2"), ("eps_cu2", "εcu2")]),
        "fctm": T("P364 table").all().get("fctm"),
        "fct_m_fl": T("P359 table").all().get("fct,m,fl"),
        "Ec": V(30669, "MPa", "P1583 table: Forjados"),
        "cover_geometric_top": V(5.0, "cm", "P336 table: Recubrimiento geométrico superior"),
        "cover_geometric_bottom": V(5.0, "cm", "P336 table: Recubrimiento geométrico inferior"),
        "cover_geometric_side": V(5.0, "cm", "P336 table: Recubrimiento geométrico lateral"),
        "aggregate_max": V(20, "mm", "P352 table: dg"),
    }
    m["B500S_as_used_by_CYPE"] = {
        **pick(T("P253 table").all(), [("fyk", "fyk"), ("gamma_s", "γs"), ("fyd", "fyd"), ("eps_su", "εsu")]),
        "eps_yd": T("P245 table").seg("Comprobación del estado limite de inestabilidad").seg("En el eje x:", "En el eje y:").get("εyd"),
        "fywk": T("P364 table").all().get("fywk"),
        "fywd": T("P364 table").all().get("fywd", note="limited to 400 MPa"),
        "Es": V(None, "MPa", "not printed", "Es is not printed; εyd = 0.00217 = 434.78/Es implies Es ≈ 200000 MPa (INFERENCE)"),
    }
    # partial factors
    pf = {}
    for tid, name in (("P1509 table", "ELU_rotura_hormigon"), ("P1513 table", "ELU_rotura_hormigon_cimentaciones"), ("P1517 table", "Desplazamientos")):
        rows = {}
        for r in TABLES[tid][3:]:
            c = cells_of(r)
            rows[c[0]] = {"gamma_fav": num(c[1]), "gamma_desfav": num(c[2]), "psi_p": num(c[3]) if c[3] != "-" else None,
                          "psi_a": num(c[4]) if c[4] != "-" else None, "src": f"{tid}: {c[0]}"}
        pf[name] = {"situacion": TABLES[tid][0], "rows": rows}
    m["partial_and_combination_factors_1_6_1"] = pf
    combos = {}
    for tid, name in (("P1526 table", "ELU_rotura_hormigon"), ("P1530 table", "ELU_rotura_hormigon_cimentaciones"), ("P1534 table", "Desplazamientos")):
        hdr = cells_of(TABLES[tid][0])[1:]
        rows = []
        for r in TABLES[tid][1:]:
            c = cells_of(r)
            rows.append({"comb": int(c[0]), "factors": {h: (num(x) if x else 0.0) for h, x in zip(hdr, c[1:])}, "src": f"{tid}: Comb. {c[0]}"})
        combos[name] = rows
    m["combinations_1_6_2"] = combos
    m["quasi_permanent_combination"] = {
        "as_printed": V("Peso propio+Cargas muertas - Tabiquería+Cargas muertas - Pavimento+0.3Sobrecarga de uso", "-",
                        "P583 table: combination of the deflection check"),
        "psi2_Qa": V(0.3, "-", "P583 table"),
        "psi2_tiro_bolardo_viento": V(0.0, "-", "P276 text + P275 image92.png (Tabla 5.10 Viento C = 0.0)",
                                      "'en situacion cuasipermanente el coeficietne [sic] de combinacion para el viento es 0' (P276, verbatim)"),
        "used_in_hand_crack_check": PV(568, P(568), note="moments of image117 (P569) are quasi-permanent"),
    }
    m["gravity_loads_1_4_1"] = [{"planta": cells_of(r)[0], "SCU_kN_m2": num(cells_of(r)[1]), "CM_kN_m2": num(cells_of(r)[2]),
                                 "src": f"P1469 table: {cells_of(r)[0]}"} for r in TABLES["P1469 table"][1:]]
    return m


# ----------------------------------------------------------------------------------------
def build_slab():
    s = {}
    s["text"] = PV(593, P(593).replace("[IMG image121.png]", ""))
    s["M_pos_max"] = PV(593, 100.08, "kN·m/m", "printed unit 'kN' (sic); per 1 m band")
    s["M_neg_max"] = PV(593, -100.32, "kN·m/m", "printed unit 'kN' (sic)")
    s["V_max"] = PV(593, 105.52, "kN/m", "printed unit 'kN'")
    s["envelope_image121"] = DI.slab_envelope_image121()
    s["plate_characteristics_image122"] = DI.plate_image122()
    s["armados_hoja_autorizacion"] = {
        "text": PV(600, P(600).replace("[IMG image123.png]", "")),
        "plan_image123": DI.plan_image123(),
        "table_image124": DI.table_image124()}
    s["ficha_1_10"] = {"description": {"src": "P1566 table / P1572 table", "text": cells_of(TABLES["P1566 table"][1])[1]},
                       "name": PV(1572, P(1572))}
    pos = cells_of(TABLES["P1574 table"][5])
    refs = [x.strip() for x in pos[0].split(" / ")]
    cols = ["M_ult_kNm_m", "M_fis_kNm_m", "EI_total_kNm2_m", "EI_fis_kNm2_m", "M_serv_I_kNm_m", "M_serv_II_kNm_m", "M_serv_III_kNm_m"]
    rows = []
    for i, ref in enumerate(refs):
        rows.append({"ref": ref, **{c: num(pos[1 + j].split(" / ")[i]) for j, c in enumerate(cols)}, "V_ult_kN_m": None,
                     "src": f"P1574 table: {ref}"})
    s["ficha_1_10"]["positive_per_1m"] = {"rows": rows, "note": "Cortante último column empty in the positive table; "
                                           "service moments per exposure class I (Ambiente III, agresivo), II (Ambiente II), III (Ambiente I) — P1577 table"}
    neg = cells_of(TABLES["P1575 table"][4])
    refs = [x.strip() for x in neg[0].split(" / ")]
    cols = ["M_ult_tipo_kNm_m", "M_ult_macizado_kNm_m", "M_fis_kNm_m", "EI_total_kNm2_m", "EI_fis_kNm2_m", "V_ult_kN_m"]
    s["ficha_1_10"]["negative_per_1m"] = {"steel": "B 500 S, Ys=1.15", "rows": [
        {"refuerzo_superior": ref, **{c: num(neg[1 + j].split(" / ")[i]) for j, c in enumerate(cols)}, "src": f"P1575 table: {ref}"}
        for i, ref in enumerate(refs)]}
    return s


def build_cantil():
    t = P(607)
    return {"text": PV(607, t),
            "reinforcement": PV(607, "4φ20 y cercos φ10/0.10"),
            "compression_layer": PV(607, 5, "cm"), "diaphragm_width": PV(607, 4.65, "m"),
            "M_atraque": PV(607, 410, "kN·m"), "span": PV(607, 6.50, "m"),
            "end_tension": PV(607, 83, "kN", "410/4.65 = 83 as printed; the division actually gives 88.2 kN (arithmetic slip in the "
                                             "document; conclusion unchanged, 88.2 < 502 kN)"),
            "tension_resistance_4phi20": PV(607, 502, "kN", "'4*314*400 N = 502 Kn' (uses 400 MPa, not fyd = 434.78 MPa; "
                                                            "4·314·400 = 502 400 N is correct)"),
            "note": "The document does not identify which member is the 'viga cantil'; its 4φ20 + cercos φ10/0.10 match no beam of the "
                    "CYPE listing (edge beams Pórtico 1/10: 2Ø16 top + 2Ø16 bottom, cercos Ø8/15). The hand check uses 400 MPa for the bars "
                    "and 314 mm² per φ20. UNRESOLVED. Arithmetic check: 410/4.65 = 88.2 kN, not the printed 83 kN (still far below 502 kN)."}


def construir(textos):
    """Dump texts (volcado.RANGOS files) -> the reference dict."""
    cargar(textos)
    out = {
        "meta": {
            "title": "CYPE design reference — Muelle de Trasmallo (Cullera), one 40 m module: piles and beams",
            "source_document": "report/A10_CALC_ESTRUCTURAS.docx (Anejo 10 Cálculo de estructuras)",
            "scope": "Body P215-P608 (Trasmallo results) and Apéndice 1 P1449-P1835 (Listados de cálculo muelle de trasmallo). "
                     "Muelle de Arrastre and casetas are excluded.",
            "program": "CYPECAD 2023 (P1454), licence 84023 (P1455); code Código Estructural (P1462)",
            "src_convention": {
                "P<n>": "paragraph index n of python-docx Document.paragraphs (same numbering as the a10_full.txt dump)",
                "P<n> table": "the table that immediately follows paragraph P<n> in document order ('#k' if several)",
                "[A > B] sym": "row found inside the table after the header rows A then B (e.g. '[Cortante en la dirección Y] VRd,max')",
                "(occurrence k)": "k-th row with that symbol inside the (sub)segment",
                "check k left/right": "k-th comparison row of the table ('value  ≤/≥  limit  ✓')",
                "P<n> image <file>": "value read visually from an embedded image anchored at P<n> (Word media file name)",
                "tabular rows": "for CYPE tables (bars, listing zones, pile tables) one src is given per row; column units are in the key names",
            },
            "extraction": "Values parsed directly from the .docx with python-docx INCLUDING nested tables (lost in a10_full.txt, e.g. "
                          "'Datos del pilar') and Symbol-font glyphs (η, σ, ν, ρ, λ, ϕ, θ, α, ε, γ, ≤, ≥ were lost in the dump). "
                          "Equation images (WMF) were rendered via LibreOffice PDF export and are only partially legible: the "
                          "'formulas_seen_in_render' / 'formula...' strings are the legible parts completed with the Eurocode 2 expressions "
                          "that reproduce the printed numbers — they are NOT verbatim transcriptions.",
            "sign_conventions": {"bars": "σs, ε: + compression, - tension (CYPE equilibrium tables)",
                                 "beam_moments": "negative = hogging (top tension)",
                                 "pile_N": "N > 0 compression"},
            "units_default": "kN, kN·m, MPa, mm/cm as printed next to each value",
            "generated": "2026-09-23",
            "related": ["sap2000/ref/cype_reference.json (CYPE analysis values, per-hypothesis forces, conventions)",
                        "diseno/ref/cype_design_reference.md (human-readable companion)"],
        },
        "key_results": None,
        "discrepancies_and_caveats": caveats(),
        "materials_and_parameters": build_materials(),
        "piles": build_piles(),
        "beams": build_beams(),
        "alveoplacas": build_slab(),
        "viga_cantil": build_cantil(),
        "not_in_document": not_in_doc(),
    }
    out["key_results"] = key_results(out)
    return out


def key_results(o):
    p1 = o["piles"]["section_1_forjado_cabeza"]
    p2 = o["piles"]["section_2_empotramiento_arranque"]
    b = o["beams"]["body_check_P3_P4"]["section_negativos_P3_1448"]
    bd = o["beams"]["body_check_P3_P4"]["deflection"]
    return {
        "note": "Copies of the most-used reference numbers (same objects as in the detailed blocks).",
        "pile_P3_head_forjado": {
            "combination": p1["normal_forces"]["combination"],
            "NEd": p1["normal_forces"]["section_resistance_first_order"]["NEd"],
            "MEd_x_first_order": p1["normal_forces"]["section_resistance_first_order"]["MEd_x"],
            "MEd_y_first_order": p1["normal_forces"]["section_resistance_first_order"]["MEd_y"],
            "eta_1": p1["normal_forces"]["eta_1_section_resistance"],
            "MSd_x_second_order": p1["normal_forces"]["instability_second_order"]["MSd_x"],
            "MSd_y_second_order": p1["normal_forces"]["instability_second_order"]["MSd_y"],
            "eta_2": p1["normal_forces"]["eta_2_instability"],
            "e2": p1["normal_forces"]["instability_second_order"]["axis_x"]["e2"],
            "lambda": p1["normal_forces"]["instability_second_order"]["axis_x"]["lambda"],
            "lambda_lim": p1["normal_forces"]["instability_second_order"]["axis_x"]["lambda_inf_lim"],
            "shear_eta_VRdmax": p1["shear"]["eta_1_VRdmax"], "VRd_max": p1["shear"]["VRd_max"],
            "shear_eta_VRdc": p1["shear"]["eta_2_VRd"], "VRd_c": p1["shear"]["VRd_s_printed"],
            "As_min": p1["min_max_reinforcement"]["As_min_total"]["As_min"],
            "As_max": p1["min_max_reinforcement"]["As_max"]["As_max"],
            "listing_aprov_pct": {"value": 92.5, "unit": "%", "src": "P1752 table: Cabeza (N,M)"},
        },
        "pile_P3_base_empotramiento": {
            "NEd": p2["normal_forces"]["section_resistance_first_order"]["NEd"],
            "MEd_x_first_order": p2["normal_forces"]["section_resistance_first_order"]["MEd_x"],
            "MEd_y_first_order": p2["normal_forces"]["section_resistance_first_order"]["MEd_y"],
            "eta_1": p2["normal_forces"]["eta_1_section_resistance"],
            "MSd_x_second_order": p2["normal_forces"]["instability_second_order"]["MSd_x"],
            "MSd_y_second_order": p2["normal_forces"]["instability_second_order"]["MSd_y"],
            "eta_2": p2["normal_forces"]["eta_2_instability"],
            "shear_eta_VRdmax": p2["shear"]["eta_1_VRdmax"], "VRd_max": p2["shear"]["VRd_max"],
            "listing_aprov_pct": {"value": 90.7, "unit": "%", "src": "P1752 table: Arranque"},
        },
        "beam_P3_P4": {
            "shear_position": b["shear"]["position"], "shear_combination": b["shear"]["combination"],
            "VEd_y": b["shear"]["VEd_y"], "VRd_s": b["shear"]["VRd_s_Vy"], "eta_VRds": b["shear"]["eta_2_VRds"],
            "VRd_max": b["shear"]["VRd_max_Vy"], "eta_VRdmax": b["shear"]["eta_1_VRdmax"],
            "Asw": b["shear"]["stirrups_dir_Y"]["Asw"], "s": b["shear"]["stirrups_dir_Y"]["s"], "z": b["shear"]["stirrups_dir_Y"]["z"],
            "MEd_x_hogging_at_P3": b["bending"]["MEd_x"], "MRd_x": b["bending"]["MRd_x"], "eta_bending": b["bending"]["eta"],
            "As_top": b["min_reinforcement"]["As"], "As_min": b["min_reinforcement"]["As_min"],
            "fT_max": bd["fT_max"], "fT_lim": bd["fT_lim"],
            "fA_max": bd["summary"]["active"]["fA,max"], "fA_lim": bd["summary"]["active"]["fA,lim"],
            "crack_hand_check_M_qp": o["beams"]["body_check_P3_P4"]["cracking"]["hand_check"]["stress_check_image118"]["MEd_x"],
            "crack_hand_check_sigma_ct": o["beams"]["body_check_P3_P4"]["cracking"]["hand_check"]["max_tension_quasi_permanent"],
            "crack_hand_check_fct": o["beams"]["body_check_P3_P4"]["cracking"]["hand_check"]["fct"],
        },
    }


def nec_gt_real():
    out = []
    for tid in ("P1608 table", "P1614 table", "P1620 table", "P1626 table", "P1632 table", "P1638 table", "P1644 table",
                "P1650 table", "P1656 table", "P1661 table"):
        for t, tv in listing_table(tid, None, None, None).items():
            for z in tv["zones"]:
                for k in ("As_top", "As_bot", "Asw_per_m"):
                    r, n = z.get(k + "_real"), z.get(k + "_nec")
                    if r is not None and n is not None and n > r:
                        out.append(f"{t} {z['zone']} {k}: nec {n} > real {r} ({tid})")
    return out


def caveats():
    return [
        {"id": "C1", "text": "Pile body section 1 heading 'FORJADO 1 (0 - 7.00 M)' (P218) but 'Datos del pilar' Tramo 0.000/7.250 m "
                              "(P220 table) and listing 'Forjado 1 (0 - 7.25 m)' (P1714 table); §3.2 'Armado de pilares' (P1692 table) "
                              "and §3.3 (P1702 table) print Tramo 0.00/6.70 m (flexible length below the beam soffit); buckling length "
                              "l0 = 6.700 m (both planes). Origin of the 7.00: the model description (P175-P182) says the piles are taken "
                              "as fixed 'a partir de una longitud de 6.40 m', the simplified frame gives the maximum moment at 6.5 m depth "
                              "and 'del aldo [sic] de la seguridad' 7.00 is adopted for the fixity in the general model; the CYPE run "
                              "actually listed uses 7.25 m (tramo 0.000/7.250).",
         "src": "P218, P220 table, P245 table, P1692 table, P175, P182"},
        {"id": "C2", "text": "Utilisation mismatch body vs listing for P3: body η2 = 0.913 (cabeza) vs listing 'N,M' 92.5 %; body "
                              "EMPOTRAMIENTO η2 = 0.894 vs listing 'Arranque' 90.7 % (and 'Pie' 91.9 %). Forces are identical "
                              "(620.06/353.51/-68.95 ↔ 620.1/353.5/-69.0; 655.55/-352.07/71.29 ↔ 655.6/-352.1/71.3). Recomputing η2 from the printed "
                              "NSd/MSd/NRd/MRd gives 0.913 and 0.894, so the listing percentages use a different measure. UNRESOLVED.",
         "src": "P242 table, P297 table, P1714 table, P1751 table"},
        {"id": "C3", "text": "The body pile sections are not named. Identified as P3 because the printed forces equal the P3 rows of "
                              "§3.5 (P3 is also the pile with the highest listing utilisation, 92.5 %).",
         "src": "P1714 table"},
        {"id": "C4", "text": "Pile shear 'VRd,s' (142.85 kN, min 99.73 kN) is computed with the formula for members WITHOUT shear "
                              "reinforcement (VRd,c, A19.6.2.2(1)); ties are not counted.", "src": "P237 table"},
        {"id": "C5", "text": "Beam section 'P3 - P4 (P3 - P4, Positivos)' (P440-P529) is an exact copy of the 'Negativos' section "
                              "(P351-P437): no sagging-moment check is printed; η_N,M = 0.840 is for MEd,x = -273.71 at 'P3'.",
         "src": "P351-P529"},
        {"id": "C6", "text": "Crack-check heading names 'P5 - P6' (P532) while the summary table is for P3 - P4 (P342 table); image117 "
                              "of the hand check shows Pórtico 6 (P7-P8, P12) with M_qp = 86.66 kN·m; the check then uses +86 kN·m.",
         "src": "P532, P342 table, P569 image117"},
        {"id": "C7", "text": "Beam equilibrium tables: side bars 6/16 (x = ±185 mm) carry σs = 0.00 while bars 7/15 (x = ±335 mm, same "
                              "strain) are counted; reason not printed.", "src": "P381 table, P389 table"},
        {"id": "C8", "text": "fywd printed 400 MPa (not 434.78) in the stirrup resistance VRd,s = 407.15 kN.", "src": "P364 table"},
        {"id": "C9", "text": "Steel printed 'B 500 S' by CYPE (P1591 table, P220 table) vs 'B500 SD' in the project text (P112, P121).",
         "src": "P1591 table, P121"},
        {"id": "C10", "text": "Listing Torsor values are printed with unit '[kN]' (should be kN·m).", "src": "P1614 table"},
        {"id": "C11", "text": "Slab negative bars at axis 2: image123 reads 17Ø12/13 (3?0) with segments 197+163 = 360, image121 reads "
                               "Ø12/13 (390) with 197+193.", "src": "P600 image123, P593 image121"},
        {"id": "C12", "text": "Viga cantil text (P607) gives 4φ20 + cercos φ10/0.10, which does not match any beam in the listing "
                               "(edge beams 2Ø16 + 2Ø16, Ø8/15).", "src": "P607, P1608 table"},
        {"id": "C13", "text": "Crack width limits (wmax) are never printed: every face is 'N.P.(1)' (concrete tension < fct).",
         "src": "P342 table, P1818-P1827 tables"},
        {"id": "C14", "text": "Listing zones where 'Área Nec.' exceeds 'Área Real' (CYPE still reports CUMPLE in §4.3): " + "; ".join(nec_gt_real()),
         "src": "P1608-P1661 tables"},
        {"id": "C15", "text": "Viga cantil hand check (P607): '410/4.65 = 83 kN' — the division gives 88.2 kN; the check still holds "
                               "against the printed 502 kN (4·314 mm²·400 MPa).",
         "src": "P607"},
        {"id": "C16", "text": "Hogging moment at the sea pile: the body check and the listing drawings give a larger value than the "
                               "listing zone table. Pórtico 4 / P3-P4: body MEd,x = -273.71 kN·m at 'P3' (P369 table) = drawing label "
                               "-273.71 (image205), but listing 1/3L 'Momento mín.' = -266.03 kN·m at x = 0.00 (P1620 table). Same "
                               "pattern on every transverse beam, span tramo, drawing label / listing 1/3L M_min at x = 0.00: Pórtico 3 "
                               "(P1-P2) -318.80/-315.48, Pórtico 5 (P5-P6) -312.87/-305.42, Pórtico 6 (P7-P8) -264.00/-256.90, Pórtico 7 "
                               "(P13-P14) -303.83/-296.38, Pórtico 8 (P15-P17) -255.61/-247.96, Pórtico 9 (P16-P18) -291.23/-287.95 kN·m. "
                               "Shear peaks agree (e.g. 471.19 kN at x = 0.00 in both). The document does not say where 'P3' is taken; "
                               "the listing x = 0.00 is therefore not the section of the body bending check, and the 'x from the pile "
                               "face' reading of beams.model_mapping.x_origin_note is only an inference.",
         "src": "P369 table; listing P1614, P1620, P1626, P1632, P1638, P1644, P1650 tables; drawings image204-image210 (P1613-P1649)"},
    ]


def not_in_doc():
    return [
        {"item": "Anchorage lengths (lbd) and lap lengths as computed values", "status": "not printed as check values; lap lengths appear only as dimension labels in the edge-beam drawings (≈115-119 cm top, ≈81-83 cm bottom for 2Ø16, image203/211/212, low-medium confidence); hook legs in the transverse-beam drawings"},
        {"item": "Crack-width calculation values (wk, sr,max, σs, εsm-εcm, ρp,eff, Ac,eff, hc,eff, k1..k4, kt, wmax)", "status": "not printed: all faces N.P.(1); only the hand check with σct = 2.20 MPa < 3.2 MPa and image118 (wk = 0.00 mm)"},
        {"item": "Positive-moment (sagging) section check of the transverse beams", "status": "not printed (the 'Positivos' block duplicates the negative one); listing gives only As,nec/As,real per zone"},
        {"item": "Detailed checks for any beam other than P3-P4 and any pile other than P3", "status": "only summary η per check in Apéndice 1 §4.2/§4.3 and As per zone in §2"},
        {"item": "Torsion design values", "status": "only η for P9-P1 and P20-P16 in §4.3 (Tc 4.6 %, Tst 15.3 %, Tsl 9.8/10.0 %, TNMx 86.1/84.6 %, TVy 8.0 %, P1-P2/P16-P18 Tc 4.9 %, TVy 15.7/15.1 %); no detailed torsion calculation"},
        {"item": "Es of reinforcement, fctm of HA-50, fctk,0.05, Ecm used for deflection/cracking", "status": "not printed (Es implied ≈ 200 GPa by εyd = 0.00217)"},
        {"item": "Pile fatigue / durability / crack checks", "status": "pile crack check explicitly skipped (P276, P330)"},
        {"item": "Deflection check details for beams other than P3-P4", "status": "only fT,max / fA,max per tramo (P1830 table, P1608-P1661 tables)"},
        {"item": "Exposure-class based cover calculation (cmin,dur, Δcdev)", "status": "only the result 5 cm (P113/P118/P122) and 'Recubrimiento geométrico 5.0 cm'"},
        {"item": "Formula expressions", "status": "stored as WMF images; partially legible after rendering; see formulas_seen_in_render fields"},
        {"item": "Bar layout of the other transverse beams", "status": "AVAILABLE in the listing drawings image204-image210 (same scheme as P3-P4 for inner frames, 5Ø20 + 1Ø20 ledge for end frames) — see beams.drawings_bar_layout; counts cross-checked by beams.inferred_bar_layouts"},
    ]


def escribir_json(d, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # stand-alone: python3 construir.py OUT.json   (dumps the .docx itself; extraer.py is the normal entry)
    import volcado
    doc = volcado.abrir()
    escribir_json(construir({k: volcado.volcado_rango(doc, lo, hi) for k, (lo, hi) in volcado.RANGOS.items()}), sys.argv[1])
    print("written", sys.argv[1])
