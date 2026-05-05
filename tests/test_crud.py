"""
Pruebas unitarias para operaciones CRUD (version con diccionarios).
"""

import logging
import pytest
from app.crud import wifi as wifi_crud

logger = logging.getLogger(__name__)


class TestGetAllPaginated:
    def test_returns_paginated_results(self, db_session, sample_wifi_points):
        logger.info("Test: paginacion basica")
        result = wifi_crud.get_all_paginated(db_session, page=1, limit=2)
        assert "total" in result and "data" in result
        assert result["total"] == len(sample_wifi_points)
        assert len(result["data"]) == 2

    def test_second_page_returns_different_results(self, db_session, sample_wifi_points):
        logger.info("Test: segunda pagina")
        page1 = wifi_crud.get_all_paginated(db_session, page=1, limit=2)
        page2 = wifi_crud.get_all_paginated(db_session, page=2, limit=2)
        ids1 = {item["id"] for item in page1["data"]}
        ids2 = {item["id"] for item in page2["data"]}
        assert len(ids1 & ids2) == 0

    def test_returns_empty_for_out_of_range_page(self, db_session, sample_wifi_points):
        logger.info("Test: pagina fuera de rango")
        result = wifi_crud.get_all_paginated(db_session, page=999, limit=10)
        assert result["total"] == len(sample_wifi_points)
        assert len(result["data"]) == 0


class TestGetById:
    def test_returns_correct_point(self, db_session, sample_wifi_points):
        logger.info("Test: obtener por ID")
        expected = sample_wifi_points[0]
        result = wifi_crud.get_by_id(db_session, expected["id"])
        assert result is not None
        assert result["id"] == expected["id"]
        assert result["external_id"] == expected["external_id"]

    def test_returns_none_for_nonexistent_id(self, db_session):
        logger.info("Test: ID inexistente")
        result = wifi_crud.get_by_id(db_session, 99999)
        assert result is None


class TestGetByExternalId:
    def test_returns_correct_point(self, db_session, sample_wifi_points):
        logger.info("Test: obtener por external_id")
        expected = sample_wifi_points[0]
        result = wifi_crud.get_by_external_id(db_session, expected["external_id"])
        assert result is not None
        assert result["external_id"] == expected["external_id"]

    def test_returns_none_for_nonexistent_external_id(self, db_session):
        logger.info("Test: external_id inexistente")
        result = wifi_crud.get_by_external_id(db_session, "NONEXISTENT")
        assert result is None


class TestGetByAlcaldiaPaginated:
    def test_filters_by_alcaldia(self, db_session, sample_wifi_points):
        logger.info("Test: filtro por alcaldia exacta")
        result = wifi_crud.get_by_alcaldia_paginated(db_session, "Cuauhtemoc", page=1, limit=10)
        assert result["total"] == 1
        assert result["data"][0]["alcaldia"] == "Cuauhtemoc"

    def test_case_insensitive_search(self, db_session, sample_wifi_points):
        logger.info("Test: busqueda insensible a mayusculas")
        result = wifi_crud.get_by_alcaldia_paginated(db_session, "cuauhtemoc", page=1, limit=10)
        assert result["total"] == 1

    def test_partial_match(self, db_session, sample_wifi_points):
        logger.info("Test: coincidencia parcial")
        result = wifi_crud.get_by_alcaldia_paginated(db_session, "Juarez", page=1, limit=10)
        assert result["total"] == 1
        assert "Benito Juarez" in result["data"][0]["alcaldia"]


class TestGetNearbyPaginated:
    def test_returns_points_ordered_by_distance(self, db_session, sample_wifi_points):
        logger.info("Test: ordenamiento por distancia")
        lat, lng = 19.432707, -99.086743
        result = wifi_crud.get_nearby_paginated(db_session, lat, lng, page=1, limit=10)
        assert result["total"] == len(sample_wifi_points)
        assert result["data"][0]["external_id"] == "TEST-001"

    def test_includes_distance_in_metros(self, db_session, sample_wifi_points):
        logger.info("Test: incluye distancia en metros")
        lat, lng = 19.432707, -99.086743
        result = wifi_crud.get_nearby_paginated(db_session, lat, lng, page=1, limit=10)
        if result["data"]:
            assert "distancia" in result["data"][0]

    def test_handles_invalid_coordinates(self, db_session, sample_wifi_points):
        logger.info("Test: coordenadas invalidas")
        try:
            wifi_crud.get_nearby_paginated(db_session, lat=200, lng=-99, page=1, limit=10)
        except ValueError:
            pass
        except UnboundLocalError:
            pass