
"""
* Nom de l'application : RentPilot
* Description : Source file: marketplace.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from datetime import datetime
from sqlalchemy import Enum as SQLAlchemyEnum
import enum

class AdStatus(enum.Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'

class Ad(db.Model):
    """
    Annonce pour une chambre vide ou colocation (ou logement entier).
    """
    __tablename__ = 'ads'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=True)

    # Basic Ad Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    available_from = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Status Management
    status = db.Column(SQLAlchemyEnum(AdStatus), default=AdStatus.PENDING, nullable=False)
    rejection_reason = db.Column(db.String(255), nullable=True)

    # Location & Filters
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    property_type = db.Column(db.String(50), default='Appartement') # e.g. Appartement, Maison, Studio
    is_furnished = db.Column(db.Boolean, default=False)
    has_syndic = db.Column(db.Boolean, default=False)

    # Kept for backward compatibility but status should be primary check
    is_active = db.Column(db.Boolean, default=True)

    # Contact Configuration
    enable_whatsapp = db.Column(db.Boolean, default=False)
    whatsapp_number = db.Column(db.String(20), nullable=True) # For wa.me link

    enable_phone = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20), nullable=True) # For tel: link

    enable_email = db.Column(db.Boolean, default=False)
    contact_email = db.Column(db.String(120), nullable=True) # For mailto: link

    # Relationships
    room = db.relationship('Room', backref='ads', lazy=True)
    establishment = db.relationship('Establishment', backref='ads', lazy=True)

class Request(db.Model):
    """
    Demandes administratives (e.g. Quittance, Attestation).
    """
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(100), nullable=False) # e.g. "Quittance", "CAF"
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
