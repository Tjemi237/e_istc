from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Restores the database from a backup file.'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='The path to the backup file to restore from.')

    def handle(self, *args, **options):
        backup_file = os.path.abspath(options['backup_file'])
        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file "{backup_file}" does not exist.')
        
        self.stdout.write(f'Restoring database from {backup_file}...')
        
        call_command('flush', '--no-input')
        call_command('loaddata', backup_file)

        self.stdout.write(self.style.SUCCESS('Successfully restored the database.'))
