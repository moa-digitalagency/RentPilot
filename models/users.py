from config.extensions import db
from flask_login import UserMixin
import enum
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

class UserRole(enum.Enum):
    ADMIN = 'Admin'
    BAILLEUR = 'Bailleur'
    TENANT_RESPONSABLE = 'Tenant_Responsable'
    COLOCATAIRE = 'Colocataire'

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(SQLAlchemyEnum(UserRole), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (using string references to avoid circular imports)
    establishment_associations = db.relationship('EstablishmentOwner', back_populates='user', lazy=True, cascade='all, delete-orphan')
    leases = db.relationship('Lease', backref='tenant', lazy=True)
    transactions = db.relationship('Transaction', backref='payer', lazy=True)
    sent_messages = db.relationship('Message', backref='sender', lazy=True)
    tickets = db.relationship('Ticket', backref='requester', lazy=True)

    def get_id(self):
        return str(self.id)

    @property
    def is_tenant(self):
        return bool(self.leases)
