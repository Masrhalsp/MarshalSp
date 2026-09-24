"""Seismic analysis and checks of one 40 m module of the Muelle de Trasmallo: runs the independent
modal / response-spectrum analysis (``modal.py``) and the accidental-situation checks
(``comprobaciones.py``) and writes

    diseno/python/output/sismo.json     all numbers (modes, participation, base shears, envelopes, checks)
    diseno/python/output/sismo.md       report

    python3 diseno/python/sismo/run_sismo.py            (~60 s)

The static outputs (pilotes.*, vigas.*, diseno_final.*, Diseno_Codigo_Estructural.xlsx, figures
d0-d8) are only read.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import comprobaciones as C  # noqa: E402
import modal as S  # noqa: E402

tm = S.tm
OUT = C.OUT
JSON_PATH = OUT / "sismo.json"
MD_PATH = OUT / "sismo.md"
MU_SENSITIVITY = 2.0            # NCSE-02 §3.7.3.1: μ = 2 (ductilidad baja) -> β = ν/μ = 0.5 (sensibilidad)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        v = float(o)
        if v != v or v in (float("inf"), float("-inf")):
            return None
        a = abs(v)
        return round(v, 2 if a >= 100 else 3 if a >= 1 else 5 if a >= 1e-3 else 8)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    return o


def run(verbose: bool = True, sensitivity: bool = True) -> dict:
    t0 = time.time()

    def log(msg):
        if verbose:
            print(f"[{time.time() - t0:5.1f} s] {msg}")

    st = S.build_structure()
    modes = S.solve_modes(st)
    rs = S.response_spectrum(st, modes, missing_mass=("Z",))
    rs30 = S.response_spectrum(st, modes)                          # 30 modes only (SAP2000 comparison)
    log(f"modal analysis: {len(modes.omega)} modes, T1 = {modes.T[0]:.3f} s")
    dense = S.dense_check(st, 8)
    push = {d: S.static_push(st, d) for d in ("X", "Y")}
    hand = S.hand_period(st)
    eqs = {d: S.equivalent_static(st, modes, d) for d in S.DIRS}
    tot = tm.load_totals(st.model)
    mp = tm.SEISMIC["mass_source"]["patterns"]
    W_loads = sum(f * tot[p] for p, f in mp.items())
    log("cross-checks done")

    mode_rows = []
    cum = {d: 0.0 for d in S.DIRS}
    for n in range(len(modes.omega)):
        r = {"mode": n + 1, "T": float(modes.T[n]), "f_Hz": float(1 / modes.T[n]),
             "Sa_H_g": S.spectral_acc(modes.T[n], "H") / S.G, "Sa_V_g": S.spectral_acc(modes.T[n], "V") / S.G}
        for d in S.DIRS:
            cum[d] += float(modes.ratio(d)[n])
            r[f"U{d}"] = float(modes.ratio(d)[n])
            r[f"sum_U{d}"] = cum[d]
        mode_rows.append(r)

    pile_res = C.check_piles(rs)
    log("pile checks done")
    beam_res = C.check_beams(rs)
    log("beam checks done")
    ps = C.pile_summary(pile_res, C.static_pile_etas())
    bs = C.beam_summary(beam_res, C.static_beam_etas())
    sens = None
    if sensitivity:
        p2 = C.check_piles(rs, scale=1.0 / MU_SENSITIVITY)
        b2 = C.check_beams(rs, scale=1.0 / MU_SENSITIVITY)
        sens = {"mu": MU_SENSITIVITY, "piles": C.pile_summary(p2, C.static_pile_etas()),
                "beams": C.beam_summary(b2, C.static_beam_etas())}
        log("sensitivity mu = 2 done")

    env = pile_res["env"]
    pile_env_rows = []
    for p in C.pilotes.PILES:
        e = env[p]
        for zi, zv in enumerate(e["z"]):
            if zi not in (0, len(e["z"]) - 1):
                continue
            row = {"pile": p, "z": float(zv)}
            for d in S.DIRS:
                for k, c in enumerate(S.PILE_COMPS):
                    row[f"{c}_{d}"] = float(e[d][zi, k])
            pile_env_rows.append(row)

    gov_p = max(ps, key=lambda r: r["eta_nm"])
    gov_pv = max(ps, key=lambda r: r["eta_v"])
    gov_b = max((r for r in bs if r["variant"] == "dispuesto"), key=lambda r: r["eta_M"])
    gov_bp = max((r for r in bs if r["variant"] == "propuesto"), key=lambda r: r["eta_M"])
    static_p = max(r["eta_nm_static"] for r in ps)
    static_b = max(r["eta_M_static"] for r in bs if r["variant"] == "dispuesto")
    summary = {
        "T": {"X": eqs["X"]["T1"], "Y": eqs["Y"]["T1"], "torsion": float(modes.T[2])},
        "participation_30": {d: float(modes.ratio(d).sum()) for d in S.DIRS},
        "base_shear": {d: float(rs.base[d][i]) for i, d in enumerate(S.DIRS)},
        "base_shear_30_modes": {d: float(rs30.base[d][i]) for i, d in enumerate(S.DIRS)},
        "pile_eta_nm": gov_p["eta_nm"], "pile_eta_nm_at": f"{gov_p['pile']} {gov_p['position']} {gov_p['check']} {gov_p['combo']}",
        "pile_eta_v": gov_pv["eta_v"], "pile_eta_v_at": f"{gov_pv['pile']} {gov_pv['v_position']} {gov_pv['v_combo']}",
        "pile_eta_nm_static": static_p,
        "beam_eta_M": gov_b["eta_M"], "beam_eta_M_at": f"{gov_b['member']} {gov_b['M_section']} {gov_b['M_check']} {gov_b['M_combo']}",
        "beam_eta_M_proposed": gov_bp["eta_M"], "beam_eta_M_static": static_b,
        "beam_eta_links": max(r["eta_links"] for r in bs), "beam_eta_Vmax": max(r["eta_Vmax"] for r in bs),
        "beam_eta_T_info": max(r["eta_T_info"] or 0 for r in bs),
        "governs": True,
    }
    summary["governs"] = summary["pile_eta_nm"] > static_p or summary["beam_eta_M"] > static_b
    summary["holds"] = summary["pile_eta_nm"] <= 1.0 and summary["pile_eta_v"] <= 1.0 and \
        summary["beam_eta_M_proposed"] <= 1.0 and summary["beam_eta_links"] <= 1.0
    if sens:
        summary["sensitivity_mu2"] = {
            "pile_eta_nm": max(r["eta_nm"] for r in sens["piles"]),
            "pile_eta_v": max(r["eta_v"] for r in sens["piles"]),
            "beam_eta_M": max(r["eta_M"] for r in sens["beams"] if r["variant"] == "dispuesto"),
            "beam_eta_M_proposed": max(r["eta_M"] for r in sens["beams"] if r["variant"] == "propuesto"),
            "beam_eta_T_info": max(r["eta_T_info"] or 0 for r in sens["beams"])}

    res = {
        "meta": {
            "module": "diseno/python/sismo (modal.py, comprobaciones.py, run_sismo.py)",
            "seismic": {k: v for k, v in tm.SEISMIC.items() if k != "mass_source"},
            "mass_source": tm.SEISMIC["mass_source"],
            "combinations": tm.seismic_combos(),
            "materials": {"gamma_c": C.GAMMA_C_ACC, "gamma_s": C.GAMMA_S_ACC, "fywd_MPa": C.FYWD,
                          "ref": "CE Anejo 19 Tabla A19.2.1 (situación accidental)"},
            "model": st.info, "master_xy": st.master,
            "runtime_s": round(time.time() - t0, 1),
        },
        "spectrum": {"H": tm.seismic_spectrum("H"), "V": tm.seismic_spectrum("V")},
        "mass": {"W_vibrating_kN": st.mass_total * S.G, "W_base_joints_kN": st.mass_base * S.G,
                 "W_total_kN": (st.mass_total + st.mass_base) * S.G, "W_from_load_totals_kN": W_loads,
                 "load_totals_kN": tot, "breakdown_kN": st.info["weight_breakdown_kN"],
                 "M_vibrating_t": st.mass_total},
        "modes": mode_rows,
        "checks": {
            "periods_eigsh": [float(t) for t in modes.T[:8]], "periods_dense_guyan": [float(t) for t in dense],
            "push_stiffness_kN_m": push,
            "T_rayleigh": {d: float(2 * np.pi * np.sqrt(st.mass_total / push[d])) for d in push},
            "hand": hand, "equivalent_static": eqs,
        },
        "base_shear": {d: {"FX": float(rs.base[d][0]), "FY": float(rs.base[d][1]), "FZ": float(rs.base[d][2])}
                       for d in S.DIRS},
        "base_shear_30_modes": {d: {"FX": float(rs30.base[d][0]), "FY": float(rs30.base[d][1]),
                                    "FZ": float(rs30.base[d][2])} for d in S.DIRS},
        "pile_envelopes": pile_env_rows,
        "beam_envelopes": beam_res["env"],
        "piles": ps, "beams": bs,
        "pile_rows": pile_res["nm"] + pile_res["shear"], "beam_rows": beam_res["rows"],
        "sensitivity": sens,
        "summary": summary,
    }
    res["meta"]["runtime_s"] = round(time.time() - t0, 1)
    return _clean(res)


# =============================================================================================
# report
# =============================================================================================
def _f(v, nd=3):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _table(rows, cols):
    out = ["| " + " | ".join(h for _, h, _ in cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(_f(r.get(k), nd) for k, _, nd in cols) + " |")
    return "\n".join(out) + "\n"


def to_markdown(R: dict) -> str:
    m, s, ck = R["meta"], R["summary"], R["checks"]
    sz = m["seismic"]
    md = ["# Sismo — Muelle de Trasmallo, módulo 40 m (análisis modal espectral independiente)\n",
          "Generado por `python3 diseno/python/sismo/run_sismo.py` (`sismo/modal.py`, `sismo/comprobaciones.py`). "
          f"Tiempo {m['runtime_s']} s. Acción sísmica de `sap2000/model/trasmallo.py` (SEISMIC, proyecto Rover): "
          f"ac = {sz['ac_g']} g, espectro elástico NCSE-02 TA = {sz['TA']} s, TB = {sz['TB']} s, vertical x {sz['vertical_factor']}, "
          f"amortiguamiento {sz['damping']:.0%}, {sz['n_modes']} modos, SRSS, direccional {tuple(sz['directional'])}. "
          "Los resultados de SAP2000 se compararán cuando estén disponibles.\n",
          "## 1. Veredicto\n",
          f"- **El sismo gobierna.** Pilotes: η N-M = {s['pile_eta_nm']:.2f} ({s['pile_eta_nm_at']}) frente a "
          f"{s['pile_eta_nm_static']:.3f} estático; cortante η = {s['pile_eta_v']:.2f} ({s['pile_eta_v_at']}).\n"
          if s["governs"] else "- El sismo no gobierna.\n",
          f"- Vigas transversales: flexión η = {s['beam_eta_M']:.2f} ({s['beam_eta_M_at']}) frente a {s['beam_eta_M_static']:.3f} "
          f"estático; con el armado propuesto η = {s['beam_eta_M_proposed']:.2f} (la armadura inferior añadida no actúa: rige el "
          f"momento negativo en la cara del pilote). Estribos (V + suspensión) η = {s['beam_eta_links']:.2f}, bielas "
          f"η = {s['beam_eta_Vmax']:.2f}. Torsión + cortante (información, (6.29)) η = {s['beam_eta_T_info']:.2f}.\n",
          f"- **El armado propuesto (diseno_final.md) {'se mantiene' if s['holds'] else 'NO se mantiene'} con el sismo elástico** "
          "(sin reducción por ductilidad, como Rover): los pilotes 40x40 con 12Ø25 (As ≈ 0.92·As,máx) no pueden resistir "
          "el momento sísmico; la solución exige otra sección de pilote, más pilotes o una reducción justificada del espectro.\n"]
    if R.get("sensitivity"):
        s2 = s["sensitivity_mu2"]
        md.append(f"- Sensibilidad (no veredicto) con μ = {R['sensitivity']['mu']:g} (NCSE-02 §3.7.3.1, ductilidad baja, "
                  f"fuerzas sísmicas / 2): pilotes η N-M = {s2['pile_eta_nm']:.2f}, cortante {s2['pile_eta_v']:.2f}; vigas "
                  f"flexión {s2['beam_eta_M']:.2f} (propuesto {s2['beam_eta_M_proposed']:.2f}), torsión (info) "
                  f"{s2['beam_eta_T_info']:.2f}.\n")
    md += ["\n## 2. Modelo y masa\n",
           f"Rigidez: modelo PyNite de `sap2000/tools/verify_pynite.py` (`build()`), sin las diagonales que emulan el "
           f"diafragma; diafragma rígido exacto (maestro en el centro de masas X = {m['master_xy'][0]:.3f}, "
           f"Y = {m['master_xy'][1]:.3f} m); {m['model']['n_nodes']} nudos, {m['model']['n_dof_reduced']} GDL reducidos. "
           "Masa concentrada traslacional (X, Y, Z), sin inercia rotacional; fuente de masa = cargas PP (con el peso "
           "propio de las barras, multiplicador 1) + CM + 0.8·Qa, sin masa propia de elementos (no se cuenta dos veces), "
           "como SAP2000 (Elements = No, Masses = No, Loads = Yes).\n\n",
           "| Fuente | Peso [kN] |\n|---|---|\n",
           *[f"| {({'self': 'PP: peso propio de barras', 'PP_area': 'PP: alveoplaca 4.10 kN/m²', 'CM': 'CM', 'Qa': '0.8·Qa'}).get(k, k)} | {v:.1f} |\n"
             for k, v in R["mass"]["breakdown_kN"].items()],
           f"| total (nudos libres + base) | {R['mass']['W_total_kN']:.1f} |\n",
           f"| PP + CM + 0.8·Qa de `load_totals()` | {R['mass']['W_from_load_totals_kN']:.1f} |\n",
           f"| en los nudos de base (no vibra) | {R['mass']['W_base_joints_kN']:.1f} |\n",
           f"| masa que vibra | {R['mass']['W_vibrating_kN']:.1f} kN = {R['mass']['M_vibrating_t']:.2f} t |\n",
           "\n## 3. Modos, periodos y masa participante\n",
           _table(R["modes"], [("mode", "modo", 0), ("T", "T [s]", 4), ("Sa_H_g", "Sa,H/g", 3), ("UX", "UX", 4),
                               ("UY", "UY", 4), ("UZ", "UZ", 4), ("sum_UX", "ΣUX", 4), ("sum_UY", "ΣUY", 4),
                               ("sum_UZ", "ΣUZ", 4)]),
           f"\nΣ 30 modos: X {s['participation_30']['X']:.4f}, Y {s['participation_30']['Y']:.4f}, "
           f"Z {s['participation_30']['Z']:.4f}. La dirección Z (modos locales de la losa) no llega al 90 %: se añade la "
           "respuesta residual de la masa no captada (missing mass) con la aceleración de periodo cero 0.7·ac en EQZ; "
           "sin ella (30 modos, como SAP2000 por defecto) el cortante vertical sería "
           f"{R['base_shear_30_modes']['Z']['FZ']:.0f} kN en lugar de {R['base_shear']['Z']['FZ']:.0f} kN.\n",
           "\n## 4. Comprobaciones cruzadas\n",
           f"- Periodos eigsh (shift-invert) vs. condensación de Guyan densa (eigh): "
           + ", ".join(f"{a:.4f}/{b:.4f}" for a, b in zip(ck["periods_eigsh"][:4], ck["periods_dense_guyan"][:4])) + " s.\n",
           f"- Rayleigh con la rigidez del modelo (fuerza unitaria en el maestro): kX = {ck['push_stiffness_kN_m']['X']:.0f}, "
           f"kY = {ck['push_stiffness_kN_m']['Y']:.0f} kN/m -> TX = {ck['T_rayleigh']['X']:.4f}, TY = {ck['T_rayleigh']['Y']:.4f} s.\n",
           f"- A mano: 14 pilotes 12EI/h³ (h = 6.70 m, cabeza sin giro): kX = {ck['hand']['kX']:.0f} kN/m, "
           f"TX = {ck['hand']['TX']:.3f} s (cota inferior: la losa sólo coacciona parcialmente el giro en X); 7 pórticos "
           f"(Chopra 1.3.5, extremos rígidos de la viga): kY = {ck['hand']['kY']:.0f} kN/m, TY = {ck['hand']['TY']:.3f} s.\n",
           "- Fuerza lateral equivalente V = M·Sa(T1): "
           + "; ".join(f"{d}: T1 = {e['T1']:.3f} s, Sa = {e['Sa_g']:.3f} g, V = {e['V']:.0f} kN (espectral {R['base_shear'][d]['F' + d]:.0f})"
                       for d, e in ck["equivalent_static"].items() if d != "Z") + ".\n",
           "\n## 5. Cortante en la base (SRSS por dirección) [kN]\n",
           "| caso | FX | FY | FZ |\n|---|---|---|---|\n",
           *[f"| EQ{d} | {v['FX']:.1f} | {v['FY']:.1f} | {v['FZ']:.1f} |\n" for d, v in R["base_shear"].items()],
           "\n## 6. Envolventes sísmicas de los pilotes (SRSS, convenio CYPE, z desde el empotramiento)\n",
           _table(R["pile_envelopes"], [("pile", "pilote", 0), ("z", "z", 2)] +
                  [(f"{c}_{d}", f"{c} {d}", 1) for d in ("X", "Y", "Z") for c in ("N", "Mx", "My", "Qx", "Qy")]),
           "\n## 7. Envolventes sísmicas de las vigas transversales (SRSS, M flector +, V = dM/dy) en las caras\n",
           _table(R["beam_envelopes"], [("member", "viga", 0), ("section", "sección", 0), ("y", "y", 2)] +
                  [(f"{c}_{d}", f"{c} {d}", 1) for d in ("X", "Y", "Z") for c in ("M", "V", "T")]),
           "\n## 8. Pilotes: situación accidental (γc 1.3, γs 1.0) frente al estático (ROM, Mode.CODIGO)\n",
           _table(R["piles"], [("pile", "pilote", 0), ("eta_nm1", "η N-M 1er", 3), ("eta_nm", "η N-M (1º/2º)", 3),
                               ("check", "", 0), ("position", "posición", 0), ("combo", "combinación", 0), ("N", "N", 1),
                               ("MEd_x", "MEd,x", 1), ("MEd_y", "MEd,y", 1), ("eta_v", "η cortante", 3),
                               ("eta_nm_static", "η N-M estático", 3), ("eta_v_static", "η V estático", 3)]),
           "\n## 9. Vigas transversales: situación accidental\n",
           _table(R["beams"], [("member", "viga", 0), ("variant", "armado", 0), ("eta_M", "η flexión", 3),
                               ("M_section", "sección", 0), ("M_check", "", 0), ("MEd", "MEd", 1), ("MRd", "MRd", 1),
                               ("M_combo", "combinación", 0), ("eta_Vmax", "η bielas", 3), ("eta_links", "η estribos", 3),
                               ("eta_T_info", "η T+V (info)", 3), ("eta_M_static", "η flexión estático", 3),
                               ("eta_links_static", "η estribos estático", 3)]),
           "\n## 10. Hipótesis y dudas\n",
           "- Espectro elástico sin reducción por ductilidad (μ = 1), como Rover y `trasmallo.SEISMIC`; la sensibilidad "
           "con μ = 2 se da sólo como información.\n",
           "- Combinaciones de signo independientes (N±, M±) de las envolventes SRSS: conservador frente a la correlación modal.\n",
           "- φef = 1.75 (dato de CYPE) en el 2º orden, también en sismo (conservador para una acción de corta duración).\n",
           "- La torsión de las vigas transversales bajo EQX (el momento de cabeza de los pilotes pasa a la losa a través de "
           "la viga) es elevada; se da como información, igual que la hipótesis de continuidad de la alveoplaca del modelo.\n",
           "- Peso propio de las barras en la masa a través del patrón PP (multiplicador de peso propio 1, con WMod del "
           "pilote 6.70/7.25), igual que SAP2000 con la masa 'desde cargas'.\n"]
    import re
    txt = re.sub(r"^(#+ .*)\n(?!\n)", r"\1\n\n", "".join(md), flags=re.M)
    return re.sub(r"([^\n])\n(#+ )", r"\1\n\n\2", txt)


def write(R: dict, out: Path = OUT) -> tuple[Path, Path]:
    out.mkdir(parents=True, exist_ok=True)
    j, m = out / JSON_PATH.name, out / MD_PATH.name
    j.write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    m.write_text(to_markdown(R), encoding="utf-8")
    return j, m


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--no-sensitivity", action="store_true")
    a = ap.parse_args(argv)
    R = run(sensitivity=not a.no_sensitivity)
    j, m = write(R, Path(a.out))
    print(f"written {j}, {m}")
    s = R["summary"]
    print(f"T1X {s['T']['X']:.3f} s, T1Y {s['T']['Y']:.3f} s; piles η N-M {s['pile_eta_nm']:.2f} (static "
          f"{s['pile_eta_nm_static']:.3f}); beams η M {s['beam_eta_M']:.2f} (static {s['beam_eta_M_static']:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
