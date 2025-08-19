"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from typing import Annotated
from fastapi import FastAPI, Depends
from app.api.v1.endpoints import categorias


# Importar configuración y base de datos

from app.core.database import get_session
from sqlmodel import Session, select,text

from app.models.models import Categoria
# Importar routers de la API


# Crear la aplicación FastAPI
app = FastAPI()

app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
