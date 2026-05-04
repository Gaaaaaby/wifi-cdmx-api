.PHONY: help run dev test import install clean migrate init-db

PYTHON = python
PIP = pip
UVICORN = uvicorn

GREEN = \033[0;32m
NC = \033[0m

help:
	@echo ""
	@echo "$(GREEN)Comandos disponibles para WiFi CDMX API:$(NC)"
	@echo ""
	@echo "  make run         - Ejecutar la API (produccion)"
	@echo "  make dev         - Ejecutar la API con autorecarga (desarrollo)"
	@echo "  make test        - Ejecutar todos los tests"
	@echo "  make test-cov    - Ejecutar tests con cobertura"
	@echo "  make import      - Importar datos desde Excel a la BD"
	@echo "  make install     - Instalar todas las dependencias"
	@echo "  make clean       - Limpiar archivos temporales"
	@echo "  make init-db     - Crear las tablas en la BD"
	@echo "  make migrate     - Ejecutar migraciones (si usas Alembic)"
	@echo ""

# Ejecutar API en modo produccion
run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

# Ejecutar API en modo desarrollo (con autorecarga)
dev:
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000

# Ejecutar todos los tests
test:
	pytest tests/ -v

# Ejecutar tests con cobertura
test-cov:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Importar datos desde Excel
import:
	$(PYTHON) scripts/import_data.py

# Instalar dependencias
install:
	$(PIP) install -r requirements.txt

# Limpiar archivos temporales
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -f test.db
	rm -f .env.local
	@echo "Archivos temporales eliminados"

# Crear tablas en la base de datos
init-db:
	$(PYTHON) -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine); print('Tablas creadas exitosamente')"

# Migraciones (si instalas Alembic en el futuro)
migrate:
	@echo "Para migraciones, instala Alembic: pip install alembic"
	@echo "Luego ejecuta: alembic revision --autogenerate -m 'migration'"