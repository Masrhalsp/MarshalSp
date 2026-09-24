"""Independent modal and response-spectrum analysis of one 40 m module of the Muelle de Trasmallo
(seismic action of sap2000/model/trasmallo.py: SEISMIC, seismic_alpha, SEISMIC_CASES, taken from the
neighbouring Rover project, NCSE-02 elastic spectrum, ac = 0.2435 g).

Model: the stiffness is the independent PyNite model of ``sap2000/tools/verify_pynite.py``
(``build()``: piles, transverse and edge beams, rigid end zones as stiff sub-members, the orthotropic
slab as beam strips along X with EI = 63550 kN m2/m x tributary width).  Two changes for the dynamic
analysis, both to reproduce the SAP2000 model:

* the pin-ended stiff diagonals that emulate the diaphragm in verify_pynite are removed and the
  SAP2000 rigid diaphragm constraint 'TABLERO' is applied exactly (master-slave transformation):
  every joint at Z = 7.25 m has UX = Ux,m - θ·(y - yc), UY = Uy,m + θ·(x - xc), RZ = θ, with the
  master at the centre of mass (xc, yc).  The diagonals leave in-plane mechanisms of the checkerboard
  grid that are stabilised only by the 1e-6 m2 strips; harmless for gravity loads, they would
  produce spurious in-plane modes;
* the 'RIGID' material (rigid zones, section 10 m2 / 10 m4) is lowered from E = 1e11 to 1e8 kN/m2
  (EI = 1e9 kN m2, still > 3700 x the beams and 1.4e4 x the piles; periods change < 0.002 %) to keep
  the condition number of K low: eigen-residuals ~1e-8 instead of ~1e-6 (1e9) or 1e-5 (1e10).

Global stiffness: ``FEModel3D.Ke()`` (sparse, PyNite 3.x; the ``K()`` of older versions), restrained
DOFs (pile bases, fixed) removed, then K_r = Tᵀ·K·T with the diaphragm transformation T.

Mass (mass source of trasmallo.SEISMIC: loads PP + CM + 0.8·Qa, no element self mass, since PP
already carries the member self weight through its self-weight multiplier 1; SAP2000: Elements = No,
Masses = No, Loads = Yes; total 3720 kN): lumped, translational only, equal in X, Y and Z (SAP2000
lumps the mass at the joints and computes no rotational inertia for line elements):
  * frames (self weight of PP): A·γ/g per metre of every sub-member (rigid zones included, as in
    verify_pynite), half to each end, times the weight modifier WMod (pile 6.70/7.25, edge beams) ->
    no double counting of the overlaps.  Were the element self mass used instead (self_mass True),
    SAP2000 would apply MMod = 1 (+30 kN): option ``mass_mod_from_weight=False``;
  * area loads PP (hollow-core plates 4.10 kN/m2), CM and 0.8·Qa: q·A/4 to the four corners of each
    slab cell; frame loads CM, 0.8·Qa (edge strips): half to each end of every sub-member;
  * the bollard loads TB1-3 are not mass; g = 9.80665 m/s2.
Rotational DOFs are massless: M is singular; the generalized eigenproblem K φ = ω² M φ is solved in
shift-invert mode (scipy.sparse.linalg.eigsh, sigma = 0, M positive semi-definite) and checked with
a dense Guyan condensation of the massless DOFs (``dense_check``).

Response spectrum (trasmallo.SEISMIC): Sa(T) = f·ac·α(T)·g, f = 1 (X, Y) or 0.7 (Z), NCSE-02 shape
TA = 0.22 s, TB = 0.88 s, 5 % damping, no ductility reduction; 30 modes; modal responses
r_nd = Γ_nd·Sd(T_n)·(response of φ_n), Sd = Sa/ω²; SRSS over the modes per direction; directional
combination 1.0/0.3/0.3 in the seismic combinations (``directional``).

Member forces per mode: local end forces f = kₑ·Tₘ·dₘ of every PyNite sub-member (no member loads:
inertia forces act at the joints), converted to the CYPE convention of diseno/python/esfuerzos.py:
  piles: N (compression +), Mx, My, Qx, Qy, T as in verify_pynite.pile_head_forces (base reaction
         + statics along the pile; Mx pairs with Qx, My with Qy);
  transverse beams (sea -> land, +Y): M sagging + = -(f5 - f1·s), V = f1 = dM/dy (verify_pynite.beam_line).
Envelopes are positive (SRSS); the sign is applied in the combinations.

Units: kN, m, t (= kN s2/m), s.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.sparse as sps
from scipy.linalg import eigh
from scipy.sparse.linalg import eigsh, splu

HERE = Path(__file__).resolve().parent
DISENO = HERE.parent
ROOT = DISENO.parents[1]
for _p in (str(ROOT / "sap2000" / "tools"), str(ROOT / "sap2000" / "model")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import trasmallo as tm  # noqa: E402
import verify_pynite as vp  # noqa: E402
from Pynite import Analysis  # noqa: E402

G = 9.80665                       # m/s2 (SAP2000 default)
RIGID_E = 1.0e8                   # kN/m2, rigid zones (verify_pynite: 1e11), see module doc
DIRS = ("X", "Y", "Z")
CASE_OF = {"X": "EQX", "Y": "EQY", "Z": "EQZ"}
PILE_COMPS = ("N", "Mx", "My", "Qx", "Qy", "T")
BEAM_COMPS = ("M", "V", "T")

# PyNite axes (x, y up, z = -y_ours).  Translational DOF index and sign for our X, Y, Z.
P_DOF = {"X": (0, 1.0), "Y": (2, -1.0), "Z": (1, 1.0)}


# =============================================================================================
# spectrum
# =============================================================================================
def spectral_acc(T: float, direction: str = "H") -> float:
    """Sa [m/s2] of the NCSE-02 elastic spectrum of trasmallo.SEISMIC (5 % damping)."""
    f = 1.0 if direction in ("H", "X", "Y") else tm.SEISMIC["vertical_factor"]
    return f * tm.SEISMIC["ac_g"] * tm.seismic_alpha(T) * G


# =============================================================================================
# model: stiffness, mass, diaphragm
# =============================================================================================
@dataclass
class Structure:
    model: dict
    fe: object
    K: sps.csr_matrix                 # reduced (free DOFs + diaphragm)
    M: sps.csr_matrix
    T: sps.csr_matrix                 # full (6·n_nodes) <- reduced
    free: np.ndarray                  # full DOF indices of the unrestrained DOFs
    iota: dict                        # direction -> reduced influence vector
    master: tuple                     # (xc, yc) centre of mass of the diaphragm
    node_mass: dict                   # node name -> translational mass [t]
    mass_total: float                 # t (free nodes)
    mass_base: float                  # t lumped at the restrained base joints (does not vibrate)
    diaphragm_nodes: list
    info: dict = field(default_factory=dict)


def _our_xyz(fe, name: str) -> tuple[float, float, float]:
    n = fe.nodes[name]
    return n.X, -n.Z, n.Y


def lumped_masses(model: dict, fe, mass_mod_from_weight: bool = True) -> tuple[dict, dict]:
    """Translational mass per node [t] from the mass source of trasmallo.SEISMIC, and a
    breakdown [kN of weight] per source."""
    ms = tm.SEISMIC["mass_source"]
    pat_f = ms["patterns"]
    mass: dict[str, float] = {}
    brk = {"self": 0.0, "PP_area": 0.0, "CM": 0.0, "Qa": 0.0}

    def add(node: str, w_kN: float, key: str) -> None:
        mass[node] = mass.get(node, 0.0) + w_kN / G
        brk[key] += w_kN

    frames = {f["name"]: f for f in model["frames"]}
    # member self weight: from the element self mass (SAP 'Elements', uses MMod) and/or from the
    # self-weight multiplier of the load patterns of the mass source (SAP 'Loads': PP has SelfWtMult 1,
    # uses WMod).  trasmallo: self_mass False + PP 1.0 -> counted once, with WMod.
    swm = {name: mult for name, _, mult, _ in tm.LOAD_PATTERNS}
    f_loads = sum(f * swm.get(p, 0.0) for p, f in pat_f.items())
    f_elem = 1.0 if ms.get("self_mass") else 0.0
    for fr in model["frames"]:
        fs = model["sections"][fr["section"]]
        gamma = next(m.unit_weight for m in model["materials"] if m.name == fs.material)
        wmod = fs.modifiers.get("WMod", 1.0)
        mmod = fs.modifiers.get("MMod", 1.0) if not mass_mod_from_weight else wmod
        w = fs.section.props["Area"] * gamma * (f_loads * wmod + f_elem * mmod)
        if w == 0:
            continue
        for seg, *_ in vp.segments(model, fr):
            for sub in fe.members[seg].sub_members.values():
                L = sub.L()
                add(sub.i_node.name, w * L / 2, "self")
                add(sub.j_node.name, w * L / 2, "self")
    for fl in model["frame_loads"]:
        f = pat_f.get(fl["pattern"], 0.0)
        if not f:
            continue
        for seg, *_ in vp.segments(model, frames[fl["frame"]]):
            for sub in fe.members[seg].sub_members.values():
                L = sub.L()
                add(sub.i_node.name, f * fl["w"] * L / 2, fl["pattern"] if fl["pattern"] != "PP" else "PP_area")
                add(sub.j_node.name, f * fl["w"] * L / 2, fl["pattern"] if fl["pattern"] != "PP" else "PP_area")
    areas = {a["name"]: a for a in model["areas"]}
    for al in model["area_loads"]:
        f = pat_f.get(al["pattern"], 0.0)
        if not f:
            continue
        js = areas[al["area"]]["joints"]
        (x1, y1, _), (x3, y3) = model["joints"][js[0]], model["joints"][js[2]][:2]
        F = f * al["q"] * abs((x3 - x1) * (y3 - y1)) / 4.0
        for j in js:
            add(j, F, "PP_area" if al["pattern"] == "PP" else al["pattern"])
    return mass, brk


def build_structure(mass_mod_from_weight: bool = True, rigid_E: float = RIGID_E) -> Structure:
    model = tm.build_model()
    fe = vp.build(model)
    for name in [n for n in fe.members if n.startswith("DG_")]:     # diaphragm emulation -> constraint
        fe.delete_member(name)
    fe.materials["RIGID"].E = rigid_E
    fe.materials["RIGID"].G = rigid_E / 2.5
    fe.add_load_combo("MODAL", {})
    Analysis._prepare_model(fe)                      # activates the members, numbers nodes
    n = len(fe.nodes)
    K = fe.Ke("MODAL", check_stability=False, sparse=True).tocsr()
    K = (K + K.T) * 0.5

    node_mass, brk = lumped_masses(model, fe, mass_mod_from_weight)
    names = list(fe.nodes)
    restrained = set(model["restraints"])
    mdiag = np.zeros(6 * n)
    for nm, m in node_mass.items():
        i = fe.nodes[nm].ID
        mdiag[6 * i:6 * i + 3] = m
    mass_base = sum(m for nm, m in node_mass.items() if nm in restrained)

    # diaphragm: every node at the deck level (joints and rigid-offset nodes)
    zd = tm.Z_DECK
    dnodes = [nm for nm in names if abs(fe.nodes[nm].Y - zd) < 1e-6]
    md = np.array([node_mass.get(nm, 0.0) for nm in dnodes])
    xy = np.array([_our_xyz(fe, nm)[:2] for nm in dnodes])
    xc, yc = (md @ xy) / md.sum()

    # reduced DOF numbering: [free non-diaphragm DOFs] + [Ux, Uy, θ of the master]
    dset = {fe.nodes[nm].ID for nm in dnodes}
    red_of = {}
    for nm in names:
        if nm in restrained:
            continue
        i = fe.nodes[nm].ID
        for k in range(6):
            if i in dset and k in (0, 2, 4):     # PyNite DX, DZ (horizontal), RY (about vertical)
                continue
            red_of[6 * i + k] = len(red_of)
    nr = len(red_of) + 3
    mUx, mUy, mTh = nr - 3, nr - 2, nr - 1
    rows, cols, vals = [], [], []
    for g, r in red_of.items():
        rows.append(g), cols.append(r), vals.append(1.0)
    for nm in dnodes:
        i = fe.nodes[nm].ID
        x, y, _ = _our_xyz(fe, nm)
        # our UX = Ux - θ (y - yc) -> PyNite DX
        rows += [6 * i, 6 * i]
        cols += [mUx, mTh]
        vals += [1.0, -(y - yc)]
        # our UY = Uy + θ (x - xc) -> PyNite DZ = -UY
        rows += [6 * i + 2, 6 * i + 2]
        cols += [mUy, mTh]
        vals += [-1.0, -(x - xc)]
        # our RZ = θ -> PyNite RY
        rows.append(6 * i + 4), cols.append(mTh), vals.append(1.0)
    T = sps.csr_matrix((vals, (rows, cols)), shape=(6 * n, nr))
    Mf = sps.diags(mdiag).tocsr()
    Kr = (T.T @ K @ T).tocsr()
    Mr = (T.T @ Mf @ T).tocsr()
    Kr = (Kr + Kr.T) * 0.5
    Mr = (Mr + Mr.T) * 0.5
    iota = {}
    for d in DIRS:
        v = np.zeros(6 * n)
        k, s = P_DOF[d]
        for nm in names:
            if nm not in restrained:
                v[6 * fe.nodes[nm].ID + k] = s
        # reduced influence vector: T·r = v on every mass DOF
        r = np.zeros(nr)
        for g, ri in red_of.items():
            r[ri] = v[g]
        if d == "X":
            r[mUx] = 1.0
        elif d == "Y":
            r[mUy] = 1.0
        iota[d] = r
    free = np.array(sorted(red_of))
    mass_total = float(sum(m for nm, m in node_mass.items() if nm not in restrained))
    info = {"n_nodes": n, "n_dof_full": 6 * n, "n_dof_reduced": nr, "n_diaphragm_nodes": len(dnodes),
            "weight_breakdown_kN": brk, "mass_mod_from_weight": mass_mod_from_weight, "rigid_E": rigid_E}
    return Structure(model, fe, Kr, Mr, T, free, iota, (float(xc), float(yc)), node_mass, mass_total,
                     mass_base, dnodes, info)


# =============================================================================================
# eigenproblem
# =============================================================================================
@dataclass
class Modes:
    omega: np.ndarray                 # rad/s
    phi: np.ndarray                   # (n_red, n_modes), M-normalised
    gamma: dict                       # direction -> (n_modes,)
    meff: dict                        # direction -> (n_modes,) t
    mtot: dict                        # direction -> t (unrestrained mass)

    @property
    def T(self) -> np.ndarray:
        return 2 * np.pi / self.omega

    def ratio(self, d: str) -> np.ndarray:
        return self.meff[d] / self.mtot[d]


def solve_modes(st: Structure, n_modes: int | None = None) -> Modes:
    n_modes = n_modes or tm.SEISMIC["n_modes"]
    w2, phi = eigsh(st.K, k=n_modes, M=st.M, sigma=0.0, which="LM")
    order = np.argsort(w2)
    w2, phi = w2[order], phi[:, order]
    mn = np.einsum("ij,ij->j", phi, st.M @ phi)
    phi = phi / np.sqrt(mn)
    for j in range(phi.shape[1]):                        # deterministic sign: largest component +
        if phi[np.argmax(np.abs(phi[:, j])), j] < 0:
            phi[:, j] *= -1
    gamma, meff, mtot = {}, {}, {}
    for d in DIRS:
        L = phi.T @ (st.M @ st.iota[d])
        gamma[d] = L
        meff[d] = L ** 2
        mtot[d] = float(st.iota[d] @ (st.M @ st.iota[d]))
    return Modes(np.sqrt(np.maximum(w2, 0.0)), phi, gamma, meff, mtot)


def dense_check(st: Structure, n_modes: int = 12) -> np.ndarray:
    """Periods of the first ``n_modes`` by Guyan condensation of the massless DOFs and a dense
    generalized symmetric eigensolution (scipy.linalg.eigh) - independent of the shift-invert."""
    mdiag = st.M.diagonal()
    m = np.where(mdiag > 0)[0]
    o = np.where(mdiag <= 0)[0]
    K = st.K.tocsc()
    Koo = K[o][:, o].tocsc()
    Kom = K[o][:, m].toarray()
    lu = splu(Koo)
    X = lu.solve(Kom)
    Kc = K[m][:, m].toarray() - Kom.T @ X
    Kc = (Kc + Kc.T) / 2
    Mc = st.M[m][:, m].toarray()
    w2 = eigh(Kc, Mc, eigvals_only=True, subset_by_index=[0, n_modes - 1])
    return 2 * np.pi / np.sqrt(w2)


# =============================================================================================
# member forces for a reduced displacement vector
# =============================================================================================
def full_disp(st: Structure, u_red: np.ndarray) -> np.ndarray:
    return st.T @ u_red


def _sub_forces(sub, D: np.ndarray) -> np.ndarray:
    """Local end forces of a PyNite sub-member for the full displacement vector D."""
    i, j = sub.i_node.ID, sub.j_node.ID
    d = np.concatenate([D[6 * i:6 * i + 6], D[6 * j:6 * j + 6]])
    return sub.ke() @ (sub.T() @ d)


class Recovery:
    """Pre-computed kₑ·Tₘ of the members used for the design sections."""

    def __init__(self, st: Structure):
        self.st = st
        fe, model = st.fe, st.model
        self.piles = {}
        for fr in model["frames"]:
            if fr["kind"] != "pile":
                continue
            seg = next(sg for sg, a, b, rigid in vp.segments(model, fr) if not rigid)
            subs = list(fe.members[seg].sub_members.values())
            sub = next(s for s in subs if s.i_node.name == fr["i"])
            self.piles[fr["cype"]] = (sub, sub.ke() @ sub.T(), sub.T())
        self.beams = {a: [] for a in range(1, tm.N_AXES + 1)}
        for fr in model["frames"]:
            if fr["kind"] != "beam_t":
                continue
            for seg, a, b, rigid in vp.segments(model, fr):
                for sub in fe.members[seg].sub_members.values():
                    yi = _our_xyz(fe, sub.i_node.name)[1]
                    yj = _our_xyz(fe, sub.j_node.name)[1]
                    kt = sub.ke() @ sub.T()
                    self.beams[fr["axis"]].append((min(yi, yj), max(yi, yj), yi < yj, sub, kt, rigid, seg))
        self.beams_by_frame: dict[str, list] = {}
        for fr in model["frames"]:
            if fr["kind"] == "beam_t":
                segs = {sg for sg, *_ in vp.segments(model, fr)}
                self.beams_by_frame[fr["name"]] = [t for t in self.beams[fr["axis"]] if t[6] in segs]
        for a in self.beams:
            self.beams[a].sort(key=lambda t: (t[0], t[1]))

    @staticmethod
    def _d(sub, D):
        i, j = sub.i_node.ID, sub.j_node.ID
        return np.concatenate([D[6 * i:6 * i + 6], D[6 * j:6 * j + 6]])

    def pile(self, D: np.ndarray, pile: str, zs) -> np.ndarray:
        """(len(zs), 6) CYPE forces (N, Mx, My, Qx, Qy, T) of a pile at heights zs above the base."""
        sub, kt, Tm = self.piles[pile]
        f_loc = kt @ self._d(sub, D)
        Fg = Tm[:6, :6].T @ f_loc[:6]                    # global (PyNite) end forces at the base
        FX, FY, FZ = Fg[0], -Fg[2], Fg[1]
        MX, MY, MZ = Fg[3], -Fg[5], Fg[4]
        zs = np.atleast_1d(np.asarray(zs, float))
        out = np.empty((len(zs), 6))
        out[:, 0] = FZ
        out[:, 1] = -(MY - FX * zs)
        out[:, 2] = MX + FY * zs
        out[:, 3] = -FX
        out[:, 4] = -FY
        out[:, 5] = -MZ
        return out

    def beam(self, D: np.ndarray, axis: int, ys, rigid_ok: bool = True) -> np.ndarray:
        """(len(ys), 3) CYPE forces (M sagging +, V = dM/dy, T) of the transverse beam of ``axis``
        at the global positions ys.  At a node shared by two sub-members the value of the member
        on the + side is returned (``side``='+') unless the position is the last node."""
        ys = np.atleast_1d(np.asarray(ys, float))
        out = np.full((len(ys), 3), np.nan)
        subs = [t for t in self.beams[axis] if rigid_ok or not t[5]]
        for k, y in enumerate(ys):
            cand = [t for t in subs if t[0] - 1e-9 <= y <= t[1] + 1e-9]
            if not cand:
                continue
            ylo, yhi, fwd, sub, kt, rigid, seg = cand[-1] if len(cand) == 1 else \
                min(cand, key=lambda t: (t[5], abs(y - 0.5 * (t[0] + t[1]))))
            f = kt @ self._d(sub, D)
            s = (y - ylo) if fwd else (yhi - y)
            M = -(f[5] - f[1] * s)
            V = f[1]
            if not fwd:                    # member drawn land -> sea: dM/dy = -dM/ds
                V = -V
            out[k] = (M, V, f[3])
        return out

    def beam_frame(self, D: np.ndarray, frame: str, y: float) -> np.ndarray:
        """(M, V, T) at global y on the SAP frame ``frame`` (its PyNite pieces: frame, frame_ZI,
        frame_ZJ; the flexible piece is preferred at the boundaries)."""
        best = None
        for ylo, yhi, fwd, sub, kt, rigid, seg in self.beams_by_frame[frame]:
            if ylo - 1e-4 <= y <= yhi + 1e-4 and (best is None or (best[5] and not rigid)):
                best = (ylo, yhi, fwd, sub, kt, rigid)
        if best is None:
            raise ValueError(f"{frame}: y = {y} outside the frame")
        ylo, yhi, fwd, sub, kt, rigid = best
        f = kt @ self._d(sub, D)
        y = min(max(y, ylo), yhi)                      # SAP stations are printed with 5 decimals
        s = (y - ylo) if fwd else (yhi - y)
        return np.array([-(f[5] - f[1] * s), f[1] if fwd else -f[1], f[3]])

    def beam_both_sides(self, D: np.ndarray, axis: int, y: float) -> list[np.ndarray]:
        """Values of every non-rigid sub-member meeting at y (face sections: both sides)."""
        res = []
        for ylo, yhi, fwd, sub, kt, rigid, seg in self.beams[axis]:
            if rigid or not (ylo - 1e-9 <= y <= yhi + 1e-9):
                continue
            f = kt @ self._d(sub, D)
            s = (y - ylo) if fwd else (yhi - y)
            M = -(f[5] - f[1] * s)
            V = f[1] if fwd else -f[1]
            res.append(np.array([M, V, f[3]]))
        return res


def base_reactions(st: Structure, rec: Recovery, D: np.ndarray) -> np.ndarray:
    """Sum of the pile base reactions (FX, FY, FZ) [kN], our axes."""
    tot = np.zeros(3)
    for pile, (sub, kt, Tm) in rec.piles.items():
        Fg = Tm[:6, :6].T @ (kt @ rec._d(sub, D))[:6]
        tot += (Fg[0], -Fg[2], Fg[1])
    return tot


# =============================================================================================
# response spectrum
# =============================================================================================
PILE_Z = (0.0, 6.70)                  # 'Pie'/'Arranque', 'Cabeza' (esfuerzos.PILE_FREE_LENGTH)


@dataclass
class RSResult:
    st: Structure
    modes: Modes
    rec: Recovery
    sa: dict                          # direction -> (n_modes,) m/s2
    modal_disp: dict                  # direction -> list of full displacement vectors per mode
    base_shear_modal: dict            # direction -> (n_modes, 3) signed base reactions
    base: dict                        # direction -> SRSS (FX, FY, FZ)


def residual_disp(st: Structure, modes: Modes, d: str) -> np.ndarray:
    """Missing-mass (residual rigid) response per unit acceleration: u_r = K⁻¹·M·ι - Σ Γ_n φ_n / ω_n²
    (reduced coordinates).  Multiplied by the zero-period acceleration of the spectrum it is the
    static response of the mass not captured by the modes (ASCE 4 / SAP2000 'missing mass')."""
    lu = splu(st.K.tocsc())
    u_s = lu.solve(st.M @ st.iota[d])
    return u_s - modes.phi @ (modes.gamma[d] / modes.omega ** 2)


def response_spectrum(st: Structure, modes: Modes, missing_mass: tuple = ()) -> RSResult:
    """Modal responses per direction; ``missing_mass`` lists the directions whose residual rigid
    response (``residual_disp`` x Sa(T = 0)) is added as one more term of the SRSS."""
    rec = Recovery(st)
    sa, md, bs, base = {}, {}, {}, {}
    for d in DIRS:
        sa[d] = np.array([spectral_acc(T, "V" if d == "Z" else "H") for T in modes.T])
        md[d] = []
        rows = []
        for n in range(len(modes.omega)):
            u = modes.gamma[d][n] * sa[d][n] / modes.omega[n] ** 2 * modes.phi[:, n]
            D = full_disp(st, u)
            md[d].append(D)
            rows.append(base_reactions(st, rec, D))
        if d in missing_mass:
            D = full_disp(st, residual_disp(st, modes, d) * spectral_acc(0.0, "V" if d == "Z" else "H"))
            md[d].append(D)
            rows.append(base_reactions(st, rec, D))
        bs[d] = np.array(rows)
        base[d] = np.sqrt((bs[d] ** 2).sum(axis=0))
    return RSResult(st, modes, rec, sa, md, bs, base)


def srss(values: np.ndarray) -> np.ndarray:
    """SRSS over the first axis (modes)."""
    return np.sqrt((np.asarray(values) ** 2).sum(axis=0))


def pile_envelopes(rs: RSResult, zs_by_pile: dict | None = None) -> dict:
    """{pile: {'z': zs, 'X'|'Y'|'Z': (len(zs), 6) SRSS envelopes (N, Mx, My, Qx, Qy, T)}}"""
    out = {}
    for pile in rs.rec.piles:
        zs = np.asarray(zs_by_pile.get(pile, PILE_Z) if zs_by_pile else PILE_Z, float)
        e = {"z": zs}
        for d in DIRS:
            e[d] = srss([rs.rec.pile(D, pile, zs) for D in rs.modal_disp[d]])
        out[pile] = e
    return out


def beam_envelopes(rs: RSResult, ys: dict[int, list[float]]) -> dict:
    """{axis: {'y': ys, d: (len(ys), 3) SRSS (M, V, T)}} (values on the + side at shared nodes)."""
    out = {}
    for a, yl in ys.items():
        yl = np.asarray(yl, float)
        e = {"y": yl}
        for d in DIRS:
            e[d] = srss([rs.rec.beam(D, a, yl) for D in rs.modal_disp[d]])
        out[a] = e
    return out


def beam_face_envelope(rs: RSResult, axis: int, y: float) -> dict:
    """SRSS (M, V, T) per direction of every flexible sub-member meeting at y; the larger of the
    sides is returned per component."""
    out = {}
    for d in DIRS:
        per_side = None
        for D in rs.modal_disp[d]:
            vals = rs.rec.beam_both_sides(D, axis, y)
            arr = np.array(vals)
            per_side = arr ** 2 if per_side is None else per_side + arr ** 2
        out[d] = np.sqrt(per_side).max(axis=0)
    return out


def directional(env: dict, lead: str) -> np.ndarray:
    """1.0·E_lead + 0.3·E_others (trasmallo.SEISMIC['directional'], SAP linear add of RS cases)."""
    d1, d2, _ = tm.SEISMIC["directional"]
    return sum((d1 if d == lead else d2) * np.asarray(env[d]) for d in DIRS)


# =============================================================================================
# cross-checks
# =============================================================================================
def static_push(st: Structure, direction: str) -> float:
    """Lateral stiffness [kN/m] of the model for a unit force at the diaphragm master."""
    f = np.zeros(st.K.shape[0])
    f[-3 if direction == "X" else -2] = 1.0
    u = splu(st.K.tocsc()).solve(f)
    return 1.0 / u[-3 if direction == "X" else -2]


def hand_period(st: Structure) -> dict:
    """Fundamental periods by hand: the 14 piles as fixed-base columns under a rigid deck.

    X (along the quay): pile heads practically fixed against rotation by the slab and edge beams:
        k = 12·E·I/h³ per pile, h = 6.70 m flexible length (the rigid top 0.55 m only translates).
    Y (across): 7 portal frames (2 piles + transverse beam), Chopra (1.3.5) with the beam stiffness
        corrected for the rigid ends inside the piles (antisymmetric rotation: 6EI·L²/l³):
        k = 24·E·Ic/h³·(12ρ + 1)/(12ρ + 4),  ρ = (E·Ib·L²/l³)/(2·E·Ic/h),  L = 3.45 m, l = 3.05 m.
    Mass: the whole vibrating mass (Σ free-node mass)."""
    mat = {m.name: m for m in tm.MATERIALS}
    Ec = mat["HA-50"].E
    Ic = st.model["sections"]["PILOTE_40x40"].section.props["I33"]
    h = tm.PILE_LENGTH - tm.PILE_TOP_RIGID
    k_fg = 12 * Ec * Ic / h ** 3
    kx = 14 * k_fg
    Eb = mat["HA-35"].E
    L = tm.Y_PILE_LAND - tm.Y_PILE_SEA
    l = L - 2 * tm.BEAM_RIGID_AT_PILE
    ks = []
    for a in range(1, tm.N_AXES + 1):
        sec = "VIGA_L80x55_ALA15x30" if a in (1, tm.N_AXES) else "VIGA_T50x55_ALAS15x30"
        Ib = st.model["sections"][sec].section.props["I33"]
        rho = (Eb * Ib * L ** 2 / l ** 3) / (2 * Ec * Ic / h)
        ks.append(24 * Ec * Ic / h ** 3 * (12 * rho + 1) / (12 * rho + 4))
    ky = sum(ks)
    m = st.mass_total
    return {"k_pile_fixed_guided": k_fg, "kX": kx, "kY": ky, "mass_t": m,
            "TX": 2 * math.pi * math.sqrt(m / kx), "TY": 2 * math.pi * math.sqrt(m / ky),
            "h": h, "rho_portal": [(Eb * st.model["sections"]["VIGA_T50x55_ALAS15x30"].section.props["I33"]
                                    * L ** 2 / l ** 3) / (2 * Ec * Ic / h)]}


def fundamental(modes: Modes, d: str) -> int:
    return int(np.argmax(modes.meff[d]))


def equivalent_static(st: Structure, modes: Modes, d: str) -> dict:
    """Lateral-force estimate: V = M·Sa(T1) with the whole vibrating mass and the period of the
    mode with the largest effective mass in the direction."""
    n = fundamental(modes, d)
    T1 = float(modes.T[n])
    sa = spectral_acc(T1, "V" if d == "Z" else "H")
    return {"mode": n + 1, "T1": T1, "Sa_g": sa / G, "M_t": modes.mtot[d], "V": modes.mtot[d] * sa,
            "V_meff": float(modes.meff[d][n] * sa)}


# =============================================================================================
# one call
# =============================================================================================
def analyse(n_modes: int | None = None, mass_mod_from_weight: bool = True,
            missing_mass: tuple = ()) -> RSResult:
    st = build_structure(mass_mod_from_weight)
    modes = solve_modes(st, n_modes)
    return response_spectrum(st, modes, missing_mass)
