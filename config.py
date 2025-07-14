import os

# Simple configuration accessor
MODEL_ENSEMBLE = os.getenv("MODEL_ENSEMBLE", "ADVANCED")

def get_db_url():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "quantumvestaidb")
    user = os.getenv("DB_USER", "dbadmin")
    password = os.getenv("DB_PASSWORD", "")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
