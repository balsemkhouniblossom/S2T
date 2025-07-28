"""training_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.shortcuts import redirect
from . import views
from . import admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Admin Dashboard
    path('admin-dashboard/', admin_views.comprehensive_admin_dashboard, name='comprehensive_admin_dashboard'),
    
    # App URLs
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('formations/', include(('formations.urls', 'formations'), namespace='formations')),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('messaging/', include(('messaging.urls', 'messaging'), namespace='messaging')),
    path('moderation/', include(('moderation.urls', 'moderation'), namespace='moderation')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
    path('forum/', include(('forum.urls', 'forum'), namespace='forum')),
    
    # Redirect common URLs
    path('login/', lambda request: redirect('/users/login/')),
    path('register/', lambda request: redirect('/users/register/')),
    path('dashboard/', lambda request: redirect('/users/dashboard/')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
