
from __future__ import annotations

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db
from core.services.bcrypt import bcrypt
from typing import TYPE_CHECKING, ClassVar, List
from core.models.auth import UserRole, LogicallyDeletedUser
from datetime import datetime
from sqlalchemy import DateTime

# No importamos Favorite en runtime para evitar import circular
if TYPE_CHECKING:
    from core.models.feature_flags_history import FeatureFlagHistory
    from core.models.favorites import Favorite


class User(Base):
    '''Modelo de usuario
    atributos:
    - id: Identificador único del usuario
    - email: Email del usuario
    - name: Nombre del usuario
    - last_name: Apellido del usuario
    - password: Contraseña hasheada del usuario
    - active: Estado del usuario (activo/inactivo)
    - role: Rol del usuario (admin, editor, public)
    - sys_admin: Indica si el usuario es administrador del sistema
    feature_flags_history: Relación con el historial de cambios de feature flags realizados por el usuario
    '''
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(nullable=True, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    role_id: ClassVar[int]
    deleted: ClassVar[bool]

    feature_flags_history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        '''Representación en string del Usuario'''
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}>"
    
    def to_dict(self) -> dict:
        '''Convierte el objeto Usuario a un diccionario'''
        return {
            "name": self.name,
            "last_name": self.last_name,
        }

def create_user(**kwargs: dict) -> str:
    """
    Crea un nuevo usuario a partir de los datos recibidos y lo persiste
    en la base de datos.

    Args:
        kwargs (dict): Los datos del usuario a ser creado.
    
    Returns:
        str: Describiendo el error (si hubo).
    """
    email = kwargs["email"]
    existente = db.session.query(User).filter_by(email=email).first()
    if existente:
        return "El correo electronico ingresado ya se encuentra en uso."
    else:
        if "role" in kwargs:
            role_id = kwargs.pop("role")
        kwargs["password"] = bcrypt.generate_password_hash(kwargs["password"]).decode("utf-8")
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        
        # Hago .pop() de role para que el constructor de User no reciba un parametro inesperado
        # y despues estas dos lineas magicas obtienen el id del usuario recien creado, para
        # utilizarlo en crear una nueva entrada en la tabla user_role.
        new_user_id = read_user_by_email(kwargs["email"]).id
        UserRole.create_entry(new_user_id, role_id)

        return ""
    
def get_user_by_id(id: int) -> User | None:
    """
    Busca un usuario en la base de datos a partir de su id.

    Args:
        id (int): El numero que identifica univocamente al usuario.

    Returns:
        User: Si encuentra un usuario con ese id.

        None: Si no pudo encontrar un usuario con id.
    """
    user = db.session.query(User).filter_by(id=id).first()
    if user:
        user.role_id = UserRole.get_user_role(user.id).role_id
    return user

def read_user_by_email(email: str) -> User | None:
    """
    Busca un usuario en la base de datos a partir de su email (unico).

    Args:
        email (str): El email correspondiente al usuario que se necesita.

    Returns:
        User: Si el email ingresado coincide con un usuario.

        None: Si no pudo encontrarse un usuario con ese email.
    """
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        user.role_id = UserRole.get_user_role(user.id)
    return user

def read_users_by(params: dict) -> list[User]:
    """
    Realiza una consulta filtrada en base a los params.

    Args:
        params (dict): Los filtros de busqueda.

    Returns:
        La lista de usuarios que cumplan con los criterios dados por
        los argumentos, o None si no hay resultados.
    """
    query_conditions = []
    if params["email"]:
        query_conditions.append(User.email.ilike(f"%{params['email']}%"))
    if params["activity"] is not None:
        query_conditions.append(User.active == params["activity"])
    if params["role"] is not None:
        query_conditions.append(UserRole.role_id == params["role"])

    if params["order-by"] == "newest-first":
        query = db.session.query(User).join(UserRole, User.id == UserRole.id).filter(*query_conditions).order_by(User.created_at.desc()).all()
    elif params["order-by"] == "oldest-first":
        query = db.session.query(User).join(UserRole, User.id == UserRole.id).filter(*query_conditions).order_by(User.created_at.asc()).all()

    roles = UserRole.get_all_relations()
    is_deleted = LogicallyDeletedUser.get_all()
    deleted_ids = {u.user_id for u in is_deleted}
    for u in query:
        u.role_id = roles[u.id-1].role_id
        u.deleted = u.id in deleted_ids

    return query

def update_user(id: int, **kwargs: dict) -> str:
    """
    Actualiza la informacion de un usuario en la base de datos.

    Args:
        id (int): El id del usuario que se va a modificar.

        kwargs (dict): Los nuevos datos.

    Returns:
        str: Mensaje de error si se produjo alguno.
    """
    new_email = kwargs["email"]
    old_email = db.session.query(User).filter_by(id=id).first().email
    if old_email != new_email:
        exists = db.session.query(User).filter_by(email=new_email).first()
        if exists:
            return "El correo electronico ingresado ya se encuentra en uso."
    if kwargs["password"]:
        kwargs["password"] = bcrypt.generate_password_hash(kwargs["password"]).decode("utf-8")
    else:
        kwargs.pop("password")
    new_role = kwargs.pop("role")
    if "deleted" in kwargs:
        kwargs.pop["deleted"]
    db.session.query(User).filter_by(id=id).update(kwargs)
    UserRole.modify_user_role(id, new_role)
    db.session.commit()
    return ""

def delete_user(id: int):
    """
    Elimina un usuario de la base de datos, no literalmente, sino que
    lo agrega a una tabla que contiene los id de usuarios eliminados
    logicamente.

    Args:
        id (int): El id del usuario que se quiere eliminar.
    """
    LogicallyDeletedUser.add_new_user(id)

def list_all_users() -> list[User]:
    """
    Busca todos los usuarios de la base de datos sin discriminacion alguna.

    Args:
        page (int): TBD

        per_page (int): TBD

    Returns:
        Una lista con todos los usuarios existentes, y el total de la
        busqueda.
    """
    query = db.session.query(User).order_by(User.created_at.asc()).all()
    roles = UserRole.get_all_relations()
    is_deleted = LogicallyDeletedUser.get_all()
    deleted_ids = {u.user_id for u in is_deleted}
    for u in query:
        u.role_id = roles[u.id-1].role_id
        u.deleted = u.id in deleted_ids

    return query

def create_user_from_google_auth(data: dict):
    data["last_name"] = " "
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    new_user_id = read_user_by_email(data["email"]).id
    UserRole.create_entry(new_user_id, 4)
