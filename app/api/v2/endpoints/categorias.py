"""
Endpoints API para Categorías
"""

from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, text

from app.core.database import get_session
from app.crud import categoria as categoria_crud
from app.models import CategoriaCreate, CategoriaRead, CategoriaUpdate

templates = Jinja2Templates(directory="app/templates")


from app.schemas.categoria_schemas import ProductosDescendientesResponse, CategoriaHijaSchema

router = APIRouter()


@router.get("/", response_model=list[CategoriaRead])
def listar_categorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    """
    Obtener lista de categorías
    """
    categorias = categoria_crud.get_multi(db, skip=skip, limit=limit)
    return categorias

@router.get("/raiz_activas", response_class=HTMLResponse)
async def listar_categorias_raiz_activas(db: Annotated[Session, Depends(get_session)], request: Request):
    """
    Obtener solo categorías raíz activas
    """
    categorias = categoria_crud.get_root_active(db)
    return templates.TemplateResponse(request=request, name="_categorias.html", context = {"categorias": categorias})

@router.get("/activas", response_model=List[CategoriaRead])
def listar_categorias_activas(db: Session = Depends(get_session)):
    """
    Obtener solo categorías activas
    """
    categorias = categoria_crud.get_activas(db)
    return categorias


@router.get("/buscar_vista", response_class=HTMLResponse)
async def mostrar_vista_buscar(request: Request):
    """
    Mostrar la vista de búsqueda con la navbar de búsqueda
    """
    return templates.TemplateResponse(
        name="_buscar.html", 
        request=request, 
        context={}
    )


@router.get("/carrito", response_class=HTMLResponse)
async def mostrar_carrito_vacio(request: Request):
    """
    Mostrar la vista del carrito vacío
    """
    return templates.TemplateResponse(
        name="_carrito.html", 
        request=request, 
        context={
            "cart_items": [],
            "total": 0.00,
            "is_empty": True
        }
    )


@router.post("/carrito", response_class=HTMLResponse)
async def mostrar_carrito_con_datos(
    request: Request,
    cart_data: dict,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Mostrar la vista del carrito con los productos enviados desde el frontend
    """
    try:
        cart_items = cart_data.get("items", [])
        
        if not cart_items:
            return templates.TemplateResponse(
                name="_carrito.html", 
                request=request, 
                context={
                    "cart_items": [],
                    "total": 0.00,
                    "is_empty": True
                }
            )
        
        # Procesar los items del carrito y calcular el total
        processed_items = []
        total = 0.00
        
        for item in cart_items:
            item_total = float(item.get("price", 0)) * int(item.get("quantity", 0))
            total += item_total
            
            processed_item = {
                "id": item.get("id"),
                "name": item.get("name", "Producto"),
                "price": float(item.get("price", 0)),
                "quantity": int(item.get("quantity", 0)),
                "imageUrl": item.get("imageUrl") if item.get("imageUrl") and item.get("imageUrl").strip() != '' else None,
                "item_total": item_total
            }
            processed_items.append(processed_item)
        
        return templates.TemplateResponse(
            name="_carrito.html", 
            request=request, 
            context={
                "cart_items": processed_items,
                "total": total,
                "is_empty": False
            }
        )
        
    except Exception as e:
        print(f"Error procesando carrito: {e}")
        return templates.TemplateResponse(
            name="_carrito.html", 
            request=request, 
            context={
                "cart_items": [],
                "total": 0.00,
                "is_empty": True,
                "error": "Error al cargar el carrito"
            }
        )


@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_session)):
    """
    Obtener una categoría por ID
    """
    categoria = categoria_crud.get(db, id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return categoria


@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    categoria_in: CategoriaCreate,
    db: Session = Depends(get_session)
):
    """
    Crear una nueva categoría
    """
    # Verificar si ya existe una categoría con ese nombre
    categoria_existente = categoria_crud.get_by_nombre(db, nombre=categoria_in.nombre)
    if categoria_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre"
        )
    
    categoria = categoria_crud.create(db, obj_in=categoria_in)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    db: Session = Depends(get_session)
):
    """
    Actualizar una categoría existente
    """
    categoria = categoria_crud.get(db, id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    # Si se está cambiando el nombre, verificar que no exista
    if categoria_in.nombre and categoria_in.nombre != categoria.nombre:
        categoria_existente = categoria_crud.get_by_nombre(db, nombre=categoria_in.nombre)
        if categoria_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )
    
    categoria = categoria_crud.update(db, db_obj=categoria, obj_in=categoria_in)
    return categoria


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_session)):
    """
    Eliminar una categoría
    """
    categoria = categoria_crud.get(db, id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    categoria_crud.remove(db, id=categoria_id)
    return {"message": "Categoría eliminada exitosamente"}


@router.patch("/{categoria_id}/activar", response_model=CategoriaRead)
def activar_categoria(categoria_id: int, db: Session = Depends(get_session)):
    """
    Activar una categoría
    """
    categoria = categoria_crud.activar(db, categoria_id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return categoria


@router.patch("/{categoria_id}/desactivar", response_model=CategoriaRead)
def desactivar_categoria(categoria_id: int, db: Session = Depends(get_session)):
    """
    Desactivar una categoría
    """
    categoria = categoria_crud.desactivar(db, categoria_id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return categoria


@router.get("/producto/{producto_id}/detalle", response_class=HTMLResponse)
async def mostrar_detalle_producto(
    request: Request,
    producto_id: int,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Mostrar el detalle completo de un producto específico
    """
    try:
        # Consulta para obtener el producto con toda su información
        query = text("""
        SELECT 
            p.id,
            p.nombre,
            p.descripcion,
            p.precio_venta as precio,
            p.stock_actual as stock,
            p.imagen_url,
            p.activo,
            c.nombre as categoria_nombre
        FROM producto p
        LEFT JOIN categoria c ON p.categoria_id = c.id
        WHERE p.id = :producto_id AND p.activo = true
        """)
        
        result = db.execute(query, {"producto_id": producto_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        producto = {
            "id": result.id,
            "nombre": result.nombre,
            "descripcion": result.descripcion or "Sin descripción disponible",
            "precio": float(result.precio) if result.precio else 0.0,
            "stock": result.stock,
            "imagen_url": result.imagen_url,
            "activo": result.activo,
            "categoria_nombre": result.categoria_nombre or "Sin categoría"
        }
        
        return templates.TemplateResponse(
            name="detalle_producto.html", 
            request=request, 
            context={"producto": producto}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error obteniendo detalle del producto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{categoria_id}/productos", response_class=HTMLResponse)
def obtener_productos_descendientes(
    request: Request,
    categoria_id: int, 
    db: Annotated[Session, Depends(get_session)],
    solo_activos: bool = True
):
    """
    Obtener todos los productos de una categoría específica y sus categorías descendientes.
    Por defecto solo incluye categorías y productos activos.
    
    Args:
        categoria_id: ID de la categoría padre
        solo_activos: Si True, solo devuelve categorías y productos activos (default: True)
        db: Sesión de base de datos
        
    Returns:
        Lista de productos de la categoría padre y todas sus subcategorías descendientes activas
    """
    # Verificar que la categoría existe
    categoria = categoria_crud.get(db, id=categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    # Obtener productos de la categoría y sus descendientes
    productos = categoria_crud.get_productos_descendientes(
        db, 
        categoria_id=categoria_id, 
        solo_activos=solo_activos
    )
    
    # Obtener categorías hijas directas
    categorias_hijas_data = categoria_crud.get_categorias_hijas(
        db,
        categoria_id=categoria_id,
        solo_activos=solo_activos
    )
    
    # Convertir a objetos del schema
    categorias_hijas = [CategoriaHijaSchema(**categoria) for categoria in categorias_hijas_data]

    return templates.TemplateResponse(name="_productos.html", request=request, context={"categoria_padre_id": categoria_id, "productos": productos, "total_productos": len(productos), "categorias_hijas": categorias_hijas})
