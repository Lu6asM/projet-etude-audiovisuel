#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration des données CSV vers PostgreSQL
Projet Open Data University - Lassitude
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Connection PostgreSQL (à adapter selon votre config)
DATABASE_URL = "postgresql://username:password@localhost:5432/audiovisuel_ina"

# Chemins des fichiers CSV
CSV_FILES = {
    'jt': '/mnt/user-data/uploads/ina-barometre-jt-tv-donnees-quotidiennes-2000-2020-nbre-sujets-durees-202410.csv',
    'years': '/mnt/user-data/uploads/20190308-years.csv',
    'hours': '/mnt/user-data/uploads/20190308-hourstatall.csv',
    'tv_years': '/mnt/user-data/uploads/20190308-tv-years.csv',
    'radio_years': '/mnt/user-data/uploads/20190308-radio-years.csv'
}

# Configuration de logging
BATCH_SIZE = 1000  # Taille des batchs pour insertion
VERBOSE = True

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def log(message):
    """Affiche un message avec timestamp"""
    if VERBOSE:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def create_db_engine(url):
    """Crée une connexion à la BDD"""
    try:
        engine = create_engine(url)
        log(f"✓ Connexion à la BDD établie")
        return engine
    except Exception as e:
        log(f"✗ Erreur de connexion à la BDD: {e}")
        raise

def get_or_create_id(engine, table, name_col, name_value, return_col='id'):
    """Récupère ou crée un ID dans une table de référence"""
    query = f"SELECT {return_col} FROM {table} WHERE {name_col} = '{name_value}'"
    
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
        if result:
            return result[0]
    
    return None

# ============================================================================
# CHARGEMENT DES DONNÉES
# ============================================================================

def load_data():
    """Charge tous les fichiers CSV"""
    log("\n" + "="*80)
    log("CHARGEMENT DES DONNÉES CSV")
    log("="*80)
    
    data = {}
    
    # JT quotidiens
    log("\n[1/5] Chargement des données JT...")
    df_jt = pd.read_csv(CSV_FILES['jt'],
                        sep=';', 
                        encoding='latin-1',
                        header=None,
                        names=['date', 'chaine', 'vide', 'theme', 'nb_sujets', 'duree_secondes'])
    df_jt = df_jt.drop('vide', axis=1)
    df_jt['date'] = pd.to_datetime(df_jt['date'], format='%d/%m/%Y')
    log(f"   ✓ {len(df_jt):,} lignes chargées")
    data['jt'] = df_jt
    
    # Expression femmes/hommes par année
    log("\n[2/5] Chargement des données genre (années)...")
    df_years = pd.read_csv(CSV_FILES['years'])
    log(f"   ✓ {len(df_years):,} lignes chargées")
    data['years'] = df_years
    
    # Stats horaires
    log("\n[3/5] Chargement des stats horaires...")
    df_hours = pd.read_csv(CSV_FILES['hours'])
    log(f"   ✓ {len(df_hours):,} lignes chargées")
    data['hours'] = df_hours
    
    # TV par année
    log("\n[4/5] Chargement TV par année...")
    df_tv = pd.read_csv(CSV_FILES['tv_years'])
    log(f"   ✓ {len(df_tv):,} lignes chargées")
    data['tv_years'] = df_tv
    
    # Radio par année
    log("\n[5/5] Chargement radio par année...")
    df_radio = pd.read_csv(CSV_FILES['radio_years'])
    log(f"   ✓ {len(df_radio):,} lignes chargées")
    data['radio_years'] = df_radio
    
    return data

# ============================================================================
# PRÉPARATION DES DONNÉES
# ============================================================================

def prepare_daily_stats(df_jt, engine):
    """Prépare les données daily_stats avec les FK"""
    log("\n" + "="*80)
    log("PRÉPARATION DES DONNÉES - DAILY_STATS")
    log("="*80)
    
    # Récupérer les mappings channel_id et theme_id
    log("\nRécupération des mappings channels...")
    with engine.connect() as conn:
        channels = pd.read_sql("SELECT id, name FROM channels", conn)
        themes = pd.read_sql("SELECT id, name FROM themes", conn)
    
    # Créer les dictionnaires de mapping
    channel_map = dict(zip(channels['name'], channels['id']))
    theme_map = dict(zip(themes['name'], themes['id']))
    
    log(f"   ✓ {len(channel_map)} chaînes mappées")
    log(f"   ✓ {len(theme_map)} thèmes mappés")
    
    # Mapper les IDs
    log("\nMapping des foreign keys...")
    df_jt['channel_id'] = df_jt['chaine'].map(channel_map)
    df_jt['theme_id'] = df_jt['theme'].map(theme_map)
    
    # Vérifier qu'il n'y a pas de valeurs NULL
    null_channels = df_jt['channel_id'].isnull().sum()
    null_themes = df_jt['theme_id'].isnull().sum()
    
    if null_channels > 0:
        log(f"   ⚠ {null_channels} chaînes non mappées détectées")
        unmapped = df_jt[df_jt['channel_id'].isnull()]['chaine'].unique()
        log(f"   Chaînes non mappées: {unmapped}")
    
    if null_themes > 0:
        log(f"   ⚠ {null_themes} thèmes non mappés détectés")
        unmapped = df_jt[df_jt['theme_id'].isnull()]['theme'].unique()
        log(f"   Thèmes non mappés: {unmapped}")
    
    # Supprimer les lignes avec des FK NULL
    df_clean = df_jt.dropna(subset=['channel_id', 'theme_id'])
    
    if len(df_clean) < len(df_jt):
        log(f"   ⚠ {len(df_jt) - len(df_clean)} lignes supprimées (FK manquantes)")
    
    # Ajouter les features calculées
    log("\nCalcul des features additionnelles...")
    df_clean['day_of_week'] = df_clean['date'].dt.day_name()
    df_clean['week_number'] = df_clean['date'].dt.isocalendar().week
    df_clean['month'] = df_clean['date'].dt.month
    df_clean['quarter'] = df_clean['date'].dt.quarter
    df_clean['year'] = df_clean['date'].dt.year
    df_clean['is_weekend'] = df_clean['date'].dt.dayofweek.isin([5, 6])
    
    # Renommer les colonnes pour la BDD
    df_clean = df_clean.rename(columns={
        'nb_sujets': 'nb_subjects',
        'duree_secondes': 'duration_sec'
    })
    
    # Sélectionner uniquement les colonnes nécessaires
    columns_to_keep = [
        'date', 'channel_id', 'theme_id', 'nb_subjects', 'duration_sec',
        'day_of_week', 'week_number', 'month', 'quarter', 'year', 'is_weekend'
    ]
    
    df_final = df_clean[columns_to_keep].copy()
    
    log(f"   ✓ {len(df_final):,} lignes prêtes pour insertion")
    
    return df_final

def prepare_yearly_gender(df_years, engine):
    """Prépare les données yearly_gender"""
    log("\n" + "="*80)
    log("PRÉPARATION DES DONNÉES - YEARLY_GENDER")
    log("="*80)
    
    # Récupérer le mapping des channels
    with engine.connect() as conn:
        channels = pd.read_sql("SELECT id, name, media_type FROM channels", conn)
    
    channel_map = dict(zip(channels['name'], channels['id']))
    
    # Filtrer uniquement les chaînes TV (pour l'instant)
    df_tv = df_years[df_years['media_type'] == 'tv'].copy()
    
    log(f"\nDonnées TV: {len(df_tv)} lignes")
    
    # Mapper les channel_id
    df_tv['channel_id'] = df_tv['channel_name'].map(channel_map)
    
    # Supprimer les lignes sans mapping
    df_clean = df_tv.dropna(subset=['channel_id'])
    
    if len(df_clean) < len(df_tv):
        log(f"   ⚠ {len(df_tv) - len(df_clean)} lignes supprimées (chaînes non trouvées)")
    
    # Sélectionner les colonnes
    columns_to_keep = [
        'channel_id', 'year', 'women_expression_rate', 
        'speech_rate', 'nb_hours_analyzed'
    ]
    
    df_final = df_clean[columns_to_keep].copy()
    
    log(f"   ✓ {len(df_final):,} lignes prêtes pour insertion")
    
    return df_final

def prepare_hourly_stats(df_hours, engine):
    """Prépare les données hourly_stats"""
    log("\n" + "="*80)
    log("PRÉPARATION DES DONNÉES - HOURLY_STATS")
    log("="*80)
    
    # Récupérer le mapping des channels
    with engine.connect() as conn:
        channels = pd.read_sql("SELECT id, name FROM channels", conn)
    
    channel_map = dict(zip(channels['name'], channels['id']))
    
    # Filtrer TV seulement
    df_tv = df_hours[df_hours['media_type'] == 'tv'].copy()
    
    log(f"\nDonnées TV horaires: {len(df_tv)} lignes")
    
    # Mapper les channel_id
    df_tv['channel_id'] = df_tv['channel_name'].map(channel_map)
    
    # Supprimer les lignes sans mapping
    df_clean = df_tv.dropna(subset=['channel_id'])
    
    # Gérer les jours fériés
    df_clean['is_holiday'] = df_clean['civil_holyday'].fillna(False).astype(bool)
    df_clean['holiday_zones'] = df_clean['school_holiday_zones'].fillna('')
    
    # Sélectionner les colonnes
    columns_to_keep = [
        'channel_id', 'date', 'hour', 
        'male_duration', 'female_duration', 'music_duration',
        'is_holiday', 'holiday_zones'
    ]
    
    df_final = df_clean[columns_to_keep].copy()
    
    log(f"   ✓ {len(df_final):,} lignes prêtes pour insertion")
    
    return df_final

# ============================================================================
# INSERTION DANS LA BDD
# ============================================================================

def insert_data(df, table_name, engine, batch_size=BATCH_SIZE):
    """Insère les données par batch"""
    log(f"\nInsertion dans {table_name}...")
    
    total_rows = len(df)
    batches = (total_rows // batch_size) + 1
    
    inserted = 0
    errors = 0
    
    for i in range(batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_rows)
        batch_df = df.iloc[start_idx:end_idx]
        
        try:
            batch_df.to_sql(
                table_name, 
                engine, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            inserted += len(batch_df)
            
            if VERBOSE and (i + 1) % 10 == 0:
                progress = (i + 1) / batches * 100
                log(f"   Progression: {progress:.1f}% ({inserted:,}/{total_rows:,} lignes)")
                
        except Exception as e:
            errors += len(batch_df)
            log(f"   ✗ Erreur batch {i+1}: {e}")
    
    log(f"   ✓ Insertion terminée: {inserted:,} lignes insérées, {errors} erreurs")
    
    return inserted, errors

# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    """Script principal de migration"""
    
    print("\n" + "="*80)
    print("MIGRATION DES DONNÉES CSV → POSTGRESQL")
    print("Projet Open Data University - Lassitude")
    print("="*80)
    
    start_time = datetime.now()
    
    try:
        # Connexion à la BDD
        log("\n[ÉTAPE 1] Connexion à la base de données")
        # Pour le test, on skip la vraie connexion
        # engine = create_db_engine(DATABASE_URL)
        
        log("\n⚠ MODE TEST: Connexion BDD désactivée")
        log("   Pour activer: décommenter la ligne create_db_engine() et configurer DATABASE_URL")
        
        # Chargement des données
        log("\n[ÉTAPE 2] Chargement des données CSV")
        data = load_data()
        
        # Préparation des données (sans insertion)
        log("\n[ÉTAPE 3] Préparation des données")
        
        # Pour le test, on simule la préparation sans BDD
        log("\n--- Simulation de préparation daily_stats ---")
        df_jt = data['jt']
        
        # Features temporelles
        df_jt['day_of_week'] = df_jt['date'].dt.day_name()
        df_jt['week_number'] = df_jt['date'].dt.isocalendar().week
        df_jt['month'] = df_jt['date'].dt.month
        df_jt['quarter'] = df_jt['date'].dt.quarter
        df_jt['year'] = df_jt['date'].dt.year
        df_jt['is_weekend'] = df_jt['date'].dt.dayofweek.isin([5, 6])
        
        log(f"   ✓ Features ajoutées: day_of_week, week_number, month, quarter, year, is_weekend")
        log(f"   ✓ {len(df_jt):,} lignes prêtes")
        
        # Stats
        log("\n" + "="*80)
        log("RÉSUMÉ DE LA MIGRATION (MODE TEST)")
        log("="*80)
        log(f"\n✓ JT quotidiens:      {len(data['jt']):>8,} lignes")
        log(f"✓ Gender (années):    {len(data['years']):>8,} lignes")
        log(f"✓ Stats horaires:     {len(data['hours']):>8,} lignes")
        log(f"✓ TV par année:       {len(data['tv_years']):>8,} lignes")
        log(f"✓ Radio par année:    {len(data['radio_years']):>8,} lignes")
        log(f"\nTotal: {sum(len(d) for d in data.values()):,} lignes chargées")
        
        # Instructions pour la vraie migration
        log("\n" + "="*80)
        log("PROCHAINES ÉTAPES POUR MIGRATION RÉELLE")
        log("="*80)
        log("""
1. Créer la base de données PostgreSQL:
   $ createdb audiovisuel_ina

2. Exécuter le schéma SQL:
   $ psql -d audiovisuel_ina -f schema_postgresql.sql

3. Configurer DATABASE_URL dans ce script:
   DATABASE_URL = "postgresql://user:pass@localhost:5432/audiovisuel_ina"

4. Décommenter la ligne create_db_engine() et les appels aux fonctions

5. Relancer le script:
   $ python3 migration_script.py
""")
        
        elapsed = datetime.now() - start_time
        log(f"\n✓ Script terminé en {elapsed.total_seconds():.2f} secondes")
        
    except Exception as e:
        log(f"\n✗ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
