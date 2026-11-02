"""Model loading and inference."""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

IMG_SIZE = (180, 180)
DEFAULT_MODEL_PATH = Path("models/best_finetuned_model.keras")


def download_model(url: str, dest: Path, progress_cb=None) -> Path:
    """Download the model file if it is not already present."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")

    def _hook(blocks, block_size, total):
        if progress_cb and total > 0:
            progress_cb(min(blocks * block_size / total, 1.0))

    urllib.request.urlretrieve(url, tmp, _hook)
    os.replace(tmp, dest)
    return dest


def load_model(path: str | Path = DEFAULT_MODEL_PATH):
    """Load the fine-tuned ResNet50 classifier.

    The saved model contains a ``Lambda`` layer wrapping
    ``resnet50.preprocess_input``; it must be supplied via ``custom_objects``.
    ``safe_mode=False`` is required for Lambda layers - only load model files
    that you trained / trust.
    """
    import tensorflow as tf  # imported lazily so unit tests don't need TF

    return tf.keras.models.load_model(
        str(path),
        custom_objects={"preprocess_input": tf.keras.applications.resnet50.preprocess_input},
        safe_mode=False,
        compile=False,
    )


def preprocess(image: Image.Image) -> np.ndarray:
    """Replicate the training pipeline: RGB -> bilinear resize 180x180 -> [0, 1].

    The model itself rescales by 255 and applies ResNet50 preprocessing
    internally, so we only feed float32 values in the [0, 1] range.
    """
    import tensorflow as tf

    image = ImageOps.exif_transpose(image).convert("RGB")
    arr = tf.image.resize(np.asarray(image), IMG_SIZE).numpy().astype("float32") / 255.0
    return np.expand_dims(arr, axis=0)


def predict(model, image: Image.Image, class_names: list[str], top_k: int = 5):
    """Return a list of (breed, probability) sorted by probability."""
    probs = model.predict(preprocess(image), verbose=0)[0]
    idx = np.argsort(probs)[::-1][:top_k]
    return [(class_names[i], float(probs[i])) for i in idx]
