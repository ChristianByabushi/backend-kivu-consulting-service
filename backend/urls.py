from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from user.views import login,logout 
from vehicule.views import index 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login, name='login'),
    path("logout/", logout, name="logout"), 
    path("user/", include("user.urls")), 
    path("garage/", include("vehicule.urls")), 
    path('',index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

