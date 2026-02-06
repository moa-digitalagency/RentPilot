from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models.users import User, UserRole
from config.extensions import db
from security.pwd_tools import check_password, hash_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password(user.password_hash, password):
            login_user(user)
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
