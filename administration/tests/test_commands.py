from django.test import TestCase
from django.core.management import call_command
from io import StringIO

class ManagementCommandsTest(TestCase):
    def test_maintenance_command(self):
        out = StringIO()
        call_command('maintenance', stdout=out)
        self.assertIn('Migrations applied successfully.', out.getvalue())
        self.assertIn('Static files collected successfully.', out.getvalue())
        self.assertIn('Maintenance tasks completed.', out.getvalue())
