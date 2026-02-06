from flask import Flask
from config.settings import Config
from config.extensions import db
from models import User, Establishment, Room, Lease, UserRole, FinancialMode, ChatRoom, ChannelType
from security.pwd_tools import hash_password
from datetime import date

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_db():
    app = create_app()
    with app.app_context():
        print(f"Connecting to database: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Drop all tables
        db.drop_all()
        print("Dropped all tables.")

        # Create all tables
        db.create_all()
        print("Created all tables.")

        # Seed Data
        # 1 Bailleur (Landlord)
        landlord = User(
            role=UserRole.BAILLEUR,
            email='landlord@demo.com',
            password_hash=hash_password('password123'),
            avatar='default_avatar.png'
        )
        db.session.add(landlord)
        db.session.commit()
        print("Added Landlord.")

        # 1 Establishment
        establishment = Establishment(
            landlord_id=landlord.id,
            address='123 Demo Street, Paris',
            fuzzy_location='Paris 1er Arrondissement (approx)',
            config_financial_mode=FinancialMode.EGAL,
            wifi_cost=29.99,
            syndic_cost=50.0
        )
        db.session.add(establishment)
        db.session.commit()
        print("Added Establishment.")

        # Chat Rooms
        general_chat = ChatRoom(
            establishment_id=establishment.id,
            type=ChannelType.GENERAL,
            name="General"
        )
        coloc_chat = ChatRoom(
            establishment_id=establishment.id,
            type=ChannelType.COLOC_ONLY,
            name="Entre Colocs"
        )
        db.session.add_all([general_chat, coloc_chat])
        db.session.commit()
        print("Added Chat Rooms.")

        # 3 Rooms
        room1 = Room(establishment_id=establishment.id, name='Chambre 1', base_price=500.0, is_vacant=False)
        room2 = Room(establishment_id=establishment.id, name='Chambre 2', base_price=450.0, is_vacant=False)
        room3 = Room(establishment_id=establishment.id, name='Chambre 3', base_price=450.0, is_vacant=False)

        db.session.add_all([room1, room2, room3])
        db.session.commit()
        print("Added Rooms.")

        # 1 Tenant Responsable
        tenant_resp = User(
            role=UserRole.TENANT_RESPONSABLE,
            email='tenant_resp@demo.com',
            password_hash=hash_password('password123'),
            avatar='default_avatar.png'
        )
        db.session.add(tenant_resp)
        db.session.commit() # Commit to get ID for Lease

        # Lease for Tenant Resp (Room 1)
        lease1 = Lease(
            user_id=tenant_resp.id,
            room_id=room1.id,
            start_date=date(2023, 1, 1),
            end_date=date(2024, 1, 1)
        )
        db.session.add(lease1)

        # 2 Colocs
        coloc1 = User(
            role=UserRole.COLOCATAIRE,
            email='coloc1@demo.com',
            password_hash=hash_password('password123'),
            avatar='default_avatar.png'
        )
        coloc2 = User(
            role=UserRole.COLOCATAIRE,
            email='coloc2@demo.com',
            password_hash=hash_password('password123'),
            avatar='default_avatar.png'
        )
        db.session.add_all([coloc1, coloc2])
        db.session.commit() # Commit to get IDs

        # Leases for Colocs
        lease2 = Lease(
            user_id=coloc1.id,
            room_id=room2.id,
            start_date=date(2023, 2, 1),
            end_date=date(2024, 2, 1)
        )
        lease3 = Lease(
            user_id=coloc2.id,
            room_id=room3.id,
            start_date=date(2023, 3, 1),
            end_date=date(2024, 3, 1)
        )
        db.session.add_all([lease2, lease3])

        db.session.commit()

        print("Database initialized with demo data (1 Landlord, 1 Establishment, 3 Rooms, 1 Tenant Resp, 2 Colocs).")

if __name__ == '__main__':
    init_db()
