from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['vehicule', 'dateDebut', 'dateFin'] 
        labels = {
            'vehicule': 'Choisir le vehicule de votre choix parmi les vehicules disponibles au garage',
            'dateDebut': 'Date de début',
            'dateFin': 'Date de fin',
        }
        
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("dateDebut")
        date_fin = cleaned_data.get("dateFin")

        if date_debut and date_fin:
            if date_debut > date_fin:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")
        
        return cleaned_data

