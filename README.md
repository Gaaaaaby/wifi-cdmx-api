
# WiFi CDMX API

API REST + GraphQL para consultar puntos de acceso WiFi en la Ciudad de Mexico.

## Stack Tecnologico

- Python 3.10+
- FastAPI - Framework web
- SQLAlchemy - ORM
- PostgreSQL + PostGIS - Base de datos
- Pytest - Tests unitarios
- Strawberry - GraphQL

## Requisitos Previos

- Python 3.10 o superior
- PostgreSQL 16 con PostGIS
- Git

## Instalacion

### 1. Clonar repositorio

```bash
git clone <repo-url>
cd wifi-cdmx-api
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env`:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/wifi-cdmx
EXCEL_PATH=data/wifi-cdmx.xlsx
PAGE_LIMIT_DEFAULT=20
PAGE_LIMIT_MAX=100
```

### 5. Crear base de datos

En pgAdmin o psql:

```sql
CREATE DATABASE "wifi-cdmx";
CREATE EXTENSION postgis;
```

### 6. Crear tablas

```bash
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 7. Importar datos

Colocar archivo `wifi-cdmx.xlsx` en carpeta `data/` y ejecutar:

```bash
python scripts/import_data.py
```

## Ejecutar API

```bash
uvicorn app.main:app --reload
```

La API estara disponible en:
- API REST: `http://localhost:8000/api/v1/wifi`
- GraphQL: `http://localhost:8000/graphql`
- Documentacion Swagger: `http://localhost:8000/docs`

## Endpoints REST

| GET | `/api/v1/wifi/` | Lista paginada de todos los puntos |
| GET | `/api/v1/wifi/{id}` | Punto por ID (autoincremental) |
| GET | `/api/v1/wifi/external/{external_id}` | Punto por ID original del Excel |
| GET | `/api/v1/wifi/alcaldia/{alcaldia}` | Lista paginada por alcaldia |
| GET | `/api/v1/wifi/cercanos/?lat=X&lng=Y` | Puntos ordenados por cercania |

### Ejemplos de respuesta

```json
{
  "total": 35344,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "external_id": "MEX-AIM-AER-AICMT1-M-GW001",
      "programa": "Aeropuerto",
      "alcaldia": "Venustiano Carranza",
      "latitud": 19.432707,
      "longitud": -99.086743
    }
  ]
}
```

## GraphQL

Endpoint: `http://localhost:8000/graphql`

### Queries disponibles

```graphql
# Lista paginada
{
  wifiAll(page: 1, limit: 10) {
    total
    page
    limit
    data { id, externalId, programa, alcaldia }
  }
}

# Por ID
{
  wifiById(id: 1) {
    id
    externalId
    programa
  }
}

# Por alcaldia
{
  wifiByAlcaldia(alcaldia: "Cuauhtemoc", page: 1, limit: 10) {
    total
    data { id, programa }
  }
}

# Puntos cercanos
{
  wifiNearby(lat: 19.432707, lng: -99.086743, page: 1, limit: 10) {
    total
    data { id, programa, distancia }
  }
}
```

## Estructura de Base de Datos

Tabla `wifi_points`:

| id | SERIAL | PK autoincremental |
| external_id | VARCHAR(100) | ID original del Excel |
| programa | VARCHAR(255) | Tipo de punto WiFi |
| alcaldia | VARCHAR(100) | Alcaldia |
| latitud | DOUBLE PRECISION | Latitud |
| longitud | DOUBLE PRECISION | Longitud |
| ubicacion | GEOGRAPHY | Columna espacial PostGIS (autogenerada) |

### Indices

- `idx_alcaldia` - Busqueda por alcaldia
- `idx_external_id` - Busqueda por ID original
- `idx_ubicacion` - Busquedas espaciales (GIST)

## Tests Unitarios

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Ejecutar por modulo

```bash
# Solo CRUD
pytest tests/test_crud.py -v

# Solo API
pytest tests/test_api.py -v

# Solo geolocalizacion
pytest tests/test_geolocation.py -v

# Solo importacion
pytest tests/test_import.py -v
```

### Con cobertura de codigo

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Variables de Entorno

| DATABASE_URL | postgresql://postgres:postgres@localhost:5432/wifi-cdmx | Conexion a BD |
| EXCEL_PATH | data/wifi-cdmx.xlsx | Ruta del archivo Excel |
| PAGE_LIMIT_DEFAULT | 20 | Limite por pagina por defecto |
| PAGE_LIMIT_MAX | 100 | Limite maximo permitido |
