"""
Contrats de schéma (pandera) pour les couches Silver et Gold.

Chaque DataFrame produit par pipeline.py est validé contre son schéma — sinon
le pipeline alerte (mode warning par défaut) ou échoue (mode strict via la
variable d'environnement PIPELINE_STRICT=1).

Les schémas utilisent `coerce=True` sur les colonnes string pour absorber les
variantes de typage (object pandas vs StringDtype pyarrow) sans casser la
validation. Cela rend le pipeline résilient aux changements de version pandas.
"""

import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check


# ─────────────────────────────────────────────
# SILVER
# ─────────────────────────────────────────────
silver_ina_jt_schema = DataFrameSchema(
    {
        "date":                    Column("datetime64[ns]", nullable=False, coerce=True),
        "chaine":                  Column(str, Check.isin(["TF1", "France 2", "France 3", "Arte", "M6"]), coerce=True),
        "rubrique":                Column(str, nullable=False, coerce=True),
        "nb_sujets":               Column(pa.Int64, Check.ge(0), nullable=True, coerce=True),
        "duree_totale":            Column(float, Check.ge(0), coerce=True),
        "annee":                   Column(int, Check.in_range(2000, 2020), coerce=True),
        "mois":                    Column(int, Check.in_range(1, 12), coerce=True),
        "jour_semaine":            Column(str, coerce=True),
        "duree_totale_min":        Column(float, Check.ge(0), coerce=True),
        "duree_moyenne_par_sujet": Column(float, nullable=True, coerce=True),
    },
    strict=False,  # tolère colonnes supplémentaires
)


silver_years_schema = DataFrameSchema(
    {
        "media_type":            Column(str, Check.isin(["tv", "radio"]), coerce=True),
        "channel_name":          Column(str, coerce=True),
        "is_public_channel":     Column("boolean", nullable=True, coerce=True),
        "year":                  Column(pa.Int64, Check.in_range(1995, 2025), coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), nullable=True, coerce=True),
        "speech_rate":           Column(float, Check.ge(0), nullable=True, coerce=True),
        "nb_hours_analyzed":     Column(float, Check.ge(0), nullable=True, coerce=True),
    },
    strict=False,
)


silver_stats_schema = DataFrameSchema(
    {
        "date":         Column("datetime64[ns]", nullable=True, coerce=True),
        "channel_name": Column(str, coerce=True),
        "media_type":   Column(str, Check.isin(["tv", "radio"]), coerce=True),
    },
    strict=False,
)


silver_hourstatall_schema = DataFrameSchema(
    {
        "year":         Column(pa.Int64, Check.in_range(1995, 2025), coerce=True),
        "channel_name": Column(str, coerce=True),
        "media_type":   Column(str, Check.isin(["tv", "radio"]), coerce=True),
    },
    strict=False,
)


# ─────────────────────────────────────────────
# GOLD
# ─────────────────────────────────────────────
gold_tv_theme_parite_schema = DataFrameSchema(
    {
        "annee":                 Column(int, Check.in_range(2010, 2019), coerce=True),
        "chaine":                Column(str, Check.isin(["TF1", "France 2", "France 3", "Arte", "M6"]), coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), coerce=True),
        "speech_rate":           Column(float, Check.ge(0), coerce=True),
        "nb_hours_analyzed":     Column(float, Check.ge(0), coerce=True),
    },
    strict=False,  # 14 colonnes part_* tolérées sans listing individuel
)


gold_parite_unifiee_schema = DataFrameSchema(
    {
        "media_type":            Column(str, Check.isin(["tv", "radio"]), coerce=True),
        "media_name":            Column(str, coerce=True),
        "year":                  Column(int, Check.in_range(1995, 2025), coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), coerce=True),
    },
    strict=True,  # exactement ces 4 colonnes, rien de plus
)


gold_stats_prime_time_schema = DataFrameSchema(
    {
        "year":                  Column(int, Check.in_range(1995, 2025), coerce=True),
        "media_type":            Column(str, Check.isin(["tv", "radio"]), coerce=True),
        "is_prime_time":         Column(bool, coerce=True),
        "female_speech_rate":    Column(float, Check.in_range(0, 1), nullable=True, coerce=True),
        "total_speech_duration": Column(float, Check.ge(0), coerce=True),
    },
    strict=False,
)


gold_themes_evenements_schema = DataFrameSchema(
    {
        "evenement":          Column(str, coerce=True),
        "date_debut":         Column(str, coerce=True),
        "date_fin":           Column(str, coerce=True),
        "rubrique":           Column(str, coerce=True),
        "duree_moy_avant":    Column(float, Check.ge(0), nullable=True, coerce=True),
        "duree_moy_pendant":  Column(float, Check.ge(0), nullable=True, coerce=True),
        "delta_pct":          Column(float, nullable=True, coerce=True),
    },
    strict=False,
)


gold_saisonnalite_schema = DataFrameSchema(
    {
        "mois":                 Column(int, Check.in_range(1, 12), coerce=True),
        "rubrique":             Column(str, coerce=True),
        "nb_sujets":            Column(int, Check.ge(0), coerce=True),
        "duree_totale_sec":     Column(int, Check.ge(0), coerce=True),
        "part_dans_mois":       Column(float, Check.in_range(0, 1), coerce=True),
        "part_annuelle":        Column(float, Check.in_range(0, 1), coerce=True),
        "indice_saisonnalite":  Column(float, Check.ge(0), coerce=True),
    },
    strict=True,
)


gold_parite_ranking_schema = DataFrameSchema(
    {
        "year":                  Column(int, Check.in_range(1995, 2025), coerce=True),
        "media_type":            Column(str, Check.isin(["tv", "radio"]), coerce=True),
        "media_name":            Column(str, coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), coerce=True),
        "rang":                  Column(int, Check.ge(1), coerce=True),
        "nb_medias":             Column(int, Check.ge(1), coerce=True),
        "quartile":              Column(int, Check.in_range(1, 4), coerce=True),
    },
    strict=True,
)


# ─────────────────────────────────────────────
# REGISTRES exposés au pipeline
# ─────────────────────────────────────────────
silver_radio_years_schema = DataFrameSchema(
    {
        "year":                  Column(int, Check.in_range(1995, 2025), coerce=True),
        "station":               Column(str, coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), nullable=True, coerce=True),
    },
    strict=False,
)


silver_tv_years_schema = DataFrameSchema(
    {
        "year":                  Column(int, Check.in_range(1995, 2025), coerce=True),
        "chaine":                Column(str, coerce=True),
        "women_expression_rate": Column(float, Check.in_range(0, 100), nullable=True, coerce=True),
    },
    strict=False,
)


SILVER_SCHEMAS = {
    "ina_jt":      silver_ina_jt_schema,
    "years":       silver_years_schema,
    "stats":       silver_stats_schema,
    "hourstatall": silver_hourstatall_schema,
    "radio_years": silver_radio_years_schema,
    "tv_years":    silver_tv_years_schema,
}

GOLD_SCHEMAS = {
    "tv_theme_parite":   gold_tv_theme_parite_schema,
    "parite_unifiee":    gold_parite_unifiee_schema,
    "stats_prime_time":  gold_stats_prime_time_schema,
    "themes_evenements": gold_themes_evenements_schema,
    "saisonnalite":      gold_saisonnalite_schema,
    "parite_ranking":    gold_parite_ranking_schema,
}
