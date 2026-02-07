"""
* Nom de l'application : RentPilot
* Description : Application entry point.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Flask
from flask_login import LoginManager
from config.settings import Config
from config.extensions import db, configure_uploads, csrf # Security Fix: Import csrf
from services.i18n_service import i18n
from routes.context_processors import register_context_processors

# Import models for LoginManager and generally to ensure they are registered with SQLAlchemy
from models import User

# Import Blueprints
from routes import (
    auth_bp, dashboard_bp, establishment_bp, finance_bp,
    chat_bp, ticket_bp, main_bp, super_admin_bp, public_bp, chore_bp
)

def create_app():
    app = Flask(__name__, static_folder='../statics', template_folder='../templates')
    app.config.from_object(Config)

    configure_uploads(app)

    db.init_app(app)
    csrf.init_app(app) # Security Fix: Enable CSRF Protection
    i18n.init_app(app)

    register_context_processors(app)

    # Init LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(establishment_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ticket_bp)
    app.register_blueprint(super_admin_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(chore_bp)

    @app.after_request
    def set_security_headers(response):
        """Add security headers to every response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # CSP: To be configured carefully, currently report-only or minimal to avoid breakage
        # response.headers['Content-Security-Policy'] = "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';"
        return response

    return app
