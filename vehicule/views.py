from django.shortcuts import render
from vehicule.models import Marque, Vehicule
from payement.models import Payement 
from reservation.models import Reservation
from django.shortcuts import render, redirect, get_object_or_404
from .models import Marque, Vehicule
from .forms import MarqueForm, VehiculeForm
# Create your views here.
def index(request):
    payements = Payement.objects.all()
    vehicules = Vehicule.objects.all().count
    marques = Marque.objects.all().count
    reservations = Reservation.objects.all()
    return render(request,'dashboard/index.html')

def marques(request):
    marques = Marque.objects.all()
    return render(request, 'garage/marques.html',
           {"marques":marques,
                                             })
def vehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'garage/vehicules.html',
           {"vehicules":vehicules,
                                             }) 

def marque_ajouter(request):
    if request.method == 'POST':
        form = MarqueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('marques')
    else:
        form = MarqueForm()
    return render(request, 'marques/create.html', {'form': form})


def marque_editer(request, slug):
    marque = get_object_or_404(Marque, slug=slug)
    if request.method == 'POST':
        form = MarqueForm(request.POST, instance=marque)
        if form.is_valid():
            form.save()
            return redirect('marques')
    else:
        form = MarqueForm(instance=marque)
    return render(request, 'marques/edit.html', {'form': form})


def marque_delete(request, slug):
    marque = get_object_or_404(Marque, slug=slug)
    marque.delete()
    return redirect('marques')
    
