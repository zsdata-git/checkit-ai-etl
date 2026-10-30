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

## Orchestration avec Apache Airflow

Le pipeline ETL est orchestré avec Apache Airflow 3.1.3, exécuté dans des conteneurs Docker.

Le DAG `checkit_etl` comprend six tâches :

1. **`verifier_environnement`** : vérification du fonctionnement de l'environnement Airflow.
2. **`extraire_fakenewsnet`** : extraction des données historiques FakeNewsNet.
3. **`extraire_fakeddit`** : extraction des données historiques Fakeddit.
4. **`extraire_newsdata`** : collecte des actualités récentes via l'API NewsData.io.
5. **`transformer_donnees`** : nettoyage, harmonisation et fusion des trois sources.
6. **`charger_donnees`** : chargement des données harmonisées dans PostgreSQL.

Les trois tâches d'extraction peuvent s'exécuter en parallèle. La transformation démarre uniquement après leur réussite, puis le chargement est effectué dans PostgreSQL.

### Démarrage de l'environnement

Depuis la racine du projet :

```bash
docker compose --env-file airflow/.env -f airflow/docker-compose.yaml up -d --build
```

L'interface Airflow est accessible localement sur le port `8080`.

Le DAG `checkit_etl` peut ensuite être déclenché manuellement depuis l'interface.

Les variables d'environnement et les identifiants de connexion sont configurés localement et ne doivent pas être publiés dans le dépôt Git.

## Stockage PostgreSQL

Les données harmonisées sont chargées dans une base PostgreSQL dédiée au projet.

La table `articles` contient notamment les informations textuelles, les références aux images, les sources et les annotations.

### Vérifications effectuées

Après l'exécution du pipeline, les contrôles SQL ont confirmé :

| Contrôle                                  | Résultat |
| ----------------------------------------- | -------- |
| Nombre total d'articles                   | 60 428   |
| Fakeddit                                  | 59 342   |
| FakeNewsNet                               | 1 056    |
| NewsData.io                               | 30       |
| Identifiants dupliqués                    | 0        |
| Titres manquants                          | 0        |
| Identifiants manquants                    | 0        |
| Sources manquantes                        | 0        |
| URL d'article manquantes pour NewsData.io | 0        |

Les annotations sont conservées selon leur provenance :

* **FakeNewsNet** : annotations binaires (`0` : réel, `1` : faux).
* **Fakeddit** : annotations issues d'une supervision faible.
* **NewsData.io** : articles non annotés (`unlabeled`).

Ces contrôles valident la cohérence structurelle des données chargées, sans constituer une vérification indépendante de la véracité des articles.

## Tests automatisés

Depuis la racine du projet :

```bash
uv run pytest tests/ -v
```

Les tests vérifient notamment la structure des données, les identifiants, les annotations et la cohérence de la fusion.

## Organisation du projet

```text
fake-news-etl/
│
├── airflow/
│   ├── config/                  # Configuration Airflow
│   ├── dags/
│   │   └── checkit_etl.py       # DAG d'orchestration ETL
│   ├── logs/                    # Journaux d'exécution Airflow
│   ├── plugins/
│   ├── .env                     # Variables d'environnement (non versionnées)
│   ├── docker-compose.yaml      # Configuration des conteneurs
│   └── Dockerfile               # Image Airflow personnalisée
│
├── data/
│   ├── raw/                     # Données extraites des trois sources
│   ├── processed/               # Données nettoyées et harmonisées
│   └── images/                  # Répertoire destiné aux images
│
├── docs/
│   └── schema_conceptuel.md     # Modèle conceptuel des données
│
├── notebooks/                   # Exploration des données
│
├── scripts/
│   └── fix_labels.py            # Script de correction des annotations
│
├── sql/
│   └── create_tables.sql        # Création des tables PostgreSQL
│
├── src/fake_news_etl/
│   ├── extraction/              # Extraction des données
│   ├── transformation/          # Nettoyage, harmonisation et fusion
│   ├── loading/                 # Chargement dans PostgreSQL
│   ├── utils/                   # Fonctions utilitaires
│   └── __init__.py
│
├── tests/                       # Tests automatisés (pytest)
│
├── .env                         # Variables sensibles (non versionnées)
├── .gitignore                   # Fichiers exclus de Git
├── .python-version              # Version Python
├── pyproject.toml               # Dépendances et configuration pytest
├── README.md                    # Documentation du projet
└── uv.lock                      # Verrouillage des dépendances
```

## Documentation

Le modèle conceptuel, les relations entre les données et l'association texte-image sont décrits dans [docs/schema_conceptuel.md](docs/schema_conceptuel.md).

## État du projet

- [x] Extraction des données
- [x] Transformation et harmonisation
- [x] Chargement PostgreSQL
- [x] Orchestration avec Apache Airflow
- [x] Vérifications SQL et tests automatisés (37 tests réussis)
- [ ] Monitoring
