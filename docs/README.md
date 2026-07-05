# Projet Audiovisuel INA - Open Data University

## 📊 Vue d'ensemble

Analyse de l'évolution des thèmes diffusés à la télévision et à la radio française (2000-2020).

**Équipe**: Groupe 5 AUDIOVISUEL  
**Membres**: D'OLIVEIRA Gérard, MEIRELES Lucas, Baptiste B GARIE  
**Rendu final**: 7 Juillet 2026  

---

## 📁 Structure du projet

```
projet-audiovisuel/
├── data/
│   ├── raw/                          # CSV originaux INA
│   └── processed/                    # Données nettoyées
├── scripts/
│   ├── analyse_exploratoire.py       # Analyse EDA complète
│   ├── migration_script.py           # Migration CSV → PostgreSQL
│   └── data_cleaning.py              # Nettoyage des données
├── database/
│   ├── schema_postgresql.sql         # Schéma BDD complet
│   └── django_models.py              # Modèles Django ORM
├── backend/                          # Django application
│   ├── manage.py
│   ├── audiovisuel/                  # App principale
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py            # Django REST
│   │   └── urls.py
│   └── config/                       # Settings Django
├── frontend/                         # Interface utilisateur
│   ├── src/
│   └── package.json
└── docs/
    └── README.md
```

---

## 🗄️ Architecture Base de Données

### Schéma relationnel

```
┌─────────────────┐
│    channels     │     Chaînes TV/Radio (5 chaînes TV)
├─────────────────┤
│ id (PK)         │
│ name            │
│ is_public       │
│ media_type      │
└─────────────────┘
        │
        │ 1:N
        ↓
┌─────────────────┐         ┌─────────────────┐
│  daily_stats    │    N:1  │     themes      │    14 thèmes
├─────────────────┤←────────┤─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ date            │         │ name            │
│ channel_id (FK) │         │ category        │
│ theme_id (FK)   │         │ slug            │
│ nb_subjects     │         │ color_hex       │
│ duration_sec    │         └─────────────────┘
│ [features...]   │
└─────────────────┘
```

### Tables principales

1. **channels**: Référentiel des chaînes (TF1, France 2, France 3, M6, Arte)
2. **themes**: 14 thèmes (Société, International, Politique France, etc.)
3. **daily_stats**: 268,424 enregistrements quotidiens (2000-2020)
4. **yearly_gender**: Taux d'expression femmes/hommes par année
5. **hourly_stats**: Statistiques horaires de parole

---

## 📈 Données disponibles

### Dataset principal: JT quotidiens (2000-2020)
- **Volume**: 268,424 lignes
- **Période**: 2000-01-01 → 2020-12-31 (20 ans)
- **Chaînes**: TF1, France 2, France 3, M6, Arte
- **Thèmes**: 14 rubriques
- **Métriques**: nombre de sujets, durée totale

### Top 5 thèmes (20 ans)
1. **Société**: 108,039 sujets (2,730h)
2. **International**: 103,299 sujets (2,370h)
3. **Politique France**: 51,716 sujets (1,330h)
4. **Economie**: 50,529 sujets (1,392h)
5. **Culture-loisirs**: 44,071 sujets (1,326h)

### Datasets complémentaires
- Taux d'expression femmes/hommes (701 lignes)
- Stats horaires (11,507 lignes)
- TV par année (10 lignes)
- Radio par année (25 lignes)

---

## 🚀 Installation & Configuration

### Prérequis

```bash
# Python 3.8+
python3 --version

# PostgreSQL 12+
psql --version

# Node.js 16+ (pour le frontend)
node --version
```

### 1. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la BDD
CREATE DATABASE audiovisuel_ina;
CREATE USER ina_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE audiovisuel_ina TO ina_user;
\q
```

### 2. Initialiser le schéma

```bash
# Exécuter le schéma SQL
psql -U ina_user -d audiovisuel_ina -f database/schema_postgresql.sql

# Vérifier l'installation
psql -U ina_user -d audiovisuel_ina -c "\dt"
```

Vous devriez voir:
```
           List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | channels      | table | ina_user
 public | daily_stats   | table | ina_user
 public | hourly_stats  | table | ina_user
 public | themes        | table | ina_user
 public | yearly_gender | table | ina_user
```

### 3. Migrer les données

```bash
# Installer les dépendances Python
pip install pandas numpy sqlalchemy psycopg2-binary

# Configurer l'URL de connexion dans migration_script.py
# Ligne 17: DATABASE_URL = "postgresql://ina_user:password@localhost:5432/audiovisuel_ina"

# Exécuter la migration
python3 scripts/migration_script.py
```

**Durée estimée**: 2-3 minutes pour 280K+ lignes

### 4. Configurer Django

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer Django et dépendances
pip install django djangorestframework django-cors-headers psycopg2-binary

# Créer le projet Django
django-admin startproject audiovisuel .
python manage.py startapp api

# Copier les modèles
cp database/django_models.py backend/api/models.py

# Configurer settings.py
```

**settings.py**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'audiovisuel_ina',
        'USER': 'ina_user',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]
```

```bash
# Appliquer les migrations Django
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## 📊 Analyses disponibles

### Analyse exploratoire (EDA)

```bash
python3 scripts/analyse_exploratoire.py
```

**Résultats**:
- Structure des données
- Distribution par chaîne
- Top thèmes par période
- Évolution temporelle
- Statistiques descriptives
- Proposition de features

### Requêtes SQL utiles

```sql
-- Top 10 thèmes sur TF1 en 2020
SELECT 
    t.name,
    SUM(ds.nb_subjects) as total_subjects,
    ROUND(SUM(ds.duration_sec) / 3600.0, 2) as duration_hours
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
JOIN channels c ON ds.channel_id = c.id
WHERE c.name = 'TF1' AND ds.year = 2020
GROUP BY t.name
ORDER BY total_subjects DESC
LIMIT 10;

-- Évolution du thème "Santé" par année
SELECT 
    year,
    SUM(nb_subjects) as total_subjects,
    AVG(avg_duration_per_subject) as avg_duration
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
WHERE t.name = 'Santé'
GROUP BY year
ORDER BY year;

-- Comparaison public vs privé
SELECT 
    c.is_public,
    t.name as theme,
    COUNT(*) as nb_days,
    SUM(ds.nb_subjects) as total_subjects
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE ds.year = 2020
GROUP BY c.is_public, t.name
ORDER BY total_subjects DESC;
```

---

## 🎨 Visualisations possibles

### 1. Timeline des thèmes dominants
```python
# Évolution des 5 thèmes principaux sur 20 ans
import plotly.express as px

query = """
SELECT year, theme_name, SUM(nb_subjects) as count
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
WHERE theme_name IN ('Société', 'International', 'Politique France', 'Economie', 'Sport')
GROUP BY year, theme_name
"""

fig = px.line(df, x='year', y='count', color='theme_name',
              title='Évolution des thèmes principaux (2000-2020)')
fig.show()
```

### 2. Heatmap chaîne × thème
```python
# Matrice de chaleur
import seaborn as sns

query = """
SELECT c.name as chaine, t.name as theme, SUM(nb_subjects) as count
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE year = 2020
GROUP BY c.name, t.name
"""

pivot = df.pivot(index='chaine', columns='theme', values='count')
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd')
```

### 3. Comparaison inter-chaînes
```python
# Profil thématique par chaîne
query = """
SELECT c.name, t.name as theme, 
       SUM(nb_subjects) * 100.0 / SUM(SUM(nb_subjects)) OVER (PARTITION BY c.name) as pct
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
GROUP BY c.name, t.name
"""

fig = px.bar(df, x='theme', y='pct', color='name', barmode='group',
             title='Répartition thématique par chaîne (%)')
```

---

## 🔧 Features Engineering

### Features temporelles
```python
# Déjà implémentées dans daily_stats
- day_of_week: nom du jour
- week_number: semaine de l'année (1-52)
- month: mois (1-12)
- quarter: trimestre (1-4)
- year: année
- is_weekend: boolean
```

### Features à créer
```python
# Métriques agrégées
- pct_theme_par_chaine: % d'un thème sur une chaîne
- theme_dominant_jour: thème le plus traité par jour
- diversite_thematique: entropie de Shannon

# Métriques dérivées
- duree_moyenne_sujet: durée / nb_sujets
- score_actualite: poids des thèmes d'info
- index_concentration: Herfindahl-Hirschman

# Analyses comparatives
- ecart_avec_moyenne_nationale
- rang_theme_par_periode
- volatilite_thematique: std mobile
```

---

## 📝 API REST (Django)

### Endpoints proposés

```
GET /api/channels/                    # Liste des chaînes
GET /api/themes/                      # Liste des thèmes
GET /api/daily-stats/                 # Stats quotidiennes (paginé)
GET /api/daily-stats/?year=2020       # Filtrer par année
GET /api/daily-stats/?channel=1       # Filtrer par chaîne
GET /api/daily-stats/?theme=2         # Filtrer par thème

GET /api/analytics/top-themes/        # Top thèmes par période
GET /api/analytics/evolution/         # Évolution temporelle
GET /api/analytics/comparison/        # Comparaison inter-chaînes
GET /api/analytics/gender/            # Stats gender
```

### Exemple de vue Django

```python
from rest_framework import viewsets
from .models import DailyStat, Channel, Theme
from .serializers import DailyStatSerializer

class DailyStatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyStat.objects.all()
    serializer_class = DailyStatSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        year = self.request.query_params.get('year')
        channel_id = self.request.query_params.get('channel')
        theme_id = self.request.query_params.get('theme')
        
        if year:
            queryset = queryset.filter(year=year)
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        
        return queryset
```

---

## 🎯 Roadmap & Priorisation

### Phase 1: Base de données (Priorité HAUTE) ✅
- [x] Schéma PostgreSQL
- [x] Modèles Django
- [x] Script de migration
- [x] Analyse exploratoire

### Phase 2: Backend (Priorité HAUTE)
- [ ] API REST Django
- [ ] Endpoints analytics
- [ ] Tests unitaires
- [ ] Documentation API

### Phase 3: Frontend (Priorité MOYENNE)
- [ ] Interface de visualisation
- [ ] Dashboard principal
- [ ] Filtres dynamiques
- [ ] Export des graphiques

### Phase 4: Analyses avancées (Optionnel)
- [ ] Clustering de chaînes
- [ ] Détection d'événements
- [ ] Prédiction de tendances
- [ ] Intégration gender data

---

## 🐛 Problèmes connus

### Encodage des caractères
Les CSV originaux utilisent `latin-1`. Certains caractères spéciaux (accents) peuvent poser problème.

**Solution**:
```python
df = pd.read_csv(file, encoding='latin-1')
```

### Valeurs manquantes
~1% des combinaisons date-chaîne sont manquantes.

**Impact**: Négligeable pour les analyses

### Performance
268K+ lignes peuvent ralentir certaines requêtes sans index.

**Solution**: Index déjà créés sur date, channel_id, theme_id

---

## 📚 Ressources

### Documentation
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pandas](https://pandas.pydata.org/docs/)

### Données sources
- [INA Baromètre JT](https://www.data.gouv.fr/datasets/)
- [Temps de parole femmes/hommes](https://www.data.gouv.fr/datasets/)

### Contact
- Email: open-data-university@latitude.sa
- Notion: [Espace étudiants](https://www.notion.so/242ff5903e5a806c969fe369fd105aa2)

---

## 📅 Timeline

- **4 Avril**: Hackathon Paris (checkpoint Lassitude)
- **7 Juillet**: Rendu final pour les cours

---

## 🤝 Contribution

**Baptiste**: Docker Django, application viz  
**Lucas & Gérard**: Structure BDD, préparation données  

Pour contribuer:
1. Créer une branche: `git checkout -b feature/ma-feature`
2. Commit: `git commit -m "Ajout de ma feature"`
3. Push: `git push origin feature/ma-feature`
4. Créer une Pull Request

---

## 📄 Licence

Projet académique - Open Data University 2026
