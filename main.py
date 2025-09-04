"""
FastAPI Market System
Sistema de gestión para market pequeño
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import categorias
from app.api.v2.endpoints import categorias as categorias_v2



# Crear la aplicación FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
app.include_router(categorias_v2.router, prefix="/api/v2/categorias", tags=["categorias_v2"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Market System"}

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")