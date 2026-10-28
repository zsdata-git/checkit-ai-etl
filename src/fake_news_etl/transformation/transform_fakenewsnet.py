"""
Transformation des données historiques FakeNewsNet.

Entrées :
    data/raw/fakenewsnet/politifact_fake.csv
    data/raw/fakenewsnet/politifact_real.csv

Sortie :
    data/processed/fakenewsnet.csv
"""

import logging
import re
from pathlib import Path

import pandas as pd

from fake_news_etl.transformation.schema import SCHEMA_COLUMNS


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "fakenewsnet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

FILES = {
    "fake": INPUT_DIR / "politifact_fake.csv",
    "real": INPUT_DIR / "politifact_real.csv",
}

LABEL_MAPPING = {
    "fake": 1,
    "real": 0,
}

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Nettoyage
# --------------------------------------------------

def clean_text(value):
    """Nettoie les espaces et les valeurs textuelles manquantes."""

    if pd.isna(value):
        return None

    text = re.sub(r"\s+", " ", str(value)).strip()

    return text if text else None


def clean_url(value):
    """Nettoie une URL sans vérifier son accessibilité."""

    url = clean_text(value)

    if url is None:
        return None

    if not url.startswith(("http://", "https://")):
        return None

    return url


# --------------------------------------------------
# 3. Lecture
# --------------------------------------------------

def load_source(path: Path, original_label: str) -> pd.DataFrame:
    """Charge un fichier FakeNewsNet et ajoute son label."""

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    df = pd.read_csv(path, dtype=str)

    required_columns = {"id", "title", "news_url"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes dans {path.name} : "
            f"{sorted(missing_columns)}"
        )

    df["original_label"] = original_label

    logger.info(
        "%s chargé : %s observations",
        path.name,
        len(df),
    )

    return df


# --------------------------------------------------
# 4. Transformation
# --------------------------------------------------

def transform_source(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les observations selon le schéma commun."""

    result = pd.DataFrame(index=df.index)

    source_ids = df["id"].map(clean_text)

    result["id"] = [
        f"fakenewsnet_{label}_{source_id}"
        if source_id is not None
        else None
        for label, source_id in zip(
            df["original_label"],
            source_ids
        )
    ]

    result["source"] = "FakeNewsNet"

    result["source_id"] = source_ids

    result["title"] = df["title"].map(clean_text)

    result["text"] = None

    result["image_url"] = None

    result["image_path"] = None

    result["article_url"] = df["news_url"].map(clean_url)

    result["published_at"] = None

    result["language"] = None

    result["label"] = df["original_label"].map(LABEL_MAPPING)

    result["original_label"] = df["original_label"]

    result["label_status"] = "binary"

    result["modality"] = "text"

    return result[SCHEMA_COLUMNS]


# --------------------------------------------------
# 5. Vérifications
# --------------------------------------------------

def validate_data(df: pd.DataFrame) -> None:
    """Vérifie les contraintes essentielles du résultat."""

    if df.empty:
        raise ValueError("Le fichier transformé est vide.")

    if df["id"].isna().any():
        raise ValueError("Certains identifiants sont manquants.")

    if df["id"].duplicated().any():
        raise ValueError("Des identifiants sont dupliqués.")

    if df["title"].isna().any():
        raise ValueError("Certains titres sont manquants.")

    if df["label"].isna().any():
        raise ValueError("Certains labels sont manquants.")

    logger.info("Validation terminée : %s observations", len(df))


# --------------------------------------------------
# 6. Export
# --------------------------------------------------

def save_data(df: pd.DataFrame, output_path: Path) -> None:
    """Enregistre les données normalisées au format CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    logger.info("Fichier enregistré : %s", output_path)


# --------------------------------------------------
# 7. Pipeline principal
# --------------------------------------------------

def run_pipeline(
    input_files: dict | None = None,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """Exécute la transformation complète de FakeNewsNet."""

    input_files = input_files or FILES

    output_path = output_path or (
        OUTPUT_DIR / "fakenewsnet.csv"
    )

    frames = []

    for original_label, path in input_files.items():

        df = load_source(path, original_label)

        frames.append(df)

    raw_df = pd.concat(frames, ignore_index=True)

    logger.info(
        "Fusion terminée : %s observations",
        len(raw_df),
    )

    transformed_df = transform_source(raw_df)

    validate_data(transformed_df)

    save_data(transformed_df, output_path)

    logger.info("Pipeline FakeNewsNet terminé.")

    return transformed_df


# --------------------------------------------------
# 8. Point d'entrée
# --------------------------------------------------

def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    run_pipeline()


if __name__ == "__main__":
    main()