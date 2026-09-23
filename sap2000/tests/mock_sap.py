"""Strict mock of the SAP2000 OAPI (SAP2000v1) as seen through comtypes.

* Every method has exactly the documented parameter list (required + optional with defaults),
  so a wrong argument count raises TypeError.
* Types / enum ranges / existence of referenced objects are validated; violations raise
  MockError (a real OAPI call would return a nonzero code -> we make it loud).
* Return values follow the comtypes convention: plain int when the method has no ByRef
  parameter; otherwise a list [ByRef values in declaration order..., ret].
* Results are synthetic but physical: they come from the PyNite re-analysis of the same model
  data, converted to SAP2000 output conventions (CSI "Frame Element Internal Forces Output
  Conventions": P/V2/V3/T on the positive-1 face along +local axes; positive M3 = moment
  vector +3 on the positive-1 face; positive M2 = compression on the +3 face = moment vector
  -2 on the positive-1 face; no output inside end offsets; ObjSta measured from the I-end).
"""

from __future__ import annotations

import math
import numbers

CALLS: dict[str, int] = {}


class MockError(Exception):
    pass


def _count(name):
    CALLS[name] = CALLS.get(name, 0) + 1


def _str(v, what):
    if not isinstance(v, str):
        raise MockError(f"{what}: expected str, got {type(v).__name__} {v!r}")


def _num(v, what):
    if isinstance(v, bool) or not isinstance(v, numbers.Real) or not math.isfinite(float(v)):
        raise MockError(f"{what}: expected finite number, got {type(v).__name__} {v!r}")


def _int(v, what, allowed=None):
    if isinstance(v, bool) or not isinstance(v, numbers.Integral):
        raise MockError(f"{what}: expected int, got {type(v).__name__} {v!r}")
    if allowed is not None and v not in allowed:
        raise MockError(f"{what}: {v} not in {sorted(allowed)}")


def _bool(v, what):
    if not isinstance(v, bool):
        raise MockError(f"{what}: expected bool, got {type(v).__name__} {v!r}")


def _arr(v, what, n=None, kind=None):
    if not isinstance(v, (list, tuple)):
        raise MockError(f"{what}: expected array (list/tuple), got {type(v).__name__}")
    if n is not None and len(v) != n:
        raise MockError(f"{what}: expected {n} items, got {len(v)}")
    for k, x in enumerate(v):
        if kind is not None:
            kind(x, f"{what}[{k}]")


class Model:
    def __init__(self):
        self.initialized = False
        self.units = None
        self.saved_path = None
        self.analyzed = False
        self.locked = False
        self.materials = {}
        self.frame_props = {}
        self.area_props = {"Default": {}}
        self.points = {}
        self.frames = {}
        self.areas = {}
        self.constraints = {}
        self.groups = {"ALL": set()}
        self.patterns = {}
        self.cases = {}
        self.combos = {}
        self.run_flags = {}
        self.selected_cases = set()
        self.selected_combos = set()
        self.next_id = 1

    def default_name(self):
        n = str(self.next_id)
        self.next_id += 1
        return n

    def need_unlocked(self, what):
        if self.locked:
            raise MockError(f"{what}: model is locked (analysed)")


class _Sub:
    def __init__(self, st: Model, results=None):
        self.st = st
        self.results = results


# ------------------------------------------------------------------------------------------
class File(_Sub):
    def NewBlank(self):
        _count("File.NewBlank")
        st = self.st
        if not st.initialized:
            raise MockError("NewBlank before InitializeNewModel")
        st.patterns = {"DEAD": {"type": 1, "sw": 1.0}}
        st.cases = {"DEAD": {"type": "LinStatic", "loads": [("Load", "DEAD", 1.0)]},
                    "MODAL": {"type": "Modal", "loads": []}}
        st.run_flags = {"DEAD": True, "MODAL": True}
        st.materials.update({"4000Psi": {"type": 2}, "A992Fy50": {"type": 1}})
        return 0

    def OpenFile(self, FileName):
        _count("File.OpenFile")
        _str(FileName, "OpenFile.FileName")
        raise MockError("OpenFile not simulated")

    def Save(self, FileName=""):
        _count("File.Save")
        _str(FileName, "Save.FileName")
        if not FileName and not self.st.saved_path:
            raise MockError("Save without a file name on a never-saved model")
        if FileName and not FileName.lower().endswith(".sdb"):
            raise MockError(f"Save: expected .sdb, got {FileName}")
        self.st.saved_path = FileName or self.st.saved_path
        return 0


class PropMaterial(_Sub):
    def SetMaterial(self, Name, MatType, Color=-1, Notes="", GUID=""):
        _count("PropMaterial.SetMaterial")
        _str(Name, "SetMaterial.Name"); _int(MatType, "SetMaterial.MatType", set(range(1, 9)))
        _int(Color, "Color"); _str(Notes, "Notes"); _str(GUID, "GUID")
        self.st.materials[Name] = {"type": MatType}
        return 0

    def SetMPIsotropic(self, Name, E, U, A, Temp=0):
        _count("PropMaterial.SetMPIsotropic")
        _str(Name, "Name")
        if Name not in self.st.materials:
            raise MockError(f"SetMPIsotropic: unknown material {Name}")
        for v, w in ((E, "E"), (U, "U"), (A, "A"), (Temp, "Temp")):
            _num(v, f"SetMPIsotropic.{w}")
        if not (E > 0 and -1 < U < 0.5):
            raise MockError(f"SetMPIsotropic: bad E/U {E} {U}")
        self.st.materials[Name].update(E=E, U=U, A=A)
        return 0

    def SetWeightAndMass(self, Name, MyOption, Value, Temp=0):
        _count("PropMaterial.SetWeightAndMass")
        _str(Name, "Name"); _int(MyOption, "MyOption", {1, 2}); _num(Value, "Value"); _num(Temp, "Temp")
        if Name not in self.st.materials:
            raise MockError(f"SetWeightAndMass: unknown material {Name}")
        self.st.materials[Name]["w"] = Value
        return 0

    def SetOConcrete_1(self, Name, Fc, IsLightweight, FcsFactor, SSType, SSHysType, StrainAtFc,
                       StrainUltimate, FinalSlope, FrictionAngle=0, DilatationalAngle=0, Temp=0):
        _count("PropMaterial.SetOConcrete_1")
        _str(Name, "Name")
        if self.st.materials.get(Name, {}).get("type") != 2:
            raise MockError(f"SetOConcrete_1: {Name} is not an existing concrete material")
        _num(Fc, "Fc"); _bool(IsLightweight, "IsLightweight"); _num(FcsFactor, "FcsFactor")
        _int(SSType, "SSType", {0, 1, 2}); _int(SSHysType, "SSHysType", set(range(0, 8)))
        for v, w in ((StrainAtFc, "StrainAtFc"), (StrainUltimate, "StrainUltimate"),
                     (FinalSlope, "FinalSlope"), (FrictionAngle, "FrictionAngle"),
                     (DilatationalAngle, "DilatationalAngle"), (Temp, "Temp")):
            _num(v, w)
        if not StrainUltimate > StrainAtFc > 0:
            raise MockError("SetOConcrete_1: StrainUltimate must exceed StrainAtFc")
        if Fc <= 0:
            raise MockError("SetOConcrete_1: Fc <= 0")
        return 0


class PropFrame(_Sub):
    def SetRectangle(self, Name, MatProp, T3, T2, Color=-1, Notes="", GUID=""):
        _count("PropFrame.SetRectangle")
        _str(Name, "Name"); _str(MatProp, "MatProp"); _num(T3, "T3"); _num(T2, "T2")
        if MatProp not in self.st.materials:
            raise MockError(f"SetRectangle: unknown material {MatProp}")
        self.st.frame_props[Name] = {"shape": "Rect", "t3": T3, "t2": T2, "mods": [1.0] * 8}
        return 0

    def SetGeneral(self, Name, MatProp, T3, T2, Area, As2, As3, Torsion, I22, I33, S22, S33,
                   Z22, Z33, R22, R33, Color=-1, Notes="", GUID=""):
        _count("PropFrame.SetGeneral")
        _str(Name, "Name"); _str(MatProp, "MatProp")
        vals = dict(T3=T3, T2=T2, Area=Area, As2=As2, As3=As3, Torsion=Torsion, I22=I22,
                    I33=I33, S22=S22, S33=S33, Z22=Z22, Z33=Z33, R22=R22, R33=R33)
        for k, v in vals.items():
            _num(v, f"SetGeneral.{k}")
            if v <= 0:
                raise MockError(f"SetGeneral.{k} <= 0")
        if MatProp not in self.st.materials:
            raise MockError(f"SetGeneral: unknown material {MatProp}")
        # plausibility: R = sqrt(I/A)
        for r, i in (("R22", "I22"), ("R33", "I33")):
            if abs(vals[r] - (vals[i] / vals["Area"]) ** 0.5) > 1e-6:
                raise MockError(f"SetGeneral: {r} inconsistent with {i} (argument order?)")
        self.st.frame_props[Name] = {"shape": "General", **vals, "mods": [1.0] * 8}
        return 0

    def SetModifiers(self, Name, Value):
        _count("PropFrame.SetModifiers")
        _str(Name, "Name"); _arr(Value, "PropFrame.SetModifiers.Value", 8, _num)
        if Name not in self.st.frame_props:
            raise MockError(f"PropFrame.SetModifiers: unknown section {Name}")
        if any(v < 0 for v in Value):
            raise MockError("negative modifier")
        self.st.frame_props[Name]["mods"] = list(Value)
        return [tuple(Value), 0]


class PropArea(_Sub):
    def SetShell_1(self, Name, ShellType, IncludeDrillingDOF, MatProp, MatAng, Thickness, Bending,
                   Color=-1, Notes="", GUID=""):
        _count("PropArea.SetShell_1")
        _str(Name, "Name"); _int(ShellType, "ShellType", set(range(1, 7)))
        _bool(IncludeDrillingDOF, "IncludeDrillingDOF"); _str(MatProp, "MatProp")
        _num(MatAng, "MatAng"); _num(Thickness, "Thickness"); _num(Bending, "Bending")
        if MatProp not in self.st.materials:
            raise MockError(f"SetShell_1: unknown material {MatProp}")
        self.st.area_props[Name] = {"type": ShellType, "t": Thickness, "mods": [1.0] * 10}
        return 0

    def SetModifiers(self, Name, Value):
        _count("PropArea.SetModifiers")
        _str(Name, "Name"); _arr(Value, "PropArea.SetModifiers.Value", 10, _num)
        if Name not in self.st.area_props:
            raise MockError(f"PropArea.SetModifiers: unknown area property {Name}")
        self.st.area_props[Name]["mods"] = list(Value)
        return [tuple(Value), 0]


class PointObj(_Sub):
    def AddCartesian(self, X, Y, Z, Name, UserName="", CSys="Global", MergeOff=False, MergeNumber=0):
        _count("PointObj.AddCartesian")
        _num(X, "X"); _num(Y, "Y"); _num(Z, "Z"); _str(Name, "Name(ByRef)"); _str(UserName, "UserName")
        _str(CSys, "CSys"); _bool(MergeOff, "MergeOff"); _int(MergeNumber, "MergeNumber")
        if CSys != "Global":
            raise MockError("only Global csys in mock")
        st = self.st
        st.need_unlocked("AddCartesian")
        if not MergeOff:
            for n, p in st.points.items():
                if max(abs(p["xyz"][0] - X), abs(p["xyz"][1] - Y), abs(p["xyz"][2] - Z)) < 1e-6:
                    return [n, 0]
        nm = UserName if UserName and UserName not in st.points else st.default_name()
        st.points[nm] = {"xyz": (float(X), float(Y), float(Z)), "restr": [False] * 6,
                         "constraints": [], "loads": []}
        return [nm, 0]

    def SetRestraint(self, Name, Value, ItemType=0):
        _count("PointObj.SetRestraint")
        _str(Name, "Name"); _arr(Value, "SetRestraint.Value", 6, _bool); _int(ItemType, "ItemType", {0, 1, 2})
        if Name not in self.st.points:
            raise MockError(f"SetRestraint: unknown point {Name}")
        self.st.points[Name]["restr"] = list(Value)
        return [tuple(Value), 0]

    def SetConstraint(self, Name, ConstraintName, ItemType=0, Replace=True):
        _count("PointObj.SetConstraint")
        _str(Name, "Name"); _str(ConstraintName, "ConstraintName"); _int(ItemType, "ItemType", {0, 1, 2})
        _bool(Replace, "Replace")
        if Name not in self.st.points:
            raise MockError(f"SetConstraint: unknown point {Name}")
        if ConstraintName not in self.st.constraints:
            raise MockError(f"SetConstraint: unknown constraint {ConstraintName}")
        self.st.points[Name]["constraints"] = [ConstraintName]
        return [ConstraintName, 0]

    def SetLoadForce(self, Name, LoadPat, Value, Replace=False, CSys="Global", ItemType=0):
        _count("PointObj.SetLoadForce")
        _str(Name, "Name"); _str(LoadPat, "LoadPat"); _arr(Value, "SetLoadForce.Value", 6, _num)
        _bool(Replace, "Replace"); _str(CSys, "CSys"); _int(ItemType, "ItemType", {0, 1, 2})
        if Name not in self.st.points:
            raise MockError(f"SetLoadForce: unknown point {Name}")
        if LoadPat not in self.st.patterns:
            raise MockError(f"SetLoadForce: unknown load pattern {LoadPat}")
        self.st.points[Name]["loads"].append((LoadPat, tuple(Value)))
        return [tuple(Value), 0]

    def SetGroupAssign(self, Name, GroupName, Remove=False, ItemType=0):
        _count("PointObj.SetGroupAssign")
        return _group_assign(self.st, self.st.points, "Point", Name, GroupName, Remove, ItemType)


def _group_assign(st, objs, kind, Name, GroupName, Remove, ItemType):
    _str(Name, "Name"); _str(GroupName, "GroupName"); _bool(Remove, "Remove"); _int(ItemType, "ItemType", {0, 1, 2})
    if Name not in objs:
        raise MockError(f"{kind}.SetGroupAssign: unknown object {Name}")
    if GroupName not in st.groups:
        raise MockError(f"{kind}.SetGroupAssign: unknown group {GroupName}")
    st.groups[GroupName].add((kind, Name))
    return 0


class FrameObj(_Sub):
    def AddByPoint(self, Point1, Point2, Name, PropName="Default", UserName=""):
        _count("FrameObj.AddByPoint")
        _str(Point1, "Point1"); _str(Point2, "Point2"); _str(Name, "Name(ByRef)")
        _str(PropName, "PropName"); _str(UserName, "UserName")
        st = self.st
        st.need_unlocked("FrameObj.AddByPoint")
        for p in (Point1, Point2):
            if p not in st.points:
                raise MockError(f"FrameObj.AddByPoint: unknown point {p}")
        if Point1 == Point2:
            raise MockError("zero-length frame")
        if PropName not in st.frame_props and PropName not in ("Default", "None"):
            raise MockError(f"FrameObj.AddByPoint: unknown section {PropName}")
        nm = UserName if UserName and UserName not in st.frames else st.default_name()
        a, b = st.points[Point1]["xyz"], st.points[Point2]["xyz"]
        st.frames[nm] = {"i": Point1, "j": Point2, "prop": PropName, "L": math.dist(a, b),
                         "offsets": (0.0, 0.0), "loads": [], "stations": None, "angle": 0.0}
        return [nm, 0]

    def _need(self, Name, what):
        _str(Name, f"{what}.Name")
        if Name not in self.st.frames:
            raise MockError(f"{what}: unknown frame {Name}")
        return self.st.frames[Name]

    def SetLocalAxes(self, Name, Ang, ItemType=0):
        _count("FrameObj.SetLocalAxes")
        f = self._need(Name, "SetLocalAxes"); _num(Ang, "Ang"); _int(ItemType, "ItemType", {0, 1, 2})
        f["angle"] = Ang
        return 0

    def SetOutputStations(self, Name, MyType, MaxSegSize, MinSections, NoOutPutAndDesignAtElementEnds=False,
                          NoOutPutAndDesignAtPointLoads=False, ItemType=0):
        _count("FrameObj.SetOutputStations")
        f = self._need(Name, "SetOutputStations")
        _int(MyType, "MyType", {1, 2}); _num(MaxSegSize, "MaxSegSize"); _int(MinSections, "MinSections")
        _bool(NoOutPutAndDesignAtElementEnds, "NoOutPutAndDesignAtElementEnds")
        _bool(NoOutPutAndDesignAtPointLoads, "NoOutPutAndDesignAtPointLoads"); _int(ItemType, "ItemType", {0, 1, 2})
        if MyType == 1 and MaxSegSize <= 0:
            raise MockError("MaxSegSize <= 0")
        f["stations"] = (MyType, MaxSegSize, MinSections)
        return 0

    def SetModifiers(self, Name, Value, ItemType=0):
        _count("FrameObj.SetModifiers")
        _str(Name, "Name"); _arr(Value, "FrameObj.SetModifiers.Value", 8, _num)
        self._need(Name, "FrameObj.SetModifiers")
        if any(v <= 0 for v in Value[:6]):
            raise MockError("non-positive stiffness modifier")
        return [tuple(Value), 0]

    def SetEndLengthOffset(self, Name, AutoOffset, Length1, Length2, RZ, ItemType=0):
        _count("FrameObj.SetEndLengthOffset")
        f = self._need(Name, "SetEndLengthOffset")
        _bool(AutoOffset, "AutoOffset"); _num(Length1, "Length1"); _num(Length2, "Length2"); _num(RZ, "RZ")
        _int(ItemType, "ItemType", {0, 1, 2})
        if not 0 <= RZ <= 1:
            raise MockError("RZ outside 0..1")
        if Length1 < 0 or Length2 < 0 or Length1 + Length2 >= f["L"]:
            raise MockError(f"SetEndLengthOffset {Name}: offsets {Length1}+{Length2} >= L {f['L']}")
        f["offsets"] = (float(Length1), float(Length2))
        return 0

    def SetLoadDistributed(self, Name, LoadPat, MyType, Dir, Dist1, Dist2, Val1, Val2, CSys="Global",
                           RelDist=True, Replace=True, ItemType=0):
        _count("FrameObj.SetLoadDistributed")
        f = self._need(Name, "SetLoadDistributed")
        _str(LoadPat, "LoadPat"); _int(MyType, "MyType", {1, 2}); _int(Dir, "Dir", set(range(1, 12)))
        for v, w in ((Dist1, "Dist1"), (Dist2, "Dist2"), (Val1, "Val1"), (Val2, "Val2")):
            _num(v, w)
        _str(CSys, "CSys"); _bool(RelDist, "RelDist"); _bool(Replace, "Replace"); _int(ItemType, "ItemType", {0, 1, 2})
        if LoadPat not in self.st.patterns:
            raise MockError(f"SetLoadDistributed: unknown pattern {LoadPat}")
        if Dir in (10, 11) and CSys != "Global":
            raise MockError("gravity dir needs Global csys")
        if RelDist and not (0 <= Dist1 <= Dist2 <= 1):
            raise MockError("relative distances outside 0..1")
        if Replace:
            f["loads"] = [l for l in f["loads"] if l[0] != LoadPat]
        f["loads"].append((LoadPat, MyType, Dir, Dist1, Dist2, Val1, Val2))
        return 0

    def SetGroupAssign(self, Name, GroupName, Remove=False, ItemType=0):
        _count("FrameObj.SetGroupAssign")
        return _group_assign(self.st, self.st.frames, "Frame", Name, GroupName, Remove, ItemType)


class AreaObj(_Sub):
    def AddByPoint(self, NumberPoints, Point, Name, PropName="Default", UserName=""):
        _count("AreaObj.AddByPoint")
        _int(NumberPoints, "NumberPoints"); _arr(Point, "AreaObj.AddByPoint.Point", NumberPoints, _str)
        _str(Name, "Name(ByRef)"); _str(PropName, "PropName"); _str(UserName, "UserName")
        st = self.st
        for p in Point:
            if p not in st.points:
                raise MockError(f"AreaObj.AddByPoint: unknown point {p}")
        if PropName not in st.area_props and PropName != "None":
            raise MockError(f"AreaObj.AddByPoint: unknown area property {PropName}")
        nm = UserName if UserName and UserName not in st.areas else st.default_name()
        st.areas[nm] = {"points": list(Point), "prop": PropName, "loads": []}
        return [tuple(Point), nm, 0]

    def SetLoadUniform(self, Name, LoadPat, Value, Dir, Replace=True, CSys="Global", ItemType=0):
        _count("AreaObj.SetLoadUniform")
        _str(Name, "Name"); _str(LoadPat, "LoadPat"); _num(Value, "Value")
        _int(Dir, "Dir", set(range(1, 12))); _bool(Replace, "Replace"); _str(CSys, "CSys")
        _int(ItemType, "ItemType", {0, 1, 2})
        if Name not in self.st.areas:
            raise MockError(f"SetLoadUniform: unknown area {Name}")
        if LoadPat not in self.st.patterns:
            raise MockError(f"SetLoadUniform: unknown pattern {LoadPat}")
        if Dir in (10, 11) and CSys != "Global":
            raise MockError("gravity dir needs Global csys")
        a = self.st.areas[Name]
        if Replace:
            a["loads"] = [l for l in a["loads"] if l[0] != LoadPat]
        a["loads"].append((LoadPat, Value, Dir))
        return 0

    def SetGroupAssign(self, Name, GroupName, Remove=False, ItemType=0):
        _count("AreaObj.SetGroupAssign")
        return _group_assign(self.st, self.st.areas, "Area", Name, GroupName, Remove, ItemType)


class ConstraintDef(_Sub):
    def SetDiaphragm(self, Name, Axis=4, CSys="Global"):
        _count("ConstraintDef.SetDiaphragm")
        _str(Name, "Name"); _int(Axis, "Axis", {1, 2, 3, 4}); _str(CSys, "CSys")
        self.st.constraints[Name] = {"type": "Diaphragm", "axis": Axis}
        return 0


class GroupDef(_Sub):
    def SetGroup(self, Name, Color=-1, SpecifiedForSelection=True, SpecifiedForSectionCutDefinition=True,
                 SpecifiedForSteelDesign=True, SpecifiedForConcreteDesign=True,
                 SpecifiedForAluminumDesign=True, SpecifiedForColdFormedDesign=True,
                 SpecifiedForStaticNLActiveStage=True, SpecifiedForBridgeResponseOutput=True,
                 SpecifiedForAutoSeismicOutput=False, SpecifiedForAutoWindOutput=False,
                 SpecifiedForMassAndWeight=True):
        _count("GroupDef.SetGroup")
        _str(Name, "Name")
        self.st.groups.setdefault(Name, set())
        return 0


class LoadPatterns(_Sub):
    def Add(self, Name, MyType, SelfWTMultiplier=0, AddAnalysisCase=True):
        _count("LoadPatterns.Add")
        _str(Name, "Name"); _int(MyType, "MyType", set(range(1, 60))); _num(SelfWTMultiplier, "SelfWTMultiplier")
        _bool(AddAnalysisCase, "AddAnalysisCase")
        st = self.st
        if Name.upper() in {p.upper() for p in st.patterns}:
            return 1
        st.patterns[Name] = {"type": MyType, "sw": float(SelfWTMultiplier)}
        if AddAnalysisCase:
            if Name.upper() in {c.upper() for c in st.cases}:
                return 1
            st.cases[Name] = {"type": "LinStatic", "loads": [("Load", Name, 1.0)]}
            st.run_flags[Name] = True
        return 0

    def Delete(self, Name):
        _count("LoadPatterns.Delete")
        _str(Name, "Name")
        st = self.st
        if Name not in st.patterns:
            return 1
        if any(l[1] == Name for c in st.cases.values() for l in c["loads"]) or len(st.patterns) == 1:
            return 1
        del st.patterns[Name]
        return 0


class LoadCases(_Sub):
    def Delete(self, Name):
        _count("LoadCases.Delete")
        _str(Name, "Name")
        if Name not in self.st.cases:
            return 1
        del self.st.cases[Name]
        self.st.run_flags.pop(Name, None)
        return 0


class RespCombo(_Sub):
    def Add(self, Name, ComboType):
        _count("RespCombo.Add")
        _str(Name, "Name"); _int(ComboType, "ComboType", {0, 1, 2, 3, 4})
        st = self.st
        taken = {n.upper() for n in list(st.cases) + list(st.combos)}
        if Name.upper() in taken:
            return 1
        st.combos[Name] = {"type": ComboType, "items": []}
        return 0

    def SetCaseList(self, Name, CNameType, CName, SF):
        _count("RespCombo.SetCaseList")
        _str(Name, "Name"); _int(CNameType, "CNameType(ByRef)", {0, 1}); _str(CName, "CName"); _num(SF, "SF")
        st = self.st
        if Name not in st.combos:
            raise MockError(f"SetCaseList: unknown combo {Name}")
        pool = st.cases if CNameType == 0 else st.combos
        if CName not in pool:
            raise MockError(f"SetCaseList: {CName} is not a {'case' if CNameType == 0 else 'combo'}")
        if CName == Name:
            raise MockError("combo references itself")
        st.combos[Name]["items"].append((CNameType, CName, SF))
        return [CNameType, 0]


class Analyze(_Sub):
    def SetRunCaseFlag(self, Name, Run, All=False):
        _count("Analyze.SetRunCaseFlag")
        _str(Name, "Name"); _bool(Run, "Run"); _bool(All, "All")
        if All:
            for c in self.st.run_flags:
                self.st.run_flags[c] = Run
            return 0
        if Name not in self.st.cases:
            return 1
        self.st.run_flags[Name] = Run
        return 0

    def RunAnalysis(self):
        _count("Analyze.RunAnalysis")
        st = self.st
        if not st.saved_path:
            raise MockError("RunAnalysis before File.Save(name)")
        st.analyzed = True
        st.locked = True
        return 0


class Setup(_Sub):
    def DeselectAllCasesAndCombosForOutput(self):
        _count("Results.Setup.DeselectAllCasesAndCombosForOutput")
        self.st.selected_cases.clear(); self.st.selected_combos.clear()
        return 0

    def SetCaseSelectedForOutput(self, Name, Selected=True):
        _count("Results.Setup.SetCaseSelectedForOutput")
        _str(Name, "Name"); _bool(Selected, "Selected")
        if Name not in self.st.cases:
            return 1
        (self.st.selected_cases.add if Selected else self.st.selected_cases.discard)(Name)
        return 0

    def SetComboSelectedForOutput(self, Name, Selected=True):
        _count("Results.Setup.SetComboSelectedForOutput")
        _str(Name, "Name"); _bool(Selected, "Selected")
        if Name not in self.st.combos:
            return 1
        (self.st.selected_combos.add if Selected else self.st.selected_combos.discard)(Name)
        return 0


class Results(_Sub):
    def __init__(self, st, synth):
        super().__init__(st)
        self.Setup = Setup(st)
        self.synth = synth

    def _pre(self, what):
        if not self.st.analyzed:
            raise MockError(f"{what}: no analysis results")
        return [c for c in self.st.cases if c in self.st.selected_cases and self.st.run_flags.get(c)]

    @staticmethod
    def _placeholders(what, NumberResults, arrays, n):
        _int(NumberResults, f"{what}.NumberResults(ByRef)")
        if len(arrays) != n:
            raise MockError(f"{what}: {len(arrays)} ByRef arrays, expected {n}")
        for k, a in enumerate(arrays):
            _arr(a, f"{what}.array{k}")

    def JointReact(self, Name, ItemTypeElm, NumberResults, Obj, Elm, LoadCase, StepType, StepNum,
                   F1, F2, F3, M1, M2, M3):
        _count("Results.JointReact")
        _str(Name, "Name"); _int(ItemTypeElm, "ItemTypeElm", {0, 1, 2, 3})
        self._placeholders("JointReact", NumberResults, [Obj, Elm, LoadCase, StepType, StepNum, F1, F2, F3, M1, M2, M3], 11)
        cases = self._pre("JointReact")
        if ItemTypeElm != 0 or Name not in self.st.points:
            return [0, (), (), (), (), (), (), (), (), (), (), (), 1]
        if not any(self.st.points[Name]["restr"]):
            return [0, (), (), (), (), (), (), (), (), (), (), (), 0]
        rows = [(Name, Name, c, "", 0.0, *self.synth.react(Name, c)) for c in cases]
        cols = list(zip(*rows)) if rows else [()] * 11
        return [len(rows), *[tuple(c) for c in cols], 0]

    def JointDispl(self, Name, ItemTypeElm, NumberResults, Obj, Elm, LoadCase, StepType, StepNum,
                   U1, U2, U3, R1, R2, R3):
        _count("Results.JointDispl")
        _str(Name, "Name"); _int(ItemTypeElm, "ItemTypeElm", {0, 1, 2, 3})
        self._placeholders("JointDispl", NumberResults, [Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3], 11)
        cases = self._pre("JointDispl")
        if ItemTypeElm != 0 or Name not in self.st.points:
            return [0, (), (), (), (), (), (), (), (), (), (), (), 1]
        rows = [(Name, Name, c, "", 0.0, *self.synth.displ(Name, c)) for c in cases]
        cols = list(zip(*rows)) if rows else [()] * 11
        return [len(rows), *[tuple(c) for c in cols], 0]

    def FrameForce(self, Name, ItemTypeElm, NumberResults, Obj, ObjSta, Elm, ElmSta, LoadCase, StepType,
                   StepNum, P, V2, V3, T, M2, M3):
        _count("Results.FrameForce")
        _str(Name, "Name"); _int(ItemTypeElm, "ItemTypeElm", {0, 1, 2, 3})
        self._placeholders("FrameForce", NumberResults,
                           [Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, P, V2, V3, T, M2, M3], 13)
        cases = self._pre("FrameForce")
        if ItemTypeElm != 0 or Name not in self.st.frames:
            return [0] + [()] * 13 + [1]
        f = self.st.frames[Name]
        L = f["L"]
        li, lj = f["offsets"]
        mytype, seg, _ = f["stations"] or (2, None, 3)
        clear = L - li - lj
        nseg = max(1, math.ceil(clear / seg - 1e-9)) if mytype == 1 else 2
        stas = [li + clear * k / nseg for k in range(nseg + 1)]
        rows = []
        for c in cases:
            for s in stas:
                p, v2, v3, t, m2, m3 = self.synth.frame(Name, s, c)
                rows.append((Name, s, f"{Name}-1", s - li, c, "", 0.0, p, v2, v3, t, m2, m3))
        cols = list(zip(*rows)) if rows else [()] * 13
        return [len(rows), *[tuple(x) for x in cols], 0]


class SapModel:
    def __init__(self, synth=None):
        st = Model()
        self._st = st
        self.File = File(st)
        self.PropMaterial = PropMaterial(st)
        self.PropFrame = PropFrame(st)
        self.PropArea = PropArea(st)
        self.PointObj = PointObj(st)
        self.FrameObj = FrameObj(st)
        self.AreaObj = AreaObj(st)
        self.ConstraintDef = ConstraintDef(st)
        self.GroupDef = GroupDef(st)
        self.LoadPatterns = LoadPatterns(st)
        self.LoadCases = LoadCases(st)
        self.RespCombo = RespCombo(st)
        self.Analyze = Analyze(st)
        self.Results = Results(st, synth)

    def InitializeNewModel(self, Units=3):
        _count("SapModel.InitializeNewModel")
        _int(Units, "Units", set(range(1, 17)))
        self._st.__init__()
        self._st.initialized = True
        self._st.units = Units
        return 0

    def SetPresentUnits(self, Units):
        _count("SapModel.SetPresentUnits")
        _int(Units, "Units", set(range(1, 17)))
        self._st.units = Units
        return 0

    def SetModelIsLocked(self, Locked):
        _bool(Locked, "Locked")
        self._st.locked = Locked
        return 0


class SapObject:
    def __init__(self, synth=None):
        self.SapModel = SapModel(synth)
        self.started = False

    def ApplicationStart(self, Units=3, Visible=True, FileName=""):
        _count("SapObject.ApplicationStart")
        self.started = True
        return 0

    def ApplicationExit(self, FileSave):
        _bool(FileSave, "FileSave")
        return 0


class Helper:
    def __init__(self, synth=None):
        self.synth = synth

    def QueryInterface(self, iface):
        return self

    def CreateObjectProgID(self, progID):
        _count("cHelper.CreateObjectProgID")
        _str(progID, "progID")
        if progID != "CSI.SAP2000.API.SapObject":
            raise MockError(progID)
        return SapObject(self.synth)

    def GetObject(self, typeName):
        _count("cHelper.GetObject")
        _str(typeName, "typeName")
        if typeName != "CSI.SAP2000.API.SapObject":
            raise MockError(typeName)
        return SapObject(self.synth)
