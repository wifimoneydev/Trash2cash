# t2c.chatbot

The Trash2Cash conversational assistant. This document describes what the
code actually does, not a planned future version.

## How it works

A bag-of-words intent classifier: `nltk` tokenizes and Porter-stems the
input, `scikit-learn`'s `CountVectorizer` + `MultinomialNB` predicts an
intent tag, and a canned response is returned for that tag. There is no
LLM, no OpenAI/GPT integration, and no conversation memory — every call to
`get_bot_response()` is independent of every other call.

The one exception is the `payout_rates` intent: its response is generated
at call time from [`t2c.rewards`](../rewards.py) — the same rate table the
reward calculator uses — instead of a hardcoded string, so the chatbot and
the calculator can never disagree about a rate again.

## Intents (7)

Trained from `data/intents.json`, ~20 example phrases total across all
seven tags:

| Tag | Example pattern | Response source |
|---|---|---|
| `greeting` | "Hi", "Hello" | static |
| `how_it_works` | "How does Trash2Cash work?" | static |
| `payout_rates` | "How much do you pay for plastic?" | **dynamic — reads `t2c.rewards.RATES`** |
| `pickup` | "Do you do pickups?" | static |
| `dropoff` | "Where can I drop off trash?" | static |
| `goodbye` | "Bye" | static |
| `plastic_types` | "Do you take PET plastic?" | static |

## Known limitations

- ~20 training examples across 7 classes is a very small training set.
  Naive Bayes always predicts *some* class with no confidence threshold,
  so out-of-distribution input (typos, unrelated questions) gets
  confidently misclassified into one of the seven tags rather than
  triggering a fallback/"I don't understand" response.
- Static responses for the other six intents (`dropoff` in particular)
  still reference things that don't exist yet, such as a locations page —
  see [`t2c/locations.py`](../locations.py) for what location data is
  actually available today.
- Retraining: run `python train_chatbot.py` from this directory to
  regenerate `data/chat_model.pkl` from `data/intents.json`.
