"""
Chargement des tables Gold (+ Silver utiles) vers PostgreSQL.
Utilise SQLAlchemy pour créer les tables et les peupler depuis data/gold/.

Usage :
    # Configurer DATABASE_URL ci-dessous ou via variable d'environnement
    python backend/load_gold_to_postgres.py
"""

import logging
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR   = ROOT / "data" / "gold"
SILVER_DIR = ROOT / "data" / "silver"

# Priorité : variable d'env > valeur par défaut
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/audiovisuel_ina",
)

# Tables à charger (fichier CSV → nom de table PostgreSQL)
TABLES = {
    # Gold — tables analytiques directement exposées à Django/Chart.js
    GOLD_DIR   / "tv_theme_parite.csv":   "gold_tv_theme_parite",
    GOLD_DIR   / "parite_unifiee.csv":    "gold_parite_unifiee",
    GOLD_DIR   / "stats_prime_time.csv":  "gold_stats_prime_time",
    # Silver — utiles pour drill-down / requêtes ad-hoc
    SILVER_DIR / "ina_jt.csv":       "silver_ina_jt",
    SILVER_DIR / "years.csv":        "silver_years",
    SILVER_DIR / "hourstatall.csv":  "silver_hourstatall",
    SILVER_DIR / "radio_years.csv":  "silver_radio_years",
    SILVER_DIR / "tv_years.csv":     "silver_tv_years",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("load_gold")


def load_all(database_url: str = DATABASE_URL) -> None:
    log.info("Connexion à %s", database_url.rsplit("@", 1)[-1])  # sans mot de passe
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        log.error("Connexion PostgreSQL échouée : %s", exc)
        log.error("Vérifier DATABASE_URL ou que PostgreSQL tourne.")
        sys.exit(1)

    for csv_path, table_name in TABLES.items():
        if not csv_path.exists():
            log.warning("Fichier absent, skip : %s", csv_path.name)
            continue
        try:
            df = pd.read_csv(csv_path)
            # 'replace' : on recrée la table à chaque run (idempotent pour projet étudiant).
            # En production on préférerait 'append' + merge sur clé métier.
            df.to_sql(
                table_name,
                engine,
                if_exists="replace",
                index=False,
                chunksize=10_000,
                method="multi",
            )
            log.info("[%s] %d lignes chargées dans %s", csv_path.name, len(df), table_name)
        except Exception as exc:
            log.error("Échec chargement %s : %s", csv_path.name, exc)

    log.info("Chargement terminé.")


if __name__ == "__main__":
    load_all()
