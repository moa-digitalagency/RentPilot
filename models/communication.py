from config.extensions import db
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime
import enum

class ChannelType(enum.Enum):
    GENERAL = 'GENERAL'       # Bailleur + Tenants
    COLOC_ONLY = 'COLOC_ONLY' # Tenants only

class MessageType(enum.Enum):
    TEXT = 'text'
    IMAGE = 'image'
    VOICE = 'voice'

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

    type = db.Column(SQLAlchemyEnum(MessageType), default=MessageType.TEXT, nullable=False)
    content = db.Column(db.Text, nullable=True) # Can be empty if just file?
    file_url = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=True) # Seconds, for voice

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # JSON list of dicts: [{"user_id": 1, "read_at": "ISO_TIMESTAMP"}]
    read_by_users = db.Column(db.JSON, default=list)

class AnnouncementSenderType(enum.Enum):
    SUPER_ADMIN = 'SuperAdmin'
    LANDLORD = 'Landlord'

class AnnouncementTargetAudience(enum.Enum):
    ALL_USERS = 'All_Users'
    SPECIFIC_ESTABLISHMENT = 'Specific_Establishment'

class AnnouncementPriority(enum.Enum):
    NORMAL = 'Normal'
    URGENT = 'Urgent'

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(SQLAlchemyEnum(AnnouncementSenderType), nullable=False)
    target_audience = db.Column(SQLAlchemyEnum(AnnouncementTargetAudience), nullable=False)

    # If specific establishment
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=True)

    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(SQLAlchemyEnum(AnnouncementPriority), default=AnnouncementPriority.NORMAL)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
