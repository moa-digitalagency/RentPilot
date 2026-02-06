from flask import Blueprint, render_template
from services.verification_service import VerificationService

public_bp = Blueprint('public', __name__)

@public_bp.route('/verify/receipt/<ticket_uuid>', methods=['GET'])
def verify_receipt(ticket_uuid):
    """
    Public route to verify a receipt via QR code.
    Accessible without login.
    """
    verification_data = VerificationService.verify_ticket(ticket_uuid)

    # render_template will fail if template doesn't exist, but that's the next step.
    return render_template('public_verification.html', verification=verification_data)
