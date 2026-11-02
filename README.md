# 🐾 Pet Breed Classifier

A Streamlit web app that identifies **37 cat and dog breeds** from a photo, powered by a
**ResNet50** model fine-tuned on the [Oxford-IIIT Pet dataset](https://www.robots.ox.ac.uk/~vgg/data/pets/).

| | |
|---|---|
| **Test accuracy** | **89.0 %** (739 held-out images) |
| **Classes** | 37 (12 cat breeds, 25 dog breeds) |
| **Input size** | 180 × 180 RGB |
| **Framework** | TensorFlow / Keras 3, Streamlit |

## Features

- Upload an image or use the camera
- Predicted breed, species (cat / dog) and confidence
- Top-5 probability chart
- Low-confidence warning for unclear photos or unsupported animals
- Model is cached, loaded once per server process
- Optional automatic model download via `MODEL_URL`

## Quick start

```bash
git clone https://github.com/ArajulKhan/pet-breed-classifier.git
cd pet-breed-classifier

# Fetch the model file (stored with Git LFS)
git lfs install
git lfs pull

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

Open <http://localhost:8501>.


## Getting the model file onto GitHub

The model is ~165 MB and **GitHub blocks files over 100 MB**, so:

**Git LFS (recommended)**

```bash
git lfs install
git lfs track "*.keras"      # already configured in .gitattributes
git add .gitattributes models/best_finetuned_model.keras
git commit -m "Add model via Git LFS"
```

Free LFS quota is 1 GB storage and 1 GB bandwidth per month.


#future work
## Docker

```bash
docker build -t pet-breed-app .
docker run -p 8501:8501 pet-breed-app
```

The image uses `tensorflow-cpu`. Mount or download the model as described above.

#Future work
## Deploy

| Platform | Notes |
|---|---|
| Streamlit Community Cloud | Connect the repo, main file `app.py`. Use Python 3.11 and either LFS or `MODEL_URL`. |
| Hugging Face Spaces | Create a Streamlit or Docker Space; store the model in the Hub. |
| Any Docker host | Use the provided `Dockerfile`. |

## Project structure

```
.
├── app.py                      # Streamlit UI
├── src/
│   ├── model.py                # model loading, preprocessing, prediction
│   └── labels.py               # class names, species, display names
├── models/
│   ├── best_finetuned_model.keras   # model (Git LFS)
│   └── class_names.json
├── notebooks/
│   └── oxford_III_cat_dog.ipynb     # training notebook
├── docs/
│   ├── architecture.pdf             # architecture design document
│   └── generate_architecture_pdf.py
├── tests/test_labels.py
├── .github/workflows/ci.yml    # lint + tests
├── .streamlit/config.toml
├── Dockerfile  requirements.txt  requirements-dev.txt
├── .gitignore  .gitattributes  ruff.toml  LICENSE
└── README.md
```

The full design is described in [`docs/architecture.pdf`](docs/architecture.pdf).

## How the model was built

| Stage | Description | Result |
|---|---|---|
| 1. Baseline CNN | 4 conv blocks trained from scratch | 27.7 % test accuracy |
| 2. Feature extraction | Frozen ResNet50 (ImageNet) + new head | ~89 % validation accuracy |
| 3. Fine-tuning | Unfreeze `conv5_block1_out` onward, LR 1e-6, BatchNorm frozen | 89.5 % val / **89.0 % test** |

Data: 7,390 images, stratified split 5,912 / 739 / 739. Details are in the notebook.

## ⚠️ Important notes

**Class order.** Training labels were built from `sorted(breeds)`, but the original
`class_names.json` was exported in dataset-shuffle order. This repo ships a corrected
(alphabetical) `models/class_names.json`, and `src/labels.py` re-sorts names on load, so
predictions are always mapped correctly. The notebook's `classification_report` call uses
`df["breed"].unique()` as `target_names`, which mislabels the per-class rows (overall accuracy is
unaffected). To fix it, use `target_names=unique_breeds` and re-run that cell.

**Lambda layer.** The model contains a `Lambda` layer (`resnet50.preprocess_input`), so it is loaded
with `custom_objects` and `safe_mode=False`. Only load model files you trust.

**Keras / TensorFlow version.** The model was saved with Keras 3.13 (TensorFlow 2.21 in Colab). If
loading fails, upgrade TensorFlow (`pip install -U tensorflow`).

## Limitations

- Only the 37 breeds in the dataset are supported; other animals or objects still receive a breed prediction.
- Mixed breeds are mapped to the closest known purebred.
- Common confusions: American Bulldog / Staffordshire Bull Terrier, Ragdoll / Birman.

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
python docs/generate_architecture_pdf.py   # regenerate the PDF
```

## Acknowledgements

- Parkhi et al., *Cats and Dogs*, CVPR 2012: Oxford-IIIT Pet dataset
- He et al., *Deep Residual Learning for Image Recognition*, 2015: ResNet
