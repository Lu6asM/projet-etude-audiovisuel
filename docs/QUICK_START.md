# 🚀 QUICK START GUIDE - Projet Audiovisuel INA

## 📦 Fichiers générés

Tous les fichiers sont dans `/home/claude/`:
1. `analyse_exploratoire.py` - Analyse EDA complète
2. `schema_postgresql.sql` - Schéma BDD PostgreSQL
3. `migration_script.py` - Migration des données
4. `django_models.py` - Modèles Django ORM
5. `README.md` - Documentation complète
6. `SYNTHESE_POINT_EQUIPE.md` - Point équipe

---

## ⚡ SETUP RAPIDE (30 minutes)

### ÉTAPE 1: Installer PostgreSQL (si pas déjà fait)

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Windows**:
Télécharger depuis https://www.postgresql.org/download/windows/

---

### ÉTAPE 2: Créer la base de données

```bash
# Se connecter en tant que postgres
sudo -u postgres psql

# Dans psql:
CREATE DATABASE audiovisuel_ina;
CREATE USER ina_user WITH PASSWORD 'ina2024!';
ALTER USER ina_user WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE audiovisuel_ina TO ina_user;
\q
```

**Vérification**:
```bash
psql -U ina_user -d audiovisuel_ina -c "SELECT version();"
```

---

### ÉTAPE 3: Créer le schéma

```bash
# Depuis le dossier contenant schema_postgresql.sql
psql -U ina_user -d audiovisuel_ina -f schema_postgresql.sql
```

**Vérification**:
```bash
psql -U ina_user -d audiovisuel_ina -c "\dt"
```

Vous devez voir:
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

---

### ÉTAPE 4: Migrer les données

```bash
# Installer les dépendances
pip install pandas numpy sqlalchemy psycopg2-binary --break-system-packages

# Éditer migration_script.py ligne 17:
# DATABASE_URL = "postgresql://ina_user:ina2024!@localhost:5432/audiovisuel_ina"

# DANS LE SCRIPT, DÉCOMMENTER LA LIGNE 262:
# engine = create_db_engine(DATABASE_URL)

# DÉCOMMENTER LES LIGNES 275-278:
# df_daily = prepare_daily_stats(data['jt'], engine)
# df_gender = prepare_yearly_gender(data['years'], engine)
# df_hourly = prepare_hourly_stats(data['hours'], engine)

# DÉCOMMENTER LES LIGNES 282-284:
# insert_data(df_daily, 'daily_stats', engine)
# insert_data(df_gender, 'yearly_gender', engine)
# insert_data(df_hourly, 'hourly_stats', engine)

# Exécuter la migration
python3 migration_script.py
```

**Durée**: 2-3 minutes pour 268K+ lignes

**Vérification**:
```bash
psql -U ina_user -d audiovisuel_ina -c "SELECT COUNT(*) FROM daily_stats;"
# Doit afficher: 268424

psql -U ina_user -d audiovisuel_ina -c "SELECT COUNT(*) FROM channels;"
# Doit afficher: 5

psql -U ina_user -d audiovisuel_ina -c "SELECT COUNT(*) FROM themes;"
# Doit afficher: 14
```

---

### ÉTAPE 5: Setup Django (optionnel)

```bash
# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer Django
pip install django djangorestframework django-cors-headers psycopg2-binary

# Créer projet
django-admin startproject audiovisuel .
python manage.py startapp api

# Copier les modèles
cp django_models.py api/models.py

# Éditer audiovisuel/settings.py
```

**settings.py**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'audiovisuel_ina',
        'USER': 'ina_user',
        'PASSWORD': 'ina2024!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    # ... apps par défaut
    'rest_framework',
    'corsheaders',
    'api',
]
```

```bash
# Appliquer migrations
python manage.py makemigrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer serveur
python manage.py runserver
```

**Accès**: http://localhost:8000/admin/

---

## 🧪 TESTS DE VALIDATION

### Test 1: Compter les enregistrements

```sql
SELECT 
    'channels' as table_name, COUNT(*) as count FROM channels
UNION ALL
SELECT 'themes', COUNT(*) FROM themes
UNION ALL
SELECT 'daily_stats', COUNT(*) FROM daily_stats
UNION ALL
SELECT 'yearly_gender', COUNT(*) FROM yearly_gender
UNION ALL
SELECT 'hourly_stats', COUNT(*) FROM hourly_stats;
```

**Résultat attendu**:
```
    table_name    | count
------------------+--------
 channels         |      5
 themes           |     14
 daily_stats      | 268424
 yearly_gender    |    701
 hourly_stats     |  11507
```

### Test 2: Top 5 thèmes

```sql
SELECT 
    t.name,
    COUNT(DISTINCT ds.date) as nb_days,
    SUM(ds.nb_subjects) as total_subjects,
    ROUND(SUM(ds.duration_sec) / 3600.0, 2) as duration_hours
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
GROUP BY t.name
ORDER BY total_subjects DESC
LIMIT 5;
```

**Résultat attendu**:
```
       name        | nb_days | total_subjects | duration_hours
-------------------+---------+----------------+----------------
 Société           |   33424 |         108039 |        2730.54
 International     |   32556 |         103299 |        2369.78
 Politique France  |   19885 |          51716 |        1330.20
 Economie          |   21485 |          50529 |        1392.23
 Culture-loisirs   |   20546 |          44071 |        1325.99
```

### Test 3: Évolution annuelle

```sql
SELECT 
    year,
    COUNT(DISTINCT date) as nb_days,
    SUM(nb_subjects) as total_subjects,
    ROUND(AVG(duration_sec), 2) as avg_duration_sec
FROM daily_stats
GROUP BY year
ORDER BY year;
```

### Test 4: Comparaison chaînes

```sql
SELECT 
    c.name,
    c.is_public,
    COUNT(DISTINCT ds.date) as nb_days,
    SUM(ds.nb_subjects) as total_subjects,
    ROUND(SUM(ds.duration_sec) / 3600.0, 2) as duration_hours
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
GROUP BY c.id, c.name, c.is_public
ORDER BY total_subjects DESC;
```

---

## 🔍 REQUÊTES UTILES

### Rechercher un thème spécifique

```sql
SELECT 
    ds.date,
    c.name as chaine,
    t.name as theme,
    ds.nb_subjects,
    ROUND(ds.duration_sec / 60.0, 2) as duration_min
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE t.name = 'Santé' 
  AND ds.year = 2020
ORDER BY ds.date DESC
LIMIT 20;
```

### Tendance d'un thème par trimestre

```sql
SELECT 
    year,
    quarter,
    SUM(nb_subjects) as total_subjects,
    ROUND(AVG(avg_duration_per_subject), 2) as avg_duration
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
WHERE t.name = 'Environnement'
GROUP BY year, quarter
ORDER BY year, quarter;
```

### Heatmap chaîne × thème

```sql
SELECT 
    c.name as chaine,
    t.name as theme,
    SUM(ds.nb_subjects) as count,
    ROUND(SUM(ds.duration_sec) / 3600.0, 2) as hours
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE ds.year = 2020
GROUP BY c.name, t.name
ORDER BY c.name, count DESC;
```

### Top jours pour un thème

```sql
SELECT 
    ds.date,
    ds.day_of_week,
    c.name as chaine,
    ds.nb_subjects,
    ROUND(ds.duration_sec / 60.0, 2) as duration_min
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE t.name = 'International'
ORDER BY ds.nb_subjects DESC
LIMIT 10;
```

---

## 📊 ANALYSES PYTHON

### Exemple 1: Timeline avec Pandas

```python
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Connexion
engine = create_engine('postgresql://ina_user:ina2024!@localhost:5432/audiovisuel_ina')

# Query
query = """
SELECT year, theme_name, SUM(nb_subjects) as count
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
WHERE theme_name IN ('Société', 'International', 'Santé')
GROUP BY year, theme_name
ORDER BY year
"""

df = pd.read_sql(query, engine)

# Pivot pour le graphique
pivot = df.pivot(index='year', columns='theme_name', values='count')

# Plot
pivot.plot(kind='line', figsize=(12, 6))
plt.title('Évolution des thèmes principaux (2000-2020)')
plt.xlabel('Année')
plt.ylabel('Nombre de sujets')
plt.legend(title='Thème')
plt.grid(True)
plt.tight_layout()
plt.savefig('evolution_themes.png')
plt.show()
```

### Exemple 2: Heatmap Seaborn

```python
import seaborn as sns

query = """
SELECT c.name as chaine, t.name as theme, SUM(nb_subjects) as count
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
JOIN themes t ON ds.theme_id = t.id
WHERE year BETWEEN 2018 AND 2020
GROUP BY c.name, t.name
"""

df = pd.read_sql(query, engine)
pivot = df.pivot(index='chaine', columns='theme', values='count')

plt.figure(figsize=(14, 6))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd')
plt.title('Répartition thématique par chaîne (2018-2020)')
plt.tight_layout()
plt.savefig('heatmap_chaines_themes.png')
plt.show()
```

---

## 🐛 TROUBLESHOOTING

### Problème 1: Connexion PostgreSQL refusée

```bash
# Vérifier que PostgreSQL tourne
sudo systemctl status postgresql

# Redémarrer si nécessaire
sudo systemctl restart postgresql

# Vérifier le fichier pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ajouter: local all all trust
```

### Problème 2: Erreur d'encodage

```python
# Dans migration_script.py, ligne 68:
df_jt = pd.read_csv(CSV_FILES['jt'],
                    sep=';', 
                    encoding='latin-1',  # ← Important!
                    header=None)
```

### Problème 3: Migration lente

```bash
# Augmenter la taille du batch
# Dans migration_script.py, ligne 14:
BATCH_SIZE = 5000  # Au lieu de 1000
```

### Problème 4: Erreur FK manquante

```sql
-- Vérifier que channels et themes sont remplis
SELECT COUNT(*) FROM channels;  -- Doit être 5
SELECT COUNT(*) FROM themes;    -- Doit être 14

-- Re-exécuter juste les inserts de base
psql -U ina_user -d audiovisuel_ina -c "
INSERT INTO channels (name, is_public, media_type) VALUES
('TF1', false, 'tv'),
('France 2', true, 'tv'),
('France 3', true, 'tv'),
('M6', false, 'tv'),
('Arte', true, 'tv')
ON CONFLICT (name) DO NOTHING;
"
```

---

## 📞 SUPPORT

**Questions techniques**: Lucas (Teams/Slack)  
**Django/Backend**: Baptiste  
**BDD/Migration**: Gérard & Lucas  

**Ressources**:
- README.md complet
- Documentation PostgreSQL: https://www.postgresql.org/docs/
- Documentation Django: https://docs.djangoproject.com/

---

## ✅ CHECKLIST FINALE

Avant de considérer le setup terminé:

- [ ] PostgreSQL installé et démarré
- [ ] Base de données `audiovisuel_ina` créée
- [ ] Schéma SQL exécuté (5 tables créées)
- [ ] Données migrées (268K lignes dans daily_stats)
- [ ] Tests de validation passés
- [ ] Au moins 1 requête de test réussie
- [ ] Django installé et configuré (optionnel)
- [ ] Admin Django accessible (optionnel)

**Si tous les checks sont ✅ → Vous êtes prêts ! 🎉**

---

## 🎯 NEXT STEPS

1. **Créer l'API REST** (Baptiste)
2. **Feature engineering** (Lucas)
3. **Premières visualisations** (Tous)
4. **Tests utilisateurs**
5. **Préparation démo 4 avril**

**Bon courage ! 💪**
