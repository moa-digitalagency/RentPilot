import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from services.qr_service import QRService
from reportlab.lib.utils import ImageReader

class PDFService:
    @staticmethod
    def generate_receipt(transaction_data: dict, output_buffer: io.BytesIO = None) -> io.BytesIO:
        """
        Generates a PDF receipt for a transaction.

        :param transaction_data: Dict containing:
            - id: int
            - user_name: str
            - user_id: int
            - amount: float
            - date: str
            - property_name: str
            - description: str
        :param output_buffer: Optional BytesIO buffer to write to.
        :return: The BytesIO buffer containing the PDF.
        """
        if output_buffer is None:
            output_buffer = io.BytesIO()

        c = canvas.Canvas(output_buffer, pagesize=A4)
        width, height = A4

        # --- Header ---
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkslateblue)
        c.drawString(2 * cm, height - 3 * cm, "RentPilot")

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.gray)
        c.drawString(2 * cm, height - 3.7 * cm, "Reçu de Paiement / Payment Receipt")

        # --- Separator ---
        c.setStrokeColor(colors.lightgrey)
        c.line(2 * cm, height - 4.5 * cm, width - 2 * cm, height - 4.5 * cm)

        # --- Details ---
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(2 * cm, height - 6 * cm, f"Reçu #{transaction_data.get('id', 'N/A')}")

        y = height - 7.5 * cm
        line_height = 1.0 * cm

        details = [
            ("Date:", str(transaction_data.get('date', 'Unknown'))),
            ("Payeur:", transaction_data.get('user_name', 'Unknown User')),
            ("Propriété:", transaction_data.get('property_name', 'Unknown Property')),
            ("Description:", transaction_data.get('description', '-')),
        ]

        c.setFont("Helvetica", 12)
        for label, value in details:
            c.drawString(2 * cm, y, label)
            c.drawString(6 * cm, y, value)
            y -= line_height

        # --- Amount Box ---
        y -= 1 * cm
        c.setFillColor(colors.whitesmoke)
        c.rect(2 * cm, y - 1.5 * cm, width - 4 * cm, 2 * cm, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(3 * cm, y - 0.5 * cm, "Montant Total / Total Amount")

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.darkgreen)
        amount = transaction_data.get('amount', 0.0)
        c.drawRightString(width - 3 * cm, y - 0.5 * cm, f"{amount:.2f} €")

        # --- QR Code ---
        # Generate QR
        try:
            qr_buffer = QRService.generate_qr_code(
                transaction_id=transaction_data.get('id', 0),
                user_id=transaction_data.get('user_id', 0),
                amount=amount
            )
            qr_image = ImageReader(qr_buffer)
            # Draw QR at bottom right
            c.drawImage(qr_image, width - 7 * cm, 3 * cm, width=4 * cm, height=4 * cm)

            c.setFont("Helvetica", 8)
            c.setFillColor(colors.gray)
            c.drawString(width - 7 * cm, 2.5 * cm, "Scan to verify transaction")
        except Exception as e:
            c.drawString(2 * cm, 2 * cm, f"Error generating QR: {str(e)}")

        # --- Footer ---
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.gray)
        c.drawCentredString(width / 2, 1.5 * cm, "Généré automatiquement par RentPilot")

        c.showPage()
        c.save()

        output_buffer.seek(0)
        return output_buffer
