"""
Prueba de conexion a base de datos real.
"""

import pytest
from app.core.database import init_db


@pytest.mark.skip(reason="Requiere PostgreSQL real corriendo")
def test_real_database_connection():
    """Verificar que la BD real responde"""
    init_db()