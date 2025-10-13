from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """
    Repository base abstrato seguindo o padrão Repository
    Implementa Dependency Inversion Principle (DIP) do SOLID
    """
    
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    def create(self, obj_in: Dict[str, Any]) -> T:
        """Criar novo registro"""
        db_obj = self.model_class(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get(self, id: int) -> Optional[T]:
        """Buscar por ID"""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Buscar múltiplos registros com paginação"""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """Atualizar registro existente"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Deletar registro por ID"""
        obj = self.db.query(self.model_class).filter(self.model_class.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Contar total de registros"""
        return self.db.query(self.model_class).count()
    
    def exists(self, id: int) -> bool:
        """Verificar se registro existe"""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first() is not None