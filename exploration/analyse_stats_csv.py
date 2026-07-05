#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse exploratoire - 20190308-stats.csv
Dataset avec données horaires détaillées (date + hour)
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("ANALYSE DU FICHIER 20190308-stats.csv")
print("="*80)

# ============================================================================
# INFORMATIONS SUR LE DATASET (basé sur l'extrait fourni)
# ============================================================================

print("\n📋 STRUCTURE CONNUE DU FICHIER")
print("-" * 80)

columns_info = {
    'media_type': 'Type de média (radio/tv)',
    'channel_code': 'Code identifiant INA de la station',
    'channel_name': 'Nom de la station/chaîne',
    'is_public_channel': 'True si chaîne publique, False si privée',
    'date': 'Date au format année-mois-jour',
    'week_day': 'Jour de la semaine (en anglais)',
    'school_holiday_zones': 'Zones en vacances scolaires (A, B, C)',
    'civil_holyday': 'True si jour férié civil',
    'hour': 'Heure de début (5-23 radio, 10-23 TV)',
    'male_duration': 'Temps de parole hommes (secondes)',
    'female_duration': 'Temps de parole femmes (secondes)',
    'music_duration': 'Temps de musique (secondes)'
}

for col, desc in columns_info.items():
    print(f"  • {col:25s}: {desc}")

print(f"\n📊 VOLUME ANNONCÉ: 1,078,801 heures de programmes analysés")

# ============================================================================
# ANALYSE DE L'EXTRAIT FOURNI
# ============================================================================

print("\n" + "="*80)
print("ANALYSE DE L'EXTRAIT FOURNI")
print("="*80)

# Créer un dataframe depuis l'extrait fourni
extrait_text = """media_type,channel_code,channel_name,is_public_channel,date,week_day,school_holiday_zones,civil_holyday,hour,male_duration,female_duration,music_duration
radio,CHE,Chérie FM,False,2001-01-01,Monday,ABC,True,5,224.34,191.86,3180.34
radio,CHE,Chérie FM,False,2001-01-01,Monday,ABC,True,11,160.68,137.90,3297.08
radio,CHE,Chérie FM,False,2001-01-01,Monday,ABC,True,13,124.20,168.28,3303.96
radio,CHE,Chérie FM,False,2001-01-02,Tuesday,ABC,False,6,550.76,223.60,2818.50
radio,CHE,Chérie FM,False,2002-04-01,Monday,B,True,15,361.99,263.28,2962.06"""

from io import StringIO
df_extrait = pd.read_csv(StringIO(extrait_text))
df_extrait['date'] = pd.to_datetime(df_extrait['date'])

print("\n📋 Aperçu de l'extrait:")
print(df_extrait)

print("\n📊 Types de données:")
print(df_extrait.dtypes)

print("\n📈 Statistiques sur les durées (secondes):")
print(df_extrait[['male_duration', 'female_duration', 'music_duration']].describe())

# Calculs de base
df_extrait['total_duration'] = df_extrait['male_duration'] + df_extrait['female_duration'] + df_extrait['music_duration']
df_extrait['speech_duration'] = df_extrait['male_duration'] + df_extrait['female_duration']
df_extrait['women_pct'] = (df_extrait['female_duration'] / df_extrait['speech_duration'] * 100).round(2)

print("\n🎯 Métriques calculées:")
print(df_extrait[['date', 'hour', 'total_duration', 'speech_duration', 'women_pct']])

# ============================================================================
# QUESTIONS À RÉPONDRE POUR L'ANALYSE COMPLÈTE
# ============================================================================

print("\n" + "="*80)
print("QUESTIONS POUR TOI (Lucas)")
print("="*80)

questions = """
Pour que je puisse faire l'analyse exploratoire complète, 
j'ai besoin des infos suivantes sur le fichier complet:

1. VOLUME
   • Nombre total de lignes dans le fichier?
   • Taille du fichier (Mo/Go)?
   
2. PÉRIODE TEMPORELLE
   • Date la plus ancienne?
   • Date la plus récente?
   • Il y a des trous dans les dates?

3. MÉDIAS COUVERTS
   • Combien de chaînes TV uniques?
   • Combien de stations radio uniques?
   • Liste des principales chaînes TV (top 5-10)?

4. COMPLÉTUDE
   • Y a-t-il beaucoup de valeurs manquantes?
   • Toutes les heures (5-23) sont présentes pour chaque date?

5. DISTRIBUTION
   • Quelle proportion TV vs Radio? (en nombre de lignes)
   • Quelle proportion Public vs Privé?

📝 COMMANDES À LANCER (si possible):

# Infos de base
wc -l 20190308-stats.csv
du -h 20190308-stats.csv

# Avec pandas (si le fichier passe en mémoire)
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('20190308-stats.csv')

print(f"Nombre de lignes: {len(df):,}")
print(f"\\nColonnes: {df.columns.tolist()}")
print(f"\\nPériode: {df['date'].min()} → {df['date'].max()}")
print(f"\\nNombre de chaînes uniques: {df['channel_name'].nunique()}")
print(f"\\nTop 10 chaînes (nb lignes):")
print(df['channel_name'].value_counts().head(10))
print(f"\\nDistribution media_type:")
print(df['media_type'].value_counts())
print(f"\\nDistribution is_public_channel:")
print(df['is_public_channel'].value_counts())
print(f"\\nValeurs manquantes:")
print(df.isnull().sum())
EOF

# Ou si trop gros, un échantillon:
head -1000 20190308-stats.csv > stats_sample.csv
tail -1000 20190308-stats.csv >> stats_sample.csv

"""

print(questions)

# ============================================================================
# CE QUE JE VAIS FAIRE AVEC CES INFOS
# ============================================================================

print("\n" + "="*80)
print("CE QUE JE FERAI ENSUITE")
print("="*80)

plan = """
Une fois que tu m'auras donné ces infos, je vais:

1. ANALYSE EXPLORATOIRE COMPLÈTE
   ✓ Structure et qualité des données
   ✓ Distribution temporelle
   ✓ Analyse par média (TV vs Radio)
   ✓ Analyse par chaîne
   ✓ Patterns horaires
   ✓ Analyse gender (parole femmes/hommes)
   ✓ Contexte (vacances, jours fériés)

2. ADAPTATION DU SCHÉMA BDD
   ✓ Modifier la table hourly_stats pour ces données
   ✓ Ajouter les index nécessaires
   ✓ Créer les FK vers channels

3. SCRIPT DE MIGRATION
   ✓ Adapter le script pour charger ce fichier
   ✓ Gérer le volume (batch processing)
   ✓ Mapping des channel_code vers channel_id

4. ANALYSES CROISÉES
   ✓ Croiser avec les données JT
   ✓ Voir si on peut lier thèmes JT et gender data
   ✓ Identifier des patterns intéressants

"""

print(plan)

print("\n" + "="*80)
print("PRÊT À CONTINUER!")
print("="*80)
print("\n👉 Envoie-moi les stats demandées ci-dessus et on continue!")
