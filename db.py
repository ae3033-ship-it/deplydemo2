from pathlib import Path
import csv

DATABASE_DIR = Path(__file__).parent / "database"


def _read_table(name):
    path = DATABASE_DIR / f"{name}.csv"
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_students():
    return _read_table("student")
