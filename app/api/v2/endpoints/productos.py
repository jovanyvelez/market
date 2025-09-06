"""
Endpoints API para Productos
"""

from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.core.database import get_session
from app.crud import producto as producto_crud

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/test", response_class=HTMLResponse)
async def test_productos(
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Endpoint de prueba para verificar productos en la base de datos
    """
    try:
        # Intentar obtener todos los productos activos
        productos_activos = producto_crud.get_activos(db)
        
        return templates.TemplateResponse(
            name="_productos.html", 
            request=request, 
            context={
                "productos": productos_activos[:10],  # Solo los primeros 10
                "total_productos": len(productos_activos), 
                "categorias_hijas": [],
                "termino_busqueda": "TEST",
                "debug_info": f"Total productos activos: {len(productos_activos)}"
            }
        )
    except Exception as e:
        print(f"Error en test_productos: {e}")
        return templates.TemplateResponse(
            name="_productos.html", 
            request=request, 
            context={
                "productos": [], 
                "total_productos": 0, 
                "categorias_hijas": [],
                "termino_busqueda": "TEST",
                "error": f"Error: {str(e)}"
            }
        )


@router.get("/buscar", response_class=HTMLResponse)
async def buscar_productos(
    request: Request,
    db: Annotated[Session, Depends(get_session)],
    q: str = Query("", description="Término de búsqueda")
):
    """
    Buscar productos activos por nombre, código de barras o descripción.
    
    Args:
        q: Término de búsqueda
        db: Sesión de base de datos
        
    Returns:
        HTML con las cards de productos que coinciden con la búsqueda
    """
    termino_limpio = q.strip()
    
    try:
        # Si el término está vacío o es muy corto, no hacer búsqueda
        if len(termino_limpio) < 1:
            return templates.TemplateResponse(
                name="_productos.html", 
                request=request, 
                context={
                    "productos": [], 
                    "total_productos": 0, 
                    "categorias_hijas": [],
                    "termino_busqueda": ""
                }
            )
        
        # Buscar productos que contengan el término en nombre, código o descripción
        productos = producto_crud.buscar_por_termino(db, termino=termino_limpio)

        print(producto for producto in productos)
        
        # No hay categorías hijas en una búsqueda
        categorias_hijas = []
        
        return templates.TemplateResponse(
            name="_productos.html", 
            request=request, 
            context={
                "productos": productos, 
                "total_productos": len(productos), 
                "categorias_hijas": categorias_hijas,
                "termino_busqueda": termino_limpio
            }
        )
    except Exception as e:
        print(f"Error en buscar_productos: {e}")
        return templates.TemplateResponse(
            name="_productos.html", 
            request=request, 
            context={
                "productos": [], 
                "total_productos": 0, 
                "categorias_hijas": [],
                "termino_busqueda": termino_limpio,
                "error": f"Error en la búsqueda: {str(e)}"
            }
        )


@router.get("/activos", response_class=HTMLResponse)
async def listar_productos_activos(
    request: Request,
    db: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Listar todos los productos activos con paginación.
    """
    productos = producto_crud.get_activos(db)
    
    # Aplicar paginación manual
    productos_paginados = productos[skip:skip + limit]
    
    return templates.TemplateResponse(
        name="_productos.html", 
        request=request, 
        context={
            "productos": productos_paginados, 
            "total_productos": len(productos_paginados), 
            "categorias_hijas": []
        }
    )
