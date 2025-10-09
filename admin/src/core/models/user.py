from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.models.userrole import UserRole as Role
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.feature_flags_history import FeatureFlagHistory

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=True, default=True)
    role: Mapped[Role] = mapped_column(nullable=True, default=Role.PUBLIC)
    sys_admin: Mapped[bool] = mapped_column(nullable=True, default=False)    
    feature_flags_history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}, {self.role}, {self.sys_admin}>"
