import json
from pathlib import Path

import pytest

from src.labels import NUM_CLASSES, load_class_names, pretty_name, species_of

CLASS_FILE = Path(__file__).resolve().parents[1] / "models" / "class_names.json"


def test_class_count():
    assert len(load_class_names(CLASS_FILE)) == NUM_CLASSES


def test_order_matches_training_labels():
    """Model output index i must be sorted(names)[i] (see src/labels.py)."""
    names = load_class_names(CLASS_FILE)
    assert names[0] == "Abyssinian"
    assert names[1] == "Bengal"
    assert names[12] == "american_bulldog"
    assert names[-1] == "yorkshire_terrier"
    assert names == sorted(names)


def test_shuffled_file_is_fixed(tmp_path):
    """The notebook exported names in shuffled order; loader must re-sort them."""
    shuffled = json.loads(CLASS_FILE.read_text())[::-1]
    p = tmp_path / "c.json"
    p.write_text(json.dumps(shuffled))
    assert load_class_names(p) == sorted(shuffled)


def test_species_split():
    names = load_class_names(CLASS_FILE)
    assert sum(species_of(n) == "Cat" for n in names) == 12
    assert sum(species_of(n) == "Dog" for n in names) == 25


def test_wrong_length_raises(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ValueError):
        load_class_names(p)


def test_pretty_name():
    assert pretty_name("american_pit_bull_terrier") == "American Pit Bull Terrier"
