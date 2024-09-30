from django.shortcuts import render
from django.contrib.auth.decorators import login_required,login_not_required
from django.shortcuts import render,redirect
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation 
from contract.models import ContratLocation

@login_required
def index(request):
    marques = Marque.objects.all()
    tous_les_vehicules= Vehicule.objects.all()
    enlocations = ContratLocation.objects.filter(reservation__client=request.user.id).distinct()
    context={
        'marques':marques,
        'tous_les_vehicules':tous_les_vehicules,
        'enlocations':enlocations
    }
    return render(request, 'location/index.html',context)

def montrer_vehicules_a_louer(request):
    marques = Marque.objects.all()
    tous_les_vehicules= Vehicule.objects.all()
    enlocations = ContratLocation.objects.filter(reservation__client=request.user.id).distinct()
    context={
        'marques':marques,
        'tous_les_vehicules':tous_les_vehicules,
        'enlocations':enlocations
    }
    return render(request, 'alouer/index.html',context)


@login_required
def ajouter(request):
    return redirect('reservation')
