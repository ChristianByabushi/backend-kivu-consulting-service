from django.db import models
from reservation.models import Reservation  

class Contrat(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    date_signature = models.DateField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField() 
