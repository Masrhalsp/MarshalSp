"""Strict mock of the SAP2000 OAPI concrete-design functions, extending
``sap2000/tests/mock_sap.py`` (same conventions: documented parameter lists, so a wrong argument
count raises TypeError; types / enum ranges / object existence validated, violations raise
MockError; ByRef results returned as ``[ByRef..., ret]``).

Signatures and behaviour from diseno/sap/sap_design_spec.md:
A.1 SetCode/GetCode, A.2 Set/GetPreference (items 1-17), A.3 Set/GetOverwrite (items 1-12; since
v24.0 items 7-12 return 1; items 5/6 return 1 unless the frame is a concrete column-design
frame), A.4 SetMPUniaxial / SetORebar_1, A.5 PropRebar.GetProp / SetProp, A.6 SetRebarColumn (15),
GetRebarColumn (15), SetRebarBeam (9), GetSectProps (13), A.7 Set/GetDesignProcedure, A.8 combos,
A.9 StartDesign / GetResultsAvailable / VerifyPassed / GetSummaryResultsColumn (Name + 13 ByRef +
ItemType) / GetSummaryResultsBeam (Name + 15 ByRef + ItemType), A.10 DatabaseTables.

Design results are synthetic (deterministic functions of the station); frame forces can come from
:class:`XlsxSynth` = the SAP2000 v27.1 export of the current model, so the analysis-identity step of
the OAPI script can be exercised end to end.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for _p in (ROOT / "sap2000" / "tests", ROOT / "diseno" / "python"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import mock_sap as M  # noqa: E402
from mock_sap import MockError, _arr, _bool, _count, _int, _num, _str  # noqa: E402

CONCRETE_CODES = {"ACI 318-19", "ACI 318-14", "AS 3600-2018", "BS8110 97", "CSA A23.3-19", "Eurocode 2-2004",
                  "Indian IS 456-2000", "Italian NTC 2018", "NZS 3101-2006", "TS 500-2000(R2018)"}
# SAP default European bar list (m2, m) [S29][G3]
DEFAULT_BARS = {f"{d}d": (math.pi * (d / 1000) ** 2 / 4, d / 1000) for d in (6, 8, 10, 12, 14, 16, 20, 25, 26, 28)}
EC2_DEFAULT_PREFS = {1: 1, 2: 1, 3: 2, 4: 24, 5: 11, 6: 1, 7: 0.005, 8: 1.15, 9: 1.5, 10: 1.0, 11: 1.0,
                     12: 0.85, 13: 0.85, 14: 0.75, 15: 0.95, 16: 1, 17: 2}
OVERWRITE_FIELDS = ["Frame", "DesignSect", "FrameType", "RLLF", "XLMajor", "XLMinor", "BetaMajor", "BetaMinor",
                    "TanTheta", "Kr", "KPhi"]
OVERWRITE_TABLE = "Overwrites - Concrete Design - Eurocode 2-2004"


def sap_rect(t3: float, t2: float) -> dict:
    """What SAP2000 computes for a rectangle (spec A.6: A, 5/6 A, J with the 0.21 correction)."""
    A = t3 * t2
    lo, hi = sorted((t3, t2))
    J = hi * lo**3 * (1 / 3 - 0.21 * (lo / hi) * (1 - lo**4 / (12 * hi**4)))
    return {"Area": A, "As2": 5 / 6 * A, "As3": 5 / 6 * A, "Torsion": J, "I22": t3 * t2**3 / 12,
            "I33": t2 * t3**3 / 12, "S22": t3 * t2**2 / 6, "S33": t2 * t3**2 / 6, "Z22": t3 * t2**2 / 4,
            "Z33": t2 * t3**2 / 4, "R22": t2 / math.sqrt(12), "R33": t3 / math.sqrt(12)}


class DesignState:
    def __init__(self, missing_bars=(), tables_available: bool = True):
        self.bars = {k: v for k, v in DEFAULT_BARS.items() if k not in set(missing_bars)}
        self.code = "ACI 318-19"
        self.prefs = dict(EC2_DEFAULT_PREFS)
        self.overwrites: dict[str, dict[int, float]] = {}
        self.table_overwrites: dict[str, dict[str, str]] = {}
        self.strength: list[str] = []
        self.auto_combos = True
        self.results: dict[str, dict] = {}
        self.designed = False
        self.tables_available = tables_available
        self.editing: dict | None = None


# ------------------------------------------------------------------------------------------
class PropMaterialD(M.PropMaterial):
    def SetMaterial(self, Name, MatType, Color=-1, Notes="", GUID=""):
        self.st.need_unlocked("SetMaterial")
        return super().SetMaterial(Name, MatType, Color, Notes, GUID)

    def SetMPUniaxial(self, Name, E, A, Temp=0):
        _count("PropMaterial.SetMPUniaxial")
        _str(Name, "Name"); _num(E, "E"); _num(A, "A"); _num(Temp, "Temp")
        mat = self.st.materials.get(Name)
        if mat is None or mat["type"] not in (6, 7):
            raise MockError(f"SetMPUniaxial: {Name} is not a rebar/tendon material")
        if E <= 0:
            raise MockError("SetMPUniaxial: E <= 0")
        mat.update(E=E, A=A)
        return 0

    def SetORebar_1(self, Name, Fy, Fu, eFy, eFu, SSType, SSHysType, StrainAtHardening, StrainUltimate,
                    FinalSlope, UseCaltransSSDefaults, Temp=0):
        _count("PropMaterial.SetORebar_1")
        _str(Name, "Name")
        for v, w in ((Fy, "Fy"), (Fu, "Fu"), (eFy, "eFy"), (eFu, "eFu"), (StrainAtHardening, "StrainAtHardening"),
                     (StrainUltimate, "StrainUltimate"), (FinalSlope, "FinalSlope"), (Temp, "Temp")):
            _num(v, f"SetORebar_1.{w}")
        _int(SSType, "SSType", {0, 1, 2}); _int(SSHysType, "SSHysType", set(range(0, 8)))
        _bool(UseCaltransSSDefaults, "UseCaltransSSDefaults")
        mat = self.st.materials.get(Name)
        if mat is None or mat["type"] != 6:
            raise MockError(f"SetORebar_1: {Name} is not a rebar material")
        if not (0 < Fy <= Fu and eFy >= Fy and eFu >= Fu and 0 < StrainAtHardening < StrainUltimate):
            raise MockError("SetORebar_1: inconsistent strengths/strains")
        mat.update(Fy=Fy, Fu=Fu)
        return 0


class PropRebar(M._Sub):
    def GetProp(self, Name, Area=0.0, Diameter=0.0):
        _count("PropRebar.GetProp")
        _str(Name, "Name")
        bar = self.st.design.bars.get(Name)
        return [bar[0], bar[1], 0] if bar else [0.0, 0.0, 1]

    def SetProp(self, Name, Area, Diameter):
        _count("PropRebar.SetProp")
        _str(Name, "Name"); _num(Area, "Area"); _num(Diameter, "Diameter")
        if Area <= 0 or Diameter <= 0 or abs(Area - math.pi * Diameter**2 / 4) > 0.05 * Area:
            raise MockError(f"PropRebar.SetProp {Name}: area/diameter inconsistent")
        self.st.design.bars[Name] = (Area, Diameter)
        return 0


class PropFrameD(M.PropFrame):
    def SetRectangle(self, Name, MatProp, T3, T2, Color=-1, Notes="", GUID=""):
        self.st.need_unlocked("SetRectangle")
        ret = super().SetRectangle(Name, MatProp, T3, T2, Color, Notes, GUID)
        if T3 <= 0 or T2 <= 0:
            raise MockError("SetRectangle: non-positive dimension")
        self.st.frame_props[Name]["mat"] = MatProp        # resets rebar data too (new dict)
        return ret

    def SetGeneral(self, Name, MatProp, *args, **kw):
        self.st.need_unlocked("SetGeneral")
        ret = super().SetGeneral(Name, MatProp, *args, **kw)
        self.st.frame_props[Name]["mat"] = MatProp
        return ret

    def SetModifiers(self, Name, Value):
        self.st.need_unlocked("PropFrame.SetModifiers")
        return super().SetModifiers(Name, Value)

    def _concrete_section(self, Name, what, shapes):
        _str(Name, f"{what}.Name")
        sec = self.st.frame_props.get(Name)
        if sec is None:
            raise MockError(f"{what}: unknown section {Name}")
        if sec["shape"] not in shapes:
            raise MockError(f"{what}: section {Name} is {sec['shape']} (only {shapes})")
        if self.st.materials.get(sec.get("mat"), {}).get("type") != 2:
            raise MockError(f"{what}: section {Name} is not concrete")
        return sec

    def _rebar_mat(self, name, what):
        _str(name, what)
        if self.st.materials.get(name, {}).get("type") != 6:
            raise MockError(f"{what}: {name} is not a rebar material")

    def SetRebarColumn(self, Name, MatPropLong, MatPropConfine, Pattern, ConfineType, Cover, NumberCBars,
                       NumberR3Bars, NumberR2Bars, RebarSize, TieSize, TieSpacingLongit, Number2DirTieBars,
                       Number3DirTieBars, ToBeDesigned):
        _count("PropFrame.SetRebarColumn")
        self.st.need_unlocked("SetRebarColumn")
        sec = self._concrete_section(Name, "SetRebarColumn", ("Rect", "Circle"))
        self._rebar_mat(MatPropLong, "MatPropLong"); self._rebar_mat(MatPropConfine, "MatPropConfine")
        _int(Pattern, "Pattern", {1, 2}); _int(ConfineType, "ConfineType", {1, 2}); _num(Cover, "Cover")
        for v, w in ((NumberCBars, "NumberCBars"), (NumberR3Bars, "NumberR3Bars"), (NumberR2Bars, "NumberR2Bars"),
                     (Number2DirTieBars, "Number2DirTieBars"), (Number3DirTieBars, "Number3DirTieBars")):
            _int(v, w)
        _str(RebarSize, "RebarSize"); _str(TieSize, "TieSize"); _num(TieSpacingLongit, "TieSpacingLongit")
        _bool(ToBeDesigned, "ToBeDesigned")
        if RebarSize not in self.st.design.bars or TieSize not in self.st.design.bars:
            raise MockError(f"SetRebarColumn: bar size {RebarSize}/{TieSize} not defined")
        if Pattern == 1 and (ConfineType != 1 or NumberR3Bars < 2 or NumberR2Bars < 2):
            raise MockError("SetRebarColumn: rectangular pattern needs ties and >= 2 bars per face")
        if not 0 < Cover < min(sec["t2"], sec["t3"]) / 2 or TieSpacingLongit <= 0:
            raise MockError("SetRebarColumn: cover / tie spacing")
        sec["rebar"] = {"type": "column", "args": [MatPropLong, MatPropConfine, Pattern, ConfineType, Cover,
                                                   NumberCBars, NumberR3Bars, NumberR2Bars, RebarSize, TieSize,
                                                   TieSpacingLongit, Number2DirTieBars, Number3DirTieBars,
                                                   ToBeDesigned]}
        return 0

    def GetRebarColumn(self, Name, MatPropLong, MatPropConfine, Pattern, ConfineType, Cover, NumberCBars,
                       NumberR3Bars, NumberR2Bars, RebarSize, TieSize, TieSpacingLongit, Number2DirTieBars,
                       Number3DirTieBars, ToBeDesigned):
        _count("PropFrame.GetRebarColumn")
        _str(Name, "Name")
        sec = self.st.frame_props.get(Name, {})
        rb = sec.get("rebar")
        if not rb or rb["type"] != "column":
            return ["", "", 0, 0, 0.0, 0, 0, 0, "", "", 0.0, 0, 0, False, 1]
        return [*rb["args"], 0]

    def SetRebarBeam(self, Name, MatPropLong, MatPropConfine, CoverTop, CoverBot, TopLeftArea, TopRightArea,
                     BotLeftArea, BotRightArea):
        _count("PropFrame.SetRebarBeam")
        self.st.need_unlocked("SetRebarBeam")
        sec = self._concrete_section(Name, "SetRebarBeam", ("Rect", "Tee", "Angle", "Circle"))
        self._rebar_mat(MatPropLong, "MatPropLong"); self._rebar_mat(MatPropConfine, "MatPropConfine")
        vals = (CoverTop, CoverBot, TopLeftArea, TopRightArea, BotLeftArea, BotRightArea)
        for v in vals:
            _num(v, "SetRebarBeam value")
        if CoverTop <= 0 or CoverBot <= 0 or CoverTop + CoverBot >= sec["t3"] or min(vals[2:]) < 0:
            raise MockError("SetRebarBeam: covers / areas")
        sec["rebar"] = {"type": "beam", "args": [MatPropLong, MatPropConfine, *vals]}
        return 0

    def GetSectProps(self, Name, Area, As2, As3, Torsion, I22, I33, S22, S33, Z22, Z33, R22, R33):
        _count("PropFrame.GetSectProps")
        _str(Name, "Name")
        for v in (Area, As2, As3, Torsion, I22, I33, S22, S33, Z22, Z33, R22, R33):
            _num(v, "GetSectProps placeholder")
        sec = self.st.frame_props.get(Name)
        if sec is None:
            return [0.0] * 12 + [1]
        p = sap_rect(sec["t3"], sec["t2"]) if sec["shape"] == "Rect" else sec
        return [p[k] for k in ("Area", "As2", "As3", "Torsion", "I22", "I33", "S22", "S33", "Z22", "Z33",
                               "R22", "R33")] + [0]


class FrameObjD(M.FrameObj):
    def SetDesignProcedure(self, Name, MyType, ItemType=0):
        _count("FrameObj.SetDesignProcedure")
        _str(Name, "Name"); _int(MyType, "MyType", {1, 2}); _int(ItemType, "ItemType", {0, 1, 2})
        names = sorted(n for k, n in self.st.groups.get(Name, ())) if ItemType == 1 else [Name]
        for n in names:
            self._need(n, "SetDesignProcedure")["design_proc"] = MyType
        return 0

    def GetDesignProcedure(self, Name, MyType):
        _count("FrameObj.GetDesignProcedure")
        f = self._need(Name, "GetDesignProcedure"); _int(MyType, "MyType")
        if f.get("design_proc", 1) == 2:
            return [9, 0]
        sec = self.st.frame_props.get(f["prop"], {})
        return [{1: 1, 2: 2}.get(self.st.materials.get(sec.get("mat"), {}).get("type"), 9), 0]


class EC2(M._Sub):
    RANGES = {1: {1, 2, 3, 5, 6, 7, 8, 9, 10, 11}, 2: {1, 2}, 3: {1, 2, 3}, 16: {1, 2, 3, 4, 5}, 17: {1, 2, 3}}

    def SetPreference(self, Item, Value):
        _count("DesignConcrete.Eurocode_2_2004.SetPreference")
        _int(Item, "Item", set(range(1, 18))); _num(Value, "Value")
        if Item in self.RANGES and int(Value) not in self.RANGES[Item]:
            return 1
        if (Item == 4 and (Value < 4 or Value % 4)) or (Item == 5 and (Value < 5 or Value % 2 == 0)):
            return 1
        if Item in (7, 8, 9, 10, 11, 12, 13, 15) and Value <= 0:
            return 1
        self.st.design.prefs[Item] = float(Value)
        return 0

    def GetPreference(self, Item, Value):
        _count("DesignConcrete.Eurocode_2_2004.GetPreference")
        _int(Item, "Item", set(range(1, 18))); _num(Value, "Value")
        return [float(self.st.design.prefs[Item]), 0]

    def _column_frame(self, name) -> bool:
        f = self.st.frames[name]
        sec = self.st.frame_props.get(f["prop"], {})
        return f.get("design_proc") == 1 and sec.get("rebar", {}).get("type") == "column"

    def SetOverwrite(self, Name, Item, Value, ItemType=0):
        _count("DesignConcrete.Eurocode_2_2004.SetOverwrite")
        _str(Name, "Name"); _int(Item, "Item", set(range(1, 13))); _num(Value, "Value")
        _int(ItemType, "ItemType", {0, 1, 2})
        names = sorted(n for k, n in self.st.groups.get(Name, ())) if ItemType == 1 else [Name]
        for n in names:
            if n not in self.st.frames:
                raise MockError(f"SetOverwrite: unknown frame {n}")
            if Item >= 7:                                   # v24.0 #7261: Cm/Dns/Ds not used by EC2
                return 1
            if Item == 1 and int(Value) not in (0, 1, 2, 3, 4):
                return 1
            if Item in (5, 6) and not self._column_frame(n):
                return 1
            if Value < 0:
                return 1
            self.st.design.overwrites.setdefault(n, {})[Item] = float(Value)
        return 0

    def GetOverwrite(self, Name, Item, Value, ProgDet):
        _count("DesignConcrete.Eurocode_2_2004.GetOverwrite")
        _str(Name, "Name"); _int(Item, "Item", set(range(1, 13))); _num(Value, "Value"); _bool(ProgDet, "ProgDet")
        if Name not in self.st.frames:
            return [0.0, False, 1]
        v = self.st.design.overwrites.get(Name, {}).get(Item, 0.0)
        return [v, v == 0.0, 0]


class DesignConcrete(M._Sub):
    def __init__(self, st):
        super().__init__(st)
        self.Eurocode_2_2004 = EC2(st)

    def SetCode(self, CodeName):
        _count("DesignConcrete.SetCode")
        _str(CodeName, "CodeName")
        if CodeName not in CONCRETE_CODES:
            return 1
        self.st.design.code = CodeName
        return 0

    def GetCode(self, CodeName):
        _count("DesignConcrete.GetCode")
        _str(CodeName, "CodeName")
        return [self.st.design.code, 0]

    def SetComboAutoGenerate(self, AutoGenerate):
        _count("DesignConcrete.SetComboAutoGenerate")
        _bool(AutoGenerate, "AutoGenerate")
        self.st.design.auto_combos = AutoGenerate
        return 0

    def SetComboStrength(self, Name, Selected):
        _count("DesignConcrete.SetComboStrength")
        _str(Name, "Name"); _bool(Selected, "Selected")
        if Name not in self.st.combos:
            return 1
        s = self.st.design.strength
        if Selected and Name not in s:
            s.append(Name)
        if not Selected and Name in s:
            s.remove(Name)
        return 0

    def GetComboStrength(self, NumberItems, MyName):
        _count("DesignConcrete.GetComboStrength")
        _int(NumberItems, "NumberItems"); _arr(MyName, "MyName")
        return [len(self.st.design.strength), tuple(self.st.design.strength), 0]

    # ---- design -------------------------------------------------------------------------------
    def _design_type(self, name) -> str | None:
        f = self.st.frames[name]
        sec = self.st.frame_props.get(f["prop"], {})
        if f.get("design_proc", 1) != 1 or self.st.materials.get(sec.get("mat"), {}).get("type") != 2:
            return None
        return sec.get("rebar", {}).get("type")

    def _stations(self, f) -> list[float]:
        L, (li, lj) = f["L"], f["offsets"]
        _, seg, _ = f["stations"] or (2, 0.25, 3)
        clear = L - li - lj
        nseg = max(1, math.ceil(clear / seg - 1e-9))
        return [li + clear * k / nseg for k in range(nseg + 1)]

    def StartDesign(self):
        _count("DesignConcrete.StartDesign")
        d = self.st.design
        if not self.st.analyzed:
            return 1
        if d.auto_combos:                                    # SAP adds its code combos (DCon*)
            for k in (1, 2):
                self.st.combos.setdefault(f"DCon{k}", {"type": 0, "items": []})
                if f"DCon{k}" not in d.strength:
                    d.strength.append(f"DCon{k}")
        if not d.strength:
            return 1
        combo = sorted(d.strength)[len(d.strength) // 2]
        d.results = {}
        for idx, name in enumerate(sorted(self.st.frames)):
            kind = self._design_type(name)
            if kind is None:
                continue
            f = self.st.frames[name]
            clear = f["L"] - sum(f["offsets"])
            rows = []
            for s in self._stations(f):
                u = (s - f["offsets"][0]) / clear if clear > 0 else 0.0
                if kind == "column":
                    rows.append({"loc": s, "ratio": 0.30 + 0.55 * u**2 + 0.002 * (idx % 7), "combo": combo,
                                 "area": 58.9e-4, "avmaj": 3.0e-4 + 1.0e-4 * u, "avmin": 2.0e-4})
                else:
                    rows.append({"loc": s, "top": 2.0e-4 + 1.2e-3 * (1 - u), "bot": 3.0e-4 + 1.0e-3 * u,
                                 "v": 6.0e-4 + 4.0e-4 * (1 - u), "tl": 0.0, "tt": 0.0, "combo": combo})
            d.results[name] = {"type": kind, "rows": rows}
        d.designed = True
        return 0

    def GetResultsAvailable(self):
        _count("DesignConcrete.GetResultsAvailable")
        return bool(self.st.design.designed)

    def DeleteResults(self):
        _count("DesignConcrete.DeleteResults")
        self.st.design.results, self.st.design.designed = {}, False
        return 0

    def VerifyPassed(self, NumberItems, n1, n2, MyName):
        _count("DesignConcrete.VerifyPassed")
        _int(NumberItems, "NumberItems"); _int(n1, "n1"); _int(n2, "n2"); _arr(MyName, "MyName")
        lim = self.st.design.prefs[15]
        failed = sorted(n for n, r in self.st.design.results.items()
                        if r["type"] == "column" and max(x["ratio"] for x in r["rows"]) > lim)
        return [len(failed), len(failed), 0, tuple(failed), 0]

    def _summary(self, what, Name, NumberItems, arrays, n_arrays, ItemType, kind):
        _str(Name, f"{what}.Name"); _int(NumberItems, f"{what}.NumberItems(ByRef)")
        if len(arrays) != n_arrays:
            raise MockError(f"{what}: {len(arrays)} ByRef arrays, expected {n_arrays}")
        for k, a in enumerate(arrays):
            _arr(a, f"{what}.array{k}")
        _int(ItemType, "ItemType", {0, 1, 2})
        res = self.st.design.results.get(Name)
        if not self.st.design.designed or res is None or res["type"] != kind:
            return None
        return res["rows"]

    def GetSummaryResultsColumn(self, Name, NumberItems, FrameName, MyOption, Location, PMMCombo, PMMArea,
                                PMMRatio, VmajorCombo, AVmajor, VminorCombo, AVminor, ErrorSummary,
                                WarningSummary, ItemType=0):
        _count("DesignConcrete.GetSummaryResultsColumn")
        rows = self._summary("GetSummaryResultsColumn", Name, NumberItems,
                             [FrameName, MyOption, Location, PMMCombo, PMMArea, PMMRatio, VmajorCombo, AVmajor,
                              VminorCombo, AVminor, ErrorSummary, WarningSummary], 12, ItemType, "column")
        if rows is None:
            return [0] + [()] * 12 + [1]
        check_mode = not self.st.frame_props[self.st.frames[Name]["prop"]]["rebar"]["args"][13]
        cols = [(Name, 1 if check_mode else 2, r["loc"], r["combo"], r["area"], r["ratio"], r["combo"], r["avmaj"],
                 r["combo"], r["avmin"], "", "") for r in rows]
        return [len(cols), *[tuple(c) for c in zip(*cols)], 0]

    def GetSummaryResultsBeam(self, Name, NumberItems, FrameName, Location, TopCombo, TopArea, BotCombo, BotArea,
                              VmajorCombo, VmajorArea, TLCombo, TLArea, TTCombo, TTArea, ErrorSummary,
                              WarningSummary, ItemType=0):
        _count("DesignConcrete.GetSummaryResultsBeam")
        rows = self._summary("GetSummaryResultsBeam", Name, NumberItems,
                             [FrameName, Location, TopCombo, TopArea, BotCombo, BotArea, VmajorCombo, VmajorArea,
                              TLCombo, TLArea, TTCombo, TTArea, ErrorSummary, WarningSummary], 14, ItemType, "beam")
        if rows is None:
            return [0] + [()] * 14 + [1]
        cols = [(Name, r["loc"], r["combo"], r["top"], r["combo"], r["bot"], r["combo"], r["v"], r["combo"], r["tl"],
                 r["combo"], r["tt"], "", "") for r in rows]
        return [len(cols), *[tuple(c) for c in zip(*cols)], 0]


class DatabaseTables(M._Sub):
    """A.10 layouts; only the EC2 overwrite table is simulated."""

    def GetAllTables(self, NumberTables, TableKey, TableName, ImportType, IsEmpty):
        _count("DatabaseTables.GetAllTables")
        _int(NumberTables, "NumberTables")
        for a in (TableKey, TableName, ImportType, IsEmpty):
            _arr(a, "GetAllTables array")
        keys = (OVERWRITE_TABLE, "Preferences - Concrete Design - Eurocode 2-2004", "Frame Section Properties 01 - General")
        if not self.st.design.tables_available:
            keys = keys[2:]
        return [len(keys), keys, keys, tuple(1 for _ in keys), tuple(False for _ in keys), 0]

    def _overwrite_rows(self) -> list[list[str]]:
        dc = DesignConcrete(self.st)
        rows = []
        for name in sorted(self.st.frames):
            kind = dc._design_type(name)
            if kind is None:
                continue
            ow = self.st.design.overwrites.get(name, {})
            tab = self.st.design.table_overwrites.get(name, {})
            ft = {0: "Program Determined", 1: "DC High", 2: "DC Medium", 3: "DC Low", 4: "Secondary"}[int(ow.get(1, 0))]
            rows.append([name, "Program Determined", ft, "0", f"{ow.get(3, 0):g}", f"{ow.get(4, 0):g}",
                         f"{ow.get(5, 0):g}", f"{ow.get(6, 0):g}", tab.get("TanTheta", "0"), "0", tab.get("KPhi", "0")])
        return rows

    def GetTableForEditingArray(self, TableKey, GroupName, TableVersion, FieldKeysIncluded, NumberRecords, TableData):
        _count("DatabaseTables.GetTableForEditingArray")
        _str(TableKey, "TableKey"); _str(GroupName, "GroupName"); _int(TableVersion, "TableVersion")
        _arr(FieldKeysIncluded, "FieldKeysIncluded"); _int(NumberRecords, "NumberRecords"); _arr(TableData, "TableData")
        if TableKey != OVERWRITE_TABLE or not self.st.design.tables_available:
            return [0, (), 0, (), 1]
        rows = self._overwrite_rows()
        return [1, tuple(OVERWRITE_FIELDS), len(rows), tuple(c for r in rows for c in r), 0]

    def SetTableForEditingArray(self, TableKey, TableVersion, FieldKeysIncluded, NumberRecords, TableData):
        _count("DatabaseTables.SetTableForEditingArray")
        _str(TableKey, "TableKey"); _int(TableVersion, "TableVersion"); _arr(FieldKeysIncluded, "FieldKeysIncluded", None, _str)
        _int(NumberRecords, "NumberRecords"); _arr(TableData, "TableData", None, _str)
        nf = len(FieldKeysIncluded)
        if nf * NumberRecords != len(TableData):
            raise MockError("SetTableForEditingArray: data size != fields x records")
        self.st.design.editing = {"key": TableKey, "fields": list(FieldKeysIncluded),
                                  "rows": [list(TableData[i * nf:(i + 1) * nf]) for i in range(NumberRecords)]}
        return [TableVersion, tuple(FieldKeysIncluded), tuple(TableData), 0]

    def ApplyEditedTables(self, FillImportLog, NumFatalErrors, NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog):
        _count("DatabaseTables.ApplyEditedTables")
        _bool(FillImportLog, "FillImportLog")
        for v in (NumFatalErrors, NumErrorMsgs, NumWarnMsgs, NumInfoMsgs):
            _int(v, "ApplyEditedTables count")
        _str(ImportLog, "ImportLog")
        ed = self.st.design.editing
        if ed is None:
            return [1, 0, 0, 0, "nothing to apply", 1]
        f = ed["fields"]
        for r in ed["rows"]:
            float(r[f.index("KPhi")]); float(r[f.index("TanTheta")])
            self.st.design.table_overwrites[r[f.index("Frame")]] = {"TanTheta": r[f.index("TanTheta")],
                                                                    "KPhi": r[f.index("KPhi")]}
        self.st.design.editing = None
        return [0, 0, 0, 0, "", 0]

    def CancelTableEditing(self):
        _count("DatabaseTables.CancelTableEditing")
        self.st.design.editing = None
        return 0


class SapModel(M.SapModel):
    def __init__(self, synth=None, missing_bars=(), tables_available: bool = True):
        super().__init__(synth)
        self._design_args = (tuple(missing_bars), tables_available)
        self._st.design = DesignState(*self._design_args)
        st = self._st
        self.PropMaterial = PropMaterialD(st)
        self.PropFrame = PropFrameD(st)
        self.FrameObj = FrameObjD(st)
        self.PropRebar = PropRebar(st)
        self.DesignConcrete = DesignConcrete(st)
        self.DatabaseTables = DatabaseTables(st)

    def InitializeNewModel(self, Units=3):
        ret = super().InitializeNewModel(Units)
        self._st.design = DesignState(*self._design_args)
        return ret


class XlsxSynth:
    """Frame forces (SAP2000 conventions) interpolated from the SAP2000 v27.1 Excel export of the
    current model - lets the mock return 'SAP' forces for the analysis-identity check."""

    def __init__(self, path: Path | None = None):
        import esfuerzos as E
        self.rows: dict = {}
        for r in E.read_table(path or E.SAP_FRAMES_XLSX):
            self.rows.setdefault((r["Frame"], r["OutputCase"]), []).append(
                (float(r["Station"]), *(float(r[k]) for k in ("P", "V2", "V3", "T", "M2", "M3"))))
        for v in self.rows.values():
            v.sort(key=lambda t: t[0])

    def frame(self, name, s, c):
        rows = self.rows[(name, c)]
        for r in rows:
            if abs(r[0] - s) < 1e-6:
                return r[1:]
        for a, b in zip(rows, rows[1:]):
            if a[0] <= s <= b[0] and b[0] > a[0]:
                t = (s - a[0]) / (b[0] - a[0])
                return tuple(x + t * (y - x) for x, y in zip(a[1:], b[1:]))
        return min(rows, key=lambda r: abs(r[0] - s))[1:]
