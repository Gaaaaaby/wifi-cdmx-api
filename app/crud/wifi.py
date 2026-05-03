"""
Operaciones CRUD usando SQLAlchemy.
Todas las funciones devuelven diccionarios, no objetos ORM.
"""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models.wifi import WifiPoint

logger = logging.getLogger(__name__)


def _point_to_dict(point: WifiPoint) -> Dict[str, Any]:
    """Convertir objeto WifiPoint a diccionario (función pura)"""
    if point is None:
        return None
    return {
        "id": point.id,
        "external_id": point.external_id,
        "programa": point.programa,
        "alcaldia": point.alcaldia,
        "latitud": point.latitud,
        "longitud": point.longitud
    }


def _points_to_dicts(points: List[WifiPoint]) -> List[Dict[str, Any]]:
    """Convertir lista de objetos a lista de diccionarios usando map"""
    return list(map(_point_to_dict, points))


def get_all_paginated(db: Session, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """Obtener lista paginada de todos los puntos WiFi"""
    offset = (page - 1) * limit
    
    total = db.query(func.count(WifiPoint.id)).scalar()
    points = db.query(WifiPoint).order_by(WifiPoint.id).offset(offset).limit(limit).all()
    
    return {"total": total, "data": _points_to_dicts(points)}


def get_by_id(db: Session, id: int) -> Optional[Dict[str, Any]]:
    """Obtener un punto WiFi por su ID"""
    point = db.query(WifiPoint).filter(WifiPoint.id == id).first()
    return _point_to_dict(point)


def get_by_external_id(db: Session, external_id: str) -> Optional[Dict[str, Any]]:
    """Obtener un punto WiFi por su ID original"""
    point = db.query(WifiPoint).filter(WifiPoint.external_id == external_id).first()
    return _point_to_dict(point)


def get_by_alcaldia_paginated(db: Session, alcaldia: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """Obtener lista paginada de puntos WiFi por alcaldia"""
    offset = (page - 1) * limit
    
    query = db.query(WifiPoint).filter(WifiPoint.alcaldia.ilike(f"%{alcaldia}%"))
    total = query.count()
    points = query.order_by(WifiPoint.id).offset(offset).limit(limit).all()
    
    return {"total": total, "data": _points_to_dicts(points)}


def get_nearby_paginated(db: Session, lat: float, lng: float, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """
    Obtener puntos WiFi ordenados por proximidad a una coordenada.
    Usa la formula de Haversine.
    """
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        raise ValueError(f"Coordenadas fuera de rango: lat={lat}, lng={lng}")
    
    offset = (page - 1) * limit
    
    haversine = f"""
        6371000 * acos(
            cos(radians({lat})) * cos(radians(latitud)) * cos(radians(longitud) - radians({lng}))
            + sin(radians({lat})) * sin(radians(latitud))
        )
    """
    
    total = db.query(WifiPoint).filter(WifiPoint.latitud.isnot(None)).count()
    
    sql = text(f"""
        SELECT id, external_id, programa, alcaldia, latitud, longitud,
               {haversine} AS distancia
        FROM wifi_points
        WHERE latitud IS NOT NULL
        ORDER BY distancia
        LIMIT :limit OFFSET :offset
    """)
    
    rows = db.execute(sql, {"limit": limit, "offset": offset}).fetchall()
    
    def row_to_dict(row):
        return {
            "id": row[0],
            "external_id": row[1],
            "programa": row[2],
            "alcaldia": row[3],
            "latitud": row[4],
            "longitud": row[5],
            "distancia": round(row[6], 2) if row[6] else None
        }
    
    data = list(map(row_to_dict, rows))
    
    return {"total": total, "data": data}