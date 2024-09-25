from django.db import models
class Marque(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=False, null=False)
    slug = models.SlugField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return f"/{self.slug}" 
    
class Vehicule(models.Model):
    numeroPlaque = models.CharField(max_length=255, unique=True)
    marque = models.ForeignKey(
        Marque, related_name="vehicules", on_delete=models.SET_NULL, null=True
    ) 
    modele = models.CharField(max_length=255) 
    anneeAchat = models.IntegerField() 
    motorisation = models.CharField(max_length=255)
    poids = models.CharField(max_length=255) 
    couleur = models.CharField(max_length=255) 
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    enlocation = models.BooleanField(default=False)
    image = models.ImageField(upload_to="vehicules/", blank=True)
    created_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f'{self.marque}--{self.modele}--{self.numeroPlaque}'

    def get_image(self):
        if self.image:
            return self.image.url 
        



