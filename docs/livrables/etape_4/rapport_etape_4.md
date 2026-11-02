# Étape 4 — Orchestration du pipeline ETL avec Apache Airflow

## 1. Objectif

L'objectif de cette étape est d'automatiser le pipeline ETL du projet CheckIt.AI à l'aide d'Apache Airflow.

Le pipeline doit permettre d'extraire des données issues de plusieurs sources, de les transformer selon un schéma commun, puis de les charger dans une base de données relationnelle.

L'ensemble doit être exécutable dans un environnement local et permettre le suivi des différentes tâches.

## 2. Architecture technique

Les technologies utilisées sont :

* **Python** : développement des scripts ETL.
* **Apache Airflow** : orchestration et suivi des tâches.
* **Docker Compose** : exécution de l'environnement Airflow.
* **PostgreSQL** : stockage des données structurées.
* **Pytest** : tests automatisés.

Le pipeline est défini dans le fichier `airflow/dags/checkit_etl.py`.

## 3. Organisation du DAG

Le DAG `checkit_etl` comporte six tâches :

| Tâche                    | Fonction                                             |
| ------------------------ | ---------------------------------------------------- |
| `verifier_environnement` | Vérifier le démarrage de l'environnement d'exécution |
| `extraire_fakenewsnet`   | Extraire les données historiques FakeNewsNet         |
| `extraire_fakeddit`      | Extraire les données historiques Fakeddit            |
| `extraire_newsdata`      | Collecter les actualités via NewsData.io             |
| `transformer_donnees`    | Harmoniser et fusionner les données                  |
| `charger_donnees`        | Charger les données dans PostgreSQL                  |

Les trois tâches d'extraction sont indépendantes et peuvent s'exécuter en parallèle.

La transformation ne démarre qu'après leur réussite. Le chargement intervient ensuite.

Le DAG utilise des `PythonOperator` et réutilise les fonctions Python développées lors des étapes précédentes.

## 4. Stockage des données

Les données transformées sont chargées dans une base PostgreSQL dédiée au projet.

La table `articles` contient les informations structurées des articles, notamment :

* les identifiants ;
* la provenance ;
* le titre et le texte ;
* les URL des articles et des images ;
* les informations de publication ;
* les annotations disponibles ;
* les informations de modalité.

Les références aux images sont conservées dans les données structurées. Leur présence ne garantit pas que les fichiers image aient été téléchargés ou validés.

## 5. Résultats de l'exécution

Une exécution manuelle du DAG a été réalisée avec succès le **30 octobre 2026**.

Les six tâches ont terminé avec l'état `success`.

La base PostgreSQL contient **60 428 articles**, répartis comme suit :

| Source      | Nombre d'articles |
| ----------- | ----------------: |
| Fakeddit    |            59 342 |
| FakeNewsNet |             1 056 |
| NewsData.io |                30 |
| **Total**   |        **60 428** |

Les 30 articles NewsData.io correspondent aux données disponibles lors de la vérification finale.

## 6. Contrôles de qualité

Des requêtes SQL ont permis de vérifier les données chargées.

Résultats :

| Contrôle                        | Résultat |
| ------------------------------- | -------: |
| Nombre total d'articles         |   60 428 |
| Identifiants uniques            |   60 428 |
| Doublons d'identifiants         |        0 |
| Titres manquants                |        0 |
| Identifiants manquants          |        0 |
| Sources manquantes              |        0 |
| URL manquantes pour NewsData.io |        0 |

Les vérifications ont également confirmé l'absence de doublons de `source_id` et d'URL d'article parmi les 30 enregistrements NewsData.io.

Les annotations sont conservées selon leur provenance :

* **FakeNewsNet** : annotations binaires (`0` = réel, `1` = faux).
* **Fakeddit** : annotations issues d'une supervision faible.
* **NewsData.io** : articles non annotés.

Ces contrôles vérifient la cohérence des données, mais ne constituent pas une vérification indépendante de la véracité des articles.

## 7. Tests automatisés

Les tests Python sont exécutés avec la commande :

```bash
uv run pytest tests/ -v
```

Résultat de la dernière exécution :

**37 tests réussis.**

Les tests portent notamment sur les schémas, les identifiants, les annotations et la cohérence des transformations.

## 8. Configuration et sécurité

L'environnement repose sur Docker Compose.

Les informations de connexion à PostgreSQL et la clé API NewsData.io sont transmises à l'environnement d'exécution par des variables d'environnement.

Les fichiers contenant des secrets sont exclus du versionnement Git.

Cette organisation évite d'inscrire directement les identifiants dans le code source. Elle ne constitue toutefois pas, à elle seule, une validation complète de la sécurité de la base.

## 9. Preuves d'exécution

Les captures d'écran associées à cette étape présentent :

1. La structure du DAG dans l'interface Airflow.
2. L'exécution réussie des six tâches.
3. Les journaux des tâches d'extraction.
4. Les journaux de transformation.
5. Les journaux de chargement.
6. Les résultats des contrôles SQL dans PostgreSQL.

## 10. Conclusion

Cette étape a permis de mettre en place un pipeline ETL local orchestré avec Apache Airflow.

Les opérations d'extraction, de transformation et de chargement sont organisées en tâches distinctes et exécutées selon leurs dépendances.

L'exécution a abouti au chargement de 60 428 articles dans PostgreSQL, avec des contrôles de qualité satisfaisants.

Le pipeline constitue une base technique pour l'étape suivante, consacrée à l'évaluation et à la visualisation des performances.
