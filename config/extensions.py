from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def configure_uploads(app):
    """
    Ensure upload directories exist.
    """
    upload_folders = [
        app.config['UPLOAD_FOLDER'],
        app.config['UPLOAD_FOLDER_CHAT']
    ]
    for folder in upload_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created upload directory: {folder}")
