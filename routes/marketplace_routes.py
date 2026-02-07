
"""
* Nom de l'application : RentPilot
* Description : Routes for Marketplace module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from config.extensions import db
from models import Ad, Room, Establishment, EstablishmentOwner, Lease
from datetime import datetime

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/', methods=['GET'])
def index():
    """
    List all active marketplace ads.
    """
    ads = Ad.query.filter_by(is_active=True).order_by(Ad.created_at.desc()).all()
    return render_template('marketplace/index.html', ads=ads)

@marketplace_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new ad.
    """
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        title = request.form.get('title')
        description = request.form.get('description')
        available_from_str = request.form.get('available_from')

        # Contact Config
        enable_whatsapp = 'enable_whatsapp' in request.form
        whatsapp_number = request.form.get('whatsapp_number')

        enable_phone = 'enable_phone' in request.form
        phone_number = request.form.get('phone_number')

        enable_email = 'enable_email' in request.form
        contact_email = request.form.get('contact_email')

        if not title or not room_id:
            flash("Titre et Chambre sont requis.", "error")
            return redirect(url_for('marketplace.create'))

        available_from = None
        if available_from_str:
            try:
                available_from = datetime.strptime(available_from_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_ad = Ad(
            room_id=room_id,
            title=title,
            description=description,
            available_from=available_from,
            enable_whatsapp=enable_whatsapp,
            whatsapp_number=whatsapp_number,
            enable_phone=enable_phone,
            phone_number=phone_number,
            enable_email=enable_email,
            contact_email=contact_email,
            is_active=True
        )

        db.session.add(new_ad)
        db.session.commit()

        flash("Votre annonce a été publiée avec succès !", "success")
        return redirect(url_for('marketplace.index'))

    # GET: Fetch rooms the user can list
    # Logic:
    # 1. If Landlord (in EstablishmentOwner), get rooms in those establishments.
    # 2. If Tenant (has Lease), get that room.

    listable_rooms = []

    # Check if Landlord
    owned_estabs = EstablishmentOwner.query.filter_by(user_id=current_user.id).all()
    if owned_estabs:
        estab_ids = [e.establishment_id for e in owned_estabs]
        listable_rooms.extend(Room.query.filter(Room.establishment_id.in_(estab_ids)).all())

    # Check if Tenant (active lease)
    active_lease = Lease.query.filter_by(user_id=current_user.id).filter(Lease.end_date >= datetime.utcnow().date()).first()
    if active_lease:
        # Avoid duplicates if they are also landlord of their own room (rare but possible in dev)
        room = Room.query.get(active_lease.room_id)
        if room and room not in listable_rooms:
            listable_rooms.append(room)

    # Fallback for Super Admin or demo: show all if list is empty? Or just show nothing.
    # If list is empty, maybe they are a new user.

    return render_template('marketplace/create.html', rooms=listable_rooms)
