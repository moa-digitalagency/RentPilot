
"""
* Nom de l'application : RentPilot
* Description : Service logic for pdf module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from services.qr_service import QRService
from models.saas_config import PlatformSettings, ReceiptFormat
from models.finance import Transaction, SaaSInvoice, SaaSInvoiceStatus
from models.users import User
from models.establishment import Room, Lease
from datetime import datetime

class PDFService:

    # CSS for Thermal Printing (if HTML generation is used in future)
    THERMAL_CSS = "@page { size: 80mm auto; margin: 0; }"

    @staticmethod
    def generate_receipt_pdf(transaction, output_buffer: io.BytesIO = None) -> io.BytesIO:
        """
        Generates a PDF receipt for a transaction.
        Adapts format based on PlatformSettings (A4 vs Thermal).
        """
        if output_buffer is None:
            output_buffer = io.BytesIO()

        # Get Settings
        settings = PlatformSettings.query.first()
        fmt = settings.receipt_format if settings else ReceiptFormat.A4_Standard

        # Extract data from ORM object
        ticket_number = transaction.ticket_number
        amount = transaction.amount
        date = transaction.date

        # User info
        user_name = "Unknown User"
        if transaction.payer:
            # User model only has email
            user_name = transaction.payer.email

        # Property info
        property_name = "Unknown Property"
        description = "Paiement"

        if transaction.invoice:
            description = transaction.invoice.description
            if not description:
                description = transaction.invoice.type.value if transaction.invoice.type else "Facture"

            if transaction.invoice.establishment:
                property_name = transaction.invoice.establishment.address

        # Prepare context for rendering
        ctx = {
            'ticket_number': ticket_number,
            'amount': amount,
            'date': date,
            'user_name': user_name,
            'property_name': property_name,
            'description': description
        }

        qr_url = f"https://domaine.com/verify/receipt/{ticket_number}"

        if fmt == ReceiptFormat.Thermal_80mm:
            return PDFService._generate_thermal_receipt(ctx, output_buffer, qr_url)
        else:
            return PDFService._generate_a4_receipt(ctx, output_buffer, qr_url)

    @staticmethod
    def _generate_thermal_receipt(data: dict, buffer: io.BytesIO, qr_url: str) -> io.BytesIO:
        # 80mm width. Height depends on content, but PDF needs fixed page size.
        width = 80 * mm
        height = 250 * mm # Safe height for receipt

        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Margins
        margin = 2 * mm
        y = height - 10 * mm

        # Styles
        c.setFillColor(colors.black)

        # Header
        c.setFont("Courier-Bold", 14)
        c.drawCentredString(width / 2, y, "RentPilot")
        y -= 5 * mm

        c.setFont("Courier", 10)
        c.drawCentredString(width / 2, y, "RECU DE PAIEMENT")
        y -= 8 * mm

        # Separator
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)
        y -= 5 * mm

        # Details
        c.setFont("Courier", 9)
        date_str = str(data.get('date', 'N/A'))
        if len(date_str) > 16:
            date_str = date_str[:16]

        details = [
            f"Ticket: {data.get('ticket_number', 'N/A')}",
            f"Date: {date_str}",
            f"Payeur: {data.get('user_name', 'N/A')}",
            f"Prop: {data.get('property_name', 'N/A')}"
        ]

        for line in details:
            c.drawString(margin, y, line)
            y -= 4 * mm

        y -= 2 * mm

        # Amount
        c.setFont("Courier-Bold", 16)
        amount = data.get('amount', 0.0)
        c.drawCentredString(width / 2, y, f"TOTAL: {amount:.2f} EUR")
        y -= 10 * mm

        # QR Code
        try:
            qr_buffer = QRService.generate_url_qr(qr_url)
            qr_image = ImageReader(qr_buffer)
            qr_size = 40 * mm
            c.drawImage(qr_image, (width - qr_size) / 2, y - qr_size, width=qr_size, height=qr_size)
            y -= qr_size + 5 * mm
        except Exception as e:
            c.setFont("Courier", 8)
            c.drawString(margin, y, "QR Error")
            y -= 5 * mm

        c.setFont("Courier", 8)
        c.drawCentredString(width / 2, y, "Scanner pour verifier")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def _generate_a4_receipt(data: dict, buffer: io.BytesIO, qr_url: str) -> io.BytesIO:
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Copied logic with minor tweaks for QR URL
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkslateblue)
        c.drawString(2 * cm, height - 3 * cm, "RentPilot")

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.gray)
        c.drawString(2 * cm, height - 3.7 * cm, "Reçu de Paiement / Payment Receipt")

        c.setStrokeColor(colors.lightgrey)
        c.line(2 * cm, height - 4.5 * cm, width - 2 * cm, height - 4.5 * cm)

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(2 * cm, height - 6 * cm, f"Reçu #{data.get('ticket_number', 'N/A')}")

        y = height - 7.5 * cm
        line_height = 1.0 * cm

        details = [
            ("Date:", str(data.get('date', 'Unknown'))),
            ("Payeur:", data.get('user_name', 'Unknown User')),
            ("Propriété:", data.get('property_name', 'Unknown Property')),
            ("Description:", data.get('description', '-')),
        ]

        c.setFont("Helvetica", 12)
        for label, value in details:
            c.drawString(2 * cm, y, label)
            c.drawString(6 * cm, y, value)
            y -= line_height

        y -= 1 * cm
        c.setFillColor(colors.whitesmoke)
        c.rect(2 * cm, y - 1.5 * cm, width - 4 * cm, 2 * cm, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(3 * cm, y - 0.5 * cm, "Montant Total / Total Amount")

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.darkgreen)
        amount = data.get('amount', 0.0)
        c.drawRightString(width - 3 * cm, y - 0.5 * cm, f"{amount:.2f} €")

        # QR Code
        try:
            qr_buffer = QRService.generate_url_qr(qr_url)
            qr_image = ImageReader(qr_buffer)
            c.drawImage(qr_image, width - 7 * cm, 3 * cm, width=4 * cm, height=4 * cm)

            c.setFont("Helvetica", 8)
            c.setFillColor(colors.gray)
            c.drawString(width - 7 * cm, 2.5 * cm, "Scan to verify transaction")
        except Exception:
            pass

        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.gray)
        c.drawCentredString(width / 2, 1.5 * cm, "Généré automatiquement par RentPilot")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_admin_stats_pdf(period: tuple) -> io.BytesIO:
        """
        Generates a PDF report for Super Admin stats.
        period: (start_date, end_date)
        """
        start_date, end_date = period
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Stats Calculation
        # 1. Revenues (Paid SaaS Invoices)
        revenue = 0.0
        paid_invoices = SaaSInvoice.query.filter(
            SaaSInvoice.status == SaaSInvoiceStatus.PAID,
            SaaSInvoice.paid_at >= start_date,
            SaaSInvoice.paid_at <= end_date
        ).all()
        for inv in paid_invoices:
            revenue += inv.amount

        # 2. New Users
        new_users_count = User.query.filter(
            User.created_at >= start_date,
            User.created_at <= end_date
        ).count()

        # 3. Occupancy Rate
        total_rooms = Room.query.count()
        occupied_rooms = Room.query.filter_by(is_vacant=False).count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0.0

        # Draw PDF
        c.setFont("Helvetica-Bold", 24)
        c.drawString(2 * cm, height - 3 * cm, "Rapport Super Admin")

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, height - 4 * cm, f"Période: {start_date} - {end_date}")

        y = height - 6 * cm

        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "Indicateurs Clés (KPI)")
        y -= 1.5 * cm

        stats = [
            f"Revenus Totaux: {revenue:.2f} €",
            f"Nouveaux Utilisateurs: {new_users_count}",
            f"Taux d'Occupation Global: {occupancy_rate:.1f}% ({occupied_rooms}/{total_rooms})"
        ]

        c.setFont("Helvetica", 12)
        for stat in stats:
            c.drawString(3 * cm, y, "- " + stat)
            y -= 1 * cm

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_lease_pdf(lease: Lease) -> io.BytesIO:
        """
        Generates a generic Lease PDF (Contract).
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        tenant = lease.tenant
        room = lease.room
        establishment = room.establishment

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 3 * cm, "CONTRAT DE BAIL")

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 4 * cm, f"Référence: LEASE-{lease.id}")

        y = height - 6 * cm
        line_height = 0.8 * cm

        # Parties
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "ENTRE LES SOUSSIGNÉS:")
        y -= 1.5 * cm

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "LE BAILLEUR (Propriétaire):")
        # Assuming we can get owner info, but EstablishmentOwner links to User.
        # For now, we use generic text or fetch if available.
        # Simple implementation:
        c.drawString(2 * cm, y - line_height, "Représenté par l'administration du bien (RentPilot)")
        y -= 2.5 * cm

        c.drawString(2 * cm, y, "ET LE PRENEUR (Locataire):")
        c.drawString(2 * cm, y - line_height, f"Nom/Email: {tenant.email}")
        if tenant.is_identity_verified:
             c.drawString(2 * cm, y - 2*line_height, "(Identité Vérifiée)")
        y -= 3 * cm

        # Object
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "OBJET DU CONTRAT:")
        y -= 1.5 * cm

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "Location d'une chambre meublée située à:")
        c.drawString(2 * cm, y - line_height, f"Adresse: {establishment.address}")
        c.drawString(2 * cm, y - 2*line_height, f"Chambre: {room.name}")
        y -= 3 * cm

        # Conditions
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "CONDITIONS FINANCIERES:")
        y -= 1.5 * cm

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, f"Loyer Mensuel: {room.base_price} EUR")
        c.drawString(2 * cm, y - line_height, "Charges: Selon consommation (ou forfait défini)")
        c.drawString(2 * cm, y - 2*line_height, f"Date d'effet: {lease.start_date.strftime('%d/%m/%Y')}")
        if lease.end_date:
            c.drawString(2 * cm, y - 3*line_height, f"Date de fin: {lease.end_date.strftime('%d/%m/%Y')}")

        y -= 5 * cm

        # Signatures
        c.drawString(2 * cm, y, "Fait à ______________________, le ______________________")
        y -= 2 * cm

        c.drawString(3 * cm, y, "Signature du Bailleur")
        c.drawString(12 * cm, y, "Signature du Locataire")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
