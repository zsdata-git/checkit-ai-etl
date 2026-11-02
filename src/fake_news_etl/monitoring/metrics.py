"""KPI de qualité et distribution des sources depuis la base CheckIt."""
import os
import psycopg
import pandas as pd


def _database_url() -> str:
    url = os.getenv('CHECKIT_DATABASE_URL')
    if not url:
        raise RuntimeError('CHECKIT_DATABASE_URL est absente : vérifier le fichier .env à la racine.')
    return url


def get_quality_metrics() -> dict:
    query = """
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE title IS NOT NULL AND BTRIM(title) <> ''),
               COUNT(*) - COUNT(DISTINCT id),
               COUNT(*) FILTER (WHERE image_url IS NOT NULL AND BTRIM(image_url) <> '')
        FROM articles
    """
    with psycopg.connect(_database_url(), connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            total, titles, duplicates, images = cur.fetchone()
    pct = lambda n: round(100 * n / total, 2) if total else 0.0
    return {
        'total_articles': total,
        'completude_titres_pct': pct(titles),
        'doublons_pct': pct(duplicates),
        'images_url_pct': pct(images),
    }


def get_articles_by_source() -> pd.DataFrame:
    query = """
        SELECT source, COUNT(*) AS nombre_articles
        FROM articles
        GROUP BY source
        ORDER BY nombre_articles DESC
    """
    with psycopg.connect(_database_url(), connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=['source', 'nombre_articles'])
