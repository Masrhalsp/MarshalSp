"""Cross-section properties for the concrete members of the Muelle de Trasmallo model.

A section is described as a union of non-overlapping rectangles in the plane of the
cross-section, using SAP2000 local-axis naming for a beam:

    * coordinate ``z2`` runs along local axis 2 (vertical for a beam, "depth", t3 direction)
    * coordinate ``z3`` runs along local axis 3 (horizontal, "width", t2 direction)

Every rectangle is ``(z3_min, z3_max, z2_min, z2_max)`` in metres.

Properties returned (SAP2000 "General" frame-section field names):

    Area, I33 (bending about local 3 = vertical bending), I22, I23, TorsConst (St Venant J),
    AS2, AS3 (shear areas), S33, S22, Z33, Z22, R33, R22, t3, t2, plus the centroid.

The St Venant torsion constant is obtained by solving the Prandtl stress-function problem
(laplacian(phi) = -2 inside, phi = 0 on the boundary, J = 2 * integral(phi)) with finite
differences, so composite shapes (inverted T, L) are handled exactly up to the grid size.
Shear areas use the energy (Jourawski) method  As = I^2 / integral(Q^2 / b^2 dA).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


Rect = tuple[float, float, float, float]  # (z3_min, z3_max, z2_min, z2_max)


@dataclass
class Section:
    name: str
    rects: list[Rect]
    description: str = ""
    props: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.props = section_properties(self.rects)


def _grid(rects: list[Rect], h: float):
    z3min = min(r[0] for r in rects)
    z3max = max(r[1] for r in rects)
    z2min = min(r[2] for r in rects)
    z2max = max(r[3] for r in rects)
    n3 = int(round((z3max - z3min) / h))
    n2 = int(round((z2max - z2min) / h))
    # cell centres
    c3 = z3min + (np.arange(n3) + 0.5) * h
    c2 = z2min + (np.arange(n2) + 0.5) * h
    inside = np.zeros((n2, n3), dtype=bool)
    for (a3, b3, a2, b2) in rects:
        m3 = (c3 > a3) & (c3 < b3)
        m2 = (c2 > a2) & (c2 < b2)
        inside |= np.outer(m2, m3)
    return c3, c2, inside


def torsion_constant(rects: list[Rect], h: float = 0.0025) -> float:
    """St Venant torsion constant by finite differences on the Prandtl stress function."""
    _, _, inside = _grid(rects, h)
    n2, n3 = inside.shape
    idx = -np.ones(inside.shape, dtype=int)
    cells = np.argwhere(inside)
    idx[inside] = np.arange(len(cells))
    A = lil_matrix((len(cells), len(cells)))
    b = np.full(len(cells), -2.0 * h * h)
    for k, (i, j) in enumerate(cells):
        A[k, k] = -4.0
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ii, jj = i + di, j + dj
            if 0 <= ii < n2 and 0 <= jj < n3 and inside[ii, jj]:
                A[k, idx[ii, jj]] = 1.0
            # outside neighbour -> phi = 0 on a boundary located half a cell away;
            # treat with the ghost-cell (phi_ghost = -phi) rule for second-order accuracy
            else:
                A[k, k] -= 1.0
    phi = spsolve(A.tocsr(), b)
    return float(2.0 * phi.sum() * h * h)


def _shear_area(rects: list[Rect], axis: str, I: float, zc: float, n: int = 4000) -> float:
    """Energy-method shear area for shear acting along ``axis`` ('2' or '3')."""
    if axis == "2":
        lo = min(r[2] for r in rects)
        hi = max(r[3] for r in rects)
    else:
        lo = min(r[0] for r in rects)
        hi = max(r[1] for r in rects)
    s = np.linspace(lo, hi, n + 1)
    mid = 0.5 * (s[1:] + s[:-1])
    ds = s[1] - s[0]
    width = np.zeros_like(mid)
    for (a3, b3, a2, b2) in rects:
        if axis == "2":
            m = (mid > a2) & (mid < b2)
            width[m] += b3 - a3
        else:
            m = (mid > a3) & (mid < b3)
            width[m] += b2 - a2
    dA = width * ds
    # first moment of the part beyond each cut, measured from the top end
    Q = np.cumsum((dA * (mid - zc))[::-1])[::-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        integrand = np.where(width > 0, Q**2 / width**2 * dA, 0.0)
    return float(I**2 / integrand.sum())


def section_properties(rects: list[Rect]) -> dict:
    A = sum((b3 - a3) * (b2 - a2) for (a3, b3, a2, b2) in rects)
    c3 = sum((b3 - a3) * (b2 - a2) * 0.5 * (a3 + b3) for (a3, b3, a2, b2) in rects) / A
    c2 = sum((b3 - a3) * (b2 - a2) * 0.5 * (a2 + b2) for (a3, b3, a2, b2) in rects) / A
    I33 = I22 = I23 = 0.0
    for (a3, b3, a2, b2) in rects:
        w, d = b3 - a3, b2 - a2
        m3, m2 = 0.5 * (a3 + b3) - c3, 0.5 * (a2 + b2) - c2
        I33 += w * d**3 / 12.0 + w * d * m2**2   # about local-3 axis (vertical bending)
        I22 += d * w**3 / 12.0 + w * d * m3**2   # about local-2 axis (lateral bending)
        I23 += w * d * m2 * m3
    z2min = min(r[2] for r in rects)
    z2max = max(r[3] for r in rects)
    z3min = min(r[0] for r in rects)
    z3max = max(r[1] for r in rects)
    t3 = z2max - z2min
    t2 = z3max - z3min
    S33 = I33 / max(z2max - c2, c2 - z2min)
    S22 = I22 / max(z3max - c3, c3 - z3min)
    Z33 = _plastic_modulus(rects, "2")
    Z22 = _plastic_modulus(rects, "3")
    J = torsion_constant(rects)
    AS2 = _shear_area(rects, "2", I33, c2)
    AS3 = _shear_area(rects, "3", I22, c3)
    return {
        "t3": t3, "t2": t2, "Area": A, "TorsConst": J, "I33": I33, "I22": I22, "I23": I23,
        "AS2": AS2, "AS3": AS3, "S33": S33, "S22": S22, "Z33": Z33, "Z22": Z22,
        "R33": (I33 / A) ** 0.5, "R22": (I22 / A) ** 0.5,
        "centroid_z3": c3, "centroid_z2": c2,
        "centroid_from_bottom": c2 - z2min, "centroid_from_top": z2max - c2,
    }


def _plastic_modulus(rects: list[Rect], axis: str, n: int = 4000) -> float:
    if axis == "2":
        lo, hi = min(r[2] for r in rects), max(r[3] for r in rects)
    else:
        lo, hi = min(r[0] for r in rects), max(r[1] for r in rects)
    s = np.linspace(lo, hi, n + 1)
    mid = 0.5 * (s[1:] + s[:-1])
    ds = s[1] - s[0]
    width = np.zeros_like(mid)
    for (a3, b3, a2, b2) in rects:
        m = ((mid > a2) & (mid < b2)) if axis == "2" else ((mid > a3) & (mid < b3))
        width[m] += (b3 - a3) if axis == "2" else (b2 - a2)
    dA = width * ds
    cum = np.cumsum(dA)
    pna = mid[np.searchsorted(cum, cum[-1] / 2.0)]
    return float(np.sum(dA * np.abs(mid - pna)))


def rectangle(name: str, width: float, depth: float, description: str = "") -> Section:
    return Section(name, [(-width / 2, width / 2, -depth / 2, depth / 2)], description)


def inverted_tee(name: str, web_w: float, depth: float, wing_w: float, wing_t: float,
                 description: str = "") -> Section:
    """CYPECAD 'b x h + a x e + a x e': web b x h with a bottom ledge (ala) a wide, e thick
    on each side. Local 2 up, bottom of section at z2 = 0."""
    rects = [
        (-web_w / 2 - wing_w, web_w / 2 + wing_w, 0.0, wing_t),      # bottom slab incl. both wings
        (-web_w / 2, web_w / 2, wing_t, depth),                       # web above the wings
    ]
    return Section(name, rects, description)


def inverted_l(name: str, web_w: float, depth: float, wing_w: float, wing_t: float,
               wing_side: int = +1, description: str = "") -> Section:
    """CYPECAD 'b x h + a x e': web b x h with a single bottom ledge on the +3 (wing_side=+1)
    or -3 (wing_side=-1) side."""
    if wing_side > 0:
        bottom = (-web_w / 2, web_w / 2 + wing_w, 0.0, wing_t)
    else:
        bottom = (-web_w / 2 - wing_w, web_w / 2, 0.0, wing_t)
    rects = [bottom, (-web_w / 2, web_w / 2, wing_t, depth)]
    return Section(name, rects, description)


if __name__ == "__main__":
    # sanity checks against closed-form values
    sq = rectangle("SQ40", 0.40, 0.40)
    j_exact = 0.1406 * 0.40**4  # beta = 0.1406 for a square
    print(f"square 40x40: J FD = {sq.props['TorsConst']:.6e}  closed form = {j_exact:.6e}")
    print(f"square 40x40: AS2 = {sq.props['AS2']:.5f}  (5/6 A = {0.16 * 5 / 6:.5f})")
    t = inverted_tee("VT", 0.50, 0.55, 0.15, 0.30)
    for k, v in t.props.items():
        print(f"  {k:22s} {v:.6g}")
