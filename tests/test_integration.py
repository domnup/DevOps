import unittest
from app import app  # Import your Flask app instance


class TestModelAppIntegration(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_model_app_integration(self):
        # Valid test input that should work with the trained model
        form_data = {
            'temperature': '275.15',
            'pressure': '1013',
            'humidity': '85',
            'wind_speed': '3.6',
            'wind_deg': '180',
            'rain_1h': '0',
            'rain_3h': '0',
            'snow': '0',
            'clouds': '20'
        }

        response = self.client.post('/', data=form_data)

        # Form should return 200 OK
        self.assertEqual(response.status_code, 200)

        # Ensure that a weather prediction appears in HTML
        self.assertIn(b"Prediction", response.data)

        # Ensure latency appears
        self.assertIn(b"ms", response.data)

        # Check prediction belongs to valid classes
        html_text = response.data.decode('utf-8').lower()
        valid_classes = [
            'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
            'misty', 'rainy', 'smokey', 'thunderstorm'
        ]
        found = any(weather in html_text for weather in valid_classes)

        self.assertTrue(
            found,
            "Prediction not found in valid weather classes."
        )


if __name__ == '__main__':
    unittest.main()
