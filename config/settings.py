import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI') or 'sqlite:///rentpilot.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'

    # Ensure upload folder is absolute path or relative to project root
    # __file__ is config/settings.py
    # dirname(__file__) is config/
    # dirname(config/) is project root
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'statics', 'uploads')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
