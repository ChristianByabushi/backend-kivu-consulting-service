from django.shortcuts import render
from payement.models import Payement
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.enums import TA_CENTER
import os
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings


def index(request):
    debut_date = request.GET.get("debutDate")
    date_fin = request.GET.get("dateFin")
    
    payements = Payement.objects.filter(
        contrat__reservation__client=request.user, 
        
    ).distinct()

    if debut_date and date_fin:
        try:
            debut_date_obj = datetime.strptime(debut_date, "%Y-%m-%d").date()
            date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d").date()

            payements = payements.filter(
                contrat__date_signature__range=(debut_date_obj, date_fin_obj)
            )
        except ValueError:
            pass  
        
    return render(request, "payement/index.html", {
        "payements": payements,
        "filters": {
            "debutDate": debut_date,
            "dateFin": date_fin
        }
    })


def generate_pdf_facture(request, idPayement):
    payement = Payement.objects.filter(pk=idPayement).first()
    print(datetime.now)
    if payement:
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="payement-{payement.id}#client{payement.contrat.reservation.first().client.nom}.pdf"'
        )

        pdf = SimpleDocTemplate(
            response,
            pagesize=A4,
        )

        logo_path = os.path.join(settings.BASE_DIR, "static/assets/img/logokcs.jpg")
        print(logo_path)

        elements = []

        # Add logo to the document
        if os.path.exists(logo_path):
            logo = Image(logo_path, 2 * inch, 1 * inch)
            elements.append(logo)

        # Add company and document title
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER

        elements.append(Paragraph("Kivu Consulting Service", title_style))
        elements.append(Paragraph(f"Payement N° {payement.id}", title_style))
        elements.append(Spacer(1, 12))

        # Add date and user information
        elements.append(
            Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"])
        )
        elements.append(
            Paragraph(
                f"Client: {payement.contrat.reservation.first().client.nom}, {payement.contrat.reservation.first().client.email}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 12))

        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(
                f"La presente temoigne le paiement du client et invite lentreprise de bien vouloir livre les vehicules au fournisseur, celui-ci apres avoir accepte leur etat sengage de bien vouloir les retourner en bon etat et de signaler en cas de probleme tout prejudice avec des preuves (images), heures et tout autre digne de confiance.",
                styles["Normal"],
            )
        )

        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(f"Montant total: {payement.montant} $", styles["Normal"])
        )
        elements.append(Spacer(1, 12))

        elements.append(
            Paragraph(f"Mode de paiement: {payement.date_paiement}", styles["Normal"])
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph(
                f"Fait à Bukavu le {datetime.now().strftime('%Y-%m-%d')}",
                styles["Normal"],
            )
        )
        pdf.build(elements)

        return response
    else:
        return HttpResponse("Desole ce payement est introuvable")
