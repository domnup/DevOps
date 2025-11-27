from flask import Flask, request, render_template
import pickle
import numpy as np
import time

app = Flask(__name__)

weather_classes = [
    'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
    'misty', 'rainy', 'smokey', 'thunderstorm'
]

def load_model(model_path='model/model.pkl'):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def classify_weather(features):
    """
    features: list or 1D array of numeric values.
    This function will always convert to a float numpy array before prediction.
    """
    # Force to a 2D float array
    features_arr = np.array(features, dtype=float).reshape(1, -1)

    model = load_model()
    start = time.time()
    prediction_index = int(model.predict(features_arr)[0])
    latency = round((time.time() - start) * 1000, 2)
    prediction = weather_classes[prediction_index]
    return prediction, latency

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            # Read raw strings from the form
            temperature_str = request.form.get('temperature', '').strip()
            pressure_str    = request.form.get('pressure', '').strip()
            humidity_str    = request.form.get('humidity', '').strip()
            wind_speed_str  = request.form.get('wind_speed', '').strip()
            wind_deg_str    = request.form.get('wind_deg', '').strip()

            # Basic required fields check
            required = {
                "temperature": temperature_str,
                "pressure": pressure_str,
                "humidity": humidity_str,
                "wind_speed": wind_speed_str,
                "wind_deg": wind_deg_str,
            }
            missing = [name for name, value in required.items() if value == ""]
            if missing:
                raise ValueError(f"Missing required field(s): {', '.join(missing)}")

            # Convert to floats explicitly
            temperature = float(temperature_str)
            pressure    = float(pressure_str)
            humidity    = float(humidity_str)
            wind_speed  = float(wind_speed_str)
            wind_deg    = float(wind_deg_str)

            # Optional fields – default to 0 if blank
            def to_float_or_zero(val):
                val = (val or "").strip()
                return float(val) if val != "" else 0.0

            rain_1h = to_float_or_zero(request.form.get('rain_1h', 0))
            rain_3h = to_float_or_zero(request.form.get('rain_3h', 0))
            snow    = to_float_or_zero(request.form.get('snow', 0))
            clouds  = to_float_or_zero(request.form.get('clouds', 0))

            # Build feature list (all floats)
            features = [
                temperature,
                pressure,
                humidity,
                wind_speed,
                wind_deg,
                rain_1h,
                rain_3h,
                snow,
                clouds,
            ]

            prediction, latency = classify_weather(features)
            return render_template('result.html', prediction=prediction, latency=latency)

        except Exception as e:
            error_msg = f"Error processing input: {e}"
            # Show the error at the top of the form page
            return render_template('form.html', error=error_msg)

    # GET request – just show the form
    return render_template('form.html')


if __name__ == '__main__':
    # Local run (not used inside Docker)
    app.run(host="0.0.0.0", port=5000)
