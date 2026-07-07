from datetime import datetime
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'etudiant',
    'retries': 0
}


def test_my_db_connection():
    pg_hook = PostgresHook(postgres_conn_id='postgres_projet_conn')

    try:
        connection_status = pg_hook.get_first("SELECT 1;")
        print(f"SUCCÈS : Airflow est BIEN connecté à la base ! Résultat : {connection_status}")
    except Exception as e:
        print(f"ÉCHEC : La connexion a échoué ! Erreur : {e}")
        raise e


with DAG(
        dag_id='aaa_test_connexion_postgres',
        default_args=default_args,
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False
) as dag:
    task_test = PythonOperator(
        task_id='tester_liaison_postgresql',
        python_callable=test_my_db_connection
    )