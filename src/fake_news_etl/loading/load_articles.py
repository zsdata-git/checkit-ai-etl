import logging
import os
from pathlib import Path

import psycopg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

CSV_PATH = Path(
    os.getenv(
        "ARTICLES_CSV_PATH",
        "data/processed/articles_unified.csv",
    )
)

DB_HOST = os.getenv("CHECKIT_DB_HOST", "localhost")
DB_PORT = int(os.getenv("CHECKIT_DB_PORT", "5433"))
DB_NAME = os.getenv("CHECKIT_DB_NAME", "checkit_db")
DB_USER = os.getenv("CHECKIT_DB_USER", "checkit")


def load_articles() -> None:
    """Charge les articles standardisés dans PostgreSQL."""

    password = os.getenv("CHECKIT_DB_PASSWORD")

    if not password:
        raise ValueError(
            "La variable CHECKIT_DB_PASSWORD est manquante."
        )

    if not CSV_PATH.is_file():
        raise FileNotFoundError(
            f"Fichier CSV introuvable : {CSV_PATH}"
        )

    logger.info("Début du chargement : %s", CSV_PATH)

    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
    ) as conn:

        with conn.cursor() as cur:

            # Table temporaire pour éviter les doublons.
            cur.execute(
                """
                CREATE TEMP TABLE staging_articles
                (LIKE articles INCLUDING DEFAULTS)
                ON COMMIT DROP
                """
            )

            # Importation rapide du CSV.
            with CSV_PATH.open("rb") as csv_file:
                with cur.copy(
                    """
                    COPY staging_articles
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, NULL '')
                    """
                ) as copy:
                    while chunk := csv_file.read(1024 * 1024):
                        copy.write(chunk)

            # Insertion uniquement des nouveaux articles.
            cur.execute(
                """
                INSERT INTO articles
                SELECT * FROM staging_articles
                ON CONFLICT (id) DO NOTHING
                """
            )

            inserted = cur.rowcount

    logger.info(
        "Chargement terminé : %s nouveaux articles insérés.",
        inserted,
    )


if __name__ == "__main__":
    load_articles()