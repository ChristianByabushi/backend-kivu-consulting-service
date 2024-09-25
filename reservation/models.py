from django.db import models
from vendors.models import Client  
from vehicule.models import Vehicule

class Reservation(models.Model):
    client = models.ForeignKey(Client,  related_name='listesDesVehiculesFournis', on_delete=models.CASCADE) 
    vehicule = models.ForeignKey(Vehicule,on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now=True) 
    dateFin = models.DateField() 
    confirmed = models.BooleanField(default=True)
    dateDebut = models.DateField()
    statut = models.CharField(max_length=50, choices=[('en_attente', 'En attente'), ('confirmee', 'Confirmée'), ('annulee', 'Annulée')]) 
