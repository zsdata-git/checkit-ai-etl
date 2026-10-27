"""
Extraction des données historiques FakeNewsNet.

Source : dépôt officiel FakeNewsNet.
Sous-ensemble : PolitiFact.
"""

import logging
from pathlib import Path

import pandas as pd
import requests


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "fakenewsnet"

BASE_URL = (
    "https://raw.githubusercontent.com/"
    "KaiDMML/FakeNewsNet/master/dataset"
)

FILES = {
    "politifact_fake.csv": f"{BASE_URL}/politifact_fake.csv",
    "politifact_real.csv": f"{BASE_URL}/politifact_real.csv",
}

EXPECTED_COLUMNS = {
    "id",
    "news_url",
    "title",
    "tweet_ids",
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
# 3. Téléchargement
# --------------------------------------------------

def download_file(url: str, destination: Path) -> None:
    """Télécharge un fichier CSV depuis une URL."""

    logger.info("Téléchargement : %s", url)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_bytes(response.content)

    logger.info(
        "Fichier sauvegardé : %s",
        destination,
    )


# --------------------------------------------------
# 4. Validation
# --------------------------------------------------

def validate_csv(file_path: Path) -> int:
    """Vérifie la structure du CSV et retourne son nombre de lignes."""

    df = pd.read_csv(file_path)

    missing_columns = EXPECTED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {missing_columns}"
        )

    if df.empty:
        raise ValueError(
            f"Le fichier {file_path.name} est vide."
        )

    logger.info(
        "%s : %s lignes, %s colonnes",
        file_path.name,
        len(df),
        len(df.columns),
    )

    return len(df)


# --------------------------------------------------
# 5. Orchestration
# --------------------------------------------------

def extract_fakenewsnet() -> None:
    """Télécharge et valide les fichiers PolitiFact."""

    logger.info("Début de l'extraction FakeNewsNet")

    total_rows = 0

    for filename, url in FILES.items():

        destination = OUTPUT_DIR / filename

        try:
            download_file(url, destination)

            rows = validate_csv(destination)

            total_rows += rows

        except (requests.RequestException, OSError, ValueError, pd.errors.ParserError) as error:
            logger.error(
                "Erreur pour %s : %s",
                filename,
                error,
            )
            raise

    logger.info(
        "Extraction terminée : %s observations",
        total_rows,
    )


# --------------------------------------------------
# 6. Point d'entrée
# --------------------------------------------------

def main() -> None:
    extract_fakenewsnet()


if __name__ == "__main__":
    main()