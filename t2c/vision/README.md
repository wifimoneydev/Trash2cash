# t2c.vision

This is an AI project I’m building to help solve a very real problem in developing countries — waste management and recycling. The idea is simple: use computer vision to identify different types of trash (plastic, nylon, cans, etc.) so that people can automatically exchange waste for cash at smart outlets.

The bigger picture here is a recycling system powered by AI — one where people drop their waste into a machine, and it detects, sorts, and rewards them instantly. That’s what I’m working toward with Trash2Cash (T2C), and `t2c.vision` is the brain that will power it.

## Verified current status (Phase 1 cleanup)

- **Architecture**: `trainvision.py` uses transfer learning on **MobileNetV2**
  (ImageNet weights, frozen base + a later fine-tuning phase), not a basic
  CNN — the code is further along than the notes below suggest.
- **Dataset**: the unmodified, stock [TrashNet dataset](https://github.com/garythung/trashnet)
  (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash` — 2,527 images).
  There is no `nylon` class in this dataset, so the "nylon vs. plastic"
  confusion described below doesn't apply to the current classes; no
  custom Nigeria-specific data collection has started yet.
- **No trained model is currently checked into this repo** — `model/` is
  empty and gitignored. `identify.py` cannot classify anything until
  `trainvision.py` is run and produces a model; it now fails with a clear
  error rather than crashing or fabricating a prediction if no model
  exists.
- **Fixed**: `identify.py` previously rescaled pixel values a second time
  at inference (`/255.0`) on top of the `Rescaling(1./255)` layer already
  baked into the trained model — a bug that would have corrupted any real
  inference. That double-rescale has been removed.

## What I’ve Done So Far

* ✅ Set up the folder structure and environment using TensorFlow/Keras.
* ✅ Collected and organized the [TrashNet dataset](https://github.com/garythung/trashnet).
* ✅ Built and trained a MobileNetV2 transfer-learning model to classify trash images (see status note above — no trained artifact is currently saved in the repo).
* ✅ Created preprocessing scripts for image resizing and augmentation.

## Where It’s At Now

The training pipeline runs, but there is currently no saved model or
measured accuracy to report — see "Verified current status" above.

## Next Steps

Right now, I’m exploring the idea of **building my own custom dataset** — one that’s more relevant to local trash types in Nigeria (pure water sachets, PET bottles, local-style packaging, etc.). I think that will give me better results than trying to rely on datasets made for other environments.

The long-term plan is to integrate this into a real-world, AI-powered trash-to-cash outlet that runs smoothly with automation.

---

## Why This Matters

I’m passionate about using AI to solve problems that actually matter — not just building models for leaderboard scores. If this works, it can give people a real incentive to clean up their environment and earn a bit of income, while also improving recycling systems from the ground up.

---

## Tech Stack

* Python
* TensorFlow / Keras
* NumPy / Pandas
* Matplotlib (for training viz)
* TrashNet dataset (custom dataset coming soon)

---

Still a work in progress, but I’m fully in. Stay tuned. 👀
