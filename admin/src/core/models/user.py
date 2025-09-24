from core.models.userrole import UserRole as Role

class User():
    __tablename__ = "users"
    id: int
    email: str
    name: str
    last_name: str
    password: str
    active: bool
    role: Role
# cuando este la base de datos, esto se modifica para
# acoplarlo a postrges y que se cree la tabla de usuarios