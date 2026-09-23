# طراحی بتن‌آرمهٔ اسکلهٔ Trasmallo طبق Código Estructural (پوشهٔ `diseno/`)

این پوشه شمع‌ها و تیرهای یک ماژول ۴۰ متری **Muelle de Trasmallo** (بندر Cullera) را طبق **Código Estructural 2021** کنترل و طراحی می‌کند. مبنا **Anejo 19** است، یعنی EN 1992-1-1 با مقادیر ملی اسپانیا. نیروها از تحلیل **SAP2000 v27.1** در پوشهٔ [`../sap2000`](../sap2000/README.md) آمده‌اند. نتیجه با طراحی اصلی CYPECAD در Anejo 10 مقایسه شده است.

این فایل فقط نقطهٔ شروع است. برای توضیح کامل:
- **توضیح کامل و قدم‌به‌قدم (فارسی، با همهٔ فرمول‌ها):** [`documentacion/01_توضیح_کامل_طراحی.md`](documentacion/01_توضیح_کامل_طراحی.md)
- **گزارش فنی انگلیسی:** [`documentacion/02_Design_Report_EN.docx`](documentacion/02_Design_Report_EN.docx)
- **خلاصهٔ طراحی نهایی** (جدول آرماتور، دلیل‌ها و نکات باز): [`output/diseno_final.md`](output/diseno_final.md)
- **فایل Excel با نمودار:** [`output/Diseno_Codigo_Estructural.xlsx`](output/Diseno_Codigo_Estructural.xlsx)

---

## ۱. مبنای حکم نهایی (F0)

- **حکم نهایی** سه جزء دارد:
  - حالت مقطع سخت‌گیرانهٔ آیین‌نامه (`Mode.CODIGO`)؛
  - **مبنای ROM**: ROM 2.0-11، Tabla 4.6.4.1، با ψ0,Qa = 1.0 و ψ2,Qa = 0.8. برای کشش بولارد ψ2 = 0 است و مقدار 0.5 فقط برای حساسیت بررسی شده؛
  - محیط **XS3** با **wmax = 0.1 mm** در ترکیب شبه‌دائمی (CE Art. 27، Tabla 27.2).
- **مبنای CYPE** همان فرض‌های Anejo 10 است: ψ0,Qa = 0.7؛ ψ2,Qa = 0.3، که مقدار ساختمانی CTE است؛ و بولارد مثل باد با ψ2 = 0. این مبنا فقط برای هم‌خوانی با CYPECAD (parity) است. ظرفیت‌های CYPE دقیقاً بازتولید شده‌اند (اختلاف 0.00 %).
- η = نیرو / ظرفیت. هر η ≤ 1 یعنی قبول (CUMPLE).

---

## ۲. طراحی نهایی (F1 تا F6)

| عضو | آرماتور نهایی | تغییر نسبت به Anejo 10 | η حاکم (ROM/codigo) | حکم |
|---|---|---|---|---|
| **شمع‌ها** P1…P18: ۱۴ عدد، 40×40، HA-50، پیش‌ساخته (F1، F2) | 12Ø25؛ ۳ خاموت Ø10 با فاصلهٔ 150 میلی‌متر، و **با فاصلهٔ 100 در ۰.۴۰ متر بالای هر شمع** | فقط خاموت‌های سر شمع فشرده‌تر شده‌اند، برای محصورشدگی (A19.7.2(2) و A19.9.5.3(4)). حدود ۲.۸ کیلوگرم فولاد اضافه برای هر شمع. | 0.987 (N-M مرتبهٔ دوم، سر P3، ELR08) | CUMPLE (با خاموت‌های محصورکننده) |
| **تیرهای میانی**، محورهای ۲ تا ۶ (T معکوس 50x55+15x30+15x30) (F3) | بالا 5Ø20؛ **پایین 8Ø20 در جان + 4Ø16 در بال‌ها (33.18 cm²)**؛ آرماتور جانبی 2+2Ø10؛ خاموت‌ها بدون تغییر (۳ ساق Ø10 با فاصلهٔ 100، به‌علاوهٔ خاموت بال‌ها) | پایین 5Ø20 + 2Ø20 (21.99 cm²) → 33.18 cm²؛ وزن آرماتور طولی 32.1 → 40.8 kg/m | 0.962 (ترک، wk = 0.096 mm با ψ2 = 0.8) | CUMPLE |
| **تیرهای انتهایی**، محورهای ۱ و ۷ (L معکوس 80x55+15x30) (F4) | بالا 5Ø20؛ پایین 5Ø20 + 1Ø20 | بدون تغییر. اگر alveoplaca روی بال تکیه کند، بالا 4Ø25. | 0.973 (عضو کششی پیچش) | CUMPLE |
| **تیرهای لبه** 25×30 (F5) | **بالا 3Ø25 روی تکیه‌گاه‌ها**؛ پایین 2Ø16؛ خاموت Ø8 با فاصلهٔ 150 | بالا 2Ø16 → 3Ø25 (wk = 0.067 mm) | 0.872 | CUMPLE، **به شرط** توزیع بار مدل SAP |
| **همهٔ تیرهای عرضی**: جزئیات (F6) | میلگردهای بالا در فاصلهٔ al = z·cot θ/2 ≈ 0.43 m از بر شمع قطع نشوند و روی شمع کامل مهار شوند. | فقط توصیه است (قاعدهٔ decalaje در A19.6.2.3(7) و 9.2.1.3). | اطلاعاتی: 1.03 تا 1.18 با cot θ = 2 | — |

- **F2، کشش بولارد:** ψ2 = 0 مثل طرح اصلی حفظ شد، چون کشش مهار در اسکلهٔ ماهیگیری بار شبه‌دائمی نیست.
  - با ψ2 = 0.5، شش شمع ترک می‌خورند و wk تا 0.153 mm می‌رسد (بیشتر از 0.1).
  - هیچ آرماتوری در محدودهٔ As,max این مشکل را حل نمی‌کند.
  - پس ψ2 = 0 یک **فرض مستند** است.
- **وضعیت آرماتور فعلی Anejo 10:**
  - **شمع‌های P1، P2، P3 و P16:** فقط در کنترل σc ≤ 0.6·fck رد می‌شوند. این نتیجه در هر سه حالت یکسان است، چون این کنترل در هر دو مبنا با همان ترکیب‌های مشخصه انجام می‌شود.
  - **تیرهای میانی:** فقط در کنترل ترک و فقط با مبنای ROM رد می‌شوند.
  - **تیرهای لبه:** در همهٔ حالت‌ها رد می‌شوند.

---

## ۳. عددهای کلیدی

| موضوع | عدد | توضیح |
|---|---|---|
| شمع: η N-M مرتبهٔ دوم (بیشینه، سر P3) | **0.987** ROM/codigo؛ 0.933 CYPE/codigo؛ 0.920 parity | CYPE با نیروهای خودش 0.913 چاپ کرده و ما همان را دقیقاً بازتولید می‌کنیم. |
| شمع: برش | 0.814 | |
| شمع: As لازم / As موجود | **58.43 / 58.91 cm²** (نسبت 0.99) | As,max = 0.04·Ac = 64 cm². پس 12Ø25 **لازم و کافی** است. شمع‌های سمت خشکی حدود 39 تا 46 cm² لازم دارند (گزینهٔ 16Ø20)، ولی شمع پیش‌ساختهٔ یکسان حفظ شد. |
| شمع: ترک در ترکیب شبه‌دائمی | ترک نمی‌خورد (σct/fctm ≤ 0.764) | |
| شمع: σc / 0.6·fck در ترکیب مشخصه (سر P1، P2، P3 و P16) | 1.109 با Ecm؛ **0.966** با Ec,eff | با خاموت Ø10/100، fck,c ≈ 63 MPa و 0.6·fck,c ≈ 37.8 MPa است، که از σc,max ≈ 33.3 MPa بیشتر است. این یک تخمین تقریبی است (A19.3.1.9). |
| تیر میانی: خمش ELU / برش (با آرماتور آویز برای بال‌ها) | 0.88 / 0.72 | مقدار برش با cot θ بهینه است. |
| تیر میانی: ترک با 7Ø20 و ψ2 = 0.8 | M_qp = 137 تا 152 kN·m بیشتر از Mcr = 125 kN·m است؛ **wk = 0.155 تا 0.172 mm** | آرماتور موجود فقط تا ψ2,Qa = 0.58 تا 0.70 قبول است (کمترین آستانه 0.583، در محورهای ۲ و ۶). |
| تیر میانی: ترک با 8Ø20 + 4Ø16 | **wk = 0.096 mm** | تا ψ2,Qa ≈ 0.85 قبول است. |
| تیر انتهایی: پیچش / خمش | 0.973 / 0.873 | حساسیت: اگر alveoplaca روی بال به فاصلهٔ حدود 0.42 m از محور شمع تکیه کند، پیچش تعادلی 56 تا 61 kN·m در بر شمع ایجاد می‌شود و η به 1.18 می‌رسد. با بالا 4Ø25، η = 0.98 می‌شود. |
| تیر لبه: ترک روی تکیه‌گاه (لنگر منفی) | wk = 0.31 mm با 2Ø16 → **0.067 mm با 3Ø25** | در مدل SAP، V حدود ۲ برابر و M حدود 13 تا 21 % بیشتر از CYPE است، چون این تیر بار دال را با shell ارتوتروپ شریک است. |
| تیر لبه: برش با θ = 45° | 1.04 تا 1.08 | با cot θ بهینه 0.55 است، یعنی قبول. |
| هم‌خوانی با CYPE | 279 سطر PASS از 368 سطر، بدون FAIL | برگهٔ Comparacion_CYPE. `investigacion/validate_codigo.py`: 151 PASS، 0 FAIL. |
| کنترل EC2 خود SAP (F7) | نسبت شمع حدود **0.71** | با η مرتبهٔ دوم ما (0.93 تا 0.99) قابل مقایسه نیست. حکم با محاسبهٔ ماست (بخش ۷). |

---

## ۴. هفت خواستهٔ شما و جای جواب هر کدام

| # | خواسته | جواب کوتاه | کجا |
|---|---|---|---|
| ۱ | آرماتور لازم شمع | 58.43 cm² در برابر 58.91 موجود؛ 12Ø25 لازم و کافی است؛ خاموت سر شمع Ø10/100 | `output/pilotes.md` › *Required steel*، *Practical layouts* و *Proposal*؛ برگهٔ `Pilotes_As`؛ شکل‌های d2 و d6 |
| ۲ | طراحی آرماتور تیرها | تیر میانی: پایین 8Ø20 + 4Ø16؛ تیر لبه: بالا 3Ø25؛ تیر انتهایی بدون تغییر | `output/vigas.md` › §3 و §5؛ برگهٔ `Propuesta`؛ شکل d5 |
| ۳ | As لازم / As موجود | برای هر شمع و هر مقطع تیر | `output/pilotes.md` › *Required steel*؛ `output/vigas.md` › §3؛ برگه‌های `Pilotes_As` و `Vigas_Flexion`؛ شکل‌های d2 و d3 |
| ۴ | مقاومت مقطع بتن‌آرمه | منحنی اندرکنش N-M شمع؛ MRd تیرها | `output/pilotes.md` › *ULS N-Mx-My*؛ `output/vigas.md` › *Anexo: Flexión ELU*؛ برگه‌های `Pilotes_ELU` و `Vigas_Flexion`؛ شکل‌های d1، d3 و d8. موتور مقطع: `codigo/seccion.py`. هم‌خوانی با CYPE: برگهٔ `Comparacion_CYPE` و شکل d7. |
| ۵ | کنترل ترک | XS3، wmax = 0.1 mm، ترکیب شبه‌دائمی؛ و σc ≤ 0.6·fck | `output/pilotes.md` › *SLS: quasi-permanent crack control* و *SLS: characteristic stresses*؛ `output/vigas.md` › §4 و *Anexo: ELS*؛ برگه‌های `Pilotes_ELS` و `Vigas_Fisuracion`؛ شکل d4 (wk بر حسب ψ2) |
| ۶ | طراحی برشی با آرماتور | شمع 0.814؛ تیرها 0.72 (با آرماتور آویز بال‌ها)؛ خاموت‌ها بدون تغییر | `output/pilotes.md` › *Shear*؛ `output/vigas.md` › *Anexo: Cortante y torsión*؛ برگه‌های `Vigas_Cortante` و `Pilotes_ELU` |
| ۷ | طراحی نهایی طبق Código Estructural | جدول بخش ۲ همین فایل | `output/diseno_final.md`؛ برگه‌های `Resumen`، `Propuesta` و `Supuestos` |

---

## ۵. نقشهٔ پوشه

| مسیر | محتوا |
|---|---|
| `README.md` | همین فایل |
| `run_diseno.py` | **دستور اصلی.** همهٔ کنترل‌ها را اجرا می‌کند و فایل Excel، `diseno_final.md/.json` و شکل‌های d1 تا d8 را می‌سازد. |
| `esfuerzos.py` | نیروهای SAP (`sap2000/resultados_sap/SAP27_Element_Forces_Frames.xlsx`) را می‌خواند، آن‌ها را به قرارداد علامت CYPE می‌برد و ترکیب‌های دو مبنای CYPE و ROM را می‌سازد. |
| `codigo/seccion.py` | موتور مقطع فیبری: N-M دومحوره، ترک و تنش. ظرفیت‌ها دقیقاً با CYPE یکی‌اند. |
| `codigo/armado_pilote.py` | آرماتور موجود شمع (12Ø25 و خاموت‌ها) و چیدمان‌های عملی دیگر |
| `codigo/pilotes.py` | همهٔ کنترل‌های شمع: N-M مرتبهٔ اول و دوم، برش، جزئیات، ترک، تنش، As لازم و مقایسه با CYPE |
| `codigo/armado_vigas.py` | آرماتور موجود تیرهای عرضی و تیرهای لبه، طبق Anejo 10 |
| `codigo/vigas.py` | همهٔ کنترل‌های تیر: خمش، برش، آرماتور آویز، پیچش، جزئیات، ترک، خیز، جست‌وجوی آرماتور پیشنهادی و مقایسه با CYPE |
| `output/diseno_final.md` | **طراحی نهایی:** جدول آرماتور، دلیل‌ها، مقدار فولاد، حکم در هر مبنا و نکات باز |
| `output/diseno_final.json` | داده‌های پشت فایل بالا، شامل منحنی‌های ψ2 و منحنی اندرکنش شمع |
| `output/Diseno_Codigo_Estructural.xlsx` | ۱۰ برگه با ۱۱ نمودار Excel: Resumen، Pilotes_ELU، Pilotes_As، Pilotes_ELS، Vigas_Flexion، Vigas_Cortante، Vigas_Fisuracion، Propuesta، Comparacion_CYPE و Supuestos |
| `output/pilotes.md` | گزارش کامل شمع‌ها، با همهٔ ترکیب‌ها و مقطع‌ها |
| `output/pilotes.json` | داده‌های گزارش شمع‌ها |
| `output/vigas.md` | گزارش کامل تیرها |
| `output/vigas.json` | داده‌های گزارش تیرها |
| `ref/cype_design_reference.json` | همهٔ مقادیر طراحی CYPE از Anejo 10، با منبع هر عدد |
| `ref/cype_design_reference.md` | همان، به شکل جدول قابل خواندن |
| `investigacion/codigo_estructural_spec.md` | فرمول‌ها، مقادیر ملی اسپانیا، قراردادهای CYPE (C1 تا C21) و بحث ψ |
| `investigacion/sap_design_spec.md` | مبنای تنظیمات طراحی در SAP2000 و تفاوت آن با CE و CYPE |
| `investigacion/validate_codigo.py` | اعتبارسنجی مستقل فرمول‌ها با اعداد CYPE (151 PASS) |
| `investigacion/validate_codigo_output.txt` | خروجی اعتبارسنجی بالا |
| `sap/GUIA_SAP_DISENO.md` | **راهنمای فارسی طراحی در SAP2000**، گام‌به‌گام |
| `sap/datos_diseno_sap.py` | تنها منبع داده‌های طراحی SAP: Preferences، Overwrites، آرماتور و ترکیب‌های ELR |
| `sap/write_s2k_diseno.py` | فایل‌های `.$2k` طراحی را می‌سازد. |
| `sap/sap_oapi_diseno.py` | اسکریپت OAPI برای ویندوز: ساخت مدل، تنظیم، تحلیل و طراحی، و خروجی `diseno_SAP2000.json/.xlsx` |
| `sap/leer_diseno_sap.py` | خروجی طراحی SAP را می‌خواند و جدول مقایسه با طراحی ما را می‌سازد (`comparacion_diseno_SAP.md`). |
| `sap/output/Muelle_Trasmallo_40m_diseno.$2k` | **فایل اصلی Import در SAP:** مدل به‌علاوهٔ همهٔ جدول‌های طراحی |
| `sap/output/Muelle_Trasmallo_40m_diseno_overwrites.$2k` | همان فایل، با جدول Overwrites (اختیاری) |
| `sap/output/Muelle_Trasmallo_40m_rect.$2k` | فقط مقطع مستطیل به‌علاوهٔ ضرایب اصلاح، برای اثبات اینکه تحلیل عوض نشده است |
| `sap/output/valores_esperados_SAP_CYPE.md` | عددهایی که انتظار می‌رود SAP با مبنای CYPE نشان دهد |
| `sap/output/valores_esperados_SAP_ROM.md` | همان، با مبنای ROM |
| `sap/output/valores_esperados_SAP_*.json` | همان دو جدول، به‌صورت JSON |
| `tests/test_pilotes.py` | آزمون‌های شمع |
| `tests/test_vigas.py` | آزمون‌های تیر |
| `tests/test_sap_diseno.py` | آزمون فایل‌های SAP و اسکریپت OAPI، با SAP شبیه‌سازی‌شده |
| `tests/mock_sap_diseno.py` | همان SAP شبیه‌سازی‌شده |
| `tests/test_run_diseno.py` | آزمون `run_diseno.py`: فایل Excel، md و json، و شکل‌ها |
| `documentacion/01_توضیح_کامل_طراحی.md` | توضیح کامل فارسی برای خوانندهٔ تازه‌کار |
| `documentacion/02_Design_Report_EN.docx` | گزارش فنی انگلیسی |
| `documentacion/fig_teoria.py` | شکل d0 را می‌سازد: نمودار مصالح و حوزه‌های گسیختگی. |
| `documentacion/figuras/d0_diagramas_pivotes.png` | نمودار تنش-کرنش بتن و فولاد، و حوزه‌های A، B و C |
| `documentacion/figuras/d1_pilotes_eta.png` | η N-M مرتبهٔ دوم هر شمع، در سه حالت |
| `documentacion/figuras/d2_pilotes_As.png` | As لازم در برابر As موجود شمع‌ها |
| `documentacion/figuras/d3_vigas_flexion.png` | η خمش، برش و پیچش تیرها |
| `documentacion/figuras/d4_fisuracion_psi2.png` | σct/fctm و wk تیرهای میانی بر حسب ψ2,Qa، برای آرماتور موجود و پیشنهادی |
| `documentacion/figuras/d5_seccion_T_actual_propuesta.png` | مقطع T معکوس: آرماتور موجود و پیشنهادی |
| `documentacion/figuras/d6_seccion_pilote.png` | مقطع و نمای شمع، با خاموت‌های سر شمع |
| `documentacion/figuras/d7_paridad_cype.png` | مقادیر ما در برابر CYPE (خط 1:1) |
| `documentacion/figuras/d8_interaccion_pilote.png` | منحنی اندرکنش N-M شمع و نقاط ELU حاکم |

---

## ۶. اجرا (لینوکس و ویندوز)

همهٔ دستورها از **ریشهٔ مخزن** (`MarshalSp`) اجرا می‌شوند. داده‌های لازم در خود مخزن هستند: `sap2000/model/trasmallo.py` و `sap2000/resultados_sap/*.xlsx`. پایتون 3.9 یا جدیدتر لازم است.

**لینوکس:**
```bash
pip install numpy scipy openpyxl matplotlib pytest
python diseno/run_diseno.py            # همه‌چیز از اول: حدود ۱.۵ دقیقه
python diseno/run_diseno.py --reuse    # از pilotes.json و vigas.json موجود استفاده می‌کند: حدود ۱۵ ثانیه
python -m pytest diseno/tests -q       # ۱۲۵ آزمون، حدود ۳ دقیقه
```

**ویندوز (cmd):**
```bat
cd MarshalSp
set PYTHONUTF8=1
pip install numpy scipy openpyxl matplotlib pytest
python diseno\run_diseno.py
python -m pytest diseno\tests -q
```

- **ویندوز:** همهٔ برنامه‌ها فایل‌ها را صریحاً با UTF-8 می‌خوانند و می‌نویسند، پس `set PYTHONUTF8=1` فقط احتیاطی است. در PowerShell معادلش `$env:PYTHONUTF8 = "1"` است. دلیل احتیاط: فایل‌ها نویسه‌هایی مثل ψ، Ø و η دارند، و پایتونِ ویندوز در حالت عادی کدگذاری محلی (cp1252 یا cp1256) را به کار می‌برد.
- **اجرای کامل (بدون `--reuse`)** فایل‌های `output/pilotes.json|md` و `output/vigas.json|md` را دوباره می‌نویسد. اعداد همان می‌مانند و فقط `runtime_s` عوض می‌شود.
- **matplotlib** فقط برای شکل‌ها لازم است. بدون آن از `--no-figs` استفاده کنید.
- **گزینه‌های دیگر `run_diseno.py`:**
  - `--no-curves`: منحنی‌های ψ2 را نمی‌سازد.
  - `--out <پوشه>`: خروجی را در پوشهٔ دیگری می‌نویسد.
  - `--fig-dir <پوشه>`: شکل‌ها را در پوشهٔ دیگری می‌نویسد.
- **اجرای جداگانهٔ `codigo/pilotes.py` یا `codigo/vigas.py`:** حتماً با `--out` و یک پوشهٔ دیگر اجرا کنید. پیش‌فرض آن‌ها بازنویسی `output/pilotes.json` و `output/vigas.json` است، و `run_diseno.py --reuse` حکم نهایی را از همین دو فایل می‌خواند (مثلاً `--basis CYPE --mode cype` مبنای حکم را عوض می‌کند).
- **اعتبارسنجی فرمول‌ها:** `python diseno/investigacion/validate_codigo.py`. نتیجهٔ درست: 151 PASS و 0 FAIL.

---

## ۷. SAP2000: طراحی مستقل با Eurocode 2 (خلاصه)

راهنمای کامل، گام‌به‌گام و فارسی: **[`sap/GUIA_SAP_DISENO.md`](sap/GUIA_SAP_DISENO.md)**

- **راه الف، اسکریپت OAPI (پیشنهادی).** روی ویندوزی که SAP2000 دارد اجرا کنید:
  ```bat
  pip install comtypes openpyxl numpy scipy
  python diseno\sap\sap_oapi_diseno.py               :: مبنای CYPE (ترکیب‌های ELU01…ELU22)
  python diseno\sap\sap_oapi_diseno.py --base ROM    :: مبنای ROM (ELR01…ELR22) = مبنای حکم نهایی
  python diseno\sap\leer_diseno_sap.py diseno\sap\output\diseno_SAP2000.json
  ```
- **راه ب، رابط گرافیکی:**
  1. *File › Import › SAP2000 .s2k Text File › New Model* و فایل `sap/output/Muelle_Trasmallo_40m_diseno.$2k` را انتخاب کنید.
  2. جداکنندهٔ اعشار ویندوز باید «.» باشد. راه دیگر ساختن فایل با ویرگول است: `python diseno/sap/write_s2k_diseno.py --decimal ,`
  3. تنظیمات را طبق بخش‌های ۴.۳ تا ۴.۸ راهنما کنترل کنید. خلاصهٔ تنظیمات:
     - Eurocode 2-2004 با CEN Default؛ γc = 1.5، γs = 1.15 و αcc = 1.0؛
     - روش Nominal Curvature با Kφ = 1.1129؛
     - Framing Type = DC Low و Tan(θ) = 1؛
     - ترکیب‌های خودکار خاموش.
- **SAP آرماتور Anejo 10 را کنترل می‌کند، نه طرح نهایی ما را:** برای شمع‌ها 12Ø25 در حالت Check، و برای تیرها As لازم.
- **نسبت شمع در SAP حدود 0.71 است**، در برابر 0.93 تا 0.99 در محاسبهٔ ما. این خطا نیست، تفاوت روش است (F7):
  - SAP لنگر معادل `M0e = 0.6·M02 + 0.4·M01 ≥ 0.4·M02` را به کار می‌برد.
  - SAP فرض می‌کند اثر P-Δ از تحلیل آمده باشد، در حالی که تحلیل ما خطی مرتبهٔ اول است.
  - پس حکم با محاسبهٔ ماست.
- **کنترل‌هایی که SAP انجام نمی‌دهد:** عرض ترک XS3، قرارداد ν1 و fywd در CE، As,min اسپانیا و آرماتور آویز بال‌ها. همهٔ این‌ها در `codigo/` انجام شده‌اند.

---

## ۸. بعد از اجرای طراحی در SAP، این‌ها را برگردانید

1. **`SAP27_Diseno_Hormigon.xlsx`:** مسیر در SAP: *Display › Show Tables › Design Data › Concrete Frame Design*، سپس *File › Export All Tables › To Excel*. این دو جدول را انتخاب کنید:
   - `Concrete Design 1 - Column Summary Data - Eurocode 2-2004`
   - `Concrete Design 2 - Beam Summary Data - Eurocode 2-2004`
2. **متن گزارش Import**، یا اسکرین‌شات آن.
3. **`Element Forces - Frames` و `Joint Reactions`** برای حالت‌های PP، CM، Qa، TB1، TB2 و TB3 (مثلاً `SAP27_diseno_Element_Forces_Frames.xlsx`)، برای اثبات اینکه تحلیل تغییر نکرده است.
4. **جزئیات طراحی `PIL_P3` و `VT2_5`:** از *Details › File › Print to file* یا اسکرین‌شات. یادداشت کنید:
   - l0 و e2 و Kφ؛
   - MEd کدام فرمول است: `M0e + Mi + M2` یا `M02 + Mi + M2`.
5. **اسکرین‌شات فرم‌های Preferences و Overwrites**، برای یک شمع و یک تیر.
6. **اگر راه OAPI را اجرا کرده‌اید:** `diseno/sap/output/diseno_SAP2000.json` و `.xlsx`، به‌علاوهٔ متن کنسول.
7. **مبنای ترکیب‌ها** را بنویسید: ELU (CYPE) یا ELR (ROM).

ما آن‌ها را با `python diseno/sap/leer_diseno_sap.py SAP27_Diseno_Hormigon.xlsx` می‌خوانیم و نتیجه در `sap/output/comparacion_diseno_SAP.md` نوشته می‌شود.

---

## ۹. نکات باز

1. **محصورشدگی سر شمع (F1):** خاموت‌های Ø10 با فاصلهٔ 100 در ۰.۴۰ متر بالای شمع باید در نقشهٔ قطعهٔ پیش‌ساخته بیایند. توجیه عددی محصورشدگی به‌عنوان «اقدام دیگر» در A19.7.2(2) تقریبی است. جایگزین: بتن HA-60.
2. **ψ2 کشش بولارد = 0 (F2):** باید با Autoridad Portuaria (سوابق پهلوگیری) تأیید شود. با ψ2 = 0.5، شش شمع ترک می‌خورند و راه‌حلی با As ≤ 0.04·Ac وجود ندارد. جایگزین: پذیرفتن wk ≤ 0.2 mm برای این حالت.
3. **محل تکیهٔ alveoplaca روی تیرهای انتهایی (F4):** روی محور شمع است یا روی بال؟ اگر روی بال باشد، بالا 4Ø25 به‌جای 5Ø20.
4. **توزیع بار روی تیرهای لبه (F5):** پیشنهاد 3Ø25 به مدل دال وابسته است (shell ارتوتروپ SAP در برابر نوارهای CYPE). یا مدل تأیید شود، یا تیر لبه عمیق‌تر شود. اگر فقط بارگذاری نواری CYPE درست باشد، 2Ø16 موجود برای ELU کافی است.
5. **قطع میلگردهای بالا (F6):** در فاصلهٔ al ≈ 0.43 m از بر شمع قطع نشوند و روی شمع کامل مهار شوند. با cot θ = 1 (فرض CYPE)، اثر کمتر است.
6. **آرماتور پایین جدید تیرهای میانی (F3):** فاصلهٔ آزاد 8Ø20 در جان 31 mm است، که از dg + 5 = 25 mm بیشتر است. بتن‌ریزی و مهار میلگردها در گرهٔ تیر و شمع کنترل شود.
7. **کنترل EC2 خود SAP (F7):** نسبت شمع حدود 0.71 است و با مرتبهٔ دوم ما قابل مقایسه نیست (بخش ۷).
8. **Anejo 10 (F8):**
   - نتایج CYPE دقیقاً بازتولید شده‌اند، ولی حکم ترک CYPE به ψ2 = 0.3 (مقدار ساختمانی) تکیه دارد.
   - CYPE این کنترل‌ها را انجام نداده است: آرماتور آویز بال‌ها، حد تنش مشخصه σc و پیچش بال تیرهای انتهایی.
   - ستون «Aprov.» در listing برابر 1.014 × η است و دلیلش معلوم نیست.
   - در متن Anejo 10 یک اشتباه محاسباتی هست: 410/4.65 = 88 kN، نه 83.
9. **φef = 1.75** (دادهٔ CYPE) در مرتبهٔ دوم شمع محافظه‌کارانه است. با ψ2 بولارد = 0، مقدار A19.5.8.4 تقریباً 0 می‌شود. این مقدار کاهش داده نشده است.

---

*مدل تحلیلی و مقایسهٔ نیروها با CYPE:* [`../sap2000/README.md`](../sap2000/README.md) و [`../documentacion/01_توضیح_کامل_پروژه.md`](../documentacion/01_توضیح_کامل_پروژه.md)
