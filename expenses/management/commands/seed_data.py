from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Villa, ExpenseCategory


class Command(BaseCommand):
    help = 'Seed initial data: villas and expense categories'

    def handle(self, *args, **options):
        self.stdout.write('جاري إنشاء البيانات الأولية...')

        # Create superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@example.com'
            )
            self.stdout.write(self.style.SUCCESS('تم إنشاء المستخدم admin بكلمة مرور admin123'))

        # Create villas
        villas = [
            {'name': 'فيلا 1', 'code': 'V001'},
            {'name': 'فيلا 2', 'code': 'V002'},
            {'name': 'فيلا 3', 'code': 'V003'},
            {'name': 'فيلا 4', 'code': 'V004'},
            {'name': 'فيلا 5', 'code': 'V005'},
            {'name': 'فيلا 6', 'code': 'V006'},
        ]
        for v in villas:
            villa, created = Villa.objects.get_or_create(
                code=v['code'],
                defaults={'name': v['name']}
            )
            if created:
                self.stdout.write(f'تم إنشاء: {villa.name}')

        # Direct categories
        direct_cats = [
            'أسمنت', 'حديد', 'طوب', 'رمل', 'سن',
            'خرسانة', 'كهرباء', 'سباكة', 'محارة', 'دهانات',
            'تشطيبات', 'نجارة', 'ألمنيوم', 'سيراميك', 'تجهيزات', 'أخرى'
        ]
        for name in direct_cats:
            cat, created = ExpenseCategory.objects.get_or_create(
                name=name, category_type='direct'
            )
            if created:
                self.stdout.write(f'تصنيف مباشر: {cat.name}')

        # Indirect categories
        indirect_cats = [
            'سائق', 'استشاري', 'إيجار', 'بنزين', 'صيانة',
            'خدمات', 'أدوات', 'مواصلات', 'مصروفات إدارية', 'تجهيزات', 'أخرى'
        ]
        for name in indirect_cats:
            cat, created = ExpenseCategory.objects.get_or_create(
                name=name, category_type='indirect'
            )
            if created:
                self.stdout.write(f'تصنيف غير مباشر: {cat.name}')

        self.stdout.write(self.style.SUCCESS('اكتملت عملية إنشاء البيانات الأولية بنجاح!'))
