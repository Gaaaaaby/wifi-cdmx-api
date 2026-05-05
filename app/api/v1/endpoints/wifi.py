"""
Endpoints REST (Obtencion de todos los puntos de wifi, Obtencion por ID, Obtencion por id_externo(id por default), Obtencion de wifi por alcaldia,
obtencion de puntos de wifi cercanos x coordenadas).
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import config
from app.models.wifi import WifiPoint
from app.crud import wifi as wifi_crud
from app.schemas.wifi import WifiPointResponse, WifiPointNearbyResponse, PaginatedResponse, ErrorResponse

router = APIRouter(prefix="/wifi", tags=["WiFi CDMX"])


def validate_pagination(page: int, limit: int):
    if page < 1:
        raise HTTPException(status_code=400, detail="page debe ser mayor o igual a 1")
    if limit < 1 or limit > config.PAGE_LIMIT_MAX:
        raise HTTPException(status_code=400, detail=f"limit debe estar entre 1 y {config.PAGE_LIMIT_MAX}")
    return page, limit


@router.get("/", response_model=PaginatedResponse)
def get_all_wifi(
    page: int = Query(1, ge=1),
    limit: int = Query(config.PAGE_LIMIT_DEFAULT, ge=1, le=config.PAGE_LIMIT_MAX),
    db: Session = Depends(get_db)
):
    page, limit = validate_pagination(page, limit)
    result = wifi_crud.get_all_paginated(db, page, limit)
    return PaginatedResponse(
        total=result["total"],
        page=page,
        limit=limit,
        data=[WifiPointResponse.model_validate(item) for item in result["data"]]
    )


@router.get("/{id}", response_model=WifiPointResponse, responses={404: {"model": ErrorResponse}})
def get_wifi_by_id(id: int, db: Session = Depends(get_db)):
    result = wifi_crud.get_by_id(db, id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Punto WiFi con ID {id} no encontrado")
    return WifiPointResponse.model_validate(result)


@router.get("/external/{external_id}", response_model=WifiPointResponse, responses={404: {"model": ErrorResponse}})
def get_wifi_by_external_id(external_id: str, db: Session = Depends(get_db)):
    result = wifi_crud.get_by_external_id(db, external_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Punto WiFi con external_id {external_id} no encontrado")
    return WifiPointResponse.model_validate(result)


@router.get("/alcaldia/{alcaldia}", response_model=PaginatedResponse)
def get_wifi_by_alcaldia(
    alcaldia: str,
    page: int = Query(1, ge=1),
    limit: int = Query(config.PAGE_LIMIT_DEFAULT, ge=1, le=config.PAGE_LIMIT_MAX),
    db: Session = Depends(get_db)
):
    page, limit = validate_pagination(page, limit)
    result = wifi_crud.get_by_alcaldia_paginated(db, alcaldia, page, limit)
    return PaginatedResponse(
        total=result["total"],
        page=page,
        limit=limit,
        data=[WifiPointResponse.model_validate(item) for item in result["data"]]
    )


@router.get("/cercanos/", response_model=PaginatedResponse)
def get_wifi_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    page: int = Query(1, ge=1),
    limit: int = Query(config.PAGE_LIMIT_DEFAULT, ge=1, le=config.PAGE_LIMIT_MAX),
    db: Session = Depends(get_db)
):
    page, limit = validate_pagination(page, limit)
    result = wifi_crud.get_nearby_paginated(db, lat, lng, page, limit)
    return PaginatedResponse(
        total=result["total"],
        page=page,
        limit=limit,
        data=[WifiPointNearbyResponse(**item) for item in result["data"]]
    )