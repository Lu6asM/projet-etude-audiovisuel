# 📊 SYNTHÈSE PROJET AUDIOVISUEL - Point équipe

**Date**: 02/02/2026  
**Équipe**: Baptiste, Lucas, Gérard  
**Objectif**: Aligner sur la structure BDD et répartir les tâches

---

## ✅ CE QUI EST FAIT

### 1. Analyse exploratoire complète
- ✓ 268,424 lignes analysées (JT 2000-2020)
- ✓ 14 thèmes identifiés
- ✓ 5 chaînes TV (TF1, France 2, France 3, M6, Arte)
- ✓ Qualité des données: 99% de complétude
- ✓ Features temporelles calculées

### 2. Architecture BDD PostgreSQL
- ✓ Schéma relationnel complet (5 tables)
- ✓ Index optimisés pour performances
- ✓ Triggers automatiques
- ✓ Vues matérialisées
- ✓ Normalisation 3NF

### 3. Scripts de migration
- ✓ Script Python CSV → PostgreSQL
- ✓ Gestion des FK et mapping
- ✓ Calcul automatique des features
- ✓ Batch processing (1000 lignes/batch)

### 4. Modèles Django
- ✓ 5 modèles ORM complets
- ✓ Validators et constraints
- ✓ Properties calculées
- ✓ Managers personnalisés

---

## 📈 CHIFFRES CLÉS

```
📊 VOLUME
   • 268,424 enregistrements quotidiens
   • 20 ans de données (2000-2020)
   • 586,438 sujets de JT
   • 14,466 heures de contenu

📺 PAR CHAÎNE (moyenne/jour)
   • TF1:      20.5 sujets, 31 min
   • France 2: 20.7 sujets, 32 min
   • France 3: 13.7 sujets, 21 min
   • M6:       12.7 sujets, 15 min
   • Arte:      9.7 sujets, 15 min

🎯 TOP 5 THÈMES
   1. Société (108K sujets)
   2. International (103K)
   3. Politique France (52K)
   4. Economie (51K)
   5. Culture-loisirs (44K)
```

---

## 🗄️ STRUCTURE BDD VALIDÉE

```
channels (5 lignes)          themes (14 lignes)
     ↓                            ↓
     └─────→ daily_stats ←────────┘
            (268K lignes)
            - date
            - nb_subjects
            - duration_sec
            - [features calculées]

yearly_gender (701 lignes)   hourly_stats (11K lignes)
- taux expression femmes     - parole par genre
- par année et chaîne        - par heure
```

**Avantages**:
- Pas de redondance (3NF)
- Requêtes rapides (index multiples)
- Facile à étendre
- Compatible Django ORM

---

## 🚀 PROCHAINES ÉTAPES

### PRIORITÉ 1: Base de données (Lucas + Gérard)
**Durée estimée**: 2-3h

1. **Créer la BDD PostgreSQL**
   ```bash
   createdb audiovisuel_ina
   psql -d audiovisuel_ina -f schema_postgresql.sql
   ```

2. **Exécuter la migration**
   ```bash
   # Configurer DATABASE_URL dans migration_script.py
   python3 migration_script.py
   ```

3. **Vérifier l'import**
   ```sql
   SELECT COUNT(*) FROM daily_stats;  -- Doit donner 268,424
   SELECT * FROM channels;            -- 5 chaînes
   SELECT * FROM themes;              -- 14 thèmes
   ```

### PRIORITÉ 2: Backend Django (Baptiste)
**Durée estimée**: 4-6h

1. **Setup Django**
   ```bash
   django-admin startproject audiovisuel .
   python manage.py startapp api
   ```

2. **Configurer settings.py**
   - Database connection
   - INSTALLED_APPS
   - CORS headers

3. **Copier les modèles**
   ```bash
   cp django_models.py backend/api/models.py
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Créer les endpoints API**
   - `/api/channels/`
   - `/api/themes/`
   - `/api/daily-stats/`
   - `/api/analytics/top-themes/`

### PRIORITÉ 3: Features & Viz (Tous)
**Durée estimée**: Variable

1. **Feature engineering** (Lucas)
   - Métriques agrégées
   - Calculs de tendances
   - Index de concentration

2. **Visualisations** (Baptiste)
   - Timeline thèmes
   - Heatmap chaîne × thème
   - Comparaisons inter-chaînes

3. **Streamlit** (Lucas - Plan B)
   - Dashboard interactif
   - Si Django prend du retard

---

## 📋 RÉPARTITION PROPOSÉE

### Baptiste (Lead Backend)
- ✅ Docker Django (en cours)
- [ ] API REST Framework
- [ ] Endpoints analytics
- [ ] Frontend viz

### Lucas (Data + Support Backend)
- ✅ Analyse exploratoire (fait)
- [ ] Migration BDD (avec Gérard)
- [ ] Feature engineering
- [ ] Streamlit (backup)

### Gérard (Data + Tests)
- [ ] Migration BDD (avec Lucas)
- [ ] Vérification données
- [ ] Tests requêtes SQL
- [ ] Documentation

---

## ⚠️ POINTS D'ATTENTION

### 1. Encodage
Les CSV sont en `latin-1` → certains accents posent problème.
**Solution**: Déjà géré dans le script de migration.

### 2. Performance
268K lignes = requêtes potentiellement lentes.
**Solution**: Index déjà créés dans le schéma SQL.

### 3. Valeurs manquantes
~1% des combinaisons date-chaîne manquent.
**Solution**: Négligeable, on garde comme ça.

### 4. Timeline serrée
7 juillet = 5 mois, mais alternance + autres projets.
**Solution**: Prioriser Backend + Viz basique d'abord.

---

## 🎯 OBJECTIFS CHECKPOINT (4 AVRIL)

**Pour Hackathon Paris (Lassitude)**:
- [x] BDD opérationnelle
- [ ] API REST fonctionnelle
- [ ] 2-3 visualisations de base
- [ ] Démo utilisable

**Stratégie**:
1. Semaine 1 (cette semaine): BDD + migration
2. Semaine 2-3: API Django
3. Semaine 4: Viz + intégration
4. Avant 4 avril: Tests & démo

---

## 💡 IDÉES VIZ POUR LE RENDU

### Obligatoires
1. **Timeline thèmes dominants** (évolution 2000-2020)
2. **Comparaison inter-chaînes** (profils thématiques)
3. **Heatmap chaîne × thème** (qui traite quoi)

### Optionnelles (si temps)
4. **Détection d'événements** (pics d'actualité)
5. **Gender data intégration** (thèmes vs parité)
6. **Prédiction tendances** (ML basique)

### Interactivité utilisateur
- Filtres: chaîne, période, thème
- Export PNG/PDF
- Possibilité de créer ses propres analyses

---

## 📁 FICHIERS DISPONIBLES

```
/home/claude/
├── analyse_exploratoire.py    # EDA complète
├── schema_postgresql.sql      # Schéma BDD
├── migration_script.py        # Migration CSV → PG
├── django_models.py           # Modèles ORM
└── README.md                  # Doc complète
```

**À récupérer maintenant** ✅

---

## 🤔 QUESTIONS À TRANCHER

### 1. Scope fonctionnel
- Focalisation sur une seule thématique? (ex: Santé, Environnement)
- Ou vue globale de tous les thèmes?

**Proposition**: Vue globale + possibilité de drill-down par thème

### 2. Frontend tech stack
- Pure Django templates?
- React/Vue.js?
- Streamlit (plus rapide)?

**Proposition**: Commencer Streamlit, migrer vers React si temps

### 3. Données radio
- Inclure les données radio? (25 lignes années)
- Ou focus 100% TV?

**Proposition**: Focus TV d'abord, radio = bonus si temps

### 4. Vidéo pour rendu
- Vidéo de démo obligatoire dans le cahier des charges
- Qui fait quoi?

**À décider**: Format, durée, contenu

---

## ✅ DÉCISIONS À PRENDRE MAINTENANT

1. **Valider le schéma BDD** → OK pour créer la base?
2. **Répartition finale** → Chacun sait ce qu'il fait?
3. **Timeline précise** → Deadlines intermédiaires?
4. **Communication** → Teams daily? Discord? Slack?
5. **Repo Git** → Où héberger le code?

---

## 📞 NEXT STEPS IMMÉDIATS

**Après ce point**:
1. Lucas & Gérard → Créer BDD + migration
2. Baptiste → Continuer Django + Docker
3. Tous → Commit initial sur Git
4. RDV dans 2-3 jours → Check avancement

**Communication**:
- Teams pour updates rapides
- Point synchro 2x/semaine

---

## 🎉 ON A DU BON MATOS !

- ✅ Structure BDD solide
- ✅ Scripts de migration prêts
- ✅ Analyse exploratoire complète
- ✅ Modèles Django propres
- ✅ Documentation claire

**On est bien partis !** 💪

---

**Questions?** → Slack/Teams
**Fichiers?** → `/home/claude/` ou je vous les envoie
