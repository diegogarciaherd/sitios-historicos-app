# src/core/services/auth_service.py
from core.database import db
from core.models.user import User
from core.models.feature_flags import FeatureFlag
from core.services.bcrypt import bcrypt
from flask import session, g
from core.services.auth_roles import has_role
from core.models.auth import LogicallyDeletedUser


def authenticate(email: str, password: str) -> tuple[User | None, str]:
    """
    Valida las credenciales del usuario contra la base de datos.

    Args:
        email (str): Correo electrónico del usuario.
        password (str): Clave en texto plano, tal como la ingresó el usuario.

    Returns:
        tuple[User | None, str]:
            - user: instancia de User si las credenciales son válidas,
              o None en caso contrario.
            - error: mensaje de error en castellano si algo falla
              (cadena vacía "" cuando está todo ok).
    """
    user = db.session.query(User).filter_by(email=email).first()
    error = ""

    # Usuario inexistente o contraseña incorrecta
    if not (user and bcrypt.check_password_hash(user.password, password)):
        error = "Correo electronico o clave incorrectos."

    # Usuario desactivado
    if user and (not user.active):
        error = (
            "Tu cuenta se encuentra desactivada.\n"
            "Contacta a un administrador para reactivarla."
        )

    # Usuario eliminado lógicamente
    if user:
        is_deleted = (
            db.session.query(LogicallyDeletedUser)
            .filter_by(user_id=user.id)
            .first()
        )
        if is_deleted:
            error = (
                "Tu cuenta ha sido eliminada.\n"
                "Contacta a un administrador para mas informacion."
            )

    return user, error


def check_flags(user: User | None):
    """Verifica si el sistema administrativo está activado mediante feature flag."""
    flag = db.session.query(FeatureFlag).filter_by(name="Sistema administrativo").first()
    activated = flag.activated if flag else False
    if not activated:
        return False
    if user:
        return not has_role("sys_admin")
    return True


def load_user():
    """Carga el usuario logueado en flask.g antes de cada request."""
    user_id = session.get("user_id")
    g.user = db.session.query(User).filter_by(id=user_id).first() if user_id else None


def get_logged_user():
    """Devuelve el usuario actualmente logueado desde flask.g."""
    return getattr(g, "user", None)
