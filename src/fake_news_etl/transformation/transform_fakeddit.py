"""
Transformation du jeu de données historique Fakeddit.

Entrée :
    data/raw/fakeddit/multimodal_validate.tsv

Sortie :
    data/processed/fakeddit.csv
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

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "fakeddit"
    / "multimodal_validate.tsv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "fakeddit.csv"
)

REQUIRED_COLUMNS = {
    "id",
    "title",
    "clean_title",
    "image_url",
    "created_utc",
    "2_way_label",
}

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Nettoyage
# --------------------------------------------------

def clean_text(value):
    """Nettoie les espaces et les valeurs manquantes."""

    if pd.isna(value):
        return None

    text = re.sub(r"\s+", " ", str(value)).strip()

    return text if text else None


def clean_url(value):
    """Nettoie une URL sans tester son accessibilité."""

    url = clean_text(value)

    if url is None:
        return None

    if not url.startswith(("http://", "https://")):
        return None

    return url


# --------------------------------------------------
# 3. Lecture
# --------------------------------------------------

def load_data(input_path: Path) -> pd.DataFrame:
    """Charge les données brutes de Fakeddit."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {input_path}"
        )

    df = pd.read_csv(
        input_path,
        sep="\t",
        dtype={"id": str},
        low_memory=False,
    )

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Colonnes manquantes : "
            f"{sorted(missing_columns)}"
        )

    logger.info(
        "Fakeddit chargé : %s observations, %s colonnes",
        len(df),
        len(df.columns),
    )

    return df


# --------------------------------------------------
# 4. Transformation
# --------------------------------------------------

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise Fakeddit selon le schéma commun."""

    result = pd.DataFrame(index=df.index)

    source_ids = df["id"].map(clean_text)

    result["id"] = source_ids.map(
        lambda value: f"fakeddit_{value}"
        if value is not None
        else None
    )

    result["source"] = "Fakeddit"

    result["source_id"] = source_ids

    # Priorité au titre nettoyé.
    clean_titles = df["clean_title"].map(clean_text)
    original_titles = df["title"].map(clean_text)

    result["title"] = clean_titles.fillna(original_titles)

    # Pas de corps d'article dans ce fichier.
    # Nous réutilisons le titre comme texte disponible.
    result["text"] = result["title"]

    result["image_url"] = df["image_url"].map(clean_url)

    result["image_path"] = None

    result["article_url"] = None

    # created_utc : timestamp Unix en secondes.
    dates = pd.to_datetime(
        df["created_utc"],
        unit="s",
        utc=True,
        errors="coerce",
    )

    result["published_at"] = dates.dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    result["language"] = None

    # Conservation des annotations d'origine.
    labels = pd.to_numeric(
        df["2_way_label"],
        errors="coerce",
    )

    result["label"] = labels.astype("Int64")

    result["original_label"] = (
        df["2_way_label"].astype("string")
    )

    result["label_status"] = "weak_supervision"

    # Une URL présente ne garantit pas une image accessible.
    result["modality"] = result["image_url"].map(
        lambda value: "text_image"
        if value is not None
        else "text"
    )

    return result[SCHEMA_COLUMNS]


# --------------------------------------------------
# 5. Validation
# --------------------------------------------------

def validate_data(df: pd.DataFrame) -> None:
    """Contrôle la cohérence des données transformées."""

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

    if not df["label"].isin([0, 1]).all():
        raise ValueError(
            "Les labels binaires doivent être 0 ou 1."
        )

    logger.info(
        "Validation terminée : %s observations",
        len(df),
    )


# --------------------------------------------------
# 6. Export
# --------------------------------------------------

def save_data(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Exporte les données normalisées au format CSV."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    logger.info(
        "Fichier enregistré : %s",
        output_path,
    )


# --------------------------------------------------
# 7. Pipeline principal
# --------------------------------------------------

def run_pipeline(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Exécute la transformation complète."""

    df = load_data(input_path)

    transformed_df = transform_data(df)

    validate_data(transformed_df)

    logger.info(
        "Répartition des labels :\n%s",
        transformed_df["label"].value_counts(),
    )

    logger.info(
        "Observations avec URL image : %s",
        transformed_df["image_url"].notna().sum(),
    )

    save_data(transformed_df, output_path)

    logger.info("Pipeline Fakeddit terminé.")

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