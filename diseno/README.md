# طراحی بتن‌آرمهٔ اسکلهٔ Trasmallo طبق Código Estructural (پوشهٔ `diseno/`)

شمع‌ها و تیرهای ماژول ۴۰ متری Muelle de Trasmallo (بندر Cullera) طبق **Código Estructural 2021, Anejo 19** طراحی و کنترل می‌شوند. نیروها از مدل **SAP2000 v27.1** پوشهٔ [`../sap2000`](../sap2000/README.md) می‌آیند و نتایج با طراحی CYPECAD در **Anejo 10** مقایسه می‌شوند.

## وضعیت

| مرحله | وضعیت | کجا |
|---|---|---|
| ۱. کنترل مستقل با پایتون (غیر از SAP) | انجام شده، بدون زلزله | [`python/`](python/) |
| ۲. به‌روز کردن زلزله طبق پروژهٔ Rover (تصمیم Eva) | **کار بعدی** | مرجع‌ها: [`referencia_rover/`](referencia_rover/) |
| ۳. طراحی بتن در خود SAP2000 (Eurocode 2) | فایل‌ها آماده‌اند (هنوز بدون زلزله)؛ بعد از مرحلهٔ ۲ به‌روز می‌شوند و کاربر اجرا می‌کند | [`sap/`](sap/)، راهنما: [`sap/GUIA_SAP_DISENO.md`](sap/GUIA_SAP_DISENO.md) |
| ۴. گزارش فارسی و گزارش فنی انگلیسی (Word) | بعد از دریافت نتایج SAP | `documentacion/` (بعداً ساخته می‌شود) |

**تصمیم سرپرست (Eva):** مدل SAP همان Muelle de Trasmallo ادامه پیدا می‌کند تا نیروهای طراحی (dimensionado) از آن گرفته شود. زلزله دیگر کنار گذاشته نمی‌شود (Anejo 10: NCSE-02، ab = 0.07g) و طبق پروژهٔ Rover وارد می‌شود: Anejo Nacional UNE-EN 1998-1، ag,R = 0.15g، K = 1، خاک D، ρ = 0.85، S = 1.91، ac = 0.2435g، طیف افقی و قائم. مطالعهٔ ژئوتکنیک Rover دادهٔ خاک همان منطقه را هم می‌دهد.

گزارش فارسی با خلاصهٔ کار قبلی (حداکثر یک صفحه) شروع می‌شود و سپس ادامهٔ کار را توضیح می‌دهد. گزارش انگلیسی کاملاً فنی است و روی نتایج SAP و مقایسه با Anejo 10 تمرکز دارد. شکل‌های گزارش‌ها هم نتایج SAP را با Anejo 10 مقایسه می‌کنند.

## نقشهٔ پوشه

| مسیر | محتوا |
|---|---|
| `ref/cype_design_reference.json` و `.md` | همهٔ اعداد طراحی CYPE در Anejo 10، هر عدد با منبعش (شمارهٔ پاراگراف، جدول یا تصویر) |
| `sap/` | ورودی‌های طراحی بتن در SAP2000: فایل‌های `.$2k`، اسکریپت OAPI، خوانندهٔ نتایج، راهنمای فارسی GUI، مشخصات فنی (`sap_design_spec.md`)، آزمون‌ها |
| `python/` | روش مستقل ما (غیر از SAP): همهٔ اسکریپت‌های پایتون، خروجی‌ها، شکل‌ها و آزمون‌ها. توضیح کامل روش‌ها در [`python/توضیح_روش_ها.md`](python/توضیح_روش_ها.md)؛ آموزش از صفر (مقایسه‌ها، فرمول‌ها و تبدیل آن‌ها به کد) در [`python/آموزش_مقایسه_ها_و_کد.md`](python/آموزش_مقایسه_ها_و_کد.md) |
| `python/output/` | نتایج پایتون: `pilotes.*`، `vigas.*`، `diseno_final.*`، `Diseno_Codigo_Estructural.xlsx` |
| `python/figuras/` | شکل‌های مقایسه‌های پایتون (d0 تا d8) |
| `referencia_rover/` | مرجع‌های پروژهٔ همسایه (Rover، اسکلهٔ Jet Ski روی Júcar): انخوی محاسبات سازه، نقشه‌ها، روش اجرا و مطالعهٔ ژئوتکنیک (PDF)، با [`README`](referencia_rover/README.md) و جدول مقایسه با Trasmallo. مبنای زلزله و دادهٔ خاک. |
| `python/extraccion_anejo10/` | استخراج اعداد CYPE از فایل Word مربوط به Anejo 10 با یک دستور (`extraer.py`)، که `ref/` را عیناً دوباره می‌سازد |

## اجرای SAP (خلاصه)

1. فایل `sap/output/Muelle_Trasmallo_40m_diseno.$2k` را در SAP2000 v27.1 با File › Import › SAP2000 .s2k (New Model) باز کنید.
2. تنظیمات Preferences، Overwrites و Design Combos را طبق بخش‌های ۴.۳ تا ۴.۷ راهنما کنترل یا وارد کنید، سپس Start Design/Check را بزنید.
3. جدول‌های `Concrete Design 1 - Column Summary Data - Eurocode 2-2004` و `Concrete Design 2 - Beam Summary Data - Eurocode 2-2004` را به Excel خروجی بگیرید.

راه جایگزین (ویندوز، پایتون): `python diseno\sap\sap_oapi_diseno.py`، که همهٔ مراحل را خودکار انجام می‌دهد.

**برای مقایسه این‌ها را برگردانید:** فایل Excel دو جدول بالا؛ گزارش Import؛ صفحهٔ Details شمع `PIL_P3` و تیر `VT2_5` (عکس یا فایل)؛ عکس فرم‌های Preferences و Overwrites.

## نتیجهٔ مقدماتی روش پایتون (قبل از مقایسه با SAP)

| عضو | آرماتور Anejo 10 | نتیجهٔ کنترل پایتون (مبنای ROM، Código سخت‌گیرانه، XS3 با wmax = 0.1 mm) |
|---|---|---|
| شمع‌ها (۱۴ عدد) | 12Ø25، خاموت Ø10/150 | ELU قبول (بیشترین η = 0.987 در P3). σc ≤ 0.6·fck در سر P1، P2، P3 و P16 با Ecm رد می‌شود (1.109). پیشنهاد: خاموت Ø10/100 در ۰.۴۰ متر بالای شمع. |
| تیرهای میانی (محورهای ۲ تا ۶) | پایین 7Ø20 | ELU قبول. با ψ2 = 0.8 ترک رد می‌شود (wk = 0.155 تا 0.172 mm). پیشنهاد: پایین 8Ø20 + 4Ø16 (wk = 0.096 mm). |
| تیرهای انتهایی (محورهای ۱ و ۷) | بدون تغییر | قبول (η = 0.973) |
| تیرهای لبه 25×30 | 2Ø16 | با توزیع بار مدل SAP، ترک روی تکیه‌گاه رد می‌شود. پیشنهاد: بالا 3Ø25 روی تکیه‌گاه‌ها. |

جزئیات در [`python/output/diseno_final.md`](python/output/diseno_final.md). نتیجهٔ نهایی بعد از مقایسه با طراحی SAP اعلام می‌شود.

## اجرای روش پایتون

```bash
pip install numpy scipy openpyxl matplotlib pytest python-docx
python3 diseno/python/run_diseno.py              # همهٔ کنترل‌ها + Excel + شکل‌ها (حدود ۹۰ ثانیه)
python3 diseno/python/run_diseno.py --reuse      # فقط Excel و شکل‌ها از JSON موجود (حدود ۱۵ ثانیه)
python3 -m pytest diseno/python/tests diseno/sap/tests -q     # ۱۳۱ آزمون
python3 diseno/python/extraccion_anejo10/extraer.py        # بازسازی ref/ از Anejo 10
```
در ویندوز همان دستورها با `python` و مسیر `diseno\python\...` کار می‌کنند. فایل‌ها صریحاً با UTF-8 خوانده و نوشته می‌شوند.
