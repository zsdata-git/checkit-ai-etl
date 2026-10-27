"""
Tests de validation des extractions de données.

Les tests utilisent les fichiers locaux et des réponses simulées.
Aucun appel réel à NewsData.io n'est effectué.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from fake_news_etl.extraction.extract_newsdata import validate_articles


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


# --------------------------------------------------
# 1. FakeNewsNet
# --------------------------------------------------

def test_fakenewsnet_files_exist():
    """Vérifie la présence des deux fichiers historiques."""

    directory = RAW_DIR / "fakenewsnet"

    assert (directory / "politifact_fake.csv").is_file()
    assert (directory / "politifact_real.csv").is_file()


def test_fakenewsnet_data():
    """Vérifie que les fichiers contiennent des observations."""

    directory = RAW_DIR / "fakenewsnet"

    fake = pd.read_csv(directory / "politifact_fake.csv")
    real = pd.read_csv(directory / "politifact_real.csv")

    assert not fake.empty
    assert not real.empty

    assert "id" in fake.columns
    assert "id" in real.columns


# --------------------------------------------------
# 2. Fakeddit
# --------------------------------------------------

def test_fakeddit_data():
    """Vérifie la présence de données multimodales."""

    filepath = (
        RAW_DIR
        / "fakeddit"
        / "multimodal_validate.tsv"
    )

    assert filepath.is_file()

    df = pd.read_csv(filepath, sep="\t")

    assert not df.empty
    assert "image_url" in df.columns
    assert df["image_url"].notna().any()


# --------------------------------------------------
# 3. NewsData.io
# --------------------------------------------------

def load_latest_newsdata():
    """Charge le fichier JSON NewsData.io le plus récent."""

    directory = RAW_DIR / "newsdata"

    files = sorted(directory.glob("newsdata_*.json"))

    assert files, "Aucun fichier NewsData.io trouvé."

    with files[-1].open(encoding="utf-8") as file:
        return json.load(file)


def test_newsdata_json_structure():
    """Vérifie la structure générale de la réponse."""

    payload = load_latest_newsdata()

    assert payload["status"] == "success"
    assert isinstance(payload["results"], list)
    assert len(payload["results"]) > 0


def test_newsdata_article_fields():
    """Vérifie les champs essentiels des articles."""

    payload = load_latest_newsdata()

    required_fields = {
        "article_id",
        "title",
        "link",
        "pubDate",
        "image_url",
    }

    for article in payload["results"]:
        assert required_fields.issubset(article.keys())


def test_newsdata_images():
    """Vérifie la présence de références d'images."""

    payload = load_latest_newsdata()

    count, image_count = validate_articles(payload)

    assert count > 0
    assert image_count > 0


# --------------------------------------------------
# 4. Gestion des cas particuliers
# --------------------------------------------------

def test_newsdata_empty_results():
    """Une réponse vide doit être acceptée sans erreur."""

    payload = {"results": []}

    count, image_count = validate_articles(payload)

    assert count == 0
    assert image_count == 0

