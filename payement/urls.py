from django.urls import path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns = [
    # Marques
    path("", views.index, name="payements"),
]
#vehicule_editer

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

