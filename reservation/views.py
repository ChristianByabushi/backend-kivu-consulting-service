from django.shortcuts import render, redirect
from .forms import ReservationForm
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation
from contract.models import ContratLocation
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib import messages


def index(request):
    user_request = "reservation"
    contract = request.GET.get("contract", None)
    reservation = request.GET.get("contract", None)

    if reservation:
        reservation = True

    marques = Marque.objects.all()
    tous_les_vehicules = Vehicule.objects.all()
    enlocations = Vehicule.objects.filter(enlocation=True)
    contrats = ContratLocation.objects.all()

    context = {
        "marques": marques,
        "tous_les_vehicules": tous_les_vehicules,
        "enlocations": enlocations,
        "contrats": contrats.filter(reservation__client=request.user),
        "reservations": Reservation.objects.filter(client=request.user),
        "contract": True,
        "reservation": True,
    }
    return render(request, "reservation/index.html", context)

def ajouter(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.client = (
                request.user
            )  
            reservation.statut = "en_attente" 
            reservation.save()
            messages.success(
                request, "Votre réservation a été enregistrée avec succès."
            )
            return redirect("reservations")
        else:
            messages.error(request, "Il y a des erreurs dans le formulaire.") 
            
    else:
        form = ReservationForm()
    return render(
        request,
        "reservation/ajouter.html",
        {"marques": Marque.objects.all(), "tous_les_vehicules": Vehicule.objects.all()},
    )
