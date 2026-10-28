# CheckIt.AI — Pipeline ETL de données multimodales

Pipeline Python de collecte, transformation et harmonisation de données textuelles et multimodales pour un projet d'analyse de fausses informations.

## Sources de données

* **FakeNewsNet** : données historiques annotées (`real` / `fake`).
* **Fakeddit** : données multimodales avec annotations issues d'une supervision faible.
* **NewsData.io** : actualités récentes collectées via API, sans labels de véracité.

## Installation

Prérequis : Python 3.11 et `uv`.

Depuis la racine du projet :

```bash
uv sync
```

## Exécution du pipeline

### 1. Extraction des données

```bash
uv run python -m fake_news_etl.extraction.extract_fakenewsnet
uv run python -m fake_news_etl.extraction.extract_fakeddit
uv run python -m fake_news_etl.extraction.extract_newsdata
```

L'extraction NewsData.io nécessite une clé API configurée dans le fichier `.env`.

### 2. Transformation et harmonisation

```bash
uv run python -m fake_news_etl.transformation.transform_fakenewsnet
uv run python -m fake_news_etl.transformation.transform_fakeddit
uv run python -m fake_news_etl.transformation.transform_newsdata
```

### 3. Fusion des sources

```bash
uv run python -m fake_news_etl.transformation.merge_sources
```

**Résultat :** `data/processed/articles_unified.csv`

Le fichier contient les observations des trois sources, harmonisées selon un schéma commun de 14 colonnes.

## Tests automatisés

Depuis la racine du projet :

```bash
uv run pytest tests/ -v
```

Les tests vérifient notamment la structure des données, les identifiants, les annotations et la cohérence de la fusion.

## Organisation du projet

```text
data/
├── raw/                  # Données extraites
└── processed/            # Données transformées et fusionnées

docs/                     # Documentation et schéma conceptuel

src/fake_news_etl/
├── extraction/           # Scripts d'extraction
└── transformation/       # Nettoyage, harmonisation et fusion

tests/                    # Tests automatisés
```

## Documentation

Le modèle conceptuel, les relations entre les données et l'association texte-image sont décrits dans [docs/schema_conceptuel.md](docs/schema_conceptuel.md).

## État du projet

* [x] Extraction des données
* [x] Transformation et harmonisation
* [ ] Chargement et orchestration du pipeline
* [ ] Monitoring
