from django.urls import path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns = [
    path("vehicules/", views.index, name="vehicules"),
    path("marques", views.index, name="marques"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

