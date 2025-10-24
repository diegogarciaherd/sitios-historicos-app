from core.database import Base, db
from sqlalchemy import ForeignKeyConstraint, Integer, Column, String, Boolean
from sqlalchemy.orm import Mapped, relationship
from flask import session, g

from core.models.feature_flags_history import FeatureFlagHistory, create_feature_flag_history, update_feature_flag_history

class FeatureFlag(Base):
    '''Modelo de Feature Flag para habilitar/deshabilitar funcionalidades'''
    ''' atributos:
    - id: Identificador único del feature flag
    - name: Nombre del feature flag
    - activated: Estado del feature flag (activado/desactivado)
    - description: Descripción del feature flag
    - message: Mensaje asociado al feature flag
    - history: Relación con el historial de cambios de la feature flag
    '''
    __tablename__ = "feature_flags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    activated = Column(Boolean, nullable=True, default=False)
    description = Column(String, nullable=True)
    message = Column(String, nullable=True)

    # Se debe guardar el historial del último cambio de la feature flag
    ForeignKeyConstraint(['id'], ['feature_flags_history.id'])
    
    # Este relationship permite acceder al historial de cambios de la feature flag directamente desde la instancia de FeatureFlag
    history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="feature_flag",
        cascade="all, delete-orphan",
    )
    def __repr__(self):
        '''Representación en string del Feature Flag'''
        return f"<Feature Flag {self.id}: {self.activated} last modified at {self.history.time if self.history else 'N/A'}>"


def list_feature_flags(page=1, per_page=10):
    '''Lista paginada de feature flags'''
    '''params:
        page: número de página
        per_page: cantidad de items por página
    returns: (flags, total)
        flags: lista de FeatureFlag
        total: cantidad total de FeatureFlag
    '''
    query = db.session.query(FeatureFlag).order_by(FeatureFlag.id)
    total = query.count()
    flags = query.offset((page - 1) * per_page).limit(per_page).all()
    return flags, total


def create_feature_flag(**kwargs):
    '''Crea un nuevo feature flag
    params:
        kwargs: atributos del feature flag'''
    user_id = kwargs.pop('user_id', None) or session.get('user_id').id
    flag = FeatureFlag(**kwargs)
    db.session.add(flag)
    db.session.commit()


    # Creo el historial a la vez que creo el feature flag
    create_feature_flag_history(flag.id, user_id=user_id)
    return flag


def update_feature_flag(id, **kwargs):
    '''Actualiza un feature flag
    params: 
        id: id del feature flag
        kwargs: atributos a actualizar
    '''
    flag = get_feature_flag(id)
    for key, value in kwargs.items():
        setattr(flag, key, value)
    db.session.commit()

    # Actualizo el historial cada vez que actualizo el feature flag
    update_feature_flag_history(flag.id, g.user.id)
    return flag

def toggle_feature_flag(id):
    '''Activa/desactiva un feature flag'''
    flag = get_feature_flag(id)
    update_feature_flag(id, activated=not flag.activated)
    return flag


def get_feature_flag(id):
    '''Obtiene un feature flag por id'''
    return db.session.query(FeatureFlag).filter(FeatureFlag.id == id).first()


def delete_feature_flag(id):
    '''Elimina un feature flag por id'''
    flag = get_feature_flag(id)
    db.session.delete(flag)
    db.session.commit()
    return flag
