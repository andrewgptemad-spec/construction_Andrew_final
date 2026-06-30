from django.core.management.base import BaseCommand
from expenses.models import ExpenseCategory


class Command(BaseCommand):
    help = 'Add specific expense categories if they do not already exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show categories that would be created without saving'
        )

    def handle(self, *args, **options):
        categories = [
            ('تكييف', 'direct'),
            ('رخام', 'direct'),
            ('بورسلين', 'direct'),
            ('مصاعد', 'direct'),
        ]

        dry = options.get('dry_run', False)

        for name, ctype in categories:
            exists = ExpenseCategory.objects.filter(name=name, category_type=ctype).exists()
            if exists:
                self.stdout.write(self.style.WARNING(f'Exists: {name} ({ctype})'))
                continue

            if dry:
                self.stdout.write(f'Would create: {name} ({ctype})')
            else:
                ExpenseCategory.objects.create(name=name, category_type=ctype)
                self.stdout.write(self.style.SUCCESS(f'Created: {name} ({ctype})'))
