from flask import Flask, render_template, request, jsonify, flash, redirect, session

from t2c.rewards import RATES, get_rate_range, calculate_reward
from t2c.locations import LOCATIONS, get_locations
from t2c.assistant.assistant import get_assistant_response

app = Flask(__name__)
app.secret_key = "dev"  # only needed for flash(); not a real secret, not for production

@app.route("/", methods=["GET", "POST"])
def home():
    reward = None
    material = None
    weight = None
    location = None

    if request.method == "POST":
        material = request.form.get("material")
        weight = request.form.get("weight")
        location = request.form.get("location")
        if material and weight and location:
            reward = calculate_reward(material, weight)

    return render_template("index.html", reward=reward, material=material, weight=weight, location=location, locations=LOCATIONS, rates=RATES)

@app.route("/process", methods=["GET", "POST"])
def process():
    reward = None
    material = None
    weight = None
    location = None

    if request.method == "POST":
        material = request.form.get("material")
        weight = request.form.get("weight")
        location = request.form.get("location")
        if material and weight and location:
            reward = calculate_reward(material, weight)

    return render_template("process.html", reward=reward, material=material, weight=weight, location=location)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    result = get_assistant_response(message, session=session)
    return jsonify(result)

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
