from core.database import Base, db
from sqlalchemy import ForeignKey, Integer, Column, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from typing import  TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.user import User
    from core.models.feature_flags import FeatureFlag

class FeatureFlagHistory(Base):
    __tablename__ = "feature_flags_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feature_flag_id = Column(Integer, ForeignKey("feature_flags.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="feature_flags_history")
    feature_flag: Mapped["FeatureFlag"] = relationship("FeatureFlag", back_populates="history")

    def __repr__(self):
        return f"<Feature Flag History for {self.id}: {self.time} by User {self.user.email}>"