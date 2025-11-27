import unittest
from app import app

class TestAppSmoke(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    # Test that the home page loads successfully
    def test_prediction_route_success(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # Test that the form is rendered correctly
    def test_get_form(self):
        response = self.client.get('/')
        self.assertIn(b"Weather Classification", response.data)
        self.assertIn(b"Temperature", response.data)


if __name__ == '__main__':
    unittest.main()
