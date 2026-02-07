
"""
* Nom de l'application : RentPilot
* Description : Source file: chores.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime
import enum

class ChoreStatus(enum.Enum):
    PENDING = 'Pending'
    DONE_WAITING_VALIDATION = 'Done_Waiting_Validation'
    COMPLETED = 'Completed'

class ChoreType(db.Model):
    """
    SECURITY WARNING: data from this model should NEVER be returned in API calls made by a user with role 'Bailleur',
    unless that landlord is also an occupant (which is rare).
    """
    __tablename__ = 'chore_types'

    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    frequency_days = db.Column(db.Integer, nullable=False, default=7)
    is_rotating = db.Column(db.Boolean, default=False)

    # Relationships
    events = db.relationship('ChoreEvent', backref='chore_type', lazy=True)

class ChoreEvent(db.Model):
    """
    SECURITY WARNING: data from this model should NEVER be returned in API calls made by a user with role 'Bailleur',
    unless that landlord is also an occupant (which is rare).
    """
    __tablename__ = 'chore_events'

    id = db.Column(db.Integer, primary_key=True)
    chore_type_id = db.Column(db.Integer, db.ForeignKey('chore_types.id'), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(SQLAlchemyEnum(ChoreStatus), default=ChoreStatus.PENDING, nullable=False)
    proof_image = db.Column(db.String(255), nullable=True)

    # Relationships
    validations = db.relationship('ChoreValidation', backref='event', lazy=True)

class ChoreValidation(db.Model):
    """
    SECURITY WARNING: data from this model should NEVER be returned in API calls made by a user with role 'Bailleur',
    unless that landlord is also an occupant (which is rare).
    """
    __tablename__ = 'chore_validations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('chore_events.id'), nullable=False)
    validator_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_validated = db.Column(db.Boolean, default=False)

    # Unique constraint: a user can only validate an event once
    __table_args__ = (
        db.UniqueConstraint('event_id', 'validator_user_id', name='unique_user_validation_per_event'),
    )