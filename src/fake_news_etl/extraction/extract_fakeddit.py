"""
Import ponctuel du jeu de données historique Fakeddit.

Source : fichier TSV multimodal_validate.tsv.
Objectif : vérifier et archiver les données brutes.
"""

import logging
import shutil
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "multimodal_validate.tsv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "fakeddit"

OUTPUT_FILE = OUTPUT_DIR / "multimodal_validate.tsv"

EXPECTED_COLUMNS = {
    "id",
    "clean_title",
    "2_way_label",
    "image_url",
}


# --------------------------------------------------
# 2. Configuration des logs
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. Lecture et validation
# --------------------------------------------------

def validate_tsv(file_path: Path) -> tuple[int, int]:
    """Vérifie la structure et les références d'images du TSV."""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    df = pd.read_csv(file_path, sep="\t")

    missing_columns = EXPECTED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {missing_columns}"
        )

    if df.empty:
        raise ValueError(
            "Le fichier Fakeddit est vide."
        )

    image_count = (
        df["image_url"]
        .notna()
        .sum()
    )

    logger.info(
        "Fichier valide : %s lignes, %s colonnes",
        len(df),
        len(df.columns),
    )

    logger.info(
        "Références d'images présentes : %s / %s",
        image_count,
        len(df),
    )

    return len(df), int(image_count)


# --------------------------------------------------
# 4. Sauvegarde
# --------------------------------------------------

def save_raw_file(source: Path, destination: Path) -> None:
    """Archive une copie du fichier source sans le modifier."""

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(source, destination)

    logger.info(
        "Fichier archivé : %s",
        destination,
    )


# --------------------------------------------------
# 5. Orchestration
# --------------------------------------------------

def extract_fakeddit() -> None:
    """Valide et archive le fichier historique Fakeddit."""

    logger.info("Début de l'import Fakeddit")

    try:
        rows, images = validate_tsv(SOURCE_FILE)

        save_raw_file(
            SOURCE_FILE,
            OUTPUT_FILE,
        )

        logger.info(
            "Import terminé : %s observations, "
            "%s références d'images",
            rows,
            images,
        )

    except (
        FileNotFoundError,
        OSError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        logger.error(
            "Erreur lors de l'import Fakeddit : %s",
            error,
        )
        raise


# --------------------------------------------------
# 6. Point d'entrée
# --------------------------------------------------

def main() -> None:
    extract_fakeddit()


if __name__ == "__main__":
    main()