
"""
* Nom de l'application : RentPilot
* Description : Source file: init_db.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
from config.init_app import create_app
from config.extensions import db
from models import (
    User, Establishment, Room, Lease, UserRole, FinancialMode,
    ChatRoom, ChannelType, PlatformSettings, SubscriptionPlan, ReceiptFormat,
    EstablishmentOwner, EstablishmentOwnerRole,
    Invoice, Transaction, PaymentProof, ExpenseType, ValidationStatus, SaaSInvoice, SaaSInvoiceStatus, PaymentMethod,
    Message, MessageType, Announcement, AnnouncementSenderType, AnnouncementTargetAudience, AnnouncementPriority,
    Ad, Request, Ticket, ChoreType, ChoreEvent, ChoreValidation, ChoreStatus
)
from security.pwd_tools import hash_password
from datetime import date
from sqlalchemy import inspect, text

def init_db():
    app = create_app()
    with app.app_context():
        # Ensure upload directories exist
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            print(f"Created upload folder: {upload_folder}")

        upload_chat_folder = app.config.get('UPLOAD_FOLDER_CHAT')
        if upload_chat_folder and not os.path.exists(upload_chat_folder):
            os.makedirs(upload_chat_folder)
            print(f"Created chat upload folder: {upload_chat_folder}")

        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Connecting to database: {db_uri}")
        if not db_uri.startswith('postgresql'):
             raise ValueError("RentPilot requires PostgreSQL. Please check your configuration.")

        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Iterate all models to check/create tables
        # We manually list them or inspect registry. Here we use the registry for robustness.
        # But for safety and specific imports above, we can rely on `db.Model.registry.mappers`
        # ensuring all imported models are registered.

        mapped_classes = [mapper.class_ for mapper in db.Model.registry.mappers]
        processed_tables = set()

        if not existing_tables:
            print("No tables found. Creating all tables...")
            db.create_all()
        else:
            print("Tables found. Running generic migration check...")
            # Create any missing tables (e.g. new models)
            db.create_all()

            # Check existing tables for missing columns
            for model_class in mapped_classes:
                if not hasattr(model_class, '__tablename__'):
                    continue

                table_name = model_class.__tablename__
                if table_name in processed_tables:
                    continue
                processed_tables.add(table_name)

                if table_name in existing_tables:
                    # Get existing columns in DB
                    existing_columns = [c['name'] for c in inspector.get_columns(table_name)]

                    # Iterate model columns
                    for column in model_class.__table__.columns:
                        if column.name not in existing_columns:
                            print(f"Migrating: Adding column '{column.name}' to table '{table_name}'")

                            # Determine column type safely
                            col_type = column.type.compile(db.engine.dialect)

                            # Construct ALTER TABLE
                            # Handle default value if NOT NULL is required to prevent errors
                            default_clause = ""
                            if not column.nullable and column.server_default is None:
                                 # Infer safe default based on type for migration
                                 type_str = str(col_type).upper()
                                 if "BOOLEAN" in type_str:
                                     default_clause = " DEFAULT FALSE" # Postgres boolean false
                                 elif "INT" in type_str:
                                     default_clause = " DEFAULT 0"
                                 else:
                                     default_clause = " DEFAULT ''"
                            elif column.server_default:
                                default_clause = f" DEFAULT {column.server_default.arg}"

                            sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {col_type}{default_clause}'

                            try:
                                with db.engine.connect() as conn:
                                    conn.execute(text(sql))
                                    conn.commit()
                                print(f"Successfully added column '{column.name}' to '{table_name}'")
                            except Exception as e:
                                print(f"Failed to add column '{column.name}' to '{table_name}': {e}")

            # Specific migration for Ads room_id nullable (PostgreSQL)
            # This is a bit risky if generic logic didn't pick it up or if we are not on Postgres
            try:
                if 'ads' in existing_tables:
                    # Check if we are on Postgres
                    if str(db.engine.url).startswith('postgresql'):
                        sql_alter = 'ALTER TABLE "ads" ALTER COLUMN "room_id" DROP NOT NULL'
                        with db.engine.connect() as conn:
                             conn.execute(text(sql_alter))
                             conn.commit()
                        print("Successfully altered 'ads.room_id' to allow NULL (PostgreSQL).")
            except Exception as e:
                print(f"Failed to alter 'ads.room_id' constraint: {e}")

        print("Database schema check complete.")

        # Seed Platform Settings
        if not PlatformSettings.query.first():
            settings = PlatformSettings(
                receipt_format=ReceiptFormat.A4_Standard,
                whatsapp_contact_number="+33612345678",
                footer_text="Bienvenue sur RentPilot, la solution moderne pour gérer vos biens.",
                copyright_text="© 2024 RentPilot Demo. Tous droits réservés.",
                social_media_config={"facebook": "https://facebook.com/rentpilot", "twitter": "https://twitter.com/rentpilot"},
                footer_links=[{"label": "Mentions Légales", "url": "/legal"}, {"label": "Support", "url": "/support"}]
            )
            db.session.add(settings)
            db.session.commit()
            print("Initialized Platform Settings with V4 defaults.")

        # Seed Subscription Plans
        if not SubscriptionPlan.query.first():
            free_plan = SubscriptionPlan(
                name="Gratuit",
                price_monthly=0.0,
                currency="EUR",
                features_json={"max_rooms": 3, "enable_chat": True, "support": "basic"},
                is_active=True
            )
            pro_plan = SubscriptionPlan(
                name="Pro",
                price_monthly=29.99,
                currency="EUR",
                features_json={"max_rooms": 100, "enable_chat": True, "support": "priority", "branding": True},
                is_active=True
            )
            db.session.add_all([free_plan, pro_plan])
            db.session.commit()
            print("Initialized Subscription Plans.")

        # Seed Data (Check if Landlord exists to avoid duplicates)
        if not User.query.filter_by(email='landlord@demo.com').first():
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
                address='123 Demo Street, Paris',
                fuzzy_location='Paris 1er Arrondissement (approx)',
                config_financial_mode=FinancialMode.EGAL,
                wifi_cost=29.99,
                syndic_cost=50.0,
                expense_types_config=["Loyer", "Eau", "Internet", "Ménage"]
            )
            db.session.add(establishment)
            db.session.commit()

            # Add Landlord association
            assoc = EstablishmentOwner(
                user_id=landlord.id,
                establishment_id=establishment.id,
                role=EstablishmentOwnerRole.PRIMARY
            )
            db.session.add(assoc)
            db.session.commit()
            print("Added Establishment and Landlord association.")

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
        else:
            print("Demo data already exists, skipping seed.")

if __name__ == '__main__':
    init_db()
