
"""
* Nom de l'application : RentPilot
* Description : Source file: establishment.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
import enum

class FinancialMode(enum.Enum):
    EGAL = 'Egal'
    INEGAL = 'Inegal'

class SaaSBilledTo(enum.Enum):
    LANDLORD = 'Landlord'
    TENANTS = 'Tenants'

class EstablishmentOwnerRole(enum.Enum):
    PRIMARY = 'Primary'
    SECONDARY = 'Secondary'

class EstablishmentOwner(db.Model):
    __tablename__ = 'establishment_owners'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), primary_key=True)
    role = db.Column(SQLAlchemyEnum(EstablishmentOwnerRole), default=EstablishmentOwnerRole.SECONDARY, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='establishment_associations')
    establishment = db.relationship('Establishment', back_populates='owner_associations')

class Establishment(db.Model):
    __tablename__ = 'establishments'

    id = db.Column(db.Integer, primary_key=True)
    # landlord_id removed as per request
    address = db.Column(db.String(255), nullable=False)
    # Fuzzy location (approximate location within 200m)
    fuzzy_location = db.Column(db.String(255), nullable=True)

    # Configuration
    subscription_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    config_financial_mode = db.Column(SQLAlchemyEnum(FinancialMode), nullable=False, default=FinancialMode.EGAL)
    saas_billed_to = db.Column(SQLAlchemyEnum(SaaSBilledTo), nullable=False, default=SaaSBilledTo.LANDLORD)
    wifi_cost = db.Column(db.Float, default=0.0)
    syndic_cost = db.Column(db.Float, default=0.0)

    expense_types_config = db.Column(db.JSON, default=list)

    # Relationships
    subscription_plan = db.relationship('SubscriptionPlan', backref='establishments')
    rooms = db.relationship('Room', backref='establishment', lazy=True)

    # New relationship for owners
    owner_associations = db.relationship('EstablishmentOwner', back_populates='establishment', cascade='all, delete-orphan')

    def get_active_expenses(self):
        """Returns the list of active expenses."""
        if self.expense_types_config:
            return self.expense_types_config
        # Return defaults if not configured
        return ['Loyer', 'Eau', 'Elec', 'Wifi', 'Travaux']

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    is_vacant = db.Column(db.Boolean, default=True)

    leases = db.relationship('Lease', backref='room', lazy=True)

class Lease(db.Model):
    __tablename__ = 'leases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)