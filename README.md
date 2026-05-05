```markdown
# WiFi CDMX API

API REST + GraphQL para consultar puntos de acceso WiFi en la Ciudad de México.

## Stack

- Python 3.11 + FastAPI
- PostgreSQL + PostGIS
- SQLAlchemy + Pydantic
- Strawberry (GraphQL)
- Docker / Docker Compose
- Pytest

## Requisitos

- Python 3.11+
- Docker y Docker Compose
- Git

## Instalación Rápida

### Con Docker

```bash
# 1. Clonar
git clone <repo-url>
cd wifi-cdmx-api

# 2. Crear carpeta para datos
mkdir -p data
# Copiar wifi-cdmx.xlsx a data/

# 3. Levantar todo
docker-compose up --build
```

### Sin Docker

```bash
# 1. Clonar
git clone <repo-url>
cd wifi-cdmx-api

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo .env
echo "DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/wifi-cdmx" > .env

# 5. Crear BD en PostgreSQL
CREATE DATABASE "wifi-cdmx";
CREATE EXTENSION postgis;

# 6. Crear tablas e importar datos
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
python scripts/import_data.py

# 7. Ejecutar
uvicorn app.main:app --reload
```

## Comandos Principales

| `make dev` | Ejecutar API (modo desarrollo) |
| `make test` | Ejecutar tests |
| `make import` | Importar datos desde Excel |
| `make init-db` | Crear tablas en BD |
| `make clean` | Limpiar archivos temporales |

## Endpoints

| GET | `/api/v1/wifi/` | Lista paginada |
| GET | `/api/v1/wifi/{id}` | Por ID |
| GET | `/api/v1/wifi/external/{id}` | Por ID original |
| GET | `/api/v1/wifi/alcaldia/{alcaldia}` | Por alcaldía |
| GET | `/api/v1/wifi/cercanos/?lat=X&lng=Y` | Por cercanía |

## GraphQL

Endpoint: `/graphql`

```graphql
{
  wifiAll(page: 1, limit: 10) {
    total { id programa alcaldia }
  }
}
```

## Comandos Docker

```bash
docker-compose up --build      # Levantar todo
docker-compose down            # Detener
docker-compose logs -f api     # Ver logs
docker-compose run --rm import # Importar datos
docker-compose exec db psql -U postgres -d wifi-cdmx # Entrar a BD
```
##La API estara en:

http://localhost:8000/docs (Swagger)

http://localhost:8000/graphql (GraphQL)

http://localhost:8000/api/v1/wifi (REST)

## Variables de Entorno

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/wifi-cdmx
EXCEL_PATH=data/wifi-cdmx.xlsx
PAGE_LIMIT_DEFAULT=20
PAGE_LIMIT_MAX=100
```

## Tests

```bash
pytest tests/ -v                    # Todos los tests
pytest tests/test_api.py -v         # Solo API
pytest tests/ --cov=app             # Con cobertura
```

## Solución de Problemas

| `Connection refused` | Verificar que PostgreSQL está corriendo |
| `Password authentication failed` | `ALTER USER postgres WITH PASSWORD 'example_password';` |
| `relation "wifi_points" does not exist` | Ejecutar `make init-db` |
| `ON CONFLICT` error | `ALTER TABLE wifi_points ADD CONSTRAINT unique_external_id UNIQUE (external_id);` |
| `localhost` en Docker | Usar `db` como host en DATABASE_URL |

## Fuente de Datos

Descargar `wifi-cdmx.xlsx` de:
https://datos.cdmx.gob.mx/dataset/puntos-de-acceso-wifi-en-la-cdmx

Colocar en carpeta `data/`

## Licencia

MIT
```
