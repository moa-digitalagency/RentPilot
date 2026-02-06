from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.users import UserRole
from models.establishment import Establishment, Lease
from models.maintenance import Ticket
from models.finance import Transaction, Invoice
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    context = {}
    context['now_date'] = datetime.now().strftime('%d/%m/%Y')
    context['now_month'] = datetime.now().strftime('%m')

    # Simple logic to get previous month
    prev_month = datetime.now().month - 1
    if prev_month == 0: prev_month = 12
    context['now_month_prev'] = f"{prev_month:02d}"

    if current_user.role == UserRole.BAILLEUR:
        # Bailleur logic
        establishments = Establishment.query.filter_by(landlord_id=current_user.id).all()

        total_tenants = 0
        est_ids = []
        for est in establishments:
            est_ids.append(est.id)
            for room in est.rooms:
                if not room.is_vacant:
                    total_tenants += 1

        open_tickets = 0
        if est_ids:
            open_tickets = Ticket.query.filter(
                Ticket.establishment_id.in_(est_ids),
                Ticket.status == 'Open'
            ).count()

        context = {
            'role': 'Bailleur',
            'establishments': establishments,
            'total_tenants': total_tenants,
            'open_tickets': open_tickets
        }

    elif current_user.role in [UserRole.COLOCATAIRE, UserRole.TENANT_RESPONSABLE]:
        # Tenant logic
        # Find active lease (assuming one active lease for simplicity)
        active_lease = Lease.query.filter_by(user_id=current_user.id).first()

        if active_lease:
            room = active_lease.room
            establishment = room.establishment
            roommates = []

            # Find roommates in same establishment
            # We iterate through rooms of the establishment
            for r in establishment.rooms:
                if not r.is_vacant and r.id != room.id:
                    # Find lease for this room
                    # This is a simplification, as there might be historical leases.
                    # Ideally we filter by date or an 'active' flag.
                    # Here we take the last one or similar.
                    l = Lease.query.filter_by(room_id=r.id).order_by(Lease.start_date.desc()).first()
                    if l and l.tenant:
                        roommates.append(l.tenant)

            context = {
                'role': 'Tenant',
                'lease': active_lease,
                'room': room,
                'establishment': establishment,
                'roommates': roommates
            }
        else:
             context = {
                'role': 'Tenant',
                'message': 'No active lease found.'
             }

    elif current_user.role == UserRole.ADMIN:
         context = {'role': 'Admin'}

    return render_template('dashboard.html', **context)
