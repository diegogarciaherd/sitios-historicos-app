# src/core/services/auth_roles.py
from functools import wraps
from flask import g, session, redirect, url_for, flash
from core.database import db
from core.models.user import User
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

# --------- helpers de estado ---------
def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def is_blocked(user: User) -> bool:
    if not user:
        return False
    return db.session.query(BlockedUser).filter_by(user_id=user.id).first() is not None

def has_role(user: User, role_name: str) -> bool:
    if not user:
        return False
    q = (
        db.session.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id, Role.name == role_name)
        .exists()
    )
    return db.session.query(q).scalar()

def has_perm(user: User, perm_code: str) -> bool:
    if not user:
        return False
    q = (
        db.session.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id, Permission.code == perm_code)
        .exists()
    )
    return db.session.query(q).scalar()

# --------- decoradores ---------
def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Tenés que iniciar sesión.", "error")
            return redirect(url_for("login.login"))
        if is_blocked(g.user):
            session.clear()
            flash("Tu usuario está bloqueado.", "error")
            return redirect(url_for("login.login"))
        return view(*args, **kwargs)
    return wrapper

def require_permission(perm_code: str):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not g.user:
                flash("Tenés que iniciar sesión.", "error")
                return redirect(url_for("login.login"))
            if not has_perm(g.user, perm_code):
                flash("No tenés permisos para realizar esta acción.", "error")
                return redirect(url_for("home"))
            return view(*args, **kwargs)
        return wrapper
    return decorator

# --------- integración con Flask ---------
def load_user():
    g.user = current_user()

def inject_template_helpers():
    return dict(
        can=lambda code: has_perm(getattr(g, "user", None), code),
        has_role=lambda name: has_role(getattr(g, "user", None), name),
        current_user=lambda: getattr(g, "user", None),
    )
