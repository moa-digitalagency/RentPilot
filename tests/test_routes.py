
"""
* Nom de l'application : RentPilot
* Description : Routes for test module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import sys
import os
import unittest
# from flask_login import login_user # Not needed if we use client.post

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.init_app import create_app
from config.extensions import db
from models.establishment import Establishment, FinancialMode, EstablishmentOwner, EstablishmentOwnerRole
from models.users import User, UserRole
from models.finance import Transaction, SaaSInvoice
from models.communication import Message, ChatRoom, MessageType, ChannelType
from datetime import datetime
from security.pwd_tools import hash_password

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create User
        self.user = User(email="landlord@test.com", role=UserRole.BAILLEUR, password_hash=hash_password("password"))
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/login', data=dict(
            email="landlord@test.com",
            password="password"
        ), follow_redirects=True)

    def test_public_verification(self):
        # Create Transaction
        trx = Transaction(
            ticket_number="TRX-TEST-123",
            amount=100.0,
            date=datetime.utcnow(),
            user_id=self.user.id
        )
        db.session.add(trx)
        db.session.commit()

        # Test Valid
        resp = self.client.get('/verify/receipt/TRX-TEST-123')
        self.assertEqual(resp.status_code, 200)
        # Check for content in public_verification.html
        self.assertIn(b"Certificat Authentique", resp.data)

        # Test Invalid
        resp = self.client.get('/verify/receipt/INVALID')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Ticket Invalide", resp.data)

    def test_establishment_setup_post(self):
        self.login()

        # Post data including custom_expenses
        data = {
            'address': 'New Address',
            'split_mode': 'Surface',
            'custom_expenses': ['Parking', 'Gardien']
        }
        resp = self.client.post('/establishment/setup', data=data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        est = Establishment.query.join(EstablishmentOwner).filter(EstablishmentOwner.user_id == self.user.id).first()
        self.assertIsNotNone(est)
        self.assertEqual(est.address, 'New Address')
        self.assertEqual(est.config_financial_mode, FinancialMode.INEGAL)
        self.assertEqual(est.expense_types_config, ['Parking', 'Gardien'])

    def test_chat_read(self):
        self.login()

        # Create Est
        est = Establishment(address="Chat Est")
        db.session.add(est)
        db.session.commit()

        owner = EstablishmentOwner(user_id=self.user.id, establishment_id=est.id, role=EstablishmentOwnerRole.PRIMARY)
        db.session.add(owner)
        db.session.commit()

        # Create Room
        room = ChatRoom(establishment_id=est.id, type=ChannelType.GENERAL)
        db.session.add(room)
        db.session.commit()

        # Create Message
        msg = Message(chat_room_id=room.id, sender_id=self.user.id, content="Hello", type=MessageType.TEXT)
        db.session.add(msg)
        db.session.commit()

        # Call read route
        resp = self.client.post(f'/chat/read/{msg.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"true", resp.data)

        # Check DB
        msg_check = Message.query.get(msg.id)
        self.assertTrue(len(msg_check.read_by_users) > 0)
        self.assertEqual(msg_check.read_by_users[0]['user_id'], self.user.id)

if __name__ == '__main__':
    unittest.main()