from functools import wraps
from flask import abort, request
from flask_login import current_user
from models.establishment import Establishment, EstablishmentOwner, EstablishmentOwnerRole
from models.users import User, UserRole
from config.extensions import db

def add_co_landlord(establishment_id, email):
    """
    Adds a co-landlord to an establishment by email.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "Utilisateur introuvable."

    # Check if user is a landlord? Or maybe any user can be a co-landlord?
    # Usually they should have the 'Bailleur' role, but let's just add them to the association table.
    # The prompt doesn't strictly say to check role here, but good practice.
    # However, I'll stick to the core requirement: find user, add to table.

    establishment = Establishment.query.get(establishment_id)
    if not establishment:
        return False, "Établissement introuvable."

    # Check if already an owner
    existing_owner = EstablishmentOwner.query.filter_by(
        user_id=user.id,
        establishment_id=establishment_id
    ).first()

    if existing_owner:
        return False, "Cet utilisateur est déjà associé à cet établissement."

    new_owner = EstablishmentOwner(
        user_id=user.id,
        establishment_id=establishment_id,
        role=EstablishmentOwnerRole.SECONDARY
    )
    db.session.add(new_owner)
    db.session.commit()

    return True, "Co-bailleur ajouté avec succès."

def landlord_required(f):
    """
    Decorator to ensure the current user is a landlord (Bailleur)
    AND is an owner of the specific establishment being accessed.

    Assumes the route has 'establishment_id' or 'id' as a parameter.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)

        # Check if user has the role 'Bailleur'
        if current_user.role != UserRole.BAILLEUR:
            abort(403)

        # Get establishment_id from kwargs
        est_id = kwargs.get('establishment_id') or kwargs.get('id')

        if not est_id:
            # If no ID is present in the route, we can't check specific permission.
            # This might happen for general routes like '/establishments'.
            # In that case, we might just pass if they are a Bailleur,
            # OR fail if this decorator is strictly for specific establishment access.
            # Given the prompt ("Il doit vérifier : current_user in establishment.owners"),
            # it implies checking against a specific establishment.
            # So if ID is missing, we probably shouldn't use this decorator or it's a 400/404.
            # However, for robustness, if no ID found, maybe we let it pass the generic role check
            # or fail. Let's abort(404) or 403.
            abort(404)

        # Check if the user is an owner of this establishment
        is_owner = EstablishmentOwner.query.filter_by(
            user_id=current_user.id,
            establishment_id=est_id
        ).first()

        if not is_owner:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
