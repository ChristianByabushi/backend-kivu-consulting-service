from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('kcs/api/', include('djoser.urls')),
    path('kcs/api/', include('djoser.urls.authtoken')),
    path('kcs/api/', include('management.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
