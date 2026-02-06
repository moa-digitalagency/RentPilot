from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import current_user
from services.i18n_service import i18n

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['fr', 'en', 'es', 'pt']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/api/lang/<lang>')
def get_lang_json(lang):
    if lang not in ['fr', 'en', 'es', 'pt']:
        return jsonify({}), 404
    return jsonify(i18n.get_translations(lang))
