from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from user.views import login, logout, register, logout_view
from payement.views import *
from vehicule.views import (
    index,
    voir_panier,
    ajouter_dans_panier,
    retirer_dans_panier,
)

from contract.views import *

from location.views import index
from location.views import montrer_vehicules_a_louer
urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
    path("user/", include("user.urls")),
    path("garage/", include("vehicule.urls")),
    path("mes-reservations/", include("reservation.urls")),
    path("payements/", include("payement.urls")),
    path("", index, name="index"),
    
    
    # locations
    path("voir-le-panier/", voir_panier, name="panier"),
    path("vehicules-a-louer/", montrer_vehicules_a_louer, name="montrer_vehicules_a_louer"),
    path("mes-vehicules-loués/", contrat_des_reservations, name="locations"), 
    path("mes-vehicules-loués/ajouter/", ajout_contrat_des_reservations, name="ajout_contrat_des_reservations"), 
    path("mes-vehicules-loués/commande/print/<int:idContrat>/", generate_pdf_contrat_commande, name="generate_pdf_contrat_commande"), 
    
    
    #payements generate_pdf_facture
    path("payements/", generate_pdf_contrat_commande, name="generate_pdf_contrat_commande"), 
    path("payements/print/<int:idPayement>/", generate_pdf_facture, name="generate_pdf_facture"), 
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
