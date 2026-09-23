"""Markdown companion diseno/ref/cype_design_reference.md, generated from the JSON (step 3 of the extraction).

Purpose
    Human-readable view of cype_design_reference.json: key reference numbers of pile P3 and beam
    P3-P4, materials and factors, pile and beam checks, Apéndice 1 listings, slab, viga cantil,
    caveats and the list of design data not printed in Anejo 10.  Pure formatting: every number is
    taken from the JSON (with its source), so the two files always agree.

Input
    the reference dict (construir.construir) or the JSON file.

Output
    render(d) -> Markdown text (no final newline).

Run (stand-alone)
    python3 diseno/python/extraccion_anejo10/generar_md.py diseno/ref/cype_design_reference.json OUT.md
"""
import json
import sys


def render(d):
    L = []
    w = L.append

    def v(o, unit=True):
        if o is None:
            return "—"
        if isinstance(o, dict) and "value" in o:
            val = o.get("printed", o["value"])
            if val is None:
                return "—"
            if isinstance(val, float) and 0 < abs(val) < 0.001:
                val = f"{val:.6f}"
            u = o.get("unit", "-")
            return f"{val} {u}" if unit and u not in ("-", "") else f"{val}"
        return str(o)

    def s(o):
        return o.get("src", "") if isinstance(o, dict) else ""

    def row(*cells):
        w("| " + " | ".join(str(c) if c is not None else "—" for c in cells) + " |")

    def table(head, rows):
        row(*head)
        row(*["---"] * len(head))
        for r in rows:
            row(*r)
        w("")

    def kv_table(title, dct, keys=None):
        if title:
            w(title)
            w("")
        rows = []
        for k in (keys or dct.keys()):
            o = dct[k]
            if isinstance(o, dict) and "value" in o:
                rows.append((k, v(o), s(o) + (f" — {o['note']}" if o.get("note") else "")))
        table(("item", "value", "source"), rows)

    meta = d["meta"]
    w("# CYPE design reference — Muelle de Trasmallo (piles and beams)")
    w("")
    w("Companion of `cype_design_reference.json`. Everything below is transcribed from Anejo 10 "
      "(`report/A10_CALC_ESTRUCTURAS.docx`), Trasmallo results in the body (P215–P608) and Apéndice 1 "
      "“Listados de cálculo muelle de trasmallo” (P1449–P1835). Muelle de Arrastre and casetas are out of scope. "
      "This page is generated from the JSON, so the two always agree.")
    w("")
    w("## How to read the sources")
    w("")
    for k, t in meta["src_convention"].items():
        w(f"- `{k}` — {t}")
    w("")
    w(f"Extraction: {meta['extraction']}")
    w("")
    w("Sign conventions: " + "; ".join(f"{k}: {t}" for k, t in meta["sign_conventions"].items()) + ".")
    w("")
    w("Anything marked **INFERENCE** is not printed in the document and was deduced (arithmetic or drawings); "
      "everything else is a transcription.")
    w("")

    # ---------------------------------------------------------------- key results
    kr = d["key_results"]
    w("## 1. Key reference numbers")
    w("")
    w("### Pile P3 (the governing pile), 12Ø25, ties Ø10/150")
    w("")
    h = kr["pile_P3_head_forjado"]
    b2 = kr["pile_P3_base_empotramiento"]
    rows = []
    for k in ("NEd", "MEd_x_first_order", "MEd_y_first_order", "eta_1", "MSd_x_second_order", "MSd_y_second_order", "eta_2",
              "shear_eta_VRdmax", "VRd_max", "listing_aprov_pct"):
        rows.append((k, v(h.get(k)), s(h.get(k)) if h.get(k) else "", v(b2.get(k)), s(b2.get(k)) if b2.get(k) else ""))
    table(("quantity", "head section 'FORJADO 1'", "source", "base section 'EMPOTRAMIENTO'", "source"), rows)
    w(f"Head only: e2 = {v(h['e2'])}, λ = {v(h['lambda'])}, λlim = {v(h['lambda_lim'])}, "
      f"VRd,c (printed 'VRd,s') = {v(h['VRd_c'])} with η = {v(h['shear_eta_VRdc'])}, As,min = {v(h['As_min'])}, "
      f"As,max = {v(h['As_max'])}. Combination: {v(h['combination'])}.")
    w("")
    w("### Transverse beam P3–P4 (Pórtico 4, inverted T 50x55+15x30+15x30)")
    w("")
    kv_table("", kr["beam_P3_P4"])

    # ---------------------------------------------------------------- materials
    m = d["materials_and_parameters"]
    w("## 2. Materials and design parameters used by CYPE")
    w("")
    kv_table("### HA-50 (piles)", m["HA50_piles_as_used_by_CYPE"])
    kv_table("### HA-35 (beams)", m["HA35_beams_as_used_by_CYPE"])
    kv_table("### B 500 S", m["B500S_as_used_by_CYPE"])
    w("### Concretes (§1.11.1) and steel (§1.11.2)")
    w("")
    table(("elemento", "hormigón", "fck MPa", "γc", "árido", "max mm", "Ec MPa", "source"),
          [(c["elemento"], c["hormigon"], c["fck_MPa"], c["gamma_c"], c["arido"], c["arido_max_mm"], c["Ec_MPa"], c["src"])
           for c in m["concretes_1_11_1"]])
    st = m["steel_bars_1_11_2_1"]
    w(f"Steel: {st['acero']} fyk {st['fyk_MPa']} MPa, γs {st['gamma_s']} ({st['src']}). Project text: "
      + "; ".join(f"{v(x)} ({s(x)})" for x in m["project_materials_text"]["piles"]) + ".")
    w("")
    w("### Partial and combination factors (§1.6.1)")
    w("")
    rows = []
    for name, blk in m["partial_and_combination_factors_1_6_1"].items():
        for act, r in blk["rows"].items():
            rows.append((name, act, r["gamma_fav"], r["gamma_desfav"], r["psi_p"], r["psi_a"], r["src"]))
    table(("state", "action", "γ fav", "γ desf", "ψp", "ψa", "source"), rows)
    qp = m["quasi_permanent_combination"]
    w(f"Quasi-permanent combination printed by CYPE: “{v(qp['as_printed'])}” ({s(qp['as_printed'])}); "
      f"ψ2 of Qa = {v(qp['psi2_Qa'])}; ψ2 of the bollard pull ('viento') = {v(qp['psi2_tiro_bolardo_viento'])} "
      f"({s(qp['psi2_tiro_bolardo_viento'])}). The 22 + 22 + 8 CYPE combinations (§1.6.2) are in the JSON "
      "(`materials_and_parameters.combinations_1_6_2`).")
    w("")

    # ---------------------------------------------------------------- piles
    P = d["piles"]
    w("## 3. Piles")
    w("")
    g = P["general"]
    w("### 3.1 Section and CYPE naming")
    w("")
    kv_table("", P["section_1_forjado_cabeza"]["datos_del_pilar"])
    w(f"Arranque section (P281 table): Tramo {v(P['section_2_empotramiento_arranque']['datos_del_pilar']['Tramo'])}, "
      f"altura libre {v(P['section_2_empotramiento_arranque']['datos_del_pilar']['Altura libre'])}, "
      f"estribos {v(P['section_2_empotramiento_arranque']['datos_del_pilar']['Estribos'])}.")
    w("")
    w(f"Sketch: {v(g['section_sketch'])} ({s(g['section_sketch'])}).")
    w("")
    w("Model mapping (from `sap2000/model/trasmallo.py`):")
    w("")
    table(("axis", "X (m)", "sea pile (Y=0)", "land pile (Y=3.45)", "edge / bollard point"),
          [(r["axis"], r["X_m"], r["pile_sea"], r["pile_land"], r["edge_point"]) for r in g["model_mapping"]["by_axis"]])
    w("Coefficients §1.9 (P1554/P1557 tables): empotramiento cabeza/pie 1.00/1.00, pandeo X/Y 1.00/1.00, "
      "coeficiente de rigidez axil 2.00 for all piles; P9–P12, P19–P21 are CHS 159.0x5.0 points 'sin vinculación exterior'.")
    w("")
    for tag, sec in (("3.2 Section 1 — 'FORJADO 1' (pile head, P3)", P["section_1_forjado_cabeza"]),
                     ("3.3 Section 2 — 'EMPOTRAMIENTO' (foundation start / arranque, P3)", P["section_2_empotramiento_arranque"])):
        w(f"### {tag}")
        w("")
        w(f"Heading: “{v(sec['heading'])}” ({s(sec['heading'])}). {sec['identification']['note']}")
        w("")
        det = sec["detailing"]
        if "column_definition" in det:
            w("**Detailing (Disposiciones, A19.8.2 / A19.9.5)**")
            w("")
            rows = []
            for grp in ("column_definition", "longitudinal", "ties"):
                for c in det[grp]["checks"]:
                    rows.append((c["check"][:110], f"{v(c['provided'])} {c['operator']} {v(c['limit'])}", s(c["provided"]).split(":")[0]))
            table(("check", "value", "source"), rows)
            lng, tie = det["longitudinal"], det["ties"]
            w(f"Longitudinal: smin = {v(lng['s_min'])} (s1 {v(lng['s1'])}, s2 {v(lng['s2'])}, s3 {v(lng['s3'])}), Ømax {v(lng['phi_max'])}, "
              f"dg {v(lng['d_g'])}, Ømin {v(lng['phi_min'])}. Ties: smin = {v(tie['s_min'])} (s1 {v(tie['s1'])}, s2 {v(tie['s2'])}, "
              f"s3 {v(tie['s3'])}); scl,max = {v(tie['spacing_limit']['s_cl_max'])} (s1 {v(tie['spacing_limit']['s1'])}, "
              f"s2 {v(tie['spacing_limit']['s2'])}, s3 {v(tie['spacing_limit']['s3'])}). {det['formulas_note']}")
            w("")
            mm = sec["min_max_reinforcement"]
            w("**Minimum / maximum reinforcement (A19.9.5.2)**")
            w("")
            table(("check", "value", "source"),
                  [(c["check"][:110], f"{v(c['provided'])} {c['operator']} {v(c['limit'])}", s(c["provided"]).split(":")[0]) for c in mm["checks"]])
            w(f"A's,min uses NEd = {v(mm['As_min_compression']['NEd'])}. {mm['As_min_compression']['note']}. {mm['As_min_total_note']}.")
            w("")
        else:
            w(f"Detailing and min/max reinforcement: “{v(det)}” ({s(det)}).")
            w("")
        sh = sec["shear"]
        w("**Shear (A19.6.2)**")
        w("")
        rows = [("η (VRd,max)", v(sh["eta_1_VRdmax"]), s(sh["eta_1_VRdmax"])),
                ("VEd,x / VEd,y", f"{v(sh['VEd_x_eta1'])} / {v(sh['VEd_y_eta1'])}", s(sh["VEd_y_eta1"])),
                ("VRd,max", v(sh["VRd_max"]), s(sh["VRd_max"])),
                ("position / combination (η VRd,max)", f"{v(sh['position_eta1'])} / {v(sh['combination_eta1'])}", s(sh["combination_eta1"]))]
        if "eta_2_VRd" in sh:
            rows += [("η (VRd,c, printed 'VRd,s')", v(sh["eta_2_VRd"]), s(sh["eta_2_VRd"])),
                     ("VEd,x / VEd,y", f"{v(sh['VEd_x_eta2'])} / {v(sh['VEd_y_eta2'])}", s(sh["VEd_y_eta2"])),
                     ("VRd,c (printed 'VRd,s')", v(sh["VRd_s_printed"]), s(sh["VRd_s_printed"])),
                     ("position / combination (η VRd,c)", f"{v(sh['position_eta2'])} / {v(sh['combination_eta2'])}", s(sh["combination_eta2"]))]
        table(("item", "value", "source"), rows)
        rows = []
        for k in sh["compression_strut_dir_X"]:
            rows.append((k, v(sh["compression_strut_dir_X"][k]), v(sh["compression_strut_dir_Y"][k])))
        table(("VRd,max parameter", "direction X", "direction Y"), rows)
        if "concrete_no_shear_reinf_dir_X" in sh:
            rows = [(k, v(sh["concrete_no_shear_reinf_dir_X"][k]), v(sh["concrete_no_shear_reinf_dir_Y"][k]))
                    for k in sh["concrete_no_shear_reinf_dir_X"]]
            table(("VRd,c parameter", "direction X", "direction Y"), rows)
        nm = sec["normal_forces"]
        w("**Axial force + biaxial bending (A19.5.8.8, A19.6.1)**")
        w("")
        w(f"Position {v(nm['position'])}, combination {v(nm['combination'])}; η1 = {v(nm['eta_1_section_resistance'])}, "
          f"η2 = {v(nm['eta_2_instability'])} ({s(nm['eta_2_instability'])}).")
        w("")
        f1 = nm["section_resistance_first_order"]
        f2 = nm["instability_second_order"]
        table(("item", "first order (η1)", "second order (η2)"),
              [("N", v(f1["NEd"]), v(f2["NSd"])), ("M x", v(f1["MEd_x"]), v(f2["MSd_x"])), ("M y", v(f1["MEd_y"]), v(f2["MSd_y"])),
               ("NRd", v(f1["NRd"]), v(f2["NRd"])), ("MRd,x", v(f1["MRd_x"]), v(f2["MRd_x"])), ("MRd,y", v(f1["MRd_y"]), v(f2["MRd_y"])),
               ("ee,x / ee,y", f"{v(f1['ee_x'])} / {v(f1['ee_y'])}", ""), ("emin", v(f1["axis_x"]["emin"]), "")])
        rows = [(k, v(f2["axis_x"][k]), v(f2["axis_y"][k])) for k in f2["axis_x"]]
        table(("slenderness / 2nd-order parameter", "'En el eje x'", "'En el eje y'"), rows)
        w("Formulas (legible parts of the equation images completed with the EC2 5.8.8 expressions that reproduce the printed numbers — not verbatim): " + "; ".join(f2["formulas_seen_in_render"]) + ".")
        w("")
        cap = nm["capacity_diagram_labels"]
        w("Capacity diagram labels: " + "; ".join(f"{k} = {v(o)}" for k, o in cap.items()) + f" ({s(cap['N_max_compression'])}).")
        w("")
        for lab, eq in (("at ultimate (same eccentricities)", nm["equilibrium_at_ultimate"]),
                        ("for the design forces", nm["equilibrium_at_design_forces"])):
            w(f"Section equilibrium {lab} — {eq['bars']['rows'][0]['src'].split(':')[0]}:")
            w("")
            table(("bar", "Ø", "x mm", "y mm", "σs MPa", "ε"),
                  [(r["bar"], r["designation"], f"{r['x_mm']:.2f}", f"{r['y_mm']:.2f}", f"{r['sigma_s_MPa']:+.2f}", f"{r['eps']:+.6f}") for r in eq["bars"]["rows"]])
            res = eq["resultants"]
            w("Resultants: " + "; ".join(f"{k} {v(r['resultant'])} (ex {v(r['e_x'])}, ey {v(r['e_y'])})" for k, r in res.items())
              + ". Summary values: " + ", ".join(f"{x['symbol']} {v(x)}" for x in eq["summary_values"])
              + ". Diagram: " + ", ".join(f"{k} {v(o)}" for k, o in eq["diagram_labels"].items()) + ".")
            w("")
        w(f"Cracking: “{v(sec['cracking'])}” ({s(sec['cracking'])}).")
        w("")

    ap = P["appendix_1_section_3"]
    w("### 3.4 Apéndice 1 §3–§4: all piles")
    w("")
    w("Armado (§3.2, P1692 table): every pile 40x40, 4Ø25 esquina + 4Ø25 cara X + 4Ø25 cara Y (cuantía 3.68 %), "
      "Forjado 1 estribos 2eØ10+1eØ10 at 15 cm, Cimentación 1eØ8.")
    w("")
    rows = []
    per = ap["elu_checks_4_2"]
    arm = {(r["pilar"], r["planta"]): r for r in ap["armado_pilares_3_2"]["rows"]}
    for pile, blk in per.items():
        cab = [r for r in blk["rows"] if r["posicion"] == "Cabeza"][0]
        pie = [r for r in blk["rows"] if r["posicion"] == "Pie"][0]
        arr = [r for r in blk["rows"] if r["posicion"] == "Arranque"][0]
        rows.append((pile, cab["Q_pct"], cab["NM_pct"], pie["Q_pct"], pie["NM_pct"], arr["Q_pct"], arr["NM_pct"],
                     arm[(pile, "Forjado 1")]["aprov_pct"], arm[(pile, "Cimentación")]["aprov_pct"], blk["src"]))
    table(("pile", "Cabeza Q %", "Cabeza N,M %", "Pie Q %", "Pie N,M %", "Arranque Q %", "Arranque N,M %",
           "§3.2 aprov Forjado", "§3.2 aprov Cimentación", "source"), rows)
    w("Governing forces per position (§3.5, P1714 table; N > 0 compression; 'N,M' rows include 2nd-order amplification):")
    w("")
    table(("pile", "position", "naturaleza", "N kN", "Mxx kN·m", "Myy kN·m", "Qx kN", "Qy kN", "pésima", "aprov %"),
          [(r["pilar"], r["posicion"], r["naturaleza"], r["N_kN"], r["Mxx_kNm"], r["Myy_kNm"], r["Qx_kN"], r["Qy_kN"], r["pesima"], r["aprov_pct"])
           for r in ap["pesimos_3_5"]["rows"]])
    w("Combinations: G, V = PP+CM+1.5·Tirobolardo; G, Q, V = 1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo (notes of the §4.2 tables).")
    w("")
    md = ap["medicion_3_6"]
    w(f"Medición (§3.6): encofrado {v(md['encofrado'])}, hormigón {v(md['hormigon_HA50'])}, Ø25 {v(md['long_Ø25'])}, "
      f"Ø10 {v(md['estribos_Ø10'])}, Ø8 {v(md['estribos_Ø8'])}, total +10 % {v(md['total_plus_10pct'])}, cuantía {v(md['cuantia'])}.")
    w("")
    w("Per-hypothesis head/base forces (§3.3) are in the JSON (`piles.appendix_1_section_3.esfuerzos_por_hipotesis_3_3`).")
    w("")

    # ---------------------------------------------------------------- beams
    B = d["beams"]
    bb = B["body_check_P3_P4"]
    w("## 4. Beams")
    w("")
    w("### 4.1 Mapping CYPE pórticos ↔ model")
    w("")
    mp = B["model_mapping"]
    table(("axis", "X m", "CYPE pórtico", "section", "cantilever tramo (sea)", "span tramo", "model frames"),
          [(r["axis"], r["X_m"], r["portico"], r["section"], r["tramo_cantilever_sea"], r["tramo_span"], r["model_frames"])
           for r in mp["transverse_beams"]])
    w("Cantilever tramo: from the sea-edge / bollard point (CYPE CHS 159.0x5.0 'punto fijo' Y = -0.45, 'mitad inferior'; model Y = -0.375) "
      "to the sea pile (Y = 0.00); CYPE L = 0.10 m (clear length between the CHS and the pile face).")
    w("Span tramo: c/c 3.45 m, CYPE L = 3.05 m (clear span between pile faces).")
    w("")
    for e in mp["edge_beams"]:
        w(f"- {e['portico']} (25x30): {e.get('tramo', ', '.join(e.get('tramos', [])))} — {e['line']}; {e['note']} Model: {e['model_frames']}.")
    w(f"- {mp['no_portico_2']}")
    w(f"- {mp['x_origin_note']}")
    w("")
    w("### 4.2 Body check of P3–P4")
    w("")
    kv_table("", bb["datos_de_la_viga"])
    w("Bars (drawing image97, P336 table): " + "; ".join(bb["bar_layout_drawing_image97"]["labels"]) + ". Stirrups: Asw 2.36 cm² at 100 mm "
      "(P364 table); listing drawings show 37x{(1eØ10+1rØ10)+(1eØ10)}/10.")
    w("")
    r0 = bb["summary_resistance"]["rows"][0]
    w(f"Summary (P340 table): Q η = {r0['Q']['eta_pct']} % at '{r0['Q']['x']}', N,M η = {r0['N,M']['eta_pct']} % at '{r0['N,M']['x']}', "
      f"torsion checks N.P., Estado {r0['Estado']['raw']}. Cracking (P342 table): all faces N.P.(1), Vfis Cumple. "
      f"Deflection (P345 table): fT,max {v(bb['summary_deflection']['long_term']['fT,max'])} ≤ {v(bb['summary_deflection']['long_term']['fT,lim'])} (L/250), "
      f"fA,max {v(bb['summary_deflection']['active']['fA,max'])} ≤ {v(bb['summary_deflection']['active']['fA,lim'])} (L/500).")
    w("")
    ng = bb["section_negativos_P3_1448"]
    w(f"#### Section “{v(ng['heading'])}”")
    w("")
    rows = []
    for grp in ("detailing_longitudinal", "detailing_stirrups", "min_reinforcement"):
        for c in ng[grp]["checks"]:
            rows.append((c["check"][:110], f"{v(c['provided'])} {c['operator']} {v(c['limit'])}", s(c["provided"]).split(":")[0]))
    for grp in ("spacing", "min_shear_ratio"):
        for c in ng["shear"][grp]["checks"]:
            rows.append((c["check"][:110], f"{v(c['provided'])} {c['operator']} {v(c['limit'])}", s(c["provided"]).split(":")[0]))
    table(("check", "value", "source"), rows)
    w(f"Longitudinal smin = {v(ng['detailing_longitudinal']['s_min'])} (s1 {v(ng['detailing_longitudinal']['s1'])}, s2 {v(ng['detailing_longitudinal']['s2'])}, "
      f"s3 {v(ng['detailing_longitudinal']['s3'])}); sb = {v(ng['detailing_longitudinal']['s_b_max_spacing'])}. As,min: z {v(ng['min_reinforcement']['z'])}, "
      f"W {v(ng['min_reinforcement']['W'])}, fct,m,fl {v(ng['min_reinforcement']['fct_m_fl'])}, fyd {v(ng['min_reinforcement']['fyd'])}.")
    w("")
    sh = ng["shear"]
    w(f"Shear at {v(sh['position'])}, combination {v(sh['combination'])}:")
    w("")
    rows = [("η VRd,max / η VRd,s", f"{v(sh['eta_1_VRdmax'])} / {v(sh['eta_2_VRds'])}", s(sh["eta_2_VRds"])),
            ("VEd,y", v(sh["VEd_y"]), s(sh["VEd_y"])), ("VRd,max", v(sh["VRd_max_Vy"]), s(sh["VRd_max_Vy"])),
            ("VRd,s", v(sh["VRd_s_Vy"]), s(sh["VRd_s_Vy"]))]
    rows += [(f"strut: {k}", v(o), s(o)) for k, o in sh["compression_strut_dir_Y"].items()]
    rows += [(f"stirrups: {k}", v(o), s(o)) for k, o in sh["stirrups_dir_Y"].items()]
    rows += [(f"spacing: {k}", v(o), s(o)) for k, o in sh["spacing"]["longitudinal"].items()]
    rows += [(f"spacing: {k}", v(o), s(o)) for k, o in sh["spacing"]["transverse_legs"].items()]
    rows += [(f"min ratio: {k}", v(o), s(o)) for k, o in sh["min_shear_ratio"].items() if isinstance(o, dict) and "value" in o]
    table(("item", "value", "source"), rows)
    bd = ng["bending"]
    w(f"Bending at {v(bd['position'])} ({v(bd['combination'])}): MEd,x = {v(bd['MEd_x'])}, MRd,x = {v(bd['MRd_x'])}, η = {v(bd['eta'])}.")
    w("")
    for lab, eq in (("at ultimate", bd["equilibrium_at_ultimate"]), ("for the design forces", bd["equilibrium_at_design_forces"])):
        w(f"Equilibrium {lab} — {eq['bars']['rows'][0]['src'].split(':')[0]}:")
        w("")
        table(("bar", "Ø", "x mm", "y mm", "σs MPa", "ε"),
              [(r["bar"], r["designation"], f"{r['x_mm']:.2f}", f"{r['y_mm']:.2f}", f"{r['sigma_s_MPa']:+.2f}", f"{r['eps']:+.6f}") for r in eq["bars"]["rows"]])
        w("Resultants: " + "; ".join(f"{k} {v(r['resultant'])} (ey {v(r['e_y'])})" for k, r in eq["resultants"].items())
          + ". Summary: " + ", ".join(f"{x['symbol']} {v(x)}" for x in eq["summary_values"])
          + ". Diagram: " + ", ".join(f"{k} {v(o)}" for k, o in eq["diagram_labels"].items()) + ".")
        w("")
    w(bd["bar_notes"])
    w("")
    w("Torsion: every torsion check “" + v(ng["torsion"][0]["result"]) + "” (P397–P435); comment P437: “" + v(ng["torsion_comment"]) + "”.")
    w("")
    w(f"The “Positivos” block: {bb['section_positivos_P3_P4']['note']['note']}")
    w("")
    cr = bb["cracking"]
    hc = cr["hand_check"]
    w("#### Cracking (body, P531–P575)")
    w("")
    w(f"Heading beam: “{v(cr['beam_named'])}” — {cr['beam_named']['note']} All 8 faces + minimum area: “{v(cr['faces'][0]['result'])}”.")
    w("")
    w(f"Hand check: “{v(hc['text_1'])}” — image117 labels: M(P8) {v(hc['quasi_permanent_moments_image117']['labels']['M_at_P8'])}, "
      f"M span {v(hc['quasi_permanent_moments_image117']['labels']['M_span_max'])}, M(P7) {v(hc['quasi_permanent_moments_image117']['labels']['M_at_P7'])}. "
      f"“{v(hc['text_2'])}”.")
    w("")
    im = hc["stress_check_image118"]
    table(("image118 value", "value"), [(k, v(o)) for k, o in im.items() if isinstance(o, dict) and "value" in o])
    w(f"Conclusion (P575): “{v(hc['conclusion'])}”")
    w("")
    df = bb["deflection"]
    w("#### Deflection (P577–P588)")
    w("")
    w(f"{v(df['statement'])}. fT,max {v(df['fT_max'])} ≤ fT,lim {v(df['fT_lim'])} = L/250 with L = {v(df['L_ref'])}.")
    w("")
    table(("escalón", "ti d", "tf d", "f0(ti) mm", "Δfi(ti) mm", "f(ti) mm", "fdif mm", "ftot mm", "ftot,max mm"),
          [(r["escalon"], r["ti_dias"], r["tf_dias"], r["f0_ti_mm"], r["dfi_ti_mm"], r["f_ti_mm"], r["fdif_mm"], r["ftot_mm"], r["ftot_max_mm"]) for r in df["history"]])

    w("### 4.3 Apéndice 1 §2 “Listado de armado de vigas” (all pórticos)")
    w("")
    w("M in kN·m (negative = hogging), V in kN, T in kN·m (printed '[kN]'), x in m from the origin of the tramo, areas in cm² "
      "(Asw in cm²/m); '—' = '--' in the listing.")
    w("")
    rows = []
    for pn, pv in B["listing_armado_vigas_2"]["porticos"].items():
        for tn, tv in pv["tramos"].items():
            for z in tv["zones"]:
                def mx(a, xk):
                    return "—" if z[a] is None else f"{z[a]} @{z[xk]}"
                rows.append((pn, tn, tv["section"]["value"], z["zone"], mx("M_min", "x_M_min"), mx("M_max", "x_M_max"),
                             mx("V_min", "x_V_min"), mx("V_max", "x_V_max"), mx("T_min", "x_T_min"), mx("T_max", "x_T_max"),
                             f"{z['As_top_real']}/{z['As_top_nec']}", f"{z['As_bot_real']}/{z['As_bot_nec']}",
                             f"{z['Asw_per_m_real']}/{z['Asw_per_m_nec']}", z["src"].split(":")[0]))
    table(("pórtico", "tramo", "section", "zone", "M min @x", "M max @x", "V min @x", "V max @x", "T min @x", "T max @x",
           "As sup real/nec", "As inf real/nec", "Asw real/nec", "src"), rows)
    rows = []
    for pn, pv in B["listing_armado_vigas_2"]["porticos"].items():
        for tn, tv in pv["tramos"].items():
            f = tv["flechas"]
            rows.append((pn, tn, f["activa"]["printed"], f["plazo_infinito"]["printed"]))
    table(("pórtico", "tramo", "F. activa", "F. a plazo infinito"), rows)

    w("### 4.4 Apéndice 1 §4.3 checks per tramo")
    w("")
    rows = []
    chk = B["appendix_checks_4_3"]
    defl = {r["viga"]: r for r in chk["deflection"]["rows"]}
    for r in chk["resistance"]["rows"]:
        def e(k):
            c = r.get(k)
            if isinstance(c, dict):
                return (f"{c['eta_pct']} %" if "eta_pct" in c else c["raw"]) + (f" @'{c['x']}'" if "x" in c else "")
            return c
        tors = ", ".join(f"{k} {e(k)}" for k in ("Tc", "Tst", "Tsl", "TNMx", "TVy") if isinstance(r.get(k), dict))
        dd = defl.get(r["viga"], {})
        rows.append((r["viga"], e("Q"), e("N,M"), tors or "N.P.", r["Estado"]["raw"],
                     f"{dd.get('fT,max')}/{dd.get('fT,lim')}", f"{dd.get('fA,max')}/{dd.get('fA,lim')}", r["src"].split(":")[0]))
    table(("tramo", "Q", "N,M", "torsion η", "Estado", "fT,max/lim mm", "fA,max/lim mm", "src"), rows)
    w("Cracking (P1818–P1826 tables): every tramo N.P.(1) on all faces and σsr, Vfis Cumple, Estado CUMPLE.")
    w("")

    w("### 4.5 Bar schedules from the listing drawings (images 203–212)")
    w("")
    dr = B["drawings_bar_layout"]
    w(dr["note"])
    w("")
    for k, o in dr.items():
        if k == "note":
            continue
        parts = [f"**{k}** ({o['src']}, confidence {o['confidence']})"]
        for kk in ("section", "upper", "stirrups", "lower", "same_bars_as", "top_bars", "top_laps", "bottom_bars", "bottom_laps"):
            if kk in o:
                parts.append(f"{kk}: {o[kk] if not isinstance(o[kk], list) else ', '.join(map(str, o[kk]))}")
        parts.append("envelope labels: " + json.dumps(o["envelope_labels"], ensure_ascii=False))
        w("- " + "; ".join(parts))
    w("")
    w("### 4.6 Bar counts from As,real (INFERENCE)")
    w("")
    for k, o in B["inferred_bar_layouts"].items():
        w(f"- {k}: {o if not isinstance(o, dict) else json.dumps(o, ensure_ascii=False)}")
    w("")

    # ---------------------------------------------------------------- slab, cantil
    A = d["alveoplacas"]
    w("## 5. Alveoplacas (P592–P605, Apéndice 1 §1.10)")
    w("")
    w(f"“{v(A['text'])}” ({s(A['text'])}). Envelope (image121): spans M+ {json.dumps(A['envelope_image121']['span_M_pos'])}; supports M− "
      f"{json.dumps(A['envelope_image121']['support_M_neg_by_axis'], ensure_ascii=False)}; V start/end {json.dumps(A['envelope_image121']['span_V_start_end'])} "
      f"({A['envelope_image121']['units']}).")
    w("")
    pc = A["plate_characteristics_image122"]
    w(f"Proposed plate (image122): {pc['referencia']} M.ULT {pc['M_ult']}, M.FIS {pc['M_fis']}, RIG.TOT {pc['rig_tot']}, RIG.FIS {pc['rig_fis']}, "
      f"M.SER.1 {pc['M_ser_1']}, M.SER.2 {pc['M_ser_2']} ({pc['units']}).")
    w("")
    ah = A["armados_hoja_autorizacion"]
    w(f"“{v(ah['text'])}” — plan image123: " + "; ".join(f"{k}: {x}" for k, x in ah["plan_image123"].items() if k not in ("src", "confidence"))
      + ". Negative bars along the pier (image121): " + "; ".join(f"{k} {x}" for k, x in A["envelope_image121"]["negative_bars_labels"].items()) + ".")
    w("")
    table(ah["table_image124"]["columns"], ah["table_image124"]["rows"])
    w("Ficha §1.10 (per 1 m band), positive bending (P1574 table) and negative bending (P1575 table):")
    w("")
    table(("ref", "M ult", "M fis", "EI total", "EI fis", "M serv I", "M serv II", "M serv III"),
          [(r["ref"], r["M_ult_kNm_m"], r["M_fis_kNm_m"], r["EI_total_kNm2_m"], r["EI_fis_kNm2_m"], r["M_serv_I_kNm_m"], r["M_serv_II_kNm_m"], r["M_serv_III_kNm_m"])
           for r in A["ficha_1_10"]["positive_per_1m"]["rows"]])
    table(("refuerzo superior", "M ult tipo", "M ult macizado", "M fis", "EI total", "EI fis", "V ult"),
          [(r["refuerzo_superior"], r["M_ult_tipo_kNm_m"], r["M_ult_macizado_kNm_m"], r["M_fis_kNm_m"], r["EI_total_kNm2_m"], r["EI_fis_kNm2_m"], r["V_ult_kN_m"])
           for r in A["ficha_1_10"]["negative_per_1m"]["rows"]])
    w(f"Plate description (P1566 table): {A['ficha_1_10']['description']['text']}")
    w("")
    C = d["viga_cantil"]
    w("## 6. Viga cantil (P606–P608)")
    w("")
    w(f"“{v(C['text'])}”")
    w("")
    table(("item", "value"), [(k, v(o)) for k, o in C.items() if isinstance(o, dict) and "value" in o and k != "text"])
    w(C["note"])
    w("")
    w("## 7. Discrepancies and caveats")
    w("")
    for c in d["discrepancies_and_caveats"]:
        w(f"- **{c['id']}** — {c['text']} ({c['src']})")
    w("")
    w("## 8. Design data NOT in the document")
    w("")
    for c in d["not_in_document"]:
        w(f"- **{c['item']}** — {c['status']}")
    w("")
    return "\n".join(L)


if __name__ == "__main__":
    txt = render(json.load(open(sys.argv[1], encoding="utf-8")))
    open(sys.argv[2], "w", encoding="utf-8").write(txt)
    print("written", sys.argv[2], txt.count("\n") + 1, "lines")
