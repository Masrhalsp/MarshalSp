"""Reinforced-concrete sections to the Código Estructural, Anejo 19 (= EN 1992-1-1 with the
Spanish national parameters).

Units inside this module: N, mm, MPa (N·mm for moments).  Callers working in kN / kN·m use
``KN`` and ``KNM`` to convert.

Sign convention (the CYPECAD listings of Anejo 10): compression POSITIVE for strains, stresses
and axial force.  x, y are section coordinates about the gross centroid; for beams y is up.

    N  = sum(sigma dA)
    Mx = sum(sigma·y dA)      (positive when the +y fibres are compressed)
    My = sum(sigma·x dA)      (positive when the +x fibres are compressed)

ULS model (A19.6.1): plane sections, perfect bond, no concrete tension, parabola-rectangle
concrete (A19.3.1.7), steel with horizontal top branch (A19.3.2.7(2)b).  Two modes:

* ``Mode.CYPE`` (default): reproduces CYPECAD 2023 exactly (validated to 0.00 % against the
  capacities printed in Anejo 10, see diseno/tests):  the failure plane stops at 99.5 % of the
  strain limits (eps_cu2·0.995, eps_su·0.995 with eps_su = 10 per mil, a CYPE limit), and the
  bars do not displace concrete (gross concrete area).
* ``Mode.CODIGO``: code-strict: eps_cu2 exactly, no steel strain limit (horizontal branch),
  bars displace concrete.

The capacity check follows CYPE: eta = |S|/|R| where R is on the failure surface along the
ray through S = (NEd, MEd,x, MEd,y) ("esfuerzos de agotamiento con las mismas excentricidades").
A fast convex-hull approximation of the whole N-Mx-My surface is used to screen many
combinations; the exact ray solution is then computed for the governing ones.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from scipy.optimize import brentq, least_squares
from scipy.spatial import ConvexHull

KN = 1e3            # N per kN
KNM = 1e6           # N·mm per kN·m


class Mode(str, Enum):
    CYPE = "cype"
    CODIGO = "codigo"


# ============================================================================================
# materials (A19 Tabla 3.1, 3.1.6, 3.1.3(2), 3.1.8, 3.2.7)
# ============================================================================================
AGGREGATE_FACTOR = {"cuarcita": 1.0, "caliza": 0.9, "arenisca": 0.7, "basalto": 1.2}


@dataclass(frozen=True)
class Concrete:
    fck: float
    gamma_c: float = 1.5
    alpha_cc: float = 1.0           # Spain: 1.00 (A19.3.1.6)
    alpha_ct: float = 1.0
    aggregate: str = "caliza"       # CYPE listing §1.11: limestone -> Ecm x 0.9

    @property
    def fcm(self) -> float:
        return self.fck + 8.0

    @property
    def fcd(self) -> float:
        return self.alpha_cc * self.fck / self.gamma_c

    @property
    def fctm(self) -> float:
        return 0.30 * self.fck ** (2 / 3) if self.fck <= 50 else 2.12 * math.log(1 + self.fcm / 10)

    @property
    def fctk005(self) -> float:
        return 0.7 * self.fctm

    @property
    def fctd(self) -> float:
        return self.alpha_ct * self.fctk005 / self.gamma_c

    def fctm_fl(self, h_mm: float) -> float:
        """A19.3.1.8 (3.23)."""
        return max((1.6 - h_mm / 1000.0) * self.fctm, self.fctm)

    @property
    def Ecm(self) -> float:
        return 22000.0 * (self.fcm / 10) ** 0.3 * AGGREGATE_FACTOR[self.aggregate]

    @property
    def eps_c2(self) -> float:
        # BOE prints 0,85 (typo); the tabulated values require 0.085
        return 0.002 if self.fck <= 50 else (2.0 + 0.085 * (self.fck - 50) ** 0.53) / 1000

    @property
    def eps_cu2(self) -> float:
        return 0.0035 if self.fck <= 50 else (2.6 + 35 * ((90 - self.fck) / 100) ** 4) / 1000

    @property
    def n(self) -> float:
        return 2.0 if self.fck <= 50 else 1.4 + 23.4 * ((90 - self.fck) / 100) ** 4


@dataclass(frozen=True)
class Steel:
    fyk: float = 500.0              # B 500 SD
    gamma_s: float = 1.15
    Es: float = 200000.0

    @property
    def fyd(self) -> float:
        return self.fyk / self.gamma_s

    @property
    def eps_yd(self) -> float:
        return self.fyd / self.Es


HA35 = Concrete(35.0)
HA50 = Concrete(50.0)
B500SD = Steel()


def bar_area(phi_mm: float) -> float:
    return math.pi * phi_mm ** 2 / 4.0


# ============================================================================================
# section
# ============================================================================================
@dataclass
class Bar:
    x: float                        # mm, about the gross centroid
    y: float
    phi: float                      # mm
    active: bool = True             # False: bar ignored in ULS (CYPE: web Ø10 of the T beam)
    tag: str = ""

    @property
    def area(self) -> float:
        return bar_area(self.phi)


@dataclass
class RCSection:
    """Union of concrete rectangles (x0, x1, y0, y1) [mm, gross-centroid axes] + bars."""
    name: str
    rects: list
    bars: list
    concrete: Concrete
    steel: Steel = B500SD
    mode: Mode = Mode.CYPE
    cell: float = 2.0               # fibre size [mm] for exact results
    eps_su_cype: float = 0.010
    strain_factor_cype: float = 0.995
    _hull: object = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.rects = [tuple(map(float, r)) for r in self.rects]
        c = self.concrete
        if self.mode == Mode.CYPE:
            self.ecu2 = c.eps_cu2 * self.strain_factor_cype
            self.esu = self.eps_su_cype * self.strain_factor_cype
            self.displace = False
        else:
            self.ecu2 = c.eps_cu2
            self.esu = 1.0              # practically unlimited (horizontal top branch)
            self.displace = True
        self.ec2, self.npar, self.fcd = c.eps_c2, c.n, c.fcd
        self.fyd, self.Es = self.steel.fyd, self.steel.Es
        self.vx = np.array([v for r in self.rects for v in (r[0], r[1], r[1], r[0])])
        self.vy = np.array([v for r in self.rects for v in (r[2], r[2], r[3], r[3])])
        self._set_bars()
        self.set_mesh(self.cell)

    # geometry ----------------------------------------------------------------------------------
    def _set_bars(self) -> None:
        self.bx = np.array([b.x for b in self.bars], float)
        self.by = np.array([b.y for b in self.bars], float)
        self.ba = np.array([b.area for b in self.bars], float)
        self.bact = np.array([b.active for b in self.bars], bool)

    def set_mesh(self, cell: float) -> None:
        xs, ys, As = [], [], []
        for (x0, x1, y0, y1) in self.rects:
            nx = max(1, int(round((x1 - x0) / cell)))
            ny = max(1, int(round((y1 - y0) / cell)))
            dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
            X, Y = np.meshgrid(x0 + (np.arange(nx) + 0.5) * dx, y0 + (np.arange(ny) + 0.5) * dy)
            xs.append(X.ravel())
            ys.append(Y.ravel())
            As.append(np.full(X.size, dx * dy))
        self.fx, self.fy, self.fa = np.concatenate(xs), np.concatenate(ys), np.concatenate(As)
        self._cell_now = cell

    @property
    def Ac(self) -> float:
        return sum((r[1] - r[0]) * (r[3] - r[2]) for r in self.rects)

    @property
    def As(self) -> float:
        return float(self.ba.sum())

    @property
    def h(self) -> float:
        return float(self.vy.max() - self.vy.min())

    @property
    def b(self) -> float:
        return float(self.vx.max() - self.vx.min())

    def gross_I(self) -> tuple[float, float]:
        """(Ix, Iy) of the gross concrete section about the gross centroid (mm4)."""
        Ix = sum((x1 - x0) * (y1 - y0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((y0 + y1) / 2) ** 2
                 for x0, x1, y0, y1 in self.rects)
        Iy = sum((y1 - y0) * (x1 - x0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((x0 + x1) / 2) ** 2
                 for x0, x1, y0, y1 in self.rects)
        return Ix, Iy

    def with_bars(self, bars: list) -> "RCSection":
        return RCSection(self.name, self.rects, bars, self.concrete, self.steel, self.mode, self.cell)

    # constitutive laws (compression +) --------------------------------------------------------
    def sig_c(self, e):
        e = np.asarray(e, float)
        par = self.fcd * (1.0 - (1.0 - np.clip(e, 0.0, self.ec2) / self.ec2) ** self.npar)
        return np.where(e > 0, np.where(e >= self.ec2, self.fcd, par), 0.0)

    def sig_s(self, e):
        return np.clip(self.Es * np.asarray(e, float), -self.fyd, self.fyd)

    # resultants --------------------------------------------------------------------------------
    def resultants(self, e0: float, kx: float, ky: float, detail: bool = False,
                   bar_area: np.ndarray | None = None):
        ec = e0 + kx * self.fx + ky * self.fy
        Fc = self.sig_c(ec) * self.fa
        es = e0 + kx * self.bx + ky * self.by
        ss = self.sig_s(es) * self.bact
        if self.displace:
            ss = ss - self.sig_c(es) * self.bact
        Fs = ss * (self.ba if bar_area is None else bar_area)
        N = Fc.sum() + Fs.sum()
        Mx = (Fc * self.fy).sum() + (Fs * self.by).sum()
        My = (Fc * self.fx).sum() + (Fs * self.bx).sum()
        if not detail:
            return np.array([N, Mx, My])
        Cc = float(Fc.sum())
        comp, ten = Fs > 0, Fs < 0
        Cs, T = float(Fs[comp].sum()), float(-Fs[ten].sum())
        ev = e0 + kx * self.vx + ky * self.vy
        return dict(N=float(N), Mx=float(Mx), My=float(My), Cc=Cc, Cs=Cs, T=T,
                    eps_c_max=float(ev.max()), eps_s_min=float(es[self.bact].min()) if self.bact.any() else 0.0,
                    bar_eps=es, bar_sig=ss, plane=(e0, kx, ky))

    # failure planes (A19 Figura 6.1): t in [0,3]: 0-1 pivot A, 1-2 pivot B, 2-3 pivot C ---------
    def ult_plane(self, alpha: float, t: float) -> tuple[float, float, float]:
        ca, sa = math.cos(alpha), math.sin(alpha)          # points to the compressed side
        s_v = self.vx * ca + self.vy * sa
        s_top, s_bot = s_v.max(), s_v.min()
        h = s_top - s_bot
        act = self.bact
        s_bar = (self.bx[act] * ca + self.by[act] * sa).min() if act.any() else s_bot
        ecu, ec2, esu = self.ecu2, self.ec2, self.esu
        if s_top - s_bar < 1e-9:                             # no tension bar below the top
            s_bar = s_bot
        if t <= 1.0:
            e_top = -esu + t * (ecu + esu)
            k = (e_top + esu) / (s_top - s_bar)
            e0 = -esu - k * s_bar
        elif t <= 2.0:
            xAB = ecu / (ecu + esu) * (s_top - s_bar)
            x = xAB + (t - 1.0) * (h - xAB)
            k = ecu / x
            e0 = ecu - k * s_top
        else:
            sC = s_top - (1 - ec2 / ecu) * h
            e_top = ecu + (t - 2.0) * (ec2 - ecu)
            k = (e_top - ec2) / (s_top - sC)
            e0 = ec2 - k * sC
        return e0, k * ca, k * sa

    def ult(self, alpha: float, t: float, detail: bool = False):
        return self.resultants(*self.ult_plane(alpha, t), detail=detail)

    # interaction surface: fast hull for screening ------------------------------------------------
    def hull(self, n_alpha: int = 72, n_t: int = 91, cell: float = 8.0):
        if self._hull is None:
            fine = self._cell_now
            self.set_mesh(cell)
            pts = [self.ult(a, t) for a in np.linspace(0, 2 * math.pi, n_alpha, endpoint=False)
                   for t in np.linspace(0.0, 3.0, n_t)]
            self.set_mesh(fine)
            pts = np.array(pts)
            L = max(np.ptp(self.vx), np.ptp(self.vy))
            sc = np.array([1.0, 1 / L, 1 / L])
            self._hull = (ConvexHull(pts * sc), sc)
        return self._hull

    def eta_fast(self, S) -> float:
        """Approximate utilisation along the ray (convex hull of the sampled surface)."""
        H, sc = self.hull()
        s = np.asarray(S, float) * sc
        nrm = float(np.linalg.norm(s))
        if nrm == 0:
            return 0.0
        d = s / nrm
        A, b = H.equations[:, :3], H.equations[:, 3]
        ad = A @ d
        with np.errstate(divide="ignore"):
            t = np.where(ad > 1e-15, -b / ad, np.inf)
        return nrm / float(t.min())

    # exact capacities ---------------------------------------------------------------------------
    def capacity_ray(self, S, coarse: float = 10.0) -> dict:
        """NRd, MRd with the same eccentricities as S = (N, Mx, My) [N, N·mm]; eta = |S|/|R|."""
        S = np.asarray(S, float)
        L = max(np.ptp(self.vx), np.ptp(self.vy))
        sc = np.array([1.0, 1 / L, 1 / L])
        shat = S * sc / np.linalg.norm(S * sc)
        fine = self._cell_now
        self.set_mesh(coarse)
        best = (9.0, 0.0, 0.0)
        for a in np.radians(np.arange(0.0, 360.0, 3.0)):
            for t in np.linspace(0.0, 3.0, 121):
                r = self.ult(a, t) * sc
                nr = np.linalg.norm(r)
                if nr > 0:
                    err = np.linalg.norm(r / nr - shat)
                    if err < best[0]:
                        best = (err, a, t)
        self.set_mesh(fine)

        def res(p):
            r = self.ult(p[0], p[1]) * sc
            return r / np.linalg.norm(r) - shat
        sol = least_squares(res, [best[1], best[2]], bounds=([-10, 0], [20, 3]), xtol=1e-13, ftol=1e-13)
        d = self.ult(sol.x[0], sol.x[1], detail=True)
        R = np.array([d["N"], d["Mx"], d["My"]])
        d["eta"] = float(np.linalg.norm(S * sc) / np.linalg.norm(R * sc))
        d["alpha"], d["t"] = float(sol.x[0]), float(sol.x[1])
        d["residual"] = float(np.linalg.norm(res(sol.x)))
        return d

    def capacity_constant_N(self, S) -> tuple[float, np.ndarray]:
        """Utilisation at constant N and constant Mx:My ratio (CYPE summary 'Aprov.')."""
        S = np.asarray(S, float)
        r0 = self.capacity_ray(S)
        ang = math.atan2(S[2], S[1])

        def res(p):
            R = self.ult(p[0], p[1])
            return [(R[0] - S[0]) / 1e5, math.atan2(R[2], R[1]) - ang]
        sol = least_squares(res, [r0["alpha"], r0["t"]], bounds=([-10, 0], [20, 3]), xtol=1e-13)
        R = self.ult(*sol.x)
        return math.hypot(S[1], S[2]) / math.hypot(R[1], R[2]), R

    def capacity_uniaxial(self, N: float, compression_side: int = +1, axis: str = "x") -> dict:
        """MRd for a given N; bending about x (compression on +y if +1) or about y."""
        if axis == "x":
            a = math.pi / 2 if compression_side > 0 else -math.pi / 2
        else:
            a = 0.0 if compression_side > 0 else math.pi
        t = brentq(lambda t: self.ult(a, t)[0] - N, 0.0, 3.0, xtol=1e-12)
        return self.ult(a, t, detail=True)

    def equilibrium(self, S) -> dict:
        """Strain plane in equilibrium with S (CYPE 'Equilibrio ... esfuerzos solicitantes')."""
        S = np.asarray(S, float)
        L = max(np.ptp(self.vx), np.ptp(self.vy))
        scale = np.array([1.0, 1 / L, 1 / L]) / max(abs(S[0]), np.linalg.norm(S[1:]) / L, 1.0)

        def res(p):
            return (self.resultants(p[0] * 1e-3, p[1] * 1e-5, p[2] * 1e-5) - S) * scale
        best = None
        for e0 in (0.5, 0.0):
            for kx in (-1.0, 0.0, 1.0):
                for ky in (-1.0, 0.0, 1.0):
                    sol = least_squares(res, [e0, kx, ky], xtol=1e-15, ftol=1e-15, gtol=1e-15,
                                        max_nfev=3000)
                    if best is None or sol.cost < best.cost:
                        best = sol
            if best.cost < 1e-20:
                break
        p = best.x
        out = self.resultants(p[0] * 1e-3, p[1] * 1e-5, p[2] * 1e-5, detail=True)
        out["cost"] = float(best.cost)
        return out


def required_tension_steel(sec: RCSection, bar_xy: list, M: float, compression_side: int,
                           N: float = 0.0) -> float:
    """Area [mm2] of the tension group ``bar_xy`` (other bars removed: singly reinforced, as
    CYPE's 'Área Nec.') so that MRd = |M| [N·mm] about x at axial force N."""
    def mrd(As):
        bars = [Bar(x, y, 2 * math.sqrt(As / len(bar_xy) / math.pi)) for x, y in bar_xy]
        s = RCSection(sec.name, sec.rects, bars, sec.concrete, sec.steel, sec.mode, sec.cell)
        return abs(s.capacity_uniaxial(N, compression_side)["Mx"])
    return brentq(lambda a: mrd(a) - abs(M), 1.0, 50000.0, xtol=0.01)


# ============================================================================================
# serviceability: linear-elastic homogenised / cracked sections (bending about x)
# ============================================================================================
def homogenised(sec: RCSection, alpha_e: float) -> dict:
    """Uncracked homogenised section (gross concrete + (alpha_e - 1)·As)."""
    parts = [((x1 - x0) * (y1 - y0), (y0 + y1) / 2, (x1 - x0) * (y1 - y0) ** 3 / 12)
             for x0, x1, y0, y1 in sec.rects]
    bars = [(b.y, b.area) for b in sec.bars]
    A = sum(a for a, _, _ in parts) + sum((alpha_e - 1) * a for _, a in bars)
    yc = (sum(a * y for a, y, _ in parts) + sum((alpha_e - 1) * a * y for y, a in bars)) / A
    I = (sum(i + a * (y - yc) ** 2 for a, y, i in parts)
         + sum((alpha_e - 1) * a * (y - yc) ** 2 for y, a in bars))
    return dict(A=A, yc=yc, I=I, ytop=float(sec.vy.max()), ybot=float(sec.vy.min()))


def uncracked_stresses(sec: RCSection, alpha_e: float, M: float, N: float = 0.0) -> dict:
    """Stresses [MPa] (compression +) for M [N·mm] (+ compresses the top) and N [N]."""
    h = homogenised(sec, alpha_e)

    def sig(y):
        return N / h["A"] + M * (y - h["yc"]) / h["I"]
    return dict(top=sig(h["ytop"]), bot=sig(h["ybot"]), bars=[alpha_e * sig(b.y) for b in sec.bars],
                **h)


def cracking_moment(sec: RCSection, alpha_e: float, fct: float, sagging: bool) -> float:
    """M [N·mm] at which the extreme tension fibre reaches fct (homogenised, N = 0)."""
    h = homogenised(sec, alpha_e)
    y = h["ybot"] if sagging else h["ytop"]
    return fct * h["I"] / abs(y - h["yc"])


def cracked_stresses(sec: RCSection, alpha_e: float, M: float) -> dict:
    """Fully cracked linear-elastic section (no concrete in tension), N = 0, bending about x.
    Compression bars counted with alpha_e (as in the research validation)."""
    ytop, ybot = float(sec.vy.max()), float(sec.vy.min())
    sag = M > 0

    def force(yn):
        F = 0.0
        for x0, x1, y0, y1 in sec.rects:
            b = x1 - x0
            if sag:
                lo, hi = max(y0, yn), y1
                if hi > lo:
                    F += b * ((hi - yn) ** 2 - (lo - yn) ** 2) / 2
            else:
                lo, hi = y0, min(y1, yn)
                if hi > lo:
                    F += b * ((yn - lo) ** 2 - (yn - hi) ** 2) / 2
        for bar in sec.bars:
            F += alpha_e * bar.area * ((bar.y - yn) if sag else (yn - bar.y))
        return F
    yn = brentq(force, ybot + 1e-6, ytop - 1e-6)
    I = 0.0
    for x0, x1, y0, y1 in sec.rects:
        b = x1 - x0
        lo, hi = (max(y0, yn), y1) if sag else (y0, min(y1, yn))
        if hi > lo:
            I += b * ((hi - yn) ** 3 - (lo - yn) ** 3) / 3
    I += sum(alpha_e * bar.area * (bar.y - yn) ** 2 for bar in sec.bars)
    x = (ytop - yn) if sag else (yn - ybot)
    return dict(yn=yn, x=x, Icr=I, sig_c=abs(M) * x / I,
                sig_s=[alpha_e * M * (bar.y - yn) / I for bar in sec.bars])   # compression +


def crack_width(sig_s: float, conc: Concrete, steel: Steel, As: float, Ac_eff: float, c: float,
                phi: float, kt: float = 0.4, k1: float = 0.8, k2: float = 0.5, k3: float = 3.4,
                k4: float = 0.425, spacing: float | None = None, h: float | None = None,
                x: float | None = None, fct_eff: float | None = None) -> dict:
    """A19.7.3.4 (7.8)-(7.11), (7.14).  sig_s = tension stress in the most tensioned bar [MPa]."""
    fct = conc.fctm if fct_eff is None else fct_eff
    alpha_e = steel.Es / conc.Ecm
    rho = As / Ac_eff
    d_eps = max((sig_s - kt * fct / rho * (1 + alpha_e * rho)) / steel.Es, 0.6 * sig_s / steel.Es)
    if spacing is not None and h is not None and x is not None and spacing > 5 * (c + phi / 2):
        sr = 1.3 * (h - x)
        rule = "(7.14)"
    else:
        sr = k3 * c + k1 * k2 * k4 * phi / rho
        rule = "(7.11)"
    return dict(wk=sr * d_eps, sr_max=sr, d_eps=d_eps, rho_p_eff=rho, alpha_e=alpha_e, rule=rule)
