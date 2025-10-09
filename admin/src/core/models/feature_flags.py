from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    activated: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __repr__(self):
        return f"<Feature Flag {self.id}: {self.activated}>"
