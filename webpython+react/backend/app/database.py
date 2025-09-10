from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Migraciones ligeras para SQLite: agregar columnas si faltan
def apply_sqlite_migrations():
    try:
        if not settings.database_url.startswith("sqlite"):
            return
        with engine.connect() as conn:
            # Tabla users: subscription_expires_at
            result = conn.execute("PRAGMA table_info(users)")
            user_cols = [row[1] for row in result]  # name is second column
            if "subscription_expires_at" not in user_cols:
                conn.execute("ALTER TABLE users ADD COLUMN subscription_expires_at DATETIME")

            # Tabla user_keys: duration_days, activated_at
            result = conn.execute("PRAGMA table_info(user_keys)")
            key_cols = [row[1] for row in result]
            if "duration_days" not in key_cols:
                conn.execute("ALTER TABLE user_keys ADD COLUMN duration_days INTEGER DEFAULT 30")
            if "activated_at" not in key_cols:
                conn.execute("ALTER TABLE user_keys ADD COLUMN activated_at DATETIME")
    except Exception as e:
        # Evitar colapsar el arranque por migración fallida; se puede revisar en logs
        print(f"[migrations] Warning applying sqlite migrations: {e}")

# Ejecutar migraciones en import
apply_sqlite_migrations()
