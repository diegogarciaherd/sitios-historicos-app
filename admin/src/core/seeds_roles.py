# src/core/seeds_roles.py
from core.database import db
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser
from core.models.user import User

def _get_or_create(model, defaults=None, **kwargs):
    inst = db.session.query(model).filter_by(**kwargs).first()
    if inst:
        return inst
    params = {**kwargs}
    if defaults:
        params.update(defaults)
    inst = model(**params)
    db.session.add(inst)
    db.session.flush()
    return inst

def run():
    print("🌱 Seeding roles, permissions, role-permissions, users, user-roles, blocked ...")

    # Roles
    admin = _get_or_create(Role, name="admin")
    editor = _get_or_create(Role, name="editor")
    viewer = _get_or_create(Role, name="viewer")

    # Permisos
    p_view   = _get_or_create(Permission, code="sites.view")
    p_create = _get_or_create(Permission, code="sites.create")
    p_edit   = _get_or_create(Permission, code="sites.edit")
    p_delete = _get_or_create(Permission, code="sites.delete")
    p_users  = _get_or_create(Permission, code="users.manage")

    db.session.commit()

    # Role -> Permisos (idempotente)
    def grant(r, p):
        _get_or_create(RolePermission, role_id=r.id, permission_id=p.id)

    # admin: todos
    for p in (p_view, p_create, p_edit, p_delete, p_users):
        grant(admin, p)

    # editor: view, create, edit
    for p in (p_view, p_create, p_edit):
        grant(editor, p)

    # viewer: solo view
    grant(viewer, p_view)
    db.session.commit()

    # Usuarios
    u_admin  = _get_or_create(User, email="admin@fiorella.com",
                              defaults=dict(name="Admin", last_name="Root", password="admin123", active=True))
    u_edit1  = _get_or_create(User, email="editor1@fiorella.com",
                              defaults=dict(name="Elena", last_name="Editor", password="editor123", active=True))
    u_edit2  = _get_or_create(User, email="editor2@fiorella.com",
                              defaults=dict(name="Eduardo", last_name="Bloq", password="editor123", active=True))
    u_view1  = _get_or_create(User, email="viewer1@fiorella.com",
                              defaults=dict(name="Violeta", last_name="View", password="viewer123", active=True))
    u_view2  = _get_or_create(User, email="viewer2@fiorella.com",
                              defaults=dict(name="Victor", last_name="View", password="viewer123", active=True))
    u_norole = _get_or_create(User, email="norole@fiorella.com",
                              defaults=dict(name="Nora", last_name="NoRole", password="norole123", active=True))

    db.session.commit()

    # Asignación de roles
    def assign(user, role):
        _get_or_create(UserRole, user_id=user.id, role_id=role.id)

    assign(u_admin, admin)
    assign(u_edit1, editor)
    assign(u_edit2, editor)
    assign(u_view1, viewer)
    assign(u_view2, viewer)
    # u_norole: sin rol a propósito

    db.session.commit()

    # Bloquear a editor2 (edge case)
    _get_or_create(BlockedUser, user_id=u_edit2.id, defaults=dict(reason="Prueba de bloqueo"))

    db.session.commit()
    print("✅ Seed de roles/usuarios completado.")
