# نظام إدارة تكاليف البناء
## Construction Cost Management System

نظام متكامل لإدارة مصروفات مشاريع البناء (الفيلات) باللغة العربية.

---

## 🚀 التشغيل السريع

```bash
# 1. إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إعداد قاعدة البيانات
python manage.py migrate

# 4. إنشاء البيانات الأولية (فيلات + تصنيفات)
python manage.py seed_data

# 5. (اختياري) بيانات تجريبية
python manage.py seed_sample

# 6. تشغيل الخادم
python manage.py runserver
```

افتح المتصفح على: http://127.0.0.1:8000

**اسم المستخدم:** admin  
**كلمة المرور:** admin123

---

## 📦 المتطلبات

```
django>=4.2
pillow
psycopg2-binary  # لـ PostgreSQL
```

---

## 🗃️ قاعدة البيانات

### SQLite (افتراضي - للتطوير)
لا يحتاج إعداد إضافي.

### PostgreSQL (الإنتاج)
في `core/settings.py`، قم بإلغاء تعليق إعدادات PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'construction_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📋 الميزات

- **لوحة التحكم**: ملخص كامل لجميع الفيلات والمصروفات
- **إدارة المصروفات**: إضافة، تعديل، حذف مع دعم المرفقات
- **التخصيص للفيلات**: توزيع متساوٍ أو مخصص على عدة فيلات
- **تفاصيل الفيلا**: عرض كامل لمصروفات كل فيلا مع البحث
- **البحث العربي**: بحث كامل في جميع المصروفات عبر الفيلات
- **التقارير**: تقارير حسب الفيلا، التصنيف، والنوع
- **رفع الملفات**: دعم صور الفواتير (JPG, PNG, PDF)
- **RTL كامل**: واجهة عربية بالكامل

---

## 🏗️ هيكل المشروع

```
construction_mgmt/
├── core/                    # إعدادات المشروع
│   ├── settings.py
│   └── urls.py
├── expenses/                # التطبيق الرئيسي
│   ├── models.py            # النماذج (Villa, Expense, etc.)
│   ├── views.py             # العروض
│   ├── forms.py             # النماذج
│   ├── urls.py              # المسارات
│   ├── admin.py             # لوحة الإدارة
│   ├── templatetags/        # فلاتر مخصصة
│   └── management/commands/ # أوامر الإدارة
│       ├── seed_data.py     # البيانات الأولية
│       └── seed_sample.py   # بيانات تجريبية
├── templates/               # القوالب HTML
│   ├── base.html
│   ├── auth/login.html
│   └── expenses/
│       ├── dashboard.html
│       ├── expense_form.html
│       ├── expense_list.html
│       ├── expense_detail.html
│       ├── villa_list.html
│       ├── villa_detail.html
│       ├── global_search.html
│       └── reports.html
└── static/css/main.css      # CSS مخصص
```

---

## 🔢 نموذج البيانات

```
Villa (فيلا)
  └── ExpenseAllocation (تخصيص)
        └── Expense (مصروف)
              └── ExpenseCategory (تصنيف)
```

كل مصروف له رقم مرجع تلقائي (EXP-YYYY-NNNNN) ويمكن توزيعه على عدة فيلات.

---

## 🌐 الصفحات

| المسار | الوصف |
|--------|-------|
| `/` | لوحة التحكم |
| `/expenses/` | قائمة المصروفات |
| `/expenses/add/` | إضافة مصروف |
| `/expenses/<id>/` | تفاصيل مصروف |
| `/expenses/<id>/edit/` | تعديل مصروف |
| `/villas/` | قائمة الفيلات |
| `/villas/<id>/` | تفاصيل فيلا |
| `/search/` | البحث الشامل |
| `/reports/` | التقارير |
| `/admin/` | لوحة الإدارة |
