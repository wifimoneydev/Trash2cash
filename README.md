# Trash2Cash (T2C)

#### Video demo: https://youtu.be/5TD3n5k77fg

#### Description

**Trash2Cash (T2C)** is a web-based recycling incentive platform developed to encourage responsible waste disposal in Nigeria through monetary rewards. Built as the final project for Harvard's CS50P course, this application lets users estimate a cash reward for recyclable trash and see a drop-off location, with a small conversational assistant alongside it.

At its core, T2C helps users input the type of recyclable material they've collected (Plastic, Nylon, or Aluminum), enter the weight of their collection, and receive an instant estimated cash reward. Users can also select a city — Lagos or Abuja — for drop-off.

---

### 🌍 The Problem

Nigeria, like many developing nations, faces a serious environmental crisis due to improper waste disposal. Streets are littered with plastic bottles, nylon sachets, and aluminum cans. These materials clog drainage systems, pollute natural ecosystems, and contribute to flooding and disease outbreaks during the rainy season.

Despite growing awareness about recycling, there remains a gap between intention and action — mostly due to a lack of structured infrastructure, poor awareness, and a missing economic incentive. Trash2Cash aims to change that by making recycling pay.

---

### 🔧 How It Works Today

1. User selects a trash material type (Plastic, Nylon, or Aluminum).
2. User enters the weight of the collected material (kg).
3. User selects a city (Lagos or Abuja).
4. The app calculates and displays an estimated cash reward using a fixed, hand-set rate table — not a live market feed.
5. A chatbot widget can answer basic questions about the service using the same rate table.

The app is Python/Flask on the backend with Jinja2-templated HTML/CSS on the frontend. See [`T2C_PROJECT_STATUS.md`](T2C_PROJECT_STATUS.md) for a full, verified account of what is and isn't implemented, including what's still static/manual (drop-off locations are a fixed LGA list, not verified real-world addresses; there's no map, no accounts, no persistence).

---

### 📁 Repository Structure

```
app.py                  # entrypoint — python app.py
project.py              # Flask routes + app object
templates/              # Jinja2 HTML templates
static/                 # CSS + chatbot widget JS
t2c/
├── rewards.py          # single source of truth for payout rates
├── locations.py        # single source of truth for drop-off location data
├── chatbot/            # intent-classifier chatbot (see t2c/chatbot/README.md)
└── vision/             # image classification pipeline (see t2c/vision/README.md)
test_project.py         # pytest suite (reward/location logic)
requirements.txt        # runtime dependencies
requirements-dev.txt    # + pytest
```

---

### 📈 Vision for the Future

Trash2Cash is more than a school project — it's a vision for the future of Nigeria.

**Short-term goals:** launch pilot programs in Lagos and Abuja; partner with local government waste departments and private recycling companies to create verified drop-off points; add more materials and pricing that reflects real market conditions.

**Long-term impact:** empower local communities to take ownership of their environment; create jobs through collection, sorting, and processing of recyclable waste; reduce non-biodegradable waste in streets, gutters, and landfills; promote a circular economy where trash is the beginning of new value chains, not the end.

None of the above is built yet — see the roadmap in `T2C_PROJECT_STATUS.md` for what's actually planned next.

---

### 🇳🇬 Why Nigeria?

Nigeria has a population of over 220 million people, generating thousands of metric tons of waste daily, with only a small fraction properly recycled. Trash2Cash targets the everyday Nigerian, especially in low- and middle-income areas, with a real financial incentive to participate in recycling.

---

### 🚀 Future Features (post-CS50, not yet built)

- User authentication (register/login) and a reward/exchange history.
- Map integration to find and display drop-off centers visually.
- Real vision-based waste classification (see `t2c/vision/README.md` for current status).
- Admin dashboard, reward leaderboard, SMS reminders, and local-language support.

---

### Running locally

```
pip install -r requirements-dev.txt
python app.py       # starts the Flask app
pytest               # runs the test suite
```

---

📬 Contact: trash2cash.ng@gmail.com · Based in Lagos, Nigeria

This project is open-source and free to use for educational or social good purposes. Contact the author for commercial use or collaborations.

Made with love, code, and a vision for a better planet. 🌱
