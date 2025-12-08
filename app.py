from flask import Flask, request, render_template
import pickle
import numpy as np
import time

app = Flask(__name__)

# Possible output classes from the trained model
weather_classes = [
    "clear",
    "cloudy",
    "drizzly",
    "foggy",
    "hazey",
    "misty",
    "rainy",
    "smokey",
    "thunderstorm",
]


def load_model(model_path: str = "model/model.pkl"):
    """Load the trained weather classification model."""
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


def classify_weather(features):
    """
    Run the model on a list of numeric features.

    features: list or 1D array of numeric values.
    """
    # Force to a 2D float array – this avoids the dtype='numeric' error
    features_arr = np.asarray(features, dtype=float).reshape(1, -1)

    model = load_model()
    start = time.time()
    prediction_index = int(model.predict(features_arr)[0])
    latency = round((time.time() - start) * 1000, 2)  # ms

    prediction = weather_classes[prediction_index]
    return prediction, latency


def parse_float_field(form, name, default=None):
    """
    Safely parse a float from form data.

    - If the field is empty and default is not None, return default.
    - If the field is empty and no default is given, raise a ValueError.
    - If the field contains non-numeric text, raise a ValueError with details.
    """
    raw = (form.get(name, "") or "").strip()

    if raw == "":
        if default is not None:
            return float(default)
        raise ValueError(f"Missing value for {name}")

    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value for {name}: {raw}") from exc


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # ----- Required fields -----
            temperature = parse_float_field(request.form, "temperature")
            pressure = parse_float_field(request.form, "pressure")
            humidity = parse_float_field(request.form, "humidity")
            wind_speed = parse_float_field(request.form, "wind_speed")
            wind_deg = parse_float_field(request.form, "wind_deg")

            # ----- Optional fields (default to 0.0 if left blank) -----
            rain_1h = parse_float_field(request.form, "rain_1h", default=0.0)
            rain_3h = parse_float_field(request.form, "rain_3h", default=0.0)
            snow = parse_float_field(request.form, "snow", default=0.0)
            clouds = parse_float_field(request.form, "clouds", default=0.0)

            # Build feature list (all pure floats)
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
            return render_template(
                "result.html",
                prediction=prediction,
                latency=latency,
            )

        except Exception as e:
            # Any parsing / model error is shown at the top of the form
            error_msg = f"Error processing input: {e}"
            return render_template("form.html", error=error_msg)

    # GET – just show the input form
    return render_template("form.html")


if __name__ == "__main__":
    # Local run (Flask dev server). In Docker/K8s gunicorn/uwsgi might be used instead.
    app.run(host="0.0.0.0", port=5000)

