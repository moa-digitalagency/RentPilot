from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from security.auth import bailleur_required
from models.establishment import Establishment, Room, Lease, FinancialMode, EstablishmentOwner, EstablishmentOwnerRole
from models.users import User
from config.extensions import db
from datetime import datetime
from services.permission_service import add_co_landlord

establishment_bp = Blueprint('establishment', __name__)

@establishment_bp.route('/establishment/create', methods=['GET', 'POST'])
@login_required
@bailleur_required
def create_establishment():
    if request.method == 'POST':
        address = request.form.get('address')
        wifi_cost = float(request.form.get('wifi_cost', 0))
        syndic_cost = float(request.form.get('syndic_cost', 0))
        mode_val = request.form.get('financial_mode', 'Egal')

        mode = FinancialMode.EGAL if mode_val == 'Egal' else FinancialMode.INEGAL

        est = Establishment(
            address=address,
            wifi_cost=wifi_cost,
            syndic_cost=syndic_cost,
            config_financial_mode=mode
        )
        db.session.add(est)
        db.session.commit()

        owner = EstablishmentOwner(
            user_id=current_user.id,
            establishment_id=est.id,
            role=EstablishmentOwnerRole.PRIMARY
        )
        db.session.add(owner)
        db.session.commit()
        flash('Establishment created', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('establishment/create.html')

@establishment_bp.route('/establishment/<int:id>/update', methods=['GET', 'POST'])
@login_required
@bailleur_required
def update_establishment(id):
    est = Establishment.query.get_or_404(id)
    owner = EstablishmentOwner.query.filter_by(user_id=current_user.id, establishment_id=est.id).first()
    if not owner:
        abort(403)

    if request.method == 'POST':
        est.address = request.form.get('address')
        est.wifi_cost = float(request.form.get('wifi_cost', 0))
        est.syndic_cost = float(request.form.get('syndic_cost', 0))
        mode_val = request.form.get('financial_mode')
        if mode_val:
            est.config_financial_mode = FinancialMode.EGAL if mode_val == 'Egal' else FinancialMode.INEGAL

        db.session.commit()
        flash('Establishment updated', 'success')
        return redirect(url_for('establishment.update_establishment', id=id))

    return render_template('establishment/update.html', establishment=est)

@establishment_bp.route('/establishment/<int:id>/add-room', methods=['POST'])
@login_required
@bailleur_required
def add_room(id):
    est = Establishment.query.get_or_404(id)
    owner = EstablishmentOwner.query.filter_by(user_id=current_user.id, establishment_id=est.id).first()
    if not owner:
        abort(403)

    name = request.form.get('name')
    base_price = float(request.form.get('base_price', 0))

    room = Room(establishment_id=est.id, name=name, base_price=base_price)
    db.session.add(room)
    db.session.commit()

    flash('Room added', 'success')
    return redirect(url_for('establishment.update_establishment', id=id))

@establishment_bp.route('/establishment/<int:id>/assign-tenant', methods=['POST'])
@login_required
@bailleur_required
def assign_tenant(id):
    est = Establishment.query.get_or_404(id)
    owner = EstablishmentOwner.query.filter_by(user_id=current_user.id, establishment_id=est.id).first()
    if not owner:
        abort(403)

    room_id = request.form.get('room_id')
    user_email = request.form.get('user_email')
    start_date_str = request.form.get('start_date')

    room = Room.query.get(room_id)
    if not room or room.establishment_id != est.id:
        flash('Invalid room', 'error')
        return redirect(url_for('establishment.update_establishment', id=id))

    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('establishment.update_establishment', id=id))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('establishment.update_establishment', id=id))

    lease = Lease(user_id=user.id, room_id=room.id, start_date=start_date)
    room.is_vacant = False

    db.session.add(lease)
    db.session.commit()

    flash('Tenant assigned', 'success')
    return redirect(url_for('establishment.update_establishment', id=id))

@establishment_bp.route('/establishment/setup', methods=['GET', 'POST'])
@login_required
@bailleur_required
def setup():
    if request.method == 'POST':
        data = {}
        if request.is_json:
            data = request.get_json()
        else:
            # Helper to mimic json structure from form
            data = request.form.to_dict()
            data['custom_expenses'] = request.form.getlist('custom_expenses')

        est = Establishment.query.join(EstablishmentOwner).filter(EstablishmentOwner.user_id == current_user.id).first()

        address = data.get('address')
        if not est:
            est = Establishment(
                address=address if address else 'Adresse Inconnue'
            )
            db.session.add(est)
            db.session.commit()

            owner = EstablishmentOwner(
                user_id=current_user.id,
                establishment_id=est.id,
                role=EstablishmentOwnerRole.PRIMARY
            )
            db.session.add(owner)

        # Update fields
        custom_expenses = data.get('custom_expenses')
        if custom_expenses:
             if isinstance(custom_expenses, list):
                 est.expense_types_config = [e for e in custom_expenses if isinstance(e, str) and e.strip()]

        if address:
            est.address = address

        if data.get('wifi_cost'):
            try:
                est.wifi_cost = float(data.get('wifi_cost'))
            except (ValueError, TypeError):
                pass

        if data.get('syndic_cost'):
            try:
                est.syndic_cost = float(data.get('syndic_cost'))
            except (ValueError, TypeError):
                pass

        split_mode = data.get('split_mode')
        if split_mode:
            if split_mode == 'Surface':
                 est.config_financial_mode = FinancialMode.INEGAL
            else:
                 est.config_financial_mode = FinancialMode.EGAL

        db.session.commit()

        if request.is_json:
             return jsonify({'status': 'success', 'redirect_url': url_for('dashboard.dashboard')})

        flash('Configuration terminée !', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('establishment_setup.html')

@establishment_bp.route('/establishment/<int:id>/co-owners', methods=['POST'])
@login_required
@bailleur_required
def add_co_owner(id):
    # Check if current user is an owner (Primary or Secondary? Usually Primary to add others)
    # Let's restrict to Primary owner for security
    owner = EstablishmentOwner.query.filter_by(
        user_id=current_user.id,
        establishment_id=id,
        role=EstablishmentOwnerRole.PRIMARY
    ).first()

    if not owner:
        abort(403, "Seul le propriétaire principal peut ajouter des co-bailleurs.")

    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email requis'}), 400

    success, msg = add_co_landlord(id, email)
    if not success:
        return jsonify({'error': msg}), 400

    return jsonify({'message': msg})

@establishment_bp.route('/establishment/<int:id>/co-owners/<int:user_id>', methods=['DELETE'])
@login_required
@bailleur_required
def remove_co_owner(id, user_id):
    # Check if current user is Primary owner
    owner = EstablishmentOwner.query.filter_by(
        user_id=current_user.id,
        establishment_id=id,
        role=EstablishmentOwnerRole.PRIMARY
    ).first()

    if not owner:
        abort(403, "Seul le propriétaire principal peut supprimer des co-bailleurs.")

    # Cannot remove yourself via this route (safety check)
    if user_id == current_user.id:
        return jsonify({'error': 'Vous ne pouvez pas vous supprimer vous-même.'}), 400

    target_owner = EstablishmentOwner.query.filter_by(
        user_id=user_id,
        establishment_id=id
    ).first()

    if not target_owner:
        return jsonify({'error': 'Co-bailleur introuvable.'}), 404

    db.session.delete(target_owner)
    db.session.commit()

    return jsonify({'message': 'Co-bailleur supprimé.'})
