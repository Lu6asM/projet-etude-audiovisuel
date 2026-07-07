from datetime import datetime
import os
import re
import requests
import pandas as pd
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import text

default_args = {
    'owner': 'etudiant',
    'retries': 1
}

DATA_DIR = "/opt/airflow/data"

SOURCES_CONFIG = {
    "barometre_jt": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/9c90780e-7975-4b29-8ece-e2d3f07ac308",
        "filename": "ina_barometre_jt.csv"
    },
    "stats_brutes_volumineux": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/db598503-d6e5-4e89-8214-167bd239d9e9",
        "filename": "20190308_stats_brutes.csv"
    },
    "years_global": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/c5b54a7f-2eb2-4db4-a6c5-3b603a56bf29",
        "filename": "20190308_years.csv"
    },
    "hourstatall": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/2d752a77-15d9-46ab-86b4-8a20477593fc",
        "filename": "20190308_hourstatall.csv"
    },
    "radio_years": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/4ac77400-054c-4a81-a770-f8e719400c78",
        "filename": "20190308_radio_years.csv"
    },
    "tv_years": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/5f4a8e22-7599-4789-bf60-7cf7df9a8e70",
        "filename": "20190308_tv_years.csv"
    },
    "parole_genreprogramme": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/cb2f0bb0-59e3-48ff-9382-0e7f47adaa91",
        "filename": "ina_csa_parole_femmes_genreprogramme.csv"
    },
    "parole_chaines": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/756365eb-a8ae-42b1-8345-76fda5dde110",
        "filename": "ina_csa_parole_femmes_chaines.csv"
    }
}


def download_source(source_key):
    config = SOURCES_CONFIG[source_key]
    os.makedirs(DATA_DIR, exist_ok=True)
    local_path = os.path.join(DATA_DIR, config["filename"])

    print(f"Téléchargement en cours depuis : {config['url']}")
    response = requests.get(config["url"], stream=True)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"Fichier sauvegardé avec succès dans {local_path}")
    else:
        raise Exception(f"Erreur HTTP {response.status_code} sur la source {source_key}")


def pipeline_barometre_jt():
    csv_path = os.path.join(DATA_DIR, SOURCES_CONFIG["barometre_jt"]["filename"])

    df = pd.read_csv(csv_path, sep=';', encoding='latin1',
                     names=['date_str', 'channel_name', 'clipping', 'theme', 'nb_sujets', 'duree'])

    df['date_pure'] = pd.to_datetime(df['date_str'], format='%d/%m/%Y')
    df['date_id'] = df['date_pure'].dt.strftime('%Y%m%d').astype(int)

    pg_hook = PostgresHook(postgres_conn_id='postgres_projet_conn')
    engine = pg_hook.get_sqlalchemy_engine()

    themes = df[['theme']].dropna().drop_duplicates().rename(columns={'theme': 'nom_categorie'})
    themes['type_categorie'] = 'Theme JT'

    query_theme = text(
        "INSERT INTO dim_themes_genres (nom_categorie, type_categorie) VALUES (:nom, :type) ON CONFLICT (nom_categorie) DO NOTHING;")
    with engine.connect() as conn:
        with conn.begin():
            for _, row in themes.iterrows():
                conn.execute(query_theme, {"nom": row['nom_categorie'], "type": row['type_categorie']})

    medias = df[['channel_name']].dropna().drop_duplicates()
    query_media = text(
        "INSERT INTO dim_medias (channel_name, media_type, is_public_channel) VALUES (:channel, 'tv', TRUE) ON CONFLICT (channel_name) DO NOTHING;")
    with engine.connect() as conn:
        with conn.begin():
            for _, row in medias.iterrows():
                conn.execute(query_media, {"channel": row['channel_name']})

    dim_themes = pd.read_sql(
        "SELECT categorie_id, nom_categorie FROM dim_themes_genres WHERE type_categorie='Theme JT'", engine)
    dim_medias = pd.read_sql("SELECT media_id, channel_name FROM dim_medias", engine)

    df = df.merge(dim_themes, left_on='theme', right_on='nom_categorie', how='inner')
    df = df.merge(dim_medias, on='channel_name', how='inner')

    fait_df = df[['date_id', 'media_id', 'categorie_id', 'nb_sujets', 'duree']].rename(
        columns={'duree': 'duree_sujets_secondes'}
    )

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("TRUNCATE TABLE fait_themes_diffusion;"))

    fait_df.to_sql('fait_themes_diffusion', con=engine, if_exists='append', index=False)
    print(f"Baromètre JT intégré avec succès ({len(fait_df)} lignes injectées).")


def pipeline_stats_brutes():
    csv_path = os.path.join(DATA_DIR, SOURCES_CONFIG["stats_brutes_volumineux"]["filename"])

    pg_hook = PostgresHook(postgres_conn_id='postgres_projet_conn')
    engine = pg_hook.get_sqlalchemy_engine()

    print("Analyse et synchronisation des médias...")
    df_medias_bruts = pd.read_csv(
        csv_path,
        sep=',',
        encoding='utf-8',
        usecols=['channel_name', 'media_type', 'is_public_channel']
    ).drop_duplicates()

    df_medias_bruts['channel_name'] = df_medias_bruts['channel_name'].str.strip()

    query_media_brute = text(
        "INSERT INTO dim_medias (channel_name, media_type, is_public_channel) "
        "VALUES (:channel, :type, :public) ON CONFLICT (channel_name) DO NOTHING;"
    )

    with engine.connect() as conn:
        with conn.begin():
            for _, row in df_medias_bruts.iterrows():
                conn.execute(query_media_brute, {
                    "channel": row['channel_name'],
                    "type": row['media_type'],
                    "public": row['is_public_channel']
                })

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("TRUNCATE TABLE fait_parole_analyse_horaire;"))

    dim_medias = pd.read_sql("SELECT media_id, channel_name FROM dim_medias", engine)

    dim_medias['channel_name_clean'] = dim_medias['channel_name'].str.lower().str.strip()
    dim_medias_merge = dim_medias[['media_id', 'channel_name_clean']]

    chunk_count = 0
    for chunk in pd.read_csv(csv_path, sep=',', encoding='utf-8', chunksize=50000):
        chunk_count += 1

        chunk['date_pure'] = pd.to_datetime(chunk['date'], format='%Y-%m-%d')
        chunk['date_id'] = chunk['date_pure'].dt.strftime('%Y%m%d').astype(int)

        chunk = chunk[chunk['date_id'] >= 20010101]

        chunk['channel_name_clean'] = chunk['channel_name'].str.lower().str.strip()

        chunk = chunk.merge(dim_medias_merge, on='channel_name_clean', how='inner')

        fait_chunk = chunk[
            ['date_id', 'media_id', 'hour', 'male_duration', 'female_duration', 'music_duration']
        ].rename(columns={'hour': 'heure_diffusion'})

        if not fait_chunk.empty:
            fait_chunk.to_sql('fait_parole_analyse_horaire', con=engine, if_exists='append', index=False)
            print(f"Chunk {chunk_count} traité : {len(fait_chunk)} lignes injectées.")
        else:
            print(f"Attention : Le Chunk {chunk_count} a fini vide après la jointure !")



def pipeline_genre_programme():
    csv_path = os.path.join(DATA_DIR, SOURCES_CONFIG["parole_genreprogramme"]["filename"])
    df = pd.read_csv(csv_path, sep=',', encoding='utf-8')

    pg_hook = PostgresHook(postgres_conn_id='postgres_projet_conn')
    engine = pg_hook.get_sqlalchemy_engine()

    genres = df[['genre']].dropna().drop_duplicates().rename(columns={'genre': 'nom_categorie'})
    genres['type_categorie'] = 'Genre Programme'

    query_genre = text(
        "INSERT INTO dim_themes_genres (nom_categorie, type_categorie) VALUES (:nom, :type) ON CONFLICT (nom_categorie) DO NOTHING;")
    with engine.connect() as conn:
        with conn.begin():
            for _, row in genres.iterrows():
                conn.execute(query_genre, {"nom": row['nom_categorie'], "type": row['type_categorie']})

    dim_genres = pd.read_sql(
        "SELECT categorie_id, nom_categorie FROM dim_themes_genres WHERE type_categorie='Genre Programme'", engine)
    df = df.merge(dim_genres, left_on='genre', right_on='nom_categorie', how='inner')

    colonnes_durations = [col for col in df.columns if re.search(r'_\d{4}$', col)]
    annees_presentes = sorted(list(set(col.split('_')[-1] for col in colonnes_durations)))

    liste_faits = []
    for year in annees_presentes:
        if f'nb_declarations_{year}' in df.columns:
            df_year = pd.DataFrame()
            df_year['categorie_id'] = df['categorie_id']
            df_year['annee'] = int(year)
            df_year['nb_declarations'] = df[f'nb_declarations_{year}']
            df_year['total_declarations_duration'] = df[f'total_declarations_duration_{year}']
            df_year['women_speech_duration'] = df[f'women_speech_duration_{year}']
            df_year['men_speech_duration'] = df[f'men_speech_duration_{year}']
            df_year['other_duration'] = df[f'other_duration_{year}']

            liste_faits.append(df_year)

    if liste_faits:
        fait_df_final = pd.concat(liste_faits, ignore_index=True)

        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("TRUNCATE TABLE fait_parole_annuelle_genre;"))

        fait_df_final.to_sql('fait_parole_annuelle_genre', con=engine, if_exists='append', index=False)
        print(f"Données par genres intégrées dynamiquement pour les années : {annees_presentes}")



with DAG(
        dag_id='pipeline_audiovisuel_dynamique',
        default_args=default_args,
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False
) as dag:
    download_tasks = {}
    for key in SOURCES_CONFIG.keys():
        download_tasks[key] = PythonOperator(
            task_id=f'download_{key}',
            python_callable=download_source,
            op_kwargs={'source_key': key}
        )

    task_load_jt = PythonOperator(
        task_id='load_barometre_jt_to_postgres',
        python_callable=pipeline_barometre_jt
    )

    task_load_brute = PythonOperator(
        task_id='load_stats_brutes_horaires_to_postgres',
        python_callable=pipeline_stats_brutes
    )

    task_load_genre = PythonOperator(
        task_id='load_genre_programme_to_postgres',
        python_callable=pipeline_genre_programme
    )

    download_tasks["barometre_jt"] >> task_load_jt
    download_tasks["stats_brutes_volumineux"] >> task_load_brute
    download_tasks["parole_genreprogramme"] >> task_load_genre