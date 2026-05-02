"""
Pruebas de integracion para endpoints de la API.
"""

import logging
import pytest

logger = logging.getLogger(__name__)


class TestGetAllWifi:
    def test_returns_200_ok(self, client):
        logger.info("Test: GET /api/v1/wifi/")
        response = client.get("/api/v1/wifi/")
        assert response.status_code == 200

    def test_returns_paginated_structure(self, client):
        logger.info("Test: estructura paginada")
        response = client.get("/api/v1/wifi/")
        data = response.json()
        assert "total" in data and "page" in data and "limit" in data and "data" in data

    def test_accepts_page_and_limit(self, client):
        logger.info("Test: parametros page y limit")
        response = client.get("/api/v1/wifi/?page=2&limit=5")
        assert response.status_code == 200
        assert response.json()["page"] == 2
        assert response.json()["limit"] == 5

    def test_returns_400_for_invalid_page(self, client):
        logger.info("Test: page=0 da error")
        response = client.get("/api/v1/wifi/?page=0")
        assert response.status_code == 422

    def test_returns_400_for_exceeded_limit(self, client):
        logger.info("Test: limit excedido da error")
        response = client.get("/api/v1/wifi/?limit=1000")
        assert response.status_code == 422


class TestGetWifiById:
    def test_returns_200_for_existing_id(self, client, sample_wifi_points):
        logger.info("Test: GET /api/v1/wifi/{id} existente")
        point_id = sample_wifi_points[0].id
        response = client.get(f"/api/v1/wifi/{point_id}")
        assert response.status_code == 200

    def test_returns_correct_structure(self, client, sample_wifi_points):
        logger.info("Test: estructura de respuesta")
        point_id = sample_wifi_points[0].id
        response = client.get(f"/api/v1/wifi/{point_id}")
        data = response.json()
        required_fields = ["id", "external_id", "programa", "alcaldia", "latitud", "longitud"]
        for field in required_fields:
            assert field in data

    def test_returns_404_for_nonexistent_id(self, client):
        logger.info("Test: ID inexistente da 404")
        response = client.get("/api/v1/wifi/99999")
        assert response.status_code == 404


class TestGetWifiByExternalId:
    def test_returns_200_for_existing_external_id(self, client, sample_wifi_points):
        logger.info("Test: GET /api/v1/wifi/external/{external_id}")
        external_id = sample_wifi_points[0].external_id
        response = client.get(f"/api/v1/wifi/external/{external_id}")
        assert response.status_code == 200

    def test_returns_404_for_nonexistent_external_id(self, client):
        logger.info("Test: external_id inexistente da 404")
        response = client.get("/api/v1/wifi/external/NONEXISTENT")
        assert response.status_code == 404


class TestGetWifiByAlcaldia:
    def test_returns_200_ok(self, client):
        logger.info("Test: GET /api/v1/wifi/alcaldia/{alcaldia}")
        response = client.get("/api/v1/wifi/alcaldia/Cuauhtemoc")
        assert response.status_code == 200

    def test_returns_paginated_structure(self, client):
        logger.info("Test: estructura paginada por alcaldia")
        response = client.get("/api/v1/wifi/alcaldia/Cuauhtemoc")
        data = response.json()
        assert "total" in data and "page" in data and "limit" in data and "data" in data


class TestGetWifiNearby:
    def test_returns_200_with_valid_coordinates(self, client):
        logger.info("Test: GET /api/v1/wifi/cercanos/ con coordenadas validas")
        response = client.get("/api/v1/wifi/cercanos/?lat=19.432707&lng=-99.086743")
        assert response.status_code == 200

    def test_requires_lat_and_lng(self, client):
        logger.info("Test: coordenadas requeridas")
        response_no_lat = client.get("/api/v1/wifi/cercanos/?lng=-99")
        response_no_lng = client.get("/api/v1/wifi/cercanos/?lat=19")
        assert response_no_lat.status_code == 422
        assert response_no_lng.status_code == 422

    def test_returns_400_for_out_of_range_lat(self, client):
        logger.info("Test: lat fuera de rango")
        response = client.get("/api/v1/wifi/cercanos/?lat=200&lng=-99")
        assert response.status_code == 422

    def test_includes_distance(self, client):
        logger.info("Test: respuesta incluye distancia")
        response = client.get("/api/v1/wifi/cercanos/?lat=19.432707&lng=-99.086743")
        data = response.json()
        if data["data"]:
            assert "distancia" in data["data"][0]


class TestHealthCheck:
    def test_returns_200_ok(self, client):
        logger.info("Test: GET /health")
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRoot:
    def test_returns_api_info(self, client):
        logger.info("Test: GET /")
        response = client.get("/")
        data = response.json()
        assert "message" in data and "version" in data and "endpoints" in data