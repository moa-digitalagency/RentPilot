import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_receipt(transaction, output_folder):
    """
    Generates a PDF receipt for a transaction.

    Args:
        transaction: Transaction object (with relationships to user, invoice/expense).
        output_folder: Path to save the PDF.

    Returns:
        str: File path of the generated PDF.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = f"receipt_{transaction.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(output_folder, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Reçu de Paiement - RentPilot", styles['Title']))
    elements.append(Spacer(1, 12))

    # Info
    # Check if transaction.payer (User) exists and has email
    payer_email = transaction.payer.email if transaction.payer else "Inconnu"
    amount = f"{transaction.amount:.2f} €"
    date_str = transaction.date.strftime('%d/%m/%Y') if transaction.date else "N/A"
    status = transaction.validation_status.value if transaction.validation_status else "N/A"

    data = [
        ["ID Transaction", str(transaction.id)],
        ["Date", date_str],
        ["Payeur", payer_email],
        ["Montant", amount],
        ["Statut", status]
    ]

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(t)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph("Ce document vaut preuve de paiement sous réserve de validation finale par le bailleur.", styles['Normal']))

    doc.build(elements)

    return filepath
