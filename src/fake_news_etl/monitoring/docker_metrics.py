
"""Collecte des métriques instantanées des conteneurs Docker."""

import json
import re
import subprocess

import pandas as pd

def _to_mib(value: str) -> float:
    """Convertit une quantité mémoire Docker en MiB."""
    match = re.fullmatch(
        r"\s*([\d.]+)\s*([KMGT]?i?B|B)\s*",
        value,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Unité mémoire non reconnue : {value}")

    amount = float(match.group(1))
    unit = match.group(2).lower()

    factors = {
        "b": 1 / (1024**2),
        "kb": 1000 / (1024**2),
        "mb": 1000**2 / (1024**2),
        "gb": 1000**3 / (1024**2),
        "tb": 1000**4 / (1024**2),
        "kib": 1 / 1024,
        "mib": 1,
        "gib": 1024,
        "tib": 1024**2,
    }

    return amount * factors[unit]

def _service_name(container: str) -> str:
    """Classe les conteneurs selon leur rôle."""
    name = container.lower()

    if "postgres" in name:
        return "PostgreSQL"
    if "redis" in name:
        return "Redis"
    if "airflow" in name:
        return "Airflow"

    return "Autre"

def get_docker_metrics() -> pd.DataFrame:
    """Retourne CPU et RAM des conteneurs CheckIt.AI."""

    command = [
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "{{json .}}",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=45,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Docker est introuvable. Vérifiez Docker Desktop."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "La collecte des statistiques Docker a expiré."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Impossible de lire les statistiques Docker : {exc.stderr}"
        ) from exc

    rows = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        item = json.loads(line)
        name = item["Name"]

        # Exclut les conteneurs sans rapport avec CheckIt.AI.
        if not (
            name.startswith("airflow-")
            or name.startswith("checkit-")
        ):
            continue

        memory_used = item["MemUsage"].split("/")[0].strip()

        rows.append(
            {
                "conteneur": name,
                "service": _service_name(name),
                "cpu_pct": float(
                    item["CPUPerc"].replace("%", "").strip()
                ),
                "memoire_mib": round(_to_mib(memory_used), 2),
                "memoire_pct": float(
                    item["MemPerc"].replace("%", "").strip()
                ),
            }
        )

    columns = [
        "conteneur",
        "service",
        "cpu_pct",
        "memoire_mib",
        "memoire_pct",
    ]

    return pd.DataFrame(rows, columns=columns)