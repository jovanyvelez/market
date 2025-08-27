"""
CRUD operations para Usuarios
"""

from typing import List, Optional, Sequence
from sqlmodel import Session, select
import hashlib
import secrets

from app.crud.base import CRUDBase
from app.models import Usuario, UsuarioCreate, UsuarioUpdate, RolUsuarioEnum


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar contraseña usando un hash simple (para desarrollo)
    En producción se debería usar bcrypt
    """
    return hashed_password == get_password_hash(plain_password)


def get_password_hash(password: str) -> str:
    """
    Generar hash de contraseña usando SHA-256 con salt
    En producción se debería usar bcrypt
    """
    salt = "market_salt_2024"  # En producción usar un salt aleatorio
    return hashlib.sha256((password + salt).encode()).hexdigest()


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[Usuario]:
        """
        Obtener usuario por username
        """
        statement = select(Usuario).where(Usuario.username == username)
        return db.exec(statement).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Usuario]:
        """
        Obtener usuario por email
        """
        statement = select(Usuario).where(Usuario.email == email)
        return db.exec(statement).first()

    def get_activos(self, db: Session) -> List[Usuario]:
        """
        Obtener solo usuarios activos
        """
        statement = select(Usuario).where(Usuario.activo == True)
        return list(db.exec(statement).all())

    def get_by_rol(self, db: Session, *, rol: RolUsuarioEnum) -> List[Usuario]:
        """
        Obtener usuarios por rol
        """
        statement = select(Usuario).where(Usuario.rol == rol)
        return list(db.exec(statement).all())

    def create_with_password(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        """
        Crear usuario con contraseña hasheada
        """
        # Hashear la contraseña
        hashed_password = get_password_hash(obj_in.password)
        
        # Crear el objeto usuario
        db_obj = Usuario(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hashed_password,
            nombre=obj_in.nombre,
            apellidos=obj_in.apellidos,
            rol=obj_in.rol,
            telefono=obj_in.telefono,
            activo=obj_in.activo
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(
        self, 
        db: Session, 
        *, 
        usuario_id: int, 
        nueva_password: str
    ) -> Optional[Usuario]:
        """
        Actualizar contraseña de un usuario
        """
        usuario = self.get(db, usuario_id)
        if usuario:
            hashed_password = get_password_hash(nueva_password)
            usuario.password_hash = hashed_password
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario

    def activar(self, db: Session, *, usuario_id: int) -> Optional[Usuario]:
        """
        Activar un usuario
        """
        usuario = self.get(db, usuario_id)
        if usuario:
            usuario.activo = True
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario

    def desactivar(self, db: Session, *, usuario_id: int) -> Optional[Usuario]:
        """
        Desactivar un usuario
        """
        usuario = self.get(db, usuario_id)
        if usuario:
            usuario.activo = False
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario

    def authenticate(
        self, 
        db: Session, 
        *, 
        username: str, 
        password: str
    ) -> Optional[Usuario]:
        """
        Autenticar usuario con username y contraseña
        """
        usuario = self.get_by_username(db, username=username)
        if not usuario:
            return None
        if not verify_password(password, usuario.password_hash):
            return None
        return usuario

    def is_active(self, usuario: Usuario) -> bool:
        """
        Verificar si el usuario está activo
        """
        return usuario.activo

    def is_admin(self, usuario: Usuario) -> bool:
        """
        Verificar si el usuario es administrador
        """
        return usuario.rol == RolUsuarioEnum.ADMIN

    def can_sell(self, usuario: Usuario) -> bool:
        """
        Verificar si el usuario puede realizar ventas
        """
        roles_venta = [RolUsuarioEnum.ADMIN, RolUsuarioEnum.VENDEDOR, RolUsuarioEnum.CAJERO]
        return usuario.rol in roles_venta

    def can_manage_inventory(self, usuario: Usuario) -> bool:
        """
        Verificar si el usuario puede gestionar inventario
        """
        roles_inventario = [RolUsuarioEnum.ADMIN, RolUsuarioEnum.ALMACENISTA]
        return usuario.rol in roles_inventario


# Instancia del CRUD para usar en los endpoints
usuario = CRUDUsuario(Usuario)
