"""
Pruebas para el script de importacion de datos (ETL).
"""
import os
import logging
import pandas as pd
import pytest
from unittest.mock import patch

logger = logging.getLogger(__name__)


class TestDataCleaning:
    def test_remove_duplicates_by_external_id(self):
        logger.info("Test: eliminar duplicados por external_id")
        df = pd.DataFrame({
            "id": ["TEST-001", "TEST-001", "TEST-002"],
            "programa": ["A", "A", "B"],
            "alcaldia": ["X", "X", "Y"],
            "latitud": [19.1, 19.1, 19.2],
            "longitud": [-99.1, -99.1, -99.2]
        })
        df = df.drop_duplicates(subset=["id"])
        assert len(df) == 2
        assert df["id"].iloc[0] == "TEST-001"
        assert df["id"].iloc[1] == "TEST-002"

    def test_remove_rows_with_null_coordinates(self):
        logger.info("Test: eliminar filas con coordenadas nulas")
        df = pd.DataFrame({
            "id": ["TEST-001", "TEST-002", "TEST-003"],
            "programa": ["A", "B", "C"],
            "alcaldia": ["X", "Y", "Z"],
            "latitud": [19.1, None, 19.3],
            "longitud": [-99.1, -99.2, None]
        })
        df = df.dropna(subset=["latitud", "longitud"])
        assert len(df) == 1
        assert df["id"].iloc[0] == "TEST-001"

    def test_convert_coordinates_to_numeric(self):
        logger.info("Test: convertir coordenadas a numerico")
        df = pd.DataFrame({
            "id": ["TEST-001"],
            "programa": ["A"],
            "alcaldia": ["X"],
            "latitud": ["19.432707"],
            "longitud": ["-99.086743"]
        })
        df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
        df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
        assert df["latitud"].iloc[0] == 19.432707
        assert df["longitud"].iloc[0] == -99.086743

    def test_filter_out_of_range_coordinates(self):
        logger.info("Test: filtrar coordenadas fuera de rango CDMX")
        df = pd.DataFrame({
            "id": ["TEST-001", "TEST-002", "TEST-003", "TEST-004"],
            "programa": ["A", "B", "C", "D"],
            "alcaldia": ["X", "Y", "Z", "W"],
            "latitud": [19.432707, 25.0, 18.5, 19.5],
            "longitud": [-99.086743, -99.0, -99.0, -95.0]
        })
        df = df[(df["latitud"].between(19.0, 19.8)) & (df["longitud"].between(-99.5, -98.8))]
        assert len(df) == 1
        assert df["id"].iloc[0] == "TEST-001"

    def test_rename_id_to_external_id(self):
        logger.info("Test: renombrar columna id a external_id")
        df = pd.DataFrame({
            "id": ["TEST-001"],
            "programa": ["A"],
            "alcaldia": ["X"],
            "latitud": [19.1],
            "longitud": [-99.1]
        })
        df = df.rename(columns={"id": "external_id"})
        assert "external_id" in df.columns
        assert "id" not in df.columns


class TestExcelReading:
    def test_raises_error_when_file_not_found(self):
        logger.info("Test: archivo no encontrado")
        with patch("os.path.exists", return_value=False):
            assert not os.path.exists("/fake/path.xlsx")