"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import categorias
from app.api.v2.endpoints import categorias as categorias_v2
from app.api.v2.endpoints import productos as productos_v2

from typing import Annotated, Any
from app.crud import categoria as categoria_crud

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from app.core.database import get_session

import json
from pydantic import BaseModel

# Crear la aplicación FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
app.include_router(categorias_v2.router, prefix="/api/v2/categorias", tags=["categorias_v2"])
app.include_router(productos_v2.router, prefix="/api/v2/productos", tags=["productos_v2"])

@app.get("/")
def read_root(db: Annotated[Session, Depends(get_session)], request: Request):
    """
    Obtener solo categorías raíz activas
    """

    categorias = categoria_crud.get_root_active(db)

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"categorias": categorias}
    )

@app.post("/prueba")
async def prueba(data: list[dict[str, Any]]):
    print("🚀 Data received in /prueba:", data)
    if data:
        for item in data:
            print("Item:", item["name"])
    return {"received": "Ok"}



@app.get("/checkout-form")
async def checkout_form(request: Request):
    """
    Mostrar formulario de datos del usuario y métodos de pago
    """
    return templates.TemplateResponse("checkout_form.html", {"request": request})

@app.post("/api/procesar-checkout")
async def procesar_checkout(request: Request):
    """
    Procesar datos del checkout (datos personales, dirección y carrito)
    """
    try:
        form_data = await request.form()
        
        # Extraer datos del formulario
        checkout_data = {
            "datos_personales": {
                "nombre": form_data.get("nombre"),
                "email": form_data.get("email"),
                "telefono": form_data.get("telefono")
            },
            "direccion": {
                "zona": form_data.get("zona"),
                "barrio": form_data.get("barrio"),
                "tipo_via": form_data.get("tipo_via"),
                "numero_via": form_data.get("numero_via"),
                "numero_casa": form_data.get("numero_casa"),
                "referencias": form_data.get("referencias", "")
            },
            "metodo_pago": form_data.get("metodo_pago"),
            "carrito": json.loads(form_data.get("cart_data", "[]"))
        }
        
        # Calcular total
        total = sum(item['price'] * item['quantity'] for item in checkout_data['carrito'])
        total_items = len(checkout_data['carrito'])
        
        print(f"🛒 Checkout procesado:")
        print(f"   Cliente: {checkout_data['datos_personales']['nombre']}")
        print(f"   Email: {checkout_data['datos_personales']['email']}")
        print(f"   Dirección: {checkout_data['direccion']['tipo_via']} {checkout_data['direccion']['numero_via']} #{checkout_data['direccion']['numero_casa']}, {checkout_data['direccion']['barrio']}")
        print(f"   Pago: {checkout_data['metodo_pago']}")
        print(f"   Total: ${total:.2f} ({total_items} items)")
        
        # Retornar página de éxito
        return templates.TemplateResponse(
            request=request,
            name="checkout_success.html",
            context={
                "cliente": checkout_data['datos_personales'],
                "direccion": checkout_data['direccion'],
                "metodo_pago": checkout_data['metodo_pago'],
                "items": checkout_data['carrito'],
                "total_items": total_items,
                "total": total
            }
        )
        
    except Exception as e:
        print(f"❌ Error en checkout: {e}")
        return templates.TemplateResponse(
            request=request,
            name="checkout_error.html",
            context={"error": str(e)}
        )