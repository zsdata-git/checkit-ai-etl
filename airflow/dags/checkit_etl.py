from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def verifier_environnement():
    print("CheckIt.AI : environnement Airflow opérationnel.")

def extraire_fakenewsnet():
    from fake_news_etl.extraction.extract_fakenewsnet import extract_fakenewsnet

    extract_fakenewsnet()


def extraire_fakeddit():
    from fake_news_etl.extraction.extract_fakeddit import extract_fakeddit

    extract_fakeddit()


def extraire_newsdata():
    from fake_news_etl.extraction.extract_newsdata import extract_newsdata

    extract_newsdata()

def transformer_donnees():
    from fake_news_etl.transformation.transform_fakenewsnet import run_pipeline as transform_fakenewsnet
    from fake_news_etl.transformation.transform_fakeddit import run_pipeline as transform_fakeddit
    from fake_news_etl.transformation.transform_newsdata import run_pipeline as transform_newsdata
    from fake_news_etl.transformation.merge_sources import run_pipeline as merge_sources

    transform_fakenewsnet()
    transform_fakeddit()
    transform_newsdata()

    merge_sources()

def charger_donnees():
    from fake_news_etl.loading.load_articles import load_articles

    load_articles()

with DAG(
    dag_id="checkit_etl",
    description="Pipeline ETL du projet CheckIt.AI",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["checkit", "etl", "fake-news"],
) as dag:

    verification = PythonOperator(
        task_id="verifier_environnement",
        python_callable=verifier_environnement,
    )

    extraction_fakenewsnet = PythonOperator(
        task_id="extraire_fakenewsnet",
        python_callable=extraire_fakenewsnet,
    )

    extraction_fakeddit = PythonOperator(
        task_id="extraire_fakeddit",
        python_callable=extraire_fakeddit,
    )

    extraction_newsdata = PythonOperator(
        task_id="extraire_newsdata",
        python_callable=extraire_newsdata,
    )

    transformation = PythonOperator(
        task_id="transformer_donnees",
        python_callable=transformer_donnees,
    )

    chargement = PythonOperator(
        task_id="charger_donnees",
        python_callable=charger_donnees,
    )

    verification >> [
        extraction_fakenewsnet,
        extraction_fakeddit,
        extraction_newsdata,
    ]

    [
        extraction_fakenewsnet,
        extraction_fakeddit,
        extraction_newsdata,
    ] >> transformation >> chargement