from django import forms
from .models import Marque, Vehicule

class MarqueForm(forms.ModelForm):
    nom = forms.CharField(error_messages={'required': 'Le nom de la marque est vide!!'})
    description = forms.CharField(error_messages={'required': 'La description de la marque est vide!!'})
    slug = forms.CharField(error_messages={'required': 'Le slug de la marque est vide!!'})
    class Meta:
        model = Marque
        fields = '__all__'

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'