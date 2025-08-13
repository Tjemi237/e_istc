"""
URL configuration for e_istc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('comptes/', include('users.urls')),
    path('administration/', include('administration.urls')),
    path('courses/', include('courses.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('forums/', include('forums.urls')),
    path('messaging/', include('messaging.urls')),
    path('notifications/', include('notifications.urls')),
    path('platform_settings/', include('platform_settings.urls')),
    
    path('', user_views.home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
