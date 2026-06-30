from django.core.management.base import BaseCommand
from django.utils import timezone
from expenses.models import Villa, ExpenseCategory, Expense, ExpenseAllocation
from decimal import Decimal
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed sample expense data for demonstration'

    def handle(self, *args, **options):
        villas = list(Villa.objects.all())
        direct_cats = list(ExpenseCategory.objects.filter(category_type='direct'))
        indirect_cats = list(ExpenseCategory.objects.filter(category_type='indirect'))

        sample_data = [
            ('شراء أسمنت', 'أسمنت', 'direct', 12000, [('V001', 4000), ('V002', 4000), ('V003', 4000)]),
            ('توريد حديد تسليح', 'حديد', 'direct', 25000, [('V001', 10000), ('V002', 8000), ('V003', 7000)]),
            ('شراء طوب أحمر', 'طوب', 'direct', 8500, [('V004', 8500)]),
            ('توريد رمل', 'رمل', 'direct', 3200, [('V001', 1600), ('V002', 1600)]),
            ('سائق نقل مواد', 'سائق', 'indirect', 2000, [('V001', 500), ('V002', 500), ('V003', 500), ('V004', 500)]),
            ('رسوم استشاري هندسي', 'استشاري', 'indirect', 15000, [('V001', 3000), ('V002', 3000), ('V003', 3000), ('V004', 3000), ('V005', 3000)]),
            ('تركيب كهرباء', 'كهرباء', 'direct', 18000, [('V002', 18000)]),
            ('أعمال سباكة', 'سباكة', 'direct', 22000, [('V003', 11000), ('V004', 11000)]),
            ('بنزين وقود', 'بنزين', 'indirect', 1500, [('V001', 300), ('V002', 300), ('V003', 300), ('V004', 300), ('V005', 300)]),
            ('دهانات داخلية', 'دهانات', 'direct', 9500, [('V005', 9500)]),
            ('سيراميك أرضيات', 'سيراميك', 'direct', 35000, [('V001', 12000), ('V002', 12000), ('V006', 11000)]),
            ('أعمال نجارة', 'نجارة', 'direct', 28000, [('V003', 14000), ('V006', 14000)]),
            ('صيانة معدات', 'صيانة', 'indirect', 4500, [('V001', 1500), ('V002', 1500), ('V003', 1500)]),
            ('توريد ألمنيوم', 'ألمنيوم', 'direct', 42000, [('V004', 20000), ('V005', 22000)]),
            ('إيجار معدات', 'إيجار', 'indirect', 8000, [('V002', 4000), ('V004', 4000)]),
            ('أعمال تشطيبات', 'تشطيبات', 'direct', 55000, [('V001', 18000), ('V002', 19000), ('V006', 18000)]),
            ('مصروفات إدارية', 'مصروفات إدارية', 'indirect', 6000, [('V001', 1000), ('V002', 1000), ('V003', 1000), ('V004', 1000), ('V005', 1000), ('V006', 1000)]),
            ('شراء خرسانة', 'خرسانة', 'direct', 65000, [('V005', 32000), ('V006', 33000)]),
        ]

        base_date = date(2026, 1, 1)
        villa_map = {v.code: v for v in villas}
        cat_map = {c.name: c for c in direct_cats + indirect_cats}

        for i, (title, cat_name, exp_type, amount, allocs) in enumerate(sample_data):
            expense_date = base_date + timedelta(days=i * 5)
            cat = cat_map.get(cat_name)
            if not cat:
                continue

            expense = Expense.objects.create(
                title=title,
                category=cat,
                expense_type=exp_type,
                total_amount=Decimal(str(amount)),
                date=expense_date,
            )

            for villa_code, alloc_amount in allocs:
                villa = villa_map.get(villa_code)
                if villa:
                    ExpenseAllocation.objects.create(
                        expense=expense,
                        villa=villa,
                        allocated_amount=Decimal(str(alloc_amount))
                    )

            self.stdout.write(f'تم إنشاء: {expense.reference_number} - {title}')

        self.stdout.write(self.style.SUCCESS(f'تم إنشاء {len(sample_data)} مصروف تجريبي بنجاح!'))
