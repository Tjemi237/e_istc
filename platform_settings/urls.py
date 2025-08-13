from django.urls import path
from . import views

app_name = 'platform_settings'

urlpatterns = [
    path('', views.platform_settings_view, name='platform_settings'),
]
