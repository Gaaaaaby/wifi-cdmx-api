"""
Middleware para agregar Request ID a cada peticion.
Facilita trazabilidad y debugging.
"""

import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Nombre del header para Request ID
REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que asigna un ID unico a cada request.
    El ID se puede pasar como header o se genera automaticamente.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Obtener Request ID del header o generar uno nuevo
        request_id = request.headers.get(REQUEST_ID_HEADER)
        
        if not request_id:
            request_id = str(uuid.uuid4())
            logger.debug(f"Request ID generado: {request_id}")
        else:
            logger.debug(f"Request ID recibido: {request_id}")
        
        # Agregar request_id al estado del request para acceso en endpoints
        request.state.request_id = request_id
        
        # Crear logger enriquecido para este request
        request_logger = logging.LoggerAdapter(logger, {"request_id": request_id})
        request.state.logger = request_logger
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar Request ID al response header
        response.headers[REQUEST_ID_HEADER] = request_id
        
        return response