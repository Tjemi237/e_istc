from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Runs maintenance tasks: migrate and collectstatic.'

    def handle(self, *args, **options):
        self.stdout.write('Running database migrations...')
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Migrations applied successfully.'))

        self.stdout.write('Collecting static files...')
        call_command('collectstatic', '--no-input')
        self.stdout.write(self.style.SUCCESS('Static files collected successfully.'))

        self.stdout.write(self.style.SUCCESS('Maintenance tasks completed.'))
