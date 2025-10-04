from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, Column

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id = Column(Integer, ForeignKey("users.id"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    activated: Mapped[bool] = mapped_column(nullable=False, default=False)
    description: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<Feature Flag {self.id}: {self.activated}>"
