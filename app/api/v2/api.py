"""
Router principal de la API v2
"""

from fastapi import APIRouter

from app.api.v1.endpoints import categorias

api_router = APIRouter()

# Incluir todas las rutas
api_router.include_router(
    categorias.router,
    prefix="/categorias_v2",
    tags=["Categorías v2"]
)
