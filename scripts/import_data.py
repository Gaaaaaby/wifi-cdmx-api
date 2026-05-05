"""
Script ETL para cargar datos de puntos WiFi desde Excel a PostgreSQL, 
se hace validacion, conversion, eliminado de duplicados y transformacion de ciertos datos para luego subirlos a la BDD
"""

import os
import sys
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EXCEL_PATH = os.getenv("EXCEL_PATH", "data/wifi-cdmx.xlsx")
BATCH_SIZE = 1000


def get_connection():
    """Obtener conexion a PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)


def is_valid_coordinate(lat, lng) -> bool:
    """Validar coordenada"""
    if lat is None or lng is None:
        return False
    try:
        lat_f = float(lat)
        lng_f = float(lng)
        return (19.0 <= lat_f <= 19.8) and (-99.5 <= lng_f <= -98.8)
    except (ValueError, TypeError):
        return False


def row_to_tuple(row) -> tuple:
    """Convertir fila de DataFrame para inserccion"""
    return (
        row["external_id"],
        row["programa"],
        row["alcaldia"],
        float(row["latitud"]),
        float(row["longitud"])
    )


def clean_dataframe(df):
    """Limpiar y transformar datos"""
    logger.info(f"Registros originales: {len(df)}")
    
    # Renombrar columna id -> external_id
    df = df.rename(columns={"id": "external_id"})
    
    # Filtrar filas con coordenadas válidas 
    df = df[df.apply(lambda row: is_valid_coordinate(row["latitud"], row["longitud"]), axis=1)]
    
    # Eliminar duplicados
    df = df.drop_duplicates(subset=["external_id"])
    
    # Convertir coordenadas a numérico
    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    
    logger.info(f"Registros validos: {len(df)}")
    return df


def insert_data(df):
    """Inserccion de datos ya transformados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    data = list(map(row_to_tuple, df.to_dict('records')))
    
    insert_sql = """
        INSERT INTO wifi_points (external_id, programa, alcaldia, latitud, longitud)
        VALUES %s
        ON CONFLICT (external_id) DO UPDATE SET
            programa = EXCLUDED.programa,
            alcaldia = EXCLUDED.alcaldia,
            latitud = EXCLUDED.latitud,
            longitud = EXCLUDED.longitud
    """
    
    total = len(data)
    for i in range(0, total, BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]
        execute_values(cursor, insert_sql, batch)
        processed = min(i + len(batch), total)
        logger.info(f"Insertados {len(batch)} registros ({processed}/{total})")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"Total insertados/actualizados: {total}")


def main():
    """Ejecucion principal"""
    logger.info("=== Iniciando importacion de datos WiFi CDMX ===")
    
    if not os.path.exists(EXCEL_PATH):
        logger.error(f"No se encuentra el archivo: {EXCEL_PATH}")
        sys.exit(1)
    
    try:
        df = pd.read_excel(EXCEL_PATH)
        df_clean = clean_dataframe(df)
        insert_data(df_clean)
        logger.info("Importacion completada exitosamente")
    except Exception as e:
        logger.error(f"Error durante la importacion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()