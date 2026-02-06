from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html')

@main_bp.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['fr', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))
