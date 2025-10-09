# admin/src/core/services/auth_roles.py
from functools import wraps
from flask import g, session, abort
from core.database import db
from core.models.user import User
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

# ---------- Carga del usuario en cada request ----------
def load_user():
    """
    - Lee session["user_id"] (email) y carga g.user
    - Si está bloqueado/inactivo, deja g.user = None
    - Calcula y guarda roles y permisos en g
    """
    g.user = None
    g.roles = set()
    g.perms = set()

    email = session.get("user_id")
    if not email:
        return

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.active:
        return

    # Bloqueado?
    blocked = db.session.query(BlockedUser).filter_by(user_id=user.id).first()
    if blocked:
        return

    # Roles del usuario
    role_ids = (
        db.session.query(UserRole.role_id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    role_ids = {rid for (rid,) in role_ids}

    if role_ids:
        role_names = db.session.query(Role.name).filter(Role.id.in_(role_ids)).all()
        g.roles = {name for (name,) in role_names}

        # Permisos por rol
        perm_ids = (
            db.session.query(RolePermission.permission_id)
            .filter(RolePermission.role_id.in_(role_ids))
            .all()
        )
        perm_ids = {pid for (pid,) in perm_ids}
        if perm_ids:
            codes = db.session.query(Permission.code).filter(Permission.id.in_(perm_ids)).all()
            g.perms = {c for (c,) in codes}

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
    """
    Expone helpers y el usuario logueado a Jinja.
    """
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
                abort(401)
            if not has_perm(code):
                abort(401)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
