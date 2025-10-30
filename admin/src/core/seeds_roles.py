# src/core/seeds_roles.py
from core.database import db
from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

def _get_or_create(model, defaults=None, **kwargs):
    '''Helper para obtener o crear una instancia de un modelo
    params:
        model: clase del modelo
        defaults: diccionario con valores por defecto para crear
        **kwargs: atributos para buscar la instancia
        returns: instancia del modelo
    '''
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
    '''Ejecuta el seed de roles, permisos, role-permissions, usuarios, user-roles y bloqueados.'''
    print("🌱 Seeding roles, permissions, role-permissions, users, user-roles, blocked ...")

    # imports tardíos para evitar import circular cuando se ejecuta directamente
    from core.models.user import User, create_user

    # Roles
    sys_admin = _get_or_create(Role, name="sys_admin")
    admin = _get_or_create(Role, name="admin")
    editor = _get_or_create(Role, name="editor")
    viewer = _get_or_create(Role, name="viewer")

    # Permisos
    p_view   = _get_or_create(Permission, code="sites.view")
    p_create = _get_or_create(Permission, code="sites.create")
    p_edit   = _get_or_create(Permission, code="sites.edit")
    p_delete = _get_or_create(Permission, code="sites.delete")
    p_export = _get_or_create(Permission, code="sites.export")
    p_users  = _get_or_create(Permission, code="users.manage")
    p_flags  = _get_or_create(Permission, code="feature_flags.manage")
    p_tags   = _get_or_create(Permission, code="tags.manage")

    db.session.commit()

    # Role -> Permisos (idempotente)
    def grant(r, p):
        '''Asigna un permiso a un rol de forma idempotente'''
        _get_or_create(RolePermission, role_id=r.id, permission_id=p.id)

    # sys_admin: todos los permisos
    for p in (p_view, p_create, p_edit, p_delete, p_users, p_flags, p_tags):
        '''Asigna todos los permisos al rol sys_admin'''
        grant(sys_admin, p)

    # admin: todos
    for p in (p_view, p_create, p_edit, p_delete, p_users, p_tags, p_export):
        '''Asigna todos los permisos al rol admin'''
        grant(admin, p)

    # editor: view, create, edit
    for p in (p_view, p_create, p_edit, p_tags):
        '''Asigna permisos de edición al rol editor'''
        grant(editor, p)

    # viewer: solo view
    grant(viewer, p_view)
    db.session.commit()

    # Usuarios
    '''Crea usuarios de prueba y les asigna roles'''
    u_sys_admin = create_user(email="sysadmin@fiorella.com",
                               name="System", last_name="Admin", password="sysadmin123", active=True, role=1)
    if not u_sys_admin:
        u_sys_admin = db.session.query(User).filter_by(email="sysadmin@fiorella.com").first()

    u_admin  = create_user(email="admin@fiorella.com",
                              name="Admin", last_name="Root", password="admin123", active=True, role=2)
    if not u_admin:
        u_admin = db.session.query(User).filter_by(email="admin@fiorella.com").first()

    u_edit1  = create_user(email="editor1@fiorella.com",
                              name="Elena", last_name="Editor", password="editor123", active=True, role=3)
    if not u_edit1:
        u_edit1 = db.session.query(User).filter_by(email="editor1@fiorella.com").first()

    u_edit2  = create_user(email="editor2@fiorella.com",
                              name="Eduardo", last_name="Bloq", password="editor123", active=True, role=3)
    if not u_edit2:
        u_edit2 = db.session.query(User).filter_by(email="editor2@fiorella.com").first()

    u_view1  = create_user(email="viewer1@fiorella.com",
                              name="Violeta", last_name="View", password="viewer123", active=True, role=4)
    if not u_view1:
        u_view1 = db.session.query(User).filter_by(email="viewer1@fiorella.com").first()

    u_view2  = create_user(email="viewer2@fiorella.com",
                              name="Victor", last_name="View", password="viewer123", active=True, role=4)
    if not u_view2:
        u_view2 = db.session.query(User).filter_by(email="viewer2@fiorella.com").first()

    db.session.commit()

    # Asignación de roles
    def assign(user, role):
        '''Asigna un rol a un usuario de forma idempotente'''
        _get_or_create(UserRole, user_id=user.id, role_id=role.id)

    assign(u_sys_admin, sys_admin)
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
