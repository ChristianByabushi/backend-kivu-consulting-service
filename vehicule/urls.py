from django.urls import path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns = [
    # Marques
    path("marques/", views.marques, name="marques"),
    path("marques/ajouter/", views.marque_ajouter, name="marque_ajouter"),
    path("marques/editer/<int:pk>/", views.marque_editer, name="marque_update"),
    path("marques/supprimer/<int:pk>/", views.marque_delete, name="marque_delete"),

    # Véhicules
    path("vehicules/", views.vehicules, name="vehicules"),
    # path("vehicules/ajouter/", views.vehicule_create, name="vehicule_create"),
    # path("vehicules/editer/<int:pk>/", views.vehicule_update, name="vehicule_update"),
    # path("vehicules/supprimer/<int:pk>/", views.vehicule_delete, name="vehicule_delete"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

