from django.db import models
from reservation.models import Reservation  
from vendors.models import Client  
from datetime import datetime
class ContratLocation(models.Model):
    reservation = models.ManyToManyField(Reservation) 
    date_signature = models.DateField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField() 
    
    def __str__(self):
        return f"Contract Vehicule#{self.id}"