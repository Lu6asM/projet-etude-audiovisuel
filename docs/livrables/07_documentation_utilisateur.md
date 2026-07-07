---
title: "Documentation utilisateur et développeur"
subtitle: "Les Français face à l'information"
date: "Juin 2026"
lang: fr
toc: true
toc-depth: 3
geometry: margin=2cm
---

\newpage

# 1. Prérequis

| Outil | Version minimale | Vérifier avec |
|---|---|---|
| Python | 3.10+ (testé sur 3.13) | `python --version` |
| pip | 23+ | `pip --version` |
| Git | 2.30+ | `git --version` |
| PostgreSQL *(optionnel)* | 15+ | `psql --version` |

> Le projet fonctionne intégralement **sans PostgreSQL** : le dashboard consomme les CSV Gold directement. PostgreSQL n'est nécessaire que pour la couche API REST en cours de finalisation.

## Plateformes testées

- ✅ Windows 11 (Python 3.13, PowerShell)
- ✅ macOS (Python 3.11)
- ✅ Linux Ubuntu 22.04 (Python 3.12)

---

# 2. Installation

## 2.1 Clone du dépôt

```bash
git clone <url-du-repo>
cd "Projet d'étude"
```

## 2.2 Environnement virtuel (recommandé)

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Git Bash
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

## 2.3 Installation des dépendances

```bash
make install
# équivalent : pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :

```
pandas>=2.2.0
numpy>=1.26.0
pandera>=0.19.0
scikit-learn>=1.4.0
ruptures>=1.1.9
matplotlib>=3.8.0
seaborn>=0.13.0
streamlit>=1.32.0
streamlit-extras>=0.4.0
plotly>=5.19.0
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.9
```

---

# 3. Lancement rapide

```bash
make pipeline    # Bronze → Silver → Gold (~30 sec)
make analyses    # Ruptures + clustering + corrélations (~20 sec)
make dashboard   # Streamlit sur http://localhost:8501
```

## Sur Windows sans `make`

```powershell
python pipeline.py
python analyses/ruptures_detection.py
python analyses/clustering_chaines.py
python analyses/correlation_themes_parite.py
python -m streamlit run dashboard/app.py
```

---

# 4. Architecture des dossiers

```
Projet d'étude/
├── pipeline.py                Pipeline Bronze → Silver → Gold
├── pipeline_schemas.py        Contrats pandera
├── requirements.txt
├── Makefile
├── data/
│   ├── raw/                   CSV sources INA
│   ├── bronze/                Ingestion brute + rapports qualité
│   ├── silver/                Données nettoyées, typées
│   └── gold/                  6 tables analytiques
├── analyses/
│   ├── ruptures_detection.py
│   ├── clustering_chaines.py
│   ├── correlation_themes_parite.py
│   └── outputs/               PNG + CSV de sortie
├── dashboard/
│   ├── app.py                 Streamlit 5 pages
│   └── .streamlit/config.toml Thème
├── docs/
│   └── livrables/             Rendus Sup de Vinci
└── logs/                      pipeline.log
```

---

# 5. Le dashboard

## 5.1 Navigation

Le dashboard se découpe en **5 pages** accessibles depuis la sidebar gauche.

### Page 1 : 🏠 Accueil

- Pitch du projet
- 4 KPI globaux : sujets JT, heures, médias, événements
- 3 trouvailles majeures avec corrélations chiffrées
- Sources et méthodologie dépliable

### Page 2 : 📊 Agenda médiatique

Tabs internes :

- **Volumes** : nombre de sujets par chaîne et par an
- **Thèmes** : évolution des rubriques en heures ou en %
- **Saisonnalité** : heatmap mois × rubrique
- **Événements** : impact des faits historiques sur les rubriques

### Page 3 : 👩 Parité H/F

Sélecteur de média : **📺 TV / 📻 Radio / ⚖️ Comparer**

Tabs internes :

- **Évolution** : taux de parole féminin par média
- **Classement** : barchart annuel + trajectoire d'un média
- **Prime time** : comparaison prime time vs hors prime time

### Page 4 : 🔀 Thèmes × Parité (cœur du projet)

Tabs internes :

- **Scatter par rubrique** : nuage de points + ligne de régression
- **Matrice complète** : heatmap toutes corrélations

### Page 5 : 🔬 Analyses avancées

Tabs internes :

- **Clustering chaînes** : projection ACP + trajectoires d'une chaîne
- **Ruptures temporelles** : série mensuelle d'une rubrique + diamants rouges sur les ruptures

## 5.2 Filtres globaux (sidebar)

- **Période** : presets (Tout, Années 2000, Années 2010, COVID, Personnalisé)
- Le filtre s'applique aux graphes temporels de toutes les pages

## 5.3 Composants natifs

Chaque graphe majeur est wrappé dans un `chart_container` qui propose trois onglets natifs :

- **Chart** : le graphique
- **Dataframe** : tableau brut sous-jacent
- **Export** : téléchargement CSV / Parquet / JSON

## 5.4 Explications « Comment lire ce graphique ? »

Sous chaque graphe principal se trouve un dépliant rédigé pour un **public non technicien**, avec :

- une explication de la métaphore visuelle (axes, couleurs, formes)
- un exemple concret (« le 11 septembre 2001 → International +400 % »)
- pas de jargon statistique non défini

---

# 6. Le pipeline data

## 6.1 Bronze (ingestion brute)

- Lecture des CSV en `encoding="latin-1"` (encodage source INA)
- Sauvegarde à l'identique dans `data/bronze/`
- Rapport qualité par dataset : nb lignes, nulls par colonne, types, doublons

## 6.2 Silver (nettoyage)

- Typage strict
- **Validation pandera** : chaque table Silver (6) et Gold (6) contrôlée contre un schéma déclaratif
- Mode warning par défaut (log uniquement) ; mode bloquant via `PIPELINE_STRICT=1` en variable d'environnement (pour CI)
  - Types
  - Bornes
  - Valeurs autorisées
- Déduplication tracée
- Enrichissement temporel (année, mois, jour de la semaine)

## 6.3 Gold (analytique)

6 tables prêtes à la consommation. Détail complet dans `02_rendu_groupe.md` § 4.3.3.

## 6.4 Logs

Tous les logs structurés vont dans `logs/pipeline.log`. Format :

```
2026-06-17 10:39:32 INFO  bronze    | ina_jt | 268424 rows | 0 dupes | 12 nulls
12:21:14 | INFO     |   [schema] ina_jt ✓
12:21:14 | INFO     |   [schema] years ✓
12:21:14 | INFO     |   [schema] parite_unifiee ✓
2026-06-17 10:39:38 WARN  silver    | yearly_gender | 3 outliers > 100 %, capped
```

---

# 7. Les analyses avancées

## 7.1 Ruptures temporelles (`ruptures_detection.py`)

Algorithme **PELT** sur les séries mensuelles de chaque rubrique majeure.

- Entrée : `silver/ina_jt.csv`
- Sortie : `analyses/outputs/ruptures_points.csv` + un PNG par rubrique

## 7.2 Clustering ACP + k-means (`clustering_chaines.py`)

- ACP sur les profils thématiques (14 dim → 2 dim)
- k-means k=3
- Sortie : `analyses/outputs/clusters_chaines.csv` + `clusters_centroides.csv` + PNG

## 7.3 Corrélations Pearson (`correlation_themes_parite.py`)

- Matrice complète thèmes × parité
- p-value pour chaque corrélation
- Sortie : `analyses/outputs/correlation_themes_parite.csv` + heatmap

---

# 8. Backend PostgreSQL (optionnel)

La documentation Backend (Postgresql + Airflow + django) se trouve dans le dossier Projet Django & Airflow (https://github.com/Lu6asM/projet-etude-audiovisuel/tree/main/docs/Projet%20Django%20%26%20Airflow)

---

# 9. FAQ et erreurs fréquentes

## 9.1 `make: command not found` (Windows)

Sur Windows, `make` n'est pas installé par défaut. Solutions :

- **Recommandé** : remplacer chaque cible Make par sa commande Python (voir § 3)
- **Alternative** : installer GNU Make via [Chocolatey](https://chocolatey.org/) (`choco install make`) ou Scoop (`scoop install make`)

## 9.2 `streamlit: command not found`

Sur Windows, le script `streamlit.exe` n'est pas toujours dans le PATH. Lancer avec :

```bash
python -m streamlit run dashboard/app.py
```

## 9.3 `UnicodeDecodeError` au chargement des CSV

Les CSV sources sont en `latin-1`. Si tu modifies le pipeline, vérifie que `encoding="latin-1"` est bien passé à `pd.read_csv`.

## 9.4 Dashboard lent au premier chargement

Normal : `st.cache_data` charge les CSV en mémoire au premier affichage. Les suivants sont instantanés.

## 9.5 Erreur pandera `SchemaError: column 'X' has dtype object`

Une transformation Silver a laissé une colonne typée incorrectement. Vérifier la cellule en amont (souvent un `to_numeric` oublié).

## 9.6 PostgreSQL : `relation "channels" does not exist`

Le schéma n'a pas été appliqué. Lancer :
```bash
psql -d audiovisuel_ina -f backend/schema_postgresql.sql
```

---

# 10. Comment ajouter un nouveau dataset

1. Déposer le CSV dans `data/raw/`
2. Ajouter une fonction d'ingestion dans `pipeline.py` (couche Bronze)
3. Ajouter une fonction de nettoyage Silver
4. Ajouter un schéma pandera dans `pipeline_schemas.py`
5. Si pertinent, ajouter une table Gold qui s'appuie dessus
6. Mettre à jour le `CLAUDE.md` racine pour documenter la source
7. Si une visualisation dépend du dataset : ajouter un loader dans `dashboard/app.py`

---

# 11. Contact et support

- **Issues GitHub** : pour les bugs et demandes de feature
- **Equipe projet** :
  - Lucas — Data & Frontend
  - Baptiste — Lead Backend
  - Gérard — Quality & Documentation

---

# Annexe : commandes utiles

```bash
# Rejouer tout depuis zéro
make clean && make pipeline && make analyses && make dashboard

# Voir le log
tail -f logs/pipeline.log

# Lister les fichiers Gold
ls -la data/gold/

# Test rapide d'une table Gold
python -c "import pandas as pd; print(pd.read_csv('data/gold/parite_unifiee.csv').head())"
```
