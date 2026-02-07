
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

    # Get unique cities/countries for filters dropdown (optional optimization)
    # unique_cities = db.session.query(Ad.city).distinct().all()

    return render_template('marketplace/index.html', ads=ads)

@marketplace_bp.route('/api/latest', methods=['GET'])
def api_latest_ads():
    """
    Return the 3 latest approved ads as JSON for the landing page carousel.
    """
    ads = Ad.query.filter(Ad.is_active == True, Ad.status == AdStatus.APPROVED).order_by(Ad.created_at.desc()).limit(3).all()

    ads_data = []
    for ad in ads:
        ads_data.append({
            'id': ad.id,
            'title': ad.title,
            'city': ad.city,
            'country': ad.country,
            'price': ad.room.base_price, # Assuming room has base_price
            'description': ad.description[:100] + '...' if ad.description else '',
            'property_type': ad.property_type,
            'available_from': ad.available_from.strftime('%d/%m/%Y') if ad.available_from else 'Immédiat'
        })

    return jsonify(ads_data)

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
            status=AdStatus.PENDING # Default to pending validation
        )

        db.session.add(new_ad)
        db.session.commit()

        flash("Votre annonce a été soumise pour validation !", "success")
        return redirect(url_for('marketplace.index'))

    # GET: Fetch rooms the user can list
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

    return render_template('marketplace/create.html', rooms=listable_rooms)
