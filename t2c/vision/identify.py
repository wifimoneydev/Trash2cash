import numpy as np
import sys
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model", "t2c_classifier_finetuned.h5")
LABEL_MAP_PATH = os.path.join(BASE_DIR, "model", "label_map.pkl")

IMG_SIZE = (224, 224)


def load_classifier():
    """Load the trained model and label map, or fail clearly.

    No trained model is currently committed to this repo (see
    t2c/vision/README.md) — this raises rather than fabricating a
    prediction, so a missing model is never mistaken for a working one.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABEL_MAP_PATH):
        raise FileNotFoundError(
            f"No trained T2CVision model found at '{MODEL_PATH}'. "
            "Run trainvision.py to produce one before running inference — "
            "there is currently no trained model checked into this repo."
        )
    import tensorflow as tf
    import joblib
    model = tf.keras.models.load_model(MODEL_PATH)
    class_names = joblib.load(LABEL_MAP_PATH)
    return model, class_names


def predict(img_path, model, class_names):
    from tensorflow.keras.preprocessing import image
    import tensorflow as tf

    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # shape (1, 224, 224, 3)
    # No manual rescaling here: the trained model already includes a
    # Rescaling(1./255) layer (see trainvision.py). Rescaling again here
    # was a bug — it silently double-normalized every inference image.

    predictions = model.predict(img_array)
    predicted_index = np.argmax(predictions[0])
    return class_names[predicted_index], predictions[0][predicted_index]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python identify.py <path_to_image>")
        sys.exit(1)

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"Error: File '{img_path}' does not exist.")
        sys.exit(1)

    try:
        model, class_names = load_classifier()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    predicted_label, confidence = predict(img_path, model, class_names)
    print(f"Prediction: {predicted_label} ({confidence*100:.2f}% confidence)")
