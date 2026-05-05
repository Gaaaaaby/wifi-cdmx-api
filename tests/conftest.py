"""
Fixtures compartidos para todos los tests.
"""

import logging
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app
from app.models.wifi import WifiPoint 

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEST_DATABASE_URL = "sqlite:///./test.db?check_same_thread=False"


@pytest.fixture(scope="session")
def engine():
    """Engine de BD para pruebas"""
    logger.info("Creando engine de tests")
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas correctamente")
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    logger.info("Engine de tests destruido")


@pytest.fixture(scope="function")
def db_session(engine):
    """Sesion de BD aislada por test"""
    logger.info("Iniciando sesion de test")
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    logger.info("Sesion de test cerrada")


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente HTTP con override de BD"""
    logger.info("Configurando cliente HTTP")
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    logger.info("Cliente HTTP liberado")


@pytest.fixture(scope="function")
def sample_wifi_points(db_session):
    """Datos de ejemplo (devuelve diccionarios)"""
    logger.info("Creando datos de ejemplo")
    points_data = [
        {"external_id": "TEST-001", "programa": "Aeropuerto", "alcaldia": "Venustiano Carranza", "latitud": 19.432707, "longitud": -99.086743},
        {"external_id": "TEST-002", "programa": "Metrobus", "alcaldia": "Cuauhtemoc", "latitud": 19.432000, "longitud": -99.150000},
        {"external_id": "TEST-003", "programa": "Pilar", "alcaldia": "Iztapalapa", "latitud": 19.360000, "longitud": -99.090000},
        {"external_id": "TEST-004", "programa": "Escuela", "alcaldia": "Benito Juarez", "latitud": 19.380000, "longitud": -99.160000},
    ]
    
    points = []
    for data in points_data:
        point = WifiPoint(**data)
        db_session.add(point)
        points.append(point)
    db_session.commit()
    
    result = []
    for p in points:
        result.append({
            "id": p.id,
            "external_id": p.external_id,
            "programa": p.programa,
            "alcaldia": p.alcaldia,
            "latitud": p.latitud,
            "longitud": p.longitud
        })
    return result


@pytest.fixture(scope="function")
def clean_db(db_session):
    """Limpia la tabla antes de cada test"""
    logger.info("Limpiando tabla wifi_points")
    db_session.execute(text("DELETE FROM wifi_points"))
    db_session.commit()
    return db_session