"""Tableau de bord de monitoring CheckIt.AI."""
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

from fake_news_etl.monitoring.metrics import get_quality_metrics, get_articles_by_source
from fake_news_etl.monitoring.airflow_metrics import get_dag_metrics, get_task_metrics

from fake_news_etl.monitoring.docker_metrics import get_docker_metrics

st.set_page_config(page_title='CheckIt.AI — Monitoring ETL', page_icon='📊', layout='wide')
st.title('📊 CheckIt.AI — Monitoring du pipeline ETL')
st.caption('Qualité des données et performances des exécutions Airflow.')

if st.button('🔄 Actualiser les indicateurs'):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=120, show_spinner=False)
def quality_data():
    return get_quality_metrics()

@st.cache_data(ttl=120, show_spinner=False)
def source_data():
    return get_articles_by_source()

@st.cache_data(ttl=120, show_spinner=False)
def dag_data():
    return get_dag_metrics()

@st.cache_data(ttl=120, show_spinner=False)
def task_data():
    return get_task_metrics()

st.header('1. Qualité des données')
try:
    with st.spinner('Lecture des indicateurs de qualité…'):
        quality = quality_data()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Articles en base', f"{quality['total_articles']:,}".replace(',', ' '))
    c2.metric('Titres renseignés', f"{quality['completude_titres_pct']:.1f} %")
    c3.metric('Doublons d’identifiant', f"{quality['doublons_pct']:.1f} %")
    c4.metric('Articles avec URL d’image', f"{quality['images_url_pct']:.1f} %")
except Exception as exc:
    st.error(f'KPI de qualité indisponibles : {exc}')

st.divider()
st.header('2. Performance du pipeline Airflow')
try:
    with st.spinner('Lecture des exécutions Airflow…'):
        dag = dag_data()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Exécutions', dag['total_runs'])
    c2.metric('Exécutions réussies', dag['successful_runs'])
    c3.metric('Taux de réussite', f"{dag['success_rate_pct']:.1f} %")
    c4.metric('Durée moyenne (succès)', f"{dag['avg_duration_seconds']:.1f} s")
except Exception as exc:
    st.error(f'KPI Airflow indisponibles : {exc}')

st.divider()
st.header('3. Répartition des articles par source')
try:
    with st.spinner('Lecture de la répartition des sources…'):
        sources = source_data()
    if sources.empty:
        st.info('Aucun article disponible dans la base.')
    else:
        st.bar_chart(sources, x='source', y='nombre_articles', horizontal=True)
        st.dataframe(sources, hide_index=True, use_container_width=True)
except Exception as exc:
    st.error(f'Répartition par source indisponible : {exc}')

st.divider()
st.header('4. Durée des tâches — dernière exécution réussie')
try:
    with st.spinner('Lecture des durées des tâches…'):
        tasks = task_data()
    if tasks.empty:
        st.info('Aucune exécution réussie trouvée.')
    else:
        st.bar_chart(tasks.dropna(subset=['duration_seconds']), x='task_id',
                     y='duration_seconds', horizontal=True)
        st.dataframe(tasks, hide_index=True, use_container_width=True)
except Exception as exc:
    st.error(f'Durées des tâches indisponibles : {exc}')

st.caption('Indicateurs calculés à partir des bases PostgreSQL CheckIt et Airflow. '
           'Les URL d’images sont des références, pas une preuve de disponibilité des images.')



st.divider()
st.header("5. Consommation des ressources Docker")

st.caption(
    "Suivi du coût technique de l'infrastructure : "
    "utilisation CPU et mémoire des conteneurs."
)

try:
    with st.spinner("Lecture des statistiques Docker..."):
        docker_df = get_docker_metrics()

    if docker_df.empty:
        st.info(
            "Aucun conteneur CheckIt.AI actif n'a été trouvé."
        )
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Conteneurs actifs",
            len(docker_df),
        )

        col2.metric(
            "CPU cumulé",
            f"{docker_df['cpu_pct'].sum():.1f} %",
        )

        col3.metric(
            "Mémoire totale utilisée",
            f"{docker_df['memoire_mib'].sum():,.0f} MiB",
        )

        st.subheader("Utilisation du CPU par conteneur")

        st.bar_chart(
            docker_df.set_index("conteneur")["cpu_pct"],
            horizontal=True,
        )

        st.subheader("Mémoire utilisée par conteneur")

        st.bar_chart(
            docker_df.set_index("conteneur")["memoire_mib"],
            horizontal=True,
        )

        st.subheader("Répartition des ressources par service")

        resources_by_service = (
            docker_df.groupby("service", as_index=False)
            .agg(
                cpu_pct=("cpu_pct", "sum"),
                memoire_mib=("memoire_mib", "sum"),
            )
        )

        st.dataframe(
            resources_by_service,
            hide_index=True,
            width="stretch",
        )

        st.subheader("Détail des conteneurs")

        st.dataframe(
            docker_df,
            hide_index=True,
            width="stretch",
        )

except Exception as exc:
    st.warning(
        "Les statistiques Docker sont indisponibles. "
        f"Détail : {exc}"
    )

st.caption(
    "Méthodologie : mesures instantanées obtenues avec "
    "'docker stats --no-stream'. Le CPU peut dépasser 100 % "
    "sur plusieurs cœurs. Les valeurs représentent "
    "l'infrastructure active, et non le coût total "
    "d'une exécution ETL. Les pourcentages CPU cumulés "
    "ne représentent pas un taux global d'utilisation."
)