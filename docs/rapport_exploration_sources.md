# CheckIt.AI — Rapport d'exploration des sources de données

**Projet :** Extraction et traitement de données multimodales pour la détection de fausses informations  
**Livrable :** Rapport d'exploration des sources  
**Étape :** 1/5 — Identification, exploration et sélection des sources  
**Format :** Markdown  

---

## 1. Contexte et objectifs

### 1.1. Contexte du projet

CheckIt.AI est un projet visant à préparer des données multimodales en vue du développement d'un système de détection de fausses informations (*fake news*).

Les informations diffusées sur Internet peuvent prendre différentes formes : articles de presse, publications sur les réseaux sociaux, images, vidéos et métadonnées associées.

La détection de désinformation nécessite donc de disposer de données suffisamment représentatives, structurées et, lorsque cela est possible, accompagnées de labels de véracité fiables.

Dans ce contexte, le projet prévoit la construction d'un pipeline ETL (*Extract, Transform, Load*) permettant d'acquérir, de transformer et de stocker des données provenant de plusieurs sources.

### 1.2. Objectifs de l'exploration

Cette première étape consiste à identifier et à comparer différentes sources de données susceptibles d'alimenter le futur pipeline.

Les objectifs sont les suivants :

* Identifier au moins trois sources pertinentes pour la détection de fausses informations.
* Examiner les modalités disponibles : texte, image et éventuellement vidéo.
* Étudier les formats, langues, métadonnées et labels.
* Évaluer les possibilités techniques d'extraction.
* Identifier les limites liées à la qualité, à l'accessibilité et aux droits d'utilisation des données.
* Sélectionner les sources les plus adaptées à la suite du projet.  
   

---

## 2. Méthodologie d'exploration

### 2.1. Critères d'évaluation

Les sources ont été comparées selon six critères principaux.

| Critère          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| Pertinence       | Adéquation avec la détection de fausses informations           |
| Modalités        | Présence de texte, d'images ou de vidéos                       |
| Format et langue | Structure des données et langues disponibles                   |
| Labels           | Disponibilité, nature et fiabilité des annotations             |
| Extraction       | Méthode d'accès et possibilité d'automatisation                |
| Contraintes      | Données manquantes, limites techniques et droits d'utilisation |

Une attention particulière a été portée à la distinction entre l'accessibilité technique des contenus et les conditions autorisant leur collecte et leur réutilisation.

### 2.2. Démarche expérimentale

Quatre sources ont été étudiées :

1. FakeNewsNet, un dataset scientifique d'actualités annotées.
2. Fakeddit, un dataset multimodal de publications Reddit.
3. NewsData.io, une API d'actualités.
4. Franceinfo, à travers ses flux RSS.

L'exploration a été réalisée dans le notebook `notebooks/01_exploration_sources.ipynb`, à l'aide de Python.

Les investigations ont notamment porté sur :

* La lecture et l'inspection des données.
* L'identification des champs disponibles.
* Le comptage des observations et des labels.
* La présence et l'accessibilité des références vers les images.
* La disponibilité des contenus textuels.
* La faisabilité d'une extraction automatisée.
* L'examen des conditions d'utilisation.

Les résultats présentés correspondent aux fichiers et échantillons effectivement explorés. Ils ne constituent pas nécessairement une description exhaustive de l'ensemble des données proposées par chaque fournisseur.

---

## 3. Exploration des sources

### 3.1. FakeNewsNet

#### Présentation

FakeNewsNet est un jeu de données scientifique développé pour la recherche sur la détection de fausses informations.  

Il regroupe des références vers des actualités vérifiées et des informations complémentaires liées à leur diffusion.   

**Référence :** https://github.com/KaiDMML/FakeNewsNet  

#### Caractéristiques

| Caractéristique      | Description                                        |
| -------------------- | -------------------------------------------------- |
| Type                 | Dataset scientifique                               |
| Domaine              | Actualités et désinformation                       |
| Langue               | Principalement anglais                             |
| Format étudié        | CSV                                                |
| Modalité textuelle   | Titres et références vers les articles             |
| Images               | Non fournies directement dans les fichiers étudiés |
| Labels               | Fake / Real                                        |
| Actualisation        | Données historiques                                |
| Extraction envisagée | Téléchargement et import ponctuel des CSV          |

#### Résultats de l'exploration

L'analyse du fichier PolitiFact a porté sur **1 056 observations**, réparties comme suit :

| Label     |    Nombre |
| --------- | --------: |
| Fake      |       432 |
| Real      |       624 |
| **Total** | **1 056** |

Les annotations constituent un avantage important, puisqu'elles permettent de distinguer les actualités considérées comme vraies ou fausses dans le cadre du dataset.

En revanche, les fichiers étudiés ne contiennent pas directement l'intégralité des articles ni leurs images.

Un test sur cinq URL d'articles a montré que trois d'entre elles renvoyaient une erreur HTTP 404.

Cette observation illustre une difficulté de récupération des contenus originaux.

#### Qualité des labels

Les labels sont associés à des contenus issus de sources de vérification journalistique, notamment PolitiFact.

Ils sont donc plus directement liés à la véracité des informations que de simples catégories de publications sur les réseaux sociaux.

Cependant, leur qualité dépend du protocole de constitution du dataset, et leur présence ne garantit pas l'accessibilité des contenus multimodaux correspondants.

#### Méthode d'extraction proposée

L'extraction repose sur un **import ponctuel des fichiers CSV** mis à disposition par le projet.

Les traitements envisagés sont :

* Lecture des fichiers avec `pandas`.
* Vérification des colonnes et des types.
* Contrôle des valeurs manquantes.
* Normalisation des labels.
* Conservation des références vers les contenus originaux.
* Intégration dans une structure de données commune.

La récupération automatisée des articles et images provenant de sites tiers n'est pas retenue sans vérification de leurs conditions d'utilisation.

#### Limites

* Contenus textuels complets non disponibles directement.
* Images absentes des fichiers explorés.
* Certaines URL historiques sont devenues inaccessibles.
* Pas d'actualisation continue.
* Droits des contenus tiers à respecter.

**Bilan :** FakeNewsNet est pertinent comme source historique annotée, mais moins adapté à une acquisition multimodale complète.

---

### 3.2. Fakeddit

#### Présentation

Fakeddit est un dataset scientifique multimodal construit à partir de publications Reddit.

Il a été développé pour étudier la classification de contenus trompeurs en combinant des informations textuelles et visuelles.

**Référence :** https://github.com/entitize/Fakeddit

#### Caractéristiques

| Caractéristique      | Description                               |
| -------------------- | ----------------------------------------- |
| Type                 | Dataset scientifique                      |
| Domaine              | Publications Reddit et contenus trompeurs |
| Langue               | Principalement anglais                    |
| Format étudié        | TSV                                       |
| Modalités            | Texte et images                           |
| Images               | Références vers des fichiers visuels      |
| Labels               | Classifications à 2, 3 et 6 classes       |
| Actualisation        | Données historiques                       |
| Extraction envisagée | Téléchargement et import ponctuel des TSV |

#### Résultats de l'exploration

Le fichier analysé contient **59 342 publications**.

Les données comportent des informations textuelles, des métadonnées et des références vers des images.

Sur un échantillon de dix images testées, **huit étaient accessibles**.

Cette disponibilité est intéressante pour un projet multimodal, même si elle ne garantit pas que l'ensemble des images du dataset soit encore récupérable.

#### Qualité des labels

Fakeddit propose plusieurs niveaux de classification :

* Classification binaire.
* Classification en trois classes.
* Classification en six classes.

Ces annotations permettent d'étudier différents types de contenus trompeurs.

Cependant, elles reposent sur une supervision indirecte liée à la construction du dataset et aux catégories de publications.

Elles ne doivent donc pas être assimilées systématiquement à des verdicts de vérification journalistique.

Par ailleurs, une partie des publications concerne des contenus humoristiques, des montages ou des images détournées, plutôt que des articles d'actualité.

#### Méthode d'extraction proposée

L'extraction repose sur un **import ponctuel du fichier TSV**.

Les traitements envisagés comprennent :

* Chargement avec `pandas`.
* Sélection des colonnes utiles.
* Vérification des textes et métadonnées.
* Analyse des labels.
* Contrôle des références vers les images.
* Normalisation du format des observations.

Une récupération locale d'images pourra être envisagée uniquement dans le respect des droits applicables aux contenus concernés.

#### Limites

* Publications principalement anglophones.
* Données historiques non actualisées.
* Qualité des labels variable selon l'objectif de classification.
* Images parfois indisponibles.
* Contenus qui ne correspondent pas toujours à de véritables actualités.
* Droits de réutilisation des images à examiner.

**Bilan :** Fakeddit constitue une source complémentaire pertinente pour expérimenter le traitement de données multimodales annotées.

---

### 3.3. NewsData.io

#### Présentation

NewsData.io est un service proposant une API REST pour accéder à des actualités provenant de différentes sources de presse.

Il permet notamment de filtrer les publications selon la langue et d'obtenir des informations structurées au format JSON.

**Références :**

* https://newsdata.io/
* https://newsdata.io/documentation
* https://newsdata.io/terms

#### Caractéristiques

| Caractéristique      | Description                                   |
| -------------------- | --------------------------------------------- |
| Type                 | API REST                                      |
| Domaine              | Actualités générales                          |
| Langue               | Multilingue, dont français                    |
| Format               | JSON                                          |
| Modalité textuelle   | Titres, descriptions et métadonnées           |
| Images               | URL d'images selon les articles               |
| Vidéos               | Références éventuelles selon les publications |
| Labels               | Aucun label de véracité                       |
| Actualisation        | Publications récentes                         |
| Extraction envisagée | Requêtes API automatisées                     |

#### Résultats de l'exploration

Une requête sur des actualités en français a permis de récupérer **dix articles** dans l'échantillon étudié.

La réponse JSON contenait **28 champs**.

Parmi les dix articles :

* Neuf disposaient d'une URL d'image.
* Huit images étaient accessibles parmi les neuf URL testées.
* Les titres et descriptions étaient disponibles.
* Le contenu intégral des articles était réservé aux offres payantes.

L'API présente donc un intérêt pour la collecte régulière de métadonnées d'actualité, mais ne garantit pas l'accès à l'intégralité des textes.

#### Qualité des labels

NewsData.io ne fournit pas de labels indiquant si une information est vraie ou fausse.

Il n'est donc pas possible d'utiliser directement les publications collectées comme exemples supervisés pour entraîner un classificateur de véracité.

L'absence de label sera conservée explicitement dans les données, sans attribuer artificiellement une classe aux articles.

#### Méthode d'extraction proposée

L'extraction sera réalisée au moyen de **requêtes HTTP vers l'API officielle**, avec authentification par clé API.

Les traitements envisagés comprennent :

* Paramétrage des requêtes.
* Filtrage des publications en français.
* Récupération des réponses JSON.
* Vérification des statuts HTTP.
* Gestion des erreurs et des limites de requêtes.
* Extraction des champs utiles.
* Détection des doublons.
* Conservation des références vers les images.
* Stockage des données structurées.

La clé API sera conservée dans une variable d'environnement, sans être intégrée au code source.

NewsData.io sera la seule source faisant l'objet d'une **collecte automatisée récurrente**.

#### Conditions d'utilisation

L'accès s'effectue dans le cadre des conditions du service et des limites du forfait utilisé.

Les conditions de NewsData.io distinguent les données proposées par le service des contenus appartenant aux éditeurs tiers.

Les textes, images et vidéos provenant de ces éditeurs restent soumis à leurs droits respectifs.

L'utilisation de l'API ne constitue donc pas une autorisation générale de télécharger, redistribuer ou exploiter librement tous les contenus référencés.

Le pipeline devra respecter les restrictions du service, les obligations d'attribution et les droits des contenus tiers.

#### Limites

* Absence de labels de véracité.
* Contenu intégral indisponible avec le forfait gratuit.
* Quotas et restrictions de l'API.
* Présence variable des images.
* Droits de réutilisation des contenus tiers.

**Bilan :** NewsData.io constitue la source principale retenue pour la collecte automatisée de publications récentes.

---

### 3.4. Franceinfo — Flux RSS

#### Présentation

Franceinfo propose des flux RSS permettant de consulter des publications d'actualité.

Deux flux ont été explorés :

* Un flux général consacré aux principaux titres.
* Un flux consacré à la rubrique « Vrai ou Fake ».

**Référence :** https://www.franceinfo.fr/

#### Caractéristiques

| Caractéristique    | Description                                  |
| ------------------ | -------------------------------------------- |
| Type               | Flux RSS                                     |
| Domaine            | Actualités et vérification d'informations    |
| Langue             | Français                                     |
| Format             | XML, avec du HTML selon les champs           |
| Modalité textuelle | Titres, descriptions et parfois contenu HTML |
| Images             | Références selon les flux                    |
| Labels             | Aucun label vrai/faux directement structuré  |
| Actualisation      | Publications récentes                        |
| Extraction étudiée | Lecture et analyse des flux RSS              |

#### Résultats de l'exploration

L'exploration a porté sur **38 publications** :

| Flux         | Nombre d'articles |
| ------------ | ----------------: |
| Les titres   |                30 |
| Vrai ou Fake |                 8 |
| **Total**    |            **38** |

Le flux général contenait notamment des titres, descriptions, dates, liens et références vers des images.

Les 30 références d'images testées dans ce flux renvoyaient une réponse HTTP 200 et correspondaient à des fichiers JPEG.

Le flux « Vrai ou Fake » contenait huit publications avec du contenu HTML, représentant environ **306 à 1 638 mots par publication**.

Les articles de vérification présentaient des analyses journalistiques, mais aucun champ ne fournissait directement un verdict de classification standardisé.

#### Qualité des labels

Les publications de la rubrique « Vrai ou Fake » peuvent présenter un intérêt pour la recherche sur la vérification de l'information.

Cependant, elles ne constituent pas directement un dataset supervisé.

Les conclusions journalistiques peuvent être nuancées et nécessiteraient une interprétation supplémentaire pour produire des labels.

#### Méthode d'extraction étudiée

Les tests techniques ont permis d'examiner :

* La lecture des flux XML.
* L'extraction des titres et descriptions.
* La récupération des dates de publication.
* L'identification des liens et des références visuelles.
* L'analyse du contenu HTML présent dans certains champs.

Toutefois, cette faisabilité technique ne suffit pas à autoriser une collecte automatisée récurrente.

#### Conditions d'utilisation

Les conditions générales d'utilisation de Franceinfo comportent une section consacrée à l'interdiction de la fouille automatisée des données.

La section 13.2 prévoit notamment des restrictions concernant l'accès automatisé destiné à extraire, copier, réutiliser ou analyser les contenus, sauf autorisation expresse, préalable et écrite de France Télévisions.

Ces restrictions concernent notamment le scraping de textes, d'images, de vidéos et de métadonnées.

**Référence :** https://www.franceinfo.fr/cgu.html

#### Limites

* Absence de labels directement exploitables.
* Structure et richesse des données variables selon les flux.
* Restrictions concernant la collecte automatisée.
* Nécessité d'une clarification des droits pour une exploitation récurrente.

**Bilan :** Franceinfo est une source techniquement intéressante, mais n'est pas retenue pour le pipeline final en raison des restrictions d'utilisation identifiées.

---

## 4. Comparaison des sources

### 4.1. Tableau comparatif

| Critère              | FakeNewsNet                 | Fakeddit               | NewsData.io                                | Franceinfo RSS             |
| -------------------- | --------------------------- | ---------------------- | ------------------------------------------ | -------------------------- |
| Type                 | Dataset                     | Dataset                | API REST                                   | Flux RSS                   |
| Langue               | Anglais                     | Anglais                | Multilingue, dont français                 | Français                   |
| Format               | CSV                         | TSV                    | JSON                                       | XML / HTML                 |
| Texte                | Titres, références          | Titres, métadonnées    | Titres, descriptions                       | Titres, descriptions, HTML |
| Images               | Non fournies directement    | Références disponibles | URL selon les articles                     | Références selon le flux   |
| Vidéos               | Non étudiées                | Non étudiées           | Non étudiées                               | Non étudiées               |
| Labels               | Fake / Real                 | 2, 3 ou 6 classes      | Aucun                                      | Non structurés             |
| Nature des labels    | Vérification journalistique | Supervision indirecte  | Sans objet                                 | Vérification contextuelle  |
| Actualisation        | Historique                  | Historique             | Continue                                   | Continue                   |
| Méthode d'extraction | Import CSV                  | Import TSV             | API REST                                   | Lecture RSS                |
| Collecte récurrente  | Non                         | Non                    | Oui                                        | Non retenue                |
| Limite principale    | Contenus incomplets         | Labels indirects       | Absence de labels et texte intégral limité | Restrictions d'utilisation |

### 4.2. Analyse comparative

Les quatre sources répondent à des besoins différents.

**FakeNewsNet** présente l'avantage de proposer des labels de véracité liés à des actualités vérifiées. Toutefois, l'accès incomplet aux articles et aux images limite son intérêt pour une collecte multimodale complète.

**Fakeddit** propose des publications textuelles associées à des références visuelles et à plusieurs niveaux de classification. Il est particulièrement utile pour étudier la structure de données multimodales annotées, mais ses labels ne correspondent pas systématiquement à une vérification factuelle journalistique.

**NewsData.io** est la source la plus adaptée à une acquisition régulière de nouvelles publications. Son API fournit des données structurées et permet de filtrer les résultats en français. En revanche, les articles ne sont pas accompagnés de labels de véracité.

**Franceinfo RSS** présente des contenus français récents et des données textuelles parfois riches. Malgré sa faisabilité technique, les restrictions contractuelles identifiées empêchent de le retenir pour la collecte automatisée envisagée sans autorisation appropriée.

Cette comparaison montre qu'aucune source ne réunit à elle seule l'ensemble des caractéristiques recherchées : actualisation continue, données multimodales complètes, labels fiables et conditions de réutilisation adaptées.

Une stratégie combinant plusieurs sources est donc privilégiée.

---

## 5. Sélection des sources et justification

### 5.1. Sources retenues

À l'issue de l'exploration et après échange avec le mentor, trois sources sont retenues pour la suite du projet.

| Source             | Statut      | Rôle                                                             |
| ------------------ | ----------- | ---------------------------------------------------------------- |
| **NewsData.io**    | Retenue     | Collecte automatisée et récurrente d'actualités                  |
| **Fakeddit**       | Retenue     | Import ponctuel de données multimodales annotées                 |
| **FakeNewsNet**    | Retenue     | Import ponctuel d'actualités historiques annotées                |
| **Franceinfo RSS** | Non retenue | Source étudiée, écartée en raison des restrictions d'utilisation |

### 5.2. Justification de la stratégie

Le choix de ces trois sources repose sur leur complémentarité.

**NewsData.io** répond au besoin d'automatisation. Son API permet de récupérer régulièrement de nouvelles publications sans devoir développer un scraper HTML sur des sites de presse.

**Fakeddit** permet de disposer d'un ensemble historique de publications multimodales annotées, utile pour tester les traitements de données textuelles et visuelles.

**FakeNewsNet** complète cette sélection avec des exemples historiques associés à des labels de véracité issus de travaux de vérification journalistique.

Ces trois sources permettent ainsi de couvrir plusieurs formats d'entrée : JSON, TSV et CSV.

Elles présentent également différents niveaux de disponibilité des labels et des modalités, ce qui permettra de concevoir des transformations tenant compte de l'hétérogénéité des données.

### 5.3. Stratégie d'extraction

Deux modes d'extraction sont prévus.

- #### Extraction automatisée récurrente

**Source : NewsData.io**

Une collecte périodique sera mise en place via l'API REST.

Elle devra permettre de récupérer les nouvelles publications, de contrôler les réponses, de gérer les erreurs et de limiter les doublons.

La fréquence des collectes sera définie en fonction des besoins du projet et des quotas du service.

- #### Extraction ponctuelle

**Sources : Fakeddit et FakeNewsNet**

Les fichiers TSV et CSV seront importés à partir des ressources publiées par les projets scientifiques.

Ces extractions ne nécessitent pas de planification récurrente, puisque les fichiers retenus constituent des jeux de données historiques.

Les imports devront néanmoins être reproductibles et documentés.

### 5.4. Gestion des différences entre sources

Les données collectées n'auront pas toutes les mêmes caractéristiques.

Le futur traitement devra notamment prendre en compte :

* Des structures CSV, TSV et JSON différentes.
* Des textes de longueur variable.
* Des images absentes ou uniquement référencées par URL.
* Des labels utilisant des conventions différentes.
* Des publications avec ou sans annotation de véracité.
* Des dates et métadonnées potentiellement manquantes.

Les données conserveront un identifiant de provenance afin de distinguer leur source d'origine.

Les labels de Fakeddit et de FakeNewsNet ne seront pas considérés comme directement équivalents.

De même, les publications NewsData.io ne recevront aucun label de véracité artificiel.

---

## 6. Recommandations pour le pipeline ETL

### 6.1. Extraction

Le pipeline devra prévoir trois mécanismes d'acquisition :

| Source      | Méthode                | Fréquence  |
| ----------- | ---------------------- | ---------- |
| NewsData.io | Requêtes API REST      | Périodique |
| Fakeddit    | Lecture de fichier TSV | Ponctuelle |
| FakeNewsNet | Lecture de fichier CSV | Ponctuelle |

Les scripts devront être organisés en fonctions réutilisables et intégrer une gestion des erreurs.

### 6.2. Transformation

Une structure commune pourra être définie pour représenter les publications, tout en conservant les spécificités de chaque source.

Les champs envisagés sont :

| Champ          | Type envisagé       | Description                          |
| -------------- | ------------------- | ------------------------------------ |
| `source`       | Texte               | Nom de la source                     |
| `source_id`    | Texte               | Identifiant dans la source d'origine |
| `title`        | Texte nullable      | Titre de la publication              |
| `text`         | Texte nullable      | Texte ou description disponible      |
| `language`     | Texte nullable      | Langue                               |
| `published_at` | Date/heure nullable | Date de publication                  |
| `article_url`  | Texte nullable      | URL du contenu original              |
| `image_url`    | Texte nullable      | Référence vers une image             |
| `label`        | Texte nullable      | Annotation d'origine, si disponible  |
| `label_scheme` | Texte nullable      | Système de classification utilisé    |
| `collected_at` | Date/heure          | Date de collecte                     |

Ce schéma constitue une proposition initiale. Il devra être affiné lors de la conception du pipeline de transformation.

Les valeurs manquantes seront conservées lorsqu'aucune information fiable ne permet de les compléter.

### 6.3. Stockage

Les données transformées pourront être stockées dans une base relationnelle.

La structure devra permettre :

* L'identification de la provenance.
* La conservation des métadonnées utiles.
* La prévention des doublons.
* Le suivi des dates de collecte.
* La distinction entre données annotées et non annotées.
* L'évolution du schéma si de nouvelles modalités sont intégrées.

Le stockage physique des images devra être étudié séparément, selon les droits applicables et les exigences techniques des étapes suivantes.

### 6.4. Qualité et traçabilité

Les traitements devront intégrer des contrôles de qualité, notamment :

* Présence des champs indispensables.
* Cohérence des types.
* Détection des valeurs manquantes.
* Contrôle des doublons.
* Vérification des dates.
* Conservation des labels d'origine.
* Journalisation des extractions et transformations.

Les erreurs rencontrées devront être enregistrées afin de faciliter le diagnostic et la maintenance.

### 6.5. Contraintes d'utilisation

L'utilisation des sources retenues devra respecter leurs conditions de diffusion et les droits associés aux contenus tiers.

En particulier :

* L'accès à une URL d'image ne garantit pas un droit de réutilisation.
* Les contenus de presse restent soumis aux droits de leurs éditeurs.
* Les fichiers de recherche ne doivent pas être considérés comme automatiquement libres de toute restriction.
* Les clés API ne doivent pas être exposées.
* Les données provenant de différentes sources doivent conserver leur provenance.

Ces précautions guideront les choix d'implémentation.

---

## 7. Conclusion

Cette première étape du projet CheckIt.AI a permis d'explorer quatre sources de données présentant des caractéristiques complémentaires.

Les expérimentations ont mis en évidence plusieurs enjeux importants pour la construction d'un pipeline de données multimodales : diversité des formats, disponibilité variable des images, hétérogénéité des labels, qualité des références historiques et contraintes d'utilisation.

Trois sources ont finalement été retenues :

* **NewsData.io**, pour l'acquisition automatisée d'actualités récentes.
* **Fakeddit**, pour l'import ponctuel de publications multimodales annotées.
* **FakeNewsNet**, pour l'import ponctuel d'actualités historiques disposant de labels de véracité.

Franceinfo RSS a été écartée de la sélection opérationnelle en raison des restrictions identifiées concernant la collecte automatisée.

Cette stratégie permet de disposer de trois sources de données complémentaires, tout en limitant l'automatisation récurrente à la source qui bénéficie d'une API officielle et d'une actualisation continue.

La prochaine étape consistera à développer les mécanismes d'extraction correspondants, puis à mettre en place les traitements nécessaires à la normalisation, au contrôle qualité et au stockage des données.

**L'exploration des sources est ainsi terminée et la stratégie d'acquisition pour la suite du projet est définie.**

---

## 8. Références

### Sources de données

1. **FakeNewsNet — Dépôt officiel**
   https://github.com/KaiDMML/FakeNewsNet

2. **Fakeddit — Dépôt officiel**
   https://github.com/entitize/Fakeddit

3. **NewsData.io — Site officiel**
   https://newsdata.io/

4. **NewsData.io — Documentation API**
   https://newsdata.io/documentation

5. **Franceinfo — Site officiel**
   https://www.franceinfo.fr/

### Conditions d'utilisation

6. **NewsData.io — Terms and Conditions**
   https://newsdata.io/terms

7. **Franceinfo — Conditions générales d'utilisation**
   https://www.franceinfo.fr/cgu.html

### Documentation technique du projet

8. **Notebook d'exploration**
   `notebooks/01_exploration_sources.ipynb`

Ce notebook contient les tests techniques, observations et résultats détaillés ayant servi à établir la comparaison et la sélection des sources.

---

## 9. Auteur 

Bouzouita Hayette  
