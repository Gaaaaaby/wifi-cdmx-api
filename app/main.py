"""
Entry point de la aplicacion FastAPI
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app.core.config import config
from app.core.database import init_db, close_all_connections, get_session
from app.api.v1.endpoints import wifi
from app.graphql.schema import schema
from app.middleware import RequestIDMiddleware, ErrorHandlerMiddleware, RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

#Request ID
app.add_middleware(RequestIDMiddleware)

# Error Handler
app.add_middleware(ErrorHandlerMiddleware)

# Limitacion de peticiones por IP
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wifi.router, prefix=f"/api/{config.API_VERSION}")


graphql_app = GraphQLRouter(schema, context_getter=lambda: {"db": get_session()})
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
def startup_event():
    logger.info("Iniciando API WiFi CDMX")
    init_db()
    logger.info(f"REST API: http://localhost:8000/api/{config.API_VERSION}/wifi")
    logger.info(f"GraphQL: http://localhost:8000/graphql")
    logger.info(f"Documentacion: http://localhost:8000/docs")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Apagando API WiFi CDMX")
    close_all_connections()


@app.get("/")
def root():
    return {
        "message": "Bienvenido a la API de Puntos WiFi CDMX",
        "version": "1.0.0",
        "endpoints": {
            "rest": f"/api/{config.API_VERSION}/wifi",
            "graphql": "/graphql",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}