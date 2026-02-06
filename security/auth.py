from functools import wraps
from flask import abort
from flask_login import current_user
from config.extensions import login_manager

# We will import User inside the loader to avoid circular imports during initialization
# from models.users import User

@login_manager.user_loader
def load_user(user_id):
    from models.users import User
    return User.query.get(int(user_id))

def bailleur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.value != 'Bailleur':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Assuming both Tenant Responsable and Colocataire are "tenants"
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role.value not in ['Tenant_Responsable', 'Colocataire']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.value != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
