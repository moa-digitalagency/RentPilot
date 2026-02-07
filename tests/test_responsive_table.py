import unittest
import sys
import os

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.init_app import create_app

class ResponsiveTableTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_responsive_table_route(self):
        response = self.client.get('/responsive-table')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Management', response.data)
        # Check for card stack structure indicators
        self.assertIn(b'Card Stack', response.data)
        self.assertIn(b'data-label="ID"', response.data)

if __name__ == '__main__':
    unittest.main()
