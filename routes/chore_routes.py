from flask import Blueprint, jsonify, request, abort, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.users import UserRole
from models.chores import ChoreEvent, ChoreType, ChoreValidation, ChoreStatus
from models.establishment import Lease, Room, Establishment
from config.extensions import db
from services.chore_service import mark_task_done, validate_task, get_active_tenants
from datetime import datetime

chore_bp = Blueprint('chore', __name__)

@chore_bp.before_request
@login_required
def check_chore_access():
    # Strict access control: Landlords cannot access unless they are tenants
    if current_user.role == UserRole.BAILLEUR and not current_user.is_tenant:
        abort(403)

@chore_bp.route('/chores', methods=['GET'])
def index():
    est_id = get_user_establishment_id()
    if not est_id:
        flash("Vous devez être locataire pour accéder à cette page.", "error")
        return redirect(url_for('dashboard.dashboard'))

    # Pre-established tasks (Chore Types)
    chore_types = ChoreType.query.filter_by(establishment_id=est_id).all()

    # Tasks pending MY validation
    # 1. Get all events in establishment with status DONE_WAITING_VALIDATION
    pending_events = ChoreEvent.query.join(ChoreType).filter(
        ChoreType.establishment_id == est_id,
        ChoreEvent.status == ChoreStatus.DONE_WAITING_VALIDATION,
        ChoreEvent.assigned_user_id != current_user.id
    ).all()

    # 2. Filter out those I already validated
    tasks_to_validate = []
    for event in pending_events:
        validator_ids = [v.validator_user_id for v in event.validations if v.is_validated]
        if current_user.id not in validator_ids:
            tasks_to_validate.append(event)

    return render_template('chores.html',
                           chore_types=chore_types,
                           tasks_to_validate=tasks_to_validate)

def get_user_establishment_id():
    """Helper to get the establishment ID for the current user (tenant)."""
    # Find active lease
    # We assume the user has at least one active lease if is_tenant is true
    # For now, just take the first lease found, or filter for active
    if not current_user.leases:
        return None

    # Sort leases by start_date desc to get most recent?
    # Or filter for active.
    today = datetime.now().date()
    for lease in current_user.leases:
        if lease.start_date <= today and (lease.end_date is None or lease.end_date >= today):
            return lease.room.establishment_id

    # Fallback to any lease if no active one found?
    # Or return None.
    if current_user.leases:
         return current_user.leases[0].room.establishment_id

    return None

@chore_bp.route('/chores/calendar', methods=['GET'])
def get_calendar_events():
    est_id = get_user_establishment_id()
    if not est_id:
        return jsonify([])

    start_str = request.args.get('start')
    end_str = request.args.get('end')

    query = ChoreEvent.query.join(ChoreType).filter(ChoreType.establishment_id == est_id)

    if start_str:
        try:
            # FullCalendar sends ISO strings like '2023-10-01T00:00:00-05:00'
            # We might need to handle timezone or just slice date
            start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date() # approximate
            query = query.filter(ChoreEvent.due_date >= start_date)
        except ValueError:
            pass # Ignore invalid date format

    if end_str:
        try:
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
            query = query.filter(ChoreEvent.due_date <= end_date)
        except ValueError:
            pass

    events = query.all()

    # Calculate total active tenants for validation ratio
    active_tenants = get_active_tenants(est_id)
    total_tenants = len(active_tenants)

    result = []
    for event in events:
        nb_validations = len([v for v in event.validations if v.is_validated])
        validation_status = f"{nb_validations}/{total_tenants} validations"

        result.append({
            'id': event.id,
            'title': event.chore_type.name,
            'start': event.due_date.isoformat(),
            'allDay': True,
            'extendedProps': {
                'validation_status': validation_status,
                'status': event.status.value,
                'assigned_user_id': event.assigned_user_id
            }
        })

    return jsonify(result)

@chore_bp.route('/chores/type', methods=['POST'])
def create_chore_type():
    est_id = get_user_establishment_id()
    if not est_id:
        abort(400, "User not associated with an establishment")

    data = request.get_json()
    if not data:
        abort(400, "Invalid JSON")

    name = data.get('name')
    if not name:
        abort(400, "Name is required")

    description = data.get('description')
    icon = data.get('icon')
    frequency = data.get('frequency_days', 7)
    is_rotating = data.get('is_rotating', False)

    new_chore = ChoreType(
        establishment_id=est_id,
        name=name,
        description=description,
        icon=icon,
        frequency_days=frequency,
        is_rotating=is_rotating
    )
    db.session.add(new_chore)
    db.session.commit()

    return jsonify({'message': 'Chore type created', 'id': new_chore.id}), 201

@chore_bp.route('/chores/<int:id>/done', methods=['POST'])
def mark_done(id):
    success, msg = mark_task_done(id, current_user.id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg})

@chore_bp.route('/chores/<int:id>/confirm', methods=['POST'])
def confirm_task(id):
    success, msg = validate_task(id, current_user.id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg})
