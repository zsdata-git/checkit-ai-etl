"""
Transformation des réponses JSON de NewsData.io.

Entrées :
    data/raw/newsdata/*.json

Sortie :
    data/processed/newsdata.csv
"""

import json
import logging
import re
from pathlib import Path

import pandas as pd

from fake_news_etl.transformation.schema import SCHEMA_COLUMNS


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "newsdata"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "newsdata.csv"

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Fonctions de nettoyage
# --------------------------------------------------

def clean_text(value):
    """Nettoie un texte et traite les valeurs absentes."""

    if value is None or not isinstance(value, str):
        return None

    text = re.sub(r"\s+", " ", value).strip()

    return text if text else None


def clean_url(value):
    """Conserve uniquement les URL HTTP/HTTPS."""

    url = clean_text(value)

    if url is None:
        return None

    if not url.startswith(("http://", "https://")):
        return None

    return url


def clean_content(value):
    """Exclut les messages de restriction de l'API."""

    text = clean_text(value)

    if text is None:
        return None

    if "ONLY AVAILABLE IN" in text.upper():
        return None

    return text


# --------------------------------------------------
# 3. Lecture des réponses JSON
# --------------------------------------------------

def load_json_files(input_dir: Path) -> list[dict]:
    """Charge les articles de tous les fichiers JSON."""

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Dossier introuvable : {input_dir}"
        )

    json_files = sorted(input_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"Aucun fichier JSON dans {input_dir}"
        )

    articles = []

    for path in json_files:

        logger.info("Lecture : %s", path.name)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError(
                f"Structure JSON invalide : {path.name}"
            )

        if payload.get("status") != "success":
            raise ValueError(
                f"Réponse API non valide : {path.name}"
            )

        results = payload.get("results")

        if not isinstance(results, list):
            raise ValueError(
                f"Champ results invalide : {path.name}"
            )

        articles.extend(results)

        logger.info(
            "%s : %s articles",
            path.name,
            len(results),
        )

    logger.info(
        "Total brut : %s articles",
        len(articles),
    )

    return articles


# --------------------------------------------------
# 4. Transformation
# --------------------------------------------------

def transform_data(articles: list[dict]) -> pd.DataFrame:
    """Normalise les articles selon le schéma commun."""

    records = []

    for article in articles:

        if not isinstance(article, dict):
            logger.warning("Article ignoré : format invalide")
            continue

        source_id = clean_text(article.get("article_id"))
        title = clean_text(article.get("title"))

        description = clean_content(article.get("description"))
        content = clean_content(article.get("content"))

        # Priorité au contenu lorsqu'il est réellement accessible.
        text = content or description or title

        image_url = clean_url(article.get("image_url"))

        publication_date = pd.to_datetime(
            article.get("pubDate"),
            utc=True,
            errors="coerce",
        )

        published_at = (
            publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            if not pd.isna(publication_date)
            else None
        )

        record = {
            "id": (
                f"newsdata_{source_id}"
                if source_id is not None
                else None
            ),
            "source": "NewsData.io",
            "source_id": source_id,
            "title": title,
            "text": text,
            "image_url": image_url,
            "image_path": None,
            "article_url": clean_url(article.get("link")),
            "published_at": published_at,
            "language": clean_text(article.get("language")),
            "label": None,
            "original_label": None,
            "label_status": "unlabeled",
            "modality": (
                "text_image" if image_url else "text"
            ),
        }

        records.append(record)

    df = pd.DataFrame(records, columns=SCHEMA_COLUMNS)

    logger.info(
        "Transformation terminée : %s observations",
        len(df),
    )

    return df


# --------------------------------------------------
# 5. Validation et déduplication
# --------------------------------------------------

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Contrôle les champs obligatoires et retire les doublons."""

    if df.empty:
        raise ValueError("Aucun article à transformer.")

    missing_ids = df["id"].isna().sum()
    missing_titles = df["title"].isna().sum()

    if missing_ids:
        logger.warning(
            "%s articles sans identifiant",
            missing_ids,
        )

    if missing_titles:
        logger.warning(
            "%s articles sans titre",
            missing_titles,
        )

    # Les observations inexploitables sont écartées.
    df = df.dropna(subset=["id", "title"]).copy()

    before = len(df)

    # Un même article peut apparaître dans plusieurs réponses API.
    df = df.drop_duplicates(
        subset=["id"],
        keep="last",
    )

    logger.info(
        "Doublons supprimés : %s",
        before - len(df),
    )

    if df.empty:
        raise ValueError(
            "Aucun article valide après nettoyage."
        )

    if df["id"].duplicated().any():
        raise ValueError(
            "Des identifiants dupliqués subsistent."
        )

    if list(df.columns) != SCHEMA_COLUMNS:
        raise ValueError(
            "Le schéma final ne correspond pas au schéma commun."
        )

    logger.info(
        "Validation terminée : %s articles",
        len(df),
    )

    return df


# --------------------------------------------------
# 6. Export
# --------------------------------------------------

def save_data(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Enregistre les données normalisées au format CSV."""

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
    input_dir: Path = INPUT_DIR,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Exécute le pipeline de transformation NewsData.io."""

    articles = load_json_files(input_dir)

    df = transform_data(articles)

    df = validate_data(df)

    logger.info(
        "Articles avec URL image : %s",
        df["image_url"].notna().sum(),
    )

    logger.info(
        "Articles sans description : %s",
        (df["text"] == df["title"]).sum(),
    )

    save_data(df, output_path)

    logger.info("Pipeline NewsData.io terminé.")

    return df


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