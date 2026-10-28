"""
Définition du schéma commun des données transformées.

Ce module constitue le contrat de données
du pipeline de transformation.
"""

import pandas as pd


# --------------------------------------------------
# 1. Colonnes attendues
# --------------------------------------------------

SCHEMA_COLUMNS = [
    "id",
    "source",
    "source_id",
    "title",
    "text",
    "image_url",
    "image_path",
    "article_url",
    "published_at",
    "language",
    "label",
    "original_label",
    "label_status",
    "modality",
]


# --------------------------------------------------
# 2. Sources autorisées
# --------------------------------------------------

VALID_SOURCES = {
    "fakenewsnet",
    "fakeddit",
    "newsdata",
}


# --------------------------------------------------
# 3. Modalités autorisées
# --------------------------------------------------

VALID_MODALITIES = {
    "text",
    "image",
    "text_image",
    "unknown",
}


# --------------------------------------------------
# 4. Statuts des labels
# --------------------------------------------------

VALID_LABEL_STATUSES = {
    "binary",
    "multiclass",
    "unlabeled",
}


# --------------------------------------------------
# 5. Création d'un DataFrame vide
# --------------------------------------------------

def create_empty_dataframe() -> pd.DataFrame:
    """
    Crée un DataFrame vide avec les colonnes
    du schéma commun.
    """

    return pd.DataFrame(columns=SCHEMA_COLUMNS)


# --------------------------------------------------
# 6. Vérification du schéma
# --------------------------------------------------

def validate_schema(df: pd.DataFrame) -> None:
    """
    Vérifie la présence des colonnes attendues
    et certaines contraintes de cohérence.

    Lève une exception si une règle est violée.
    """

    missing_columns = set(SCHEMA_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {sorted(missing_columns)}"
        )

    if df.empty:
        return

    if df["id"].isna().any():
        raise ValueError("Des identifiants sont manquants.")

    if df["id"].duplicated().any():
        raise ValueError("Des identifiants sont dupliqués.")

    if df["source_id"].isna().any():
        raise ValueError("Des identifiants source sont manquants.")

    if df["source"].isna().any():
        raise ValueError("Des sources sont manquantes.")

    if not df["source"].isin(VALID_SOURCES).all():
        raise ValueError("Une source est inconnue.")

    if not df["modality"].isin(VALID_MODALITIES).all():
        raise ValueError("Une modalité est invalide.")

    if not df["label_status"].isin(
        VALID_LABEL_STATUSES
    ).all():
        raise ValueError("Un statut de label est invalide.")

    valid_labels = df["label"].dropna()

    if not valid_labels.isin([0, 1]).all():
        raise ValueError(
            "Les labels binaires doivent être 0 ou 1."
        )