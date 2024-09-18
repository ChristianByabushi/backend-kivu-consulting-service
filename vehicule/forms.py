from django import forms
from .models import Marque, Vehicule

class MarqueForm(forms.ModelForm):
    class Meta:
        model = Marque
        fields = '__all__'

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'