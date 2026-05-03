"""
Conexion a PostgreSQL con SQLAlchemy puro.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/wifi-cdmx"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Probar la conexion"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Base de datos conectada correctamente")
    except Exception as e:
        logger.error(f"Error de conexion: {e}")
        raise


def get_db():
    """Obtener una sesion (dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_session():
    """Obtener una sesion directa (para scripts y GraphQL)"""
    return SessionLocal()

def close_all_connections() -> None:
    """Cerrar conexiones"""
    if engine:
        engine.dispose()
        logger.info("Conexiones cerradas")