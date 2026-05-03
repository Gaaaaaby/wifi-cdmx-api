"""
Definicion de las queries y llama a los resolvers.
"""

import strawberry
from strawberry.types import Info
from app.core.database import get_session
from app.graphql.resolvers import (
    resolve_wifi_all,
    resolve_wifi_by_id,
    resolve_wifi_by_external_id,
    resolve_wifi_by_alcaldia,
    resolve_wifi_nearby
)
from app.graphql.types import (
    PaginatedWifiType,
    WifiPointType,
    PaginatedNearbyType
)


def get_db_from_info(info: Info):
    """Extraer la sesion de BD del contexto de GraphQL"""
    return info.context["db"]


@strawberry.type
class Query:
    """Queries disponibles en el esquema GraphQL"""

    @strawberry.field
    def wifi_all(self, info: Info, page: int = 1, limit: int = 20) -> PaginatedWifiType:
        """Obtener todos los puntos WiFi paginados"""
        db = get_db_from_info(info)
        return resolve_wifi_all(db, page, limit)

    @strawberry.field
    def wifi_by_id(self, info: Info, id: int) -> WifiPointType:
        """Obtener un punto WiFi por su ID"""
        db = get_db_from_info(info)
        return resolve_wifi_by_id(db, id)

    @strawberry.field
    def wifi_by_external_id(self, info: Info, external_id: str) -> WifiPointType:
        """Obtener un punto WiFi por su ID original"""
        db = get_db_from_info(info)
        return resolve_wifi_by_external_id(db, external_id)

    @strawberry.field
    def wifi_by_alcaldia(self, info: Info, alcaldia: str, page: int = 1, limit: int = 20) -> PaginatedWifiType:
        """Obtener puntos WiFi por alcaldia paginados"""
        db = get_db_from_info(info)
        return resolve_wifi_by_alcaldia(db, alcaldia, page, limit)

    @strawberry.field
    def wifi_nearby(self, info: Info, lat: float, lng: float, page: int = 1, limit: int = 20) -> PaginatedNearbyType:
        """Obtener puntos WiFi cercanos ordenados por distancia"""
        db = get_db_from_info(info)
        return resolve_wifi_nearby(db, lat, lng, page, limit)


# Esquema principal
schema = strawberry.Schema(query=Query)