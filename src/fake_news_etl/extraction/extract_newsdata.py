"""
Extraction automatisable des actualités via NewsData.io.

- Paramètres configurables
- Gestion des erreurs HTTP et API
- Sauvegarde JSON horodatée
- Logs de suivi
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "newsdata"

API_URL = "https://newsdata.io/api/1/latest"

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Connexion à l'API
# --------------------------------------------------

def fetch_news(
    api_key: str,
    language: str = "fr",
    category: str | None = None,
) -> dict:
    """Interroge NewsData.io et retourne la réponse JSON."""

    params = {
        "apikey": api_key,
        "language": language,
    }

    if category:
        params["category"] = category

    logger.info(
        "Requête NewsData.io : langue=%s, catégorie=%s",
        language,
        category or "toutes",
    )

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

    except requests.Timeout as error:
        raise RuntimeError(
            "Délai d'attente dépassé pour NewsData.io."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"Erreur HTTP lors de l'appel API : {error}"
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "La réponse de l'API n'est pas un JSON valide."
        ) from error

    if payload.get("status") != "success":
        raise RuntimeError(
            f"Réponse API non valide : {payload.get('results', payload.get('status'))}"
        )

    results = payload.get("results")

    if not isinstance(results, list):
        raise RuntimeError(
            "Champ 'results' absent ou de type incorrect."
        )

    return payload


# --------------------------------------------------
# 3. Validation
# --------------------------------------------------

def validate_articles(payload: dict) -> tuple[int, int]:
    """Contrôle le nombre d'articles et de liens d'images."""

    articles = payload["results"]

    if not articles:
        logger.warning(
            "Aucun article retourné par l'API."
        )
        return 0, 0

    image_count = sum(
        bool(article.get("image_url"))
        for article in articles
        if isinstance(article, dict)
    )

    logger.info(
        "%s articles récupérés, %s références d'images",
        len(articles),
        image_count,
    )

    return len(articles), image_count


# --------------------------------------------------
# 4. Sauvegarde
# --------------------------------------------------

def save_json(payload: dict, output_dir: Path) -> Path:
    """Enregistre la réponse brute dans un fichier JSON."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S_%fZ"
    )

    destination = output_dir / f"newsdata_{timestamp}.json"

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    logger.info(
        "Réponse JSON sauvegardée : %s",
        destination,
    )

    return destination


# --------------------------------------------------
# 5. Orchestration
# --------------------------------------------------

def extract_newsdata(
    language: str = "fr",
    category: str | None = None,
) -> None:
    """Exécute une extraction complète."""

    api_key = os.getenv("NEWSDATA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NEWSDATA_API_KEY absente du fichier .env."
        )

    logger.info("Début de l'extraction NewsData.io")

    payload = fetch_news(
        api_key=api_key,
        language=language,
        category=category,
    )

    count, images = validate_articles(payload)

    destination = save_json(
        payload,
        OUTPUT_DIR,
    )

    logger.info(
        "Extraction terminée : %s articles, %s images référencées. "
        "Fichier : %s",
        count,
        images,
        destination.name,
    )


# --------------------------------------------------
# 6. Point d'entrée
# --------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extraction des actualités NewsData.io."
    )

    parser.add_argument(
        "--language",
        default="fr",
        help="Langue des articles (défaut : fr).",
    )

    parser.add_argument(
        "--category",
        default=None,
        help="Catégorie optionnelle.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        extract_newsdata(
            language=args.language,
            category=args.category,
        )
    except RuntimeError:
        logger.exception(
            "Échec de l'extraction NewsData.io"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()