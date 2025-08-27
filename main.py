"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends
from src.api.v1.endpoints import categorias
from src.api.v2.endpoints import categorias as categorias_v2


# Importar configuración y base de datos

from src.core.database import get_session
from sqlmodel import Session, select,text

from src.models.models import Categoria
# Importar routers de la API


# Crear la aplicación FastAPI
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
app.include_router(categorias_v2.router, prefix="/api/v2/categorias", tags=["categorias_v2"])
