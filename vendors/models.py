from django.db import models
from user.models import User
from user.models import User


class Fournisseur(models.Model):
    nom = models.CharField(max_length=255, null=False)
    numeroTel = models.CharField(max_length=30, null=True)
    adresse = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Fournisseur-{self.name}.{self.id}"

class Client(User):
    nom = models.CharField(max_length=255)
    numeroTel = models.CharField(max_length=30, null=True)
    adresse = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"Client-{self.name}.{self.id}"

