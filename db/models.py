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
        
        


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to='images/avatar/', default='/images/avatar/avatar.png')
    role = models.CharField(max_length=10, null=True, default='Client')

    USERNAME_FIELD = 'email'
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None
    
    def __str__(self):
        return f"{self.id}-{self.email}"
        



class Client(User):
    nom = models.CharField(max_length=255)
    numeroTel = models.CharField(max_length=30, null=True)
    adresse = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"Client-{self.nom}.{self.id}"
    
class Reservation(models.Model):
    client = models.ForeignKey(Client,  related_name='listesDesVehiculesFo', on_delete=models.CASCADE) 
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


from datetime import datetime
class ContratLocation(models.Model):
    reservation = models.ManyToManyField(Reservation) 
    date_signature = models.DateField(default=datetime.now)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()  
    pret=models.BooleanField(default=False)
    
    def __str__(self):
        return f"Contract Vehicule#{self.id}"
    
class Payement(models.Model):
    contrat = models.ForeignKey(ContratLocation, on_delete=models.CASCADE)
    mode_paiement = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    receveur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_paiement = models.DateTimeField(default=datetime.now) 


    
    

    