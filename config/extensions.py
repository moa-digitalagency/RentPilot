"""
* Nom de l'application : RentPilot
* Description : Configuration settings.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect # Security Fix: Import CSRFProtect

import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect() # Security Fix: Initialize CSRFProtect

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
