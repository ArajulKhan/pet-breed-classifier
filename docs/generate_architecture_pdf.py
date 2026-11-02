"""Generates docs/architecture.pdf  ->  python docs/generate_architecture_pdf.py"""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

OUT = Path(__file__).with_name("architecture.pdf")
W = A4[0] - 4 * cm  # usable width

INK, MUTED = colors.HexColor("#1F2933"), colors.HexColor("#616E7C")
ACCENT, LIGHT = colors.HexColor("#E4572E"), colors.HexColor("#FDEEE9")
BLUE, BLUE_L = colors.HexColor("#2B6CB0"), colors.HexColor("#E6F0FA")
GREEN, GREEN_L = colors.HexColor("#2F855A"), colors.HexColor("#E6F4EC")
GREY_L = colors.HexColor("#F1F3F5")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=18, textColor=INK, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, textColor=ACCENT, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.5, leading=13.5, textColor=INK)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=8.5, leading=11.5, textColor=MUTED)
CELL = ParagraphStyle("C", parent=BODY, fontSize=8.5, leading=11)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
TITLE = ParagraphStyle("T", parent=H1, fontSize=28, leading=33, spaceAfter=4)
SUB = ParagraphStyle("Sub", parent=BODY, fontSize=12, textColor=MUTED, spaceAfter=14)
CAP = ParagraphStyle("Cap", parent=SMALL, alignment=TA_CENTER, spaceBefore=3)


def P(t, s=BODY):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(f"&bull;&nbsp; {i}", ParagraphStyle("bl", parent=BODY, leftIndent=12, firstLineIndent=-10, spaceAfter=2)) for i in items]


def table(rows, widths, header=True):
    data = [[Paragraph(str(c), CELLB if (header and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD2D9")),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), INK)]
        st += [("BACKGROUND", (0, i), (-1, i), GREY_L) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t


# ---------- diagram helpers ----------
def box(d, x, y, w, h, title, sub=None, fill=BLUE_L, stroke=BLUE, size=8.5):
    d.add(Rect(x, y, w, h, rx=5, ry=5, fillColor=fill, strokeColor=stroke, strokeWidth=1.1))
    ty = y + h / 2 + (3 if sub else -3)
    d.add(String(x + w / 2, ty, title, textAnchor="middle", fontName="Helvetica-Bold", fontSize=size, fillColor=INK))
    if sub:
        d.add(String(x + w / 2, y + h / 2 - 8, sub, textAnchor="middle", fontName="Helvetica", fontSize=size - 1.5, fillColor=MUTED))


def arrow(d, x1, y1, x2, y2, color=MUTED):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2))
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    s = 5
    d.add(Polygon([x2, y2, x2 - s * math.cos(a - 0.4), y2 - s * math.sin(a - 0.4),
                   x2 - s * math.cos(a + 0.4), y2 - s * math.sin(a + 0.4)], fillColor=color, strokeColor=color))


def label(d, x, y, t, size=7.5, color=MUTED, anchor="middle", bold=False):
    d.add(String(x, y, t, textAnchor=anchor, fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size, fillColor=color))


def system_diagram():
    d = Drawing(W, 330)
    # Client zone
    d.add(Rect(0, 215, W, 110, rx=6, ry=6, fillColor=colors.white, strokeColor=colors.HexColor("#CBD2D9"), strokeDashArray=[3, 3]))
    label(d, 8, 313, "CLIENT (browser)", 7.5, MUTED, "start", True)
    box(d, 20, 235, 110, 55, "User", "uploads photo or camera shot", fill=GREY_L, stroke=MUTED)
    box(d, W - 150, 235, 130, 55, "Result view", "breed - species - top-5", fill=GREEN_L, stroke=GREEN)
    # Server zone
    d.add(Rect(0, 10, W, 195, rx=6, ry=6, fillColor=colors.white, strokeColor=colors.HexColor("#CBD2D9"), strokeDashArray=[3, 3]))
    label(d, W - 8, 193, "SERVER (Streamlit process / Docker container)", 7.5, MUTED, "end", True)
    bw, bh, gap = 98, 50, 24
    xs = [12 + i * (bw + gap) for i in range(4)]
    box(d, xs[0], 115, bw, bh, "app.py", "Streamlit UI", fill=LIGHT, stroke=ACCENT)
    box(d, xs[1], 115, bw, bh, "src/model.py", "preprocess()", fill=BLUE_L)
    box(d, xs[2], 115, bw, bh, "ResNet50 model", "Keras .keras file", fill=BLUE_L)
    box(d, xs[3], 115, bw, bh, "src/labels.py", "index -> breed", fill=BLUE_L)
    for i, n in enumerate(["2", "3", "4"]):
        arrow(d, xs[i] + bw, 140, xs[i + 1] - 1, 140)
        label(d, xs[i] + bw + gap / 2, 146, n, 8, ACCENT, bold=True)
    # client <-> app
    arrow(d, 75, 235, xs[0] + 30, 166, ACCENT)
    label(d, 20, 205, "1", 8, ACCENT, "start", True)
    arrow(d, xs[0] + 70, 166, W - 85, 235, GREEN)
    label(d, W / 2 + 40, 205, "5", 8, GREEN, "start", True)
    # storage
    box(d, xs[2] - 2, 30, bw + 4, 50, "models/ folder", "best_finetuned_model.keras", fill=GREY_L, stroke=MUTED, size=8)
    box(d, xs[3] - 2, 30, bw + 4, 50, "class_names.json", "37 breed labels", fill=GREY_L, stroke=MUTED, size=8)
    arrow(d, xs[2] + bw / 2, 80, xs[2] + bw / 2, 114)
    arrow(d, xs[3] + bw / 2, 80, xs[3] + bw / 2, 114)
    box(d, xs[0], 30, bw + 4, 50, "Remote storage", "optional: MODEL_URL", fill=GREY_L, stroke=MUTED, size=8)
    arrow(d, xs[0] + bw + 4, 55, xs[2] - 3, 55)
    label(d, (xs[0] + bw + xs[2]) / 2, 60, "download once", 6.5)
    label(d, 8, 20, "1 image bytes   2 PIL image   3 180x180 batch   4 37 probabilities   5 breed + top-5 rendered", 7, MUTED, "start")
    return d


def model_diagram():
    layers = [
        ("Input", "180 x 180 x 3  (values 0-1)", GREY_L, MUTED),
        ("Data augmentation (training only)", "RandomFlip, Rotation 0.1, Zoom 0.1, Contrast 0.1", GREY_L, MUTED),
        ("Rescaling(255)  +  Lambda(resnet50.preprocess_input)", "back to 0-255, RGB->BGR, mean subtraction", BLUE_L, BLUE),
        ("ResNet50 conv base (ImageNet weights)", "stages conv1 - conv5; conv5_block1+ fine-tuned, BatchNorm frozen", LIGHT, ACCENT),
        ("GlobalAveragePooling2D", "6x6x2048 feature map -> 2048 vector", BLUE_L, BLUE),
        ("Dense(256, ReLU)  +  Dropout(0.5)", "task-specific head", BLUE_L, BLUE),
        ("Dense(37, Softmax)", "probability for each breed", GREEN_L, GREEN),
    ]
    h, gap = 36, 14
    H = len(layers) * (h + gap)
    d = Drawing(W, H)
    bw = W - 80
    for i, (t, s, f, st) in enumerate(layers):
        y = H - (i + 1) * (h + gap) + gap
        box(d, 40, y, bw, h, t, s, fill=f, stroke=st, size=9)
        if i < len(layers) - 1:
            arrow(d, 40 + bw / 2, y, 40 + bw / 2, y - gap + 1)
    return d


def flow_diagram():
    steps = [("Oxford-IIIT\nPet images", "7,390"), ("Stratified\nsplit", "80/10/10"), ("tf.data\npipeline", "180x180"),
             ("Stage 1\nBaseline CNN", "27.7%"), ("Stage 2\nFeature extr.", "~89% val"), ("Stage 3\nFine-tuning", "89.0%")]
    d = Drawing(W, 120)
    n = len(steps)
    bw = (W - (n - 1) * 14) / n
    for i, (t, m) in enumerate(steps):
        x = i * (bw + 14)
        fill, st = (GREEN_L, GREEN) if i == n - 1 else ((LIGHT, ACCENT) if i >= 3 else (BLUE_L, BLUE))
        d.add(Rect(x, 35, bw, 60, rx=5, ry=5, fillColor=fill, strokeColor=st, strokeWidth=1.1))
        l1, l2 = t.split("\n")
        label(d, x + bw / 2, 73, l1, 8, INK, bold=True)
        label(d, x + bw / 2, 61, l2, 8, INK, bold=True)
        label(d, x + bw / 2, 44, m, 8, MUTED)
        if i < n - 1:
            arrow(d, x + bw, 65, x + bw + 13, 65)
    label(d, W / 2, 10, "test accuracy shown for stages 1 and 3; stage 2 shows validation accuracy", 7)
    return d


def sequence_diagram():
    d = Drawing(W, 250)
    actors = ["User", "Streamlit UI", "model.py", "Keras model"]
    n = len(actors)
    xs = [W * (i + 0.5) / n for i in range(n)]
    for x, a in zip(xs, actors):
        box(d, x - 55, 215, 110, 28, a, fill=BLUE_L, size=9)
        d.add(Line(x, 215, x, 10, strokeColor=colors.HexColor("#9AA5B1"), strokeDashArray=[3, 3]))
    msgs = [(0, 1, 195, "upload / capture image"), (1, 1, 175, "Image.open() + validate"),
            (1, 2, 155, "predict(image, class_names)"), (2, 2, 135, "EXIF fix, RGB, resize 180x180, /255"),
            (2, 3, 115, "model.predict(batch of 1)"), (3, 2, 95, "37 softmax probabilities"),
            (2, 1, 75, "top-5 (breed, probability)"), (1, 1, 55, "species + low-confidence check"),
            (1, 0, 35, "breed, confidence, bar chart")]
    for a, b, y, t in msgs:
        if a == b:
            d.add(Rect(xs[a] + 4, y - 7, 150 if a == 2 else 135, 14, fillColor=GREY_L, strokeColor=colors.HexColor("#CBD2D9")))
            label(d, xs[a] + 8, y - 3, t, 7, INK, "start")
        else:
            arrow(d, xs[a], y, xs[b], y, ACCENT if a < b else GREEN)
            label(d, (xs[a] + xs[b]) / 2, y + 3, t, 7, INK)
    return d


# ---------- page template ----------
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "Pet Breed Classifier - Architecture Design")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#CBD2D9"))
    canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                            bottomMargin=2.2 * cm, title="Pet Breed Classifier - Architecture Design",
                            author="Pet Breed Classifier project")
    s = []
    # ---- Page 1
    s += [Spacer(1, 1.2 * cm), P("Pet Breed Classifier", TITLE),
          P("Architecture Design Document &nbsp;|&nbsp; Streamlit app + fine-tuned ResNet50", SUB)]
    s += [table([["Item", "Detail"],
                 ["Task", "Single-label image classification: 37 cat and dog breeds (12 cats, 25 dogs)"],
                 ["Dataset", "Oxford-IIIT Pet - 7,390 images, split 5,912 train / 739 validation / 739 test (stratified)"],
                 ["Model", "ResNet50 (ImageNet) + GAP + Dense(256) + Dropout(0.5) + Dense(37, softmax); 24.1M parameters"],
                 ["Input", "RGB image resized to 180 x 180"],
                 ["Result", "89.0% test accuracy, 0.351 test loss"],
                 ["Frontend", "Streamlit (upload or camera input, top-5 chart, low-confidence warning)"],
                 ["Packaging", "Python 3.11, requirements.txt, Dockerfile, Git LFS for the model"]],
                [3 * cm, W - 3 * cm])]
    s += [P("1. Purpose and scope", H2),
          P("This document describes how the trained notebook model is packaged into an interactive web application. "
            "The app lets a user upload or capture a photo and returns the predicted breed, its species, the model's "
            "confidence and the five most likely breeds. Training is performed offline in the notebook "
            "(<font face='Courier'>notebooks/oxford_III_cat_dog.ipynb</font>); the app only performs inference."),
          P("2. Design goals", H2)]
    s += bullets(["<b>Faithful preprocessing</b> - inference uses exactly the same resize and scaling as the training pipeline.",
                  "<b>Simple deployment</b> - one process, no database, no external API; works locally, in Docker or on Streamlit Community Cloud.",
                  "<b>Honest outputs</b> - show probabilities, not only a label, and warn when confidence is low.",
                  "<b>Cached model</b> - load once per server process with <font face='Courier'>st.cache_resource</font>."])
    s += [PageBreak()]

    # ---- Page 2
    s += [P("3. System architecture", H1),
          P("The system is a single Python process. The browser talks to Streamlit; Streamlit calls small, testable "
            "modules for preprocessing, inference and label handling."),
          Spacer(1, 6), system_diagram(), P("Figure 1 - Components and request flow", CAP), Spacer(1, 8),
          P("Components", H2),
          table([["Component", "Responsibility"],
                 ["<font face='Courier'>app.py</font>", "UI layout, file/camera input, caching, error handling, result rendering"],
                 ["<font face='Courier'>src/model.py</font>", "Model loading (with Lambda custom object), preprocessing, top-k prediction, optional model download"],
                 ["<font face='Courier'>src/labels.py</font>", "Loads class names, enforces model output order, species detection, display names"],
                 ["<font face='Courier'>models/</font>", "<i>best_finetuned_model.keras</i> (~165 MB, Git LFS) and <i>class_names.json</i>"],
                 ["<font face='Courier'>tests/</font>", "Unit tests for label logic (run without TensorFlow)"]],
                [4.2 * cm, W - 4.2 * cm])]
    s += [P("Streamlit execution model", H2),
          P("Streamlit reruns the script on every interaction. Expensive objects are therefore cached: the model with "
            "<font face='Courier'>@st.cache_resource</font> (shared across sessions) and the class list with "
            "<font face='Courier'>@st.cache_data</font>."), PageBreak()]

    # ---- Page 3
    s += [P("4. Model architecture", H1),
          P("A ResNet50 convolutional base pre-trained on ImageNet is reused as a feature extractor and partially fine-tuned. "
            "Preprocessing is embedded in the model, so callers only supply values in the 0-1 range."),
          Spacer(1, 6), model_diagram(), P("Figure 2 - Layer stack of <i>best_finetuned_model.keras</i>", CAP), Spacer(1, 6),
          P("Key design decisions", H2)]
    s += bullets(["<b>Transfer learning</b> - a CNN trained from scratch reached only 27.7% test accuracy; ResNet50 features lift this to 89%.",
                  "<b>Partial fine-tuning</b> - layers from <font face='Courier'>conv5_block1_out</font> onward were unfrozen with a very low learning rate (1e-6). "
                  "BatchNorm layers stay frozen to protect pre-trained statistics.",
                  "<b>Embedded preprocessing</b> - Rescaling(255) followed by <font face='Courier'>preprocess_input</font> keeps the data pipeline simple (0-1 floats) "
                  "but means the Lambda layer needs <font face='Courier'>custom_objects</font> and <font face='Courier'>safe_mode=False</font> at load time.",
                  "<b>Regularisation</b> - augmentation (training only) and Dropout(0.5) in the head."])
    s += [P("Output label mapping", H2),
          P("Training labels were created from <font face='Courier'>sorted(unique_breeds)</font>, so output neuron <i>i</i> maps to the "
            "<i>i</i>-th breed in alphabetical order (uppercase cat breeds first, e.g. 0 = Abyssinian, 1 = Bengal, ..., 12 = american_bulldog). "
            "The notebook exported <font face='Courier'>class_names.json</font> in dataset-shuffle order instead; "
            "<font face='Courier'>labels.py</font> always re-sorts the names, which restores the correct mapping."),
          PageBreak()]

    # ---- Page 4
    s += [P("5. Training pipeline", H1),
          P("Training happens offline in Google Colab. The exported model is the artefact consumed by the app."),
          Spacer(1, 6), flow_diagram(), P("Figure 3 - Training stages and results", CAP), Spacer(1, 6),
          table([["Stage", "Setup", "Optimizer / LR", "Result"],
                 ["1. Baseline CNN", "4 x Conv-Pool, Dense(256), Dropout; 5.7M params, from scratch", "Adam 1e-3", "27.7% test acc"],
                 ["2. Feature extraction", "ResNet50 frozen, new head trained, up to 15 epochs", "Adam 1e-3", "~89% val acc"],
                 ["3. Fine-tuning", "Unfreeze conv5_block1_out onward (BN frozen), up to 10 epochs", "Adam 1e-6", "89.5% val, 89.0% test"]],
                [3.2 * cm, 7.3 * cm, 3 * cm, W - 13.5 * cm]),
          P("Data pipeline", H2)]
    s += bullets(["Labels come from file names (<font face='Courier'>leonberger_58.jpg</font> -> <i>leonberger</i>); 37 balanced classes of about 200 images each.",
                  "Shuffle (seed 42), then 80% train and a 50/50 split of the remainder into validation and test, stratified by class.",
                  "<font face='Courier'>tf.data</font>: read file, decode JPEG (3 channels), bilinear resize to 180x180, divide by 255, batch 32, prefetch.",
                  "EarlyStopping on validation loss (patience 5, restore best weights)."])
    s += [PageBreak(), KeepTogether([P("6. Inference sequence", H1), sequence_diagram(), P("Figure 4 - Single prediction", CAP)]), Spacer(1, 10)]

    # ---- Page 5
    s += [P("7. Deployment", H1),
          table([["Option", "How", "Notes"],
                 ["Local", "<font face='Courier'>pip install -r requirements.txt</font><br/><font face='Courier'>streamlit run app.py</font>", "Fastest way to try; needs the model in models/"],
                 ["Docker", "<font face='Courier'>docker build -t pet-app .</font><br/><font face='Courier'>docker run -p 8501:8501 pet-app</font>", "Uses tensorflow-cpu; reproducible"],
                 ["Streamlit Community Cloud", "Connect GitHub repo, main file app.py", "Git LFS files are fetched on deploy; or set MODEL_URL secret"],
                 ["Hugging Face Spaces", "Streamlit/Docker Space; host the model in the Hub", "Good option for files > 100 MB"]],
                [3.6 * cm, 7.4 * cm, W - 11 * cm]),
          P("Model hosting", H2),
          P("GitHub rejects single files above 100 MB, and the model is about 165 MB. Two supported approaches: "
            "(a) <b>Git LFS</b> (<font face='Courier'>.gitattributes</font> already tracks *.keras; free quota is 1 GB storage / 1 GB bandwidth per month), "
            "or (b) host the file elsewhere (GitHub Release asset, Hugging Face Hub, cloud bucket) and set the "
            "<font face='Courier'>MODEL_URL</font> environment variable; the app downloads it once on first start."),
          P("Configuration", H2),
          table([["Name", "Where", "Purpose"],
                 ["MODEL_URL", "env var or .streamlit/secrets.toml", "Direct-download URL used when models/best_finetuned_model.keras is missing"],
                 ["maxUploadSize", ".streamlit/config.toml", "Upload limit in MB (default 10)"]],
                [3.2 * cm, 5.5 * cm, W - 8.7 * cm]),
          PageBreak(),
          P("8. Repository layout", H2),
          P("<font face='Courier' size=8>app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Streamlit UI<br/>"
            "src/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model.py, labels.py<br/>"
            "models/ &nbsp;&nbsp;&nbsp;&nbsp;best_finetuned_model.keras (LFS), class_names.json<br/>"
            "notebooks/ &nbsp;training notebook<br/>"
            "docs/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;architecture.pdf + generator script<br/>"
            "tests/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pytest unit tests<br/>"
            "Dockerfile, requirements.txt, .gitignore, .gitattributes, ruff.toml, LICENSE, README.md<br/>"
            ".github/workflows/ci.yml &nbsp;lint + tests</font>", BODY)]
    s += [P("9. Limitations and future work", H1)]
    s += bullets(["<b>Closed set</b> - only 37 breeds. Softmax always produces a breed, so other animals or objects get a confident-looking wrong answer; the app only warns below 50% confidence. "
                  "Adding an 'other / not a pet' class or an out-of-distribution detector would help.",
                  "<b>Mixed breeds</b> - the dataset contains purebreds; mixed breeds will be mapped to the nearest known breed.",
                  "<b>Accuracy</b> - 89% overall; visually similar pairs (e.g. American Bulldog vs. Staffordshire Bull Terrier, Ragdoll vs. Birman) are the main errors. "
                  "Higher resolution (224+), longer fine-tuning or a newer backbone (EfficientNetV2, ConvNeXt) are natural upgrades.",
                  "<b>Model security</b> - Lambda layers require <font face='Courier'>safe_mode=False</font>; only load model files you produced. "
                  "Re-exporting the model without a Lambda layer (preprocessing in the app) would remove this requirement.",
                  "<b>Throughput</b> - CPU inference of one image takes well under a second, which is fine for a demo; add batching or a model server for heavy traffic."])
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
