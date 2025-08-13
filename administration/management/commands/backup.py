from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Backs up the database'

    def handle(self, *args, **options):
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')

        with open(backup_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata', '--exclude=contenttypes', '--exclude=auth.Permission', '--indent=2', stdout=f)

        self.stdout.write(self.style.SUCCESS(f'Successfully backed up the database to {backup_file}.'))
