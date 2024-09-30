from django.shortcuts import render
from django.contrib.auth.decorators import login_required, login_not_required
from django.shortcuts import render, redirect
from vehicule.models import Marque, Vehicule
from reservation.models import Reservation
from contract.models import ContratLocation
from django.db.models import F, ExpressionWrapper, DecimalField, IntegerField, Sum 
from django.db.models import F, ExpressionWrapper, DecimalField, DurationField
from django.db.models.functions import Cast
from django.contrib import messages
from django.shortcuts import render
from datetime import datetime
def contrat_des_reservations(request):
    marques = Marque.objects.all()
    tous_les_vehicules = Vehicule.objects.all()
    enlocations = ContratLocation.objects.filter(
        reservation__client=request.user, reservation__statut="Approuvee"
    ).distinct()

    context = {
        "marques": marques,
        "tous_les_vehicules": tous_les_vehicules,
        "enlocations": enlocations,
    }
    return render(request, "location/index.html", context)



def ajout_contrat_des_reservations(request):
    reservations = Reservation.objects.filter(
        client=request.user, sur_commande=False, statut='Approuvee'
    )

    if request.method == 'POST':
        listesReservations = request.POST.getlist('imagecheck') 
        total_montant_commande = 0
        contrat = ContratLocation()  
        contrat.montant_total=total_montant_commande
        contrat.save()  
        for reservationId in listesReservations:
            print(reservationId)
            reservation = Reservation.objects.filter(pk=reservationId).first() 
            if reservation:
                reservation.sur_commande = True 
                reservation.save()  
                total_montant_commande += reservation.calculate_total_price()  
                contrat.reservation.add(reservation)  
        contrat.montant_total = total_montant_commande
      
        contrat.description = f"{len(listesReservations)} véhicules en bon état commandés par Monsieur/Madame {request.user.first_name}, {request.user.email}, lié à une commande des   réserves disponibles dans notre garage en date du {datetime.now().strftime('%Y-%m-%d')}. Il est dès lors demandé au présent client de se rendre à nos assises sur Avenue Vamaro Numéro 22, dans les 3 jours suivant l'élaboration de cette commande, sinon l'entreprise Kivu Consulting se trouvera dans l'obligation de l'annuler."
        contrat.save()  

        messages.success(request, "Votre commande a été enregistrée avec succès, Merci de nous avoir fait confiance!") 
        return redirect("locations")
    
    return render(request, "location/ajouterCommande.html", {
        'reservations': reservations
    })



from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
import os
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings

def generate_pdf_contrat_commande(request, idContrat): 
    contrat =  ContratLocation.objects.filter(pk=idContrat).first()
    if contrat:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Contrat-Commande-{contrat.id}#client{contrat.reservation.first().client.nom}.pdf"'

        pdf = SimpleDocTemplate(
            response,
            pagesize=A4,
        )
        
        logo_path = os.path.join(settings.BASE_DIR, 'static/assets/img/logokcs.jpg')
        print(logo_path)
        
        elements = []

        # Add logo to the document
        if os.path.exists(logo_path):
            logo = Image(logo_path, 2 * inch, 1 * inch)
            elements.append(logo)
        
        # Add company and document title
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.alignment = TA_CENTER
        
        elements.append(Paragraph('Kivu Consulting Service', title_style))
        elements.append(Paragraph(f'Contrat de Commande N° {contrat.id}', title_style))
        elements.append(Spacer(1, 12))
        
        # Add date and user information
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Paragraph(f"Client: {contrat.reservation.first().client.nom}, {contrat.reservation.first().client.email}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Table Header for Reservations
        reservation_data = [['Véhicule', 'Date Début', 'Date Fin', 'Prix par jour', 'Total']]
        
        # Fetch each reservation from the contract
        for reservation in contrat.reservation.all():
            vehicule = reservation.vehicule
            total_price = reservation.calculate_total_price()
            reservation_data.append([
                vehicule.__str__(),  # Vehicule description
                reservation.dateDebut.strftime('%Y-%m-%d'),
                reservation.dateFin.strftime('%Y-%m-%d'),
                f"{vehicule.prix} $",
                f"{total_price} $"
            ])
        
        table = Table(reservation_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Montant total: {contrat.montant_total} $", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph(f"Description: {contrat.description}", styles['Normal']))
        
        pdf.build(elements)
        
        return response
    else:
        return HttpResponse('Desole le contrat de commande est introuvable')


