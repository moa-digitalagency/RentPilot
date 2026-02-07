
"""
* Nom de l'application : RentPilot
* Description : Routes for Marketplace module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from config.extensions import db
from models import Ad, Room, Establishment, EstablishmentOwner, Lease
from models.marketplace import AdStatus
from security.auth import bailleur_required
from datetime import datetime

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/', methods=['GET'])
def index():
    """
    List all active marketplace ads with filters.
    """
    query = Ad.query.filter(Ad.is_active == True, Ad.status == AdStatus.APPROVED)

    # Filters
    city = request.args.get('city')
    country = request.args.get('country')
    property_type = request.args.get('property_type')
    is_furnished = request.args.get('is_furnished') == 'on'
    has_syndic = request.args.get('has_syndic') == 'on'

    if city:
        query = query.filter(Ad.city.ilike(f'%{city}%'))
    if country:
        query = query.filter(Ad.country.ilike(f'%{country}%'))
    if property_type:
        query = query.filter(Ad.property_type == property_type)
    if is_furnished:
        query = query.filter(Ad.is_furnished == True)
    if has_syndic:
        query = query.filter(Ad.has_syndic == True)

    ads = query.order_by(Ad.created_at.desc()).all()

    return render_template('marketplace/index.html', ads=ads)

@marketplace_bp.route('/api/latest', methods=['GET'])
def api_latest_ads():
    """
    Return the 3 latest approved ads as JSON for the landing page carousel.
    """
    ads = Ad.query.filter(Ad.is_active == True, Ad.status == AdStatus.APPROVED).order_by(Ad.created_at.desc()).limit(3).all()

    ads_data = []
    for ad in ads:
        price = 0
        if ad.room:
            price = ad.room.base_price
        elif ad.establishment:
            price = sum(r.base_price for r in ad.establishment.rooms)

        ads_data.append({
            'id': ad.id,
            'title': ad.title,
            'city': ad.city,
            'country': ad.country,
            'price': price,
            'description': ad.description[:100] + '...' if ad.description else '',
            'property_type': ad.property_type,
            'available_from': ad.available_from.strftime('%d/%m/%Y') if ad.available_from else 'Immédiat'
        })

    return jsonify(ads_data)

@marketplace_bp.route('/create', methods=['GET', 'POST'])
@login_required
@bailleur_required
def create():
    """
    Create a new ad. Restricted to Landlords.
    """
    if request.method == 'POST':
        selection = request.form.get('selection') # Format: 'room:123' or 'establishment:456'

        if not selection or ':' not in selection:
             flash("Veuillez sélectionner un bien valide.", "error")
             return redirect(url_for('marketplace.create'))

        target_type, target_id = selection.split(':')

        title = request.form.get('title')
        description = request.form.get('description')
        available_from_str = request.form.get('available_from')

        # New Fields
        city = request.form.get('city')
        country = request.form.get('country')
        property_type = request.form.get('property_type')
        is_furnished = 'is_furnished' in request.form
        has_syndic = 'has_syndic' in request.form

        # Contact Config
        enable_whatsapp = 'enable_whatsapp' in request.form
        whatsapp_number = request.form.get('whatsapp_number')

        enable_phone = 'enable_phone' in request.form
        phone_number = request.form.get('phone_number')

        enable_email = 'enable_email' in request.form
        contact_email = request.form.get('contact_email')

        if not title:
            flash("Titre requis.", "error")
            return redirect(url_for('marketplace.create'))

        available_from = None
        if available_from_str:
            try:
                available_from = datetime.strptime(available_from_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        room_id = None
        establishment_id = None

        if target_type == 'room':
            room = Room.query.get(target_id)
            if not room:
                flash("Chambre introuvable.", "error")
                return redirect(url_for('marketplace.create'))

            owner = EstablishmentOwner.query.filter_by(user_id=current_user.id, establishment_id=room.establishment_id).first()
            if not owner:
                flash("Vous n'êtes pas propriétaire de ce bien.", "error")
                return redirect(url_for('marketplace.create'))
            room_id = room.id

        elif target_type == 'establishment':
            est = Establishment.query.get(target_id)
            if not est:
                flash("Établissement introuvable.", "error")
                return redirect(url_for('marketplace.create'))

            owner = EstablishmentOwner.query.filter_by(user_id=current_user.id, establishment_id=est.id).first()
            if not owner:
                flash("Vous n'êtes pas propriétaire de ce bien.", "error")
                return redirect(url_for('marketplace.create'))

            # Strict Availability Check
            vacant_rooms = [r for r in est.rooms if r.is_vacant]
            if len(vacant_rooms) != len(est.rooms):
                 flash("Attention: Certaines chambres sont occupées. Vous ne pouvez publier le logement entier que s'il est entièrement disponible.", "warning")
                 return redirect(url_for('marketplace.create'))

            establishment_id = est.id
        else:
             flash("Type de cible invalide.", "error")
             return redirect(url_for('marketplace.create'))

        new_ad = Ad(
            room_id=room_id,
            establishment_id=establishment_id,
            title=title,
            description=description,
            available_from=available_from,
            city=city,
            country=country,
            property_type=property_type,
            is_furnished=is_furnished,
            has_syndic=has_syndic,
            enable_whatsapp=enable_whatsapp,
            whatsapp_number=whatsapp_number,
            enable_phone=enable_phone,
            phone_number=phone_number,
            enable_email=enable_email,
            contact_email=contact_email,
            is_active=True,
            status=AdStatus.PENDING
        )

        db.session.add(new_ad)
        db.session.commit()

        flash("Votre annonce a été soumise pour validation !", "success")
        return redirect(url_for('marketplace.index'))

    # GET: Fetch listable items
    listable_items = []

    owned_estabs = EstablishmentOwner.query.filter_by(user_id=current_user.id).all()
    for owner in owned_estabs:
        est = owner.establishment

        # Add Establishment (Whole Property)
        is_fully_available = all(r.is_vacant for r in est.rooms)

        # Only allow listing whole property if fully available (optional UI hint, enforce in backend)
        listable_items.append({
            'value': f'establishment:{est.id}',
            'label': f"🏠 Logement Entier: {est.address} ({len(est.rooms)} chambres) - {sum(r.base_price for r in est.rooms)}€",
            'disabled': not is_fully_available,
            'note': '' if is_fully_available else '(Occupé)'
        })

        # Add Individual Rooms
        for room in est.rooms:
            listable_items.append({
                'value': f'room:{room.id}',
                'label': f"🛏️ Chambre: {room.name} - {room.base_price}€",
                'disabled': not room.is_vacant,
                'note': '' if room.is_vacant else '(Occupé)'
            })

    return render_template('marketplace/create.html', items=listable_items)
