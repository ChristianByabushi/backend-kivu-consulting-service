from django.shortcuts import render,redirect
from .forms import ReservationForm
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation 
from contract.models import ContratLocation
from django.contrib.auth.decorators import login_required,login_not_required


def index(request):
    user_request='reservation'

    contract=request.GET.get('contract', None)
    reservation=request.GET.get('contract', None)
    
    if reservation:
        reservation=True 
    
    
    marques = Marque.objects.all()
    tous_les_vehicules= Vehicule.objects.all()
    enlocations = Vehicule.objects.filter(enlocation=True)
    contrats= ContratLocation.objects.all() 
    
    context={
        'marques':marques,
        'tous_les_vehicules':tous_les_vehicules,
        'enlocations':enlocations, 
        'contrats':contrats.filter(reservation__client=request.user),
        'reservations':Reservation.objects.filter(client=request.user),
        'contract':True,
        'reservation':True
    }
    return render(request, 'reservation/index.html',context)

def ajouter(request):
    return redirect('reservation')