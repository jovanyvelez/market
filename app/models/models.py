"""
Modelos SQLModel para el sistema de Market
Basado en el script de base de datos PostgreSQL
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# =============================================================================
# ENUMS
# =============================================================================

class UnidadMedidaEnum(str, Enum):
    PIEZA = "pieza"
    KG = "kg"
    LITRO = "litro"
    GRAMO = "gramo"
    METRO = "metro"
    CAJA = "caja"
    PAQUETE = "paquete"


class TipoClienteEnum(str, Enum):
    REGULAR = "regular"
    VIP = "vip"
    MAYORISTA = "mayorista"


class RolUsuarioEnum(str, Enum):
    ADMIN = "admin"
    CAJERO = "cajero"
    VENDEDOR = "vendedor"
    ALMACENISTA = "almacenista"


class MetodoPagoEnum(str, Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    CREDITO = "credito"


class EstadoVentaEnum(str, Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    DEVUELTA = "devuelta"


class EstadoCompraEnum(str, Enum):
    PENDIENTE = "pendiente"
    RECIBIDA = "recibida"
    CANCELADA = "cancelada"


class TipoMovimientoEnum(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    MERMA = "merma"


class EstadoCajaEnum(str, Enum):
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class CategoriaGastoEnum(str, Enum):
    SERVICIOS = "servicios"
    MERCANCIA = "mercancia"
    MANTENIMIENTO = "mantenimiento"
    ADMINISTRATIVO = "administrativo"
    OTROS = "otros"


class TipoConfigEnum(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"


# =============================================================================
# MODELOS BASE
# =============================================================================

class BaseModel(SQLModel):
    """Modelo base con campos comunes"""
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# CATEGORIA
# =============================================================================

class CategoriaBase(SQLModel):
    nombre: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)


class Categoria(CategoriaBase, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    padre: int | None = Field(default=None, foreign_key="categoria.id")

    # Relaciones
    productos: List["Producto"] = Relationship(back_populates="categoria")


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    activo: Optional[bool] = None


# =============================================================================
# PROVEEDOR
# =============================================================================

class ProveedorBase(SQLModel):
    nombre: str = Field(max_length=150)
    contacto: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    rfc: Optional[str] = Field(default=None, max_length=15)
    activo: bool = Field(default=True)


class Proveedor(ProveedorBase, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    productos: List["Producto"] = Relationship(back_populates="proveedor")
    compras: List["Compra"] = Relationship(back_populates="proveedor")


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorRead(ProveedorBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class ProveedorUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=150)
    contacto: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    rfc: Optional[str] = Field(default=None, max_length=15)
    activo: Optional[bool] = None


# =============================================================================
# PRODUCTO
# =============================================================================

class ProductoBase(SQLModel):
    codigo_barras: Optional[str] = Field(default=None, max_length=50, unique=True)
    nombre: str = Field(max_length=200)
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    proveedor_id: Optional[int] = Field(default=None, foreign_key="proveedor.id")
    precio_compra: Decimal = Field(decimal_places=2)
    precio_venta: Decimal = Field(decimal_places=2)
    stock_actual: int = Field(default=0)
    stock_minimo: int = Field(default=0)
    stock_maximo: int = Field(default=1000)
    unidad_medida: UnidadMedidaEnum = Field(default=UnidadMedidaEnum.PIEZA)
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    fecha_vencimiento: Optional[date] = None
    activo: bool = Field(default=True)


class Producto(ProductoBase, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    proveedor: Optional[Proveedor] = Relationship(back_populates="productos")
    detalles_venta: List["DetalleVenta"] = Relationship(back_populates="producto")
    detalles_compra: List["DetalleCompra"] = Relationship(back_populates="producto")
    movimientos: List["MovimientoInventario"] = Relationship(back_populates="producto")


class ProductoCreate(ProductoBase):
    pass


class ProductoRead(ProductoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    categoria: Optional[CategoriaRead] = None
    proveedor: Optional[ProveedorRead] = None


class ProductoUpdate(SQLModel):
    codigo_barras: Optional[str] = Field(default=None, max_length=50)
    nombre: Optional[str] = Field(default=None, max_length=200)
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    precio_compra: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    stock_maximo: Optional[int] = None
    unidad_medida: Optional[UnidadMedidaEnum] = None
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    fecha_vencimiento: Optional[date] = None
    activo: Optional[bool] = None


# =============================================================================
# CLIENTE
# =============================================================================

class ClienteBase(SQLModel):
    numero_cliente: Optional[str] = Field(default=None, max_length=20, unique=True)
    nombre: str = Field(max_length=100)
    apellidos: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_cliente: TipoClienteEnum = Field(default=TipoClienteEnum.REGULAR)
    descuento_aplicable: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    limite_credito: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    activo: bool = Field(default=True)


class Cliente(ClienteBase, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    ventas: List["Venta"] = Relationship(back_populates="cliente")


class ClienteCreate(ClienteBase):
    pass


class ClienteRead(ClienteBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class ClienteUpdate(SQLModel):
    numero_cliente: Optional[str] = Field(default=None, max_length=20)
    nombre: Optional[str] = Field(default=None, max_length=100)
    apellidos: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_cliente: Optional[TipoClienteEnum] = None
    descuento_aplicable: Optional[Decimal] = None
    limite_credito: Optional[Decimal] = None
    activo: Optional[bool] = None


# =============================================================================
# USUARIO
# =============================================================================

class UsuarioBase(SQLModel):
    username: str = Field(max_length=50, unique=True)
    email: str = Field(max_length=100, unique=True)
    nombre: str = Field(max_length=100)
    apellidos: Optional[str] = Field(default=None, max_length=100)
    rol: RolUsuarioEnum
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: bool = Field(default=True)


class Usuario(UsuarioBase, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    ultimo_acceso: Optional[datetime] = None
    
    # Relaciones
    ventas: List["Venta"] = Relationship(back_populates="usuario")
    compras: List["Compra"] = Relationship(back_populates="usuario")
    movimientos: List["MovimientoInventario"] = Relationship(back_populates="usuario")
    cajas: List["Caja"] = Relationship(back_populates="usuario")
    gastos: List["Gasto"] = Relationship(back_populates="usuario")


class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=6)


class UsuarioRead(UsuarioBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    ultimo_acceso: Optional[datetime] = None


class UsuarioUpdate(SQLModel):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    nombre: Optional[str] = Field(default=None, max_length=100)
    apellidos: Optional[str] = Field(default=None, max_length=100)
    rol: Optional[RolUsuarioEnum] = None
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)


# =============================================================================
# VENTA
# =============================================================================

class VentaBase(SQLModel):
    numero_venta: str = Field(max_length=20, unique=True)
    cliente_id: Optional[int] = Field(default=None, foreign_key="cliente.id")
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha_venta: datetime = Field(default_factory=datetime.utcnow)
    subtotal: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    descuento: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    impuestos: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total: Decimal = Field(decimal_places=2)
    metodo_pago: MetodoPagoEnum
    estado: EstadoVentaEnum = Field(default=EstadoVentaEnum.COMPLETADA)
    observaciones: Optional[str] = None


class Venta(VentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    cliente: Optional[Cliente] = Relationship(back_populates="ventas")
    usuario: Usuario = Relationship(back_populates="ventas")
    detalles: List["DetalleVenta"] = Relationship(back_populates="venta")


class VentaCreate(VentaBase):
    pass


class VentaRead(VentaBase):
    id: int
    cliente: Optional[ClienteRead] = None
    usuario: UsuarioRead


class VentaUpdate(SQLModel):
    cliente_id: Optional[int] = None
    estado: Optional[EstadoVentaEnum] = None
    observaciones: Optional[str] = None


# =============================================================================
# DETALLE VENTA
# =============================================================================

class DetalleVentaBase(SQLModel):
    venta_id: int = Field(foreign_key="venta.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: Decimal = Field(decimal_places=2)
    precio_unitario: Decimal = Field(decimal_places=2)
    descuento_unitario: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    subtotal: Decimal = Field(decimal_places=2)


class DetalleVenta(DetalleVentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    venta: Venta = Relationship(back_populates="detalles")
    producto: Producto = Relationship(back_populates="detalles_venta")


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaRead(DetalleVentaBase):
    id: int
    producto: ProductoRead


# =============================================================================
# COMPRA
# =============================================================================

class CompraBase(SQLModel):
    numero_compra: str = Field(max_length=20, unique=True)
    proveedor_id: int = Field(foreign_key="proveedor.id")
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha_compra: datetime = Field(default_factory=datetime.utcnow)
    subtotal: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    impuestos: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total: Decimal = Field(decimal_places=2)
    estado: EstadoCompraEnum = Field(default=EstadoCompraEnum.PENDIENTE)
    observaciones: Optional[str] = None


class Compra(CompraBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    proveedor: Proveedor = Relationship(back_populates="compras")
    usuario: Usuario = Relationship(back_populates="compras")
    detalles: List["DetalleCompra"] = Relationship(back_populates="compra")


class CompraCreate(CompraBase):
    pass


class CompraRead(CompraBase):
    id: int
    proveedor: ProveedorRead
    usuario: UsuarioRead


class CompraUpdate(SQLModel):
    estado: Optional[EstadoCompraEnum] = None
    observaciones: Optional[str] = None


# =============================================================================
# DETALLE COMPRA
# =============================================================================

class DetalleCompraBase(SQLModel):
    compra_id: int = Field(foreign_key="compra.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: Decimal = Field(decimal_places=2)
    precio_unitario: Decimal = Field(decimal_places=2)
    subtotal: Decimal = Field(decimal_places=2)


class DetalleCompra(DetalleCompraBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    compra: Compra = Relationship(back_populates="detalles")
    producto: Producto = Relationship(back_populates="detalles_compra")


class DetalleCompraCreate(DetalleCompraBase):
    pass


class DetalleCompraRead(DetalleCompraBase):
    id: int
    producto: ProductoRead


# =============================================================================
# MOVIMIENTO INVENTARIO
# =============================================================================

class MovimientoInventarioBase(SQLModel):
    producto_id: int = Field(foreign_key="producto.id")
    tipo_movimiento: TipoMovimientoEnum
    cantidad: Decimal = Field(decimal_places=2)
    stock_anterior: int
    stock_nuevo: int
    referencia: Optional[str] = Field(default=None, max_length=100)
    motivo: Optional[str] = None
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha_movimiento: datetime = Field(default_factory=datetime.utcnow)


class MovimientoInventario(MovimientoInventarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    producto: Producto = Relationship(back_populates="movimientos")
    usuario: Usuario = Relationship(back_populates="movimientos")


class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass


class MovimientoInventarioRead(MovimientoInventarioBase):
    id: int
    producto: ProductoRead
    usuario: UsuarioRead


# =============================================================================
# CAJA
# =============================================================================

class CajaBase(SQLModel):
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha_apertura: datetime = Field(default_factory=datetime.utcnow)
    fecha_cierre: Optional[datetime] = None
    monto_inicial: Decimal = Field(decimal_places=2)
    monto_final: Optional[Decimal] = Field(default=None, decimal_places=2)
    total_ventas_efectivo: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total_gastos: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    diferencia: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    estado: EstadoCajaEnum = Field(default=EstadoCajaEnum.ABIERTA)
    observaciones: Optional[str] = None


class Caja(CajaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    usuario: Usuario = Relationship(back_populates="cajas")
    gastos: List["Gasto"] = Relationship(back_populates="caja")


class CajaCreate(CajaBase):
    pass


class CajaRead(CajaBase):
    id: int
    usuario: UsuarioRead


class CajaUpdate(SQLModel):
    fecha_cierre: Optional[datetime] = None
    monto_final: Optional[Decimal] = None
    total_ventas_efectivo: Optional[Decimal] = None
    total_gastos: Optional[Decimal] = None
    diferencia: Optional[Decimal] = None
    estado: Optional[EstadoCajaEnum] = None
    observaciones: Optional[str] = None


# =============================================================================
# GASTO
# =============================================================================

class GastoBase(SQLModel):
    concepto: str = Field(max_length=200)
    monto: Decimal = Field(decimal_places=2)
    categoria: CategoriaGastoEnum
    fecha_gasto: date
    usuario_id: int = Field(foreign_key="usuario.id")
    caja_id: Optional[int] = Field(default=None, foreign_key="caja.id")
    observaciones: Optional[str] = None


class Gasto(GastoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    usuario: Usuario = Relationship(back_populates="gastos")
    caja: Optional[Caja] = Relationship(back_populates="gastos")


class GastoCreate(GastoBase):
    pass


class GastoRead(GastoBase):
    id: int
    usuario: UsuarioRead
    caja: Optional[CajaRead] = None


class GastoUpdate(SQLModel):
    concepto: Optional[str] = Field(default=None, max_length=200)
    monto: Optional[Decimal] = None
    categoria: Optional[CategoriaGastoEnum] = None
    fecha_gasto: Optional[date] = None
    caja_id: Optional[int] = None
    observaciones: Optional[str] = None


# =============================================================================
# CONFIGURACION
# =============================================================================

class ConfiguracionBase(SQLModel):
    clave: str = Field(max_length=100, unique=True)
    valor: str
    descripcion: Optional[str] = None
    tipo: TipoConfigEnum = Field(default=TipoConfigEnum.STRING)


class Configuracion(ConfiguracionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)


class ConfiguracionCreate(ConfiguracionBase):
    pass


class ConfiguracionRead(ConfiguracionBase):
    id: int
    fecha_actualizacion: datetime


class ConfiguracionUpdate(SQLModel):
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[TipoConfigEnum] = None
