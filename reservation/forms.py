from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
        labels = {
            'vehicule': 'Choisir le vehicule de votre choix parmi les vehicules disponibles au garage',
            'dateDebut': 'Date de début',
            'dateFin': 'Date de fin',
        }
        
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('dateDebut')
        date_fin = cleaned_data.get('dateFin')

        if date_debut and date_fin:
            if date_fin <= date_debut:
                raise forms.ValidationError("La date de fin doit être supérieure à la date de début.")

        return cleaned_data

