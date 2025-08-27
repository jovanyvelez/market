"""
Esquemas de respuesta para categorías y productos
"""

from typing import List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel


class ProductoDescendienteSchema(BaseModel):
    """Esquema simplificado para productos descendientes"""
    id: int
    nombre: str
    precio: float
    stock: int
    activo: bool
    categoria: str
    
    class Config:
        from_attributes = True


class CategoriaHijaSchema(BaseModel):
    """Esquema para categorías hijas"""
    id: int
    nombre: str
    
    class Config:
        from_attributes = True


class ProductosDescendientesResponse(BaseModel):
    """Respuesta para obtener productos de una categoría y sus descendientes"""
    categoria_padre_id: int
    productos: List[Dict[str, Any]]
    total_productos: int
    categorias_hijas: List[CategoriaHijaSchema]
    
    class Config:
        from_attributes = True
