---
title: "Les Français face à l'information"
subtitle: "Projet d'études M1 Big Data & IA — Rendu groupe"
author: "Baptiste, Lucas, Gérard"
date: "Juin 2026"
lang: fr
toc: true
toc-depth: 2
geometry: margin=2cm
---

\newpage

# 1. Présentation de l'entreprise et de l'équipe projet

## 1.1 Contexte de la commande

Ce projet est porté dans le cadre de l'**Open Data University**, plateforme nationale qui met à disposition des étudiants des défis de data science à partir de jeux de données publics.
Le défi auquel notre équipe a répondu, *Les Françaises et les Français face à l'information — Saison 3*, est proposé en partenariat avec :

- **L'INA** (Institut national de l'audiovisuel) — fournisseur principal des données (Baromètre JT, projet Gender Equality Monitor)
- **L'ARCOM** — autorité de régulation de la communication audiovisuelle, dont les rapports annuels ont inspiré la problématique
- **défis.data.gouv.fr** — la plateforme qui héberge le défi

Le commanditaire fictif que nous adressons est constitué de **trois personae** :

| Persona | Attente |
|---|---|
| **Citoyen** | Prendre conscience de ce qui est diffusé et par qui — outil pédagogique grand public |
| **Association de défense de l'égalité H/F** | Disposer de chiffres robustes pour appuyer un plaidoyer |
| **Pouvoirs publics / chaînes** | Données fiables pour orienter les politiques de représentation |

Le cadre méthodologique impose des **données ouvertes** et le respect des CGU INA.
Le projet doit pouvoir être réutilisé et publié sur `data.gouv.fr`.

## 1.2 Équipe projet

Le projet est porté par une équipe de trois étudiants en M1 Big Data & IA à Sup de Vinci :

| Nom | Prénom | Rôle | Responsabilités principales |
|---|---|---|---|
| [TODO Nom Lucas] | Lucas | Data / Frontend | EDA initial, pipeline Silver/Gold, analyses avancées, dashboard Streamlit |
| [TODO Nom Baptiste] | Baptiste | Lead Backend | Schéma PostgreSQL, modèles Django ORM, migration, API REST |
| [TODO Nom Gérard] | Gérard | Data / QA | Pipeline Bronze, validation pandera, tests, documentation utilisateur |

> *Les responsabilités sont indicatives : la collaboration est transversale (relectures croisées, pair-programming sur phases sensibles, décisions d'architecture collégiales).*

\newpage

# 2. Analyse de la problématique et solution proposée

## 2.1 Constat de départ

Trois faits ont structuré notre lecture du sujet :

1. **L'ARCOM (2023)** établit que les femmes ne représentent que **34 % du temps de parole** à la télévision et à la radio.
2. **Le journal Le Monde (2013)** : *« En dix ans, le nombre de faits divers dans les JT a augmenté de 73 %. »*
3. **L'ARCOM** rapporte par ailleurs que **58 % des Français** s'informent via les réseaux sociaux ou plateformes vidéo au moins une fois par jour, et que **11 % le font exclusivement**.

Ces trois faits posent une question simple :
**Que regardent les Français à la télévision, par qui, et comment cela a-t-il évolué sur vingt ans ?**

## 2.2 Reformulation en problématique projet

Le défi propose trois axes :

1. L'évolution des **thèmes diffusés** à la télévision et à la radio française
2. La **représentation des femmes** au sein des émissions diffusées
3. L'évolution du **rapport des Français à l'information** et à l'audiovisuel

Notre équipe a choisi de couvrir en profondeur les **axes 1 et 2**, et de croiser explicitement les deux pour produire l'apport original du projet :

> **Existe-t-il un lien entre la composition thématique d'une chaîne et la place qu'elle donne aux femmes à l'antenne ?**

L'axe 3 (rapport des Français à l'info) est laissé hors scope pour ne pas diluer la profondeur des deux premiers, conformément à la liberté laissée par le cahier des charges de l'Open Data University.

## 2.3 Cible utilisateur du livrable

Le livrable principal est un **tableau de bord interactif** consultable :

- par un **citoyen** sans formation statistique (explications dépliables, langage accessible)
- par une **association** qui souhaite extraire un chiffre précis (filtres, classements, export CSV)
- par un **journaliste / chercheur** qui veut comparer des chaînes ou des périodes (vue clustering, ruptures temporelles)

Trois personae, **une interface unique** : c'est notre contrainte UX centrale.

## 2.4 Introduction à la solution proposée

Nous avons construit un **pipeline de bout en bout** organisé en quatre couches :

1. **Ingestion brute (Bronze)** — lecture des CSV INA et génération automatique de rapports qualité
2. **Nettoyage (Silver)** — typage, parsing, validation par contrats pandera, déduplication tracée
3. **Tables analytiques (Gold)** — 6 tables agrégées prêtes à l'emploi
4. **Consommation** — dashboard Streamlit + 3 analyses avancées (ruptures, clustering, corrélations)

Le **MVP livré** est le dashboard Streamlit. Un backend PostgreSQL + Django est en cours de finalisation pour permettre l'exposition des données via API REST.

Un schéma global est fourni en section 5 (solution technique).

\newpage

# 3. Organisation, planification et méthodologie

## 3.1 Méthodologie

Notre équipe a appliqué une **méthodologie agile hybride** :

- **Sprints** de 2 semaines, démos courtes en fin de sprint
- **Rétrospectives** à chaque livraison majeure (Bronze, Silver, Gold, MVP dashboard)
- **Code review** systématique : chaque pull request relue par au moins un autre membre
- **Conventions de commit** : `feat:`, `fix:`, `docs:`, `refactor:`
- **Branches Git** : `main` protégée, `feat/xxx` pour les développements

Les outils utilisés :

| Outil | Usage |
|---|---|
| **GitHub** | Versioning, pull requests, issues |
| **Teams / Discord** | Communication, pair-programming |
| **VS Code + Cursor** | IDE principal |
| **Python 3.13** | Langage |
| **Makefile** | Orchestration locale (install, pipeline, dashboard) |

## 3.2 Planning

Le projet s'étale sur **5 mois** (février → juin 2026).
Voir le diagramme Gantt complet dans `00_planning.md` ; résumé :

| Phase | Mois | Livraison |
|---|---|---|
| Cadrage + EDA | Février | Diagnostic + choix techno |
| Pipeline data | Mars | Bronze + Silver + Gold |
| Backend | Avril | Schéma BDD + migration + modèles Django |
| Analyses avancées | Avril–Mai | Ruptures + clustering + corrélations |
| Frontend | Mai–Juin | Dashboard Streamlit 5 pages |
| Livrables | Juin | Documents techniques + vidéo MVP |

## 3.3 Répartition des responsabilités

Voir `00_planning.md` § *Rôles dans l'équipe*. La répartition est synthétisée dans le diagramme suivant :

```
Lucas    --> Pipeline Silver/Gold + Analyses avancées + Dashboard
Baptiste --> Schéma PG + Django ORM + Migration + API REST
Gérard   --> Pipeline Bronze + Validation pandera + Tests + Doc utilisateur
```

## 3.4 Gestion des risques

Voir `00_planning.md` § *Gestion des risques* pour la matrice détaillée. Les risques majeurs identifiés et leurs mitigations :

- **Backend Django incomplet** → dashboard Streamlit conçu pour être autonome (pas de dépendance API).
- **Données radio sans informations thématiques** → périmètre TV pour les analyses thématiques, radio limitée à la parité (ce qui correspond aux données disponibles).
- **Pandera bloque en cours de pipeline** → rapports qualité Bronze générés en amont pour anticiper les schémas problématiques.

## 3.5 Gestion des coûts

Le projet **M1** n'impose pas une comptabilité analytique détaillée. Pour information :

- **Stack** : 100 % open source (Python, Streamlit, PostgreSQL, scikit-learn, ruptures, pandera, Plotly)
- **Hébergement développement** : machines personnelles
- **Hébergement cible** (déploiement futur) :
  - Streamlit Community Cloud — **gratuit**
  - PostgreSQL via Railway / Supabase — **0 à 25 €/mois** selon volume
- **Coût humain estimé** : 3 personnes × ~120 h ≈ 360 h-personne ≈ **18 000 € HT** au tarif jour-homme moyen Junior Data (350 €/j)

\newpage

# 4. Présentation de la solution technique

## 4.1 Architecture globale

Le projet est structuré en **quatre couches** suivant le pattern *médaillon* popularisé par Databricks :

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCES   →  BRONZE   →   SILVER   →   GOLD   →   APPS    │
│  (CSV INA)    (brut)       (propre)     (analytique)        │
└─────────────────────────────────────────────────────────────┘
```

Le diagramme détaillé avec les flux est fourni dans `06_diagrammes.md` § 1.

### 4.1.1 Pourquoi le pattern médaillon

- **Séparation des responsabilités** : chaque couche a un contrat clair (Bronze conserve la source, Silver garantit la qualité, Gold agrège pour la consommation)
- **Reproductibilité** : on peut rejouer n'importe quelle étape sans repartir des CSV
- **Auditabilité** : on conserve la trace de la source à la table finale
- **Évolutivité** : ajouter un dataset n'impacte que les couches en amont des tables Gold concernées

### 4.1.2 Choix de stack

| Composant | Choix | Justification |
|---|---|---|
| Langage | **Python 3.13** | Standard data, expertise interne, écosystème complet |
| DataFrames | **pandas** | Volume modeste (268 K lignes), pas besoin de Spark/Dask |
| Validation | **pandera** | Contrats de schéma déclaratifs, intégration native pandas |
| ML / stats | **scikit-learn** + **ruptures** | ACP, k-means, PELT — bibliothèques standards du domaine |
| Stockage analytique | **CSV** (Silver/Gold) | Suffisant pour le volume, lisible humainement, portable |
| Stockage relationnel | **PostgreSQL** | Norme industrielle, indexation, FK, vues matérialisées |
| ORM | **Django** | API REST simple à monter, admin natif, mature |
| Frontend | **Streamlit** | Cycle développement court, idéal pour MVP, support Plotly natif |
| Visualisation | **Plotly Express** | Interactivité native, export, hover personnalisé |

## 4.2 Sources de données

| Dataset | Volumétrie | Période | Apport |
|---|---|---|---|
| `ina-barometre-jt` | 268 K lignes | 2000-2020 | Thèmes JT quotidiens, 5 chaînes, 14 rubriques |
| `20190308-stats` | ~6 K lignes | 1995-2018 | Temps de parole H/F par date/heure |
| `20190308-years` | 701 lignes | 1995-2018 | Agrégats annuels parité |
| `20190308-hourstatall` | 11 K lignes | 1995-2018 | Parole par tranche horaire (prime time) |
| `20190308-radio-years` | ~150 lignes | 1995-2018 | Parité radio |
| `20190308-tv-years` | ~300 lignes | 1995-2018 | Parité TV |
| `evenements_france` (manuel) | 25 lignes | 2000-2020 | Événements historiques de référence |

## 4.3 Détail des couches

### 4.3.1 Bronze — Ingestion brute

- Lecture des CSV en `latin-1` (encodage source INA)
- Sauvegarde à l'identique dans `data/bronze/`
- Génération d'un **rapport qualité** par dataset : nb lignes, nulls par colonne, types détectés, doublons potentiels
- Logs structurés dans `logs/pipeline.log`

### 4.3.2 Silver — Données propres

- **Typage strict** (`pd.to_datetime`, `astype(int)`, etc.)
- **Validation pandera** : les 6 tables Silver (`ina_jt`, `years`, `stats`, `hourstatall`, `radio_years`, `tv_years`) sont chacune validées contre un schéma déclaratif défini dans `pipeline_schemas.py`
  - Contrôle des types (avec `coerce=True` pour absorber les variantes pandas object vs StringDtype pyarrow)
  - Contrôle des bornes (taux ∈ [0, 100], années ∈ [1995, 2020], etc.)
  - Contrôle des valeurs autorisées (`media_type ∈ {'tv', 'radio'}`, `chaine ∈ {'TF1', 'France 2', ...}`)
  - Mode warning par défaut + mode strict opt-in via `PIPELINE_STRICT=1`
- **Déduplication** tracée (compteur logué)
- **Enrichissement temporel** : `annee`, `mois`, `jour_semaine`, `duree_totale_min`, `duree_moyenne_par_sujet`

### 4.3.3 Gold — 6 tables analytiques

| Table | Grain | Usage métier |
|---|---|---|
| `tv_theme_parite` | (année, chaîne) 2010-2019 | Croise parts de rubriques × taux d'expression des femmes |
| `parite_unifiee` | (media_type, média, année) | Format long pour visualisation TV + radio |
| `stats_prime_time` | (année, media_type, is_prime_time) | Évolution parité prime time vs hors prime time |
| `themes_evenements` | (événement, rubrique) | Delta % durée médiatique avant/pendant un fait historique |
| `saisonnalite` | (mois, rubrique) | Indice de saisonnalité sur 20 ans |
| `parite_ranking` | (année, média, media_type) | Classement annuel par parité + rang/quartile |

Les 6 tables Gold sont elles aussi validées chacune par un schéma pandera (`pipeline_schemas.py` § Gold).

À l'exécution, le pipeline log une ligne `[schema] X ✓` ou `✗` par table.
Sortie type d'une exécution réussie : **12 lignes ✓** consécutives dans `logs/pipeline.log`.

## 4.4 Analyses avancées (IA / Data Science)

### 4.4.1 Détection de ruptures temporelles (PELT)

- **Algorithme** : PELT (*Pruned Exact Linear Time*) implémenté dans `ruptures`
- **Hypothèse** : la moyenne mensuelle d'une rubrique change brutalement à certains moments (COVID, Macron 2017, etc.) — on cherche ces points
- **Modèle** : `model="l2"` (changement de moyenne), pénalité ajustée empiriquement
- **Sorties** : `analyses/outputs/ruptures_points.csv` + graphes PNG par rubrique
- **Trouvailles** : COVID 2020 sur Santé, attentats 2015 sur International, élections 2017 sur Politique France

### 4.4.2 Clustering ACP + k-means

- **Étape 1 — ACP** : on réduit le profil thématique d'une chaîne (14 dimensions = 14 parts de rubriques) en 2 composantes principales
- **Étape 2 — k-means** : on regroupe les points (chaîne × année) en **k=3 clusters**
- **Choix de k=3** : méthode du coude + interprétabilité (au-delà de 3, les groupes deviennent difficiles à étiqueter)
- **Sorties** : `analyses/outputs/clusters_chaines.csv` + `clusters_centroides.csv`
- **Trois archétypes identifiés** :
  - **Cluster Généralistes grand public** — M6, TF1, France 3 dominantes en Société + Faits divers
  - **Cluster International** — Arte, dominant en International + Culture
  - **Cluster Newsrooms politiques** — France 2, dominant en Politique France + Économie

### 4.4.3 Corrélations Pearson thèmes × parité

- Matrice complète des **corrélations de Pearson** entre chaque part de rubrique et le taux d'expression des femmes
- **Test de significativité** : p-value pour chaque corrélation
- **Sorties** : `analyses/outputs/correlation_themes_parite.csv` + heatmap
- **Trouvailles centrales** :
  - **+0,58 Faits divers ↔ Parité** (significatif p < 0,001)
  - **+0,57 Sciences et techniques ↔ Parité**
  - **−0,60 International ↔ Parité**
  - **−0,52 Économie ↔ Parité**

## 4.5 Frontend — Dashboard Streamlit

### 4.5.1 Architecture

- **5 pages** accessibles depuis une sidebar de navigation :
  1. 🏠 **Accueil** — pitch, KPI, 3 trouvailles
  2. 📊 **Agenda médiatique** — volumes, thèmes, saisonnalité, événements (tabs internes)
  3. 👩 **Parité H/F** — évolution, classement, prime time (tabs internes)
  4. 🔀 **Thèmes × Parité** — scatter par rubrique + matrice (cœur du projet)
  5. 🔬 **Analyses avancées** — clustering ACP + ruptures PELT

### 4.5.2 Accessibilité non-techniciens

- **11 explications dépliables** sous chaque graphique majeur, sans jargon statistique (« indicateur de lien », pas « corrélation de Pearson »)
- Exemples concrets cités (« le 11 septembre 2001 → International +400 % »)
- Vocabulaire imagé : « vont ensemble », « s'opposent », « plus on monte »

### 4.5.3 Stack frontend

- **Streamlit 1.57** + **streamlit-extras** (chart_container, row, metric_cards, bottom_container)
- **Plotly Express** + **Plotly Graph Objects** (template custom pour cohérence visuelle)
- Configuration thème dans `.streamlit/config.toml` (mode clair forcé, palette indigo)
- **Cache** : `@st.cache_data` pour les chargements CSV (idempotent)

### 4.5.4 Fonctionnalités UX

- Filtre de **période global** dans la sidebar (presets : Années 2000, 2010, COVID, personnalisé)
- **Sélecteur de média** unifié (TV / Radio / Comparer) sur la page parité
- **chart_container** : chaque graphe wrappé en onglets Chart / Dataframe / Export
- **Annotations contextuelles** sur les graphes (ligne verticale COVID sur Santé, élections sur Politique France)
- **Empty states** propres quand un filtre vide les données

## 4.6 Backend — PostgreSQL + Django

### 4.6.1 Schéma

5 tables normalisées 3NF :

```
channels (5)     themes (14)
   |                |
   +----> daily_stats <----+
         (268 K lignes)

yearly_gender (701)    hourly_stats (11 K)
```

Voir `06_diagrammes.md` § 3 pour le diagramme ER.

### 4.6.2 Implémentation

- **`backend/schema_postgresql.sql`** — DDL complet + index + contraintes
- **`backend/load_gold_to_postgres.py`** — chargement des tables Gold dans PostgreSQL (batch 1000 lignes)
- **`backend/django_models.py`** — modèles ORM avec validators, properties calculées, managers
- **API REST** — endpoints `/api/channels/`, `/api/themes/`, `/api/daily-stats/`, `/api/analytics/` (en cours)

### 4.6.3 Statut

Le backend est **livré comme module optionnel**. Le MVP livré (dashboard Streamlit) consomme directement les tables Gold en CSV, sans dépendance à PostgreSQL. Le backend permettra à terme :

- d'exposer les données via API à des clients tiers
- de gérer des utilisateurs et des permissions
- de migrer vers un frontend React/Chart.js si l'évolution du projet l'exige

## 4.7 Qualité, tests, reproductibilité

- **Validation pandera** sur les 12 tables Silver + Gold (6 Silver + 6 Gold) — mode warning par défaut, mode bloquant activable via la variable d'environnement `PIPELINE_STRICT=1` pour la CI
- **Logs structurés** dans `logs/pipeline.log` avec rapports qualité par dataset
- **Reproductibilité** : `make install && make pipeline && make analyses && make dashboard` reconstruit tout depuis zéro en quelques minutes
- **Encodage** : `latin-1` forcé sur les sources INA (problème détecté en EDA)

## 4.8 Trouvailles et apport pour les personae

Trois résultats actionnables identifiés :

1. **−0,60 entre International et parité H/F** : les chaînes très tournées vers l'international donnent moins la parole aux femmes. → *Argument associatif* : un quota thématique seul ne règle pas la parité, il faut des quotas croisés.
2. **+0,58 entre Faits divers / Société et parité** : les rubriques de proximité sont les plus inclusives. → *Argument citoyen* : les JT « grand public » ne sont pas forcément les moins représentatifs.
3. **3 archétypes éditoriaux** détectés automatiquement (généralistes / international / politiques). → *Argument régulateur* : une chaîne a un ADN identifiable, qui peut servir de référence dans des engagements pluriannuels.

\newpage

# 5. Conclusion

Le projet a permis à l'équipe de mobiliser de manière transversale les compétences acquises en formation :

- **Cadrage fonctionnel** (analyse du sujet, choix des axes traités)
- **Architecture data** (pipeline médaillon, contrats pandera)
- **Modélisation BDD** (3NF, PostgreSQL, Django ORM)
- **Data science** (ACP, k-means, ruptures PELT, Pearson)
- **Visualisation et UX** (Streamlit + Plotly, accessibilité grand public)
- **Posture professionnelle** (méthodologie agile, code review, communication structurée)

Le MVP livré — **un dashboard de 5 pages exploitable par un citoyen comme par un journaliste** — répond à la problématique posée par le défi tout en posant une question originale (lien thèmes ↔ parité) qui n'était pas explicitement attendue.

Les perspectives d'évolution (API REST, déploiement cloud, publication data.gouv.fr, bonus inaSpeechSegmenter) sont documentées et constituent des suites naturelles à un éventuel approfondissement.
