
"""
* Nom de l'application : RentPilot
* Description : Service logic for chat module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from models.communication import Message
from datetime import datetime

class ChatService:
    @staticmethod
    def mark_message_as_read(msg_id: int, user_id: int) -> bool:
        """
        Marks a message as read by a specific user.
        Adds the user ID and timestamp to the read_by_users JSON field.
        """
        msg = Message.query.get(msg_id)
        if not msg:
            return False

        # read_by_users is a list of dicts
        current_reads = msg.read_by_users
        if current_reads is None:
            current_reads = []

        # Check if user already read
        for entry in current_reads:
            if isinstance(entry, dict) and entry.get('user_id') == user_id:
                return False # Already read

        # Append new read entry
        new_entry = {
            "user_id": user_id,
            "read_at": datetime.utcnow().isoformat()
        }

        # Create a new list to ensure SQLAlchemy detects the change
        updated_reads = list(current_reads)
        updated_reads.append(new_entry)

        msg.read_by_users = updated_reads
        db.session.commit()

        return True