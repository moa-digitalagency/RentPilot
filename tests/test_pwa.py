
import unittest
from config.init_app import create_app
from config.extensions import db
from models import PlatformSettings

class PWATestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            settings = PlatformSettings(app_name="TestApp")
            db.session.add(settings)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_manifest_disabled(self):
        """Test manifest returns 404 when PWA is disabled (default)"""
        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 404)

    def test_manifest_enabled_default(self):
        """Test manifest returns JSON when PWA is enabled with default settings"""
        with self.app.app_context():
            settings = PlatformSettings.query.first()
            settings.pwa_enabled = True
            db.session.commit()

        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], "TestApp")
        self.assertEqual(data['display'], "standalone")
        # Should have fallback icon (logo.png)
        self.assertTrue(len(data['icons']) > 0)
        self.assertEqual(data['icons'][0]['src'], "/static/img/logo.png")

    def test_manifest_enabled_custom(self):
        """Test manifest returns custom JSON when PWA is enabled with custom settings"""
        with self.app.app_context():
            settings = PlatformSettings.query.first()
            settings.pwa_enabled = True
            settings.pwa_display_mode = 'custom'
            settings.pwa_custom_name = "CustomApp"
            settings.pwa_custom_icon_url = "/static/custom.png"
            db.session.commit()

        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], "CustomApp")
        self.assertEqual(data['short_name'], "CustomApp")
        self.assertEqual(data['icons'][0]['src'], "/static/custom.png")

if __name__ == '__main__':
    unittest.main()
