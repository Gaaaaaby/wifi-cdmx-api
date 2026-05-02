"""
Operaciones CRUD usando SQLAlchemy puro con estilo funcional.
Uso de map(), filter() y lambda en lugar de loops imperativos.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models.wifi import WifiPoint

logger = logging.getLogger(__name__)


def _row_to_dict(row):
    """Convertir una fila de BD a diccionario (función pura)"""
    return {
        "id": row[0],
        "external_id": row[1],
        "programa": row[2],
        "alcaldia": row[3],
        "latitud": row[4],
        "longitud": row[5]
    }


def _rows_to_dicts(rows):
    """Convertir múltiples filas usando map (funcional)"""
    return list(map(_row_to_dict, rows))


def get_all_paginated(db: Session, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """Obtener lista paginada de todos los puntos WiFi"""
    offset = (page - 1) * limit
    
    total = db.query(func.count(WifiPoint.id)).scalar()
    rows = db.query(
        WifiPoint.id,
        WifiPoint.external_id,
        WifiPoint.programa,
        WifiPoint.alcaldia,
        WifiPoint.latitud,
        WifiPoint.longitud
    ).order_by(WifiPoint.id).offset(offset).limit(limit).all()
    
    return {"total": total, "data": _rows_to_dicts(rows)}


def get_by_id(db: Session, id: int) -> Optional[WifiPoint]:
    """Obtener un punto WiFi por su ID"""
    result = db.query(WifiPoint).filter(WifiPoint.id == id).first()
    return result


def get_by_external_id(db: Session, external_id: str) -> Optional[WifiPoint]:
    """Obtener un punto WiFi por su ID original"""
    result = db.query(WifiPoint).filter(WifiPoint.external_id == external_id).first()
    return result


def get_by_alcaldia_paginated(db: Session, alcaldia: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """Obtener lista paginada de puntos WiFi por alcaldia"""
    offset = (page - 1) * limit
    
    query = db.query(WifiPoint).filter(WifiPoint.alcaldia.ilike(f"%{alcaldia}%"))
    total = query.count()
    
    rows = query.order_by(WifiPoint.id).offset(offset).limit(limit).all()
    
    # Funcional: convertir objetos ORM a dict usando map y lambda
    data = list(map(lambda p: {
        "id": p.id,
        "external_id": p.external_id,
        "programa": p.programa,
        "alcaldia": p.alcaldia,
        "latitud": p.latitud,
        "longitud": p.longitud
    }, rows))
    
    return {"total": total, "data": data}


def get_nearby_paginated(db: Session, lat: float, lng: float, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """
    Obtener puntos WiFi ordenados por proximidad a una coordenada.
    Usa la formula de Haversine con estilo funcional.
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
    
    # Funcional: map con lambda para construir los diccionarios
    def make_point_with_distance(row):
        return {
            "id": row[0],
            "external_id": row[1],
            "programa": row[2],
            "alcaldia": row[3],
            "latitud": row[4],
            "longitud": row[5],
            "distancia": round(row[6], 2) if row[6] else None
        }
    
    data = list(map(make_point_with_distance, rows))
    
    return {"total": total, "data": data}