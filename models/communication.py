from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime
import enum

class ChannelType(enum.Enum):
    GENERAL = 'GENERAL'       # Bailleur + Tenants
    COLOC_ONLY = 'COLOC_ONLY' # Tenants only

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    type = db.Column(SQLAlchemyEnum(ChannelType), nullable=False)
    name = db.Column(db.String(100), nullable=True) # Optional name

    messages = db.relationship('Message', backref='chat_room', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Flag to distinguish is implicit via chat_room.type, but we can add a property/helper if needed.
