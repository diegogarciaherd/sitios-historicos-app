# admin/src/core/services/auth_roles.py
from functools import wraps
from flask import g, session, abort
from core.database import db
# 🔽 IMPORTS de auth (no generan ciclo)
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

# ---------- Carga del usuario en cada request ----------
def load_user():
    """
    - Lee session["user_id"] (id) y carga g.user
    - Si está bloqueado/inactivo, deja g.user = None
    - Calcula y guarda roles y permisos en g
    """
    # 🔽 import tardío para evitar ciclo con core.models.user
    from core.models.user import User

    g.user = None
    g.roles = set()
    g.perms = set()

    user_id = session.get("user_id")
    # Compatibilidad por si alguna vez se guardó un objeto en session
    if user_id and not isinstance(user_id, (int, str)):
        user_id = getattr(user_id, "id", None)

    if not user_id:
        return

    # Cargar usuario desde la base
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user or not getattr(user, "active", True):
        return

    # ¿Bloqueado?
    if db.session.query(BlockedUser).filter_by(user_id=user.id).first():
        return

    # Roles del usuario
    role_ids = {
        rid for (rid,) in db.session.query(UserRole.role_id)
        .filter(UserRole.user_id == user.id)
        .all()
    }

    if role_ids:
        g.roles = {
            name for (name,) in db.session.query(Role.name)
            .filter(Role.id.in_(role_ids))
            .all()
        }

        # Permisos por rol
        perm_ids = {
            pid for (pid,) in db.session.query(RolePermission.permission_id)
            .filter(RolePermission.role_id.in_(role_ids))
            .all()
        }
        if perm_ids:
            g.perms = {
                code for (code,) in db.session.query(Permission.code)
                .filter(Permission.id.in_(perm_ids))
                .all()
            }

    g.user = user


# ---------- Helpers para usar en Jinja y código ----------
def has_role(role: str) -> bool:
    return role in getattr(g, "roles", set())

def has_perm(code: str) -> bool:
    return code in getattr(g, "perms", set())

# Alias común para plantillas
def can(code: str) -> bool:
    return has_perm(code)

def inject_template_helpers():
    """Expone helpers y el usuario logueado a Jinja."""
    return {
        "user": getattr(g, "user", None),
        "logged_user": getattr(g, "user", None),
        "can": can,
        "has_role": has_role,
    }


# ---------- Decorador para proteger vistas ----------
def require_permission(code: str):
    """
    Uso:
        @require_permission("sites.edit")
        def edit(...):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "user", None):
                abort(401)  # no autenticado
            if not has_perm(code):
                abort(403)  # autenticado pero sin permiso
            return fn(*args, **kwargs)
        return wrapper
    return decorator

