"""KPI Airflow via sa base de métadonnées, interrogée en lecture seule avec psql."""
from pathlib import Path
import io
import subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
COMPOSE = ['docker', 'compose', '--env-file', str(ROOT / 'airflow' / '.env'),
           '-f', str(ROOT / 'airflow' / 'docker-compose.yaml')]


def execute_airflow_query(query: str, columns: list[str]) -> pd.DataFrame:
    cmd = COMPOSE + ['exec', '-T', 'postgres', 'psql', '-U', 'airflow', '-d', 'airflow',
                     '-X', '-q', '-t', '-A', '-F', '\t', '-v', 'ON_ERROR_STOP=1', '-c', query]
    try:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                encoding='utf-8', timeout=30, check=True)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('Lecture des métriques Airflow trop longue (>30 s).') from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f'Lecture PostgreSQL Airflow impossible : {exc.stderr.strip()}') from exc
    if not result.stdout.strip():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(io.StringIO(result.stdout), sep='\t', header=None,
                     names=columns, dtype=str, keep_default_na=False)
    return df


def get_dag_metrics() -> dict:
    query = """
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE state = 'success'),
               ROUND(AVG(EXTRACT(EPOCH FROM (end_date - start_date)))
                     FILTER (WHERE state = 'success'), 2)
        FROM dag_run WHERE dag_id = 'checkit_etl'
    """
    df = execute_airflow_query(query, ['total', 'success', 'duration'])
    if df.empty:
        raise RuntimeError('Aucune réponse pour les statistiques du DAG.')
    row = df.iloc[0]
    total = int(row['total'])
    success = int(row['success'])
    duration = float(row['duration']) if row['duration'] else 0.0
    return {'total_runs': total, 'successful_runs': success,
            'success_rate_pct': round(100 * success / total, 2) if total else 0.0,
            'avg_duration_seconds': duration}


def get_task_metrics() -> pd.DataFrame:
    query = """
        SELECT ti.task_id, ti.state,
               ROUND(EXTRACT(EPOCH FROM (ti.end_date - ti.start_date))::numeric, 2)
        FROM task_instance ti
        JOIN dag_run dr ON ti.dag_id = dr.dag_id AND ti.run_id = dr.run_id
        WHERE ti.dag_id = 'checkit_etl'
          AND dr.run_id = (
              SELECT run_id FROM dag_run
              WHERE dag_id = 'checkit_etl' AND state = 'success'
              ORDER BY start_date DESC LIMIT 1)
        ORDER BY ti.start_date
    """
    df = execute_airflow_query(query, ['task_id', 'state', 'duration_seconds'])
    df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce')
    return df
