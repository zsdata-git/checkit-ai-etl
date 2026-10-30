"""
Fusion des données transformées provenant de trois sources :
- FakeNewsNet
- Fakeddit
- NewsData.io

Objectif :
Produire un jeu de données unifié respectant le schéma commun.
"""

import logging
from pathlib import Path

import pandas as pd

from fake_news_etl.transformation.schema import SCHEMA_COLUMNS


# ============================================================
# 1. Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILES = {
    "FakeNewsNet": PROCESSED_DIR / "fakenewsnet.csv",
    "Fakeddit": PROCESSED_DIR / "fakeddit.csv",
    "NewsData.io": PROCESSED_DIR / "newsdata.csv",
}

OUTPUT_FILE = PROCESSED_DIR / "articles_unified.csv"

logger = logging.getLogger(__name__)


# ============================================================
# 2. Lecture des données
# ============================================================

def load_source(source_name: str, file_path: Path) -> pd.DataFrame:
    """Charge un fichier CSV et vérifie son schéma."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable pour {source_name} : {file_path}"
        )

    df = pd.read_csv(file_path, dtype={"id": "string", "source_id": "string"})

    logger.info(
        "%s chargé : %s lignes, %s colonnes",
        source_name,
        len(df),
        len(df.columns),
    )

    expected_columns = list(SCHEMA_COLUMNS)

    missing_columns = set(expected_columns) - set(df.columns)
    extra_columns = set(df.columns) - set(expected_columns)

    if missing_columns or extra_columns:
        raise ValueError(
            f"Schéma incorrect pour {source_name}. "
            f"Colonnes manquantes : {missing_columns}. "
            f"Colonnes supplémentaires : {extra_columns}."
        )

    if df["source"].isna().any():
        raise ValueError(
            f"Valeurs manquantes dans la colonne source : {source_name}"
        )

    if not df["source"].eq(source_name).all():
        raise ValueError(
            f"Provenance incohérente dans le fichier {source_name}"
        )

    return df[expected_columns]


# ============================================================
# 3. Fusion
# ============================================================

def merge_dataframes(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatène les sources et vérifie les identifiants."""

    df_unified = pd.concat(
        dataframes,
        ignore_index=True,
    )

    
    logger.info(
        "Fusion effectuée : %s observations",
        len(df_unified),
    )

    # Normalisation des labels pour PostgreSQL.
    # Conserve les valeurs manquantes des articles non étiquetés.
    df_unified["label"] = pd.to_numeric(
        df_unified["label"],
        errors="raise",
    ).astype("Int64")

    logger.info("Labels normalisés au format entier nullable (Int64).")

    if df_unified["id"].isna().any():
        raise ValueError("Certains identifiants sont manquants.")

    duplicate_count = df_unified["id"].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{duplicate_count} identifiants dupliqués détectés."
        )

    logger.info("Validation des identifiants terminée.")

    return df_unified


# ============================================================
# 4. Sauvegarde
# ============================================================

def save_data(df: pd.DataFrame) -> None:
    """Enregistre le fichier final."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    logger.info("Fichier enregistré : %s", OUTPUT_FILE)


# ============================================================
# 5. Pipeline
# ============================================================

def run_pipeline() -> pd.DataFrame:
    """Exécute la lecture, la fusion, la validation et l'export."""

    logger.info("Début du pipeline de fusion.")

    dataframes = []

    for source_name, file_path in INPUT_FILES.items():
        df = load_source(source_name, file_path)
        dataframes.append(df)

    df_unified = merge_dataframes(dataframes)

    logger.info("Répartition par source :")
    logger.info(
        "\n%s",
        df_unified["source"].value_counts().to_string(),
    )

    logger.info("Répartition des statuts de labels :")
    logger.info(
        "\n%s",
        df_unified["label_status"].value_counts(
            dropna=False
        ).to_string(),
    )

    save_data(df_unified)

    logger.info("Pipeline de fusion terminé.")

    return df_unified


# ============================================================
# 6. Point d'entrée
# ============================================================

def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    run_pipeline()


if __name__ == "__main__":
    main()