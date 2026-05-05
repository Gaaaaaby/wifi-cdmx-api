import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# URL FORZADA (no depende de variable de entorno)
DATABASE_URL = "postgresql://postgres:admin123@db:5432/wifi-cdmx"

logger.info(f"Conectando a base de datos: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Probar la conexion"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Base de datos conectada correctamente")
    except Exception as e:
        logger.error(f"Error de conexion: {e}")
        raise


def get_db():
    """Obtener una sesion (para dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    """Obtener una sesion directa (para GraphQL y scripts)"""
    return SessionLocal()


def close_all_connections():
    """Cerrar todas las conexiones"""
    if engine:
        engine.dispose()
        logger.info("Conexiones cerradas")