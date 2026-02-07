
"""
* Nom de l'application : RentPilot
* Description : Source file: maintenance.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Linking to establishment helps if the user has multiple (unlikely for tenant but good for data integrity)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.String(50), default='Normal')
    status = db.Column(db.String(50), nullable=False, default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)