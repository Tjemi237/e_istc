from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import PlatformSettings
from django.core.files.uploadedfile import SimpleUploadedFile

class PlatformSettingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', is_superuser=True)
        self.client.login(username='admin', password='password')

    def test_settings_view_get(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('platform_settings:platform_settings'))
        self.assertEqual(response.status_code, 200)

    def test_settings_view_post(self):
        self.client.login(username='admin', password='password')
        # A valid 1x1 transparent PNG
        logo_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00IHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\xaf\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        logo = SimpleUploadedFile("logo.png", logo_content, content_type="image/png")
        response = self.client.post(reverse('platform_settings:platform_settings'), {
            'primary_color': '#111111',
            'secondary_color': '#222222',
            'logo': logo
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('logo', response.context['form'].errors)