"""Apply schema.sql and load database/*.csv into the Railway Postgres database."""

from pathlib import Path
import csv
import os
import sys

from dotenv import load_dotenv
import psycopg2

ROOT = Path(__file__).parent
DATABASE_DIR = ROOT / "database"
SCHEMA_PATH = ROOT / "schema.sql"

TABLES = (
    "student",
    "tool",
    "student_tool",
    "time_slot",
    "student_availability",
)


def database_url():
    load_dotenv(ROOT / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is missing from .env")
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


def sql_statements(sql):
    statements = []
    current = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(current).strip()
            if statement and not statement.upper().startswith("INSERT "):
                statements.append(statement)
            current = []
    return statements


def empty_to_none(value):
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def load_csv(name):
    path = DATABASE_DIR / f"{name}.csv"
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def apply_schema(cursor):
    cursor.execute(
        """
        DROP TABLE IF EXISTS student_availability, student_tool, student, tool, time_slot CASCADE;
        DROP TYPE IF EXISTS school_year, intro_programming, day_type, time_period CASCADE;
        """
    )
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    for statement in sql_statements(schema):
        cursor.execute(statement)


def insert_students(cursor, rows):
    cursor.executemany(
        """
        INSERT INTO student (
            id, netid, email, name, school_year, intro_programming,
            skill_programming, skill_data_stats, skill_frontend_design,
            skill_business_pitch, working_style, interests, semester_goal,
            submitted_at
        ) VALUES (
            %(id)s, %(netid)s, %(email)s, %(name)s, %(school_year)s,
            %(intro_programming)s, %(skill_programming)s, %(skill_data_stats)s,
            %(skill_frontend_design)s, %(skill_business_pitch)s,
            %(working_style)s, %(interests)s, %(semester_goal)s, %(submitted_at)s
        )
        """,
        [
            {
                "id": int(row["id"]),
                "netid": row["netid"],
                "email": empty_to_none(row["email"]),
                "name": row["name"],
                "school_year": row["school_year"],
                "intro_programming": row["intro_programming"],
                "skill_programming": int(row["skill_programming"]),
                "skill_data_stats": int(row["skill_data_stats"]),
                "skill_frontend_design": int(row["skill_frontend_design"]),
                "skill_business_pitch": int(row["skill_business_pitch"]),
                "working_style": empty_to_none(row["working_style"]),
                "interests": empty_to_none(row["interests"]),
                "semester_goal": empty_to_none(row["semester_goal"]),
                "submitted_at": row["submitted_at"],
            }
            for row in rows
        ],
    )


def insert_tools(cursor, rows):
    cursor.executemany(
        "INSERT INTO tool (id, name) VALUES (%(id)s, %(name)s)",
        [{"id": int(row["id"]), "name": row["name"]} for row in rows],
    )


def insert_time_slots(cursor, rows):
    cursor.executemany(
        "INSERT INTO time_slot (id, day_type, period) VALUES (%(id)s, %(day_type)s, %(period)s)",
        [
            {
                "id": int(row["id"]),
                "day_type": row["day_type"],
                "period": row["period"],
            }
            for row in rows
        ],
    )


def insert_student_tools(cursor, rows):
    cursor.executemany(
        "INSERT INTO student_tool (student_id, tool_id) VALUES (%(student_id)s, %(tool_id)s)",
        [
            {"student_id": int(row["student_id"]), "tool_id": int(row["tool_id"])}
            for row in rows
        ],
    )


def insert_student_availability(cursor, rows):
    cursor.executemany(
        """
        INSERT INTO student_availability (student_id, time_slot_id)
        VALUES (%(student_id)s, %(time_slot_id)s)
        """,
        [
            {
                "student_id": int(row["student_id"]),
                "time_slot_id": int(row["time_slot_id"]),
            }
            for row in rows
        ],
    )


def reset_sequences(cursor):
    for table in ("student", "tool", "time_slot"):
        cursor.execute(
            """
            SELECT setval(
                pg_get_serial_sequence(%s, 'id'),
                COALESCE((SELECT MAX(id) FROM {table}), 1)
            )
            """.format(table=table),
            (table,),
        )


def main():
    connection = psycopg2.connect(database_url())
    connection.autocommit = False
    try:
        with connection.cursor() as cursor:
            apply_schema(cursor)
            insert_students(cursor, load_csv("student"))
            insert_tools(cursor, load_csv("tool"))
            insert_time_slots(cursor, load_csv("time_slot"))
            insert_student_tools(cursor, load_csv("student_tool"))
            insert_student_availability(cursor, load_csv("student_availability"))
            reset_sequences(cursor)
            counts = {}
            for table in TABLES:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print("Deployed schema and CSV data to Railway.")
    for table, count in counts.items():
        print(f"  {table}: {count} rows")


if __name__ == "__main__":
    main()
