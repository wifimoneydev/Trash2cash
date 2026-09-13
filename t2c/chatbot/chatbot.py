import json
import joblib
import random
import os
import nltk
from nltk.stem import PorterStemmer

from t2c.rewards import RATES

nltk.download('punkt')

# === Preprocessing ===
stemmer = PorterStemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence.lower())

def stem_words(words):
    return [stemmer.stem(w) for w in words]

# === Get the absolute path of the current file ===
BASE_DIR = os.path.dirname(__file__)

# === Load trained model ===
model_path = os.path.join(BASE_DIR, "data", "chat_model.pkl")
model = joblib.load(model_path)

# === Load intents and responses ===
intents_path = os.path.join(BASE_DIR, "data", "intents.json")
with open(intents_path) as file:
    data = json.load(file)

tag_responses = {
    intent["tag"]: intent["responses"] for intent in data["intents"]
}

# Confidence below this means "don't guess" — return the fallback instead
# of the classifier's best (but weak) guess. Tuned against
# t2c/chatbot/evaluate.py's evaluation set; see t2c/chatbot/README.md for
# the reasoning and the accuracy numbers behind this value.
CONFIDENCE_THRESHOLD = 0.30

FALLBACK_RESPONSE = (
    "I'm not sure I understood that. You can ask me about recyclable "
    "materials, rewards, or drop-off locations."
)


def _payout_rates_response():
    """Build the payout-rates reply from the real reward table (t2c.rewards)
    instead of a hardcoded string, so this can never drift out of sync with
    the reward calculator."""
    parts = [f"{material}: ₦{lo}-₦{hi}/kg" for material, (lo, hi) in RATES.items()]
    return "Our current rates are — " + "; ".join(parts) + "."


def classify(user_input):
    """Return (tag, confidence) for the given input.

    `confidence` is the classifier's predicted probability for its top
    class (from MultinomialNB.predict_proba) — exposed so callers (the
    evaluation script, tests, logging) can inspect it. Not shown to
    normal users; get_bot_response() is what end users see.
    """
    tokens = tokenize(user_input)
    stems = " ".join(stem_words(tokens))
    probs = model.predict_proba([stems])[0]
    best_index = probs.argmax()
    return model.classes_[best_index], probs[best_index]


# === Predict response based on user input ===
def get_bot_response(user_input, threshold=CONFIDENCE_THRESHOLD):
    tag, confidence = classify(user_input)
    if confidence < threshold:
        # Don't guess: an unrelated or out-of-distribution question should
        # never be silently mapped to the closest-sounding intent.
        return FALLBACK_RESPONSE
    if tag == "payout_rates":
        return _payout_rates_response()
    return random.choice(tag_responses.get(tag, [FALLBACK_RESPONSE]))

# === (Optional) Command line chat for quick test ===
if __name__ == "__main__":
    print("Trash2Cash Bot: Hello! Type 'quit' to exit.")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            print("Trash2Cash Bot: Goodbye!")
            break
        response = get_bot_response(inp)
        print(f"Trash2Cash Bot: {response}")
