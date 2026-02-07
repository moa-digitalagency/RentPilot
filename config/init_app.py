from flask import Flask
from flask_login import LoginManager
from config.settings import Config
from config.extensions import db, configure_uploads
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

    return app
