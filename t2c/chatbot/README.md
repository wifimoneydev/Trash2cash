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

## Confidence threshold (added Phase 2)

`get_bot_response()` calls `classify()`, which returns `(tag, confidence)`
from `MultinomialNB.predict_proba()`. If `confidence < CONFIDENCE_THRESHOLD`
(currently **0.30**, module-level constant, overridable per call), the bot
returns `FALLBACK_RESPONSE` instead of guessing. See
[`evaluate.py`](evaluate.py) and `T2C_PROJECT_STATUS.md` for how 0.30 was
chosen: it's the highest threshold that doesn't reject the model's own
canonical training phrases (e.g. bare "Hi"/"Hello" score ~0.315) — a
higher threshold catches more out-of-domain questions but starts
rejecting legitimate short greetings, which is worse.

## Intents (7)

Trained from `data/intents.json`, ~57 example phrases total across all
seven tags (expanded from ~24 in Phase 2 — see evaluation results below):

| Tag | Example pattern | Response source |
|---|---|---|
| `greeting` | "Hi", "Hello" | static |
| `how_it_works` | "How does Trash2Cash work?" | static |
| `payout_rates` | "How much do you pay for plastic?" | **dynamic — reads `t2c.rewards.RATES`** |
| `pickup` | "Do you do pickups?" | static |
| `dropoff` | "Where can I drop off trash?" | static |
| `goodbye` | "Bye" | static |
| `plastic_types` | "Do you take PET plastic?" | static |

## Evaluation

`evaluate.py` scores the classifier against `data/eval_set.json` (53
hand-written utterances: paraphrases, spelling variants, casual Nigerian
English, short/ambiguous queries, and out-of-domain questions — none of
them copied into the training data, to keep the score honest). Run it
with `python -m t2c.chatbot.evaluate` from the repo root. Current result
at threshold 0.30: **69.8% overall accuracy, 38.5% OOD recall**. Full
numbers and the before/after comparison are in `T2C_PROJECT_STATUS.md`.

## Known limitations

- At threshold 0.30, roughly 3 in 8 out-of-domain questions still get a
  confident (wrong) answer rather than the fallback — see `evaluate.py`'s
  `false_confident` output. Raising the threshold reduces this but starts
  breaking legitimate short inputs (see "Confidence threshold" above).
  This is a real, measured trade-off, not fully solved — a next step
  would be more training data or a dedicated out-of-scope class, which
  is a bigger change than this phase's "conservative data only" scope
  allowed.
- ~57 training examples across 7 classes is still a small training set;
  very short inputs (single words) get low confidence regardless of
  correctness, because bag-of-words has little signal to work with.
- Static responses for the other six intents (`dropoff` in particular)
  still reference things that don't exist yet, such as a locations page —
  see [`t2c/locations.py`](../locations.py) for what location data is
  actually available today.
- Retraining: run `python train_chatbot.py` from this directory (or
  `python t2c/chatbot/train_chatbot.py` from the repo root) to regenerate
  `data/chat_model.pkl` from `data/intents.json`.
