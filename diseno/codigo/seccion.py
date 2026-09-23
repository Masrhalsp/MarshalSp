"""Reinforced-concrete cross-section engine (Código Estructural Anejo 19 = EN 1992-1-1).

A section is a set of concrete rectangles plus discrete bars, in local coordinates (u, v) [m]
with origin anywhere (the gross centroid is used as the reference point for moments).

Sign convention (as in the CYPE listings of Anejo 10): compression POSITIVE for strains,
stresses and the axial force N.  Moments about the reference point:

    Mu = sum(F·v)   (moment producing compression in the +v fibres is positive)
    Mv = -sum(F·u)  ... not used; we report   Mx := Mu (bending about the u axis)
                                              My := sum(F·u) (compression in +u fibres > 0)

so that a positive moment compresses the positive side of the corresponding coordinate.

Ultimate limit state (A19.6.1): plane sections, no concrete tensile strength, parabola-
rectangle diagram for concrete (A19.3.1.7, eps_c2 / eps_cu2 / n from fck), elastic-perfectly
plastic steel with fyd (horizontal top branch, A19.3.2.7(2)b), steel strain limited to
``eps_ud`` (CYPE works with 10 per mil, see the bar strains of the equilibrium tables).

Serviceability: elastic cracked (or uncracked) section with modular ratio alpha_e = Es/Ec.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

try:
    from scipy.spatial import ConvexHull
except ImportError:  # pragma: no cover
    ConvexHull = None


# --------------------------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Concrete:
    fck: float                  # MPa
    gamma_c: float = 1.5
    alpha_cc: float = 1.0       # Spain (Anejo 19 national choice), CYPE fcd = fck/1.5

    @property
    def fcd(self) -> float:
        return self.alpha_cc * self.fck / self.gamma_c

    @property
    def fcm(self) -> float:
        return self.fck + 8.0

    @property
    def fctm(self) -> float:    # A19 Table 3.1
        return 0.30 * self.fck ** (2 / 3) if self.fck <= 50 else 2.12 * math.log(1 + self.fcm / 10)

    @property
    def fctk005(self) -> float:
        return 0.7 * self.fctm

    def fctm_fl(self, h: float) -> float:
        """Mean flexural tensile strength A19.3.1.8: max((1.6 - h[mm]/1000)·fctm, fctm)."""
        return max((1.6 - h * 1000 / 1000.0) * self.fctm, self.fctm)

    @property
    def Ecm(self) -> float:     # MPa, A19 Table 3.1 (siliceous aggregate)
        return 22000.0 * (self.fcm / 10) ** 0.3

    @property
    def eps_c2(self) -> float:
        return 0.002 if self.fck <= 50 else (2.0 + 0.085 * (self.fck - 50) ** 0.53) / 1000

    @property
    def eps_cu2(self) -> float:
        return 0.0035 if self.fck <= 50 else (2.6 + 35 * ((90 - self.fck) / 100) ** 4) / 1000

    @property
    def n(self) -> float:
        return 2.0 if self.fck <= 50 else 1.4 + 23.4 * ((90 - self.fck) / 100) ** 4

    def sigma_uls(self, eps: np.ndarray) -> np.ndarray:
        """Design stress [MPa] (compression +) for strain eps (compression +)."""
        e = np.clip(eps, 0.0, None)
        s = np.where(e < self.eps_c2, self.fcd * (1 - (1 - e / self.eps_c2) ** self.n), self.fcd)
        return np.where(eps > 0, s, 0.0)


@dataclass(frozen=True)
class Steel:
    fyk: float = 500.0          # MPa, B 500 SD
    gamma_s: float = 1.15
    Es: float = 200000.0
    eps_ud: float = 0.010       # strain limit used by CYPE (10 per mil)

    @property
    def fyd(self) -> float:
        return self.fyk / self.gamma_s

    @property
    def eps_yd(self) -> float:
        return self.fyd / self.Es

    def sigma_uls(self, eps: np.ndarray) -> np.ndarray:
        return np.clip(self.Es * eps, -self.fyd, self.fyd)


# --------------------------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Bar:
    u: float                    # m
    v: float                    # m
    diameter: float             # mm
    tag: str = ""

    @property
    def area(self) -> float:    # m2
        return math.pi * (self.diameter / 1000) ** 2 / 4


@dataclass
class Section:
    """Concrete rectangles (u0, v0, u1, v1) [m] + bars."""
    name: str
    rects: list
    bars: list = field(default_factory=list)
    concrete: Concrete = Concrete(35)
    steel: Steel = Steel()
    mesh: float = 0.005         # fibre size [m]

    def __post_init__(self) -> None:
        us, vs, As = [], [], []
        for (u0, v0, u1, v1) in self.rects:
            nu = max(1, int(round((u1 - u0) / self.mesh)))
            nv = max(1, int(round((v1 - v0) / self.mesh)))
            du, dv = (u1 - u0) / nu, (v1 - v0) / nv
            uu = u0 + du * (np.arange(nu) + 0.5)
            vv = v0 + dv * (np.arange(nv) + 0.5)
            U, V = np.meshgrid(uu, vv)
            us.append(U.ravel())
            vs.append(V.ravel())
            As.append(np.full(U.size, du * dv))
        self.fu = np.concatenate(us)
        self.fv = np.concatenate(vs)
        self.fa = np.concatenate(As)
        self.Ac = float(self.fa.sum())
        self.uc = float((self.fa * self.fu).sum() / self.Ac)     # gross centroid
        self.vc = float((self.fa * self.fv).sum() / self.Ac)
        self._set_bars()

    def _set_bars(self) -> None:
        self.bu = np.array([b.u for b in self.bars], float)
        self.bv = np.array([b.v for b in self.bars], float)
        self.ba = np.array([b.area for b in self.bars], float)

    # geometry helpers ------------------------------------------------------------------------
    @property
    def As_total(self) -> float:
        return float(self.ba.sum())

    @property
    def u_range(self) -> tuple[float, float]:
        return min(r[0] for r in self.rects), max(r[2] for r in self.rects)

    @property
    def v_range(self) -> tuple[float, float]:
        return min(r[1] for r in self.rects), max(r[3] for r in self.rects)

    def with_bars(self, bars: list) -> "Section":
        s = Section.__new__(Section)
        s.__dict__.update(self.__dict__)
        s.bars = list(bars)
        s._set_bars()
        return s

    # ULS ---------------------------------------------------------------------------------------
    def forces(self, eps0: float, ku: float, kv: float, a_bars: np.ndarray | None = None
               ) -> tuple[float, float, float]:
        """Resultants (N [kN], Mx [kN m], My [kN m]) about the gross centroid for the strain
        plane eps = eps0 + ku·(u-uc) + kv·(v-vc) (compression +). ``Mx`` is the moment of the
        forces about the u axis (lever arm v - vc), ``My`` about the v axis (lever arm u - uc).
        """
        c = self.concrete
        ec = eps0 + ku * (self.fu - self.uc) + kv * (self.fv - self.vc)
        sc = c.sigma_uls(ec) * 1000.0                        # kPa
        Fc = sc * self.fa
        ab = self.ba if a_bars is None else a_bars
        es = eps0 + ku * (self.bu - self.uc) + kv * (self.bv - self.vc)
        # bars displace concrete in compression
        ss = self.steel.sigma_uls(es) * 1000.0 - c.sigma_uls(es) * 1000.0
        Fs = ss * ab
        N = Fc.sum() + Fs.sum()
        Mx = (Fc * (self.fv - self.vc)).sum() + (Fs * (self.bv - self.vc)).sum()
        My = (Fc * (self.fu - self.uc)).sum() + (Fs * (self.bu - self.uc)).sum()
        return float(N), float(Mx), float(My)

    def _extent(self, du: float, dv: float) -> tuple[float, float]:
        """(max, min) of the projection d = (u-uc)·du + (v-vc)·dv over the concrete outline
        (rectangle corners, not fibre centres)."""
        ds = [(u - self.uc) * du + (v - self.vc) * dv
              for (u0, v0, u1, v1) in self.rects for u in (u0, u1) for v in (v0, v1)]
        return max(ds), min(ds)

    def _plane_for_depth(self, x: float, du: float, dv: float, top: float, bot_c: float,
                         bot_s: float) -> tuple[float, float]:
        """(eps_top, curvature) of the failure plane with neutral-axis depth x measured from
        the most compressed fibre along (du, dv).  Domains 2-4 (0 < x <= h): eps_cu2 at the
        top or eps_ud at the most tensioned bar, whichever governs; domain 5 (x > h, whole
        section compressed): pivot C at (1 - eps_c2/eps_cu2)·h with eps = eps_c2."""
        c, s = self.concrete, self.steel
        h = top - bot_c
        if x <= h:
            k1 = c.eps_cu2 / x
            dmax = top - bot_s
            k2 = s.eps_ud / (dmax - x) if dmax > x else math.inf
            k = min(k1, k2)
            return k * x, k
        xc = (1 - c.eps_c2 / c.eps_cu2) * h
        k = c.eps_c2 / (x - xc)                 # line through (xc, eps_c2) and (x, 0)
        return c.eps_c2 + k * xc, k

    def _ultimate_planes(self, n_angle: int = 72, n_depth: int = 160) -> list[tuple]:
        planes = []
        for ia in range(n_angle):
            th = 2 * math.pi * ia / n_angle
            du, dv = math.cos(th), math.sin(th)         # unit vector towards compression
            top, bot_c = self._extent(du, dv)
            if self.bu.size:
                bot_s = float(((self.bu - self.uc) * du + (self.bv - self.vc) * dv).min())
            else:
                bot_s = bot_c
            h = top - bot_c
            xs = np.concatenate([h * np.linspace(1e-4, 1.0, n_depth),
                                 h * (1.0 + np.geomspace(1e-3, 50.0, max(10, n_depth // 4)))])
            for x in xs:
                eps_top, k = self._plane_for_depth(float(x), du, dv, top, bot_c, bot_s)
                planes.append((eps_top, k, du, dv, top))
            planes.append((self.concrete.eps_c2, 0.0, du, dv, top))   # pure compression
        return planes

    def interaction_points(self, n_angle: int = 72, n_depth: int = 160) -> np.ndarray:
        pts = []
        for eps_top, k, du, dv, top in self._ultimate_planes(n_angle, n_depth):
            # eps(p) = eps_top - k·(top - d(p)),  d(p) = (u-uc)du + (v-vc)dv
            eps0 = eps_top - k * top
            pts.append(self.forces(eps0, k * du, k * dv))
        pts.append(self.forces(-self.steel.eps_ud, 0.0, 0.0))   # pure tension
        return np.array(pts)

    def interaction_hull(self, n_angle: int = 72, n_depth: int = 160):
        if ConvexHull is None:
            raise RuntimeError("scipy is required for the interaction surface")
        pts = self.interaction_points(n_angle, n_depth)
        scale = np.array([max(abs(pts[:, 0]).max(), 1e-9), max(abs(pts[:, 1]).max(), 1e-9),
                          max(abs(pts[:, 2]).max(), 1e-9)])
        return ConvexHull(pts / scale), scale

    def utilisation(self, N: float, Mx: float, My: float, hull=None) -> tuple[float, tuple]:
        """eta = |S| / |R| along the ray from the origin through S = (N, Mx, My): the
        CYPE 'NRd, MRd with the same eccentricities' check.  Returns (eta, (NRd, MRdx, MRdy))."""
        if hull is None:
            hull = self.interaction_hull()
        H, scale = hull
        s = np.array([N, Mx, My]) / scale
        nrm = float(np.linalg.norm(s))
        if nrm < 1e-12:
            return 0.0, (0.0, 0.0, 0.0)
        d = s / nrm
        # plane equations: a·x + b <= 0 inside; ray x = t·d, t_max = min over planes with a·d > 0
        A, b = H.equations[:, :3], H.equations[:, 3]
        ad = A @ d
        with np.errstate(divide="ignore"):
            t = np.where(ad > 1e-12, -b / ad, np.inf)
        tmax = float(t.min())
        R = d * tmax * scale
        return nrm / tmax, (float(R[0]), float(R[1]), float(R[2]))

    # uniaxial helpers ---------------------------------------------------------------------------
    def mrd_uniaxial(self, N: float, axis: str = "x", sign: int = 1,
                     a_bars: np.ndarray | None = None) -> float:
        """Resisting moment about ``axis`` for axial force N (compression +), with the
        compression on the ``sign`` side (+1: +v side for axis 'x', +u side for axis 'y').
        Bisection on the neutral-axis depth over the failure planes of A19.6.1."""
        du, dv = (0.0, float(sign)) if axis == "x" else (float(sign), 0.0)
        top, bot_c = self._extent(du, dv)
        d_s = (self.bu - self.uc) * du + (self.bv - self.vc) * dv
        bot_s = float(d_s.min()) if d_s.size else bot_c

        def res(x: float):
            eps_top, k = self._plane_for_depth(x, du, dv, top, bot_c, bot_s)
            return self.forces(eps_top - k * top, k * du, k * dv, a_bars)

        h = top - bot_c
        lo, hi = 1e-6 * h, 60.0 * h
        Nlo, Nhi = res(lo)[0], res(hi)[0]
        if not (Nlo <= N <= Nhi):
            raise ValueError(f"N = {N:.1f} outside [{Nlo:.1f}, {Nhi:.1f}]")
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if res(mid)[0] < N:
                lo = mid
            else:
                hi = mid
        _, Mx, My = res(0.5 * (lo + hi))
        return Mx if axis == "x" else My

    # SLS: elastic section ---------------------------------------------------------------------
    def elastic_stresses(self, N: float, Mx: float, alpha_e: float, cracked: bool = True,
                         My: float = 0.0) -> dict:
        """Linear-elastic stresses [MPa] (compression +) for N [kN], Mx, My [kN m] about the gross
        centroid.  ``cracked``: concrete in tension ignored (iterative neutral-axis search on
        the fibre model); otherwise the homogenised gross section is used."""
        Ec = 1.0                                    # work in concrete units
        area = self.fa.copy()
        uu, vv = self.fu - self.uc, self.fv - self.vc
        bu, bv = self.bu - self.uc, self.bv - self.vc
        # bars: (alpha_e - 1) in compression or uncracked, alpha_e in cracked tension
        active = np.ones_like(area, dtype=bool)
        eps = None
        for _ in range(200):
            wa = np.where(active, area, 0.0)
            # homogenised stiffness matrix for (eps0, ku, kv)
            eb = None if eps is None else (eps[0] + eps[1] * bu + eps[2] * bv)
            if cracked and eb is not None:
                wb = np.where(eb < 0, alpha_e, alpha_e - 1.0) * self.ba
            else:
                wb = (alpha_e - 1.0) * self.ba
            K = np.zeros((3, 3))
            for w, u_, v_ in ((wa, uu, vv), (wb, bu, bv)):
                g = np.vstack([np.ones_like(u_), u_, v_])
                K += (g * w) @ g.T
            rhs = np.array([N, My, Mx]) / 1000.0    # kN -> MN so stresses come out in MPa
            sol = np.linalg.solve(K * Ec, rhs)
            new_eps = sol
            if not cracked:
                eps = new_eps
                break
            ec = new_eps[0] + new_eps[1] * uu + new_eps[2] * vv
            new_active = ec >= 0.0
            if eps is not None and np.array_equal(new_active, active):
                eps = new_eps
                break
            active, eps = new_active, new_eps
        ec = eps[0] + eps[1] * uu + eps[2] * vv
        eb = eps[0] + eps[1] * bu + eps[2] * bv
        sc = np.where(ec >= 0, ec, 0.0 if cracked else ec)
        return {
            "sigma_c_max": float(sc.max()), "sigma_c_min": float(ec.min()),
            "sigma_s": eb * alpha_e,                # MPa, compression +
            "strain_plane": tuple(float(e) for e in eps),   # in stress units / Ec
        }


def rect_section(name: str, b: float, h: float, bars: list, concrete: Concrete,
                 steel: Steel = Steel(), mesh: float = 0.005) -> Section:
    return Section(name, [(-b / 2, -h / 2, b / 2, h / 2)], bars, concrete, steel, mesh)
