"""Streamlit app: Cat & Dog breed classifier (Oxford-IIIT Pet, 37 breeds)."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError

from src.labels import load_class_names, pretty_name, species_of
from src.model import DEFAULT_MODEL_PATH, download_model, load_model, predict

CLASS_NAMES_PATH = Path("models/class_names.json")
LOW_CONFIDENCE = 0.50

st.set_page_config(page_title="Pet Breed Classifier", page_icon="🐾", layout="centered")


# Cached resources
@st.cache_resource(show_spinner="Loading model...")
def get_model():
    return load_model(DEFAULT_MODEL_PATH)


@st.cache_data
def get_class_names() -> list[str]:
    return load_class_names(CLASS_NAMES_PATH)


def ensure_model_file() -> bool:
    """Make sure the model file exists locally; download it if MODEL_URL is set."""
    if DEFAULT_MODEL_PATH.exists():
        return True

    url = os.getenv("MODEL_URL") or st.secrets.get("MODEL_URL", None)
    if not url:
        return False

    bar = st.progress(0.0, text="Downloading model (first run only)...")
    try:
        download_model(url, DEFAULT_MODEL_PATH, progress_cb=lambda p: bar.progress(p))
    except Exception as exc:  # noqa: BLE001
        bar.empty()
        st.error(f"Model download failed: {exc}")
        return False
    bar.empty()
    return True


# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "A **ResNet50** model fine-tuned on the **Oxford-IIIT Pet** dataset "
        "to recognise **37 cat and dog breeds**."
    )
    st.metric("Test accuracy", "89.0%")
    st.caption("Evaluated on 739 held-out images (20 per breed, approx.).")
    with st.expander("Supported breeds"):
        names = get_class_names()
        cats = [pretty_name(n) for n in names if species_of(n) == "Cat"]
        dogs = [pretty_name(n) for n in names if species_of(n) == "Dog"]
        st.markdown("**Cats (12)**\n\n" + ", ".join(cats))
        st.markdown("**Dogs (25)**\n\n" + ", ".join(dogs))
    st.caption(
        "The model only knows these 37 breeds. Photos of other animals or "
        "breeds will still get a (wrong) answer - check the confidence."
    )


# Main page
st.title("🐾 Cat & Dog Breed Classifier")
st.write("Upload a clear photo of a cat or dog and the model will guess its breed.")

if not ensure_model_file():
    st.error("Model file not found.")
    st.markdown(
        "Place `best_finetuned_model.keras` in the `models/` folder, **or** set a "
        "`MODEL_URL` environment variable / Streamlit secret pointing to a "
        "direct-download link. See the README for details."
    )
    st.stop()

model = get_model()
class_names = get_class_names()

source = st.radio("Image source", ["Upload", "Camera"], horizontal=True)
if source == "Upload":
    file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp"])
else:
    file = st.camera_input("Take a photo")

if file is None:
    st.info("Waiting for an image...")
    st.stop()

try:
    image = Image.open(file)
    image.load()
except (UnidentifiedImageError, OSError):
    st.error("Could not read that file as an image. Try a JPG or PNG.")
    st.stop()

col_img, col_res = st.columns([1, 1.1], gap="large")

with col_img:
    st.image(image, caption="Your image", use_container_width=True)

with st.spinner("Classifying..."):
    results = predict(model, image, class_names, top_k=5)

top_breed, top_prob = results[0]

with col_res:
    st.subheader(pretty_name(top_breed))
    st.markdown(f"{'🐱' if species_of(top_breed) == 'Cat' else '🐶'} **{species_of(top_breed)}**")
    st.metric("Confidence", f"{top_prob:.1%}")
    if top_prob < LOW_CONFIDENCE:
        st.warning(
            "Low confidence. The photo may be unclear, show a mixed breed, or "
            "contain an animal outside the 37 supported breeds."
        )

st.subheader("Top 5 predictions")
df = pd.DataFrame(
    {
        "Breed": [pretty_name(b) for b, _ in results],
        "Probability": [p for _, p in results],
    }
).set_index("Breed")
st.bar_chart(df, horizontal=True)
st.dataframe(
    df.assign(Probability=df["Probability"].map("{:.2%}".format)),
    use_container_width=True,
)
