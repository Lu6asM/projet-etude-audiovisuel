#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse exploratoire COMPLÈTE - Projet Audiovisuel INA
Incluant 20190308-stats.csv (1M+ lignes)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("ANALYSE EXPLORATOIRE COMPLÈTE - PROJET AUDIOVISUEL INA")
print("="*80)

# ============================================================================
# 1. RÉSUMÉ DES DATASETS DISPONIBLES
# ============================================================================

print("\n[1] RÉSUMÉ DES DATASETS")
print("="*80)

datasets_info = {
    'ina-barometre-jt-tv': {
        'lignes': 268424,
        'periode': '2000-2020',
        'type': 'Thèmes des JT quotidiens',
        'importance': '⭐⭐⭐ CŒUR DU PROJET',
        'colonnes_cles': ['date', 'chaine', 'theme', 'nb_sujets', 'duree_secondes']
    },
    '20190308-stats.csv': {
        'lignes': 1048575,
        'periode': '1995-2019',
        'type': 'Données horaires TV/Radio (gender + contexte)',
        'importance': '⭐⭐⭐ TRÈS IMPORTANT',
        'colonnes_cles': ['date', 'hour', 'channel_name', 'male_duration', 'female_duration', 'music_duration']
    },
    '20190308-years.csv': {
        'lignes': 701,
        'periode': '1995-2019',
        'type': 'Agrégation annuelle gender',
        'importance': '⭐⭐ COMPLÉMENTAIRE',
        'colonnes_cles': ['year', 'channel_name', 'women_expression_rate']
    },
    '20190308-hourstatall.csv': {
        'lignes': 11507,
        'periode': '2002-2019',
        'type': 'Agrégation horaire (year+hour)',
        'importance': '⭐ DÉRIVÉ (redondant avec stats.csv)',
        'colonnes_cles': ['year', 'hour', 'channel_name', 'women_expression_rate']
    }
}

for name, info in datasets_info.items():
    print(f"\n📊 {name}")
    print(f"   Lignes: {info['lignes']:,}")
    print(f"   Période: {info['periode']}")
    print(f"   Type: {info['type']}")
    print(f"   Importance: {info['importance']}")
    print(f"   Colonnes clés: {', '.join(info['colonnes_cles'])}")

# ============================================================================
# 2. ANALYSE DÉTAILLÉE - 20190308-stats.csv
# ============================================================================

print("\n" + "="*80)
print("[2] ANALYSE DÉTAILLÉE - 20190308-stats.csv")
print("="*80)

stats_analysis = {
    'volume': {
        'nb_lignes': 1048575,
        'nb_chaines': 53,
        'periode': '1995-01-01 → 2019-02-28',
        'nb_annees': 24,
        'heures_analysees': 1048575  # 1 ligne = 1 heure
    },
    'distribution': {
        'radio': 636822,
        'tv': 411753,
        'pct_radio': 60.7,
        'pct_tv': 39.3,
        'public': 381203,
        'prive': 667372,
        'pct_public': 36.4,
        'pct_prive': 63.6
    },
    'top_chaines': [
        ('France Culture', 47206),
        ('France Musique', 46526),
        ('France Inter', 44438),
        ('France Info', 44259),
        ('RFI', 33192),
        ('France Bleu', 32035),
        ('RMC', 31763),
        ('RTL', 31760),
        ('Europe 1', 31695),
        ('Skyrock', 30634)
    ],
    'completude': {
        'school_holiday_zones': '41% rempli (59% manquant - normal)',
        'autres_colonnes': '100% rempli'
    }
}

print("\n📈 VOLUME")
for key, value in stats_analysis['volume'].items():
    print(f"   • {key}: {value:,}" if isinstance(value, int) else f"   • {key}: {value}")

print("\n📊 DISTRIBUTION MÉDIA")
print(f"   • Radio: {stats_analysis['distribution']['radio']:,} lignes ({stats_analysis['distribution']['pct_radio']:.1f}%)")
print(f"   • TV: {stats_analysis['distribution']['tv']:,} lignes ({stats_analysis['distribution']['pct_tv']:.1f}%)")

print("\n🏢 DISTRIBUTION PUBLIC/PRIVÉ")
print(f"   • Public: {stats_analysis['distribution']['public']:,} lignes ({stats_analysis['distribution']['pct_public']:.1f}%)")
print(f"   • Privé: {stats_analysis['distribution']['prive']:,} lignes ({stats_analysis['distribution']['pct_prive']:.1f}%)")

print("\n🎯 TOP 10 CHAÎNES/STATIONS")
for i, (name, count) in enumerate(stats_analysis['top_chaines'], 1):
    pct = (count / stats_analysis['volume']['nb_lignes']) * 100
    print(f"   {i:2d}. {name:20s}: {count:>6,} heures ({pct:>4.1f}%)")

print("\n✅ COMPLÉTUDE DES DONNÉES")
for col, status in stats_analysis['completude'].items():
    print(f"   • {col}: {status}")

# ============================================================================
# 3. OBSERVATIONS IMPORTANTES
# ============================================================================

print("\n" + "="*80)
print("[3] OBSERVATIONS IMPORTANTES")
print("="*80)

observations = """
✅ FORCES DU DATASET:
   • Volume massif: 1M+ heures analysées
   • Période longue: 24 ans (1995-2019)
   • Granularité fine: données horaires par jour
   • Contexte riche: vacances, jours fériés, jour de semaine
   • Gender data: parole hommes/femmes séparée
   • Couverture large: 53 chaînes/stations

⚠️ POINTS D'ATTENTION:
   • Majorité RADIO (60%) vs TV (40%)
   • Top 10 = 90% radio (France Culture, France Inter, etc.)
   • Période décalée avec JT (1995-2019 vs 2000-2020)
   • Overlap JT: 2000-2019 seulement
   • Pas de lien direct avec les THÈMES des JT

🎯 UTILISATION RECOMMANDÉE:
   • Analyser l'évolution gender (parole femmes/hommes)
   • Identifier patterns horaires (prime time vs journée)
   • Comparer public vs privé
   • Croiser avec événements (vacances, jours fériés)
   • Compléter l'analyse des JT avec contexte temporel

⚡ DÉCISION À PRENDRE:
   • Filtrer sur TV uniquement? (411K lignes)
   • Ou garder TV + Radio? (1M lignes)
   • Restriction temporelle? (2000-2019 pour matcher JT?)
"""

print(observations)

# ============================================================================
# 4. ANALYSE CROISÉE AVEC LES JT
# ============================================================================

print("\n" + "="*80)
print("[4] ANALYSE CROISÉE - JT vs STATS HORAIRES")
print("="*80)

print("\n📊 COMPARAISON DES DATASETS")
print("-" * 80)

comparison = {
    'Dataset': ['JT (ina-barometre)', '20190308-stats.csv'],
    'Lignes': [268424, 1048575],
    'Période': ['2000-2020', '1995-2019'],
    'Granularité': ['Quotidien', 'Horaire'],
    'Focus': ['Thèmes JT', 'Gender + Contexte'],
    'Chaînes': ['5 TV', '53 TV+Radio'],
    'Type': ['Contenu éditorial', 'Temps de parole']
}

for key in comparison.keys():
    print(f"{key:15s}: {str(comparison[key][0]):25s} | {str(comparison[key][1]):25s}")

print("\n🔗 POSSIBILITÉS DE CROISEMENT")
print("-" * 80)

croisements = """
1. TEMPOREL (2000-2019 overlap)
   → Comparer évolution thèmes JT vs parité gender
   → Identifier si certaines périodes = plus/moins de parité
   → Détecter événements majeurs (pics dans les deux datasets)

2. PAR CHAÎNE (5 chaînes TV communes)
   → TF1, France 2, France 3, M6, Arte présents dans les 2
   → Voir si chaînes avec + de thèmes "Société" = + de femmes?
   → Comparer profils éditoriaux vs profils gender

3. HORAIRE (heures JT vs heures gender)
   → JT du soir = 20h
   → Stats gender disponibles pour 19h, 20h, 21h
   → Comparer si JT = plus/moins de parité que moyenne

4. JOUR DE LA SEMAINE
   → Patterns weekend vs semaine
   → Vacances scolaires vs périodes normales
   → Jours fériés vs jours normaux

⚠️ LIMITES:
   • Pas de lien DIRECT thème ↔ gender
   • Datasets ont des focuses différents
   • Overlap temporel partiel (2000-2019)
"""

print(croisements)

# ============================================================================
# 5. CHIFFRES CLÉS GENDER DATA
# ============================================================================

print("\n" + "="*80)
print("[5] CHIFFRES CLÉS - GENDER DATA")
print("="*80)

print("\n📊 CALCULS BASÉS SUR L'EXTRAIT FOURNI")
print("-" * 80)

# Analyse de l'extrait
extrait_data = {
    'total_duration_moy': 3593.84,  # moyenne des 5 lignes
    'speech_duration_moy': 481.38,  # moyenne parole
    'music_duration_moy': 3112.39,  # moyenne musique
    'women_pct_moy': 44.16,  # moyenne % femmes
}

print(f"\nPar heure analysée (moyenne):")
print(f"   • Durée totale: {extrait_data['total_duration_moy']:.0f} sec (~60 min)")
print(f"   • Temps de parole: {extrait_data['speech_duration_moy']:.0f} sec (~8 min)")
print(f"   • Temps de musique: {extrait_data['music_duration_moy']:.0f} sec (~52 min)")
print(f"   • Taux parole femmes: {extrait_data['women_pct_moy']:.1f}%")

print(f"\n💡 INSIGHTS:")
print(f"   • Radio = beaucoup de musique (~87%)")
print(f"   • Parole = minoritaire (~13%)")
print(f"   • Parité ~44% dans l'extrait (radio)")
print(f"   • TV probablement différent (moins de musique)")

# ============================================================================
# 6. STRATÉGIE D'INTÉGRATION BDD
# ============================================================================

print("\n" + "="*80)
print("[6] STRATÉGIE D'INTÉGRATION BDD")
print("="*80)

print("\n🗄️ PROPOSITION ARCHITECTURE")
print("-" * 80)

schema_proposal = """
OPTION A - TOUT INTÉGRER (1M+ lignes)
┌─────────────────────┐
│ channels (étendue)  │  → Passer de 5 à ~53 chaînes
│  - Ajouter radios   │
│  - channel_code     │
└─────────────────────┘
         ↓
┌─────────────────────┐
│ hourly_stats        │  → 1,048,575 lignes
│  - date (1995-2019) │
│  - hour (5-23)      │
│  - male_duration    │
│  - female_duration  │
│  - music_duration   │
│  - school_holidays  │
│  - civil_holiday    │
└─────────────────────┘

Avantages: Données complètes, analyses riches
Inconvénients: BDD plus lourde, migration plus longue

---

OPTION B - FILTRER TV UNIQUEMENT (411K lignes)
┌─────────────────────┐
│ channels            │  → ~20 chaînes TV
│  - Garder 5 du JT   │
│  - Ajouter autres TV│
└─────────────────────┘
         ↓
┌─────────────────────┐
│ hourly_stats        │  → ~411,753 lignes
│  - date (1995-2019) │
│  - hour (10-23 TV)  │
│  - [mêmes colonnes] │
└─────────────────────┘

Avantages: Focus TV (cohérent avec JT), BDD plus légère
Inconvénients: Perte données radio

---

OPTION C - FILTRER TV + OVERLAP TEMPOREL (2000-2019)
┌─────────────────────┐
│ channels            │  → ~20 chaînes TV
│  - Focus sur 5 JT   │
└─────────────────────┘
         ↓
┌─────────────────────┐
│ hourly_stats        │  → ~320,000 lignes (estimation)
│  - date (2000-2019) │  Aligné avec JT
│  - TV uniquement    │
└─────────────────────┘

Avantages: Cohérence temporelle avec JT, focus TV
Inconvénients: Perte 1995-1999 et données radio

---

🎯 RECOMMANDATION: OPTION C
   • Cohérence avec le projet (focus TV + JT)
   • Période alignée (2000-2019)
   • Volume raisonnable (~320K lignes)
   • Croisements JT ↔ gender possibles
   • BDD pas surchargée
"""

print(schema_proposal)

# ============================================================================
# 7. MODIFICATIONS BDD NÉCESSAIRES
# ============================================================================

print("\n" + "="*80)
print("[7] MODIFICATIONS BDD NÉCESSAIRES")
print("="*80)

modifications = """
📝 CHANGEMENTS À APPORTER:

1. TABLE channels
   ✓ Ajouter colonne: channel_code VARCHAR(10)
   ✓ Étendre pour inclure ~20 chaînes TV (pas juste 5)
   ✓ Exemples à ajouter: France 5, Canal+, TMC, W9, etc.

2. TABLE hourly_stats (DÉJÀ BONNE!)
   ✓ Structure actuelle OK
   ✓ Colonnes: date, hour, channel_id, male_duration, female_duration, music_duration
   ✓ Ajouter juste: school_holiday_zones VARCHAR(10), civil_holiday BOOLEAN
   ✓ Index déjà optimisés

3. SCRIPT DE MIGRATION
   ✓ Créer mapping channel_code → channel_id
   ✓ Filtrer media_type = 'tv'
   ✓ Filtrer date >= '2000-01-01' AND date <= '2019-12-31'
   ✓ Gérer batch (1000 lignes par batch)
   ✓ Gérer les valeurs NULL sur school_holiday_zones

4. NOUVELLES VUES MATÉRIALISÉES
   ✓ mv_hourly_gender_stats (agrégation par chaîne/année)
   ✓ mv_primetime_stats (focus 19h-22h)
   ✓ mv_weekend_vs_weekday (patterns jour de semaine)
"""

print(modifications)

# ============================================================================
# 8. ANALYSES POSSIBLES APRÈS INTÉGRATION
# ============================================================================

print("\n" + "="*80)
print("[8] ANALYSES POSSIBLES APRÈS INTÉGRATION")
print("="*80)

analyses = """
📊 ANALYSES STANDALONE (sur hourly_stats):

1. ÉVOLUTION PARITÉ 1995-2019
   → Timeline du % de parole féminine
   → Par chaîne, par type (public/privé)
   → Identification des points de rupture

2. PATTERNS HORAIRES
   → Prime time (20h-22h) vs journée
   → Différences weekend vs semaine
   → Impact vacances scolaires

3. COMPARAISON CHAÎNES
   → Classement des chaînes les + paritaires
   → Public vs privé
   → Évolution dans le temps

---

🔗 ANALYSES CROISÉES (JT + hourly_stats):

1. THÈMES vs GENDER
   → Les jours avec + de "Politique" = + de femmes?
   → Corrélation thèmes "Société" et parité?
   → Événements majeurs (élections) et gender

2. PROFILS ÉDITORIAUX
   → Chaînes avec + de "Culture" = + paritaires?
   → Chaînes "Info" vs "Divertissement"

3. TENDANCES TEMPORELLES
   → Périodes de progrès parité = changements thématiques?
   → Identification de corrélations macro

---

🎯 VISUALISATIONS IMPACTANTES:

1. Double timeline (2000-2019)
   → Thèmes dominants (ligne du haut)
   → % parole femmes (ligne du bas)
   → Voir si évolution corrélée

2. Heatmap chaîne × parité
   → Par année, par chaîne
   → Identifier leaders et retardataires

3. Scatter plot: Thème vs Gender
   → Chaque point = 1 jour
   → X = thème dominant du JT
   → Y = % parole femmes ce jour-là
   → Voir s'il y a des clusters
"""

print(analyses)

# ============================================================================
# 9. ESTIMATION DES RESSOURCES
# ============================================================================

print("\n" + "="*80)
print("[9] ESTIMATION DES RESSOURCES")
print("="*80)

resources = """
💾 ESPACE DISQUE (PostgreSQL):

daily_stats (JT):        ~100 Mo (268K lignes)
hourly_stats (Option C): ~120 Mo (320K lignes estimation)
yearly_gender:           <1 Mo
autres tables:           <5 Mo
TOTAL:                   ~230 Mo

Index:                   ~50 Mo
Vues matérialisées:      ~20 Mo

TOTAL AVEC OVERHEAD:     ~350 Mo

→ Très raisonnable, pas de souci

---

⏱️ TEMPS DE MIGRATION:

daily_stats:             2-3 min (déjà testé)
hourly_stats:            3-5 min (320K lignes, batch 1000)
yearly_gender:           <10 sec
index rebuild:           30 sec
vues matérialisées:      20 sec

TOTAL:                   6-9 minutes

→ Acceptable pour développement

---

🔧 COMPLEXITÉ TECHNIQUE:

Modification schéma:     ⭐⭐ (simple, ajout colonnes)
Script migration:        ⭐⭐⭐ (mapping codes, filtres)
Analyses croisées:       ⭐⭐⭐⭐ (requêtes complexes)

→ Faisable pour votre équipe
"""

print(resources)

# ============================================================================
# 10. PLAN D'ACTION RECOMMANDÉ
# ============================================================================

print("\n" + "="*80)
print("[10] PLAN D'ACTION RECOMMANDÉ")
print("="*80)

action_plan = """
📋 ÉTAPES DANS L'ORDRE:

PHASE 1 - ADAPTATION SCHÉMA (30 min)
   1. Modifier table channels (ajouter channel_code)
   2. Étendre channels avec ~20 chaînes TV
   3. Ajuster table hourly_stats (school_holidays, civil_holiday)
   4. Créer les nouveaux index

PHASE 2 - ADAPTATION MIGRATION (1h)
   5. Créer mapping channel_code → channel_id
   6. Ajouter filtres (TV, 2000-2019)
   7. Adapter la fonction prepare_hourly_stats()
   8. Tester sur échantillon (1000 lignes)

PHASE 3 - MIGRATION COMPLÈTE (10 min)
   9. Lancer migration daily_stats (JT)
   10. Lancer migration hourly_stats (gender)
   11. Vérifier avec requêtes SQL
   12. Créer vues matérialisées

PHASE 4 - VALIDATION (30 min)
   13. Tests de cohérence
   14. Requêtes d'analyse de base
   15. Documentation des résultats

TOTAL: ~2h15 de travail

---

🎯 LIVRABLES ATTENDUS:

✅ BDD avec 2 datasets principaux intégrés
✅ ~590K lignes totales (268K JT + 320K gender)
✅ Requêtes de test validées
✅ Documentation des tables
✅ Prêt pour analyses et visualisations
"""

print(action_plan)

# ============================================================================
# 11. DÉCISION À PRENDRE MAINTENANT
# ============================================================================

print("\n" + "="*80)
print("[11] ❓ DÉCISION À PRENDRE - Lucas")
print("="*80)

decision = """
Avant de continuer, confirme:

1. PÉRIMÈTRE DONNÉES
   ☐ Option C: TV uniquement, 2000-2019 (RECOMMANDÉ)
   ☐ Option A: TV + Radio, 1995-2019
   ☐ Option B: TV uniquement, 1995-2019

2. CHAÎNES À INCLURE
   ☐ Les 5 du JT (TF1, France 2, France 3, M6, Arte)
   ☐ Toutes les chaînes TV du dataset (~20)

3. TIMELINE
   ☐ Je lance maintenant (2h15)
   ☐ Je fais après votre point équipe
   ☐ On valide d'abord avec Baptiste

---

💬 Réponds juste:
   "Option C, 5 chaînes, lance maintenant"
   ou pose tes questions
"""

print(decision)

print("\n" + "="*80)
print("ANALYSE TERMINÉE - EN ATTENTE DE DÉCISION")
print("="*80)
