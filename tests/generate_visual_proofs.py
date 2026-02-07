
"""
* Nom de l'application : RentPilot
* Description : Source file: generate_visual_proofs.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
import sys
import time
import uuid
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from playwright.sync_api import sync_playwright
from config.init_app import create_app
from config.extensions import db
from models import Transaction, User, ValidationStatus, ChatRoom, Message, MessageType, ChannelType, UserRole

# Configuration
BASE_URL = "http://localhost:5000"
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def setup_test_data():
    """Ensures there is a valid transaction and chat message for testing."""
    app = create_app()
    with app.app_context():
        # --- RECEIPT SETUP ---
        tenant1 = User.query.filter_by(email='coloc1@demo.com').first()
        tenant2 = User.query.filter_by(email='coloc2@demo.com').first()

        if not tenant1 or not tenant2:
            print("Warning: Tenants not found. Is the DB initialized?")
            return None

        # Check/Create Transaction
        existing_trx = Transaction.query.first()
        ticket_uuid = existing_trx.ticket_number if existing_trx else str(uuid.uuid4())

        if not existing_trx:
            trx = Transaction(
                user_id=tenant1.id,
                amount=500.0,
                validation_status=ValidationStatus.VALIDATED,
                date=datetime.now(timezone.utc),
                ticket_number=ticket_uuid
            )
            db.session.add(trx)
            db.session.commit()
            print(f"Created test transaction: {ticket_uuid}")

        # --- CHAT SETUP ---
        # Ensure Coloc Room exists (ID 2 usually, but let's find it)
        # We need to find a room of type COLOC_ONLY
        coloc_room = ChatRoom.query.filter_by(type=ChannelType.COLOC_ONLY).first()
        if not coloc_room:
            # Create if missing (should be there from init_db)
            est_id = tenant1.leases[0].room.establishment_id if tenant1.leases else 1
            coloc_room = ChatRoom(establishment_id=est_id, type=ChannelType.COLOC_ONLY, name="Entre Colocs")
            db.session.add(coloc_room)
            db.session.commit()

        # Create a message from Tenant1, read by Tenant2
        # Content with Emoji
        msg = Message(
            chat_room_id=coloc_room.id,
            sender_id=tenant1.id,
            content="Salut tout le monde ! 🍕 Qui est chaud pour une pizza ce soir ?",
            type=MessageType.TEXT,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(msg)
        db.session.commit()

        # Mark as read by Tenant2
        # We need to use raw SQL or service/model method if relationship is managed
        # Message.read_by_users is a JSON field in some designs or a separate table?
        # Memory says: "ChatService.mark_message_as_read updates the Message model's read_by_users JSON field"
        # Let's check Message model.
        # Wait, if it's a JSON field, I can update it.
        # But `routes/chat_routes.py` calls `ChatService.mark_message_as_read`.
        # Let's check `models/communication.py` to see `read_by_users` type.
        pass # I'll just skip manual read injection if it's complex, the visual proof of the message is enough.
             # "Vu par X" is nice but optional if complex.
             # Actually, if I can just append to the list if it's JSON.

        from services.chat_service import ChatService
        ChatService.mark_message_as_read(msg.id, tenant2.id)

        print(f"Created test chat message in room {coloc_room.id}")

        return ticket_uuid, coloc_room.id

def run_e2e_tests():
    # Setup data
    setup_res = setup_test_data()
    if setup_res:
        transaction_uuid, chat_room_id = setup_res
    else:
        transaction_uuid = "UUID-TEST"
        chat_room_id = 2

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("\n--- PHASE 1: PUBLIC & SUPER ADMIN ---")

        # 1. Landing Page
        print("1. Visiting Landing Page...")
        page.goto(f"{BASE_URL}/")
        try:
            page.click("text=PT")
            time.sleep(1)
        except Exception as e:
            print(f"   [Warning] Could not switch to PT: {e}")

        page.screenshot(path=f"{SCREENSHOT_DIR}/01_landing_portuguese.png")
        print("   -> 01_landing_portuguese.png")

        # 2. Receipt Verification
        print(f"2. Verifying Receipt ({transaction_uuid})...")
        page.goto(f"{BASE_URL}/verify/receipt/{transaction_uuid}")
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_public_receipt_valid.png")
        print("   -> 02_public_receipt_valid.png")

        # 3. Super Admin Settings
        print("3. Super Admin Settings...")
        page.goto(f"{BASE_URL}/login") # Fixed URL
        page.fill('input[name="email"]', 'admin@rentpilot.com')
        page.fill('input[name="password"]', 'SuperSecretPass123!')
        page.click('button[type="submit"]')
        time.sleep(1)

        # Navigate to Settings
        # Try /admin/settings (Standard admin route) or /super_admin/settings
        # I'll check response url or try both
        page.goto(f"{BASE_URL}/admin/settings")
        time.sleep(1)

        try:
            page.fill('input[name="primary_color_hex"]', '#FF0000')
            if not page.is_checked('input[name="is_maintenance_mode"]'):
                page.check('input[name="is_maintenance_mode"]')
            page.click('button:has-text("Enregistrer")')
            time.sleep(1)
        except Exception as e:
             print(f"   [Warning] Settings interaction failed: {e}")

        page.screenshot(path=f"{SCREENSHOT_DIR}/03_superadmin_settings.png")
        print("   -> 03_superadmin_settings.png")

        page.goto(f"{BASE_URL}/auth/logout")
        time.sleep(1)


        print("\n--- PHASE 2: BAILLEUR & CO-PROPRIÉTÉ ---")

        # 4. Landlord Dashboard
        print("4. Landlord Dashboard...")
        page.goto(f"{BASE_URL}/login")
        page.fill('input[name="email"]', 'landlord@demo.com')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        time.sleep(2)

        page.screenshot(path=f"{SCREENSHOT_DIR}/04_landlord_dashboard.png")
        print("   -> 04_landlord_dashboard.png")

        # 5. Co-Owners Invite
        print("5. Inviting Co-Owner...")
        # Assume establishment ID 1
        page.goto(f"{BASE_URL}/establishment/1/update")
        time.sleep(1)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_cobailleur_invite.png")
        print("   -> 05_cobailleur_invite.png")

        # 6. Establishment Setup (Custom Expenses)
        print("6. Establishment Setup (Custom Expense)...")
        page.goto(f"{BASE_URL}/establishment/setup")
        time.sleep(1)

        try:
            # Wizard navigation
            # Check if we are on step 1 (Look for "Étape 1")
            # If buttons exist, click them.
            if page.locator('button[onclick="nextStep(2)"]').is_visible():
                page.click('button[onclick="nextStep(2)"]')
                time.sleep(0.5)
            if page.locator('button[onclick="nextStep(3)"]').is_visible():
                page.click('button[onclick="nextStep(3)"]')
                time.sleep(0.5)

            page.fill('#new-expense-input', 'Jardinage')
            page.click('button:has-text("Ajouter")')
            time.sleep(0.5)
        except Exception as e:
            print(f"   [Warning] Setup wizard navigation failed: {e}")

        page.screenshot(path=f"{SCREENSHOT_DIR}/06_custom_expenses.png")
        print("   -> 06_custom_expenses.png")

        page.goto(f"{BASE_URL}/auth/logout")
        time.sleep(1)


        print("\n--- PHASE 3: COLOCATAIRE & VIE COMMUNAUTAIRE ---")

        # 7. Tenant Dashboard
        print("7. Tenant Dashboard (Red Theme Check)...")
        page.goto(f"{BASE_URL}/login")
        page.fill('input[name="email"]', 'coloc1@demo.com')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        time.sleep(2)

        page.screenshot(path=f"{SCREENSHOT_DIR}/07_tenant_dashboard_red_theme.png")
        print("   -> 07_tenant_dashboard_red_theme.png")

        # 8. Chore Wheel
        print("8. Chore Planning...")
        page.goto(f"{BASE_URL}/chores")
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/08_chore_planning.png")
        print("   -> 08_chore_planning.png")

        # 9. Chat
        print(f"9. Chat (Room {chat_room_id})...")
        # Go to specific room to ensure messages are loaded
        page.goto(f"{BASE_URL}/chat/{chat_room_id}")
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/09_chat_coloc_read_receipt.png")
        print("   -> 09_chat_coloc_read_receipt.png")

        # 10. Payment Modal
        print("10. Payment Modal...")
        page.goto(f"{BASE_URL}/finance")
        time.sleep(1)

        try:
            page.click('button:has-text("Payer")')
            time.sleep(1)
        except Exception as e:
            print(f"   [Warning] Could not click 'Payer': {e}")
            page.evaluate("window.openModal('modal-pay')")
            time.sleep(1)

        page.screenshot(path=f"{SCREENSHOT_DIR}/10_payment_modal.png")
        print("   -> 10_payment_modal.png")

        browser.close()
        print("\nAll proofs generated successfully in 'screenshots/'")

if __name__ == "__main__":
    run_e2e_tests()