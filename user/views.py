from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
import json
from django.http import JsonResponse ,HttpResponse
from django.shortcuts import redirect 
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password, check_password 
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required,login_not_required
from user.models import User
@login_not_required
def login(request):
    if request.user.is_authenticated: 
        return render(request, 'configuration/connected.html')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            error_message = 'Utilisateur ou mot de passe incorrect' 
            return render(request, 'comptes/login.html', {'error_message': error_message})
    return render(request, "comptes/login.html") 

def compte(request):
    context={}
    # if User.objects.filter(id=request.user.id, groups__name='titulaire').exists():
        #  context['listesClasses'] = Classe.objects.filter(titulaire_id=request.user.id).all()
    # context['institution'] = Institution.objects.last()
    return render(request, 'comptes/moncompte.html', context)
def reinitialiserMotDepasseUtilisateur(request, userId):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=userId)
            new_password = "changemoi"  
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Mot de passe réinitialisé avec succès !', 'new_password': new_password})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur introuvable.'})
    else:
        return JsonResponse({'error': 'Requête invalide.'})


def logout_view(request):
    logout(request) 
    return  redirect('login')

def changeMotdepasse(request):
    ancien_pwd = request.POST.get('ancienPwd')
    nouveau_pwd = request.POST.get('nouveauPwd')
    confirm_nouveau_pwd = request.POST.get('confirmnouveauPwd')
    if not all([nouveau_pwd,ancien_pwd, confirm_nouveau_pwd,]):
            return JsonResponse({'success': False, 'message': "Veuillez compléter tous les champs s'il vous plaît."}, status=400)

    if nouveau_pwd != confirm_nouveau_pwd:
        return JsonResponse({'success': False, 'message': 'Les mots de passe ne correspondent pas.'})

    user = request.user
    if not check_password(ancien_pwd, user.password):
        return JsonResponse({'success': False, 'message': 'Ancien mot de passe incorrect.'}, status=200)

    user.password = make_password(nouveau_pwd)
    user.save()
    # messages.success(request, 'Mot de passe modifié avec succès.')
    return JsonResponse({'success': True, 'message': 'Mot de passe modifié avec succès.'})

def editerMoncompte(request):
    if request.method == 'POST':
        noms = request.POST.get('noms')
        login = request.POST.get('login')  
        pwd = request.POST.get('pwd') 
        avatar =  request.FILES.get('avatar') 

        if not all([login, noms, pwd]):
            return JsonResponse({'success': False, 'message': "Veuillez compléter tous les champs s'il vous plaît."}, status=400)

        if not check_password(pwd, request.user.password):
            return JsonResponse({'success': False, 'message': 'Mot de passe incorrect.'}, status=200)

        userAediter = User.objects.get(pk=request.user.id) 
        userAediter.login = login 
        userAediter.noms = noms 
        if avatar:
            userAediter.avatar =avatar
        userAediter.save()
        return JsonResponse({'success': True,  'message': 'Modifications du compte apportee avec succes!'}) 
   

def ajouterUtilisateur(request):
    login = request.POST.get('login')
    noms = request.POST.get('noms')
    role = request.POST.get('role')
    password = request.POST.get('password')
    groups = request.POST.getlist('groups[]')  

    # Create the user
    user = User.objects.create_user(login=login, noms=noms, password=password)  # Replace with your password generation logic
    
    # Set user attributes
    user.role = role
    user.save()


    # Assign user to groups
    for group_id in groups:
        group = Group.objects.get(pk=group_id)
        user.groups.add(group)

    # Redirect or return a success message
    return JsonResponse({'success': True, 'message': 'Utilisateur créé avec succès'})



def modifierrUtilisateur(request, userId):
    try:
        user = User.objects.get(pk=userId)
        groups_string = request.POST.get('login')
        noms = request.POST.get('noms')
        role = request.POST.get('role') 

        user.noms = noms
        user.role = role

        # delete first all user groups
        user.groups.clear()

        # Convert the stringified groups data into a list of group IDs
        groups_string = request.POST.get('groups')
        new_groups = json.loads(groups_string)

        # Add new groups
        for group_id in new_groups:
            group = Group.objects.get(pk=group_id)
            user.groups.add(group)
        user.save()
        return JsonResponse({'success': True, 'message': 'User groups updated successfully'})
        
    except Group.DoesNotExist or User.DoesNotExist :
            return JsonResponse({'success': False, 'message': "Classe non trouvée."}, status=404) 
    

def getUtilisateur(request, userId):
    try:
        userResult = User.objects.get(pk=userId) 
        userGroups=[] 
        for groupe in userResult.groups.all():
            userGroups.append({
                'id':groupe.id,
                'name':groupe.name
            }) 
        output={
            'groups': userGroups, 
            'login':userResult.login,
            'noms':userResult.noms,
            'role': userResult.role,
        }
        
        return JsonResponse({'success': True,  'utilisateur':  output}) 
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': "Utilisateur non trouvée."}, status=404)

def supprimerUtilisateur(request, userId):
    try:
        userAsupprimer = User.objects.get(pk=userId) 
        userAsupprimer.delete() 
        return JsonResponse({'success': True,  'message': 'Utilisateur supprimé avec succès!'}) 
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': "Utilisateur non trouvé."}, status=404)
