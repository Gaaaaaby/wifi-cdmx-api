"""
Test simple para verificar que los fixtures funcionan.
"""

import pytest


def test_db_session_works(db_session):
    """Verificar que la sesion de BD funciona"""
    from app.models.wifi import WifiPoint
    
    point = WifiPoint(
        external_id="TEST-FIXTURE",
        programa="Prueba",
        alcaldia="Test",
        latitud=19.43,
        longitud=-99.08
    )
    db_session.add(point)
    db_session.commit()
    
    result = db_session.query(WifiPoint).filter_by(external_id="TEST-FIXTURE").first()
    assert result is not None


def test_client_works(client):
    """Verificar que el cliente HTTP funciona - necesita API corriendo"""
    response = client.get("/health")
    assert response.status_code == 200


def test_sample_points_created(sample_wifi_points):
    """Verificar que los puntos de ejemplo se crearon"""
    assert len(sample_wifi_points) == 4


def test_clean_db_works(clean_db, db_session):
    """Verificar que clean_db limpia la tabla"""
    from app.models.wifi import WifiPoint
    
    count = db_session.query(WifiPoint).count()
    assert count == 0