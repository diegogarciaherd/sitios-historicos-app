# src/core/seeds_roles.py
from core.database import db
from core.models.auth import Role, Permission, RolePermission, UserRole
from core.models.user import User

def _get_or_create(model, **kwargs):
    inst = model.query.filter_by(**kwargs).first()
    if inst: return inst
    inst = model(**kwargs)
    db.session.add(inst)
    db.session.commit()
    return inst

def run():
    print("🌱 Seeding roles/permissions/admin (idempotente)...")

    # Roles
    admin  = _get_or_create(Role, name="admin")
    editor = _get_or_create(Role, name="editor")
    viewer = _get_or_create(Role, name="viewer")

    # Permisos
    perm_codes = [
        # sitios
        "sites_index", "sites_show", "sites_create", "sites_update", "sites_destroy",
        # usuarios (solo admin)
        "user_index", "user_show", "user_new", "user_update", "user_destroy",
    ]
    perms = {c: _get_or_create(Permission, code=c) for c in perm_codes}

    # Asignación
    def grant(role, codes):
        for code in codes:
            if not RolePermission.query.filter_by(role_id=role.id, permission_id=perms[code].id).first():
                db.session.add(RolePermission(role_id=role.id, permission_id=perms[code].id))
        db.session.commit()

    # admin: todo
    grant(admin, perm_codes)
    # editor: sólo sitios (no usuarios)
    grant(editor, ["sites_index","sites_show","sites_create","sites_update"])
    # viewer: sólo ver
    grant(viewer, ["sites_index","sites_show"])

    # usuario admin por defecto
    admin_user = User.query.filter_by(email="admin@fiorella.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@fiorella.com",
            name="Admin", last_name="Principal",
            password="admin123",  # <— recuerda hashear en login/alta!
            active=True
        )
        db.session.add(admin_user); db.session.commit()
    if not UserRole.query.filter_by(user_id=admin_user.id, role_id=admin.id).first():
        db.session.add(UserRole(user_id=admin_user.id, role_id=admin.id)); db.session.commit()

    print("✅ Listo.")
