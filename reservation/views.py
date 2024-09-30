from django.shortcuts import render, redirect
from .forms import ReservationForm
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation
from contract.models import ContratLocation
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib import messages


def index(request):
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
    }
    return render(request, "reservation/index.html", context)

def index(request):
    # Get all possible options
    marques = Marque.objects.all()
    tous_les_vehicules = Vehicule.objects.all()

    # Get the filter parameters from GET request
    statut = request.GET.get('statut')
    debut_date = request.GET.get('debutDate')
    fin_date = request.GET.get('dateFin')
    marque_id = request.GET.get('marque')
    vehicule_id = request.GET.get('vehicule')

    # Start with all reservations for the current user
    reservations = Reservation.objects.filter(client=request.user)

    # Apply filters if they exist
    if statut:
        reservations = reservations.filter(statut=statut)
    if debut_date:
        reservations = reservations.filter(dateDebut__gte=debut_date)
    if fin_date:
        reservations = reservations.filter(dateFin__lte=fin_date)
    if marque_id:
        reservations = reservations.filter(vehicule__marque_id=marque_id)
    if vehicule_id:
        reservations = reservations.filter(vehicule_id=vehicule_id)

    # Other filtering logic for enlocations and contrats
    enlocations = Vehicule.objects.filter(enlocation=True)
    contrats = ContratLocation.objects.filter(reservation__client=request.user)

    context = {
        "marques": marques,
        "tous_les_vehicules": tous_les_vehicules,
        "enlocations": enlocations,
        "contrats": contrats,
        "reservations": reservations,
        "filters": request.GET,  # Pass the filters back to template
    }
    
    return render(request, "reservation/index.html", context)


def ajouter(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.client = request.user.client
            reservation.statut = "en_attente"
            reservation.save()
            messages.success(
                request, "Votre réservation a été enregistrée avec succès, veuillez svp attendre l'approbation."
            )
            return redirect("reservations")
        else:
            errors = form.errors.as_text()
            messages.error(request, f"{errors}") 
    else:
        form = ReservationForm() 
    return render(
        request,
        "reservation/ajouter.html",
        {
            "marques": Marque.objects.all(),
            "tous_les_vehicules": Vehicule.objects.all(),
            "form": form
        },
    )
