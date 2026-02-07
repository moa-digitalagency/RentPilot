
"""
* Nom de l'application : RentPilot
* Description : Routes for public module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from services.verification_service import VerificationService
from services.i18n_service import i18n
from models import PlatformSettings

public_bp = Blueprint('public', __name__)

@public_bp.route('/sw.js')
def service_worker():
    response = current_app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@public_bp.route('/manifest.json')
def manifest():
    """
    Dynamic PWA Manifest.
    """
    settings = PlatformSettings.query.first()
    if not settings or not settings.pwa_enabled:
        return jsonify({}), 404

    # Default values
    name = settings.app_name
    short_name = settings.app_name
    theme_color = settings.primary_color_hex or "#4F46E5"
    background_color = "#ffffff"

    # Icons: Use custom icon if provided, otherwise fallback to logo or default favicon
    icons = []

    icon_src = None

    if settings.pwa_display_mode == 'custom':
        if settings.pwa_custom_name:
            name = settings.pwa_custom_name
            short_name = settings.pwa_custom_name
        if settings.pwa_custom_icon_url:
            icon_src = settings.pwa_custom_icon_url

    # Fallback to logo if no custom icon (or if mode is default)
    if not icon_src and settings.logo_url:
        icon_src = settings.logo_url

    # If still no icon, maybe use a default placeholder (optional, but good for validity)
    if not icon_src:
        # Assuming a default logo exists in static if not set in DB, but DB usually has one.
        # Use a generic path that might 404 but structure is valid.
        icon_src = "/static/img/logo.png"

    # Add icon to manifest
    if icon_src:
        icons.append({
            "src": icon_src,
            "sizes": "192x192",
            "type": "image/png"
        })
        icons.append({
            "src": icon_src,
            "sizes": "512x512",
            "type": "image/png"
        })

    manifest_data = {
        "name": name,
        "short_name": short_name,
        "start_url": "/",
        "display": "standalone",
        "background_color": background_color,
        "theme_color": theme_color,
        "icons": icons,
        "orientation": "portrait-primary"
    }

    return jsonify(manifest_data)

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