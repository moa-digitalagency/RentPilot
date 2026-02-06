from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
import enum
from datetime import datetime

db = SQLAlchemy()

# Enums
class UserRole(enum.Enum):
    ADMIN = 'Admin'
    BAILLEUR = 'Bailleur'
    TENANT_RESPONSABLE = 'Tenant_Responsable'
    COLOCATAIRE = 'Colocataire'

class FinancialMode(enum.Enum):
    EGAL = 'Egal'
    INEGAL = 'Inegal'

class ExpenseType(enum.Enum):
    EAU = 'Eau'
    ELEC = 'Elec'
    WIFI = 'Wifi'
    TRAVAUX = 'Travaux'

class PaymentStatus(enum.Enum):
    EN_ATTENTE = 'En attente'
    VALIDE = 'Validé'
    REJETE = 'Rejeté'

class ChannelType(enum.Enum):
    GENERAL = 'GENERAL'
    COLOC_ONLY = 'COLOC_ONLY'

# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(SQLAlchemyEnum(UserRole), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)

    # Relationships
    establishments = db.relationship('Establishment', backref='landlord', lazy=True)
    leases = db.relationship('Lease', backref='tenant', lazy=True)
    payments = db.relationship('Payment', backref='payer', lazy=True)
    sent_messages = db.relationship('Message', backref='sender', lazy=True)
    tickets = db.relationship('Ticket', backref='requester', lazy=True)

class Establishment(db.Model):
    __tablename__ = 'establishments'

    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    geo_approx = db.Column(db.String(100), nullable=True)
    config_financial_mode = db.Column(SQLAlchemyEnum(FinancialMode), nullable=False, default=FinancialMode.EGAL)
    wifi_cost = db.Column(db.Float, default=0.0)
    syndic_cost = db.Column(db.Float, default=0.0)

    rooms = db.relationship('Room', backref='establishment', lazy=True)
    expenses = db.relationship('Expense', backref='establishment', lazy=True)

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

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    type = db.Column(SQLAlchemyEnum(ExpenseType), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    proof_file_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=True) # Status not strictly defined in prompt enum list

    payments = db.relationship('Payment', backref='expense', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    proof_file_path = db.Column(db.String(255), nullable=True)
    status = db.Column(SQLAlchemyEnum(PaymentStatus), nullable=False, default=PaymentStatus.EN_ATTENTE)
    validation_date = db.Column(db.DateTime, nullable=True)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    channel_type = db.Column(SQLAlchemyEnum(ChannelType), nullable=False)

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Open')
