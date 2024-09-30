from django.db import models 
from contract.models import ContratLocation 
from user.models import User
from datetime import datetime

class Payement(models.Model):
    contrat = models.ForeignKey(ContratLocation, on_delete=models.CASCADE)
    mode_paiement = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    receveur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_paiement = models.DateTimeField(default=datetime.now)
    
    