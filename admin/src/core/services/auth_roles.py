<<<<<<< HEAD
# src/core/services/auth_roles.py
=======
# src/core/services/authz.py
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
from functools import wraps
from flask import g, session, redirect, url_for, flash
from core.database import db
from core.models.user import User
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

<<<<<<< HEAD
# --------- helpers de estado ---------
def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

=======

# --------- helpers de estado ---------
def current_user():
    """Devuelve el usuario logueado o None."""
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
def is_blocked(user: User) -> bool:
    if not user:
        return False
    return db.session.query(BlockedUser).filter_by(user_id=user.id).first() is not None

<<<<<<< HEAD
=======

>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
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

<<<<<<< HEAD
def has_perm(user: User, perm_code: str) -> bool:
=======

def has_perm(user: User, perm_code: str) -> bool:
    """¿Alguno de los roles del usuario tiene este permiso?"""
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
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

<<<<<<< HEAD
# --------- decoradores ---------
=======

# --------- decoradores para vistas ---------
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Tenés que iniciar sesión.", "error")
<<<<<<< HEAD
            return redirect(url_for("login.login"))
=======
            return redirect(url_for("login.login"))  # endpoint de tu login_bp
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
        if is_blocked(g.user):
            session.clear()
            flash("Tu usuario está bloqueado.", "error")
            return redirect(url_for("login.login"))
        return view(*args, **kwargs)
    return wrapper

<<<<<<< HEAD
def require_permission(perm_code: str):
=======

def require_permission(perm_code: str):
    """Protege rutas con un permiso concreto, ej: 'sites.edit'."""
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
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

<<<<<<< HEAD
# --------- integración con Flask ---------
def load_user():
    g.user = current_user()

def inject_template_helpers():
=======

# --------- integración con Flask ---------
def load_user():
    """Hook para cargar g.user en cada request."""
    g.user = current_user()
    # Si querés forzar salida de bloqueados en cada request, descomentá:
    # if g.user and is_blocked(g.user):
    #     session.clear()
    #     flash("Tu usuario está bloqueado.", "error")
    #     return redirect(url_for("login.login"))


def inject_template_helpers():
    """Helpers para Jinja: can('perm'), has_role('admin') y current_user."""
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
    return dict(
        can=lambda code: has_perm(getattr(g, "user", None), code),
        has_role=lambda name: has_role(getattr(g, "user", None), name),
        current_user=lambda: getattr(g, "user", None),
    )
