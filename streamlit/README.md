# Projet M1 Big Data & IA — Les Françaises et Français face à l'information

Analyse de l'évolution des thèmes JT, de la représentation des femmes dans l'audiovisuel, et du rapport des Français à l'information (2000–2020).

## Stack

Python (pandas) • pandera • scikit-learn • ruptures • Streamlit • Django • PostgreSQL • Chart.js
Architecture médaillon : **Bronze → Silver → Gold** + validation de schéma + analyses avancées

## Structure du projet

```
.
├── pipeline.py                   Pipeline Bronze → Silver → Gold (point d'entrée)
├── pipeline_schemas.py           Contrats pandera (validation auto Silver/Gold)
├── requirements.txt              Dépendances Python
├── Makefile                      Raccourcis : install, pipeline, analyses, dashboard, db-load
├── data/
│   ├── raw/                      CSVs sources + events historiques + README
│   ├── bronze/                   Ingestion brute + rapports qualité
│   ├── silver/                   Données nettoyées, typées, enrichies
│   └── gold/                     6 tables analytiques prêtes Chart.js
├── analyses/                     Analyses avancées (produisent PNG + CSV)
│   ├── ruptures_detection.py     Détection automatique de points de bascule
│   ├── clustering_chaines.py     ACP + k-means sur profils thématiques
│   ├── correlation_themes_parite.py   Pearson thèmes × parité H/F
│   └── outputs/                  Sorties (graphes, CSV de synthèse)
├── dashboard/
│   └── app.py                    MVP Streamlit 6 onglets
├── backend/                      Django + PostgreSQL
│   ├── django_models.py
│   ├── schema_postgresql.sql
│   ├── migration_script.py       Legacy
│   └── load_gold_to_postgres.py  Chargement data/gold → Postgres
├── exploration/                  Scripts d'analyse ad-hoc initiaux
├── docs/                         Cahier des charges, synthèse équipe
└── logs/                         Sorties d'exécution du pipeline
```

## Démarrage rapide

```bash
make install      # Installer les dépendances Python
make pipeline     # Générer Bronze/Silver/Gold
make analyses     # Lancer les 3 analyses (ruptures, clustering, corrélations)
make dashboard    # Lancer le dashboard Streamlit sur localhost:8501
make db-load      # Charger Gold + Silver dans PostgreSQL
```

## 6 tables Gold

| Table | Grain | Usage |
|---|---|---|
| `tv_theme_parite` | (année, chaîne) 2010-2019 | Croise parts de rubriques JT × taux d'expression des femmes |
| `parite_unifiee` | (media_type, média, année) | Parité radio + TV, format long |
| `stats_prime_time` | (année, media_type, is_prime_time) | Évolution parité prime time vs hors prime time |
| `themes_evenements` | (événement, rubrique) | Delta % durée médiatique avant/pendant un fait historique |
| `saisonnalite` | (mois, rubrique) | Indice de saisonnalité des thèmes sur 20 ans |
| `parite_ranking` | (année, média, media_type) | Classement annuel par parité + rang/quartile |

## 3 analyses avancées

1. **Détection de ruptures temporelles** (`ruptures` PELT) — identifie automatiquement les points de bascule dans l'intensité des rubriques (COVID 2020, Macron 2017, crise 2008…)
2. **Clustering ACP + k-means** — regroupe les chaînes TV en archétypes thématiques (3 clusters identifiés)
3. **Corrélations Pearson** — matrice complète thèmes × parité. Trouvailles : +0.58 Société/Faits divers ↔ parité femmes, −0.60 International ↔ parité

## Datasets sources

- **ina-barometre-jt** — thèmes quotidiens JT 2000-2020, 5 chaînes, 14 rubriques
- **20190308-stats** — temps de parole H/F par chaîne/date/heure
- **20190308-years** — agrégats annuels parité
- **20190308-hourstatall** — stats par tranche horaire
- **20190308-radio-years / tv-years** — taux d'expression femmes par média
- **evenements_france.csv** — référentiel manuel 2000-2020 d'événements clés

## Qualité & validation

- Logs structurés (`logs/pipeline.log`) avec rapports qualité par dataset
- Contrats de schéma pandera : chaque table Silver/Gold validée automatiquement
- Gestion des nulls documentée dans chaque transformation
- Doublons détectés et supprimés avec trace
