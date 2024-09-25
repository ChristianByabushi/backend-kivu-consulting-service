from django.shortcuts import render
from django.contrib.auth.decorators import login_required,login_not_required
from django.shortcuts import render,redirect
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation 
from contract.models import ContratLocation

@login_not_required
def index(request):
    marques = Marque.objects.all()
    tous_les_vehicules= Vehicule.objects.all()
    enlocations = Vehicule.objects.filter(enlocation=True)
    context={
        'marques':marques,
        'tous_les_vehicules':tous_les_vehicules,
        'enlocations':enlocations
    }
    return render(request, 'location/index.html',context)

def ajouter(request):
    return redirect('reservation')
