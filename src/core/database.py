"""
Configuración de la base de datos para SQLModel
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL no está configurada. "
        "Por favor configura la variable de entorno DATABASE_URL en tu archivo .env"
    )

# Crear el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    #echo=True,  # En producción cambiar a False
    future=True
)


def create_db_and_tables():
    """
    Crear todas las tablas en la base de datos
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos para FastAPI dependency injection
    """
    with Session(engine) as session:
        yield session


# Para usar en development/testing
def get_db_session() -> Session:
    """
    Obtener una sesión de base de datos directa
    """
    return Session(engine)
