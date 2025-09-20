"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
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

@app.get("/")
def read_root(db: Annotated[Session, Depends(get_session)], request: Request):
    """
    Obtener solo categorías raíz activas
    """
    categorias = categoria_crud.get_root_active(db)
    return templates.TemplateResponse(request=request, name="index.html", context = {"categorias": categorias})



# Modelo para los items de la lista
class Item(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int
    categoria: str | None = None

# Modelo para la lista completa
class ListaItems(BaseModel):
    items: list[Item]
    total: float
    timestamp: str

@app.get("/test", response_class=HTMLResponse)
async def get_main_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.7/dist/htmx.min.js" integrity="sha384-ZBXiYtYQ6hJ2Y0ZNoYuI+Nq5MqWBr+chMrS/RkXpNzQCApHEhOt2aY8EJgqwHLkJ" crossorigin="anonymous"></script>
        <script>
            // Variable global con lista de objetos
            window.miListaGlobal = {
                items: [
                    { id: 1, nombre: "Laptop", precio: 999.99, cantidad: 2, categoria: "electrónica" },
                    { id: 2, nombre: "Mouse", precio: 25.50, cantidad: 5, categoria: "accesorios" },
                    { id: 3, nombre: "Teclado", precio: 75.00, cantidad: 3, categoria: "accesorios" },
                    { id: 4, nombre: "Monitor", precio: 299.99, cantidad: 1, categoria: "electrónica" }
                ],
                total: 999.99 * 2 + 25.50 * 5 + 75.00 * 3 + 299.99 * 1,
                timestamp: new Date().toISOString()
            };
            
            // Función para actualizar antes de enviar
            function actualizarLista() {
                window.miListaGlobal.timestamp = new Date().toISOString();
                // Recalcular total
                window.miListaGlobal.total = window.miListaGlobal.items.reduce(
                    (sum, item) => sum + (item.precio * item.cantidad), 0
                );
            }
            
            // Función para agregar nuevo item
            function agregarItem() {
                const nuevoId = window.miListaGlobal.items.length + 1;
                window.miListaGlobal.items.push({
                    id: nuevoId,
                    nombre: `Producto ${nuevoId}`,
                    precio: Math.random() * 100 + 10,
                    cantidad: Math.floor(Math.random() * 5) + 1,
                    categoria: "nuevo"
                });
                actualizarLista();
                alert(`Item agregado! Total items: ${window.miListaGlobal.items.length}`);
            }
        </script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            button { margin: 5px; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
            .success { background: #d4edda; border-color: #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
            .item { margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h2>Envío de Lista de Objetos con htmx</h2>
        
        <div>
            <strong>Items en lista:</strong> <span id="contador">4</span>
            <button onclick="agregarItem(); document.getElementById('contador').textContent = window.miListaGlobal.items.length;">
                + Agregar Item
            </button>
        </div>
        
        <!-- Envío como form-urlencoded -->
        <button 
            hx-post="/api/lista" 
            hx-vals='js:{lista: window.miListaGlobal}'
            hx-trigger="click"
            hx-target="#resultado"
            onclick="actualizarLista()">
            Enviar Lista (Form)
        </button>
        
        <!-- Envío como JSON -->
        <button 
            hx-post="/api/lista-json" 
            hx-headers='{"Content-Type": "application/json"}'
            hx-vals='js:{lista: window.miListaGlobal}'
            hx-trigger="click"
            hx-target="#resultado"
            onclick="actualizarLista()">
            Enviar como JSON
        </button>
        
        <!-- Envío para procesamiento con Pydantic -->
        <button 
            hx-post="/api/lista-model" 
            hx-headers='{"Content-Type": "application/json"}'
            hx-vals='js:{lista: window.miListaGlobal}'
            hx-trigger="click"
            hx-target="#resultado"
            onclick="actualizarLista()">
            Enviar con Validación
        </button>
        
        <div id="resultado"></div>
        
        <script>
            // Actualizar contador inicial
            document.getElementById('contador').textContent = window.miListaGlobal.items.length;
        </script>
    </body>
    </html>
    """

# Endpoint para recibir lista como form-urlencoded
@app.post("/api/lista")
async def recibir_lista(request: Request):
    try:
        form_data = await request.form()
        lista_str = form_data.get("lista")
        
        if lista_str:
            lista_data = json.loads(lista_str) # type: ignore
            
            # Procesar la lista
            total_items = len(lista_data["items"])
            total_valor = lista_data["total"]
            
            # Construir HTML con los items
            items_html = "".join(
                f"<div class='item'>"
                f"ID: {item['id']}, {item['nombre']} - "
                f"${item['precio']} x {item['cantidad']} = "
                f"${item['precio'] * item['cantidad']:.2f}"
                f"</div>"
                for item in lista_data["items"]
            )
            
            return HTMLResponse(
                f"<div class='result success'>"
                f"<h3>✅ Lista recibida correctamente</h3>"
                f"<p><strong>Total items:</strong> {total_items}</p>"
                f"<p><strong>Valor total:</strong> ${total_valor:.2f}</p>"
                f"<p><strong>Timestamp:</strong> {lista_data['timestamp']}</p>"
                f"<div><strong>Items:</strong>{items_html}</div>"
                f"</div>"
            )
        else:
            return HTMLResponse("<div class='result error'>No se recibió la lista</div>")
            
    except json.JSONDecodeError:
        return HTMLResponse("<div class='result error'>Error decodificando JSON</div>")
    except Exception as e:
        return HTMLResponse(f"<div class='result error'>Error: {str(e)}</div>")


# Endpoint simple para mostrar carrito - JavaScript maneja el contenido
@app.get("/carrito")
async def mostrar_carrito(request: Request):
    """Vista simple del carrito - JavaScript maneja todo el contenido"""
    return templates.TemplateResponse(
        request=request, 
        name="_carrito_simple.html", 
        context={}
    )


# Endpoint legacy (POST) - mantener por si necesitamos revertir
@app.post("/carrito")
async def mostrar_carrito_post(request: Request):
    try:
        form_data = await request.form()
        datos_str = form_data.get("datos")
        lista_str = form_data.get("lista")  # Backup para compatibilidad
        
        # Debug: mostrar todos los datos del form
        print(f"Form data completo: {dict(form_data)}")
        print(f"datos_str: {datos_str}")
        print(f"lista_str: {lista_str}")
        
        # Usar datos_str o lista_str como fallback
        cart_data_str = datos_str or lista_str
        
        print(f"Datos recibidos: {cart_data_str}")
        
        if cart_data_str:
            print(f"Procesando datos del carrito...")
            # Convertir string a datos utilizables
            if isinstance(cart_data_str, str):
                try:
                    # Intentar parsear como JSON
                    datos_data = json.loads(cart_data_str)
                except json.JSONDecodeError:
                    # Si no es JSON válido, intentar evaluarlo como estructura Python
                    try:
                        import ast
                        datos_data = ast.literal_eval(cart_data_str)
                    except (ValueError, SyntaxError):
                        # Si todo falla, retornar error
                        return templates.TemplateResponse(
                            request=request, 
                            name="_carrito.html", 
                            context={"cart_items": [], "error": "Formato de datos inválido"}
                        )
            else:
                datos_data = cart_data_str

            # Convertir a lista si es necesario
            if isinstance(datos_data, dict):
                if 'items' in datos_data:
                    cart_items = datos_data['items']
                else:
                    cart_items = [datos_data]
            elif isinstance(datos_data, list):
                cart_items = datos_data
            else:
                cart_items = []
            
            # Asegurar que cada item tenga las propiedades necesarias
            processed_items = []
            for item in cart_items:
                processed_item = {
                    'id': item.get('id', 0),
                    'name': item.get('name', item.get('nombre', 'Producto sin nombre')),
                    'price': float(item.get('price', item.get('precio', 0))),
                    'quantity': int(item.get('quantity', item.get('cantidad', 1))),
                    'imageUrl': item.get('imageUrl', item.get('imagen', ''))
                }
                processed_items.append(processed_item)
            
            return templates.TemplateResponse(
                request=request, 
                name="_carrito.html", 
                context={"cart_items": processed_items}
            )
        else:
            print("No se recibieron datos del carrito (datos_str y lista_str están vacíos)")
            return templates.TemplateResponse(
                request=request, 
                name="_carrito.html", 
                context={"cart_items": [], "error": "No se recibieron datos del carrito. Asegúrate de que tienes productos en el carrito."}
            )
            
    except Exception as e:
        return templates.TemplateResponse(
            request=request, 
            name="_carrito.html", 
            context={"cart_items": [], "error": f"Error procesando el carrito: {str(e)}"}
        )


# Endpoints para modificar carrito desde la vista del carrito
@app.post("/carrito/increase/{product_id}")
async def increase_cart_item(product_id: int, request: Request):
    """Incrementar cantidad de un producto en el carrito y retornar vista actualizada"""
    try:
        # Obtener carrito actual de localStorage (simulado desde el request)
        # En una app real, obtendrías esto de la sesión o base de datos
        form_data = await request.form()
        
        # Para simplicidad, vamos a reconstruir el carrito desde localStorage
        # El frontend debe enviar el carrito actual
        cart_data = request.headers.get('HX-Current-URL', '')  # o usar otra estrategia
        
        # Por ahora, retornamos un mensaje de que necesitamos implementar esto
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={
                "cart_items": [], 
                "error": "Función de incremento en desarrollo. Use el botón del carrito principal para ver el carrito actualizado."
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={"cart_items": [], "error": f"Error: {str(e)}"}
        )


@app.post("/carrito/decrease/{product_id}")
async def decrease_cart_item(product_id: int, request: Request):
    """Decrementar cantidad de un producto en el carrito y retornar vista actualizada"""
    try:
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={
                "cart_items": [], 
                "error": "Función de decremento en desarrollo. Use el botón del carrito principal para ver el carrito actualizado."
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={"cart_items": [], "error": f"Error: {str(e)}"}
        )


@app.post("/carrito/remove/{product_id}")
async def remove_cart_item(product_id: int, request: Request):
    """Eliminar un producto del carrito y retornar vista actualizada"""
    try:
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={
                "cart_items": [], 
                "error": "Función de eliminación en desarrollo. Use el botón del carrito principal para ver el carrito actualizado."
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="_carrito.html", 
            context={"cart_items": [], "error": f"Error: {str(e)}"}
        )
