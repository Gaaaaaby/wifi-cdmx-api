"""
Pruebas para calculos de geolocalizacion con formula harvesine
"""

import logging
import math
import pytest

logger = logging.getLogger(__name__)

'''Harvesine es una formula que calcula la distancia real entre 2 puntos en una esfera
Funcionamiento de la formula: convierte grados a radianes- 
calcula la diferencia entre las 2 coordenadas - aplica senos y cosenos -
multiplica por 6,371 (radio de la tierra en mtros)
'''

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class TestHaversineFormula:
    def test_distance_from_point_to_itself_is_zero(self):
        logger.info("Test: distancia punto a si mismo es cero")
        lat, lng = 19.432707, -99.086743
        assert haversine(lat, lng, lat, lng) == 0

    def test_distance_between_two_known_points(self):
        logger.info("Test: distancia entre Aeropuerto y Zocalo")
        lat1, lng1 = 19.432707, -99.086743
        lat2, lng2 = 19.432926, -99.133148
        distance = haversine(lat1, lng1, lat2, lng2)
        assert 4500 < distance < 5500

    def test_distance_is_symmetric(self):
        logger.info("Test: distancia simetrica")
        lat1, lng1 = 19.432707, -99.086743
        lat2, lng2 = 19.380000, -99.160000
        assert haversine(lat1, lng1, lat2, lng2) == haversine(lat2, lng2, lat1, lng1)


class TestCoordinateValidation:
    def test_valid_latitude_range(self):
        logger.info("Test: rango valido de latitud")
        # Una latitud valida debe estar entre -90 y 90
        assert -90 <= 19.432707 <= 90
        # Una latitud invalida esta fuera de ese rango
        assert not (-90 <= 200 <= 90)

    def test_valid_longitude_range(self):
        logger.info("Test: rango valido de longitud")
        assert -180 <= -99.086743 <= 180
        assert not (-180 <= 200 <= 180)

    def test_cdmx_bounding_box(self):
        logger.info("Test: coordenadas dentro de CDMX")
        # Coordenada dentro de CDMX (Aeropuerto)
        lat, lng = 19.432707, -99.086743
        assert 19.0 <= lat <= 19.8
        assert -99.5 <= lng <= -98.8
        
        # Coordenada fuera de CDMX
        lat, lng = 25.0, -99.0
        assert not (19.0 <= lat <= 19.8) or not (-99.5 <= lng <= -98.8)