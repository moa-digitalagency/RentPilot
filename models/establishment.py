from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
import enum

class FinancialMode(enum.Enum):
    EGAL = 'Egal'
    INEGAL = 'Inegal'

class Establishment(db.Model):
    __tablename__ = 'establishments'

    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    # Fuzzy location (approximate location within 200m)
    fuzzy_location = db.Column(db.String(255), nullable=True)

    # Configuration
    config_financial_mode = db.Column(SQLAlchemyEnum(FinancialMode), nullable=False, default=FinancialMode.EGAL)
    wifi_cost = db.Column(db.Float, default=0.0)
    syndic_cost = db.Column(db.Float, default=0.0)

    # Relationships
    rooms = db.relationship('Room', backref='establishment', lazy=True)
    # expenses relationship will be defined in finance.py via backref or we can define it here if possible.
    # Usually backref in Expense is enough.

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
