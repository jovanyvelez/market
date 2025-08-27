"""
Configuración general de la aplicación
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    """
    
    # Información del proyecto
    PROJECT_NAME: str = "Market API"
    PROJECT_DESCRIPTION: str = "API para sistema de market con FastAPI y SQLModel"
    VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/market_db"
    
    # Seguridad
    SECRET_KEY: str = "tu-clave-secreta-super-segura-cambia-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Supabase (opcional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "productos"
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
