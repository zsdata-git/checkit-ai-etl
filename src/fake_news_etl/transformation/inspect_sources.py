"""
Phase A - Inspection des sources brutes.

Objectif :
- Identifier les colonnes disponibles.
- Vérifier les types de données.
- Examiner les valeurs manquantes.
- Préparer le mapping des transformations.
"""

import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DIR = PROJECT_ROOT / "data" / "raw"


# --------------------------------------------------
# 2. Inspection d'un DataFrame
# --------------------------------------------------

def inspect_dataframe(
    df: pd.DataFrame,
    source_name: str,
) -> None:

    print(f"\n{'=' * 60}")
    print(f"SOURCE : {source_name}")
    print(f"{'=' * 60}")

    print(f"\nDimensions : {df.shape}")

    print("\nColonnes et types :")

    for column, dtype in df.dtypes.items():
        print(f"  {column}: {dtype}")

    print("\nValeurs manquantes :")

    missing = df.isna().sum()

    for column, count in missing.items():
        print(f"  {column}: {count}")

    print("\nPremière observation :")

    if not df.empty:
        print(df.iloc[0].to_dict())


# --------------------------------------------------
# 3. FakeNewsNet
# --------------------------------------------------

def inspect_fakenewsnet() -> None:

    source_dir = RAW_DIR / "fakenewsnet"

    for filename in [
        "politifact_fake.csv",
        "politifact_real.csv",
    ]:

        filepath = source_dir / filename

        df = pd.read_csv(filepath)

        inspect_dataframe(df, filename)


# --------------------------------------------------
# 4. Fakeddit
# --------------------------------------------------

def inspect_fakeddit() -> None:

    filepath = (
        RAW_DIR
        / "fakeddit"
        / "multimodal_validate.tsv"
    )

    df = pd.read_csv(filepath, sep="\t")

    inspect_dataframe(df, "Fakeddit")


# --------------------------------------------------
# 5. NewsData.io
# --------------------------------------------------

def inspect_newsdata() -> None:

    source_dir = RAW_DIR / "newsdata"

    files = sorted(source_dir.glob("newsdata_*.json"))

    if not files:
        raise FileNotFoundError(
            "Aucun fichier NewsData.io trouvé."
        )

    filepath = files[-1]

    with filepath.open(
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(file)

    articles = payload.get("results", [])

    df = pd.DataFrame(articles)

    inspect_dataframe(df, "NewsData.io")


# --------------------------------------------------
# 6. Exécution
# --------------------------------------------------

def main() -> None:

    inspect_fakenewsnet()

    inspect_fakeddit()

    inspect_newsdata()


if __name__ == "__main__":
    main()