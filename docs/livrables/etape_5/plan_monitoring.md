# CheckIt.AI — Plan de monitoring du pipeline ETL

## 1. Contexte et objectifs

Le projet CheckIt.AI repose sur un pipeline ETL permettant de collecter, transformer et stocker des données issues de trois sources : Fakeddit, FakeNewsNet et NewsData.io.

Le pipeline est orchestré avec Apache Airflow, exécuté dans un environnement Docker et utilise PostgreSQL pour le stockage des données.

Un tableau de bord développé avec Streamlit permet de visualiser les indicateurs de qualité des données et les performances des exécutions.

Le présent plan définit les modalités de surveillance du pipeline afin de :

* Détecter rapidement les erreurs d'exécution.
* Contrôler la qualité et l'intégrité des données.
* Surveiller les temps de traitement.
* Identifier les problèmes de disponibilité des sources.
* Définir les actions à entreprendre en cas d'anomalie.

Ce plan décrit les contrôles existants et propose des mesures complémentaires pour une éventuelle mise en production.

## 2. Indicateurs de performance (KPI)

### 2.1. Qualité des données

| Indicateur             | Description                                            | Valeur observée |
| ---------------------- | ------------------------------------------------------ | --------------- |
| Nombre d'articles      | Nombre total d'enregistrements stockés                 | 60 428          |
| Complétude des titres  | Pourcentage d'articles possédant un titre renseigné    | 100 %           |
| Doublons d'identifiant | Pourcentage d'identifiants dupliqués                   | 0 %             |
| Présence d'URL d'image | Pourcentage d'articles possédant une référence d'image | 98 %            |

La présence d'une URL d'image ne garantit pas que l'image soit accessible ou exploitable.

### 2.2. Performance du pipeline

| Indicateur              | Description                               | Valeur observée |
| ----------------------- | ----------------------------------------- | --------------- |
| Exécutions enregistrées | Nombre d'exécutions analysées             | 5               |
| Exécutions réussies     | Nombre d'exécutions terminées avec succès | 4               |
| Taux de réussite        | Proportion des exécutions réussies        | 80 %            |
| Durée moyenne           | Durée moyenne des exécutions réussies     | 22,3 secondes   |

Ces valeurs constituent un état initial du pipeline et peuvent évoluer avec les prochaines exécutions.

### 2.3. Durée des tâches

Les durées des six tâches Airflow sont également suivies :

1. Vérification de l'environnement.
2. Extraction depuis NewsData.io.
3. Extraction depuis FakeNewsNet.
4. Extraction depuis Fakeddit.
5. Transformation des données.
6. Chargement dans PostgreSQL.

La visualisation des durées permet d'identifier les étapes susceptibles de ralentir l'exécution globale.

### 2.4. Consommation des ressources Docker

Le coût technique du pipeline ETL est évalué à partir de la consommation des ressources informatiques mobilisées par les conteneurs Docker.

Les indicateurs suivants sont collectés à l'aide de la commande `docker stats --no-stream` et présentés dans le tableau de bord Streamlit.

| Indicateur              | Description                                               | Unité        |
| ----------------------- | --------------------------------------------------------- | ------------ |
| Utilisation CPU         | Charge processeur de chaque conteneur                     | %            |
| Mémoire utilisée        | Quantité de mémoire RAM consommée                         | MiB          |
| Utilisation mémoire     | Part de la limite mémoire du conteneur utilisée           | %            |
| Répartition par service | Consommation regroupée entre Airflow, PostgreSQL et Redis | % CPU et MiB |

Ces mesures permettent d'identifier les services les plus consommateurs de ressources et d'anticiper les besoins d'infrastructure.


## 3. Seuils d'alerte proposés

Les seuils suivants constituent des règles de surveillance proposées. Ils ne correspondent pas à des alertes automatiques déjà configurées.

| Indicateur                         | Seuil proposé                         | Niveau        | Action                                                     |
| ---------------------------------- | ------------------------------------- | ------------- | ---------------------------------------------------------- |
| Échec d'une exécution Airflow      | Au moins un nouvel échec              | Critique      | Examiner les logs et identifier la tâche concernée         |
| Complétude des titres              | Inférieure à 99 %                     | Avertissement | Vérifier l'extraction et les transformations               |
| Doublons d'identifiant             | Supérieurs à 0 %                      | Critique      | Contrôler les identifiants et le chargement                |
| Durée totale d'exécution           | Supérieure à 60 secondes              | Avertissement | Identifier les tâches les plus lentes                      |
| Disponibilité de NewsData.io       | Échec de l'appel API                  | Avertissement | Vérifier la connexion, les quotas et la réponse de l'API   |
| Chargement PostgreSQL              | Échec de la tâche de chargement       | Critique      | Vérifier la connexion et les erreurs SQL                   |
| Utilisation CPU d'un conteneur     | Supérieure à 150 % de façon prolongée | Avertissement | Identifier le service concerné et analyser les traitements |
| Utilisation mémoire d'un conteneur | Supérieure à 80 % de sa limite        | Avertissement | Examiner la consommation et les risques de saturation      |


Le pourcentage d'articles possédant une URL d'image est suivi à titre informatif. Un seuil global strict serait peu pertinent, car les trois sources ne proposent pas les mêmes informations multimodales.

Les seuils devront être ajustés à partir d'un historique d'exécutions plus représentatif.

## 4. Gestion des erreurs et des incidents

### 4.1. Détection

Les anomalies peuvent être identifiées à partir :

* Des statuts des tâches et des exécutions dans Airflow.
* Des journaux d'exécution du pipeline.
* Des indicateurs affichés dans le tableau de bord Streamlit.
* Des données stockées dans PostgreSQL.

### 4.2. Procédure de résolution

Lorsqu'une anomalie est détectée :

1. **Identifier l'incident** : relever l'heure, l'exécution et la tâche concernée.
2. **Consulter les logs** : rechercher le message d'erreur et son origine.
3. **Vérifier les dépendances** : contrôler les services Docker, la connexion PostgreSQL et les sources externes.
4. **Corriger le problème** : intervenir sur la configuration, la connexion ou le traitement concerné.
5. **Relancer le pipeline** : effectuer une nouvelle exécution lorsque la correction est appliquée.
6. **Vérifier le résultat** : contrôler les statuts Airflow et les indicateurs de qualité.
7. **Documenter l'incident** : conserver une trace de la cause et de la solution.

### 4.3. Exemples d'incidents

**Incident A — API NewsData.io indisponible**

* Symptôme : échec de la tâche d'extraction.
* Causes possibles : problème réseau, quota atteint ou indisponibilité de l'API.
* Réponse : consulter les logs, vérifier la réponse de l'API et relancer l'extraction lorsque le service est disponible.

**Incident B — Erreur de connexion PostgreSQL**

* Symptôme : échec du chargement ou impossibilité de consulter certains KPI.
* Causes possibles : service arrêté, configuration incorrecte ou problème d'authentification.
* Réponse : vérifier l'état du conteneur PostgreSQL, les paramètres de connexion et les logs.

**Incident C — Données dupliquées**

* Symptôme : augmentation du taux de doublons d'identifiant.
* Causes possibles : problème de génération des identifiants ou chargement incorrect.
* Réponse : analyser les données concernées, contrôler la logique de chargement et corriger la cause avant une nouvelle exécution.

## 5. Fréquence de surveillance

Le projet est actuellement exploité dans un environnement local de développement.

La surveillance repose sur les consultations manuelles d'Airflow, de Streamlit et des journaux d'exécution.

Pour une exploitation régulière, les fréquences suivantes sont proposées :

| Contrôle                            | Fréquence recommandée         |
| ----------------------------------- | ----------------------------- |
| Statut des exécutions Airflow       | Après chaque exécution        |
| Logs des tâches en échec            | Immédiatement après détection |
| Qualité des données                 | Après chaque chargement       |
| Durée des tâches                    | Après chaque exécution        |
| Répartition des articles par source | Une fois par semaine          |
| Revue des incidents                 | Une fois par mois             |
| Consommation CPU et mémoire Docker  |	Après chaque exécution        |

Ces fréquences devront être adaptées à la périodicité réelle du pipeline.

## 6. Évolutions envisagées

Le dispositif actuel comprend :

* L'orchestration des traitements avec Airflow.
* La journalisation des exécutions.
* Le stockage des données dans PostgreSQL.
* Un tableau de bord Streamlit présentant les KPI.

Pour une future mise en production, plusieurs améliorations sont envisageables :

* Configurer des notifications automatiques lors des échecs Airflow.
* Historiser les KPI de qualité pour suivre leur évolution.
* Ajouter une surveillance de la disponibilité des services.
* Mettre en place des alertes sur les durées d'exécution anormales.
* Vérifier l'accessibilité réelle des images référencées.
* Mesurer la consommation de ressources et les coûts d'exploitation.
* Historiser les mesures CPU et mémoire pendant les exécutions du pipeline afin de mieux évaluer les pics de consommation, de comparer les traitements et d'estimer les besoins d'infrastructure.


## 7. Conclusion

Le monitoring de CheckIt.AI permet de suivre deux dimensions essentielles du pipeline ETL : la qualité des données et la performance des traitements.

Le tableau de bord Streamlit fournit une visualisation des principaux indicateurs, tandis qu'Airflow et ses journaux permettent d'analyser les exécutions et les erreurs.

Le plan de monitoring formalise les contrôles à effectuer, les seuils d'alerte proposés et les procédures de gestion des incidents.

Il constitue une base pour fiabiliser le pipeline et préparer son éventuelle exploitation en production.
