from django.urls import path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns = [
    # Marques
    path("", views.index, name="reservations"),
    path("ajout-vehicule-au-panier", views.index, name="ajouter_au_panier"),
    path("retirer-vehicule-au-panier", views.index, name="retirer_au_panier"),
    path("editer-vehicule-au-panier", views.index, name="editer_au_panier"),
    path("supprimer-vehicule-au-panier", views.index, name="supprimer_au_panier"),
]
#vehicule_editer

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

