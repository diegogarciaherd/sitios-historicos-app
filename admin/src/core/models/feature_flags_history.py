from core.database import Base, db
from sqlalchemy import ForeignKey, Integer, Column, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from typing import  TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from core.models.user import User
    from core.models.feature_flags import FeatureFlag

class FeatureFlagHistory(Base):
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
        return f"<Feature Flag History for {self.id}: {self.time} by User {self.user.email}>"
    
def create_feature_flag_history(feature_flag_id: int, user_id: int):
    history_entry = FeatureFlagHistory(
        feature_flag_id=feature_flag_id,
        user_id=user_id,
        time=datetime.datetime.now()
    )
    db.session.add(history_entry)
    db.session.commit()
    return history_entry

def update_feature_flag_history(feature_flag_id: int, user_id: int):
    # Actualizo el usuario y tiempo del historial de la feature flag
    history_entry = get_feature_flag_history(feature_flag_id)
    history_entry.user_id = user_id
    history_entry.time = datetime.datetime.now()
    db.session.commit()
    return history_entry

def get_feature_flag_history(feature_flag_id: int):
    return db.session.query(FeatureFlagHistory).filter(FeatureFlagHistory.feature_flag_id == feature_flag_id).first()