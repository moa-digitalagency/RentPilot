from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
import enum
from datetime import datetime

class ExpenseType(enum.Enum):
    EAU = 'Eau'
    ELEC = 'Elec'
    WIFI = 'Wifi'
    TRAVAUX = 'Travaux'
    LOYER = 'Loyer'

class ValidationStatus(enum.Enum):
    PENDING = 'Pending'
    VALIDATED = 'Validated'
    REJECTED = 'Rejected'

class Invoice(db.Model):
    """
    Represents a bill/expense that needs to be paid (e.g. Monthly Electricity Bill).
    Previously 'Expense'.
    """
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    type = db.Column(SQLAlchemyEnum(ExpenseType), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    transactions = db.relationship('Transaction', backref='invoice', lazy=True)
    establishment = db.relationship('Establishment', backref='invoices')

class Transaction(db.Model):
    """
    Represents a payment made by a user.
    Previously 'Payment'.
    """
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True) # Can be null if it's just a general payment? Or required?
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    validation_status = db.Column(SQLAlchemyEnum(ValidationStatus), nullable=False, default=ValidationStatus.PENDING)
    validation_date = db.Column(db.DateTime, nullable=True)

    # Relationship to Proof
    proof = db.relationship('PaymentProof', backref='transaction', uselist=False, lazy=True)

class PaymentProof(db.Model):
    """
    Links to the uploaded proof file.
    """
    __tablename__ = 'payment_proofs'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
