from django.db import models
from vendors.models import Client  
from vehicule.models import Vehicule

class Reservation(models.Model):
    client = models.ForeignKey(Client,  related_name='listesDesVehiculesFournis', on_delete=models.CASCADE) 
    vehicule = models.ForeignKey(Vehicule,on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now=True) 
    dateFin = models.DateField() 
    sur_commande = models.BooleanField(default=False)
    dateDebut = models.DateField()
    statut = models.CharField(max_length=50, choices=[('en_attente', 'En attente'), ('Approuvee', 'Approuvee'), ('annulee', 'Annulée')]) 
    def __str__(self):
        return f"{self.client.nom}-reservation-{self.date_creation}"
    def get_number_of_days(self):
        if self.dateFin and self.dateDebut:
            delta = self.dateFin - self.dateDebut
            return delta.days + 1 
        return 1
    def calculate_total_price(self):
        number_of_days = self.get_number_of_days()
        if self.vehicule and number_of_days > 0:
            return self.vehicule.prix * number_of_days 
        return 0
    class Meta:
        ordering=['-date_creation'] 
        
    
    