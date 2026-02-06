import sys
import os
import unittest
import io
from PIL import Image

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.init_app import create_app
from config.extensions import db
from models.establishment import Establishment, SaaSBilledTo
from models.finance import SaaSInvoice, Invoice, ExpenseType, SaaSInvoiceStatus, PaymentMethod
from models.saas_config import SubscriptionPlan, PlatformSettings
from models.users import User, UserRole
from services.billing_service import BillingService
from services.branding_service import BrandingService
from services.seo_manager import SEOManager
from services.chat_media_service import ChatMediaService
from werkzeug.datastructures import FileStorage

class TestServices(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Setup basic data
        user = User(role=UserRole.BAILLEUR, email="test@test.com", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        self.user = user

        self.plan = SubscriptionPlan(name="ProTest", price_monthly=50.0, is_active=True)
        db.session.add(self.plan)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_branding_service(self):
        # Default
        theme = BrandingService.get_active_theme()
        self.assertEqual(theme['app_name'], 'RentPilot')

        # Update Settings
        settings = PlatformSettings(app_name="TestApp", primary_color_hex="#000000")
        db.session.add(settings)
        db.session.commit()

        theme = BrandingService.get_active_theme()
        self.assertEqual(theme['app_name'], 'TestApp')
        self.assertEqual(theme['primary_color'], '#000000')

    def test_seo_manager(self):
        tags = SEOManager.get_meta_tags("Home")
        self.assertIn("Home | RentPilot", tags['title'])

        sitemap = SEOManager.generate_sitemap("http://localhost")
        self.assertIn("<loc>http://localhost/login</loc>", sitemap)

    def test_chat_media_service(self):
        # Create dummy image
        img = Image.new('RGB', (100, 100), color = 'red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)

        file = FileStorage(stream=img_io, filename="test.jpg", content_type="image/jpeg")

        path = ChatMediaService.process_and_save(file)
        self.assertTrue(path.endswith('.jpg'))
        self.assertTrue(os.path.exists(path))

        # Cleanup
        if os.path.exists(path):
            os.remove(path)

    def test_billing_service_landlord(self):
        # Create Establishment
        est = Establishment(
            landlord_id=self.user.id, address="Test",
            saas_billed_to=SaaSBilledTo.LANDLORD,
            subscription_plan_id=self.plan.id
        )
        db.session.add(est)
        db.session.commit()

        # Generate
        count = BillingService.generate_monthly_invoices()
        self.assertEqual(count, 1)

        # Verify SaaS Invoice
        saas_inv = SaaSInvoice.query.filter_by(establishment_id=est.id).first()
        self.assertIsNotNone(saas_inv)
        self.assertEqual(saas_inv.amount, 50.0)

        # Verify NO Internal Invoice
        internal_inv = Invoice.query.filter_by(establishment_id=est.id).first()
        self.assertIsNone(internal_inv)

    def test_billing_service_tenant(self):
        # Create Establishment
        est = Establishment(
            landlord_id=self.user.id, address="Test2",
            saas_billed_to=SaaSBilledTo.TENANTS,
            subscription_plan_id=self.plan.id
        )
        db.session.add(est)
        db.session.commit()

        # Generate
        count = BillingService.generate_monthly_invoices()
        self.assertEqual(count, 1)

        # Verify SaaS Invoice
        saas_inv = SaaSInvoice.query.filter_by(establishment_id=est.id).first()
        self.assertIsNotNone(saas_inv)

        # Verify Internal Invoice
        internal_inv = Invoice.query.filter_by(establishment_id=est.id, type=ExpenseType.SAAS).first()
        self.assertIsNotNone(internal_inv)
        self.assertEqual(internal_inv.amount, 50.0)

    def test_offline_payment(self):
        est = Establishment(
            landlord_id=self.user.id, address="Test3",
            subscription_plan_id=self.plan.id
        )
        db.session.add(est)
        db.session.commit()
        BillingService.generate_monthly_invoices()
        saas_inv = SaaSInvoice.query.filter_by(establishment_id=est.id).first()

        # Mock Proof
        proof_io = io.BytesIO(b"dummy pdf content")
        file = FileStorage(stream=proof_io, filename="proof.pdf", content_type="application/pdf")

        updated_inv = BillingService.handle_offline_payment(saas_inv.id, file)

        self.assertEqual(updated_inv.status, SaaSInvoiceStatus.OFFLINE_PENDING)
        self.assertEqual(updated_inv.payment_method, PaymentMethod.OFFLINE)
        self.assertTrue(updated_inv.proof_file_path.endswith('.pdf'))

        if os.path.exists(updated_inv.proof_file_path):
            os.remove(updated_inv.proof_file_path)

if __name__ == '__main__':
    unittest.main()
