"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from fastapi import FastAPI, Request, Depends, Response
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