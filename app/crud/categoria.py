"""
CRUD operations para Categorías
"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, text

from app.crud.base import CRUDBase
from app.models import Categoria, CategoriaCreate, CategoriaUpdate


class CRUDCategoria(CRUDBase[Categoria, CategoriaCreate, CategoriaUpdate]):
    
    def get_by_nombre(self, db: Session, *, nombre: str) -> Optional[Categoria]:
        """
        Obtener categoría por nombre
        """
        statement = select(Categoria).where(Categoria.nombre == nombre)
        return db.exec(statement).first()

    def get_root_active(self, db: Session) -> List[dict]:
        """
        Obtener todas las categorias raíz activas id y nombre
        """
        try:
            statement = select(Categoria).where(Categoria.padre == None, Categoria.activo == True)
            categorias = db.exec(statement).all()
            return [{"id": categoria.id, "nombre": categoria.nombre} for categoria in categorias]
        except Exception as e:
            print(f"Error en get_root_active: {e}")
            return []

    def get_activas(self, db: Session) -> List[Categoria]:
        """
        Obtener solo las categorías activas
        """
        statement = select(Categoria).where(Categoria.activo == True)
        return [] #db.exec(statement).all()

    def get_with_productos_count(self, db: Session) -> List[dict]:
        """
        Obtener categorías con el conteo de productos
        """
        # Aquí puedes implementar una consulta más compleja
        # Por ahora retornamos las categorías básicas
        categorias = self.get_activas(db)
        result = []
        for categoria in categorias:
            result.append({
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "activo": categoria.activo,
                "total_productos": len(categoria.productos) if categoria.productos else 0
            })
        return result

    def activar(self, db: Session, *, categoria_id: int) -> Optional[Categoria]:
        """
        Activar una categoría
        """
        categoria = self.get(db, categoria_id)
        if categoria:
            categoria.activo = True
            db.add(categoria)
            db.commit()
            db.refresh(categoria)
        return categoria

    def desactivar(self, db: Session, *, categoria_id: int) -> Optional[Categoria]:
        """
        Desactivar una categoría
        """
        categoria = self.get(db, categoria_id)
        if categoria:
            categoria.activo = False
            db.add(categoria)
            db.commit()
            db.refresh(categoria)
        return categoria

    def get_categorias_hijas(
        self, 
        db: Session, 
        *, 
        categoria_id: int, 
        solo_activos: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtener las categorías hijas directas de una categoría padre.
        
        Args:
            db: Sesión de base de datos
            categoria_id: ID de la categoría padre
            solo_activos: Si True, solo categorías activas (default: True)
            
        Returns:
            Lista de categorías hijas con id y nombre
        """
        try:
            # Filtro para categorías activas
            activo_filter = "AND activo = true" if solo_activos else ""
            
            query = text(f"""
            SELECT id, nombre 
            FROM categoria 
            WHERE padre = :categoria_id {activo_filter}
            ORDER BY nombre
            """)
            
            result = db.execute(query, {"categoria_id": categoria_id}).fetchall()
            
            return [
                {
                    "id": row.id,
                    "nombre": row.nombre
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error en get_categorias_hijas: {e}")
            return []

    def get_productos_descendientes(
        self, 
        db: Session, 
        *, 
        categoria_id: int, 
        solo_activos: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtener todos los productos de la categoría dada y sus descendientes.
        Por defecto solo incluye categorías y productos activos.
        
        Args:
            db: Sesión de base de datos
            categoria_id: ID de la categoría padre
            solo_activos: Si True, solo categorías y productos activos (default: True)
            
        Returns:
            Lista de productos con información de categoría
        """
        try:
            # Filtros para categorías y productos activos
            categoria_filter = "AND activo = true" if solo_activos else ""
            producto_filter = "AND p.activo = true" if solo_activos else ""
            categoria_recursiva_filter = "AND c.activo = true" if solo_activos else ""
            
            query = text(f"""
            WITH RECURSIVE categoria_tree AS (
                -- Caso base: la categoría específica
                SELECT id, nombre FROM categoria 
                WHERE id = :categoria_id {categoria_filter}
                
                UNION ALL
                
                -- Caso recursivo: todos los descendientes activos
                SELECT c.id, c.nombre FROM categoria c
                INNER JOIN categoria_tree ct ON c.padre = ct.id
                WHERE 1=1 {categoria_recursiva_filter}
            )
            SELECT 
                p.id,
                p.nombre,
                p.precio_venta as precio,
                p.stock_actual as stock,
                p.activo,
                p.imagen_url,
                ct.nombre as categoria
            FROM categoria_tree ct
            INNER JOIN producto p ON ct.id = p.categoria_id
            WHERE 1=1 {producto_filter}
            ORDER BY p.nombre
            """)
            
            result = db.execute(query, {"categoria_id": categoria_id}).fetchall()
            
            return [
                {
                    "id": row.id,
                    "nombre": row.nombre,
                    "precio": float(row.precio) if row.precio else 0.0,
                    "stock": row.stock,
                    "activo": row.activo,
                    "categoria": row.categoria,
                    "imagen_url": row.imagen_url,
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error en get_productos_descendientes: {e}")
            return []


# Instancia del CRUD para usar en los endpoints
categoria = CRUDCategoria(Categoria)
