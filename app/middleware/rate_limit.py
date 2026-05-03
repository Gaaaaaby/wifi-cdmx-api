"""
Middleware para Rate Limiting usando algoritmo de Token Bucket.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para limitar el numero de requests por IP.
    Implementa algoritmo Token Bucket.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.requests_limit = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
        self.buckets: Dict[str, Tuple[int, float]] = defaultdict(lambda: (self.requests_limit, time.time()))
        logger.info(f"RateLimitMiddleware inicializado: {self.requests_limit} requests cada {self.window_seconds} segundos")
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente (considerando proxies)
        client_ip = self._get_client_ip(request)
        
        # Verificar rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Demasiadas peticiones. Limite: {self.requests_limit} requests cada {self.window_seconds} segundos"
            )
        
        # Agregar headers de rate limit
        response = await call_next(request)
        remaining, reset = self._get_bucket_status(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP real del cliente considerando proxies"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Verificar si el request esta dentro del limite"""
        now = time.time()
        tokens, last_refill = self.buckets[client_ip]
        
        # Refill tokens basado en tiempo transcurrido
        elapsed = now - last_refill
        refill_tokens = int(elapsed / self.window_seconds) * self.requests_limit
        
        if refill_tokens > 0:
            tokens = min(self.requests_limit, tokens + refill_tokens)
            self.buckets[client_ip] = (tokens, now)
        
        # Consumir un token
        if tokens >= 1:
            self.buckets[client_ip] = (tokens - 1, self.buckets[client_ip][1])
            return True
        
        return False
    
    def _get_bucket_status(self, client_ip: str) -> Tuple[int, int]:
        """Obtener estado actual del bucket (tokens restantes, tiempo de reset)"""
        tokens, last_refill = self.buckets.get(client_ip, (self.requests_limit, time.time()))
        now = time.time()
        elapsed = now - last_refill
        
        if elapsed > self.window_seconds:
            return self.requests_limit, int(now + self.window_seconds)
        
        remaining_tokens = max(0, tokens)
        reset_time = int(last_refill + self.window_seconds)
        
        return remaining_tokens, reset_time