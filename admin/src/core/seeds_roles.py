# src/core/seeds_roles.py
from core.database import db
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser
from core.models.user import User, create_user, read_user_by_email

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

def ensure_user(**kwargs) -> User:
    """
    Crea el usuario si no existe (create_user devuelve str),
    y SIEMPRE retorna el objeto User desde la base.
    """
    msg = create_user(**kwargs)  # "" si lo creó, texto si ya existía
    user = read_user_by_email(kwargs["email"])
    if not user:
        raise RuntimeError(f"No pude obtener el usuario {kwargs['email']}: {msg}")
    return user

def run():
    print("🌱 Seeding roles, permissions, role-permissions, users, user-roles, blocked ...")

    # Roles
    sys_admin = _get_or_create(Role, name="sys_admin")
    admin     = _get_or_create(Role, name="admin")
    editor    = _get_or_create(Role, name="editor")
    viewer    = _get_or_create(Role, name="viewer")

    # Permisos
    p_view    = _get_or_create(Permission, code="sites.view")
    p_create  = _get_or_create(Permission, code="sites.create")
    p_edit    = _get_or_create(Permission, code="sites.edit")
    p_delete  = _get_or_create(Permission, code="sites.delete")
    p_export  = _get_or_create(Permission, code="sites.export")
    p_users   = _get_or_create(Permission, code="users.manage")
    p_flags   = _get_or_create(Permission, code="feature_flags.manage")
    p_tags    = _get_or_create(Permission, code="tags.manage")
    p_history = _get_or_create(Permission, code="sites.history_view")

    db.session.commit()

    # Grant idempotente
    def grant(role, perm):
        _get_or_create(RolePermission, role_id=role.id, permission_id=perm.id)

    
    # sys_admin: todos los permisos
    for p in (p_view, p_create, p_edit, p_delete, p_users, p_flags, p_tags, p_export, p_history):
        grant(sys_admin, p)

    # admin: todos los de sitios + gestión
    for p in (p_view, p_create, p_edit, p_delete, p_users, p_tags, p_export, p_history):
        grant(admin, p)

    # editor: puede ver, crear, editar y ver historial
    for p in (p_view, p_create, p_edit, p_tags, p_history):
        grant(editor, p)

    # viewer: solo ver y ver historial
    for p in (p_view, p_history):
        grant(viewer, p)

    db.session.commit()

    # Usuarios (usar ensure_user y pasar role=<id> del rol creado arriba)
    u_sys_admin = ensure_user(email="sysadmin@fiorella.com",
                              name="System", last_name="Admin",
                              password="sysadmin123", active=True, role=sys_admin.id)

    u_admin  = ensure_user(email="admin@fiorella.com",
                           name="Admin", last_name="Root",
                           password="admin123", active=True, role=admin.id)

    u_edit1  = ensure_user(email="editor1@fiorella.com",
                           name="Elena", last_name="Editor",
                           password="editor123", active=True, role=editor.id)

    u_edit2  = ensure_user(email="editor2@fiorella.com",
                           name="Eduardo", last_name="Bloq",
                           password="editor123", active=True, role=editor.id)

    u_view1  = ensure_user(email="viewer1@fiorella.com",
                           name="Violeta", last_name="View",
                           password="viewer123", active=True, role=viewer.id)

    u_view2  = ensure_user(email="viewer2@fiorella.com",
                           name="Victor", last_name="View",
                           password="viewer123", active=True, role=viewer.id)

    # Como create_user ya crea la entrada en user_roles, NO reasignamos acá 
    db.session.commit()

    # Bloquear a editor2 (edge case) – idempotente 
    _get_or_create(BlockedUser, user_id=u_edit2.id, defaults=dict(reason="Prueba de bloqueo"))

    db.session.commit()
    print("✅ Seed de roles/usuarios completado.")
