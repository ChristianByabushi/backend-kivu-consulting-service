from django.urls import path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns = [
    # Marques
    path("", views.index, name="reservations"),
    path("ajouter", views.ajouter, name="ajouter_reservation"),
    path("retirer-vehicule", views.index, name="retirer_reservation"),
    path("editer-vehicule", views.index, name="editer_au_panier"),
    path("supprimer-vehicule", views.index, name="supprimer_au_reservation"),
]
#vehicule_editer

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

