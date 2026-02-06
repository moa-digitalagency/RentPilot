from functools import wraps
from flask import abort, session, current_app
from flask_login import current_user, login_user
from config.extensions import login_manager
from security.pwd_tools import check_password

# We will import User inside the loader to avoid circular imports during initialization
# from models.users import User

def authenticate_and_login_user(email, password):
    """
    Custom login function to handle Super Admin (Env) and Regular Users (DB).
    Returns (success, role_name_or_user_obj).
    """
    # 1. Check Super Admin (Hardcoded/Env)
    sa_id = current_app.config.get('SUPER_ADMIN_ID')
    sa_pass = current_app.config.get('SUPER_ADMIN_PASS')

    if email == sa_id and password == sa_pass:
        session.clear() # Clear any previous session
        session['is_super_admin'] = True
        return True, 'SuperAdmin'

    # 2. Check Database User
    from models.users import User
    user = User.query.filter_by(email=email).first()

    if user and check_password(user.password_hash, password):
        login_user(user)
        return True, user.role.value

    return False, None

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_super_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

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
