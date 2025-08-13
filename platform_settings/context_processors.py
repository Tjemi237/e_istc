from .models import PlatformSettings

def platform_settings(request):
    settings, created = PlatformSettings.objects.get_or_create(pk=1)
    return {'platform_settings': settings}
