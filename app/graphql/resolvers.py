"""
Conversion de datos que vienen de la BDD (dicts, objetos) a tipo GraphQL.
"""

import logging
from sqlalchemy.orm import Session
from app.crud import wifi as wifi_crud
from app.graphql.types import (
    WifiPointType,
    WifiPointNearbyType,
    PaginatedWifiType,
    PaginatedNearbyType
)

logger = logging.getLogger(__name__)


def _dict_to_wifi_type(item: dict) -> WifiPointType:
    """Convertir dict a tipo GraphQL (funcion pura)"""
    if item is None:
        return None
    return WifiPointType(
        id=item["id"],
        external_id=item["external_id"],
        programa=item["programa"],
        alcaldia=item["alcaldia"],
        latitud=item["latitud"],
        longitud=item["longitud"]
    )


def _dict_to_nearby_type(item: dict) -> WifiPointNearbyType:
    """Convertir dict con distancia a tipo GraphQL"""
    return WifiPointNearbyType(
        id=item["id"],
        external_id=item["external_id"],
        programa=item["programa"],
        alcaldia=item["alcaldia"],
        latitud=item["latitud"],
        longitud=item["longitud"],
        distancia=item.get("distancia")
    )


def resolve_wifi_all(db: Session, page: int = 1, limit: int = 20) -> PaginatedWifiType:
    """Resolver para obtener todos los puntos WiFi paginados"""
    logger.info(f"GraphQL: wifi_all(page={page}, limit={limit})")
    result = wifi_crud.get_all_paginated(db, page, limit)
    
    data = [_dict_to_wifi_type(item) for item in result["data"]]
    
    return PaginatedWifiType(
        total=result["total"],
        page=page,
        limit=limit,
        data=data
    )


def resolve_wifi_by_id(db: Session, id: int) -> WifiPointType:
    """Resolver para obtener un punto por ID"""
    logger.info(f"GraphQL: wifi_by_id(id={id})")
    result = wifi_crud.get_by_id(db, id)
    if not result:
        return None
    return _dict_to_wifi_type(result)


def resolve_wifi_by_external_id(db: Session, external_id: str) -> WifiPointType:
    """Resolver para obtener un punto por external_id"""
    logger.info(f"GraphQL: wifi_by_external_id(external_id={external_id})")
    result = wifi_crud.get_by_external_id(db, external_id)
    if not result:
        return None
    return _dict_to_wifi_type(result)


def resolve_wifi_by_alcaldia(db: Session, alcaldia: str, page: int = 1, limit: int = 20) -> PaginatedWifiType:
    """Resolver para obtener puntos por alcaldia paginados"""
    logger.info(f"GraphQL: wifi_by_alcaldia(alcaldia={alcaldia}, page={page}, limit={limit})")
    result = wifi_crud.get_by_alcaldia_paginated(db, alcaldia, page, limit)
    
    data = [_dict_to_wifi_type(item) for item in result["data"]]
    
    return PaginatedWifiType(
        total=result["total"],
        page=page,
        limit=limit,
        data=data
    )


def resolve_wifi_nearby(db: Session, lat: float, lng: float, page: int = 1, limit: int = 20) -> PaginatedNearbyType:
    """Resolver para obtener puntos cercanos ordenados por distancia"""
    logger.info(f"GraphQL: wifi_nearby(lat={lat}, lng={lng}, page={page}, limit={limit})")
    result = wifi_crud.get_nearby_paginated(db, lat, lng, page, limit)
    
    data = [_dict_to_nearby_type(item) for item in result["data"]]
    
    return PaginatedNearbyType(
        total=result["total"],
        page=page,
        limit=limit,
        data=data
    )