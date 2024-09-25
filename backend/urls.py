from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from user.views import login,logout,register,logout_view
from vehicule.views import index 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login, name='login'),
    path('register/',register, name='register'),
    path("logout/", logout_view, name="logout"), 
    path("user/", include("user.urls")), 
    path("garage/", include("vehicule.urls")), 
    path("reservation/", include("reservation.urls")), 
    path("payements/", include("payement.urls")), 
    path("locations/", include("location.urls")), 
    path('',index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 