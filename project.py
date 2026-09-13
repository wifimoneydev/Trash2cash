from flask import Flask, render_template, request, jsonify, flash, redirect, session

from t2c.rewards import RATES, get_rate_range, calculate_reward, normalize_material
from t2c.locations import LOCATIONS, get_locations, list_location_records  # get_locations re-exported for test_project.py
from t2c.assistant.assistant import get_assistant_response

app = Flask(__name__)
app.secret_key = "dev"  # only needed for flash(); not a real secret, not for production


@app.route("/")
def home():
    return render_template("index.html", rates=RATES)


@app.route("/rewards", methods=["GET", "POST"])
def rewards():
    reward = None
    error = None
    material = None
    weight = None
    material_label = None

    if request.method == "POST":
        material = request.form.get("material", "")
        weight = request.form.get("weight", "")
        key = normalize_material(material)

        if key is None:
            error = f"'{material}' isn't in our verified material list. We currently accept: {', '.join(RATES.keys())}."
        else:
            try:
                weight_val = float(weight)
            except (TypeError, ValueError):
                weight_val = None

            if weight_val is None or weight_val < 0:
                error = "Please enter a weight of 0 or more."
            else:
                reward = calculate_reward(material, weight_val)
                material_label = key

    return render_template(
        "rewards.html",
        reward=reward, error=error, material=material, weight=weight,
        material_label=material_label, rates=RATES,
    )


@app.route("/api/reward", methods=["POST"])
def api_reward():
    data = request.get_json(silent=True) or {}
    material = data.get("material", "")
    weight = data.get("weight", "")

    key = normalize_material(material)
    if key is None:
        return jsonify({
            "ok": False,
            "error": "unsupported_material",
            "message": f"'{material}' isn't in our verified material list. We currently accept: {', '.join(RATES.keys())}.",
        })

    try:
        weight_val = float(weight)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "invalid_weight", "message": "Please enter a valid number for weight."})

    if weight_val < 0:
        return jsonify({"ok": False, "error": "invalid_weight", "message": "Weight can't be negative."})

    reward = calculate_reward(material, weight_val)
    lo, hi = get_rate_range(material)
    return jsonify({"ok": True, "material": key, "weight": weight_val, "reward": reward, "rate_range": [lo, hi]})


@app.route("/locations")
def locations():
    cities = list(LOCATIONS.keys())
    selected_city = request.args.get("city") or cities[0]
    if selected_city not in LOCATIONS:
        selected_city = cities[0]
    records = list_location_records(selected_city)
    return render_template("locations.html", cities=cities, selected_city=selected_city, records=records)


@app.route("/api/locations")
def api_locations():
    city = request.args.get("city", "")
    if city not in LOCATIONS:
        return jsonify({"ok": False, "error": "unknown_city", "cities": list(LOCATIONS.keys()), "records": []})
    return jsonify({"ok": True, "city": city, "records": list_location_records(city)})


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    result = get_assistant_response(message, session=session)
    return jsonify(result)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Local/mock only: no email is sent and nothing is persisted.
        print("Contact form submitted:", name, email, message)

        flash("Message sent successfully!")
        return redirect("/contact")

    return render_template("contact.html")


def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
