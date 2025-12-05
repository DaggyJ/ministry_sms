"""
URL configuration for ministry_sms project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import os
from accounts.views import admin_users_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('smsapp.urls', namespace='smsapp')),
    path('accounts/', include('accounts.urls', namespace='accounts')),  
    path('admin-users-list/', admin_users_list, name='admin_users_list'),

]


# Only for development server
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=os.path.join(settings.BASE_DIR, 'static'))

