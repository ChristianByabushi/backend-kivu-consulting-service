from django.db import models
from vehicule.models import Vehicule 
from vendors.models import Fournisseur
# Create your models here.

class approvisionnement(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT) 
    nbreVehicule = models.IntegerField() 
    pu = models.DecimalField(
        max_digits=10, decimal_places=3, null=False)
    qte = models.DecimalField(max_digits=10,
                                         decimal_places=3, null=False)
    fournisseur = models.ForeignKey(
        Fournisseur, related_name='listesDesVehiculesFournis', on_delete=models.PROTECT, null=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

