from django.db import models 
from contract.models import Contrat 
from user.models import User
# Create your models here.
class Payement(models.Model):
    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE)
    mode_paiement = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    receveur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_paiement = models.DateField() 
     
