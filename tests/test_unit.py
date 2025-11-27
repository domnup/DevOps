import unittest
from app import app, classify_weather, load_model
import numpy as np

class TestUnit(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    # Test missing required field (wind_speed missing)
    def test_post_missing_field(self):
        form_data = {
            'temperature': '270.277',
            'pressure': '1006',
            'humidity': '84',
            # 'wind_speed' missing on purpose
            'wind_deg': '274',
            'rain_1h': '0',
            'rain_3h': '0',
            'snow': '0',
            'clouds': '9'
        }
        response = self.client.post('/', data=form_data)

        # Should reload form with "Error processing input" message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Missing", response.data)  # error message appears

    # Test model loads without error
    def test_model_can_be_loaded(self):
        model = load_model()
        self.assertIsNotNone(model)

    # CLEAR classification test
    def test_clear_classification_output(self):
        test_input = np.array([269.686,1002,78,0,23,0,0,0,0], dtype=float)
        class_result, _ = classify_weather(test_input)
        self.assertIn(class_result, [
            'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
            'misty', 'rainy', 'smokey', 'thunderstorm'
        ])

    # RAINY classification test
    def test_rainy_classification_output(self):
        test_input = np.array([279.626,998,99,1,314,0.3,0,0,88], dtype=float)
        class_result, _ = classify_weather(test_input)
        self.assertIn(class_result, [
            'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
            'misty', 'rainy', 'smokey', 'thunderstorm'
        ])

    # FOGGY classification test
    def test_foggy_classification_output(self):
        test_input = np.array([289.47,1015,88,2,300,0,0,0,20], dtype=float)
        class_result, _ = classify_weather(test_input)
        self.assertIn(class_result, [
            'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
            'misty', 'rainy', 'smokey', 'thunderstorm'
        ])

if __name__ == '__main__':
    unittest.main()
