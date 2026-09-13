import json
import joblib
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

nltk.download('punkt')

# Preprocessing
stemmer = PorterStemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence.lower())

def stem_words(words):
    return [stemmer.stem(w) for w in words]

# Load intents
with open("data/intents.json") as file:
    data = json.load(file)

X = []
y = []
tag_responses = {}

for intent in data["intents"]:
    tag = intent["tag"]
    tag_responses[tag] = intent["responses"]
    for pattern in intent["patterns"]:
        tokens = tokenize(pattern)
        stems = " ".join(stem_words(tokens))
        X.append(stems)
        y.append(tag)

# Train model
model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

model.fit(X, y)

# Save model
joblib.dump(model, "data/chat_model.pkl")
print("✅ Model trained and saved as chat_model.pkl")
