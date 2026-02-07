
"""
* Nom de l'application : RentPilot
* Description : Service logic for verification module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from models.finance import Transaction
from models.establishment import Establishment

class VerificationService:
    @staticmethod
    def verify_ticket(ticket_number: str) -> dict:
        """
        Verifies a ticket number and returns a safe DTO.
        """
        transaction = Transaction.query.filter_by(ticket_number=ticket_number).first()

        if not transaction:
            return None

        # Base DTO
        dto = {
            "ticket_number": transaction.ticket_number,
            "amount": transaction.amount,
            "status": transaction.validation_status.value if transaction.validation_status else "Unknown",
            "timestamp": transaction.date.isoformat() if transaction.date else None,
            "purpose": "Paiement",
            "issuer": "RentPilot"
        }

        # Enrich info
        if transaction.invoice:
            # Purpose from invoice
            description = transaction.invoice.description
            if not description:
                # Use type
                description = f"Paiement {transaction.invoice.type.value}" if transaction.invoice.type else "Facture"
            dto["purpose"] = description

            # Issuer from establishment
            if transaction.invoice.establishment:
                # No name field, using address
                # Be careful not to expose too much if address is private?
                # But "Nom Etablissement" usually implies a business name.
                # Since we don't have it, we'll use "Propriété"
                dto["issuer"] = "Propriété"

        return dto