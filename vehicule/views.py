from django.shortcuts import render
from vehicule.models import Marque, Vehicule
from payement.models import Payement 
from reservation.models import Reservation
# Create your views here.
def index(request):
    payements = Payement.objects.all()
    vehicules = Vehicule.objects.all().count
    marques = Marque.objects.all().count
    reservations = Reservation.objects.all()
    return render(request,'dashboard/index.html')