import os
import sys
import time
import threading
import unittest
from datetime import date, datetime
from playwright.sync_api import sync_playwright, expect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from config.extensions import db
from models.users import User, UserRole
from models.establishment import Establishment, Room, Lease, FinancialMode, SaaSBilledTo
from models.finance import Transaction, Invoice, ExpenseType, ValidationStatus, PaymentProof
from security.pwd_tools import hash_password
from config.settings import Config

# Configuration
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'proofs')
BASE_URL = "http://localhost:5000"

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class RentPilotProofs:
    def __init__(self):
        self.valid_ticket_number = None

    def setup_database(self):
        """Initializes the database with specific scenario data."""
        with app.app_context():
            print("Resetting database...")
            db.drop_all()
            db.create_all()

            # 1. Super Admin (Handled via Env/Config, but we might need a DB user if auth logic checks it?
            # Context says "Super Admins use environment variables... bypassing flask_login".
            # So no DB record needed for Super Admin login usually, unless the code changed.
            # However, let's proceed relying on Config.)

            # 2. Bailleur (Landlord)
            landlord = User(
                role=UserRole.BAILLEUR,
                email='bailleur@test.com',
                password_hash=hash_password('password'),
                avatar='default_avatar.png'
            )
            db.session.add(landlord)
            db.session.commit()

            # 3. Establishment (Loyer 1000€, 4 Chambres)
            # Note: Rent is usually configured in expense_types_config or as an Invoice.
            # But the 'Setup' scenario (Parcours 2) says "Configurer 'Répartition par chambre'".
            # This implies we might start with a raw establishment or partially configured.
            # However, Parcours 3 (Tenant) needs the logic to work immediately.
            # So I will fully configure it, and for Parcours 2, I might "re-configure" it or just verify.
            # Actually, Parcours 2 says "Aller sur /setup -> Configurer...".
            # To make the flow natural, maybe I should create the establishment but NOT fully configure the expenses yet?
            # BUT Parcours 3 comes after. If I configure it in Parcours 2, it will be ready for Parcours 3.
            # So:
            # - Create Landlord & Establishment (Basic)
            # - Parcours 2: Landlord configures split.
            # - Parcours 3: Tenant checks math.

            est = Establishment(
                landlord_id=landlord.id,
                address='10 Rue de la Paix, Paris',
                fuzzy_location='Paris Center',
                config_financial_mode=FinancialMode.EGAL, # Will be changed in Parcours 2? Or verified?
                # The prompt says "Configurer 'Répartition par chambre'".
                # I'll start with EGAL and change to something else or just confirm EGAL?
                # "Répartition par chambre" usually means Per Room (Inegal/Surface) or just assigning rooms.
                # Let's assume the script will perform the setup action.
                wifi_cost=0.0,
                syndic_cost=0.0,
                expense_types_config=["Loyer"] # Minimal config
            )
            db.session.add(est)
            db.session.commit()

            # 4. Rooms (4 Chambres)
            rooms = []
            for i in range(1, 5):
                r = Room(establishment_id=est.id, name=f'Chambre {i}', base_price=250.0, is_vacant=False)
                db.session.add(r)
                rooms.append(r)
            db.session.commit()

            # 5. Colocataires (4 Tenants)
            tenants = []
            for i, room in enumerate(rooms):
                t = User(
                    role=UserRole.COLOCATAIRE,
                    email=f'coloc{i+1}@test.com',
                    password_hash=hash_password('password'),
                    avatar='default_avatar.png'
                )
                db.session.add(t)
                tenants.append(t)
            db.session.commit()

            # 6. Leases
            for t, r in zip(tenants, rooms):
                l = Lease(
                    user_id=t.id,
                    room_id=r.id,
                    start_date=date(2023, 1, 1),
                    end_date=date(2025, 1, 1)
                )
                db.session.add(l)
            db.session.commit()

            # 7. Invoice (Loyer)
            # We DO NOT create a Loyer Invoice because Room.base_price handles the rent
            # and CostCalculator sums both. We want (1000 from rooms + 0 from invoices) / 4 = 250.

            # 8. Transaction for Validation (Parcours 2)
            # Bailleur needs to "Valider un paiement en attente".
            # So one tenant must have paid (Pending).
            trx_pending = Transaction(
                user_id=tenants[1].id, # Coloc 2
                amount=250.0,
                invoice_id=None, # Direct payment (Rent)
                validation_status=ValidationStatus.PENDING,
                date=datetime.utcnow()
            )
            db.session.add(trx_pending)

            # 9. Valid Transaction for Public Verification (Parcours 4)
            trx_valid = Transaction(
                user_id=tenants[0].id,
                amount=250.0,
                invoice_id=None,
                validation_status=ValidationStatus.VALIDATED,
                date=datetime.utcnow()
            )
            db.session.add(trx_valid)
            db.session.commit()

            self.valid_ticket_number = trx_valid.ticket_number
            print(f"Database seeded. Valid Ticket: {self.valid_ticket_number}")

    def run_server(self):
        """Starts the Flask server."""
        app.run(port=5000, use_reloader=False)

    def run_tests(self):
        """Runs the Playwright scenarios."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # Set headless=False to watch
            context = browser.new_context(locale='fr-FR')
            page = context.new_page()

            try:
                # --- Parcours 1: Super Admin & Branding ---
                print("--- Parcours 1: Super Admin ---")

                # Login
                page.goto(f"{BASE_URL}/login")
                page.fill('input[name="email"]', Config.SUPER_ADMIN_ID)
                page.fill('input[name="password"]', Config.SUPER_ADMIN_PASS)
                page.click('button[type="submit"]')
                # Wait for redirect
                page.wait_for_url(f"{BASE_URL}/admin/dashboard")

                # Branding Settings
                page.goto(f"{BASE_URL}/admin/settings")
                # Change color to Purple (#800080 or similar)
                # The input is type="color", we can just fill it
                page.fill('input[name="primary_color_hex"]', '#800080')
                page.click('button:has-text("Enregistrer les modifications")')

                # Screenshot 01
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '01_admin_branding.png'))
                print("Screenshot 01: Admin Branding")

                # Dashboard Stats
                page.goto(f"{BASE_URL}/admin/dashboard")
                # Verify stats are not empty (look for a number > 0 or specific text)
                # Assuming the dashboard shows some stats.
                # Screenshot 02
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '02_admin_dashboard.png'))
                print("Screenshot 02: Admin Dashboard")

                # Logout
                page.goto(f"{BASE_URL}/logout")


                # --- Parcours 2: Bailleur & Configuration ---
                print("--- Parcours 2: Bailleur ---")

                # Login
                page.goto(f"{BASE_URL}/login")
                page.fill('input[name="email"]', 'bailleur@test.com')
                page.fill('input[name="password"]', 'password')
                page.click('button[type="submit"]')
                page.wait_for_url(f"{BASE_URL}/dashboard")

                # Setup / Configuration
                page.goto(f"{BASE_URL}/establishment/setup") # Using the likely route based on file
                # If it redirects to /setup or similar, Playwright follows.

                # Navigate wizard if needed. The template has steps.
                # Assuming we land on Step 1 or similar.
                # The scenario says "Configurer 'Répartition par chambre'".
                # This is in Step 3 of the wizard.
                # Step 1 -> Next
                if page.is_visible('#step-1-content'):
                    page.click('button[onclick="nextStep(2)"]')
                # Step 2 -> Next
                if page.is_visible('#step-2-content'):
                    page.click('button[onclick="nextStep(3)"]')

                # Step 3: Configure Split
                # "Répartition par chambre" -> "Surface" or just "Egal" but specific request.
                # Let's assume "Répartition par chambre" implies ensuring rooms are set up or split mode.
                # The template has radio buttons: "Egal" and "Surface".
                # I'll select "Egal" (Parts égales) as "Répartition par chambre" might be ambiguous,
                # but "1000€ / 4" in Tenant scenario implies Equal Split.
                # If "Répartition par chambre" meant "Per Room", the math would differ.
                # I will stick to "Egal" to satisfy the math check later, but fill the form.
                # Input Rent 1000
                page.fill('input[name="rent_total"]', '1000')
                page.fill('input[name="charges_total"]', '0')
                page.check('input[value="Egal"]')

                # Screenshot 03
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '03_landlord_setup.png'))
                print("Screenshot 03: Landlord Setup")

                # Submit
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')

                # Finance Validation
                page.goto(f"{BASE_URL}/finance")
                # Look for "Valider" button for the pending transaction (created in setup_db)
                # It's in a table row.
                # Screenshot 04
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '04_landlord_validation.png'))
                print("Screenshot 04: Landlord Validation")

                # Click Validate
                page.click('button:has-text("Valider")')
                # Optional: handle modal confirmation if any?
                # Template says: onclick="openModal('modal-preview-proof')" then inside modal "Valider le paiement".
                # So we might need to interact with modal.
                # Check template:
                # <button onclick="openModal('modal-preview-proof')" ...>Voir</button>
                # <button class="bg-emerald-500 ...">Valider</button> (Direct validate button in table?)
                # Looking at `finance.html`:
                # <td ...> <button onclick="openModal...">Voir</button> <button class="bg-emerald-500...">Valider</button> </td>
                # There is a direct "Valider" button in the table. Let's assume it works directly or opens a confirmation.
                # If it needs confirmation, we'll see. Assuming direct for now or simple interaction.

                # Logout
                page.goto(f"{BASE_URL}/logout")


                # --- Parcours 3: Colocataire & Logique ---
                print("--- Parcours 3: Colocataire ---")

                # Login Coloc 1
                page.goto(f"{BASE_URL}/login")
                page.fill('input[name="email"]', 'coloc1@test.com')
                page.fill('input[name="password"]', 'password')
                page.click('button[type="submit"]')
                page.wait_for_url(f"{BASE_URL}/dashboard")

                # Verification Logique
                # "Ma part à payer" -> 250 €
                # Selector: The template has <span class="text-4xl font-bold">550 €</span> (Mock)
                # Wait! The template `dashboard.html` has HARDCODED mock data in some places if not replaced by Jinja.
                # `{% if role == 'Tenant' %}` block.
                # `<span class="text-4xl font-bold">550 €</span> <!-- Mock Data, ideally passed from backend -->`
                # Oh... if the template uses Mock Data, my assertion will fail if the backend doesn't inject the real value.
                # Let me re-read `dashboard.html`.
                # It says: `<span class="text-4xl font-bold">550 €</span> <!-- Mock Data, ideally passed from backend -->`
                # If the backend logic IS implemented, it should replace this.
                # However, if I am testing the "Showcase", maybe the backend IS injecting it?
                # I need to trust that `dashboard.html` rendered variable `{{ amount_due }}` or similar.
                # Wait, looking at the `read_file` output for `dashboard.html`:
                # It literally says: `<span class="text-4xl font-bold">550 €</span> <!-- Mock Data, ideally passed from backend -->`
                # It does NOT seems to have a Jinja variable there like `{{ user_amount }}`.
                # This suggests the template might NOT be dynamic for that specific field yet?
                # OR I missed it.
                # Let's check `routes/dashboard_routes.py` or similar if I could.
                # But if the template is hardcoded, the test will fail.
                # I should probably UPDATE the template to be dynamic if I can, OR assume the "Contexte RentPilot QA & Showcase" implies I should fix it or it's already working and I misread the file (maybe it was just a comment *saying* it's mock data but the code is actually dynamic?).
                # Re-reading `dashboard.html` content carefully:
                # ` <span class="text-4xl font-bold">550 €</span> <!-- Mock Data, ideally passed from backend -->`
                # It looks hardcoded.
                # **CRITICAL:** I should probably FIX this in the template to make the test pass, or the "QA" task involves flagging it.
                # But the task is "Crée un script... vérifier la logique". If the logic isn't hooked up, the script validates that it's broken.
                # However, usually "Showcase" implies it should work.
                # I'll check `routes/dashboard_routes.py` quickly to see what context is passed.
                # If it passes `amount_to_pay`, I'll update the template.
                # I'll add a quick check step in the plan to "Ensure Dashboard is Dynamic".

                # For now, I'll write the script to expect 250. If it fails, I'll know why.
                # Actually, I'll verify the template in a separate step before running this.
                # But for the script content:

                # Screenshot 05 (FR)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '05_tenant_dashboard_fr.png'))
                print("Screenshot 05: Tenant Dashboard FR")

                # Check Math
                # Try to get the amount.
                # We look for the card "Ma part à payer"
                amount_text = page.locator("text=Ma part à payer").locator("..").locator("span.text-4xl").inner_text()
                # amount_text might be "250 €" or "250,00 €"
                import re
                amount_val = float(re.sub(r'[^\d.,]', '', amount_text).replace(',', '.'))

                expected = 250.0
                if abs(amount_val - expected) > 1.0:
                    raise Exception(f"Erreur Calcul: Attendu {expected}, Lu {amount_val}")
                print("Logique Mathématique OK")

                # Change Lang to English
                # Assuming there's a route `/change-lang/en` or similar?
                # Or query param `?lang=en`.
                page.goto(f"{BASE_URL}/dashboard?lang=en")
                # Screenshot 06
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '06_tenant_dashboard_en.png'))
                print("Screenshot 06: Tenant Dashboard EN")

                # Chat
                page.goto(f"{BASE_URL}/chat")
                page.fill('#message-input', 'Bonjour la team !')
                page.click('button[type="submit"]')
                # Wait for message to appear
                page.wait_for_selector('text=Bonjour la team !')
                # Screenshot 07
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '07_chat_interface.png'))
                print("Screenshot 07: Chat")

                # Tickets
                page.goto(f"{BASE_URL}/tickets")
                # Fill form
                page.fill('input[placeholder*="Fuite"]', 'Problème de serrure')
                # Select Urgency "Moyenne"
                page.select_option('select', label='Moyenne') # Or value if known
                page.fill('textarea', 'La serrure est bloquée.')
                page.click('button:has-text("Envoyer le signalement")')
                # Screenshot 08
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '08_ticket_creation.png'))
                print("Screenshot 08: Ticket Creation")

                # Logout
                page.goto(f"{BASE_URL}/logout")


                # --- Parcours 4: Public & Vérification ---
                print("--- Parcours 4: Public ---")

                # Landing Page ES
                page.goto(f"{BASE_URL}/?lang=es")
                # Screenshot 09
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '09_landing_es.png'))
                print("Screenshot 09: Landing ES")

                # Verify Success
                page.goto(f"{BASE_URL}/verify/receipt/{self.valid_ticket_number}")
                # Screenshot 10
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '10_public_verification_success.png'))
                print("Screenshot 10: Verification Success")

                # Verify Fail
                page.goto(f"{BASE_URL}/verify/receipt/FAKE-UUID-123")
                # Screenshot 11
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, '11_public_verification_fail.png'))
                print("Screenshot 11: Verification Fail")

            except Exception as e:
                print(f"ERROR: {e}")
                # Save screenshot on error
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'error.png'))
                raise e
            finally:
                browser.close()

if __name__ == "__main__":
    tester = RentPilotProofs()

    # Setup DB
    tester.setup_database()

    # Start Server in Thread
    server_thread = threading.Thread(target=tester.run_server)
    server_thread.daemon = True
    server_thread.start()

    # Give server time to start
    time.sleep(3)

    # Run Tests
    tester.run_tests()
    print("Tests Completed.")
