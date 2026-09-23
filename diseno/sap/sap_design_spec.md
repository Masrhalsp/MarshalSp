# SAP2000 v27.1 — Concrete Frame Design to "Eurocode 2-2004": implementation spec (Muelle de Trasmallo)

Scope: piles 40x40 HA-50 with 12Ø25 in **CHECK** mode, transverse beams (inverted T 50x55+15x30+15x30,
inverted L 80x55+15x30) **designed** (required As), through (1) the CSI OAPI (Python + comtypes, pattern of
`sap2000/tools/sap_oapi_run.py`) and (2) the `.$2k` text import (pattern of `sap2000/tools/write_s2k.py`).

Confidence tags used below:

* **VERIFIED** – stated in an official CSI document, or seen in a real SAP2000-exported `.$2k`/`.s2k`/xlsx
  file (version given).
* **VERIFIED-3P** – taken from third-party code that reads/writes real SAP2000 files or was run against a
  live SAP2000 (source given). Good, but not CSI.
* **INFERRED** – consistent with several sources but not seen literally for EC2 in v27.
* **UNVERIFIED** – could not be confirmed; must be checked once in SAP2000 (a 10-minute check is described in §6).

All evidence downloaded during this research is kept in
`scratchpad/research/{csi,gh,pdf}/` (CSI help pages as .txt, real .s2k files, manuals and release notes as .txt).

**Independent check (adversarial review, 2026-09-23).** Every OAPI signature used in the snippets was re-checked
against a second source that is not the online CSI help: third-party SAP2000/ETABS code calling the function with
the same argument list or reading the same result indices, and a SAP2000v1 type-library listing ([G13]-[G16] and the
"other confirmations" line in §1). The functions checked were SetRebarColumn/Beam, SetORebar_1, SetMPUniaxial,
GetSectProps, GetSummaryResultsBeam/Column, VerifyPassed, SetComboAutoGenerate, GetDesignProcedure,
DesignConcrete.Eurocode_2_2004 and DatabaseTables.*. The v24.0 release note #7261 (item 1 = DC High/Medium/Low/Secondary;
items 7-12 return 1) was re-downloaded and matches. The .$2k titles and fields were re-read in real v21, v25.0,
v25.2, v25.3.1, v26.2 and v26.3 exports. The SAP rectangle J/As formulas equal the exported values of 6 rectangles.
Corrections made by the checker:
- φef: CYPE's Kφ = 1.373 corresponds to φef = 1.750, not 1.8.
- A dedicated OAPI rebar-size object exists: `PropRebar.SetProp`.
- "General sections are not designed" is downgraded to INFERRED.
- The TTArea per-leg reasoning is corrected.
- The lu with end offsets explanation is corrected.
- The overwrite-table cross-reference is corrected: it is C.10, not C.9.
- Added a warning about the v24.2+ crack-width design, which can raise the reported beam As.
- Added a warning that the online OAPI help is not updated for v24+.
- Added a robust combo deselection step.
- Added a "read the installed XML/CHM first" step (§6 step 0).

---------------------------------------------------------------------------------------------------------

## 0. Decisions in one page

| Item | Value / action | Tag |
|---|---|---|
| Design code string | `"Eurocode 2-2004"` (not "EN 1992-1-1:2023", which v27.0 added as a separate code) | VERIFIED [S5][S27] |
| National annex | **No Spain option.** Use `Country = CEN Default` and set γc=1.5, γs=1.15, αcc=1.0, αct=1.0, θ0=0.005 explicitly (= CYPE values: fcd 33.33/23.33 MPa, fyd 434.78 MPa, θ0 = 1/200) | VERIFIED [S1][S16 App. F][G7] |
| Second-order method | Nominal curvature (EC2 5.8.8) – same method CYPE used (A19.5.8.8) | VERIFIED [S1][S16 §3.4.2.2] |
| Utilization factor limit | 1.0 (default 0.95) | VERIFIED [S1][S16 App. C] |
| Framing type (EC8 ductility) | Overwrite **DC Low** on every designed frame (program default = DC High!) | VERIFIED [S23 #7261][S16 §4.4] |
| Pile effective length | Unbraced-length ratio 6.70/7.25 = **0.924138** (major & minor) and β = **1.0** → l0 = 6.70 m (CYPE: l0 = 6.700 m, "coeficiente de pandeo" 1.00) | overwrite items VERIFIED [S3]; the ratio multiplies "the frame object length" [S16 App. D] and the CSI reference defines the element length L as joint-to-joint (clear length Lc = L − ioff − joff) [S17 p.129] → 0.924138 × 7.25 = 6.70 INFERRED; confirm l0 = 6.70 in the design details (§6 step 3) |
| Creep factor Kφ | SAP default 1.0; CYPE used Kφ = 1.373 (= 1 + β·φef = 1 + 0.213·1.750; CYPE prints φef = 1.750 in the Kφ block and φef = 1.8 only in the λlim coefficient A). Settable only by table/DB editing (field `KPhi`), not by the documented OAPI items | VERIFIED-3P [G7]; default 1.0 VERIFIED [S16 App. D] |
| Strut angle | CYPE uses θ = 45° → overwrite `TanTheta = 1` (SAP default optimises θ for beams) | VERIFIED-3P [G7], behaviour VERIFIED [S23 #7380] |
| Pile section | Keep `PILOTE_40x40` Rectangular; `SetRebarColumn`: 4 bars per face (=12Ø25), bar `"25d"`, ties `"10d"` @ 0.15, clear cover 0.05, **ToBeDesigned = False (check)** | VERIFIED [S12][S29] |
| Beam sections | Replace the `General` sections by **Rectangular** sections (50x55 inner, 80x55 end) carrying **property modifiers** that reproduce the composite A, As2, As3, J, I22, I33, mass, weight (§B.3). Analysis unchanged; design sees a rectangle | modifiers ignored by design: VERIFIED [S18] |
| Beam rebar data | `SetRebarBeam` covers to bar centroid = 0.05 + 0.010 + 0.010 = **0.07 m** top and bottom, areas 0 (design) | VERIFIED [S12] |
| Rebar sizes | `"25d"`, `"20d"`, `"10d"` exist by default in a new model ("European (metric) bar sizes 6d…28d"); `"N25"` does **not** exist. OAPI can check/add them with `PropRebar.GetProp` / `PropRebar.SetProp(Name, Area, Diameter)` (A.5) | defaults VERIFIED [S30][G2][G3]; `PropRebar` VERIFIED-3P (A.5) |
| Frames not designed | rigid beam segments inside the piles (`rigid=True`, ×100 modifiers) and edge beams 25x30 → design procedure **No Design** | VERIFIED [S15][G9] |
| Design combinations | `ELU01…ELU22` = Strength; auto-generated code combos **off**; envelopes `ENV_*`, `CIM*`, `ELS*` not selected (CYPE checks piles and beams with the "Hormigón" family, e.g. "1.35·PP+1.35·CM+1.05·Qa+1.5·Tirobolardo") | VERIFIED [S10][G4][G5]; CYPE: Anejo dump lines 409, 543, 1684 |
| P-Δ analysis | Do **not** add P-Δ (CYPE: first order + nominal curvature). SAP assumes P-Δ was run for sway (b = 1) — same as CYPE's approach here | VERIFIED [S16 §2.6, App. A] |

---------------------------------------------------------------------------------------------------------

## 1. Sources

Official CSI (OAPI help = the online copy of `CSI_OAPI_Documentation.chm`, "common API (from SAP and CSiBridge)"):
Abbreviation: `…` = `https://docs.csiamerica.com/help-files/common-api(from-sap-and-csibridge)/SAP2000_API_Fuctions`.


* [S1] SetPreference {Concrete Eurocode 2-2004}: https://docs.csiamerica.com/help-files/common-api(from-sap-and-csibridge)/SAP2000_API_Fuctions/Design/Concrete/Eurocode_2-2004/SetPreference_%7BConcrete_Eurocode_2-2004%7D.htm
* [S2] GetPreference: https://docs.csiamerica.com/help-files/common-api(from-sap-and-csibridge)/SAP2000_API_Fuctions/Design/Concrete/Eurocode_2-2004/GetPreference%7BConcrete_Eurocode_2-2004%7D.htm
* [S3] SetOverwrite: https://docs.csiamerica.com/help-files/common-api(from-sap-and-csibridge)/SAP2000_API_Fuctions/Design/Concrete/Eurocode_2-2004/SetOverwrite%7BConcrete_Eurocode_2-2004%7D.htm
* [S4] GetOverwrite: https://docs.csiamerica.com/help-files/common-api(from-sap-and-csibridge)/SAP2000_API_Fuctions/Design/Concrete/Eurocode_2-2004/GetOverwrite_%7BConcrete_Eurocode_2-2004%7D.htm
* [S5] SetCode / GetCode: …/Design/Concrete/SetCode_%7BConcrete%7D.htm , …/Design/Concrete/GetCode_%7BConcrete%7D.htm
* [S6] StartDesign: …/Design/Concrete/StartDesign_%7BConcrete%7D.htm
* [S7] GetSummaryResultsBeam: …/Design/Concrete/GetSummaryResultsBeam.htm
* [S8] GetSummaryResultsColumn: …/Design/Concrete/GetSummaryResultsColumn.htm
* [S9] GetResultsAvailable: …/Design/Concrete/GetResultsAvailable_%7BConcrete%7D.htm
* [S10] SetComboStrength / GetComboStrength / SetComboAutoGenerate: …/Design/Concrete/SetComboStrength_%7BConcrete%7D.htm , …/Design/Concrete/GetComboStrength_%7BConcrete%7D.htm , …/Design/Concrete/SetComboAutoGenerate_%7BConcrete%7D.htm
* [S11] SetDesignSection / VerifyPassed / DeleteResults: …/Design/Concrete/SetDesignSection_%7BConcrete%7D.htm , …/Design/Concrete/VerifyPassed_%7BConcrete%7D.htm , …/Design/Concrete/DeleteResults_%7BConcrete%7D.htm
* [S12] PropFrame.SetRebarColumn / GetRebarColumn / SetRebarBeam: …/Definitions/Properties/Frame/SetRebarColumn.htm , …/Definitions/Properties/Frame/GetRebarColumn.htm , …/Definitions/Properties/Frame/SetRebarBeam.htm
* [S13] PropFrame.SetRectangle / SetTee / SetModifiers / GetSectProps: …/Definitions/Properties/Frame/SetRectangle.htm , …/Definitions/Properties/Frame/SetTee_%7BFrame%7D.htm , …/Definitions/Properties/Frame/SetModifiers_%7BFrame%7D.htm , …/Definitions/Properties/Frame/GetSectProps.htm
* [S14] PropMaterial.SetMaterial / SetMPUniaxial / SetWeightAndMass / SetORebar_1 / AddMaterial: …/Definitions/Properties/Material/SetMaterial.htm , …/Definitions/Properties/Material/SetMPUniaxial.htm , …/Definitions/Properties/Material/SetWeightAndMass_%7BMaterial%7D.htm , …/Definitions/Properties/Material/SetORebar_1.htm , …/Definitions/Properties/Material/AddMaterial.htm
* [S15] FrameObj.SetDesignProcedure / GetDesignProcedure: …/Object_Model/Frame_Object/SetDesignProcedure.htm , …/Object_Model/Frame_Object/GetDesignProcedure.htm


Manuals, help, release notes:

* [S16] *Concrete Frame Design Manual, Eurocode 2-2004 with 8-2004, for SAP2000* (Feb 2017): https://docs.csiamerica.com/manuals/sap2000/Design/CFD-EC-2-2004.pdf
* [S17] *CSI Analysis Reference Manual* (end offsets pp. 127-130, property modifiers pp. 123-124): https://docs.csiamerica.com/manuals/sap2000/CSiRefer.pdf
* [S18] SAP2000 v26 help, Frame – Property Modifiers ("the modification factors affect only the analysis properties. They do not affect the design properties"): https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/Assign/Frame/Frame_Property_Modifiers.htm
* [S19] SAP2000 v26 help, Reinforcement Data form: https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/Define/Section_Properties/Frame_Sections/Reinforcement_Data_Form.htm
* [S20] SAP2000 help, Add SD Section (Section Designer design types): https://docs.csiamerica.com/help-files/sap/Menus/Define/Section_Properties/Frame_Sections/Section_Designer_Section.htm
* [S21] SAP2000 help, Concrete Frame Design procedure / Select Design Combos / Change Design Section / Start Design: https://docs.csiamerica.com/help-files/sap/Getting_Started/Concrete_Frame_Design_Procedure.htm , https://docs.csiamerica.com/help-files/sap/Menus/Design/Concrete_Frame_Design/CF_Select_Design_Combos.htm , …/CF_Change_Design_Section.htm , …/CF_Start_Design-Check_of_Structure.htm
* [S22] ETABS help, Frame Section Property Data form ("Modify/Show Rebar button … appears on the forms for Rectangular, Encased Rectangle, Encased Circle, Tee, and Angle shapes when the Material is concrete"): https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Properties/Frame_Sections/Frame_Section_Property_Data_Form.htm
* [S23] SAP2000 v24.0.0 release notes (#7261 API EC2 overwrites, #7379 ConsiderTorsion/TanTheta/IgnoreBeneficialPu in prefs & overwrites, #7380 optimised θ, #7061 EC2 eq. 6.18): https://www.csiamerica.com/software/SAP2000/24/ReleaseNotesSAP2000v2400.pdf
* [S24] v24.2.0 release notes (#9150 EC2 crack-width design/check for frames): https://www.csiamerica.com/software/SAP2000/24/ReleaseNotesSAP2000v2420.pdf
* [S25] v25.0.0 (#9729 `DatabaseTables.GetAvailableTables` now lists frame-design result tables) and v25.2.0 (#10009 table "Concrete Design 1 - Column Summary Data" shows PMM ratio also when overstressed): https://www.csiamerica.com/software/SAP2000/25/ReleaseNotesSAP2000v2500.pdf , https://www.csiamerica.com/software/SAP2000/25/ReleaseNotesSAP2000v2520.pdf
* [S26] v26.3.0 (#11271 "Consider Torsion Design?" overwrite was ignored before, EC2 included): https://www.csiamerica.com/software/SAP2000/26/ReleaseNotesSAP2000v2630.pdf
* [S27] v27.0.0 (#10688 EN 1992-1-1:2023 added; #11618 EC2 torsion re-implemented; #11669 min. shear rebar now enforced when VEd > VRd,c; #11901 design section overwrote analysis section when set by API; #11904 `RunAnalysis` right after `ApplicationStart` fails → wait): https://www.csiamerica.com/software/SAP2000/27/ReleaseNotesSAP2000v2700.pdf
* [S28] CSI Knowledge Base, Design FAQ (table path pattern "Display > Show Tables > Design Data > …"; design type + design procedure needed): https://wiki.csiamerica.com/display/kb/Design+FAQ
* [S29] SAP2000 v26 help, Reinforcement Bar Sizes (default bar lists): https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/Define/Section_Properties/Reinforcement_Bar_Sizes.htm
  ([S30] = same page; kept as a separate tag in §0.)

Real exported files / third-party code (GitHub):

* [G1] SAP2000 **v25.3.1** export listing every table title (incl. `PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004`, `OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004`, `FRAME SECTION PROPERTIES 02/03`, `FRAME DESIGN PROCEDURES`, `AUTO COMBINATION OPTION DATA 01 - GENERAL`, `REBAR SIZES`): https://github.com/wensley-rushing/OpenBIM/blob/HEAD/models/WaterTower.s2k
* [G2] SAP2000 **v26.2.0** export (N, mm): `REBAR SIZES` incl. `10d/20d/25d`; `PROGRAM CONTROL … ConcCode=… ConcSCode="Eurocode 2-2004"`: https://github.com/krmsari/sap2000-tbdy2018/blob/HEAD/SapApi/Init.$2k
* [G3] SAP2000 **v25.1.0** export (kN, m): `REBAR SIZES` values in m: https://github.com/btayfur/structural-optimization/blob/HEAD/Code/Examples/Exmp7/model_v25.$2k
* [G4] SAP2000 **v21.0.0** CSI verification model (column **check**, `ReinfType=Check`, `ConcDesign=Strength`, `AutoGen=Yes`): https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize.SAP2000/RCDF%202017%20CFD%20Ex002.$2k
* [G5] SAP2000 **v21.0.0** CSI verification model (concrete **Tee** beam with `FRAME SECTION PROPERTIES 03`, `ConcDesign=Strength`, `AutoGen=No`, `MATERIAL PROPERTIES 03E`): https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize.SAP2000/RCDF%202017%20CFD%20Ex003.$2k
* [G6] SAP2000 **v20.1.0** export with EC2-family preferences (`PREFERENCES - CONCRETE DESIGN - ITALIAN NTC 2008`) and overwrites: https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize.SAP2000/model/test.$2k
* [G7] MPT.Net SAP2000 `.$2k` serializer by M. P. Thomas (ex-CSI verification engineer): EC2 preference reader/writer (field names incl. `Country`), EC2 overwrite reader (real v20 rows quoted in comments), enum strings: https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize/SAP2000/Readers/ReadDesignConcretePreferences.cs , …/Writers/WriteDesignConcretePreferences.cs , …/Readers/ReadDesignConcreteOverwrites.cs , https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize/Models/Helpers/Design/Preferences/Concrete/EN_2_2004_Preferences.cs , …/Models/Helpers/Design/Overwrites/Concrete/EN_2_2004_Overwrites.cs , …/Models/Helpers/Design/Preferences/eMultiResponseCase.cs , table titles …/SAP2000/SAP2000Tables.cs
* [G8] SAP2000 **v20.1.0** XML export with `Concrete Design 2 - Beam Summary Data - Mexican RCDF 2004` rows (field list): https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.Serialize.SAP2000/model/RCDF%202004%20CFD%20Ex003.xml
* [G9] SAP2000 **v25.3.1** export with `DesignProc="No Design"` and circular columns: https://github.com/wensley-rushing/OpenBIM/blob/HEAD/models/csi/painter/Painter_Street_v1.2.s2k
* [G10] SAP2000 **v25.2.0** / **v25.0.0** / **v24.2.0** / **v16.1.1** exports with `FRAME SECTION PROPERTIES 02 - CONCRETE COLUMN` rows: https://github.com/wensley-rushing/OpenBIM/blob/HEAD/models/Analysis/Example%201-006a.s2k , https://github.com/joreilly86/Engineering-Fundamentals/blob/HEAD/Structural/SAP2000/API_1-001.$2k , https://github.com/kanzie88/CSI-SAP2000-Python-OAPI-Tunnel-design/blob/HEAD/Section%20Test/SAP2000%20Model/Test.$2k , https://github.com/umairnaeem2703/CE4011-Assignment-4-Submission/blob/HEAD/SAP2000/q2_a/q2_a.$2k
* [G11] ETABS (not SAP) EC2 design-table fixture (field concepts only: Kr, KPhi, Torsion, IgnorePu, TLng/TTrn fields): https://github.com/Tuyen-lt/Python4ETABS/blob/HEAD/tests/fixtures/design_codes/eurocode_2_2004/frame/manifest.json
* [G12] Skills_SAP: DatabaseTables signatures/ByRef layouts verified by the author against a live SAP2000 through comtypes: https://github.com/fcocarrascob/Skills_SAP/blob/HEAD/scripts/registry.json , https://github.com/fcocarrascob/Skills_SAP/blob/HEAD/scripts/wrappers/func_DatabaseTables_GetTableForDisplayArray.py , …/func_DatabaseTables_GetAllFieldsInTable.py
* [G13] comtypes index layout of `GetSummaryResultsBeam/Column` return lists: https://github.com/ebrahimraeyat/etabs_api2/blob/HEAD/src/etabs_api/design.py
* [G14] (added by the checker) `SapModel.PropRebar`: member list of the SAP2000v1 type library in
  https://github.com/GLY2024/Sap2000py/blob/HEAD/src/sap2000py/native.pyi (class `_PropRebarProxy`; the same file lists
  `DesignConcrete` members incl. `SetComboAutoGenerate`, `GetSummaryResultsBeam/Column`, and **no** service/crack
  combo function); `SetProp(name, area, diameter)` calls in https://github.com/rpakishore/ak_sap/blob/HEAD/src/ak_sap/Material/Materials/rebar.py ,
  https://github.com/fcocarrascob/Skills_SAP/blob/HEAD/scripts/modelo_base/backend_modelo_base.py ,
  https://github.com/fcocarrascob/SAPy2000/blob/HEAD/Modelo_Base/modelo_base_backend.py
* [G15] (added by the checker) second, independent SAP2000 code base for the DatabaseTables ByRef layouts
  (`GetAllTables` → `raw[1:-1]` = TableKey, TableName, ImportType, IsEmpty; `GetAllFieldsInTable` → `raw[2:-1]`;
  `GetTableForDisplayArray` → `raw[2]`, `raw[4]`; `ApplyEditedTables(True)` → 4 counts, ImportLog, ret):
  https://github.com/rpakishore/ak_sap/blob/HEAD/src/ak_sap/Database/tables.py
* [G16] (added by the checker) SAP2000 **v26.3.0** exports with `FRAME SECTION PROPERTIES 03 - CONCRETE BEAM`
  (`TopRghtArea` spelling), `FRAME DESIGN PROCEDURES`, `AUTO COMBINATION OPTION DATA 01 - GENERAL` and 03E rebar rows:
  https://github.com/IvanRivera007/gitdocs-2026/blob/HEAD/MAESTRIA%202DO%20TRIMESTRE/JULIAN%20DINAMICA%20ESTRUCTURAL/TAREA%204/prueba2.$2k ,
  https://github.com/berckanala/Proyecto_civil/blob/HEAD/Entrega_4/excel_codigos/vigas_est%C3%A1ticas.$2k
* Other independent confirmations used by the checker: SAP `GetSummaryResultsBeam` VB call with the same 16 arguments
  (https://github.com/Nemo-Tuan-CTCI/SAP2000Addins/blob/HEAD/SAP2000DLL/cPlugin.vb), SAP v14 wrapper with the same
  argument lists and `GetDesignProcedure` codes 1/2/7/8/9 (https://github.com/vitorscoelho/sw4k , `DesignConcrete.kt`,
  `FrameObj.kt`), `SetRebarColumn`/`SetRebarBeam`/`SetORebar_1` argument order in real SAP scripts
  (https://github.com/sanlocoz/structural-modeling/blob/HEAD/first_program.py), `DesignConcrete.Eurocode_2_2004`
  property path (https://github.com/MarkPThomas/MPT.Net/blob/HEAD/MPT/CSI/API/MPT.CSI.API/Core/Program/ModelBehavior/Design/CodesDesign/Concrete/Eurocode_2_2004.cs).
* [U1] The user's own SAP2000 **v27.1.0** exports: `sap2000/resultados_sap/SAP27_*.xlsx` (Excel layout; `PROGRAM CONTROL` shows `ProgLevel=Advanced`, `ConcCode=ACI 318-19` default, `ConcSCode=Eurocode 2-2004`).
* [C1] Anejo 10 dump `a10_full.txt`: pile check l0 = 6.700 m, c = 9.870, Kr = 1.000, K(φ) = 1.373 (φef = 1.750, β = 0.213; the φef = 1.8 printed at line 628 belongs to λlim), d = 328 mm, θ0 = 1/200, αh = 0.7727 (l = 6.700), ei = 12.94 mm, e2 = 92.12 mm (lines 596-700); θ = 45° in shear checks (lines 434, 458, 1709); "coeficiente de pandeo" X = Y = 1.00 (line 5833).

---------------------------------------------------------------------------------------------------------

## 2. Part A — OAPI (Python + comtypes)

### A.0 Conventions (as already used in `sap_oapi_run.py`)

* Every function returns 0 on success. With comtypes, a call that has ByRef arguments returns a list:
  `[ByRef_1, ByRef_2, …, ByRef_n, return_code]` (ByVal arguments are not echoed). Pass placeholders
  (`0`, `""`, `[]`, `False`) for ByRef outputs. Confirmed pattern for design results in [G13]
  (`ret[1]` = FrameName … `ret[-1]` = code) and for DatabaseTables in [G12].
* Units: results come in the *present* units → call `SetPresentUnits(6)` (kN_m_C) before reading; areas in m²,
  Av/s in m²/m, locations in m. [S7][S8]
* `eItemType`: Object = 0, Group = 1, SelectedObjects = 2 [S3][S7][S8][S11]. Groups `PILOTES` and
  `VIGAS_TRANSVERSALES` already exist in the model.
* v27.0 note: `RunAnalysis` called immediately after `ApplicationStart` can fail until the licence is
  acquired → the model-building time is enough, but when attaching and running at once add `time.sleep(5)`. [S27 #11904]

### A.1 Code

```text
Function SetCode(ByVal CodeName As String) As Long          [S5]
Function GetCode(ByRef CodeName As String) As Long          [S5]
```
Valid string (list in [S5]): **`"Eurocode 2-2004"`**. v27.0 additionally offers EN 1992-1-1:2023 [S27]; its code
string is UNVERIFIED and not wanted here (Código Estructural Anejo 19 = EN 1992-1-1:2004 + NA).
Always read it back: `m.DesignConcrete.GetCode("")` → `["Eurocode 2-2004", 0]`.
(`.$2k`: `PROGRAM CONTROL … ConcCode="Eurocode 2-2004"`, §C.1.)

### A.2 Preferences — `DesignConcrete.Eurocode_2_2004.SetPreference / GetPreference`

```text
Function SetPreference(ByVal Item As Long, ByVal Value As Double) As Long   [S1]
Function GetPreference(ByVal Item As Long, ByRef Value As Double) As Long   [S2]
```
(The doc says "integer between 1 and 16" but documents 17 items; item 17 was added in v14.2.2 [S1].)

| Item | Meaning [S1] | Allowed values [S1] | Default [S16 App. C / F] | **Set to** |
|---|---|---|---|---|
| 1 | Country | 1 CEN Default, 2 United Kingdom, 3 Slovenia, 5 Norway, 6 Singapore, 7 Sweden, 8 Finland, 9 Denmark, 10 Portugal, 11 Germany | CEN Default | **1** |
| 2 | Combos equation | 1 Eq. 6.10, 2 Max of 6.10a/6.10b | Eq. 6.10 | 1 (only affects auto combos, which are off) |
| 3 | Second order method | 1 Nominal stiffness, 2 Nominal curvature, 3 None | Nominal curvature | **2** |
| 4 | Number of interaction curves | ≥ 4, multiple of 4 | 24 | 24 (36/48 if a ratio ≈ 1 needs refinement) |
| 5 | Number of interaction points | ≥ 5, odd | 11 | 11 (21 for refinement) |
| 6 | Consider minimum eccentricity | 0 No, other Yes | Yes | **1** |
| 7 | Theta0 | > 0 | 0.005 | **0.005** |
| 8 | Gamma steel | > 0 | 1.15 | **1.15** |
| 9 | Gamma concrete | > 0 | 1.5 | **1.5** |
| 10 | AlphaCC | > 0 | 1.0 (CEN) | **1.0** (Spain/CYPE: fcd = fck/1.5) |
| 11 | AlphaCT | > 0 | 1.0 (CEN) | **1.0** |
| 12 | AlphaLCC | > 0 | 0.85 | 0.85 (lightweight, unused) |
| 13 | AlphaLCT | > 0 | 0.85 | 0.85 (unused) |
| 14 | Pattern live load factor | ≥ 0 | 0.75 | 0.75 (auto combos only) |
| 15 | Utilization factor limit | > 0 | 0.95 | **1.0** |
| 16 | Multi-response case design | 1 Envelopes, 2 Step-by-step, 3 Last step, 4 Envelopes–All, 5 Step-by-step–All | Envelopes | 1 |
| 17 | Reliability class | 1, 2, 3 | Class 2 | 2 |

**Spain?** No. The OAPI list [S1] has no Spain; the `.$2k` country strings used by the SAP serializer [G7] are
`CEN Default, Denmark, Finland, Germany, Ireland, Norway, Poland, Portugal, Singapore, Slovenia, Sweden,
United Kingdom` (Ireland/Poland exist in the table enum but their OAPI numbers — probably 4 and 12 — are
UNVERIFIED). CEN Default with the explicit values above reproduces every NDP that CYPE printed in the Anejo
(fcd, fyd, θ0). Other NDPs (CRd,c = 0.18/γc, vmin, k1 = 0.15, 1 ≤ cotθ ≤ 2.5, As,min formulas, ν) are the CEN
recommended ones [S16 Table F-1]; whether each equals the Spanish Anejo 19 value was not checked item by item.

Not exposed by the documented OAPI items (INFERRED to exist in v24+ because of [S23 #7379] and [G11]):
"Framing Type" and "Ignore Seismic Code?" preferences [S16 §4.2], Consider Torsion, TanTheta,
Ignore Beneficial Pu, crack-width preferences. Handle them per object with overwrites (A.3) or with
DatabaseTables (A.10).

```python
EC2_PREFS = {1: 1, 2: 1, 3: 2, 4: 24, 5: 11, 6: 1, 7: 0.005, 8: 1.15, 9: 1.5,
             10: 1.0, 11: 1.0, 12: 0.85, 13: 0.85, 14: 0.75, 15: 1.0, 16: 1, 17: 2}

def set_ec2_preferences(m):
    check(m.DesignConcrete.SetCode("Eurocode 2-2004"), "DesignConcrete.SetCode")
    code = check(m.DesignConcrete.GetCode(""), "GetCode")[0]
    assert code == "Eurocode 2-2004", code
    ec2 = m.DesignConcrete.Eurocode_2_2004
    for item, val in EC2_PREFS.items():
        check(ec2.SetPreference(item, float(val)), f"EC2 SetPreference {item}")
    for item, val in EC2_PREFS.items():          # read back: a silent reset shows up here
        got = check(ec2.GetPreference(item, 0.0), f"EC2 GetPreference {item}")[0]
        if abs(got - val) > 1e-9:
            raise RuntimeError(f"EC2 preference {item}: set {val}, SAP has {got}")
```

### A.3 Overwrites — `DesignConcrete.Eurocode_2_2004.SetOverwrite / GetOverwrite`

```text
Function SetOverwrite(ByVal Name As String, ByVal Item As Long, ByVal Value As Double,
                      Optional ByVal ItemType As eItemType = Object) As Long                 [S3]
Function GetOverwrite(ByVal Name As String, ByVal Item As Long, ByRef Value As Double,
                      ByRef ProgDet As Boolean) As Long                                      [S4]
```

| Item | Meaning [S3] | Values | Status in v24+ |
|---|---|---|---|
| 1 | Framing type | 0 = program default; doc [S3] says 1 Sway / 2 Nonsway, **but since v24.0 the values are 1 DC High, 2 DC Medium, 3 DC Low, 4 Secondary** [S23 #7261] | use **3 (DC Low)** |
| 2 | Live load reduction factor | ≥ 0, 0 = program | leave 0 |
| 3 | Unbraced length ratio, Major | ≥ 0, 0 = program; ratio × object length = lu [S16 App. B] | piles **0.924138** |
| 4 | Unbraced length ratio, Minor | idem | piles **0.924138** |
| 5 | Effective length factor β Major | ≥ 0, 0 = program (β "conservatively taken as 1" [S16 §3.4.2.2]) | piles **1.0**; returns 1 (error) if the section is not a column-design section [S23 #7261] |
| 6 | Effective length factor β Minor | idem | piles **1.0** |
| 7-12 | Cm, Dns, Ds (major/minor) | — | **not used by EC2; since v24.0 these calls return 1** [S23 #7261] |

Why DC Low: the program default framing type for EC2 is "DCH MRF" [S16 §4.4]; "Program Determined" means
"the highest ductility requirement" [G7 EN_2_2004_Overwrites.cs]. DCL = design to EC2 only (EC8 5.3).

Not reachable with the documented items but present in the EC2 overwrite table: `TanTheta`, `Kr`, `KPhi`
(v20 rows in [G7]); plus, INFERRED for v24+, Consider Torsion and crack-width limit [S23 #7379][S27 #11710].
Use A.10 (DatabaseTables) or the `.$2k` table C.10 for them.
Caveat (checker): the online OAPI help used here ([S1]-[S4]) still shows the v14-era item lists (item 1 "Sway/Nonsway",
items 1-12), i.e. it was not updated for v24.0 #7261. v24.2 #9252 speaks of removing "Consider Torsion" from "the API
functions" of IS 456, so for some codes the v24+ Set/GetOverwrite/Preference item lists are longer than the online
help. The `CSI_OAPI_Documentation.chm` installed with SAP2000 v27.1 may therefore list extra EC2 items
(Consider Torsion, TanTheta, …) — check it before falling back to DatabaseTables (§6).

```python
L_PILE, L_CLEAR = 7.25, 6.70

def designed_frames(model):
    """Frames that get concrete design (A.7): piles and the non-rigid transverse-beam segments."""
    return [f for f in model["frames"]
            if f["kind"] == "pile" or (f["kind"] == "beam_t" and not f.get("rigid", False))]

def set_ec2_overwrites(m, model):
    ec2 = m.DesignConcrete.Eurocode_2_2004
    r = L_CLEAR / L_PILE                                                     # 0.924138 -> l0 = 6.70 m
    for f in designed_frames(model):                                         # ItemType 0 = object
        check(ec2.SetOverwrite(f["name"], 1, 3.0, 0), f"FrameType=DC Low {f['name']}")
        if f["kind"] == "pile":
            for item, val in ((3, r), (4, r), (5, 1.0), (6, 1.0)):
                check(ec2.SetOverwrite(f["name"], item, val, 0), f"overwrite {item} {f['name']}")
    v, progdet = check(ec2.GetOverwrite("PIL_P1", 1, 0.0, False), "GetOverwrite")[:2]
    assert int(round(v)) == 3 and not progdet
```
Per-object calls are used on purpose: the groups `PILOTES`/`VIGAS_TRANSVERSALES` also contain frames with
"No Design" (rigid segments), for which a group call may return non-zero (UNVERIFIED).
Order: call after the pile section has column rebar data (`SetRebarColumn`) and after `SetDesignProcedure`,
otherwise items 5/6 fail [S23].

### A.4 Rebar material B500SD

```text
Function SetMaterial(ByVal Name As String, ByVal MatType As eMatType, Optional ByVal Color As Long = -1,
                     Optional ByVal Notes As String = "", Optional ByVal GUID As String = "") As Long    [S14]
    eMatType: MATERIAL_STEEL=1, CONCRETE=2, NODESIGN=3, ALUMINUM=4, COLDFORMED=5, REBAR=6, TENDON=7
Function SetMPUniaxial(ByVal Name As String, ByVal e As Double, ByVal a As Double,
                       Optional ByVal Temp As Double = 0) As Long                                    [S14]
Function SetWeightAndMass(ByVal Name As String, ByVal MyOption As Long, ByVal Value As Double,
                          Optional ByVal Temp As Double = 0) As Long   MyOption 1 = weight/volume   [S14]
Function SetORebar_1(ByVal Name As String, ByVal Fy As Double, ByVal Fu As Double, ByVal eFy As Double,
                     ByVal eFu As Double, ByVal SSType As Long, ByVal SSHysType As Long,
                     ByVal StrainAtHardening As Double, ByVal StrainUltimate As Double,
                     ByVal FinalSlope As Double, ByVal UseCaltransSSDefaults As Boolean,
                     Optional ByVal Temp As Double = 0) As Long                                       [S14]
    SSType 0 user / 1 parametric-simple / 2 parametric-Park; SSHysType 0 elastic / 1 kinematic / 2 Takeda
```
```python
def define_rebar(m):
    check(m.PropMaterial.SetMaterial("B500SD", 6), "SetMaterial B500SD")
    check(m.PropMaterial.SetMPUniaxial("B500SD", 200e6, 1.17e-5), "SetMPUniaxial B500SD")
    check(m.PropMaterial.SetWeightAndMass("B500SD", 1, 76.97), "SetWeightAndMass B500SD")
    # Fy, Fu, eFy, eFu [kN/m2]; simple parametric curve, kinematic hysteresis (= .$2k 03E defaults)
    check(m.PropMaterial.SetORebar_1("B500SD", 500e3, 575e3, 550e3, 632.5e3, 1, 1, 0.01, 0.09, -0.1, False),
          "SetORebar_1 B500SD")
    ensure_bar_sizes(m)

BAR_SIZES = {"10d": (7.85e-5, 0.010), "20d": (3.14e-4, 0.020), "25d": (4.91e-4, 0.025)}   # SAP defaults, kN-m [G3]

def ensure_bar_sizes(m):
    """Add a bar size only if the model lacks it (A.5). GetProp is called without output placeholders, as in
    the SAP2000 libraries that use it [G14], because its output layout is not documented online; only its
    return code (last element, sap_oapi_run.rc) is used."""
    for name, (area, dia) in BAR_SIZES.items():
        if rc(m.PropRebar.GetProp(name)) != 0:
            check(m.PropRebar.SetProp(name, area, dia), f"PropRebar.SetProp {name}")
```
Alternative `PropMaterial.AddMaterial(Name, 6, Region, Standard, Grade, UserName)` [S14] needs the exact library
strings of `CSiMaterialLibrary*.xml` for a European B500 grade — UNVERIFIED, not needed.
Design uses fyk = Fy and Es = 200 GPa fixed by the code implementation [S16 §3.2]; Fu/eFy/eFu do not enter EC2
frame design.

### A.5 Rebar size names

Default bar list of every SAP2000 model [S29]: ASTM `#2…#18`, ASTM metric `10M…55M`, European
`6d, 8d, 10d, 12d, 14d, 16d, 20d, 25d, 26d, 28d`; real exports also contain `N12, N16, N20, N24, N28, N32, N36`
(v25.1 kN-m [G3], v26.2 N-mm [G2], v25.3.1 kip-in [G1]). Values in a kN-m model [G3]:
`10d` A = 7.85E-05 m² (Ø 0.010), `20d` A = 3.14E-04 (Ø 0.020), `25d` A = 4.91E-04 (Ø 0.025) → 12 × 25d = 58.92 cm²
(CYPE 58.91). **Use `"25d"` (piles) and `"10d"` (ties); `"N25"` does not exist.**
Adding a size: GUI *Define > Section Properties > Reinforcement Bar Sizes* [S29], the `.$2k` table
`REBAR SIZES` (`RebarID`, `Area`, `Diameter`) (C.4), or the OAPI object **`SapModel.PropRebar`**
(`ChangeName, Count, Delete, GetNameList, GetProp, GetRebarProps, SetProp` in the SAP2000v1 type library [G14]).
`PropRebar.SetProp(Name, Area, Diameter)` is used with exactly these 3 arguments by three independent SAP2000 code
bases [G14] — VERIFIED-3P (no page in the online CSI OAPI help). `GetProp` output order is **not** settled: the
3P code disagrees (`[0]=Area,[1]=Diameter` in ak_sap, `[2]` read as area in another file) → `ensure_bar_sizes`
(A.4) uses only its return code. Beam design does not use bar sizes (areas only) [S19].

### A.6 Frame sections and reinforcement data

```text
Function SetRectangle(ByVal Name, ByVal MatProp, ByVal t3 As Double, ByVal t2 As Double,
                      Optional Color=-1, Optional Notes="", Optional GUID="") As Long              [S13]
Function SetModifiers(ByVal Name As String, ByRef Value() As Double) As Long                     [S13]
    Value(0) A, (1) As2, (2) As3, (3) J, (4) I22, (5) I33, (6) mass, (7) weight
Function GetSectProps(ByVal Name, ByRef Area, ByRef As2, ByRef As3, ByRef Torsion, ByRef I22,
                      ByRef I33, ByRef S22, ByRef S33, ByRef Z22, ByRef Z33, ByRef R22, ByRef R33) As Long [S13]
Function SetRebarColumn(ByVal Name As String, ByVal MatPropLong As String, ByVal MatPropConfine As String,
                        ByVal Pattern As Long, ByVal ConfineType As Long, ByVal Cover As Double,
                        ByVal NumberCBars As Long, ByVal NumberR3Bars As Long, ByVal NumberR2Bars As Long,
                        ByVal RebarSize As String, ByVal TieSize As String, ByVal TieSpacingLongit As Double,
                        ByVal Number2DirTieBars As Long, ByVal Number3DirTieBars As Long,
                        ByVal ToBeDesigned As Boolean) As Long                                      [S12]
Function SetRebarBeam(ByVal Name As String, ByVal MatPropLong As String, ByVal MatPropConfine As String,
                      ByVal CoverTop As Double, ByVal CoverBot As Double, ByVal TopLeftArea As Double,
                      ByVal TopRightArea As Double, ByVal BotLeftArea As Double,
                      ByVal BotRightArea As Double) As Long                                         [S12]
```
Meaning [S12]:
* `Pattern` 1 rectangular / 2 circular; `ConfineType` 1 ties / 2 spiral (only for Pattern 2).
* `Cover` (column) = **clear cover to the ties** [S12][S19] → 0.05 m. Bar centre = 0.05 + 0.010 + 0.0125 = 0.0725 m.
* `NumberR3Bars` / `NumberR2Bars` = bars **per face incl. corners** on the faces parallel to local 3 / 2
  → 4 and 4 = 12 bars. `NumberCBars` only for circular.
* `ToBeDesigned` True = design, **False = check** (the pile case).
* `CoverTop/CoverBot` (beam) = distance from the face to the **centroid** of the longitudinal bars → 0.07 m.
* The four beam areas are only "reinforcement overrides for ductile beams" (capacity shear, minimum mid-span
  steel, default hinges) [S19] → 0 for our non-seismic design.
* `SetRebarColumn` applies only to SECTION_RECTANGULAR = 8 and SECTION_CIRCLE = 9; `SetRebarBeam` to
  SECTION_T = 3, SECTION_ANGLE = 4, SECTION_RECTANGULAR = 8, SECTION_CIRCLE = 9; the material must be concrete,
  otherwise an error is returned [S12].
* `SetRectangle`/`SetTee` on an existing name **reset all items of the section** [S13] → order:
  `SetRectangle` → `SetModifiers` → `SetRebar*`.

```python
def sap_rect_props(h, b):
    """Properties SAP2000 computes for a solid rectangle t3=h, t2=b (formula checked against the
    TorsConst/AS2 values of 7 real exported rectangles, e.g. 0.5x0.5 -> J = 8.80208E-03 [G10])."""
    A = b * h
    lo, hi = sorted((b, h))
    J = hi * lo**3 * (1/3 - 0.21 * (lo/hi) * (1 - lo**4 / (12 * hi**4)))
    return {"Area": A, "AS2": 5/6*A, "AS3": 5/6*A, "TorsConst": J, "I22": h*b**3/12, "I33": b*h**3/12}

def rect_modifiers(true, got):
    """8 modifiers (A, As2, As3, J, I22, I33, mass, weight) making a rectangle behave like `true`.
    Mass and weight are separate terms (weight = a*w*WMod) [S17 p.123] -> MMod = WMod = A ratio."""
    a = true["Area"] / got["Area"]
    return [a, true["AS2"]/got["AS2"], true["AS3"]/got["AS3"], true["TorsConst"]/got["TorsConst"],
            true["I22"]/got["I22"], true["I33"]/got["I33"], a, a]

DESIGN_RECT = {"VIGA_T50x55_ALAS15x30": (0.55, 0.50),      # web 50x55 of the inverted T
               "VIGA_L80x55_ALA15x30": (0.55, 0.80),       # web 80x55 of the inverted L
               "VIGA_L80x55_ALA15x30_M": (0.55, 0.80)}

def define_design_sections(m, model):
    define_rebar(m)
    # piles: 12 phi 25 (4 per face), ties phi 10 @ 150, clear cover 50 mm, CHECK
    check(m.PropFrame.SetRebarColumn("PILOTE_40x40", "B500SD", "B500SD", 1, 1, 0.05, 0, 4, 4,
                                     "25d", "10d", 0.15, 2, 2, False), "SetRebarColumn PILOTE_40x40")
    r = check(m.PropFrame.GetRebarColumn("PILOTE_40x40", "", "", 0, 0, 0.0, 0, 0, 0, "", "", 0.0, 0, 0, False),
              "GetRebarColumn")
    # r = [MatPropLong, MatPropConfine, Pattern, ConfineType, Cover, NumberCBars, NumberR3Bars, NumberR2Bars,
    #      RebarSize, TieSize, TieSpacingLongit, Number2DirTieBars, Number3DirTieBars, ToBeDesigned, ret]
    assert r[6] == 4 and r[7] == 4 and r[8] == "25d" and not r[13], r
    for name, (h, b) in DESIGN_RECT.items():
        true = model["sections"][name].section.props            # composite A, AS2, AS3, J, I22, I33
        check(m.PropFrame.SetRectangle(name, "HA-35", h, b), f"SetRectangle {name}")
        sp = check(m.PropFrame.GetSectProps(name, 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.), "GetSectProps")
        got = dict(zip(("Area", "AS2", "AS3", "TorsConst", "I22", "I33"), sp[:6]))   # SAP's own numbers
        check(m.PropFrame.SetModifiers(name, rect_modifiers(true, got)), f"SetModifiers {name}")
        # covers to bar centroid: 50 mm cover + phi10 stirrup + phi20/2; areas 0 -> design
        check(m.PropFrame.SetRebarBeam(name, "B500SD", "B500SD", 0.07, 0.07, 0., 0., 0., 0.),
              f"SetRebarBeam {name}")
```
Numbers for the record (SAP rectangle vs composite, from `model/sections.py`):

| Section | AMod=MMod=WMod | A2Mod | A3Mod | JMod | I2Mod | I3Mod |
|---|---|---|---|---|---|---|
| VIGA_T50x55_ALAS15x30 (rect 0.55x0.50) | 1.327273 | 1.313245 | 1.433600 | 1.467072 | 2.688727 | 1.250206 |
| VIGA_L80x55_ALA15x30 (rect 0.55x0.80) | 1.102273 | 1.105216 | 1.135065 | 1.107293 | 1.396113 | 1.087939 |
| VIGA_L80x55_ALA15x30_M | 1.102273 | 1.105216 | 1.134641 | 1.107293 | 1.396113 | 1.087939 |

The existing object modifiers (×100 on rigid segments) multiply these [S17 p.124] — still rigid.
`PILOTE_40x40` keeps its section modifiers (AMod = 2, WMod = 6.70/7.25): ignored by design [S18].

### A.7 Which frames are designed — `FrameObj.SetDesignProcedure`

```text
Function SetDesignProcedure(ByVal Name As String, ByVal MyType As Long,
                            Optional ByVal ItemType As eItemType = Object) As Long     [S15]
    MyType 1 = Default from material, 2 = No design
Function GetDesignProcedure(ByVal Name As String, ByRef MyType As Long) As Long        [S15]
    MyType returned: 1 Steel, 2 Concrete, 7 Aluminum, 8 Cold Formed, 9 No Design
```
A frame is concrete-designed when (a) its design procedure is "from material" and the material is Concrete,
(b) its section has a concrete design type: Rectangular/Circular with column or beam rebar data, Tee/Angle
with beam rebar data, or a Section-Designer section with design type "Concrete Column" [S12][S19][S20][S22][S28].
```python
def set_design_procedures(m, model):
    for f in model["frames"]:
        no_design = f["kind"] == "beam_edge" or f.get("rigid", False)
        check(m.FrameObj.SetDesignProcedure(f["name"], 2 if no_design else 1, 0), f"SetDesignProcedure {f['name']}")
    assert check(m.FrameObj.GetDesignProcedure("PIL_P1", 0), "GetDesignProcedure")[0] == 2   # concrete
```

### A.8 Design combinations

```text
Function SetComboAutoGenerate(ByVal AutoGenerate As Boolean) As Long      [S10]  (v18.1+)
Function SetComboStrength(ByVal Name As String, ByVal Selected As Boolean) As Long   [S10]
Function GetComboStrength(ByRef NumberItems As Long, ByRef MyName() As String) As Long [S10]
```
Auto-generated combos (DCON…) are regenerated after each design run while the option is on [S21]; the
program also uses its default combos "if no other user-defined combinations are available" [S16 §2.1].
```python
def select_design_combos(m):
    check(m.DesignConcrete.SetComboAutoGenerate(False), "SetComboAutoGenerate")
    for fam, combos in tm.COMBOS.items():
        for k in range(1, len(combos) + 1):
            check(m.DesignConcrete.SetComboStrength(f"{fam}{k:02d}", fam == "ELU"), f"SetComboStrength {fam}{k:02d}")
        check(m.DesignConcrete.SetComboStrength(f"ENV_{fam}", False), f"SetComboStrength ENV_{fam}")
    wanted = [f"ELU{k:02d}" for k in range(1, len(tm.COMBOS["ELU"]) + 1)]
    n, names = check(m.DesignConcrete.GetComboStrength(0, []), "GetComboStrength")[:2]
    for extra in set(names or []) - set(wanted):     # e.g. default "DCon*" combos created before auto-gen was off
        check(m.DesignConcrete.SetComboStrength(extra, False), f"deselect {extra}")
    n, names = check(m.DesignConcrete.GetComboStrength(0, []), "GetComboStrength")[:2]
    assert sorted(names or []) == wanted, names
```
Envelope combos must not be design combos: SAP builds max/min permutations and loses correspondence [S16 §2.1].

### A.9 Run design and read results

```text
Function StartDesign() As Long            [S6]  fails if no concrete frame objects or no analysis results
Function GetResultsAvailable() As Boolean [S9]  (v18.2+)
Function VerifyPassed(ByRef NumberItems As Long, ByRef n1 As Long, ByRef n2 As Long,
                      ByRef MyName() As String) As Long       [S11]  n1 = failed, n2 = not checked
Function DeleteResults() As Long                               [S11]
Function SetDesignSection(ByVal Name, ByVal PropName, ByVal LastAnalysis As Boolean,
                          Optional ByVal ItemType = Object) As Long   [S11]  (not needed; see B.3)

Function GetSummaryResultsColumn(ByVal Name As String, ByRef NumberItems As Long, ByRef FrameName() As String,
    ByRef MyOption() As Long, ByRef Location() As Double, ByRef PMMCombo() As String, ByRef PMMArea() As Double,
    ByRef PMMRatio() As Double, ByRef VmajorCombo() As String, ByRef AVmajor() As Double,
    ByRef VminorCombo() As String, ByRef AVminor() As Double, ByRef ErrorSummary() As String,
    ByRef WarningSummary() As String, Optional ByVal ItemType As eItemType = Object) As Long       [S8]
Function GetSummaryResultsBeam(ByVal Name As String, ByRef NumberItems As Long, ByRef FrameName() As String,
    ByRef Location() As Double, ByRef TopCombo() As String, ByRef TopArea() As Double, ByRef BotCombo() As String,
    ByRef BotArea() As Double, ByRef VmajorCombo() As String, ByRef VmajorArea() As Double,
    ByRef TLCombo() As String, ByRef TLArea() As Double, ByRef TTCombo() As String, ByRef TTArea() As Double,
    ByRef ErrorSummary() As String, ByRef WarningSummary() As String,
    Optional ByVal ItemType As eItemType = Object) As Long                                          [S7]
```
Output meaning [S7][S8]:
* `Location` [L] = distance from the **I-end of the frame object** (piles: base = 0, top design station = 6.70;
  beams: add the Y of joint I, as `extract()` already does for forces). Rows are per design station
  (INFERRED: the per-station rows of [G11]; one "item" per station).
* Column: `MyOption` 1 = Check, 2 = Design; `PMMRatio` meaningful in check, `PMMArea` [L²] in design;
  `AVmajor`, `AVminor` = required shear steel per unit length [L²/L] (the CSI doc says only "area of transverse
  shear reinforcing per unit length"; "all legs" = EC2 Asw/s is INFERRED).
* Beam: `TopArea`, `BotArea` [L²] = flexural steel, **torsion steel not included**; `VmajorArea` [L²/L]
  = Asw/s for shear; `TLArea` [L²] = total longitudinal steel for torsion; `TTArea` [L²/L] = transverse
  torsion steel per unit length. "Per leg" vs "total" is UNVERIFIED for v27: the 2017 manual computes
  At/s = Vt/(z·fywd·cotθ) with Vt = torsional shear in one wall [S16 §3.5.3.4] → area of **one** leg of the closed
  stirrup, but EC2 torsion was re-implemented in v27.0 [S27 #11618]. (EC2 6.3.2(3) itself only gives the
  longitudinal ΣAsl, eq. 6.28; the transverse steel follows from 6.2 applied to each wall.)
  "Top" = +2 face = physical top (default local axes, no rotation).
* Combo names suffixed "(Sp)" = special code multipliers / capacity design.

```python
def design_and_read(m, model, save_path):
    set_ec2_preferences(m)
    define_design_sections(m, model)      # before the analysis: it is also the analysis section
    set_design_procedures(m, model)
    set_ec2_overwrites(m, model)
    select_design_combos(m)
    check(m.File.Save(str(save_path)), "File.Save")
    check(m.Analyze.RunAnalysis(), "RunAnalysis")
    check(m.DesignConcrete.StartDesign(), "DesignConcrete.StartDesign")
    if not m.DesignConcrete.GetResultsAvailable():
        raise RuntimeError("no concrete design results")
    check(m.SetPresentUnits(6), "SetPresentUnits")
    piles, beams = [], []
    for f in designed_frames(model):                                         # ItemType 0 = object
        if f["kind"] == "pile":
            col = check(m.DesignConcrete.GetSummaryResultsColumn(f["name"], 0, *[[] for _ in range(12)], 0),
                        f"GetSummaryResultsColumn {f['name']}")
            n, frame, opt, loc, pcombo, parea, pratio, vmc, avmaj, vnc, avmin, err, warn = col[:13]
            piles += [dict(frame=frame[k], option=opt[k], loc=loc[k], combo=pcombo[k], ratio=pratio[k],
                           av_major=avmaj[k], av_minor=avmin[k], error=err[k], warning=warn[k])
                      for k in range(n)]
        else:
            bm = check(m.DesignConcrete.GetSummaryResultsBeam(f["name"], 0, *[[] for _ in range(14)], 0),
                       f"GetSummaryResultsBeam {f['name']}")
            (n, frame, loc, tc, ta, bc, ba, vc, va, tlc, tla, ttc, tta, err, warn) = bm[:15]
            y0 = model["joints"][f["i"]][1]
            beams += [dict(frame=frame[k], axis=f["axis"], y=y0 + loc[k], loc=loc[k], top_combo=tc[k],
                           As_top=ta[k], bot_combo=bc[k], As_bot=ba[k], v_combo=vc[k], Asw_s=va[k],
                           Asl_T=tla[k], Ast_s=tta[k], error=err[k], warning=warn[k]) for k in range(n)]
    n_bad, n_failed, n_unchecked, bad = check(m.DesignConcrete.VerifyPassed(0, 0, 0, []), "VerifyPassed")[:4]
    return piles, beams, {"failed": n_failed, "not_checked": n_unchecked, "frames": list(bad or [])}
```
(Argument counts: column = Name + 13 ByRef + ItemType; beam = Name + 15 ByRef + ItemType. Returned lists:
column `[NumberItems, 12 arrays, ret]`, beam `[NumberItems, 14 arrays, ret]` — same indexing as [G13].)

Mock (`tests/mock_sap.py`) additions needed for `run_mock.py`: `DesignConcrete` (SetCode, GetCode,
SetComboAutoGenerate, SetComboStrength, GetComboStrength, StartDesign, GetResultsAvailable, VerifyPassed,
GetSummaryResultsColumn/Beam with the argument counts above, `Eurocode_2_2004` sub-object with Set/GetPreference
(item 1-17) and Set/GetOverwrite (item 1-6, 7-12 → return 1)), `PropFrame.SetRebarColumn` (15 args),
`GetRebarColumn` (15), `SetRebarBeam` (9), `GetSectProps` (13), `PropMaterial.SetMPUniaxial` (3-4),
`SetORebar_1` (11-12), `FrameObj.SetDesignProcedure` (2-3) / `GetDesignProcedure` (2), `PropRebar.GetProp`
(1 arg, return code last) / `SetProp` (3).

### A.10 DatabaseTables alternative (for items the OAPI does not expose, and to read design tables)

Signatures and ByRef layouts (VERIFIED-3P against a live SAP2000 [G12], and independently the same layouts in a second
SAP2000 library [G15]; function existence VERIFIED by [S25 #9729], [S27]):
```text
GetAllTables(NumberTables, TableKey(), TableName(), ImportType(), IsEmpty())
        -> raw[0]=NumberTables, raw[1]=TableKey[], raw[2]=TableName[], raw[3]=ImportType[], raw[4]=IsEmpty[], raw[-1]
GetAllFieldsInTable(TableKey, TableVersion, NumberFields, FieldKey(), FieldName(), Description(), UnitsString(), IsImportable())
        -> raw[0]=TableVersion, raw[1]=NumberFields, raw[2]=FieldKey[], raw[3]=FieldName[], raw[4]=Description[],
           raw[5]=UnitsString[], raw[6]=IsImportable[], raw[-1]
GetTableForEditingArray(TableKey, GroupName, TableVersion, FieldKeysIncluded(), NumberRecords, TableData())
        -> raw[0]=TableVersion, raw[1]=FieldKeysIncluded[], raw[2]=NumberRecords, raw[3]=TableData[] (flat, row-major)
SetTableForEditingArray(TableKey, TableVersion, FieldKeysIncluded(), NumberRecords, TableData()) -> raw[-1]
ApplyEditedTables(FillImportLog, NumFatalErrors, NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog)
        -> raw[0..3] counts, raw[4] = ImportLog, raw[-1]
CancelTableEditing()
GetTableForDisplayArray(TableKey, FieldKeyList(), GroupName, TableVersion, FieldKeysIncluded(), NumberRecords, TableData())
        -> raw[0]=FieldKeyList (echo), raw[1]=TableVersion, raw[2]=FieldKeysIncluded[], raw[3]=NumberRecords, raw[4]=TableData[]
```
Table keys are the mixed-case display names (e.g. "Material Properties 01 - General" [G12]); discover them,
never hard-code:
```python
import re

def table_key(m, pattern):
    raw = check(m.DatabaseTables.GetAllTables(0, [], [], [], []), "GetAllTables")
    keys = [k for k in raw[1] if re.search(pattern, k, re.I)]
    if len(keys) != 1:
        raise RuntimeError(f"{pattern!r} matches {keys}")
    return keys[0]

def table_fields(m, key):          # print once in SAP to lock the v27 field names (see section 6)
    raw = check(m.DatabaseTables.GetAllFieldsInTable(key, 0, 0, [], [], [], [], []), "GetAllFieldsInTable")
    return list(zip(raw[2], raw[3], raw[4], raw[5], raw[6]))

def edit_rows(m, key, key_field, updates):
    """updates = {row_key: {field: text}} ; values are strings as in the table."""
    raw = check(m.DatabaseTables.GetTableForEditingArray(key, "All", 0, [], 0, []), f"GetTableForEditingArray {key}")
    version, fields, nrec, data = raw[0], list(raw[1]), raw[2], list(raw[3])
    nf = len(fields)
    rows = [data[i*nf:(i+1)*nf] for i in range(nrec)]
    for row in rows:
        for fld, val in updates.get(row[fields.index(key_field)], {}).items():
            row[fields.index(fld)] = val
    flat = [c for row in rows for c in row]
    check(m.DatabaseTables.SetTableForEditingArray(key, version, fields, nrec, flat), f"SetTableForEditingArray {key}")
    res = m.DatabaseTables.ApplyEditedTables(True, 0, 0, 0, 0, "")
    if res[-1] != 0 or res[0] or res[1]:
        raise RuntimeError(f"ApplyEditedTables {key}: {res[:5]}")

# example: CYPE creep factor and theta = 45 deg on the piles, theta = 45 deg on the beams
# key = table_key(m, r"^Overwrites - Concrete Design - Eurocode 2-2004$")      # key text UNVERIFIED -> regex
# edit_rows(m, key, "Frame", {f["name"]: {"KPhi": "1.373", "TanTheta": "1"} for f in piles})

def read_display_table(m, key):
    raw = check(m.DatabaseTables.GetTableForDisplayArray(key, [""], "All", 0, [], 0, []), f"display {key}")
    fields, nrec, data = list(raw[2]), raw[3], list(raw[4])
    nf = len(fields)
    return [dict(zip(fields, data[i*nf:(i+1)*nf])) for i in range(nrec)]
```

---------------------------------------------------------------------------------------------------------

## 3. Part B — Behaviour questions

### B.1 Are "General" sections designed? — **No** (INFERRED, strong: follows from documented rebar-data restrictions; no CSI sentence states it)
* Reinforcement data (which is what makes a section a concrete beam or column for the design
  post-processor [S16 §2.3]) can only be attached to Rectangular/Circular (column or beam) and Tee/Angle (beam)
  sections: `SetRebarColumn` → types 8, 9 only; `SetRebarBeam` → types 3, 4, 8, 9 only, "calling this function for
  any other type … returns an error" [S12]; the rebar button exists only for Rectangular, Encased, Tee and Angle
  concrete shapes [S22]; the SAP Reinforcement Data form is for "rectangular or circular concrete members" [S19];
  the General-section form has only Section Properties / Time Dependent / Modifiers / Material / Dimensions /
  Color, no rebar button (https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/Define/Section_Properties/Frame_Sections/General_Section.htm).
  No CSI sentence saying literally "General sections are not designed" was found, hence "indirect".
* Consequence: the current `VIGA_*` General sections would produce no beam design. Hence B.3.

### B.2 Section Designer sections — **columns only** (VERIFIED)
"When a concrete material property has been specified, the No Design/Check option and the Concrete Column option
are available … If the Design Type is Concrete Column, any frame section assigned this property is designed by
the Concrete Frame Design postprocessor", with a Check/Design choice [S20]. There is no "Concrete Beam" design type
for SD sections, so an SD inverted T would only get a P-M-M check, no As top/bottom, no Asw/s beam design.

### B.3 Property modifiers and the "rectangle + modifiers" plan — **sound** (with 4 caveats)
* "Note that the modification factors affect only the analysis properties. They do not affect the design
  properties." [S18] (also: modifiers are not used for stress output, and "stresses used for frame design … are
  computed separately" [S17 pp.145-146]). Design uses the section
  dimensions t3 × t2 and the rebar data.
* Analysis is unchanged if **all 8** factors are set: CSI applies modifiers separately to a·e1, as2·g12, as3·g12,
  j·g12, i33·e1, i22·e1, **mass a·m and weight a·w** [S17 p.123] → MMod and WMod must equal the area ratio,
  otherwise PP changes (current PP self-weight uses A = 0.365 m²).
* Rectangle formulas SAP uses (A, As = 5/6 A, J with the 0.21 correction) were checked on 7 real exported
  rectangles (ratio 1.000000) [G10][G3]; the code above anyway reads SAP's own numbers with `GetSectProps`.
* Model check after the change: rerun and compare with `resultados_sap/SAP27_Element_Forces_Frames.xlsx`
  (`tools/compare_sap_tables.py`) — differences must be at round-off level.
* Design consequences (inverted T, rectangle 50x55; inverted L, rectangle 80x55):
  1. Sagging (bottom tension, compression in the 50-wide web at the top): **exact** (same h = 0.55, same d = 0.48).
  2. Hogging over the piles (top tension, compression at the bottom where the real width is 0.80/0.95):
     rectangle uses 0.50/0.80 → **slightly conservative** (x/d is small; difference in As_top of a few %).
     SAP designs negative moments always as rectangles anyway [S16 §2.4, §3.5.1.2.2].
  3. Shear: bw = web width (0.50 / 0.80) – same as CYPE's web; z = 0.9d [S16 §3.5.2.3].
  4. Caveats: (a) As,min of the bottom face uses bt = 0.50 instead of the 0.80 ledge width
     (EC2 9.2.1.1, bt = mean width of the tension zone [S16 §3.5.1.3]) → recompute As,min in post-processing;
     (b) torsion properties Ak, uk, tef from the rectangle, not the T (conservative); (c) beams are designed for
     major-axis M3, V2, T only; axial force and minor bending M2 (from the bollard loads) are ignored
     ("must be investigated independently") [S16 §2.4] — since v24 some codes consider axial force through an
     "Ignore Beneficial Pu" option [S23 #7379]; for EC2 the v27 behaviour is UNVERIFIED; (d) v24.2+ crack-width
     design would also use the rectangle.
* Alternatives considered:
  * **Concrete Tee rotated 180°** (local-axis angle 180): `SetTee(Name, Mat, t3=0.55, t2=0.80, tf=0.30, tw=0.50)`
    [S13] with `SetRebarBeam` (allowed for SECTION_T [S12]); a concrete Tee beam with CONCRETE BEAM data exists in a
    real CSI example [G5]. SAP's "top/positive" refer to the local +2 face, so with the rotation positive moments
    (SAP "bottom steel") would be physical hogging with the 0.80 × 0.30 flange in compression — a true T-beam
    design [S16 §3.5.1.2.2] (INFERRED from the local-axis convention). Costs: SAP "Top" = physical bottom,
    covers swapped, M3/V2 output signs flip for `compare.py`, and SAP's Tee torsion constant formula is not
    reproducible (checked: none of the usual formulas matches the exported J values) → modifiers must be computed
    from `GetSectProps` at run time; `.$2k` route needs two passes. Gain: only the small hogging refinement.
    Not recommended now; possible later refinement.
  * **Angle (L) for the end beams**: SAP angle sections use geometric axes and carry I23 ≠ 0 (real export:
    equal angle `I23=7.5525863516129E-07` in the v20.1.0 export [G6]) → changes the analysis coupling; not
    recommended.
  * **Precast I/U**: not designable by concrete frame design (`SetRebarBeam` does not accept them [S12]).
  * **Analysis section ≠ design section** (keep General for analysis, rectangle as design section via
    `SetDesignSection` or the `DesignSect` field): works for one design pass, but "the design section property is
    used for the next analysis section property" [S21 CF_Change_Design_Section] and v27.0 fixed a case where the
    API-set analysis section was overwritten by the design section [S27 #11901]. With modifiers on the rectangle
    there is no need for the split — use one section for both.

### B.4 EC2 column design in SAP: slenderness, sway, effective length, eccentricity
From [S16] §2.6, §3.4.2, App. A, B, D (2017 manual; no later EC2-column changes found in v24-v27 notes):
* Capacity: 3-D P-M-M surface (εcu = 0.0035 for fck ≤ 50, rectangular block λ = 0.8, η = 1.0, γc, γs, αcc, αct
  included), capacity ratio = OL/OC for each combination and each output station [S16 §3.4.1-3.4.2.3].
* **Imperfections**: ei = θi·l0/2, θi = θ0·αh·αm, αm = 1 (isolated member), αh = 2/√l; Mi = ei·NEd;
  "ei shall be taken ≥ emin" (EC2 6.1(4): h/30 ≥ 20 mm); applied in one direction at a time [S16 §3.4.2.1].
  (Which length SAP uses in αh is not legible in the manual text: UNVERIFIED; CYPE used l = 6.70 → αh = 0.7727.)
* **Second order (member P-δ)**: Nominal Curvature (default) → MEd = M0Ed + M2, M0Ed = M0e + Mi,
  M0e = 0.6 M02 + 0.4 M01 ≥ 0.4 M02, M2 = NEd·e2, e2 = (1/r)·l0²/c with **c = 8** fixed,
  1/r = Kr·Kφ·εyd/(0.45 d), **Kr = 1 and Kφ = 1 by default, overwritable per member**; skipped when λ < λlim
  (EC2 5.8.3.1). Nominal Stiffness: EI = 0.3·Ec·Ig, c0 = 8, NB with βl = 1 [S16 §3.4.2.2, App. D].
* **Effective length**: l0 = β·lu; lu = (unbraced-length ratio) × **object length** ("normally … the distance
  between END-I and END-J") [S16 §2.7, App. B]; β "conservatively taken as 1" but overwritable [S16 §3.4.2.2.1].
  Whether the *program-determined* lu subtracts the 0.55 m rigid end offset is not stated → UNVERIFIED → set the
  ratio 0.924138 explicitly. With an explicit ratio, lu = 0.924138 × L gives 6.70 m provided "object length" is the
  joint-to-joint length L (CSI reference: L = total length, Lc = L − ioff − joff [S17 p.129]) — INFERRED, not
  "irrelevant": confirm l0 = 6.70 m in the PIL_P1 design details (§6 step 3); if SAP printed 6.19 m (= ratio × Lc),
  use ratio 1.0 instead.
* **Sway vs braced**: no longer a EC2 switch — the "Framing type" item is the EC8 ductility class since v24.0
  [S23 #7261]. Global sway (P-Δ) must come from a P-Δ analysis; the design assumes it was done (b = 1)
  [S16 §2.6, §3.3, App. A]. CYPE ran first order + nominal curvature with β = 1 → do the same (no P-Δ).
* **End offsets**: output and design stations are over the **clear length** only; forces are output at the support
  faces and at equally spaced points; nothing inside the offsets [S16 §2.2][S17 pp.129-130]. Pile design stations
  therefore run 0 → 6.70 m (top station = beam soffit, like CYPE "Cabeza").

SAP vs CYPE for the pile check (what will differ even with identical forces):

| Aspect | SAP2000 EC2 [S16] | CYPE (Anejo, [C1]) | Setting / remark |
|---|---|---|---|
| Method | Nominal curvature | A19.5.8.8 nominal curvature | SOM = 2 |
| l0 | β·ratio·L | 6.700 m | ratio 0.924138, β = 1 |
| c in e2 | 8 | π² = 9.870 | cannot be changed → SAP e2 = 1.234 × CYPE |
| Kφ | 1 (default) | 1.373 (φef = 1.750) | `KPhi = 1.373` via table; `KPhi = 1.113` (=1.373·8/π²) reproduces CYPE's e2 exactly |
| Kr | 1 (default, not computed) | 1.000 | same |
| First-order moment used with e2 | M0e = 0.6 M02 + 0.4 M01 ≥ 0.4 M02 (manual, no sway/braced distinction) | ee = first-order eccentricity at the critical section (head) | SAP ≤ CYPE for double curvature (sway piles); whether SAP also keeps MEd ≥ M02 at the end stations is not stated in [S16] → compare station by station |
| emin | max(ei, emin) replaces ei | emin floors ee, ei added | small difference |
| fcd, fyd | αcc·fck/γc, fyk/γs | 33.33 / 434.78 MPa | αcc = 1, γc = 1.5, γs = 1.15 |

### B.5 Beam design outputs, face of support
* Flexure at every output station: top As from negative M (rectangular section), bottom As from positive M
  (rectangular or T); compression steel added when m > mlim, no redistribution (δ = 1); As,min/As,max per
  EC2 9.2.1.1 [S16 §3.5.1]. Since v24.0 the extra longitudinal steel from shear (EC2 6.18, ΔFtd) is calculated
  [S23 #7061] (where it is reported is UNVERIFIED).
* Shear: VRd,c (6.2.a/b), VRd,max (6.9), Asw/s (6.8), minimum ρw (9.2.2(5)); θ optimised within
  1 ≤ cotθ ≤ 2.5 for beams (always, since v24.0 [S23 #7380]); θ = 45° when torsion is significant (TEd > Tcr)
  and/or the combination is seismic (manual wording ambiguous); columns θ = 45°; torsion steel with θ = 45°
  [S16 §3.4.4, §3.5.2, §3.5.3]. Minimum shear steel is enforced also when VEd > VRd,c since v27.0 [S27 #11669].
  CYPE used θ = 45° → overwrite `TanTheta = 1`.
* Torsion: TRd,c check (6.31); if exceeded, closed stirrups At/s and longitudinal Asl; for T-beams the flange is
  used for section properties but not for reinforcement [S16 §3.5.3]; re-implemented in v27.0 [S27 #11618];
  "Consider Torsion Design?" overwrite honoured since v26.3 [S26 #11271]. CYPE reports no torsion in the inner
  beam checks ("no hay momento torsor", Anejo lines 1980-2036) → to compare, either set Consider Torsion = No for
  the beams (table field, name UNVERIFIED, see §6) or compare flexure/shear only.
* Face of support: design stations = output stations on the clear length; the first station is the face of the
  rigid end zone [S16 §2.2][S17 pp.129-130]. SAP does **not** reduce shear to the section at d from the face
  (EC2 6.2.1(8)); it designs every station including the face → conservative vs a d-from-face check.
  In our model the beam segments are already split at the pile faces (±0.20 m), and fully rigid segments are
  "No Design" (A.7).
* SLS: the 2017 manual says serviceability is not handled [S16 §3.2], but v24.2 added EC2 crack-width
  design/check for beams (M3) and columns, with results in the design report and database tables [S24 #9150]
  (crack-width limit overwrite fixed in v25.1 / v27.0). How service combinations are flagged for it (a
  "Service"/crack type in *Select Design Combos*?) and the table names are UNVERIFIED → keep the quasi-permanent
  crack check (PP + CM + 0.3·Qa) in our own post-processing. **Risk for the As comparison (checker):** v25.0 #9395
  says the beam (M3) *required* reinforcement "is increased by constant increments until the crack width, concrete
  and steel stresses satisfy the requirements", i.e. when the crack-width design is active the reported
  TopArea/BotArea can be SLS-governed, not ULS. The OAPI has no function to select service combos (only
  `SetComboStrength`, cf. [G14]), so it is unknown which combos (if any) feed that check in an OAPI-built model →
  after the first run, open the design details of one inner beam and confirm that no crack-width iteration raised
  As (§6).

---------------------------------------------------------------------------------------------------------

## 4. Part C — `.$2k` tables (format of `write_s2k.py`: 3-space separators, `Yes/No`, quotes around values with
spaces, lines > 240 chars wrapped with ` _`)

All example lines below were produced with `write_s2k.S2K` so that the formatting matches the writer that
already imports into v27.1 with 0 errors.

### C.1 `PROGRAM CONTROL` — add `ConcCode` — confidence HIGH
Field seen in v25.1, v25.3.1, v26.2 and the user's v27.1 exports [G1][G2][G3][U1]:
```
TABLE:  "PROGRAM CONTROL"
   ProgramName=SAP2000   Version=27.1.0   ProgLevel=Ultimate   CurrUnits="KN, m, C"   ConcCode="Eurocode 2-2004"   RegenHinge=Yes
```
Real line (v26.2.0, [G2]): `… CurrUnits="N, mm, C"   SteelCode="AISC 360-16"   ConcCode="ACI 318-19"   AlumCode="AA 2015"   ColdCode=AISI-16   ConcSCode="Eurocode 2-2004"   RegenHinge=Yes`.
(The user's licence is `ProgLevel=Advanced` [U1]; `Ultimate` already imported without error, so leave it.)

### C.2 Rebar material — confidence HIGH
Tables/fields as in real v21.0 and v25.x exports [G5][G10]:
```
TABLE:  "MATERIAL PROPERTIES 01 - GENERAL"
   Material=B500SD   Type=Rebar   SymType=Uniaxial   TempDepend=No   Color=White   Notes="Acero B 500 SD"
TABLE:  "MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES"
   Material=B500SD   UnitWeight=76.97   UnitMass=7.848756   E1=200000000   A1=1.17E-05
TABLE:  "MATERIAL PROPERTIES 03E - REBAR DATA"
   Material=B500SD   Fy=500000   Fu=575000   EffFy=550000   EffFu=632500   SSCurveOpt=Simple   SSHysType=Kinematic   SHard=0.01   SCap=0.09   FinalSlope=-0.1   UseCTDef=No
```
Real lines: v21.0 [G5] `Material=A615Gr60-460   Type=Rebar   SymType=Uniaxial   TempDepend=No   Color=White   Notes=…`,
`Material=A615Gr60-460   UnitWeight=76.9728639422648   UnitMass=7.84904737995992   E1=200000000   A1=1.17E-05`,
`Material=A615Gr60-460   Fy=460000   Fu=620530   EffFy=0.001   EffFu=0.001   SSCurveOpt=Simple   SSHysType=Kinematic   SHard=0.01   SCap=0.09   FinalSlope=-0.1   UseCTDef=No`.
v25.2 adds `CoupModType="Von Mises"` at the end of 03E [G10] (optional). The concrete rows (01, 02, 03B) stay as now.

### C.3 `FRAME SECTION PROPERTIES 01 - GENERAL` — beams become Rectangular + modifiers — confidence HIGH
(Rectangular rows with only t3/t2 + modifiers are what the writer already emits for `PILOTE_40x40`.)
```
TABLE:  "FRAME SECTION PROPERTIES 01 - GENERAL"
   SectionName=VIGA_T50x55_ALAS15x30   Material=HA-35   Shape=Rectangular   t3=0.55   t2=0.5   Color=Green   FromFile=No   AMod=1.327273   A2Mod=1.313245   A3Mod=1.4336   JMod=1.467072   I2Mod=2.688727   I3Mod=1.250206   MMod=1.327273 _
        WMod=1.327273   Notes="Design rectangle; modifiers = composite section"
   SectionName=VIGA_L80x55_ALA15x30   Material=HA-35   Shape=Rectangular   t3=0.55   t2=0.8   Color=Green   FromFile=No   AMod=1.102273   A2Mod=1.105216   A3Mod=1.135065   JMod=1.107293   I2Mod=1.396113   I3Mod=1.087939   MMod=1.102273 _
        WMod=1.102273   Notes="Design rectangle; modifiers = composite section"
   SectionName=VIGA_L80x55_ALA15x30_M   … A3Mod=1.134641 … (same otherwise)
```
`FRAME SECTION ASSIGNMENTS` then writes `SectionType=Rectangular` for these frames (the writer takes it from
`fs.shape`). Real concrete Tee row, if the Tee alternative is ever used (v21.0 [G5]):
`SectionName=FSEC1   Material=C30/37   Shape=Tee   t3=0.5   t2=0.6   tf=0.1   tw=0.3   Area=0.18 …`.

### C.4 `REBAR SIZES` — confidence HIGH (fields), MEDIUM (import semantics)
Fields `RebarID, Area, Diameter` in every real export [G1][G2][G3][G10]. The default list already contains
`10d/20d/25d` [S29], so the table is optional. If written, use SAP's own default values (kN-m, [G3]) so that
"replace" and "merge" import semantics give the same result (which one SAP applies is UNVERIFIED):
```
TABLE:  "REBAR SIZES"
   RebarID=10d   Area=7.85000013635E-05   Diameter=0.0099999997735
   RebarID=20d   Area=0.000314000005454   Diameter=0.019999999547
   RebarID=25d   Area=0.000491000008712   Diameter=0.0250000001907
```
Real line (v25.1.0 kN-m [G3]): `RebarID=25d   Area=0.000491000008711815   Diameter=0.0250000001907349`.

### C.5 `FRAME SECTION PROPERTIES 02 - CONCRETE COLUMN` — confidence HIGH
Same field set in v16.1.1, v20.1, v21.0, v24.2, v25.0, v25.2, v25.3.1 exports [G4][G6][G10][G9]:
`SectionName, RebarMatL, RebarMatC, ReinfConfig (Rectangular|Circular), LatReinf (Ties|Spiral), Cover,
NumBars3Dir, NumBars2Dir, BarSizeL, BarSizeC, SpacingC, NumCBars2, NumCBars3, ReinfType (Design|Check)`
(circular: `NumBarsCirc` instead of the two face counts [G9]).
```
TABLE:  "FRAME SECTION PROPERTIES 02 - CONCRETE COLUMN"
   SectionName=PILOTE_40x40   RebarMatL=B500SD   RebarMatC=B500SD   ReinfConfig=Rectangular   LatReinf=Ties   Cover=0.05   NumBars3Dir=4   NumBars2Dir=4   BarSizeL=25d   BarSizeC=10d   SpacingC=0.15   NumCBars2=2   NumCBars3=2 _
        ReinfType=Check
```
Real line, check mode, metric bar (v21.0.0 [G4]):
`SectionName=ConcCol-550x350   RebarMatL=A615Gr60-460   RebarMatC=A615Gr60-460   ReinfConfig=Rectangular   LatReinf=Ties   Cover=0.0361   NumBars3Dir=5   NumBars2Dir=2   BarSizeL=25M   BarSizeC=10M   SpacingC=0.15   NumCBars2=3   NumCBars3=3   ReinfType=Check`.
Mapping to OAPI: NumBars3Dir ↔ NumberR3Bars, NumBars2Dir ↔ NumberR2Bars, NumCBars2 ↔ Number2DirTieBars,
NumCBars3 ↔ Number3DirTieBars (INFERRED from the names; symmetric here, so harmless).

### C.6 `FRAME SECTION PROPERTIES 03 - CONCRETE BEAM` — confidence HIGH (v14.2, v20.1, v21.0 and v26.3.0 [G16])
Fields: `SectionName, RebarMatL, RebarMatC, TopCover, BotCover, TopLeftArea, TopRghtArea, BotLeftArea, BotRghtArea` (note `Rght`).
```
TABLE:  "FRAME SECTION PROPERTIES 03 - CONCRETE BEAM"
   SectionName=VIGA_T50x55_ALAS15x30   RebarMatL=B500SD   RebarMatC=B500SD   TopCover=0.07   BotCover=0.07   TopLeftArea=0   TopRghtArea=0   BotLeftArea=0   BotRghtArea=0
   SectionName=VIGA_L80x55_ALA15x30   RebarMatL=B500SD   RebarMatC=B500SD   TopCover=0.07   BotCover=0.07   TopLeftArea=0   TopRghtArea=0   BotLeftArea=0   BotRghtArea=0
   SectionName=VIGA_L80x55_ALA15x30_M   RebarMatL=B500SD   RebarMatC=B500SD   TopCover=0.07   BotCover=0.07   TopLeftArea=0   TopRghtArea=0   BotLeftArea=0   BotRghtArea=0
```
Real line (v21.0.0 [G5]): `SectionName=FSEC1   RebarMatL=A615Gr60-460   RebarMatC=A615Gr60-460   TopCover=0.075   BotCover=0.075   TopLeftArea=0   TopRghtArea=0   BotLeftArea=0   BotRghtArea=0`.
A concrete Rectangular section must appear in exactly one of 02/03 (column or beam). Edge beams: either add a 03
row for `VIGA_BORDE_25x30` or leave them "No Design" (recommended, C.7).

### C.7 `FRAME DESIGN PROCEDURES` — confidence HIGH
Fields `Frame, DesignProc`; values `"From Material"` and `"No Design"` (v16-v25.3.1 exports [G4][G9][G10]; enum
strings [G7 eFrameDesignProcedure]). Write one row per frame:
```
TABLE:  "FRAME DESIGN PROCEDURES"
   Frame=PIL_P1   DesignProc="From Material"
   Frame=VT2_3   DesignProc="No Design"
```
(`"No Design"` for `rigid=True` beam segments and all `beam_edge` frames.)

### C.8 Combination flags — confidence HIGH
The concrete-design flag lives in `COMBINATION DEFINITIONS`, field `ConcDesign` on the first row of each combo:
`None` or `Strength` (v21.0 [G4][G5]; field present with `None` in v24.2 [G10] and in our v27 writer). There is no
separate "concrete design combinations" table in SAP (ETABS has "Concrete Frame Design Load Combination Data"
[G11], SAP does not in the v25.3.1 list [G1]).
```
TABLE:  "COMBINATION DEFINITIONS"
   ComboName=ELU01   ComboType="Linear Add"   AutoDesign=No   CaseName=PP   ScaleFactor=1   SteelDesign=None   ConcDesign=Strength   AlumDesign=None   ColdDesign=None   Notes="CYPE ELU rotura hormigon comb. 1"
   ComboName=ELU01   CaseName=CM   ScaleFactor=1
```
Real line (v21.0.0 [G5]): `ComboName=COMB1   ComboType="Linear Add"   AutoDesign=No   CaseName=DL30   ScaleFactor=1.35   SteelDesign=None   ConcDesign=Strength   AlumDesign=None   ColdDesign=None`.
Writer change: in `combo()` set `"ConcDesign": "Strength" if fam == "ELU" else "None"` for the Linear-Add combos,
`None` for `ENV_*`.
Auto combos off (v21.0 [G5] `AutoGen=No`, [G4] `AutoGen=Yes`; table present in v25.3.1 [G1]):
```
TABLE:  "AUTO COMBINATION OPTION DATA 01 - GENERAL"
   DesignType=Concrete   AutoGen=No
```

### C.9 `PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004` — title HIGH, fields MEDIUM
Title in the v25.3.1 table list [G1] and in [G7 SAP2000Tables.cs]. Fields = exactly those read/written for EC2
by the SAP serializer [G7]; the same names (minus `Country`) appear in a real v20.1 row of the EC2-based Italian
NTC 2008 table [G6]:
`THDesign=Envelopes   NumCurves=24   NumPoints=11   MinEccen=Yes   PatLLF=0.75   UFLimit=0.95   CombosEq="Eq. 6.10"   RelClass="Class 2"   SOM="Nominal Stiffness"   Theta0=0.005   GammaS=1.15   GammaC=1.5   AlphaCC=0.85   AlphaCT=1   AlphaLCC=0.85   AlphaLCT=0.85` (NTC 2008, v20.1.0 [G6]).
Value strings [G7]: THDesign `Envelopes | Step-by-Step | Last Step | "Envelopes - All" | "Step-by-Step - All"`;
CombosEq `"Eq. 6.10" | "Max of Eq. 6.10a/6.10b"`; RelClass `"Class 1|2|3"`; SOM `"Nominal Stiffness" |
"Nominal Curvature" | None`; Country `"CEN Default" | Denmark | Finland | Germany | Ireland | Norway | Poland |
Portugal | Singapore | Slovenia | Sweden | "United Kingdom"`.
```
TABLE:  "PREFERENCES - CONCRETE DESIGN - EUROCODE 2-2004"
   THDesign=Envelopes   NumCurves=24   NumPoints=11   MinEccen=Yes   PatLLF=0.75   UFLimit=1   CombosEq="Eq. 6.10"   RelClass="Class 2"   SOM="Nominal Curvature"   Theta0=0.005   GammaS=1.15   GammaC=1.5   AlphaCC=1   AlphaCT=1 _
        AlphaLCC=0.85   AlphaLCT=0.85   Country="CEN Default"
```
v24+ fields not in the v20 serializer (INFERRED from [S23 #7379] and the SAP ACI 318-19 preference rows of
v25.1/v25.3.1/v26.2 exports `… IgnoreBPu=Yes   CTorsion=Yes … TanTheta=1` [G1][G2][G3]): probably `CTorsion`,
`TanTheta`, `IgnoreBPu`, plus a framing-type field and crack-width items. Do **not** write guessed names; set
DC Low per frame in C.10, and confirm the rest with §6. (Unknown fields are reported in the import log.)
Because country NDPs may overwrite γ/α when `Country` is read, CEN Default is chosen — its defaults equal the
values we need anyway, so field order cannot matter.

### C.10 `OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004` — title HIGH, fields MEDIUM-HIGH (v20 rows)
Real SAP rows quoted in [G7 ReadDesignConcreteOverwrites.cs]:
```
Frame=20   DesignSect="Program Determined"   FrameType="Program Determined"   RLLF=0   XLMajor=1   XLMinor=0   BetaMajor=2   BetaMinor=0   TanTheta=0   Kr=0   KPhi=0
Frame=27   DesignSect="Program Determined"   FrameType="Program Determined"   RLLF=0   XLMajor=0   XLMinor=0   TanTheta=0   Kr=0   KPhi=0
```
(beam rows carry no `BetaMajor/BetaMinor`). 0 = program determined. FrameType strings `"Program Determined" |
"DC High" | "DC Medium" | "DC Low" | Secondary` [G7 EN_2_2004_Overwrites.cs]. TanTheta 0.4…1.0 (0 = from
preferences) [G7].
```
TABLE:  "OVERWRITES - CONCRETE DESIGN - EUROCODE 2-2004"
   Frame=PIL_P1   DesignSect="Program Determined"   FrameType="DC Low"   RLLF=0   XLMajor=0.924138   XLMinor=0.924138   BetaMajor=1   BetaMinor=1   TanTheta=1   Kr=0   KPhi=1.373
   Frame=VT2_1   DesignSect="Program Determined"   FrameType="DC Low"   RLLF=0   XLMajor=0   XLMinor=0   TanTheta=1   Kr=0   KPhi=0
```
(one row per pile `PIL_*` and per designed `VT*` segment; `KPhi=1.373` reproduces CYPE's Kφ, or `1.113` to also
absorb c = 8 vs π²; `KPhi=0` = SAP default 1.0.)

### C.11 Tables NOT needed
`SECTION DESIGNER PROPERTIES *` (not used), `FRAME SECTION PROPERTIES 04…18` (other shapes),
`CONCRETE DESIGN …` result tables (output only; not importable).

### C.12 Writer summary (changes to `write_s2k.py` / `trasmallo.py`)
1. `trasmallo.py`: beam sections `shape="Rectangular"` with `design_rect=(h, b)` and modifiers computed with
   `sap_rect_props` (A.6); rebar material B500SD already exists (kind "Rebar") → emit it; add rebar data
   (column: pile; beam: VIGA_*), design-procedure flag per frame, overwrite rows.
2. `write_s2k.py`: add `ConcCode`, rebar material rows, tables C.5-C.10, `ConcDesign=Strength` for ELU.
3. `check_s2k.py`: add checks (every `VT*`/`PIL_*` designed frame has an overwrite row; every section in 02/03
   exists and is Rectangular; B500SD referenced exists; `25d`/`10d` names).

---------------------------------------------------------------------------------------------------------

## 5. Part D — Output tables for the post-processor

GUI: *Design > Concrete Frame Design > Start Design/Check* (F7), then *Display > Show Tables* (Ctrl+T) →
**Design Data > Concrete Frame Design** (path pattern as for steel: "Display > Show Tables > Design Data > Steel
Frame > … Table: Steel Design 1 - Summary Data" [S28]) → select the tables below → export to Excel.

| Table (SAP naming pattern "Concrete Design n - …- <Code>") | Status |
|---|---|
| `Concrete Design 1 - Column Summary Data - Eurocode 2-2004` | name pattern VERIFIED (real named-set selections "Concrete Design 1 - Column Summary Data - Mexican RCDF 2004" [G4], "Concrete Design 2 - Beam Summary Data - Mexican RCDF 2017" [G5]; EC2 table named in [S25 #10009]) |
| `Concrete Design 2 - Beam Summary Data - Eurocode 2-2004` | idem |
| `Concrete Design 3 - Joint Summary Data - Eurocode 2-2004` | only for DCH/DCM; empty with DC Low (INFERRED) |
| crack-width tables (v24.2+) | names UNVERIFIED |

Fields:
* **Beam summary** — real v20.1 SAP export (RCDF 2004, a code without torsion) [G8]:
  `Frame, DesignSect, DesignType, Status, Location, FTopCombo, FTopArea, FBotCombo, FBotArea, VCombo, VRebar,
  ErrMsg, WarnMsg`. For EC2 (torsion) additional torsion fields are expected: `TLngCombo, TLng…, TTrnCombo,
  TTrn…` (ETABS EC2 uses `TLngRebar`, `TTrnRebar` [G11]; exact SAP names UNVERIFIED).
* **Column summary** — INFERRED: `Frame, DesignSect, DesignType, DesignOpt, Status, Location, PMMCombo, PMMArea,
  PMMRatio, VMajCombo, VMajRebar, VMinCombo, VMinRebar, ErrMsg, WarnMsg` (PMMRatio/PMMArea/VMajRebar/VMinRebar used
  by a SAP results reader [Treu-Structure ResultsDeserializer.cs, https://github.com/rforsbach/Treu-Structure];
  DesignOpt/PMMRatio/VMajRebar/VMinRebar in the ETABS EC2 table [G11]).
* Units with kN-m: areas m², rebar per length m²/m, Location m.

Excel layout of a SAP v27.1 export (VERIFIED on the user's files [U1]): row 1 `TABLE:  <table name>`, row 2 field
keys, row 3 units, data from row 4; one sheet per table (sheet name = table name, truncated by Excel to 31 chars
— read the title in A1, not the sheet name); a `Program Control` sheet is added.

Parser (tolerant to the unverified torsion/column field names):
```python
import re
from openpyxl import load_workbook

def read_sap_xlsx(path):
    """{table name: {"fields": [...], "units": [...], "rows": [dict]}} for a SAP2000 Excel export."""
    out = {}
    for ws in load_workbook(path, read_only=True, data_only=True).worksheets:
        it = ws.iter_rows(values_only=True)
        title = str(next(it)[0])
        name = title.split("TABLE:", 1)[1].strip()
        fields = [f for f in next(it)]
        units = list(next(it))
        rows = [dict(zip(fields, r)) for r in it if any(v is not None for v in r)]
        out[name] = {"fields": fields, "units": units, "rows": rows}
    return out

ALIASES = {  # canonical -> regex over SAP field keys
    "frame": r"^Frame$", "loc": r"^(Location|Station)$", "status": r"^Status$",
    "as_top": r"^FTopArea$", "as_bot": r"^FBotArea$", "asw_s": r"^VRebar$",
    "asl_t": r"^TLng(Area|Rebar)$", "ast_s": r"^TTrn(Area|Rebar)$",
    "pmm_ratio": r"^PMMRatio$", "pmm_area": r"^PMMArea$", "pmm_combo": r"^PMMCombo$",
    "av_major": r"^VMaj(Rebar|Area)$", "av_minor": r"^VMin(Rebar|Area)$",
    "err": r"^ErrMsg$", "warn": r"^WarnMsg$",
}

def normalise(table):
    cols = {}
    for canon, rx in ALIASES.items():
        hit = [f for f in table["fields"] if f and re.match(rx, f)]
        if hit:
            cols[canon] = hit[0]
    return [{c: r.get(f) for c, f in cols.items()} for r in table["rows"]]

def design_tables(path):
    t = read_sap_xlsx(path)
    beam = next(v for k, v in t.items() if k.startswith("Concrete Design 2 - Beam Summary Data"))
    col = next(v for k, v in t.items() if k.startswith("Concrete Design 1 - Column Summary Data"))
    return normalise(col), normalise(beam)
```
The OAPI route (A.9) or `DatabaseTables.GetTableForDisplayArray` (A.10) return the same data without Excel;
`GetAvailableTables` lists the design result tables only from v25.0 on [S25 #9729].
Post-processing of beam rows: global Y = Y(joint I of the segment) + Location; the station at a pile face is the
segment end whose rigid offset touches the pile.

---------------------------------------------------------------------------------------------------------

## 6. What must still be confirmed once in SAP2000 v27.1 (10 minutes, then freeze the `.$2k` writer)

0. (Checker, no SAP run needed) Read two files of the v27.1 installation: (a) `CSI_OAPI_Documentation.chm` →
   `SetPreference`/`SetOverwrite {Concrete Eurocode 2-2004}` item lists (the online copy is v14-era, see A.3);
   (b) the table/field-key XML that v24.2+ installs in the program folder ("The resulting XML file as applied to all
   possible tables is now automatically included in the installation folder", v24.2.0 #9205; also produced by
   *Options > Database > Write Table and Field Keys to XML File*). (b) gives the exact v27 keys of the EC2
   preference/overwrite tables and of the `Concrete Design 1/2` result tables, which settles most of items 1-2.

1. Set the code to Eurocode 2-2004, open *Design > Concrete Frame Design > View/Revise Preferences* and
   *Overwrites* for one pile and one beam, then *Display > Show Tables*, *Model Definition > … Design Preferences*
   and *Design Overwrites*, and export `Preferences - Concrete Design - Eurocode 2-2004` and
   `Overwrites - Concrete Design - Eurocode 2-2004` (or run `table_fields()` of A.10 on both keys). This fixes:
   the v27 field names for framing type / Consider Torsion / TanTheta / IgnoreBPu / crack width, the FrameType
   string ("DC Low"), and the Ireland/Poland OAPI numbers (not needed).
2. After one design run, export `Concrete Design 1/2 …` and note the torsion/column field keys (update `ALIASES`).
3. Check in the design report of pile PIL_P1 (right-click, Details): l0 = 6.70 m (not 6.19 m), e2 with c = 8, ei,
   emin, Kφ; and in one inner beam (VT*_n next to a pile) that the reported As is ULS-governed (no crack-width
   iteration, B.5) and whether torsion steel is reported per leg.
4. *Select Design Combos*: confirm only ELU01-ELU22 are listed as Strength and that no DCON combos appear;
   look at the "Load Combination Type" drop-down to see whether a service/crack type exists (for the crack check).
5. Import the modified `.$2k` and read the import log: any "field not recognized" line names a wrong field.

UNVERIFIED items (collected): OAPI numbers for Ireland/Poland; how SAP measures lu when end offsets exist;
which length enters αh; v27 extra fields of the EC2 preference/overwrite tables and the FrameType string for
v27; SAP names of EC2 torsion/column fields in the design summary tables; crack-width combination flag and
tables and whether crack-width design raises the reported beam As; `REBAR SIZES` import semantics (replace vs
merge); `PropRebar.GetProp` output order (SetProp is VERIFIED-3P, A.5); code string of
EN 1992-1-1:2023; whether TTArea is per leg; where the EC2 6.18 extra tension steel is reported; the EC2 beam
axial-force (IgnoreBPu) behaviour in v27.
