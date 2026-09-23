# طراحی بتن‌آرمهٔ اسکلهٔ Trasmallo طبق Código Estructural (پوشهٔ `diseno/`)

شمع‌ها و تیرهای ماژول ۴۰ متری Muelle de Trasmallo (بندر Cullera) طبق **Código Estructural 2021, Anejo 19** طراحی و کنترل می‌شوند. نیروها از مدل **SAP2000 v27.1** پوشهٔ [`../sap2000`](../sap2000/README.md) می‌آیند و نتایج با طراحی CYPECAD در **Anejo 10** مقایسه می‌شوند.

## وضعیت

| مرحله | وضعیت | کجا |
|---|---|---|
| ۱. کنترل مستقل با پایتون (غیر از SAP) | انجام شده | [`python/`](python/) |
| ۲. طراحی بتن در خود SAP2000 (Eurocode 2) | **فایل‌ها آماده‌اند؛ منتظر اجرای کاربر** | [`sap/`](sap/)، راهنما: [`sap/GUIA_SAP_DISENO.md`](sap/GUIA_SAP_DISENO.md) |
| ۳. گزارش فارسی و گزارش فنی انگلیسی (Word) | **بعد از دریافت نتایج SAP** | `documentacion/` (بعداً ساخته می‌شود) |

گزارش فارسی با خلاصهٔ کار قبلی (حداکثر یک صفحه) شروع می‌شود و سپس ادامهٔ کار را توضیح می‌دهد. گزارش انگلیسی کاملاً فنی است و روی نتایج SAP و مقایسه با Anejo 10 تمرکز دارد. شکل‌های گزارش‌ها هم نتایج SAP را با Anejo 10 مقایسه می‌کنند.

## نقشهٔ پوشه

| مسیر | محتوا |
|---|---|
| `ref/cype_design_reference.json` و `.md` | همهٔ اعداد طراحی CYPE در Anejo 10، هر عدد با منبعش (شمارهٔ پاراگراف، جدول یا تصویر) |
| `sap/` | ورودی‌های طراحی بتن در SAP2000: فایل‌های `.$2k`، اسکریپت OAPI، خوانندهٔ نتایج، راهنمای فارسی GUI، مشخصات فنی (`sap_design_spec.md`)، آزمون‌ها |
| `python/` | روش مستقل ما (غیر از SAP): همهٔ اسکریپت‌های پایتون، خروجی‌ها، شکل‌ها و آزمون‌ها. توضیح کامل روش‌ها در [`python/توضیح_روش_ها.md`](python/توضیح_روش_ها.md) |
| `python/output/` | نتایج پایتون: `pilotes.*`، `vigas.*`، `diseno_final.*`، `Diseno_Codigo_Estructural.xlsx` |
| `python/figuras/` | شکل‌های مقایسه‌های پایتون (d0 تا d8) |

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
python3 -m pytest diseno/python/tests diseno/sap/tests -q
```
در ویندوز همان دستورها با `python` و مسیر `diseno\python\...` کار می‌کنند. فایل‌ها صریحاً با UTF-8 خوانده و نوشته می‌شوند.
