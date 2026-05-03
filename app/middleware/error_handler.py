"""
Middleware global para manejo de errores.
Centraliza el logging y formato de respuestas de error.
"""

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from psycopg2 import OperationalError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que captura excepciones no manejadas y retorna respuestas estandar.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        
        except HTTPException as e:
            # Excepciones HTTP (404, 400, etc.) - mantener como estan
            self._log_error(request, e, e.status_code)
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "detail": str(e)}
            )
        
        except IntegrityError as e:
            # Error de integridad de BD (constraint violation, duplicados)
            self._log_error(request, e, 409)
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Conflicto de datos",
                    "detail": "El registro ya existe o viola una restriccion de integridad"
                }
            )
        
        except OperationalError as e:
            # Error de conexion a base de datos
            self._log_error(request, e, 503)
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Servicio no disponible",
                    "detail": "Error de conexion con la base de datos"
                }
            )
        
        except SQLAlchemyError as e:
            # Error de base de datos
            self._log_error(request, e, 500)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error de base de datos",
                    "detail": str(e) if self._is_development() else "Error interno del servidor"
                }
            )
        
        except ValueError as e:
            # Error de validacion
            self._log_error(request, e, 400)
            return JSONResponse(
                status_code=400,
                content={"error": "Error de validacion", "detail": str(e)}
            )
        
        except Exception as e:
            # Error generico no esperado
            self._log_error(request, e, 500, full_traceback=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error interno del servidor",
                    "detail": "Ocurrio un error inesperado"
                }
            )
    
    def _log_error(self, request: Request, error: Exception, status_code: int, full_traceback: bool = False):
        """Loggear error con contexto del request"""
        request_id = getattr(request.state, "request_id", "unknown")
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        
        log_message = (
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Status: {status_code} - IP: {client_ip} - Error: {str(error)}"
        )
        
        if status_code >= 500:
            logger.error(log_message)
            if full_traceback:
                logger.error(traceback.format_exc())
        else:
            logger.warning(log_message)
    
    def _is_development(self) -> bool:
        """Detectar si estamos en entorno de desarrollo"""
        import os
        return os.getenv("ENVIRONMENT", "development") == "development"