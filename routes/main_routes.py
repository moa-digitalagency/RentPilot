
"""
* Nom de l'application : RentPilot
* Description : Routes for main module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import current_user, login_required
from services.i18n_service import i18n
from services.upload_service import UploadService
from services.geo_service import GeoService
from config.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['fr', 'en', 'es', 'pt']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/api/lang/<lang>')
def get_lang_json(lang):
    if lang not in ['fr', 'en', 'es', 'pt']:
        return jsonify({}), 404
    return jsonify(i18n.get_translations(lang))

@main_bp.route('/responsive-table')
def responsive_table_demo():
    # Sample data for the responsive table
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "Tenant", "status": "Active", "last_login": "2023-10-25"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "Landlord", "status": "Active", "last_login": "2023-10-24"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "Tenant", "status": "Inactive", "last_login": "2023-09-15"},
        {"id": 4, "name": "Alice Williams", "email": "alice@example.com", "role": "Admin", "status": "Active", "last_login": "2023-10-26"},
        {"id": 5, "name": "Charlie Brown", "email": "charlie@example.com", "role": "Tenant", "status": "Pending", "last_login": "N/A"},
    ]
    return render_template('responsive_table_demo.html', users=users)

@main_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')

@main_bp.route('/profile/verify-identity', methods=['POST'])
@login_required
def verify_identity():
    id_card_file = request.files.get('identity_card')

    if not id_card_file or id_card_file.filename == '':
        flash("Veuillez sélectionner un fichier.", "error")
        return redirect(url_for('main.profile'))

    try:
        # Save to 'identity' subfolder
        saved_path = UploadService.save_file(id_card_file, subfolder='identity')
        current_user.identity_card_url = '/' + saved_path
        current_user.is_identity_verified = True # Auto-verify for now as per instructions implies simple upload
        db.session.commit()
        flash("Pièce d'identité téléchargée avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors du téléchargement: {str(e)}", "error")

    return redirect(url_for('main.profile'))

@main_bp.route('/api/geo/detect', methods=['GET'])
def geo_detect():
    ip = request.remote_addr
    # Handle Proxy headers
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]

    # Localhost check
    if ip == '127.0.0.1' or ip == '::1':
        # Default mock for dev
        return jsonify({'city': 'Paris', 'country': 'France', 'country_code': 'FR'})

    location = GeoService.get_client_ip_info(ip)

    if not location:
        # Fallback
        return jsonify({'city': 'Paris', 'country': 'France', 'country_code': 'FR'})

    return jsonify(location)
