#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os
import time

from sqlalchemy import create_engine, text

url = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://rednote:rednote@mysql:3306/rednote",
)

for attempt in range(30):
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready")
        break
    except Exception as exc:
        print(f"Waiting for DB ({attempt + 1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database not available after retries")
PY

echo "Running migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
