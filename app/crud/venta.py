"""
CRUD operations para Ventas
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import (
    Venta, VentaCreate, VentaUpdate,
    DetalleVenta, DetalleVentaCreate,
    EstadoVentaEnum, MetodoPagoEnum
)


class CRUDVenta(CRUDBase[Venta, VentaCreate, VentaUpdate]):
    
    def get_by_numero_venta(self, db: Session, *, numero_venta: str) -> Optional[Venta]:
        """
        Obtener venta por número de venta
        """
        statement = select(Venta).where(Venta.numero_venta == numero_venta)
        return db.exec(statement).first()

    def get_ventas_del_dia(self, db: Session, *, fecha: date = None) -> List[Venta]:
        """
        Obtener ventas de un día específico (por defecto hoy)
        """
        if fecha is None:
            fecha = date.today()
        
        statement = select(Venta).where(
            Venta.fecha_venta >= datetime.combine(fecha, datetime.min.time()),
            Venta.fecha_venta < datetime.combine(fecha, datetime.max.time())
        )
        return db.exec(statement).all()

    def get_por_cliente(self, db: Session, *, cliente_id: int) -> List[Venta]:
        """
        Obtener ventas de un cliente específico
        """
        statement = select(Venta).where(Venta.cliente_id == cliente_id)
        return db.exec(statement).all()

    def get_por_usuario(self, db: Session, *, usuario_id: int) -> List[Venta]:
        """
        Obtener ventas realizadas por un usuario
        """
        statement = select(Venta).where(Venta.usuario_id == usuario_id)
        return db.exec(statement).all()

    def get_por_metodo_pago(
        self, 
        db: Session, 
        *, 
        metodo_pago: MetodoPagoEnum,
        fecha_inicio: date = None,
        fecha_fin: date = None
    ) -> List[Venta]:
        """
        Obtener ventas por método de pago en un rango de fechas
        """
        statement = select(Venta).where(Venta.metodo_pago == metodo_pago)
        
        if fecha_inicio:
            statement = statement.where(
                Venta.fecha_venta >= datetime.combine(fecha_inicio, datetime.min.time())
            )
        if fecha_fin:
            statement = statement.where(
                Venta.fecha_venta <= datetime.combine(fecha_fin, datetime.max.time())
            )
            
        return db.exec(statement).all()

    def get_por_estado(self, db: Session, *, estado: EstadoVentaEnum) -> List[Venta]:
        """
        Obtener ventas por estado
        """
        statement = select(Venta).where(Venta.estado == estado)
        return db.exec(statement).all()

    def calcular_total_ventas_dia(self, db: Session, *, fecha: date = None) -> Decimal:
        """
        Calcular total de ventas del día
        """
        ventas = self.get_ventas_del_dia(db, fecha=fecha)
        total = sum(venta.total for venta in ventas if venta.estado == EstadoVentaEnum.COMPLETADA)
        return Decimal(str(total))

    def calcular_total_por_metodo_pago(
        self, 
        db: Session, 
        *, 
        fecha: date = None
    ) -> dict:
        """
        Calcular totales por método de pago del día
        """
        ventas = self.get_ventas_del_dia(db, fecha=fecha)
        totales = {
            MetodoPagoEnum.EFECTIVO: Decimal('0.00'),
            MetodoPagoEnum.TARJETA: Decimal('0.00'),
            MetodoPagoEnum.TRANSFERENCIA: Decimal('0.00'),
            MetodoPagoEnum.CREDITO: Decimal('0.00')
        }
        
        for venta in ventas:
            if venta.estado == EstadoVentaEnum.COMPLETADA:
                totales[venta.metodo_pago] += venta.total
                
        return totales

    def generar_numero_venta(self, db: Session) -> str:
        """
        Generar número de venta automático
        Formato: V-YYYYMMDD-NNNN
        """
        hoy = date.today()
        prefijo = f"V-{hoy.strftime('%Y%m%d')}"
        
        # Buscar el último número del día
        statement = select(Venta).where(
            Venta.numero_venta.startswith(prefijo)
        ).order_by(Venta.numero_venta.desc())
        
        ultima_venta = db.exec(statement).first()
        
        if ultima_venta:
            # Extraer el número secuencial
            ultimo_numero = int(ultima_venta.numero_venta.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
            
        return f"{prefijo}-{nuevo_numero:04d}"

    def crear_venta_completa(
        self,
        db: Session,
        *,
        venta_data: VentaCreate,
        detalles: List[DetalleVentaCreate]
    ) -> Venta:
        """
        Crear una venta completa con sus detalles
        """
        # Generar número de venta si no existe
        if not venta_data.numero_venta:
            venta_data.numero_venta = self.generar_numero_venta(db)
        
        # Crear la venta
        venta = self.create(db, obj_in=venta_data)
        
        # Crear los detalles
        for detalle_data in detalles:
            detalle_data.venta_id = venta.id
            detalle = DetalleVenta.model_validate(detalle_data)
            db.add(detalle)
        
        db.commit()
        db.refresh(venta)
        return venta

    def cancelar_venta(self, db: Session, *, venta_id: int) -> Optional[Venta]:
        """
        Cancelar una venta (cambiar estado y restaurar stock)
        """
        venta = self.get(db, venta_id)
        if venta and venta.estado == EstadoVentaEnum.COMPLETADA:
            venta.estado = EstadoVentaEnum.CANCELADA
            
            # TODO: Restaurar stock de los productos
            # Esto requeriría acceso al CRUD de productos
            
            db.add(venta)
            db.commit()
            db.refresh(venta)
            
        return venta


# Instancia del CRUD para usar en los endpoints
venta = CRUDVenta(Venta)
