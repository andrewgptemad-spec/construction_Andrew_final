from django.core.management.base import BaseCommand
from expenses.models import Villa


class Command(BaseCommand):
    help = 'Rename existing villas to the provided standardized names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show the planned renames without saving them'
        )

    def handle(self, *args, **options):
        mapping = {
            'V001': 'RV1G-17D-OWEST',
            'V002': 'RV4G-12D-OWEST',
            'V003': 'RV3-56A-OWEST',
            'V004': 'RV3-64A-OWEST',
            'V005': 'B10-V8-FH',
            'V006': 'B12-V7-FH',
        }

        dry = options.get('dry_run', False)

        for code, new_name in mapping.items():
            try:
                villa = Villa.objects.get(code=code)
            except Villa.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Villa with code {code} not found'))
                continue

            old_name = villa.name
            if dry:
                self.stdout.write(f'{code}: "{old_name}" -> "{new_name}"')
            else:
                villa.name = new_name
                villa.save()
                self.stdout.write(self.style.SUCCESS(f'{code}: "{old_name}" -> "{new_name}"'))
