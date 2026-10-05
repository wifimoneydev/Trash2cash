from flask import Flask, render_template, request, jsonify, flash, redirect, session

from t2c.rewards import calculate_reward, get_rate_per_kg
from t2c.materials import (
    list_categories, list_materials, get_material, get_category,
    get_material_by_slug, RATE_DISCLAIMER,
)
from t2c.alias_resolver import resolve_material_id, search_materials
from t2c.locations import LOCATIONS, get_locations, list_location_records  # get_locations re-exported for test_project.py
from t2c.assistant.assistant import get_assistant_response

app = Flask(__name__)
app.secret_key = "dev"  # only needed for flash(); not a real secret, not for production

# The homepage "Popular Recyclables" picks — the most commonly asked-about
# material from each category. Not a ranking derived from real usage data
# yet; a reasonable editorial starting set.
POPULAR_MATERIAL_IDS = ["pet_bottles", "pure_water_sachets", "aluminium_cans"]

# Presentation-only wording for rate_status — the canonical values stay
# "reference"/"placeholder" in t2c/materials.py; this just avoids showing
# internal data-management terminology ("placeholder") to users. One
# place so Materials and material-detail pages can't drift apart.
RATE_STATUS_LABELS = {
    "reference": "Reference Rate",
    "placeholder": "Estimated Rate",
}


@app.template_filter("rate_status_label")
def rate_status_label(status):
    return RATE_STATUS_LABELS.get(status, status)


@app.route("/")
def home():
    popular_materials = [get_material(mid) for mid in POPULAR_MATERIAL_IDS]
    return render_template("index.html", popular_materials=popular_materials)


@app.route("/materials")
def materials():
    query = request.args.get("q", "").strip()
    category_id = request.args.get("category") or None

    if query:
        results = search_materials(query)
        if category_id:
            results = [m for m in results if m["category_id"] == category_id]
    else:
        results = list_materials(category_id)

    categories = list_categories()
    return render_template(
        "materials.html",
        categories=categories,
        category_names={c["id"]: c["name"] for c in categories},
        materials=results,
        selected_category=category_id,
        query=query,
    )


@app.route("/materials/<slug>")
def material_detail(slug):
    material = get_material_by_slug(slug)
    if material is None:
        return render_template("material_not_found.html", slug=slug), 404
    category = get_category(material["category_id"])
    return render_template(
        "material_detail.html",
        material=material,
        category=category,
        disclaimer=RATE_DISCLAIMER,
        cities=list(LOCATIONS.keys()),
    )


@app.route("/rewards", methods=["GET", "POST"])
def rewards():
    reward = None
    error = None
    material_id = None
    category_id = None
    weight = None
    material = None

    if request.method == "POST":
        category_id = request.form.get("category", "")
        material_id = request.form.get("material", "")
        weight = request.form.get("weight", "")

        material = get_material(material_id)
        if material is None:
            error = "Please choose a specific material from the list below."
        else:
            try:
                weight_val = float(weight)
            except (TypeError, ValueError):
                weight_val = None

            if weight_val is None or weight_val < 0:
                error = "Please enter a weight of 0 or more."
            else:
                reward = calculate_reward(material_id, weight_val)
    else:
        # Pre-fill from a deep link (e.g. the Materials page's "Estimate
        # Reward" button) without auto-submitting the form.
        material_id = request.args.get("material", "")
        material = get_material(material_id) if material_id else None
        category_id = material["category_id"] if material else (request.args.get("category", "") or "")

    return render_template(
        "rewards.html",
        reward=reward, error=error,
        category_id=category_id, material_id=material_id, weight=weight,
        material=material,
        categories=list_categories(),
        all_materials=list_materials(),
        disclaimer=RATE_DISCLAIMER,
    )


@app.route("/api/reward", methods=["POST"])
def api_reward():
    data = request.get_json(silent=True) or {}
    material_id = data.get("material_id", "")
    weight = data.get("weight", "")

    material = get_material(material_id)
    if material is None:
        return jsonify({
            "ok": False,
            "error": "unsupported_material",
            "message": f"'{material_id}' isn't a recognized material id. See /materials for the supported list.",
        })

    try:
        weight_val = float(weight)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "invalid_weight", "message": "Please enter a valid number for weight."})

    if weight_val < 0:
        return jsonify({"ok": False, "error": "invalid_weight", "message": "Weight can't be negative."})

    reward = calculate_reward(material_id, weight_val)
    rate = get_rate_per_kg(material_id)
    return jsonify({
        "ok": True,
        "material_id": material_id,
        "material_name": material["name"],
        "category_id": material["category_id"],
        "weight": weight_val,
        "rate_per_kg": rate,
        "rate_status": material["rate_status"],
        "reward": reward,
        "disclaimer": RATE_DISCLAIMER,
    })


@app.route("/api/materials")
def api_materials():
    query = request.args.get("q", "")
    category_id = request.args.get("category") or None
    if query:
        results = search_materials(query)
        if category_id:
            results = [m for m in results if m["category_id"] == category_id]
    else:
        results = list_materials(category_id)
    return jsonify({"ok": True, "materials": results})


def _attach_material_compatibility(records, material):
    """Tag each location record with whether the catalogue's own data
    supports this material being accepted there. Never invents a "yes" —
    see t2c/materials.py supported_location_ids, the one source of
    truth for this relationship."""
    if material is None:
        return records
    compatible = records and records[0]["city"] in material["supported_location_ids"]
    for record in records:
        record["material_compatibility"] = "selected_locations" if compatible else "not_yet_verified"
    return records


@app.route("/locations")
def locations():
    cities = list(LOCATIONS.keys())
    selected_city = request.args.get("city") or cities[0]
    if selected_city not in LOCATIONS:
        selected_city = cities[0]

    material_id = request.args.get("material") or None
    selected_material = get_material(material_id) if material_id else None

    records = _attach_material_compatibility(list_location_records(selected_city), selected_material)
    return render_template(
        "locations.html",
        cities=cities, selected_city=selected_city, records=records,
        all_materials=list_materials(), selected_material=selected_material,
    )


@app.route("/api/locations")
def api_locations():
    city = request.args.get("city", "")
    if city not in LOCATIONS:
        return jsonify({"ok": False, "error": "unknown_city", "cities": list(LOCATIONS.keys()), "records": []})

    material_id = request.args.get("material") or None
    material = get_material(material_id) if material_id else None
    if material_id and material is None:
        return jsonify({"ok": False, "error": "unsupported_material", "records": []})

    records = _attach_material_compatibility(list_location_records(city), material)
    return jsonify({"ok": True, "city": city, "material_id": material_id, "records": records})


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
