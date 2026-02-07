
"""
* Nom de l'application : RentPilot
* Description : Source file: __init__.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .establishment_routes import establishment_bp
from .finance_routes import finance_bp
from .chat_routes import chat_bp
from .ticket_routes import ticket_bp
from .main_routes import main_bp
from .super_admin_routes import super_admin_bp
from .public_routes import public_bp
from .chore_routes import chore_bp