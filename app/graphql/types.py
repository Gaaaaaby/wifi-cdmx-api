"""
Define los tipos de datos que se retornaran de las consultas GraphQL.
flujo: 
Schema recibe query → Llama al Resolver → 
Resolver llama a CRUD → CRUD devuelve dict → 
Resolver convierte dict a Type → Schema devuelve Type

"""

import strawberry
from typing import Optional, List


@strawberry.type
class WifiPointType:
    """Tipo GraphQL para un punto WiFi"""
    id: int
    external_id: str
    programa: str
    alcaldia: str
    latitud: float
    longitud: float
@strawberry.type
class WifiPointNearbyType:
    """Tipo GraphQL para punto WiFi con distancia"""
    id: int
    external_id: str
    programa: str
    alcaldia: str
    latitud: float
    longitud: float
    distancia: Optional[float]
@strawberry.type
class PaginatedWifiType:
    """Tipo GraphQL para respuesta paginada"""
    total: int
    page: int
    limit: int
    data: List[WifiPointType]
@strawberry.type
class PaginatedNearbyType:
    """Tipo GraphQL para respuesta paginada con distancias"""
    total: int
    page: int
    limit: int
    data: List[WifiPointNearbyType]