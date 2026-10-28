"""
Tests automatisés du pipeline de transformation.

Objectifs :
- Vérifier le schéma commun.
- Contrôler les fichiers transformés.
- Vérifier les labels et leur provenance.
- Tester la fusion et la détection des doublons.
- Tester les cas particuliers.
"""

from pathlib import Path

import pandas as pd
import pytest

from fake_news_etl.transformation.schema import SCHEMA_COLUMNS
from fake_news_etl.transformation.merge_sources import merge_dataframes


# ============================================================
# 1. Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SOURCE_FILES = {
    "FakeNewsNet": PROCESSED_DIR / "fakenewsnet.csv",
    "Fakeddit": PROCESSED_DIR / "fakeddit.csv",
    "NewsData.io": PROCESSED_DIR / "newsdata.csv",
}

EXPECTED_COLUMNS = list(SCHEMA_COLUMNS)

REQUIRED_COLUMNS = {
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
}


# ============================================================
# 2. Fixtures
# ============================================================

@pytest.fixture(scope="module")
def source_dataframes():
    """Charge les trois fichiers transformés."""

    dataframes = {}

    for source_name, file_path in SOURCE_FILES.items():

        assert file_path.exists(), (
            f"Fichier manquant : {file_path}"
        )

        dataframes[source_name] = pd.read_csv(file_path)

    return dataframes


@pytest.fixture
def sample_dataframe():
    """Crée un petit jeu de données conforme au schéma."""

    rows = []

    for index in range(2):

        row = {
            column: None
            for column in EXPECTED_COLUMNS
        }

        row.update(
            {
                "id": f"test_{index}",
                "source": "TestSource",
                "source_id": str(index),
                "title": f"Article de test {index}",
                "text": "Contenu de test",
                "label": index,
                "original_label": index,
                "label_status": "binary",
                "modality": "text",
            }
        )

        rows.append(row)

    return pd.DataFrame(rows, columns=EXPECTED_COLUMNS)


# ============================================================
# 3. Tests du schéma commun
# ============================================================

def test_schema_has_14_columns():
    """Le schéma doit contenir exactement 14 colonnes."""

    assert len(EXPECTED_COLUMNS) == 14


def test_schema_has_no_duplicate_columns():
    """Les noms des colonnes doivent être uniques."""

    assert len(EXPECTED_COLUMNS) == len(set(EXPECTED_COLUMNS))


def test_schema_contains_required_columns():
    """Tous les champs attendus doivent être présents."""

    assert set(EXPECTED_COLUMNS) == REQUIRED_COLUMNS


@pytest.mark.parametrize(
    "source_name",
    list(SOURCE_FILES.keys()),
)
def test_source_schema(source_dataframes, source_name):
    """Chaque source doit respecter le schéma commun."""

    df = source_dataframes[source_name]

    assert list(df.columns) == EXPECTED_COLUMNS


# ============================================================
# 4. Tests de qualité des données
# ============================================================

@pytest.mark.parametrize(
    "source_name",
    list(SOURCE_FILES.keys()),
)
def test_source_ids_not_null(source_dataframes, source_name):
    """Les identifiants ne doivent pas être manquants."""

    df = source_dataframes[source_name]

    assert df["id"].notna().all()


@pytest.mark.parametrize(
    "source_name",
    list(SOURCE_FILES.keys()),
)
def test_source_ids_unique(source_dataframes, source_name):
    """Les identifiants doivent être uniques."""

    df = source_dataframes[source_name]

    assert not df["id"].duplicated().any()


@pytest.mark.parametrize(
    "source_name",
    list(SOURCE_FILES.keys()),
)
def test_source_provenance(source_dataframes, source_name):
    """La provenance doit correspondre au fichier."""

    df = source_dataframes[source_name]

    assert df["source"].eq(source_name).all()


@pytest.mark.parametrize(
    "source_name",
    list(SOURCE_FILES.keys()),
)
def test_titles_not_empty(source_dataframes, source_name):
    """Chaque observation doit posséder un titre."""

    df = source_dataframes[source_name]

    assert df["title"].notna().all()

    assert df["title"].astype(str).str.strip().ne("").all()


# ============================================================
# 5. Tests des labels
# ============================================================

def test_fakenewsnet_labels(source_dataframes):
    """FakeNewsNet doit contenir des labels binaires."""

    df = source_dataframes["FakeNewsNet"]

    assert df["label"].notna().all()

    assert set(df["label"].unique()).issubset({0, 1})

    assert df["label_status"].eq("binary").all()


def test_fakeddit_labels(source_dataframes):
    """Fakeddit conserve le statut de supervision faible."""

    df = source_dataframes["Fakeddit"]

    assert df["label"].notna().all()

    assert set(df["label"].unique()).issubset({0, 1})

    assert df["label_status"].eq("weak_supervision").all()


def test_newsdata_unlabeled(source_dataframes):
    """NewsData.io ne doit pas recevoir de faux labels."""

    df = source_dataframes["NewsData.io"]

    assert df["label"].isna().all()

    assert df["label_status"].eq("unlabeled").all()


# ============================================================
# 6. Tests de la fusion
# ============================================================

def test_merge_preserves_rows(sample_dataframe):
    """La fusion doit conserver toutes les observations."""

    first = sample_dataframe.iloc[[0]].copy()

    second = sample_dataframe.iloc[[1]].copy()

    result = merge_dataframes([first, second])

    assert len(result) == 2


def test_merge_preserves_schema(sample_dataframe):
    """La fusion doit conserver les 14 colonnes."""

    result = merge_dataframes([sample_dataframe])

    assert list(result.columns) == EXPECTED_COLUMNS


def test_merge_detects_duplicate_ids(sample_dataframe):
    """Deux identifiants identiques doivent provoquer une erreur."""

    duplicate = sample_dataframe.iloc[[0]].copy()

    with pytest.raises(
        ValueError,
        match="identifiants dupliqués",
    ):
        merge_dataframes([sample_dataframe, duplicate])


def test_merge_detects_missing_ids(sample_dataframe):
    """Un identifiant manquant doit provoquer une erreur."""

    invalid_df = sample_dataframe.copy()

    invalid_df.loc[0, "id"] = None

    with pytest.raises(
        ValueError,
        match="identifiants sont manquants",
    ):
        merge_dataframes([invalid_df])


# ============================================================
# 7. Tests du fichier final
# ============================================================

def test_unified_file_exists():
    """Le fichier final doit avoir été généré."""

    file_path = PROCESSED_DIR / "articles_unified.csv"

    assert file_path.exists()


def test_unified_file_schema():
    """Le fichier unifié doit respecter le schéma."""

    file_path = PROCESSED_DIR / "articles_unified.csv"

    df = pd.read_csv(file_path)

    assert list(df.columns) == EXPECTED_COLUMNS


def test_unified_file_has_no_duplicate_ids():
    """Le fichier unifié ne doit contenir aucun ID dupliqué."""

    file_path = PROCESSED_DIR / "articles_unified.csv"

    df = pd.read_csv(file_path)

    assert not df["id"].duplicated().any()


def test_unified_row_count(source_dataframes):
    """La fusion doit conserver le nombre total de lignes."""

    file_path = PROCESSED_DIR / "articles_unified.csv"

    unified_df = pd.read_csv(file_path)

    expected_count = sum(
        len(df)
        for df in source_dataframes.values()
    )

    assert len(unified_df) == expected_count