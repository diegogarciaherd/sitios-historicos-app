# src/core/seeds_roles.py
from core.database import db
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser
from core.models.user import User

def run():
    print("🌱 Seeding roles, permissions, and admin user...")

    # --- Roles ---
    roles = {
        "admin": Role(name="admin"),
        "editor": Role(name="editor"),
        "viewer": Role(name="viewer")
    }

    db.session.add_all(roles.values())
    db.session.commit()

    # --- Permisos ---
    permissions = [
        Permission(code="sites.view"),
        Permission(code="sites.create"),
        Permission(code="sites.edit"),
        Permission(code="sites.delete"),
        Permission(code="users.manage"),
    ]
    db.session.add_all(permissions)
    db.session.commit()

    # --- Asignar permisos a roles ---
    role_perms = [
        # Admin: todos los permisos
        *[RolePermission(role_id=roles["admin"].id, permission_id=p.id) for p in permissions],
        # Editor: solo view, create, edit
        *[RolePermission(role_id=roles["editor"].id, permission_id=p.id)
          for p in permissions if p.code in ["sites.view", "sites.create", "sites.edit"]],
        # Viewer: solo ver
        RolePermission(role_id=roles["viewer"].id,
                       permission_id=next(p.id for p in permissions if p.code == "sites.view"))
    ]
    db.session.add_all(role_perms)
    db.session.commit()

    # --- Usuario admin ---
    admin = User(
        email="admin@fiorella.com",
        name="Admin",
        last_name="Principal",
        password="admin123",  # NOTA: en producción usar hash
        active=True
    )
    db.session.add(admin)
    db.session.commit()

    # --- Asignar rol admin al usuario ---
    db.session.add(UserRole(user_id=admin.id, role_id=roles["admin"].id))
    db.session.commit()

    print("✅ Roles, permisos y usuario admin creados correctamente.")
