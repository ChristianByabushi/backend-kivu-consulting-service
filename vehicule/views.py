from django.shortcuts import render
from vehicule.models import Marque, Vehicule
from payement.models import Payement 
from reservation.models import Reservation
from django.shortcuts import render, redirect, get_object_or_404
from .models import Marque, Vehicule
from django.contrib import messages  
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
    marques = Marque.objects.all()
    vehicules = Vehicule.objects.all()
    return render(request, 'garage/vehicules.html',
           {"vehicules":vehicules,"marques":marques,
                                             }) 
def marque_ajouter(request):
    if request.method == 'POST':
        form = MarqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La marque a été créée avec succès!')
            return redirect('marques')
        else:
            errors = form.errors.as_text()
            messages.error(request, f'La création de la marque a échoué. {errors}')
    else:
        form = MarqueForm()
    return render(request, 'garage/forms/ajouterMarque.html', {'form': form}) 


def marque_delete(request, slug):
    marque = get_object_or_404(Marque, slug=slug)
    marque.delete()
    messages.success(request, "La marque a été supprimée avec succès.")
    return redirect('marques') 

def marque_editer(request, slug):
    marque = get_object_or_404(Marque, slug=slug)
    if request.method == 'POST':
        form = MarqueForm(request.POST, instance=marque)
        if form.is_valid():
            form.save()
            messages.success(request, 'La marque a été editée avec succès!')
            return redirect('marques')
        else:
            errors = form.errors.as_text()
            messages.error(request, f'La modification de la marque a échoué. {errors}')
    else:
        form = MarqueForm(instance=marque)
    return render(request, 'garage/forms/editerMarque.html', {'marque': marque}) 

def vehicule_editer(request, numeroplaque):
    vehicule = get_object_or_404(Vehicule, numeroPlaque=numeroplaque)
    if request.method == 'POST':
        form = VehiculeForm(request.POST,request.FILES,  instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicule a été editée avec succès!')
            return redirect('vehicules')
        else:
            errors = form.errors.as_text()
            messages.error(request, f'La modification de la marque a échoué. {errors}')
    else:
        form = VehiculeForm(instance=vehicule) 
    marques=Marque.objects.all()
    return render(request, 'garage/forms/editerVehicule.html', {'vehicule': vehicule,"marques": marques})

                                         
def vehicule_ajouter(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le vehicule  a été créé avec succès!')
            return redirect('vehicules')
        else:
            errors = form.errors.as_text()
            messages.error(request, f'La création du vehicule a échoué. {errors}')
    else:
        form = VehiculeForm() 
    marques=Marque.objects.all()
    return render(request, 'garage/forms/ajouterVehicule.html', {'form': form, "marques":marques}) 

def vehicule_delete(request, numeroplaque):
    vehicule = get_object_or_404(Vehicule, numeroPlaque=numeroplaque)
    vehicule.delete()
    messages.success(request, "Le vehicule a été supprimé avec succès.")
    return redirect('vehicules')


