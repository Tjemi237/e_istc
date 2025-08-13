from django.shortcuts import render, redirect
from .models import PlatformSettings
from .forms import PlatformSettingsForm
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def platform_settings_view(request):
    settings, created = PlatformSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = PlatformSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('platform_settings:platform_settings')
        else:
            print(form.errors)
    else:
        form = PlatformSettingsForm(instance=settings)
    return render(request, 'platform_settings/platform_settings.html', {'form': form})