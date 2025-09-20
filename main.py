"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import categorias
from app.api.v2.endpoints import categorias as categorias_v2
from app.api.v2.endpoints import productos as productos_v2

from typing import Annotated
from app.crud import categoria as categoria_crud

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from app.core.database import get_session

import json
from pydantic import BaseModel


# Opcional: modelo para cuando se usan forms
class DatosForm(BaseModel):
    datos: str  # Los datos vendrán como string JSON


# Crear la aplicación FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
app.include_router(categorias_v2.router, prefix="/api/v2/categorias", tags=["categorias_v2"])
app.include_router(productos_v2.router, prefix="/api/v2/productos", tags=["productos_v2"])


def categorias_root(db: Session):
    """
    Obtener solo categorías raíz activas
    """
    return categoria_crud.get_root_active(db)


@app.get("/")
def read_root(db: Annotated[Session, Depends(get_session)], request: Request):
    """
    Obtener solo categorías raíz activas
    """
    items = request.cookies.get("items")
    if items:
        print("Cart items from cookies:", items)
    categorias = categorias_root(db)
    total_items = 0
    total = 0
    cart_items = []
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"categorias": categorias, "total_items": total_items,
                  "total": total,
                  "items": cart_items}
    )

# Endpoint para procesar el carrito de compras
@app.post("/procesar-carrito")
async def procesar_carrito(request: Request, response: Response):
    print("🚀 Ingreso a /procesar-carrito")
    try:
        # Intentar primero leer como JSON (para hx-vals)
        try:
            json_data = await request.json()
            lista_data = json_data.get("lista", [])
        except:
            # Si falla, intentar leer como form data (compatibilidad hacia atrás)
            form_data = await request.form()
            lista_str = form_data.get("lista")
            if lista_str:
                # Convertir a string si es UploadFile
                if hasattr(lista_str, 'read'):
                    lista_str = str(await lista_str.read(), 'utf-8')
                elif not isinstance(lista_str, str):
                    lista_str = str(lista_str)
                lista_data = json.loads(lista_str)
            else:
                lista_data = []

        cart_items = lista_data

        if not cart_items:
            return templates.TemplateResponse(
                request=request,
                name="checkout_empty_partial.html",
                context={}
            )

        # Calcular total
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        total_items = len(cart_items)
        categorias = []
        response.set_cookie(key="usuario", value="john_doe")
        response.set_cookie(key="tipo", value="admin")
        #return RedirectResponse(url="/")
        return templates.TemplateResponse(
            request=request,
            #name="checkout_success_partial.html",
            name="index.html",
            context={
                "categorias": categorias, 
                "total_items": total_items,
                "total": total,
                "items": cart_items
            }
        )

    except json.JSONDecodeError:
        return templates.TemplateResponse(
            request=request,
            name="checkout_error_partial.html",
            context={
                "error_title": "Error de formato",
                "error_message": "Error procesando los datos del carrito."
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="checkout_error_partial.html",
            context={
                "error_title": "Error interno",
                "error_message": str(e)
            }
        )

