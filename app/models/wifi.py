"""
Modelo SQLAlchemy para la tabla wifi_points.
"""

from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class WifiPoint(Base):
    """Modelo de punto WiFi"""
    __tablename__ = "wifi_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    programa = Column(String(255), nullable=False)
    alcaldia = Column(String(100), nullable=False, index=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)

    def __repr__(self):
        return f"<WifiPoint(id={self.id}, external_id={self.external_id})>"