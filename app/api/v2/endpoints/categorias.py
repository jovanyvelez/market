"""
Endpoints API para Categorías
"""
import json
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, text

from app.core.database import get_session
from app.crud import categoria as categoria_crud
from app.models import CategoriaCreate, CategoriaRead, CategoriaUpdate
from pydantic import BaseModel

class CategoriaProductosRequest(BaseModel):
    padre: int

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


def get_data_descendants_products(categoria_id: int, db: Session, solo_activos: bool = True) -> dict:
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

    hijas = categoria_crud.get_categorias_hijas(
        db,
        categoria_id=categoria_id,
        solo_activos=solo_activos
    )

    return {"productos": productos, "categorias_hijas": hijas}

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


    # Obtener productos de la categoría y sus descendientes
    data = get_data_descendants_products(categoria_id=categoria_id, db=db, solo_activos=solo_activos)

    productos = data["productos"]
    
    
    # Obtener categorías hijas directas
    categorias_hijas_data =  data["categorias_hijas"]
    
    # Convertir a objetos del schema
    categorias_hijas = [CategoriaHijaSchema(**categoria) for categoria in categorias_hijas_data]

    return templates.TemplateResponse(name="_productos.html", request=request, context={"padre": None, "categoria_padre_id": categoria_id, "productos": productos, "total_productos": len(productos), "categorias_hijas": categorias_hijas})

@router.post("/{categoria_id}/productos", response_class=HTMLResponse)
def obtener_productos_descendientes_post(
    db: Annotated[Session, Depends(get_session)],
    request: Request,
    categoria_id: int, 
    padre: int = Form(...),
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
 
    # Obtener productos de la categoría y sus descendientes
    data = get_data_descendants_products(categoria_id=categoria_id, db=db, solo_activos=solo_activos)

    productos = data["productos"]
    
    
    # Obtener categorías hijas directas
    categorias_hijas_data =  data["categorias_hijas"]
    
    # Convertir a objetos del schema
    categorias_hijas = [CategoriaHijaSchema(**categoria) for categoria in categorias_hijas_data]

    return templates.TemplateResponse(name="_productos.html", request=request, context={"padre": padre,"categoria_padre_id": categoria_id, "productos": productos, "total_productos": len(productos), "categorias_hijas": categorias_hijas})

@router.get("/productos/{producto_id}/detalle", response_class=HTMLResponse)
def obtener_detalle_producto(
    request: Request,
    producto_id: int,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Obtener el detalle de un producto específico (solo vista informativa)
    """
    # Usar consulta SQL directa
    statement = text("""
        SELECT p.id, p.nombre, p.descripcion, p.precio_venta, 
               p.imagen_url, p.categoria_id, p.codigo_barras,
               c.nombre as categoria_nombre
        FROM producto p
        LEFT JOIN categoria c ON p.categoria_id = c.id
        WHERE p.id = :producto_id
    """)
    
    result = db.execute(statement, {"producto_id": producto_id}).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Convertir el resultado a dict para el template
    producto_data = {
        "id": result.id,
        "nombre": result.nombre,
        "descripcion": result.descripcion,
        "precio_venta": result.precio_venta,
        "imagen_url": result.imagen_url,
        "codigo_barras": result.codigo_barras,
        "categoria_id": result.categoria_id,
        "categoria_nombre": result.categoria_nombre or "Sin categoría"
    }

    return templates.TemplateResponse(
        name="detalle_producto.html", 
        request=request, 
        context={
            "producto": producto_data,
            "categoria_nombre": producto_data["categoria_nombre"]
        }
    )


# ============================================================================
# ENDPOINTS PARA FORMULARIO DEL CARRITO
# ============================================================================

@router.post("/carrito/increase/{product_id}", response_class=HTMLResponse)
async def aumentar_cantidad_carrito(
    product_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Aumentar cantidad de un producto en el carrito (para botón +)
    """
    # Obtener carrito de session o cookie temporal
    # Por ahora vamos a devolver el carrito vacío como placeholder
    return templates.TemplateResponse(
        name="_carrito.html", 
        request=request, 
        context={
            "cart_items": [],
            "total": 0.00,
            "is_empty": True
        }
    )


@router.post("/carrito/decrease/{product_id}", response_class=HTMLResponse)
async def disminuir_cantidad_carrito(
    product_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Disminuir cantidad de un producto en el carrito (para botón -)
    """
    # Obtener carrito de session o cookie temporal
    # Por ahora vamos a devolver el carrito vacío como placeholder
    return templates.TemplateResponse(
        name="_carrito.html", 
        request=request, 
        context={
            "cart_items": [],
            "total": 0.00,
            "is_empty": True
        }
    )


@router.post("/carrito/update/{product_id}", response_class=HTMLResponse)
async def actualizar_cantidad_carrito(
    product_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Actualizar cantidad específica de un producto en el carrito (input number)
    """
    # Obtener nueva cantidad del form data
    form_data = await request.form()
    # Procesar actualización...
    # Por ahora vamos a devolver el carrito vacío como placeholder
    return templates.TemplateResponse(
        name="_carrito.html", 
        request=request, 
        context={
            "cart_items": [],
            "total": 0.00,
            "is_empty": True
        }
    )


@router.post("/carrito/remove/{product_id}", response_class=HTMLResponse)
async def eliminar_producto_carrito(
    product_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Eliminar un producto del carrito
    """
    # Procesar eliminación...
    # Por ahora vamos a devolver el carrito vacío como placeholder
    return templates.TemplateResponse(
        name="_carrito.html", 
        request=request, 
        context={
            "cart_items": [],
            "total": 0.00,
            "is_empty": True
        }
    )


@router.post("/carrito/checkout", response_class=HTMLResponse)
async def procesar_checkout(
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """
    Procesar la compra final del carrito (submit del formulario)
    """
    try:
        print("=== INICIANDO CHECKOUT ===")
        
        # Obtener datos del formulario
        form_data = await request.form()
        print(f"Form data recibido: {dict(form_data)}")
        
        # Procesar items del carrito desde el formulario
        cart_items = []
        item_index = 0
        
        while f"items[{item_index}][id]" in form_data:
            item = {
                "id": int(form_data[f"items[{item_index}][id]"]),
                "name": form_data[f"items[{item_index}][name]"],
                "price": float(form_data[f"items[{item_index}][price]"]),
                "quantity": int(form_data[f"items[{item_index}][quantity]"])
            }
            cart_items.append(item)
            print(f"Item procesado: {item}")
            item_index += 1
        
        if not cart_items:
            print("No hay items en el carrito")
            return templates.TemplateResponse(
                name="_carrito.html", 
                request=request, 
                context={
                    "cart_items": [],
                    "total": 0.00,
                    "is_empty": True,
                    "error": "No hay productos en el carrito"
                }
            )
        
        # Validar productos contra la base de datos y calcular total
        validated_items = []
        total = 0.00
        
        for item in cart_items:
            print(f"Validando producto ID: {item['id']}")
            
            # Verificar que el producto existe y está activo
            statement = text("""
                SELECT id, nombre, precio_venta, stock_actual, activo
                FROM producto 
                WHERE id = :producto_id AND activo = true
            """)
            
            result = db.execute(statement, {"producto_id": item['id']}).first()
            
            if not result:
                print(f"Producto ID {item['id']} no encontrado o inactivo")
                continue
                
            # Verificar stock disponible
            if result.stock_actual < item['quantity']:
                print(f"Stock insuficiente para {result.nombre}. Disponible: {result.stock_actual}, Solicitado: {item['quantity']}")
                # Por ahora continuamos, pero en producción podrías manejar esto diferente
                available_quantity = max(0, int(result.stock_actual))
                if available_quantity == 0:
                    continue
                item['quantity'] = available_quantity
            
            # Usar precio actual de la base de datos
            actual_price = float(result.precio_venta)
            item_total = actual_price * item['quantity']
            total += item_total
            
            validated_items.append({
                "id": result.id,
                "name": result.nombre,
                "price": actual_price,
                "quantity": item['quantity'],
                "item_total": item_total
            })
            
            print(f"Item validado: {result.nombre} - Cantidad: {item['quantity']} - Total: ${item_total:.2f}")
        
        if not validated_items:
            print("No hay items válidos después de la validación")
            return templates.TemplateResponse(
                name="_carrito.html", 
                request=request, 
                context={
                    "cart_items": [],
                    "total": 0.00,
                    "is_empty": True,
                    "error": "No hay productos válidos en el carrito"
                }
            )
        
        print(f"=== CHECKOUT EXITOSO ===")
        print(f"Total de items: {len(validated_items)}")
        print(f"Total a pagar: ${total:.2f}")
        
        # TODO: Aquí implementarías:
        # - Reducir stock de productos
        # - Crear registro de pedido
        # - Procesar pago
        # - Enviar confirmación por email
        
        # Obtener timestamp actual
        from datetime import datetime
        now = datetime.now()
        
        # Devolver página de éxito completa
        print("Devolviendo página de éxito completa...")
        return templates.TemplateResponse(
            name="checkout_success.html", 
            request=request, 
            context={
                "success_message": f"¡Compra procesada exitosamente! Total: ${total:.2f}",
                "order_total": total,
                "items_purchased": len(validated_items),
                "now": now
            }
        )
        
    except Exception as e:
        print(f"Error en checkout: {str(e)}")
        return templates.TemplateResponse(
            name="_carrito.html", 
            request=request, 
            context={
                "cart_items": [],
                "total": 0.00,
                "is_empty": True,
                "error": f"Error procesando la compra: {str(e)}"
            }
        )
