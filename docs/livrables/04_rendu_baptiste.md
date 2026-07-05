---
title: "Rendu individuel — Baptiste"
subtitle: "Projet Les Français face à l'information — M1 Big Data & IA"
author: "Baptiste [TODO Nom de famille]"
date: "Juin 2026"
lang: fr
toc: true
toc-depth: 2
geometry: margin=2cm
---

\newpage

# 1. Mon périmètre dans le projet

Sur ce projet, j'ai assumé le rôle **Lead Backend** :

- **Conception du schéma PostgreSQL** : 5 tables normalisées en 3NF (`channels`, `themes`, `daily_stats`, `yearly_gender`, `hourly_stats`), index optimisés, triggers automatiques, vues matérialisées pour les agrégats fréquents
- **Modèles Django ORM** : transcription du schéma en classes Python avec validators, properties calculées et managers personnalisés
- **Scripts de migration** : `migration_script.py` puis `load_gold_to_postgres.py` pour basculer les CSV Gold dans PostgreSQL en batch
- **API REST Django** (en cours de finalisation) : endpoints `/api/channels/`, `/api/themes/`, `/api/daily-stats/`, `/api/analytics/top-themes/`
- Conteneurisation Docker en cours (prévue pour le déploiement)

L'objectif personnel : produire un **backend industrialisable** capable d'alimenter, à terme, des frontends multiples (React, Chart.js, mobile) au-delà du dashboard Streamlit.

\newpage

# 2. Perspectives d'évolution

## 2.1 Finaliser l'API REST

Les endpoints prévus mais non encore livrés :

- `GET /api/channels/` — liste des chaînes avec métadonnées
- `GET /api/themes/` — liste des rubriques
- `GET /api/daily-stats/?channel=tf1&start=2020-01-01&end=2020-12-31` — séries temporelles filtrables
- `GET /api/analytics/top-themes/?year=2020` — agrégats les plus demandés (cache)
- `GET /api/analytics/parite-ranking/?year=2020&media_type=tv` — classement parité
- `POST /api/auth/` — JWT pour clients tiers

Avec **Django REST Framework** comme base, **drf-spectacular** pour l'OpenAPI auto-documentée, et **django-cors-headers** pour permettre l'appel depuis un frontend séparé.

## 2.2 Conteneurisation

```
project/
├── docker-compose.yml        # postgres + django + streamlit
├── backend/
│   └── Dockerfile            # Django + gunicorn
├── dashboard/
│   └── Dockerfile            # Streamlit
└── data/                     # volume monté pour les CSV Gold
```

Permet à un nouveau membre de l'équipe (ou à un évaluateur) de lancer le projet complet avec `docker-compose up`, sans installer Python, PostgreSQL ni dépendances locales.

## 2.3 Déploiement cloud

Stratégie envisagée :

- **API Django** sur Railway ou Render (free tier suffisant pour la démo)
- **PostgreSQL managé** sur Supabase (free 500 Mo) ou Neon (free 3 Go)
- **Dashboard Streamlit** sur Streamlit Community Cloud
- **DNS** sur un sous-domaine personnel pour la démo

## 2.4 Authentification et permissions

Aujourd'hui le backend n'est pas protégé. À terme :

- **Lecture publique** des données agrégées (mission de service public)
- **Écriture / mise à jour** réservée aux administrateurs (Django Admin natif)
- **Tokens JWT** pour les intégrations tierces avec rate limiting

\newpage

# 3. Analyse critique des limites techniques rencontrées

## 3.1 Volumétrie sous-estimée au départ

Les 268 K lignes de `daily_stats` paraissaient modestes, mais en multipliant par 14 rubriques et 5 chaînes (avec des jointures), certaines requêtes analytiques sont rapidement passées au-dessus de 200 ms. **Solution appliquée** : index composites `(channel_id, theme_id, jour)` + vue matérialisée `mv_monthly_aggregates` rafraîchie quotidiennement.

## 3.2 Encodage CSV vs UTF-8 PostgreSQL

Les CSV INA en `latin-1` ont posé problème lors du chargement initial : PostgreSQL est en UTF-8 strict, certains caractères passaient en `\x...`. **Solution** : conversion explicite dans le script de migration (`csv.reader(open(path, encoding="latin-1"))` puis insertion sur connexion UTF-8).

## 3.3 Choix Django vs FastAPI

J'ai hésité entre **Django REST Framework** (plus structuré, ORM intégré, admin natif) et **FastAPI** (plus moderne, async, plus rapide). J'ai tranché pour Django pour la cohérence avec l'écosystème enseigné en cours et la richesse de l'admin. Une refonte FastAPI serait pertinente si on visait des performances très élevées ou un déploiement serverless.

## 3.4 Pas de tests unitaires sur les modèles

Faute de temps, je n'ai pas écrit de suite de tests pytest sur les modèles Django. Les contraintes BDD couvrent une partie (FK, NOT NULL, CHECK), mais la logique métier des properties calculées et des managers n'est pas testée. **Dette technique à rattraper** en début de cycle suivant.

## 3.5 Migration scripts vs Django migrations

J'ai créé un `migration_script.py` autonome avant de basculer sur Django, ce qui fait deux pipelines de chargement (le script Python et `makemigrations`). C'est redondant et déroutant pour un nouvel arrivant. Idéalement : tout passer par Django et garder le script SQL `schema_postgresql.sql` comme documentation seulement.

\newpage

# 4. Documentation utilisateur

Voir `07_documentation_utilisateur.md` pour la doc complète. Section backend :

## Mise en place de la BDD

```bash
# 1. Installer PostgreSQL 15+
# 2. Créer la base
createdb audiovisuel_ina

# 3. Appliquer le schéma
psql -d audiovisuel_ina -f backend/schema_postgresql.sql

# 4. Charger les données Gold
make pipeline      # si pas déjà fait
python backend/load_gold_to_postgres.py

# 5. Vérifier
psql -d audiovisuel_ina -c "SELECT COUNT(*) FROM daily_stats;"
# attendu : 268424
```

## Lancer l'API Django (à venir)

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
# API : http://localhost:8000/api/
# Admin : http://localhost:8000/admin/
```

\newpage

# 5. Analyse personnelle

## 5.1 Défis rencontrés

**Coordination avec la couche Gold.**
Le contrat entre la sortie du pipeline data (CSV Gold) et l'entrée du chargement BDD a évolué plusieurs fois : nouvelles colonnes, renommages, changements de types. J'ai dû renégocier avec Lucas plusieurs schémas à chaque itération du pipeline. Une **convention de schéma versionné** (type pandera schema sérialisé) aurait évité plusieurs régressions.

**Indexation PostgreSQL.**
J'avais sous-estimé l'impact des index sur la performance. La première version chargeait les données sans index pour ne pas ralentir l'insertion, ce qui était correct. Mais j'ai oublié de les recréer après chargement, et certaines requêtes prenaient 3-5 secondes. Une fois les index posés, on est descendu à <50 ms. **Leçon** : penser l'index dès la conception, pas après.

**Choix de Django vs FastAPI sous pression de temps.**
Le débat a duré une semaine. En rétrospective, le bon réflexe aurait été de **prototyper les deux** pendant une demi-journée avec un endpoint chacun, pour décider sur du concret plutôt que sur la doctrine.

## 5.2 Forces personnelles identifiées

- **Pensée systémique** : capacité à voir le projet comme un ensemble (BDD + pipeline + frontend + déploiement) et anticiper les contrats entre couches
- **Rigueur sur les conventions** : nommage cohérent des tables, des champs, des migrations
- **Documentation des schémas** : j'ai produit un `schema_postgresql.sql` lisible avec commentaires inline, qui sert aussi de doc

## 5.3 Faiblesses identifiées

- **Difficulté à finir** : j'ai eu tendance à raffiner le schéma plutôt qu'à livrer l'API, ce qui a retardé le backend complet
- **Connaissance fragmentaire du data science** : je laisse le ML à Lucas mais cela me fait dépendre de lui pour interpréter les sorties (clusters, ruptures)
- **Pas assez de pair-programming** : j'ai travaillé en solo sur le backend, alors qu'un duo aurait accéléré et solidifié le résultat

## 5.4 Compétences développées

| Compétence | Niveau avant | Niveau après |
|---|---|---|
| PostgreSQL avancé (index, MV, triggers) | Intermédiaire | Confirmé |
| Django ORM (modèles, managers, validators) | Intermédiaire | Confirmé |
| Django REST Framework | Débutant | Intermédiaire |
| Normalisation 3NF en pratique | Théorique | Pratique |
| Migration scripts (batch, gestion erreurs) | Débutant | Intermédiaire |
| Architecture microservices | Notions | Compréhension claire |

## 5.5 Axes d'amélioration pour de futurs projets

1. **Livrer un endpoint qui marche dès le premier sprint**, même grossier — itérer plutôt que peaufiner.
2. **Tester ses modèles** systématiquement avec pytest-django : couverture > 70 % avant merge.
3. **Versionner les contrats inter-couches** (pandera schemas, OpenAPI spec) pour éviter les régressions silencieuses.
4. **Pair-programmer** sur les phases d'intégration : éviter le « tunnel » solo.
5. **Apprendre FastAPI** pour pouvoir comparer en connaissance de cause sur le prochain projet.
6. **Mettre Docker dès le jour 1** : ne plus jamais avoir un évaluateur qui ne peut pas lancer le projet.
