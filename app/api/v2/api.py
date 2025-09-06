"""
Router principal de la API v2
"""

from fastapi import APIRouter

from app.api.v2.endpoints import categorias, productos

api_router = APIRouter()

# Incluir todas las rutas
api_router.include_router(
    categorias.router,
    prefix="/categorias",
    tags=["Categorías v2"]
)

api_router.include_router(
    productos.router,
    prefix="/productos",
    tags=["Productos v2"]
)
