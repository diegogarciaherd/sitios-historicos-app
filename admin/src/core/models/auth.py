# src/core/models/auth.py
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from core.database import Base  # usa DeclarativeBase
# IMPORTANTE: la tabla users ya existe en otro módulo.
# Solo la referenciamos por FK sin definir el modelo acá.


#Acá creamos roles, permissions, role_permissions, user_roles y blocked_users. Todo referenciado por FK a users.id.

class Role(Base):
    '''Modelo de rol de usuario
    atributos:
    - id: Identificador único del rol
    - name: Nombre del rol (ej: admin, editor)
    '''
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # ej: admin, editor
    # helper
    def __repr__(self):
        ''' Representación del rol ''' 
        return f"<Role {self.name}>"

class Permission(Base):
    '''Modelo de permiso
    atributos:
     - id: Identificador único del permiso
     - code: Código del permiso (ej: user_index)
    '''
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)  # patron modulo_accion, ej: user_index
    def __repr__(self): return f"<Perm {self.code}>"

class RolePermission(Base):
    '''Asociación entre roles y permisos
    atributos:
     - id: Identificador único de la asociación
     - role_id: FK al rol
     - permission_id: FK al permiso
    '''
    __tablename__ = "role_permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_perm"),)

class UserRole(Base):
    '''Asociación entre usuarios y roles
    atributos:
     - id: Identificador único de la asociación
     - user_id: FK al usuario
     - role_id: FK al rol
    '''
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

class BlockedUser(Base):
    """
    En lugar de agregar un campo a users, usamos una tabla auxiliar.
    Si un registro existe aquí, el usuario está bloqueado.
    atributos:
    - id: Identificador único del bloqueo
    - user_id: FK al usuario bloqueado
    - reason: Razón del bloqueo
    - created_at: Fecha y hora del bloqueo
    """
    __tablename__ = "blocked_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
