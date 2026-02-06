from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required
from models.users import User, UserRole
from config.extensions import db
from security.pwd_tools import check_password, hash_password
from security.auth import authenticate_and_login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        success, role = authenticate_and_login_user(email, password)

        if success:
            if role == 'SuperAdmin':
                return redirect(url_for('super_admin.dashboard'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role_value = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            try:
                # Handle case sensitive role mapping if necessary, or assume exact match
                role = UserRole(role_value)
            except ValueError:
                flash('Invalid role', 'error')
                return render_template('auth/register.html')

            hashed_pw = hash_password(password)
            new_user = User(email=email, password_hash=hashed_pw, role=role)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            return redirect(url_for('dashboard.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.pop('is_super_admin', None)
    return redirect(url_for('auth.login'))
