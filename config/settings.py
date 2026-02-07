
"""
* Nom de l'application : RentPilot
* Description : Configuration settings.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI') or 'postgresql://rentpilot:rentpilot@localhost:5432/rentpilot'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_please_change_in_prod'

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Only set Secure flag in production/https environment
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'

    # Uploads
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'statics', 'uploads')
    UPLOAD_FOLDER_CHAT = os.environ.get('UPLOAD_FOLDER_CHAT') or os.path.join(basedir, 'statics', 'uploads', 'chat')

    # Super Admin (Env variables)
    # Audited: Moved default credentials to be clearly identified as fallbacks
    SUPER_ADMIN_ID = os.environ.get('SUPER_ADMIN_ID') or 'admin@rentpilot.com'
    SUPER_ADMIN_PASS = os.environ.get('SUPER_ADMIN_PASS') or 'SuperSecretPass123!'

    # APILayer / Geolocation
    GEO_API_KEY = os.environ.get('GEO_API_KEY')
