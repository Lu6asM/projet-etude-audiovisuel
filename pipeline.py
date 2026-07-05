"""
Pipeline Bronze → Silver
Projet M1 Big Data & IA — "Les Françaises et Français face à l'information"
"""

import logging
import os
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# Validation de schéma (optionnelle — si pandera non installé, on skip)
try:
    from pipeline_schemas import GOLD_SCHEMAS, SILVER_SCHEMAS
    _PANDERA_OK = True
except ImportError:
    _PANDERA_OK = False
    GOLD_SCHEMAS = {}
    SILVER_SCHEMAS = {}

# ─────────────────────────────────────────────
# CONFIGURATION — modifier ces chemins si besoin
# ─────────────────────────────────────────────
ROOT = Path(__file__).parent
RAW_DIR    = ROOT / "data" / "raw"      # CSVs sources originaux
BRONZE_DIR = ROOT / "data" / "bronze"
SILVER_DIR = ROOT / "data" / "silver"
GOLD_DIR   = ROOT / "data" / "gold"
LOG_DIR    = ROOT / "logs"

# Fichiers source
SOURCES = {
    "ina_jt": RAW_DIR / "ina-barometre-jt-tv-donnees-quotidiennes-2000-2020-nbre-sujets-durees-202410.csv",
    "stats":        RAW_DIR / "20190308-stats.csv",
    "years":        RAW_DIR / "20190308-years.csv",
    "hourstatall":  RAW_DIR / "20190308-hourstatall.csv",
    "radio_years":  RAW_DIR / "20190308-radio-years.csv",
    "tv_years":     RAW_DIR / "20190308-tv-years.csv",
}

# Référentiel d'événements historiques (construit manuellement)
EVENTS_PATH = RAW_DIR / "evenements_france.csv"

# S'assurer que les dossiers existent avant l'initialisation du logger
for _d in (BRONZE_DIR, SILVER_DIR, GOLD_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Tranches horaires prime time (définition CSA)
PRIME_RADIO_START, PRIME_RADIO_END = 6, 9    # 06h–09h
PRIME_TV_START,    PRIME_TV_END    = 19, 22  # 19h–22h


# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
def setup_logging() -> logging.Logger:
    # StreamHandler en UTF-8 pour éviter les erreurs cp1252 sur Windows
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.stream.reconfigure(encoding="utf-8", errors="replace")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            stream_handler,
            logging.FileHandler(LOG_DIR / "pipeline.log", mode="w", encoding="utf-8"),
        ],
    )
    return logging.getLogger("pipeline")


log = setup_logging()


# ─────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────
def slugify(name: str) -> str:
    """snake_case sans accents ni caractères spéciaux."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return (
        ascii_str.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
        .replace(".", "_")
        .replace("%", "pct")
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [slugify(c) for c in df.columns]
    return df


def quality_report(name: str, df: pd.DataFrame) -> None:
    """Affiche un rapport de qualité (shape, types, nulls, doublons)."""
    log.info("══════════════════════════════════════════════")
    log.info("QUALITE [%s]  shape=%s", name, df.shape)
    log.info("  Colonnes   : %s", list(df.columns))
    log.info("  Types      : %s", df.dtypes.to_dict())
    nulls = (df.isnull().sum() / len(df) * 100).round(2)
    null_str = "  ".join(f"{c}={v}%" for c, v in nulls.items() if v > 0) or "aucun"
    log.info("  Nulls %%    : %s", null_str)
    dups = df.duplicated().sum()
    log.info("  Doublons   : %d", dups)
    log.info("══════════════════════════════════════════════")


def save_bronze(name: str, df: pd.DataFrame) -> None:
    path = BRONZE_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    log.info("[bronze] %s → %s  (%d lignes)", name, path.name, len(df))


def save_silver(name: str, df: pd.DataFrame) -> None:
    path = SILVER_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    log.info("[silver] %s → %s  (%d lignes)", name, path.name, len(df))


def save_gold(name: str, df: pd.DataFrame) -> None:
    path = GOLD_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    log.info("[gold] %s → %s  (%d lignes)", name, path.name, len(df))


def validate(df: pd.DataFrame, name: str, schemas: dict) -> None:
    """Valide un DataFrame contre son schéma pandera.

    Comportement :
      - Si pandera n'est pas installé ou si la table n'a pas de schéma : silencieux
      - Par défaut : log INFO si OK, WARNING si échec (non bloquant)
      - Avec PIPELINE_STRICT=1 dans l'env : lève une exception en cas d'échec
    """
    if not _PANDERA_OK or name not in schemas:
        return
    try:
        schemas[name].validate(df, lazy=True)
        log.info("  [schema] %s ✓", name)
    except Exception as exc:
        msg = str(exc).replace("\n", " | ")[:300]
        if os.getenv("PIPELINE_STRICT") == "1":
            log.error("  [schema] %s ✗ STRICT — %s", name, msg)
            raise
        log.warning("  [schema] %s ✗ — %s", name, msg)


def load_silver(name: str) -> pd.DataFrame:
    """Recharge une table silver depuis le disque (pour la couche Gold)."""
    return pd.read_csv(SILVER_DIR / f"{name}.csv", encoding="utf-8")


# ─────────────────────────────────────────────
# COUCHE BRONZE — ingestion brute
# ─────────────────────────────────────────────
def ingest_bronze() -> dict[str, pd.DataFrame]:
    log.info("▶ DEBUT COUCHE BRONZE")
    dfs: dict[str, pd.DataFrame] = {}

    # ── ina_jt ──────────────────────────────
    try:
        df = pd.read_csv(
            SOURCES["ina_jt"],
            sep=";",
            encoding="latin-1",
            header=None,
            # Fichier sans en-tête : on nomme les colonnes directement
            names=["date", "chaine", "col_vide", "rubrique", "nb_sujets", "duree_totale"],
        )
        quality_report("ina_jt", df)
        save_bronze("ina_jt", df)
        dfs["ina_jt"] = df
    except Exception as exc:
        log.error("[bronze] ina_jt — %s", exc)

    # ── datasets CSV standard ────────────────
    for name in ("stats", "years", "hourstatall", "radio_years", "tv_years"):
        try:
            df = pd.read_csv(SOURCES[name], encoding="utf-8")
            quality_report(name, df)
            save_bronze(name, df)
            dfs[name] = df
        except Exception as exc:
            log.error("[bronze] %s — %s", name, exc)

    log.info("▶ FIN COUCHE BRONZE  (%d datasets chargés)", len(dfs))
    return dfs


# ─────────────────────────────────────────────
# COUCHE SILVER — transformations par dataset
# ─────────────────────────────────────────────

# ── ina_jt ──────────────────────────────────
def silver_ina_jt(df: pd.DataFrame) -> pd.DataFrame:
    log.info("── silver ina_jt")
    df = df.copy()

    # Supprimer la colonne vide systématique (3e position, toujours NaN)
    df = df.drop(columns=["col_vide"])

    # Normaliser les noms de colonnes
    df = normalize_columns(df)

    # Parser la date (format JJ/MM/AAAA)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    n_bad_dates = df["date"].isnull().sum()
    if n_bad_dates:
        log.warning("  ina_jt — %d dates non parsées → lignes supprimées", n_bad_dates)
    df = df.dropna(subset=["date"])

    # Typage
    df["nb_sujets"] = pd.to_numeric(df["nb_sujets"], errors="coerce").astype("Int64")
    df["duree_totale"] = pd.to_numeric(df["duree_totale"], errors="coerce")

    # Supprimer les doublons
    before = len(df)
    df = df.drop_duplicates()
    log.info("  doublons supprimés : %d", before - len(df))

    # Nulls stratégie :
    # - chaine / rubrique : catégories métier indispensables → on supprime la ligne
    # - nb_sujets / duree_totale : valeurs numériques → on supprime aussi (pas de valeur par défaut sensée)
    df = df.dropna(subset=["chaine", "rubrique", "nb_sujets", "duree_totale"])

    # Variables temporelles dérivées
    df["annee"]       = df["date"].dt.year
    df["mois"]        = df["date"].dt.month
    # isoweekday() : 1=lundi … 7=dimanche ; on préfère le nom lisible
    df["jour_semaine"] = df["date"].dt.day_name()

    # Durée en minutes (plus lisible pour les graphes Chart.js)
    df["duree_totale_min"] = (df["duree_totale"] / 60).round(4)

    # Durée moyenne par sujet (secondes) — garde les secondes brutes pour précision
    # Division par zéro : nb_sujets == 0 très rare mais possible → on pose NaN
    df["duree_moyenne_par_sujet"] = np.where(
        df["nb_sujets"] > 0,
        df["duree_totale"] / df["nb_sujets"],
        np.nan,
    )
    df["duree_moyenne_par_sujet"] = df["duree_moyenne_par_sujet"].round(2)

    log.info("  ina_jt silver : %d lignes, %d colonnes", *df.shape)
    return df


# ── stats ────────────────────────────────────
def silver_stats(df: pd.DataFrame) -> pd.DataFrame:
    log.info("── silver stats")
    df = df.copy()

    # Renommer la typo d'origine (civil_holyday → civil_holiday)
    df = df.rename(columns={"civil_holyday": "civil_holiday"})
    df = normalize_columns(df)

    # Parser la date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    n_bad = df["date"].isnull().sum()
    if n_bad:
        log.warning("  stats — %d dates non parsées → supprimées", n_bad)
    df = df.dropna(subset=["date"])

    # Typage booléen — la source CSV stocke 'True'/'False' en string
    df["is_public_channel"] = df["is_public_channel"].map(
        {"True": True, "False": False, True: True, False: False}
    ).astype("boolean")

    # civil_holiday : même traitement booléen
    df["civil_holiday"] = df["civil_holiday"].map(
        {"True": True, "False": False, True: True, False: False}
    ).astype("boolean")

    # Durées numériques
    for col in ("male_duration", "female_duration", "music_duration"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Nulls stratégie :
    # - durées nulles : rare, correspond à des tranches sans diffusion mesurée → on garde (valeur = 0)
    for col in ("male_duration", "female_duration", "music_duration"):
        df[col] = df[col].fillna(0.0)

    # Supprimer les doublons
    before = len(df)
    df = df.drop_duplicates()
    log.info("  doublons supprimés : %d", before - len(df))

    # Variables dérivées
    df["total_speech_duration"] = df["male_duration"] + df["female_duration"]

    # Taux de parole féminine — division par zéro si total == 0 (musique pure)
    df["female_speech_rate"] = np.where(
        df["total_speech_duration"] > 0,
        df["female_duration"] / df["total_speech_duration"],
        np.nan,
    )
    df["female_speech_rate"] = df["female_speech_rate"].round(6)

    # Weekend : Saturday=6, Sunday=7 en isoweekday
    # La source donne le nom anglais du jour (Monday, Tuesday…)
    weekend_days = {"Saturday", "Sunday"}
    df["is_weekend"] = df["week_day"].isin(weekend_days)

    # Jour férié : civil_holiday OU school_holiday_zones non-null
    # school_holiday_zones contient un code zone (A/B/C) quand c'est vacances scolaires
    df["is_holiday"] = df["civil_holiday"].fillna(False) | df["school_holiday_zones"].notna()

    log.info("  stats silver : %d lignes, %d colonnes", *df.shape)
    return df


# ── years ────────────────────────────────────
def silver_years(df: pd.DataFrame) -> pd.DataFrame:
    log.info("── silver years")
    df = df.copy()
    df = normalize_columns(df)

    # Typage
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["is_public_channel"] = df["is_public_channel"].map(
        {"True": True, "False": False, True: True, False: False}
    ).astype("boolean")
    for col in ("women_expression_rate", "speech_rate", "nb_hours_analyzed"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Nulls stratégie :
    # - women_expression_rate / speech_rate : métriques clés → on garde les nulls
    #   (signifie absence de données pour cette année/chaîne, pas une erreur)
    # - nb_hours_analyzed null : on peut imputer 0 mais le plus honnête est de garder NaN
    before = len(df)
    df = df.drop_duplicates()
    log.info("  doublons supprimés : %d", before - len(df))

    log.info("  years silver : %d lignes, %d colonnes", *df.shape)
    return df


# ── hourstatall ──────────────────────────────
def silver_hourstatall(df: pd.DataFrame) -> pd.DataFrame:
    log.info("── silver hourstatall")
    df = df.copy()

    # La source a 'nb_hours_analysed' (avec 's') — on harmonise avec years
    df = df.rename(columns={"nb_hours_analysed": "nb_hours_analyzed"})
    df = normalize_columns(df)

    # Typage
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["hour"] = pd.to_numeric(df["hour"], errors="coerce").astype("Int64")
    df["is_public_channel"] = df["is_public_channel"].map(
        {"True": True, "False": False, True: True, False: False}
    ).astype("boolean")
    for col in ("women_expression_rate", "speech_rate", "nb_hours_analyzed"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Supprimer les doublons
    before = len(df)
    df = df.drop_duplicates()
    log.info("  doublons supprimés : %d", before - len(df))

    # Prime time selon méthodologie CSA
    # Radio : matin info 06h–09h  /  TV : soirée 19h–22h
    # On utilise la colonne media_type pour distinguer
    radio_prime = (df["media_type"] == "radio") & df["hour"].between(PRIME_RADIO_START, PRIME_RADIO_END - 1)
    tv_prime    = (df["media_type"] == "tv")    & df["hour"].between(PRIME_TV_START,    PRIME_TV_END - 1)
    df["is_prime_time"] = radio_prime | tv_prime

    log.info("  hourstatall silver : %d lignes, %d colonnes", *df.shape)
    return df


# ── radio_years (wide → long) ────────────────
def silver_wide_years(df: pd.DataFrame, name: str) -> pd.DataFrame:
    log.info("── silver %s (unpivot)", name)
    df = df.copy()

    # La première colonne est toujours 'year' — on la renomme, sans toucher
    # aux autres colonnes qui deviendront des VALEURS (noms de chaînes/stations
    # avec accents, casse, caractères spéciaux : à préserver pour l'affichage)
    df = df.rename(columns={df.columns[0]: "year"})

    value_cols = [c for c in df.columns if c != "year"]

    # Melt : year + variable (station/chaîne) + value (taux expression femmes)
    var_name = "station" if "radio" in name else "chaine"
    df_long = df.melt(
        id_vars=["year"],
        value_vars=value_cols,
        var_name=var_name,
        value_name="women_expression_rate",
    )

    # Typage
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype("Int64")
    df_long["women_expression_rate"] = pd.to_numeric(df_long["women_expression_rate"], errors="coerce")

    # Nulls stratégie :
    # Les NaN représentent des années où la station n'était pas encore mesurée
    # → on supprime ces lignes (pas de valeur = pas de ligne, conformément au cahier des charges)
    before = len(df_long)
    df_long = df_long.dropna(subset=["women_expression_rate"])
    log.info("  lignes NaN supprimées (station non mesurée) : %d", before - len(df_long))

    # Supprimer les doublons
    before2 = len(df_long)
    df_long = df_long.drop_duplicates()
    log.info("  doublons supprimés : %d", before2 - len(df_long))

    log.info("  %s silver : %d lignes, %d colonnes", name, *df_long.shape)
    return df_long


# ─────────────────────────────────────────────
# ORCHESTRATION PRINCIPALE
# ─────────────────────────────────────────────
def run_silver(bronze: dict[str, pd.DataFrame]) -> None:
    log.info("▶ DEBUT COUCHE SILVER")

    transforms = {
        "ina_jt":      (silver_ina_jt,     "ina_jt"),
        "stats":       (silver_stats,      "stats"),
        "years":       (silver_years,      "years"),
        "hourstatall": (silver_hourstatall, "hourstatall"),
    }

    for key, (fn, out_name) in transforms.items():
        if key not in bronze:
            log.warning("  %s absent du bronze, étape ignorée", key)
            continue
        try:
            silver_df = fn(bronze[key])
            quality_report(f"silver_{out_name}", silver_df)
            validate(silver_df, out_name, SILVER_SCHEMAS)
            save_silver(out_name, silver_df)
        except Exception as exc:
            log.error("[silver] %s — %s", key, exc, exc_info=True)

    # Wide datasets (radio_years, tv_years) : schéma propre par média
    for key, out_name in (("radio_years", "radio_years"), ("tv_years", "tv_years")):
        if key not in bronze:
            log.warning("  %s absent du bronze, étape ignorée", key)
            continue
        try:
            silver_df = silver_wide_years(bronze[key], key)
            quality_report(f"silver_{out_name}", silver_df)
            validate(silver_df, out_name, SILVER_SCHEMAS)
            save_silver(out_name, silver_df)
        except Exception as exc:
            log.error("[silver] %s — %s", key, exc, exc_info=True)

    log.info("▶ FIN COUCHE SILVER")


# ─────────────────────────────────────────────
# COUCHE GOLD — tables analytiques
# ─────────────────────────────────────────────

# Mapping chaînes INA → nom canonique dans `years` (pour la jointure)
# Les 5 chaînes INA existent toutes dans years (cf. diagnostic)
INA_TO_YEARS_CHANNEL = {
    "Arte":     "ARTE",
    "France 2": "France 2",
    "France 3": "France 3",
    "M6":       "M6",
    "TF1":      "TF1",
}


def gold_tv_theme_parite() -> pd.DataFrame:
    """
    Croise thèmes JT (INA) et parité H/F (years TV) sur (chaîne, année).
    Grain final : une ligne par (année, chaîne) avec :
      - part du temps consacré à chaque rubrique (colonnes pivot)
      - women_expression_rate / speech_rate / nb_hours_analyzed
    Période effective : 2010-2019 (intersection INA ∩ years).
    """
    log.info("── gold gold_tv_theme_parite")
    ina   = load_silver("ina_jt")
    years = load_silver("years")

    # 1) Agréger INA à l'année × chaîne × rubrique (somme durées et sujets)
    ina_agg = (
        ina.groupby(["annee", "chaine", "rubrique"], as_index=False)
           .agg(duree_totale_sec=("duree_totale", "sum"),
                nb_sujets=("nb_sujets", "sum"))
    )

    # 2) Calculer la part (%) de chaque rubrique dans l'année-chaîne
    total_annee_chaine = (
        ina_agg.groupby(["annee", "chaine"], as_index=False)["duree_totale_sec"]
               .sum().rename(columns={"duree_totale_sec": "total_chaine_sec"})
    )
    ina_agg = ina_agg.merge(total_annee_chaine, on=["annee", "chaine"])
    ina_agg["part_rubrique"] = (ina_agg["duree_totale_sec"] / ina_agg["total_chaine_sec"]).round(4)

    # 3) Pivot : une colonne par rubrique, préfixe 'part_' pour la lisibilité
    part_pivot = (
        ina_agg.pivot_table(index=["annee", "chaine"],
                            columns="rubrique",
                            values="part_rubrique",
                            fill_value=0.0)
               .add_prefix("part_")
    )
    part_pivot.columns = [slugify(c) for c in part_pivot.columns]
    part_pivot = part_pivot.reset_index()

    # 4) Normaliser le nom de chaîne pour le join
    part_pivot["chaine_join"] = part_pivot["chaine"].map(INA_TO_YEARS_CHANNEL)

    # 5) Filtrer years sur TV uniquement
    years_tv = years[years["media_type"] == "tv"].copy()

    # 6) Jointure (annee, chaine)
    gold = part_pivot.merge(
        years_tv[["year", "channel_name", "women_expression_rate",
                  "speech_rate", "nb_hours_analyzed", "is_public_channel"]],
        left_on=["annee", "chaine_join"],
        right_on=["year", "channel_name"],
        how="inner",  # seuls les couples (année, chaîne) présents des 2 côtés → 2010-2019
    ).drop(columns=["chaine_join", "year", "channel_name"])

    # Réordonner : clefs en tête, puis métriques parité, puis parts rubriques
    cols_order = (
        ["annee", "chaine", "is_public_channel",
         "women_expression_rate", "speech_rate", "nb_hours_analyzed"]
        + sorted(c for c in gold.columns if c.startswith("part_"))
    )
    gold = gold[cols_order].sort_values(["annee", "chaine"]).reset_index(drop=True)

    log.info("  gold_tv_theme_parite : %d lignes, %d colonnes", *gold.shape)
    return gold


def gold_parite_unifiee() -> pd.DataFrame:
    """
    Concatène radio_years et tv_years (même structure après melt) avec
    une colonne `media_type` pour distinguer. Une seule table pour les dashboards.
    """
    log.info("── gold gold_parite_unifiee")
    radio = load_silver("radio_years").rename(columns={"station": "media_name"})
    tv    = load_silver("tv_years").rename(columns={"chaine":  "media_name"})
    radio["media_type"] = "radio"
    tv["media_type"]    = "tv"

    # Exclure les lignes agrégats "Médiane*" — ce ne sont pas des chaînes/stations
    mask_radio = ~radio["media_name"].str.startswith("Médiane", na=False)
    mask_tv    = ~tv["media_name"].str.startswith("Médiane", na=False)
    radio = radio[mask_radio]
    tv    = tv[mask_tv]

    gold = pd.concat([radio, tv], ignore_index=True)
    gold = gold[["media_type", "media_name", "year", "women_expression_rate"]]
    gold = gold.sort_values(["media_type", "media_name", "year"]).reset_index(drop=True)

    log.info("  gold_parite_unifiee : %d lignes (%d radio + %d tv)",
             len(gold), mask_radio.sum(), mask_tv.sum())
    return gold


def gold_stats_prime_time() -> pd.DataFrame:
    """
    Agrège stats (1M lignes horaires) en (année, media_type, is_prime_time).
    Transforme un dataset trop granulaire pour Chart.js en vue exploitable.
    Prime time définition CSA : radio 06-09h, TV 19-22h.
    """
    log.info("── gold gold_stats_prime_time")
    stats = load_silver("stats")

    # Dériver l'année et is_prime_time (même règle que hourstatall)
    stats["year"] = pd.to_datetime(stats["date"]).dt.year
    stats["is_prime_time"] = (
        ((stats["media_type"] == "radio") & stats["hour"].between(PRIME_RADIO_START, PRIME_RADIO_END - 1))
        | ((stats["media_type"] == "tv")    & stats["hour"].between(PRIME_TV_START,    PRIME_TV_END - 1))
    )

    # Agrégation : sommes pondérées pour reconstruire les taux proprement
    gold = (
        stats.groupby(["year", "media_type", "is_prime_time"], as_index=False)
             .agg(male_duration=("male_duration", "sum"),
                  female_duration=("female_duration", "sum"),
                  music_duration=("music_duration", "sum"),
                  nb_observations=("date", "count"))
    )
    gold["total_speech_duration"] = gold["male_duration"] + gold["female_duration"]
    # Ré-calcul du taux sur les totaux agrégés (plus juste qu'une moyenne de ratios)
    gold["female_speech_rate"] = np.where(
        gold["total_speech_duration"] > 0,
        gold["female_duration"] / gold["total_speech_duration"],
        np.nan,
    ).round(6)

    gold = gold.sort_values(["year", "media_type", "is_prime_time"]).reset_index(drop=True)
    log.info("  gold_stats_prime_time : %d lignes, %d colonnes", *gold.shape)
    return gold


def gold_themes_evenements() -> pd.DataFrame:
    """
    Croise les sujets JT quotidiens avec un référentiel d'événements historiques
    (attentats, élections, crises…). Pour chaque événement, on mesure le delta
    de durée médiatique sur la rubrique visée (ex: +X% de 'Santé' pendant COVID).

    Méthode :
    - Fenêtre "pendant" = [date_debut, date_fin]
    - Fenêtre "avant"   = 30 jours précédant date_debut (baseline)
    - delta_pct = (moyenne_pendant / moyenne_avant - 1) * 100
    """
    log.info("── gold gold_themes_evenements")
    if not EVENTS_PATH.exists():
        log.warning("  %s absent — étape ignorée", EVENTS_PATH.name)
        return pd.DataFrame()

    ina = load_silver("ina_jt")
    ina["date"] = pd.to_datetime(ina["date"])

    events = pd.read_csv(EVENTS_PATH)
    events["date_debut"] = pd.to_datetime(events["date_debut"])
    events["date_fin"]   = pd.to_datetime(events["date_fin"])

    # Durée totale par (date, rubrique), toutes chaînes confondues
    ina_daily = (
        ina.groupby(["date", "rubrique"], as_index=False)["duree_totale"]
           .sum()
    )

    rows = []
    for _, ev in events.iterrows():
        # Chaque événement a une catégorie principale + d'éventuelles autres
        # rubriques impactées (colonne 'impact_attendu', séparées par '+')
        rubriques_cibles = [r.strip() for r in ev["impact_attendu"].split("+")]
        for rub in rubriques_cibles:
            during = ina_daily[
                (ina_daily["date"] >= ev["date_debut"])
                & (ina_daily["date"] <= ev["date_fin"])
                & (ina_daily["rubrique"] == rub)
            ]
            before = ina_daily[
                (ina_daily["date"] >= ev["date_debut"] - pd.Timedelta(days=30))
                & (ina_daily["date"] <  ev["date_debut"])
                & (ina_daily["rubrique"] == rub)
            ]
            mean_during = during["duree_totale"].mean() if len(during) else np.nan
            mean_before = before["duree_totale"].mean() if len(before) else np.nan
            delta_pct = (
                (mean_during / mean_before - 1) * 100
                if mean_before and mean_before > 0 else np.nan
            )
            rows.append({
                "evenement":       ev["evenement"],
                "date_debut":      ev["date_debut"].date(),
                "date_fin":        ev["date_fin"].date(),
                "rubrique":        rub,
                "duree_moy_avant": round(mean_before, 2) if pd.notna(mean_before) else None,
                "duree_moy_pendant": round(mean_during, 2) if pd.notna(mean_during) else None,
                "delta_pct":       round(delta_pct, 2) if pd.notna(delta_pct) else None,
            })

    gold = pd.DataFrame(rows).sort_values(["date_debut", "rubrique"]).reset_index(drop=True)
    log.info("  gold_themes_evenements : %d lignes (%d événements × rubriques)",
             len(gold), events.shape[0])
    return gold


def gold_saisonnalite() -> pd.DataFrame:
    """
    Heatmap des thèmes par mois — agrégation (mois, rubrique) sur 20 ans.
    Permet de détecter la saisonnalité : Sport l'été (JO, Tour de France),
    Politique à la rentrée, Économie en fin d'année, etc.
    """
    log.info("── gold gold_saisonnalite")
    ina = load_silver("ina_jt")

    # Total par (mois, rubrique) toutes chaînes × toutes années confondues
    by_month = (
        ina.groupby(["mois", "rubrique"], as_index=False)
           .agg(duree_totale_sec=("duree_totale", "sum"),
                nb_sujets=("nb_sujets", "sum"),
                nb_jours=("date", "nunique"))
    )

    # Part relative de la rubrique DANS le mois (% du temps JT de ce mois)
    total_par_mois = (
        by_month.groupby("mois", as_index=False)["duree_totale_sec"]
                .sum().rename(columns={"duree_totale_sec": "total_mois_sec"})
    )
    by_month = by_month.merge(total_par_mois, on="mois")
    by_month["part_dans_mois"] = (by_month["duree_totale_sec"] / by_month["total_mois_sec"]).round(4)

    # Indice de saisonnalité : part du mois / part moyenne annuelle
    # > 1 = rubrique sur-représentée ce mois-ci
    part_annuelle = (
        ina.groupby("rubrique")["duree_totale"].sum()
           / ina["duree_totale"].sum()
    ).to_dict()
    by_month["part_annuelle"] = by_month["rubrique"].map(part_annuelle).round(4)
    by_month["indice_saisonnalite"] = (
        by_month["part_dans_mois"] / by_month["part_annuelle"]
    ).round(3)

    gold = by_month[[
        "mois", "rubrique", "nb_sujets", "duree_totale_sec",
        "part_dans_mois", "part_annuelle", "indice_saisonnalite"
    ]].sort_values(["rubrique", "mois"]).reset_index(drop=True)

    log.info("  gold_saisonnalite : %d lignes (12 mois × 14 rubriques)", len(gold))
    return gold


def gold_parite_ranking() -> pd.DataFrame:
    """
    Classement annuel des chaînes/stations par taux d'expression des femmes.
    Permet d'identifier top/flop et suivre l'évolution du rang d'un média.
    Source : gold_parite_unifiee.
    """
    log.info("── gold gold_parite_ranking")
    # On lit directement la table gold précédente si elle existe
    parite_path = GOLD_DIR / "parite_unifiee.csv"
    if not parite_path.exists():
        log.warning("  parite_unifiee.csv absent — dépendance non satisfaite")
        return pd.DataFrame()

    df = pd.read_csv(parite_path)

    # Rang décroissant dans chaque (année, media_type) — 1 = meilleure parité
    df["rang"] = df.groupby(["year", "media_type"])["women_expression_rate"] \
                   .rank(method="min", ascending=False).astype("Int64")

    # Nombre total de médias en compétition cette année
    df["nb_medias"] = df.groupby(["year", "media_type"])["media_name"].transform("count")

    # Quartile : 1 = top 25 %, 4 = bottom 25 %
    df["quartile"] = df.groupby(["year", "media_type"])["women_expression_rate"] \
                       .transform(lambda s: pd.qcut(s, 4, labels=[4, 3, 2, 1], duplicates="drop")) \
                       .astype("Int64")

    df = df[[
        "year", "media_type", "media_name",
        "women_expression_rate", "rang", "nb_medias", "quartile"
    ]].sort_values(["year", "media_type", "rang"]).reset_index(drop=True)

    log.info("  gold_parite_ranking : %d lignes", len(df))
    return df


def run_gold() -> None:
    log.info("▶ DEBUT COUCHE GOLD")

    # IMPORTANT : ordre respecté car gold_parite_ranking dépend de gold_parite_unifiee
    gold_tables = {
        "tv_theme_parite":    gold_tv_theme_parite,
        "parite_unifiee":     gold_parite_unifiee,
        "stats_prime_time":   gold_stats_prime_time,
        "themes_evenements":  gold_themes_evenements,
        "saisonnalite":       gold_saisonnalite,
        "parite_ranking":     gold_parite_ranking,
    }

    for name, fn in gold_tables.items():
        try:
            df = fn()
            if df.empty:
                log.warning("[gold] %s — DataFrame vide, skip", name)
                continue
            quality_report(f"gold_{name}", df)
            validate(df, name, GOLD_SCHEMAS)
            save_gold(name, df)
        except Exception as exc:
            log.error("[gold] %s — %s", name, exc, exc_info=True)

    log.info("▶ FIN COUCHE GOLD")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Pipeline démarré — Python %s", sys.version.split()[0])

    bronze = ingest_bronze()
    run_silver(bronze)
    run_gold()

    log.info("Pipeline terminé. Bronze → %s | Silver → %s | Gold → %s",
             BRONZE_DIR, SILVER_DIR, GOLD_DIR)


if __name__ == "__main__":
    main()
