"""
Configuracion central de la aplicacion usando Pydantic BaseSettings.
Valida tipos y carga automaticamente desde .env.
"""

import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuracion de la aplicacion.
    Las variables se cargan automaticamente desde .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/wifi-cdmx",
        description="URL de conexion a PostgreSQL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, ge=1, le=50, description="Tamaño del pool de conexiones")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100, description="Maximo de conexiones extras")
    DATABASE_ECHO: bool = Field(default=False, description="Loggear todas las queries SQL")
    

    API_TITLE: str = Field(default="WiFi CDMX API", description="Titulo de la API")
    API_DESCRIPTION: str = Field(
        default="API para consultar puntos de acceso WiFi en la Ciudad de Mexico",
        description="Descripcion de la API"
    )
    API_VERSION: str = Field(default="v1", description="Version de la API")
    API_PREFIX: str = Field(default="/api/v1", description="Prefijo para endpoints REST")
    

    
    PAGE_LIMIT_DEFAULT: int = Field(default=20, ge=1, le=1000, description="Limite por pagina por defecto")
    PAGE_LIMIT_MAX: int = Field(default=100, ge=1, le=1000, description="Limite maximo permitido")
    

    
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, description="Numero maximo de requests por ventana")
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=1, description="Ventana de tiempo en segundos")
    CORS_ALLOWED_ORIGINS: list = Field(default=["*"], description="Origenes permitidos para CORS")
    

    
    EXCEL_PATH: str = Field(default="data/wifi-cdmx.xlsx", description="Ruta del archivo Excel con datos")
    BATCH_SIZE: int = Field(default=1000, ge=100, le=10000, description="Tamaño de batch para importacion")
    
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validar que la URL de la base de datos sea correcta"""
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL debe comenzar con postgresql://")
        if "localhost" not in v and "127.0.0.1" not in v and "@db" not in v:
            logger.warning(f"Base de datos remota detectada: {v.split('@')[1] if '@' in v else 'unknown'}")
        return v
    
    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list:
        """Convertir string de origenes separados por coma a lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    

    def get_database_dsn(self) -> str:
        """Retorna el DSN para psycopg2 (sin async)"""
        return self.DATABASE_URL
    
    def get_pagination_limit(self, requested_limit: int) -> int:
        """Retorna el limite de paginacion validado"""
        if requested_limit < 1:
            return self.PAGE_LIMIT_DEFAULT
        return min(requested_limit, self.PAGE_LIMIT_MAX)


# Instancia global de configuracion
try:
    settings = Settings()
    logger.info("Configuracion cargada correctamente")
    
    # Ocultar contraseña en logs
    safe_url = settings.DATABASE_URL
    if "@" in safe_url:
        parts = safe_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            if len(user_pass) == 2:
                safe_url = f"{user_pass[0]}:***@{parts[1]}"
    logger.info(f"Database: {safe_url}")
    
except Exception as e:
    logger.error(f"Error al cargar configuracion: {e}")
    raise


# Mantener compatibilidad con codigo existente
config = settings