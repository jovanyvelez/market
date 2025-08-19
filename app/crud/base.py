"""
CRUD base genérico para operaciones comunes
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Objeto CRUD con métodos por defecto para Create, Read, Update y Delete (CRUD).
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Obtener un registro por ID
        """
        return db.get(self.model, id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Obtener múltiples registros con paginación
        """
        statement = select(self.model).offset(skip).limit(limit)
        return db.exec(statement).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Crear un nuevo registro
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Actualizar un registro existente
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Eliminar un registro por ID
        """
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_field(
        self, db: Session, *, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """
        Obtener un registro por cualquier campo
        """
        statement = select(self.model).where(
            getattr(self.model, field_name) == field_value
        )
        return db.exec(statement).first()

    def get_multi_by_field(
        self, 
        db: Session, 
        *, 
        field_name: str, 
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Obtener múltiples registros por cualquier campo
        """
        statement = select(self.model).where(
            getattr(self.model, field_name) == field_value
        ).offset(skip).limit(limit)
        return db.exec(statement).all()

    def count(self, db: Session) -> int:
        """
        Contar total de registros
        """
        statement = select(self.model)
        return len(db.exec(statement).all())

    def exists(self, db: Session, *, id: int) -> bool:
        """
        Verificar si existe un registro por ID
        """
        return self.get(db, id) is not None
