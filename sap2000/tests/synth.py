"""Synthetic SAP2000 results from the PyNite solution of the same model data, expressed in
SAP2000 output conventions (independently of the conversion formulas under review).

Frame internal forces are obtained from the PyNite global end forces of the flexible member
plus statics of the piece [I-face, cut], then projected on the SAP2000 default local axes:
    P = F.e1, V2 = F.e2, V3 = F.e3, T = M.e1, M3 = +M.e3, M2 = -M.e2
where F, M are the force / moment vector acting on the positive-1 face of the cut
(CSI: positive M2 causes compression on the +3 face -> moment vector along -2 on the +1 face).
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "tools"))

import trasmallo as tm  # noqa: E402
import verify_pynite as vp  # noqa: E402


def ours(v):
    """PyNite axes (x, y up, z) -> model axes (X, Y, Z up)."""
    return np.array([v[0], -v[2], v[1]], dtype=float)


def sap_local_axes(pi, pj):
    e1 = (pj - pi) / np.linalg.norm(pj - pi)
    if np.linalg.norm(np.cross(e1, [0, 0, 1])) < 1e-3:       # vertical: local 2 = +X
        e2 = np.array([1.0, 0, 0])
    else:                                                    # 1-2 plane vertical, 2 upward
        z = np.array([0, 0, 1.0])
        e2 = z - e1 * (z @ e1)
        e2 /= np.linalg.norm(e2)
    e3 = np.cross(e1, e2)
    return e1, e2, e3


class Synth:
    def __init__(self):
        self.model = tm.build_model()
        self.res, self.fe = vp.run(self.model, with_fe=True)
        self.frames = {f["name"]: f for f in self.model["frames"]}
        self.extra = self.model.get("_extra_nodes", {})
        self.wload = {}
        for fr in self.model["frames"]:
            fs = self.model["sections"][fr["section"]]
            gamma = next(m.unit_weight for m in self.model["materials"] if m.name == fs.material)
            self.wload[(fr["name"], "PP")] = fs.section.props["Area"] * gamma * fs.modifiers.get("WMod", 1.0)
        for fl in self.model["frame_loads"]:
            k = (fl["frame"], fl["pattern"])
            self.wload[k] = self.wload.get(k, 0.0) + fl["w"]
        self._check()

    def _pos(self, n):
        return np.array(self.model["joints"].get(n, self.extra.get(n)), dtype=float)

    def react(self, j, c):
        n = self.fe.nodes[j]
        F = ours((n.RxnFX[c], n.RxnFY[c], n.RxnFZ[c]))
        M = ours((n.RxnMX[c], n.RxnMY[c], n.RxnMZ[c]))
        return (*F, *M)

    def displ(self, j, c):
        n = self.fe.nodes[j]
        U = ours((n.DX[c], n.DY[c], n.DZ[c]))
        R = ours((n.RX[c], n.RY[c], n.RZ[c]))
        return (*U, *R)

    def frame(self, name, s, c):
        fr = self.frames[name]
        pi, pj = self._pos(fr["i"]), self._pos(fr["j"])
        e1, e2, e3 = sap_local_axes(pi, pj)
        li = (fr.get("offsets") or (0.0, 0.0))[0]
        mem = self.fe.members[name]                          # flexible part keeps the frame name
        a = fr["i"] if li <= 0 else f"{name}_RI"
        pa = self._pos(a)
        x = s - li
        assert -1e-9 <= x <= mem.L() + 1e-9, (name, s, x, mem.L())
        fg = mem.T().T @ mem.f(c)                            # global end forces (PyNite axes)
        Fa, Ma = ours(fg[0:3, 0]), ours(fg[3:6, 0])          # actions on the member at end a
        w = self.wload.get((name, c), 0.0)
        Fq = np.array([0, 0, -w * x])
        pc = pa + x * e1
        Fcut = -(Fa + Fq)
        Mcut = -(Ma + np.cross(pa - pc, Fa) + np.cross(pa + 0.5 * x * e1 - pc, Fq))
        return (Fcut @ e1, Fcut @ e2, Fcut @ e3, Mcut @ e1, -(Mcut @ e2), Mcut @ e3)

    def _check(self):
        """Self-check: at the pile base, the cut force must equal minus the support reaction."""
        for fr in self.model["frames"]:
            if fr["kind"] != "pile":
                continue
            for c in tm.PATTERN_ORDER:
                p, v2, v3, t, m2, m3 = self.frame(fr["name"], 0.0, c)
                F1, F2, F3, M1, M2, M3 = self.react(fr["i"], c)
                assert abs(p + F3) < 1e-6 and abs(v2 + F1) < 1e-6 and abs(v3 + F2) < 1e-6, fr["name"]
                # moment vector on the +1 face at the base = -(reaction moment)
                assert abs(-m2 + M1) < 1e-6 and abs(m3 + M2) < 1e-6 and abs(t + M3) < 1e-6, fr["name"]
