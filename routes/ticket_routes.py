from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.maintenance import Ticket
from models.users import UserRole
from models.establishment import Establishment, Lease
from config.extensions import db
from datetime import datetime

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/tickets', methods=['GET'])
@login_required
def list_tickets():
    if current_user.role == UserRole.BAILLEUR:
        # Bailleur sees all tickets for his establishments
        establishments = Establishment.query.filter_by(landlord_id=current_user.id).all()
        est_ids = [e.id for e in establishments]
        if est_ids:
             tickets = Ticket.query.filter(Ticket.establishment_id.in_(est_ids)).all()
        else:
             tickets = []
    else:
        # Tenant sees tickets they created
        tickets = Ticket.query.filter_by(requester_id=current_user.id).all()

    return render_template('ticket/list.html', tickets=tickets)

@ticket_bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'Normal')

        establishment_id = None
        # Try to link to establishment
        if current_user.role == UserRole.BAILLEUR:
            # Bailleur creating ticket? Maybe for a specific establishment.
            try:
                establishment_id = int(request.form.get('establishment_id'))
            except (ValueError, TypeError):
                establishment_id = None
        else:
            # Tenant
            lease = Lease.query.filter_by(user_id=current_user.id).first()
            if lease and lease.room:
                establishment_id = lease.room.establishment_id

        ticket = Ticket(
            requester_id=current_user.id,
            establishment_id=establishment_id,
            title=title,
            description=description,
            priority=priority,
            status='Open',
            created_at=datetime.utcnow()
        )
        db.session.add(ticket)
        db.session.commit()

        flash('Ticket created', 'success')
        return redirect(url_for('ticket.list_tickets'))

    # Context for template (e.g. list of establishments for Bailleur)
    context = {}
    if current_user.role == UserRole.BAILLEUR:
        context['establishments'] = Establishment.query.filter_by(landlord_id=current_user.id).all()

    return render_template('ticket/create.html', **context)
