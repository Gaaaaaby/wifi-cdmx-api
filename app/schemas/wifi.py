"""
Modelos Pydantic para validacion y serializacion.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List


class WifiPointBase(BaseModel):
    external_id: str = Field(..., description="ID original del punto WiFi")
    programa: str = Field(..., description="Programa o tipo de punto WiFi")
    alcaldia: str = Field(..., description="Alcaldia donde se ubica")
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


class WifiPointResponse(WifiPointBase):
    id: int
    model_config = {"from_attributes": True}


class WifiPointNearbyResponse(WifiPointResponse):
    distancia: Optional[float] = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[Any]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None