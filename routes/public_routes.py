
"""
* Nom de l'application : RentPilot
* Description : Routes for public module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from services.verification_service import VerificationService
# Assuming i18n service is available globally or can be imported.
# Based on main_routes.py, it's imported as 'from services.i18n_service import i18n'
from services.i18n_service import i18n

public_bp = Blueprint('public', __name__)

@public_bp.route('/verify/receipt/<ticket_uuid>', methods=['GET'])
def verify_receipt(ticket_uuid):
    """
    Public route to verify a receipt via QR code.
    Accessible without login.
    """
    verification_data = VerificationService.verify_ticket(ticket_uuid)

    # render_template will fail if template doesn't exist, but that's handled by other steps if needed.
    return render_template('public_verification.html', verification=verification_data)

@public_bp.route('/contact', methods=['POST'])
def contact_submit():
    """
    Handle contact form submission.
    """
    # Simulate data processing
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Simulate email sending (logging for now)
    print(f"Contact Form Submission: Name={name}, Email={email}, Subject={subject}, Message={message}")

    # Flash success message
    flash(i18n.get_text('landing.contact_success'), 'success')

    # Redirect back to the contact section on the landing page
    return redirect(url_for('main.index', _anchor='contact'))