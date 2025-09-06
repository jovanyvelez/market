"""
CRUD operations para Productos
"""

from typing import List, Optional, Sequence
from decimal import Decimal
from sqlmodel import Session, select, and_, or_, column, func, text



from app.crud.base import CRUDBase
from app.models import Producto, ProductoCreate, ProductoUpdate


class CRUDProducto(CRUDBase[Producto, ProductoCreate, ProductoUpdate]):
    
    def get_by_codigo_barras(self, db: Session, *, codigo_barras: str) -> Optional[Producto]:
        """
        Obtener producto por código de barras
        """
        statement = select(Producto).where(Producto.codigo_barras == codigo_barras)
        return db.exec(statement).first()

    def get_by_nombre(self, db: Session, *, nombre: str) -> List[Producto]:
        """
        Buscar productos por nombre (búsqueda parcial)
        """
        statement = select(Producto).where(func.lower(Producto.nombre).like(f"%{nombre.lower()}%"))
        result = db.exec(statement).all()
        return list(result)

    def get_by_categoria(self, db: Session, *, categoria_id: int) -> List[Producto]:
        """
        Obtener productos por categoría
        """
        statement = select(Producto).where(Producto.categoria_id == categoria_id)
        result = db.exec(statement).all()
        return list(result)

    def get_activos(self, db: Session) -> List[dict]:
        """
        Obtener solo productos activos con formato compatible con plantillas
        """
        try:
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
            WHERE p.activo = true
            ORDER BY p.nombre
            """)
            
            result = db.execute(query).fetchall()
            
            return [
                {
                    "id": row.id,
                    "nombre": row.nombre,
                    "descripcion": row.descripcion,
                    "precio": float(row.precio) if row.precio else 0.0,
                    "stock": row.stock,
                    "imagen_url": row.imagen_url,
                    "activo": row.activo,
                    "categoria_nombre": row.categoria_nombre
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error en get_activos: {e}")
            return []

    def get_stock_bajo(self, db: Session) -> List[Producto]:
        """
        Obtener productos con stock bajo (stock actual <= stock mínimo)
        """
        statement = select(Producto).where(
            Producto.stock_actual <= Producto.stock_minimo
        ).where(Producto.activo == True)
        result = db.exec(statement).all()
        return list(result)

    def get_agotados(self, db: Session) -> List[Producto]:
        """
        Obtener productos agotados (stock = 0)
        """
        statement = select(Producto).where(Producto.stock_actual == 0)
        result = db.exec(statement).all()
        return list(result)

    def actualizar_stock(
        self, 
        db: Session, 
        *, 
        producto_id: int, 
        nuevo_stock: int,
        motivo: str = "Ajuste manual"
    ) -> Optional[Producto]:
        """
        Actualizar stock de un producto
        """
        producto = self.get(db, producto_id)
        if producto:
            stock_anterior = producto.stock_actual
            producto.stock_actual = nuevo_stock
            db.add(producto)
            db.commit()
            db.refresh(producto)
            
            # Aquí podrías registrar el movimiento en MovimientoInventario
            # TODO: Implementar registro de movimiento
            
        return producto

    def incrementar_stock(
        self, 
        db: Session, 
        *, 
        producto_id: int, 
        cantidad: int
    ) -> Optional[Producto]:
        """
        Incrementar stock de un producto (compras/devoluciones)
        """
        producto = self.get(db, producto_id)
        if producto:
            producto.stock_actual += cantidad
            db.add(producto)
            db.commit()
            db.refresh(producto)
        return producto

    def decrementar_stock(
        self, 
        db: Session, 
        *, 
        producto_id: int, 
        cantidad: int
    ) -> Optional[Producto]:
        """
        Decrementar stock de un producto (ventas)
        """
        producto = self.get(db, producto_id)
        if producto and producto.stock_actual >= cantidad:
            producto.stock_actual -= cantidad
            db.add(producto)
            db.commit()
            db.refresh(producto)
            return producto
        return None  # No hay suficiente stock

    def buscar_por_termino(
        self, 
        db: Session, 
        *, 
        termino: str,
        skip: int = 0,
        limit: int = 50
    ):
        """
        Búsqueda global por nombre, código de barras o descripción
        Devuelve productos con formato compatible con las plantillas
        """
        try:
            # Limpiar el término de búsqueda
            palabra = termino.strip().lower()
            
            # Consulta que busca en nombre, código de barras y descripción
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
            WHERE p.activo = true
            AND (
                LOWER(p.nombre) LIKE :termino
                OR LOWER(p.codigo_barras) LIKE :termino
                OR LOWER(p.descripcion) LIKE :termino
            )
            ORDER BY p.nombre
            LIMIT :limit OFFSET :skip
            """)
            
            result = db.execute(query, {
                "termino": f"%{palabra}%",
                "limit": limit,
                "skip": skip
            }).fetchall()
            
            return [
                {
                    "id": row.id,
                    "nombre": row.nombre,
                    "descripcion": row.descripcion,
                    "precio": float(row.precio) if row.precio else 0.0,
                    "stock": row.stock,
                    "imagen_url": row.imagen_url,
                    "activo": row.activo,
                    "categoria_nombre": row.categoria_nombre
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error en buscar_por_termino: {e}")
            return []


    def get_mas_vendidos(self, db: Session, *, limit: int = 10) -> List[Producto]:
        """
        Obtener productos más vendidos
        """
        # Esta consulta requeriría JOIN con DetalleVenta
        # Por ahora retornamos productos activos
        statement = select(Producto).where(Producto.activo == True).limit(limit)
        result = db.exec(statement).all()
        return list(result)

    def verificar_disponibilidad(
        self, 
        db: Session, 
        *, 
        producto_id: int, 
        cantidad_solicitada: int
    ) -> bool:
        """
        Verificar si hay suficiente stock para una venta
        """
        producto = self.get(db, producto_id)
        if producto:
            return producto.stock_actual >= cantidad_solicitada
        return False


# Instancia del CRUD para usar en los endpoints
producto = CRUDProducto(Producto)
