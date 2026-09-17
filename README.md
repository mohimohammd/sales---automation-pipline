# Enterprise Sales Analytics — Automated Data Pipeline

## المشكلة (Problem)
لوحة "Enterprise Sales Analytics" الأصلية تعتمد على بيانات ثابتة (Static)
يتم توليدها وتحميلها مرة واحدة يدوياً. هذا يعني أن أي تحديث للبيانات
(مبيعات جديدة، تغيّر أسعار الصرف) يتطلب تدخل يدوي متكرر — وهي مشكلة
حقيقية في بيئات العمل حيث تصل بيانات المعاملات باستمرار ويجب أن
تعكسها اللوحات دون تأخير.

## الحل (Solution)
بُني هذا الـ pipeline لأتمتة العملية بالكامل:

1. **توليد بيانات يومية** (`generate_daily_sales.py`) — يحاكي وصول
   طلبات مبيعات جديدة يومياً بنفس هيكل بيانات المشروع الأصلي.
2. **جلب بيانات حقيقية** (`fetch_exchange_rates.py`) — يسحب أسعار
   الصرف الفعلية يومياً من API خارجي (SAR إلى USD/EUR/GBP/AED/EGP/INR)،
   مما يضيف طبقة بيانات حقيقية غير اصطناعية للمشروع.
3. **تحميل تدريجي** (`load_to_sql.py`) — يُدخل البيانات الجديدة فقط
   إلى SQL Server دون تكرار (Incremental Load)، وينشئ الجداول تلقائياً
   إن لم تكن موجودة.
4. **جدولة سحابية** (GitHub Actions) — يشغّل الخطوات الثلاث تلقائياً
   كل يوم الساعة 6:00 صباحاً بتوقيت الرياض، بدون أي تدخل يدوي أو
   الحاجة لجهاز شخصي يعمل باستمرار.
5. **صفحة Power BI جديدة**: "Multi-Currency Performance" تستخدم
   أسعار الصرف الحقيقية اليومية لعرض المبيعات بعملات متعددة.

## الأثر (Impact)
- تحويل التحديث من "يدوي، غير منتظم" إلى "تلقائي، يومي، موثّق"
- كل تشغيل يظهر في تبويب Actions على GitHub كسجل تدقيق فعلي (audit trail)
- إضافة بُعد بيانات حقيقي (أسعار الصرف الحية) لمشروع كان بالكامل
  بيانات اصطناعية

## البنية التقنية
```
sales-automation-pipeline/
├── scripts/
│   ├── generate_daily_sales.py     # توليد الطلبات اليومية
│   ├── fetch_exchange_rates.py     # جلب أسعار الصرف الحقيقية
│   └── load_to_sql.py              # تحميل تدريجي إلى SQL Server
├── data/incoming/                  # ملفات CSV اليومية (تُنشأ تلقائياً)
├── .github/workflows/
│   └── daily_pipeline.yml          # جدولة GitHub Actions اليومية
├── requirements.txt
└── README.md
```

## الإعداد (Setup)
1. أنشئ الـ Secrets التالية في إعدادات الـ repository
   (Settings → Secrets and variables → Actions):
   - `SQL_SERVER_HOST`
   - `SQL_DATABASE_NAME`
   - `SQL_USERNAME`
   - `SQL_PASSWORD`
   - `EXCHANGE_RATE_API_KEY` (اختياري — بدونه يُستخدم endpoint مجاني بديل)
2. الـ workflow يشتغل تلقائياً يومياً، أو يدوياً عبر تبويب
   Actions → Daily Sales & Exchange Rate Pipeline → Run workflow.

## المهارات المُظهرة (Skills Demonstrated)
Python (ETL) · REST API Integration · SQL Server (Incremental Load,
Idempotent Upserts) · CI/CD Automation (GitHub Actions) · Environment-based
Secrets Management · Power BI (Multi-Currency Modeling)
