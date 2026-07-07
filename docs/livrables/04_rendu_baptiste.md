# 1. Mon périmètre dans le projet

Sur ce projet, j'ai assumé le rôle **Lead Backend** :

- **Conception du schéma PostgreSQL** : 6 tables normalisées en 3NF (`dim_medias`, `dim_temps`, `dim_theme_genre`, `fait_parole_analyse_horaire`, `fait_parole_annuelle_genre`, `fait_theme_diffusion`), index optimisés, triggers automatiques, vues matérialisées pour les agrégats fréquents
- **Modèles Django ORM** : transcription du schéma en classes Python avec validators, properties calculées et managers personnalisés
- **API REST Django** (en cours de finalisation) : endpoints `/api/parole/`, `/api/themes-jt/`, `/api/parole-global/`, `/api/parole-zoom/`, `/api/predictions-parole/`, `api/themes/`
- Conteneurisation Docker en cours (prévue pour le déploiement)

L'objectif personnel : produire un **backend industrialisable** capable d'alimenter, à terme, des frontends multiples (React, Chart.js, mobile) au-delà du dashboard Streamlit.



# 2. Architecture Django du projet
## 2.0 Conteneurisation

```
Projet d'étude/
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── dashboard/
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   ├── import.html
│   │   ├── index.html
│   │   ├── page_parole_global.html
│   │   ├── page_parole_zoom.html
│   │   └── page_themes_jt.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── predictions.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── db.sqlite3
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```

Permet à un nouveau membre de l'équipe (ou à un évaluateur) de lancer le projet complet avec `docker-compose up`, sans installer Python, PostgreSQL ni dépendances locales.

## 2.1 Les routes (`urls.py`)

Le fichier `urls.py` constitue le point d'entrée des requêtes HTTP.

Chaque URL est associée à une fonction située dans `views.py`.

Exemple :

```python
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/parole/', views.data_temps_parole, name='api_parole'),
    path('api/themes/', views.data_themes_evolution, name='api_themes')
    ]
```

Les routes peuvent renvoyer :

- une page HTML destinée à être affichée dans le navigateur ;
- des données JSON destinées à être consommées par JavaScript ou par une autre application.

---

## 2.2 Les vues (`views.py`)

Les vues représentent la logique métier de l'application.

Elles reçoivent une requête HTTP, interrogent la base de données via l'ORM Django, effectuent les traitements nécessaires puis renvoient une réponse.

Dans ce projet, les vues remplissent principalement deux rôles :

- afficher les différentes pages du tableau de bord ;
- construire les jeux de données statistiques utilisés par les graphiques.

Par exemple, une vue peut agréger le temps de parole par année :

```python
def data_temps_parole(request):
    donnees = (
        FaitParoleAnalyseHoraire.objects
        .values('date__annee')
        .annotate(
            total_femmes=Sum('female_duration'),
            total_hommes=Sum('male_duration')
        )
        .order_by('date__annee')
    )

    categories_ans = [item['date__annee'] for item in donnees]
    data_femmes = [round(item['total_femmes'] / 3600, 2) for item in donnees]
    data_hommes = [round(item['total_hommes'] / 3600, 2) for item in donnees]

    return JsonResponse({
        'labels': categories_ans,
        'femmes': data_femmes,
        'hommes': data_hommes
    })
```

Les données obtenues sont ensuite converties au format JSON.

---

## 2.3 Les modèles (`models.py`)

Les modèles représentent les différentes tables de la base PostgreSQL.

Chaque classe Django correspond à une table relationnelle.

L'utilisation de l'ORM permet de manipuler les données directement en Python sans écrire de requêtes SQL complexes.

L'ORM prend automatiquement en charge :

- les jointures ;
- les filtres ;
- les agrégations ;
- les regroupements ;
- la conversion en SQL.

Cette approche rend le code plus lisible tout en conservant de bonnes performances.

---

## 2.4 Les templates

Les templates correspondent aux différentes pages HTML du tableau de bord.

Ils contiennent :

- la structure HTML ;
- les feuilles de style CSS ;
- le code JavaScript chargé de récupérer les données des API.

Chaque page possède son propre template :

- `index.html`
- `page_parole_globale.html`
- `page_parole_global.html`
- `page_parole_themes_jt.html`

Les graphiques sont générés dynamiquement après le chargement de la page.

---
## 2.5 Les endpoints de l'API REST

La liste des endpoint présents:

- `GET /api/parole/` — temps de parole total des femmes et des hommes par année
- `GET /api/themes/` — retourne les dix catégories de thèmes les plus représentées dans les journaux télévisés
- `GET /api/themes-jt/` — regroupe plusieurs jeux de données nécessaires à la page 
    - les cinq thèmes les plus fréquents ;
    - l'évolution annuelle des catastrophes et faits divers ;
    - la durée moyenne des sujets par catégorie ;
    - la répartition entre chaînes publiques et privées.
- `GET /api/parole-global` — indicateurs globaux concernant le temps de parole
    - l'évolution annuelle du temps de parole féminin et masculin ;
    - la répartition selon le type de média ;
    - la comparaison entre durée de parole et durée musicale ;
    - le taux de représentation féminine.
- `GET /api/parole-zoom` — analyse plus détaillée du temps de parole
    - le taux de parole par heure de diffusion ;
    - la comparaison entre les différentes chaînes ;
    - la répartition entre chaînes publiques et privées ;
    - la comparaison entre la période de nuit et la journée.
- `GET /api/predictions-parole` — module de prédiction (`predire_evolution_parole`) afin d'estimer l'évolution future du temps de parole.


Ces endpoints sont appelés depuis JavaScript afin d'alimenter les graphiques sans recharger la page.

Cette architecture facilite également la réutilisation du backend par d'autres applications.

# 2.bis Airflow
Dans le but d'alimenter de manière constante et péreine la base de donnée, il m'a fallu monté un Airflow appelant les données recherchées de l'INA

# 3. Analyse critique des limites techniques rencontrées

## 3.1 Volumétrie sous-estimée au départ

Les 268 K lignes de `daily_stats` paraissaient modestes, mais en multipliant par 14 rubriques et 5 chaînes (avec des jointures), certaines requêtes analytiques sont rapidement passées au-dessus de 200 ms. **Solution appliquée** : index composites `(channel_id, theme_id, jour)` + vue matérialisée `mv_monthly_aggregates` rafraîchie quotidiennement.

## 3.2 Choix Django contre FastAPI

J'ai hésité entre **Django REST Framework** (plus structuré, ORM intégré, admin natif) et **FastAPI** (plus moderne, async, plus rapide). J'ai tranché pour Django pour la cohérence avec l'écosystème enseigné en cours et la richesse de l'admin. Une refonte FastAPI serait pertinente si on visait des performances très élevées ou un déploiement serverless.

## 3.3 Pas de tests unitaires sur les modèles

Faute de temps, je n'ai pas écrit de suite de tests pytest sur les modèles Django. Les contraintes BDD couvrent une partie (FK, NOT NULL, CHECK), mais la logique métier des properties calculées et des managers n'est pas testée. **Dette technique à rattraper** en début de cycle suivant.



# 4. Analyse personnelle

## 4.1 Défis rencontrés

**Coordination avec la couche Gold.**
Le contrat entre la sortie du pipeline data (CSV Gold) et l'entrée du chargement BDD a évolué plusieurs fois : nouvelles colonnes, renommages, changements de types. J'ai dû renégocier avec Lucas plusieurs schémas à chaque itération du pipeline. Une **convention de schéma versionné** (type pandera schema sérialisé) aurait évité plusieurs régressions.

**Indexation PostgreSQL.**
J'avais sous-estimé l'impact des index sur la performance. La première version chargeait les données sans index pour ne pas ralentir l'insertion, ce qui était correct. Mais j'ai oublié de les recréer après chargement, et certaines requêtes prenaient 3-5 secondes. Une fois les index posés, on est descendu à <50 ms. **Leçon** : penser l'index dès la conception, pas après.

**Choix de Django vs FastAPI sous pression de temps.**
Le débat a duré une semaine. En rétrospective, le bon réflexe aurait été de **prototyper les deux** pendant une demi-journée avec un endpoint chacun, pour décider sur du concret plutôt que sur la doctrine.

## 4.2 Forces personnelles identifiées

- **Pensée systémique** : capacité à voir le projet comme un ensemble (BDD + pipeline + frontend + déploiement) et anticiper les contrats entre couches
- **Rigueur sur les conventions** : nommage cohérent des tables, des champs, des migrations
- **Soucis de l'optimisation pour expérience utilisateur**

## 4.3 Faiblesses identifiées

- **Difficulté à finir** : j'ai eu tendance à raffiner le schéma plutôt qu'à livrer l'API, ce qui a retardé le backend complet
- **Connaissance fragmentaire du data science** : je laisse le ML à Lucas mais cela me fait dépendre de lui pour interpréter les sorties (clusters, ruptures)
- **Pas assez de pair-programming** : j'ai travaillé en solo sur le backend, alors qu'un duo aurait accéléré et solidifié le résultat

## 4.4 Compétences développées

| Compétence | Niveau avant | Niveau après |
|---|---|---|
| PostgreSQL avancé (index, MV, triggers) | Débutant | Confirmé |
| Django ORM (modèles, managers, validators) | Débutant | Confirmé |
| Django REST Framework | Débutant | Confirmé |
| Normalisation 3NF en pratique | Théorique | Pratique |
| Architecture microservices | Notions | Compréhension claire |

## 5 Axes d'améliorations

## 5.1 Déploiement cloud

Stratégie envisagée :

- **API Django** sur Railway ou Render (free tier suffisant pour la démo)
- **PostgreSQL managé** sur Supabase (free 500 Mo) ou Neon (free 3 Go)
- **Dashboard Streamlit** sur Streamlit Community Cloud
- **DNS** sur un sous-domaine personnel pour la démo

## 5.2 Authentification et permissions

Aujourd'hui le backend n'est pas protégé. À terme :

- **Lecture publique** des données agrégées (mission de service public)
- **Écriture / mise à jour** réservée aux administrateurs (Django Admin natif)
- **Tokens JWT** pour les intégrations tierces avec rate limiting

## 5.3 Ajouts de nouveaux endpoints
L'ajout de nouveaux endpoint peut être important en fonction des besoins de chacuns, avec un système de choix de la data a sélectionner.



## Axes d’améliorations personnels pour de futurs projets
1. **Livrer un endpoint qui marche dès le premier sprint**, même grossier — itérer plutôt que peaufiner.
2. **Tester ses modèles** systématiquement avec pytest-django : couverture > 70 % avant merge.
3. **Versionner les contrats inter-couches** (pandera schemas, OpenAPI spec) pour éviter les régressions silencieuses.
4. **Apprendre FastAPI** pour pouvoir comparer en connaissance de cause sur le prochain projet.
5. **Mettre Docker dès le jour 1** : ne plus jamais avoir un évaluateur qui ne peut pas lancer le projet.
