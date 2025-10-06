from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models.userrole import UserRole as Role

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False, default=True)
    role: Mapped[Role] = mapped_column(nullable=False, default=Role.PUBLIC)
    sys_admin: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __repr__(self):
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}, {self.role}, {self.sys_admin}>"
