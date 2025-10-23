from core.database import Base, db
from sqlalchemy import ForeignKey, Integer, Column, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from typing import  TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from core.models.user import User
    from core.models.feature_flags import FeatureFlag

class FeatureFlagHistory(Base):
    '''Modelo de historial de cambios de Feature Flags'''
    ''' atributos:
    - id: Identificador único del historial
    - time: Fecha y hora del cambio
    - user_id: FK al usuario que hizo el cambio
    - feature_flag_id: FK a la feature flag modificada
    una relación con User y FeatureFlag
    '''
    __tablename__ = "feature_flags_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=True, default=datetime.datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # El id de la feature flag coincide con el id del historial
    feature_flag_id = Column(Integer, ForeignKey("feature_flags.id"), nullable=False)
    
    # Guardo el objeto de user
    user: Mapped["User"] = relationship("User", back_populates="feature_flags_history")
    feature_flag: Mapped["FeatureFlag"] = relationship("FeatureFlag", back_populates="history")

    def __repr__(self):
        '''Representación en string del historial de Feature Flag'''
        return f"<Feature Flag History for {self.id}: {self.time} by User {self.user.email}>"
    
def create_feature_flag_history(feature_flag_id: int, user_id: int):
    '''Crea un nuevo historial para una feature flag'''
    history_entry = FeatureFlagHistory(
        feature_flag_id=feature_flag_id,
        user_id=user_id,
        time=datetime.datetime.now()
    )
    db.session.add(history_entry)
    db.session.commit()
    return history_entry

def update_feature_flag_history(feature_flag_id: int, user_id: int):
    '''Actualiza el historial de una feature flag'''
    # Actualizo el usuario y tiempo del historial de la feature flag
    history_entry = get_feature_flag_history(feature_flag_id)
    history_entry.user_id = user_id
    history_entry.time = datetime.datetime.now()
    db.session.commit()
    return history_entry

def get_feature_flag_history(feature_flag_id: int):
    '''Obtiene el historial de una feature flag por su id'''
    return db.session.query(FeatureFlagHistory).filter(FeatureFlagHistory.feature_flag_id == feature_flag_id).first()