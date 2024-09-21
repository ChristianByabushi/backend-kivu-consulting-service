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
        
        def clean_image(self):
            image = self.cleaned_data.get('image')
            if not image and self.instance.pk:
                # If no new image is provided, keep the existing image
                return self.instance.image
            return image