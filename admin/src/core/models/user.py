from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db
from core.services.bcrypt import bcrypt
from core.database import Base
from typing import TYPE_CHECKING, ClassVar
from core.models.auth import UserRole, LogicallyDeletedUser

if TYPE_CHECKING:
    from core.models.feature_flags_history import FeatureFlagHistory

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
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=True, default=True)
    role_id: ClassVar[int]
    feature_flags_history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        '''Representación en string del Usuario'''
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}, ROLE_ID: {self.role_id}>"

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
    Busca un usuario en la base de datos a partir de su ID, el cual es
    manejado por la misma base de datos.

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

def read_users_by_activeness(active: bool, page: int=1, per_page: int=10) -> list[User] | None:
    """
    Busca todos aquellos usuarios que cumplan con el criterio dado
    por "active". Si active=True, seran todos los usuarios que
    se encuentren activos en el sistema, en caso contrario, todos
    aquellos que se encuentren inactivos/bloqueados.

    Args:
        active (bool): True para usuarios activos, False para usuarios
        inactivos.

        page (int): TBD

        per_page (int): TBD

    Returns:
        La lista de usuarios que cumplen con el criterio, y el numero
        de tuplas devueltas en la consulta, o None si no hay resultados.
    """
    query = db.session.query(User).filter_by(active=active).all()
    roles = UserRole.get_all_relations()
    for u in query:
        u.role_id = roles[u.id].role_id

    return query

def read_users_by_role(role: str, page: int=1, per_page: int=10) -> list[User] | None:
    """
    Busca todos los usuarios que cumplan con el criterio dado por "role".

    Args:
        role (str): El rol por el que se quiere filtrar (public, editor, admin).

        page (int): TBD

        per_page (int): TBD

    Returns:
        La lista de usuarios que cumplen con el criterio, y el numero
        de tuplas devueltas en la consulta o None si no hay resultados.
    """
    query = db.session.query(User).filter_by(role=role).all()
    roles = UserRole.get_all_relations()
    for u in query:
        u.role_id = roles[u.id-1].role_id

    return query

def read_users_by(role: str | None, active: bool | None) -> list[User]:
    """
    Realiza la consulta en base a los argumentos. Puede ser filtrar por
    rol y actividad, solo por rol, o solo por actividad.

    Args:
        role (str): El rol, si quiere incluirse como criterio. Puede ser
        None.

        active (bool): Si esta activo o no. Tambien puede ser None.

    Returns:
        La lista de usuarios que cumplan con los criterios dados por
        los argumentos, o None si no hay resultados.
    """
    query = None
    if (role is not None and active is None):
        query = db.session.query(User).filter_by(role=role).all()
    if (active is not None and role is None):
        query = db.session.query(User).filter_by(active=active).all()
    if (role is not None and active is not None):
        query = db.session.query(User).filter_by(role=role).filter_by(active=active).all()
    roles = UserRole.get_all_relations()
    for u in query:
        u.role_id = roles[u.id-1].role_id
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
    new_role = kwargs.pop("role")
    db.session.query(User).filter_by(id=id).update(kwargs)
    UserRole.modify_user_role(id, new_role)
    db.session.commit()
    return ""

def delete_user(id: int):
    """
    Elimina un usuario de la base de datos.

    Args:
        id (int): El id del usuario que se quiere eliminar.

    ((Hace un borrado fisico. Cambiar para que sea logico en su lugar))
    """
    LogicallyDeletedUser.add_new_user(id)

def list_all_users(page: int=1, per_page: int=10) -> list[User]:
    """
    Busca todos los usuarios de la base de datos sin discriminacion alguna.

    Args:
        page (int): TBD

        per_page (int): TBD

    Returns:
        Una lista con todos los usuarios existentes, y el total de la
        busqueda.
    """
    query = db.session.query(User).all()
    roles = UserRole.get_all_relations()
    for u in query:
        u.role_id = roles[u.id-1].role_id
    return query
