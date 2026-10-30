from pathlib import Path

import pandas as pd

csv_path = Path("data/processed/articles_unified.csv")

df = pd.read_csv(csv_path)

# Conserver les valeurs manquantes tout en utilisant des entiers
df["label"] = pd.to_numeric(df["label"], errors="raise").astype("Int64")

df.to_csv(csv_path, index=False)

print("Valeurs de label :")
print(df["label"].value_counts(dropna=False))
print(f"Nombre d'articles : {len(df)}")