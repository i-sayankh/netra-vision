import json
import os

ANALYSES_DIR = "analyses"


def save_analysis(record: dict) -> dict:
    """
    Persist an analysis record to disk, keyed by its id.
    """
    os.makedirs(ANALYSES_DIR, exist_ok=True)
    path = os.path.join(ANALYSES_DIR, f"{record['id']}.json")

    with open(path, "w") as f:
        json.dump(record, f)

    return record


def get_analysis(analysis_id: str) -> dict | None:
    """
    Retrieve a single analysis record by id, or None if it doesn't exist.
    """
    path = os.path.join(ANALYSES_DIR, f"{analysis_id}.json")

    if not os.path.isfile(path):
        return None

    with open(path) as f:
        return json.load(f)


def list_analyses() -> list[dict]:
    """
    Retrieve all analysis records, most recent first.
    """
    if not os.path.isdir(ANALYSES_DIR):
        return []

    records = []
    for name in os.listdir(ANALYSES_DIR):
        if name.endswith(".json"):
            with open(os.path.join(ANALYSES_DIR, name)) as f:
                records.append(json.load(f))

    records.sort(key=lambda r: r["created_at"], reverse=True)
    return records
