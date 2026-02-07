
"""
* Nom de l'application : RentPilot
* Description : Service logic for chore module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from datetime import datetime, timedelta
from config.extensions import db
from models.chores import ChoreType, ChoreEvent, ChoreValidation, ChoreStatus
from models.establishment import Establishment, Lease, Room
from models.users import User
from sqlalchemy import func

def get_active_tenants(establishment_id):
    """
    Returns a list of active tenants (Users) for the given establishment.
    Checks for active leases.
    """
    # Find rooms in the establishment
    rooms = Room.query.filter_by(establishment_id=establishment_id).all()
    room_ids = [r.id for r in rooms]

    if not room_ids:
        return []

    # Find active leases for these rooms
    # Active means start_date <= today and (end_date is None or end_date >= today)
    today = datetime.now().date()

    active_leases = Lease.query.filter(
        Lease.room_id.in_(room_ids),
        Lease.start_date <= today,
        (Lease.end_date == None) | (Lease.end_date >= today)
    ).all()

    tenants = [lease.tenant for lease in active_leases]
    # Sort by ID to ensure consistent order for rotation
    tenants.sort(key=lambda u: u.id)

    return tenants

def generate_planning(establishment_id):
    """
    Called weekly (Cron). Creates future ChoreEvents.
    """
    establishment = Establishment.query.get(establishment_id)
    if not establishment:
        return None

    active_tenants = get_active_tenants(establishment_id)
    if not active_tenants:
        return "No active tenants found."

    chore_types = ChoreType.query.filter_by(establishment_id=establishment_id).all()

    events_created = []

    for chore in chore_types:
        if chore.is_rotating:
            # 1. Find the last event for this chore
            last_event = ChoreEvent.query.filter_by(chore_type_id=chore.id)\
                .order_by(ChoreEvent.due_date.desc()).first()

            next_assignee = None

            if not last_event:
                # First time: assign to the first tenant in the list
                next_assignee = active_tenants[0]
            else:
                # Find the index of the last assignee in the current active list
                last_assignee_id = last_event.assigned_user_id

                try:
                    # Find index of user with this ID
                    current_idx = next((i for i, u in enumerate(active_tenants) if u.id == last_assignee_id), -1)

                    if current_idx == -1:
                        # Last assignee is no longer active. Start from beginning? Or random?
                        # Start from beginning seems safest.
                        next_assignee = active_tenants[0]
                    else:
                        # Next index
                        next_idx = (current_idx + 1) % len(active_tenants)
                        next_assignee = active_tenants[next_idx]

                except ValueError:
                    next_assignee = active_tenants[0]

            # Create the event
            # Due date: For simplicity, let's say due in 'frequency_days' from now, or align with weeks.
            # If cron runs weekly, we might be generating for the upcoming week.
            due_date = datetime.now() + timedelta(days=chore.frequency_days)

            new_event = ChoreEvent(
                chore_type_id=chore.id,
                assigned_user_id=next_assignee.id,
                due_date=due_date,
                status=ChoreStatus.PENDING
            )
            db.session.add(new_event)
            events_created.append(new_event)

        else:
            # Non-rotating logic (Optional based on prompt, but good to handle)
            # Assign to ALL active tenants? Or skip?
            # Prompt doesn't specify. I'll skip for now to avoid cluttering.
            pass

    db.session.commit()
    return f"Created {len(events_created)} events."

def mark_task_done(event_id, user_id):
    """
    Passes the status to Done_Waiting_Validation.
    """
    event = ChoreEvent.query.get(event_id)
    if not event:
        return False, "Tâche introuvable."

    if event.assigned_user_id != user_id:
        return False, "Ce n'est pas votre tâche."

    event.status = ChoreStatus.DONE_WAITING_VALIDATION
    db.session.commit()
    return True, "Tâche marquée comme terminée."

def validate_task(event_id, validator_user_id):
    """
    Registers validation.
    Checks consensus: if nb_validations == (total_colocs - 1), set status to Completed.
    """
    event = ChoreEvent.query.get(event_id)
    if not event:
        return False, "Tâche introuvable."

    if event.assigned_user_id == validator_user_id:
        return False, "Vous ne pouvez pas valider votre propre tâche."

    # Check if already validated by this user
    existing_validation = ChoreValidation.query.filter_by(
        event_id=event_id,
        validator_user_id=validator_user_id
    ).first()

    if existing_validation:
        return False, "Vous avez déjà validé cette tâche."

    # Create validation
    validation = ChoreValidation(
        event_id=event_id,
        validator_user_id=validator_user_id,
        is_validated=True
    )
    db.session.add(validation)

    # We need to commit here to count correctly? Or just flush.
    db.session.flush()

    # Consensus Logic
    # 1. Get total active tenants in the establishment
    # We can get establishment from chore_type
    establishment_id = event.chore_type.establishment_id
    active_tenants = get_active_tenants(establishment_id)
    total_colocs = len(active_tenants)

    # 2. Count validations
    nb_validations = ChoreValidation.query.filter_by(event_id=event_id, is_validated=True).count()
    # Note: The current session add might not be reflected in count() if not committed,
    # but flush() should make it visible to the transaction.
    # Actually, count() does a DB query. If we flushed, it *should* see it in the transaction
    # depending on isolation level, but simpler is to use len(event.validations) if backref is updated,
    # or just trust the increment.

    # Let's rely on the query.
    # If the user performing the task is one of the active tenants, then we need (N-1) validations.

    needed_validations = total_colocs - 1
    if needed_validations < 1:
        needed_validations = 0 # Single tenant case?

    if nb_validations >= needed_validations:
        event.status = ChoreStatus.COMPLETED

    db.session.commit()
    return True, "Validation enregistrée."

def get_chore_finance_link(chore_type_id):
    """
    Returns a link/hint for finance if applicable.
    """
    chore = ChoreType.query.get(chore_type_id)
    if not chore:
        return None

    # Check keywords
    keywords = ['achat', 'buy', 'course', 'gaz', 'electricity', 'facture']
    name_lower = chore.name.lower()

    if any(k in name_lower for k in keywords):
        return {
            'has_link': True,
            'text': "Créer une dépense associée",
            'url': f"/finance/expense/create?ref_chore={chore.id}" # Hypothetical URL
        }
    return {'has_link': False}