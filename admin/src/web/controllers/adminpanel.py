from flask import Blueprint, request, render_template, flash, redirect, url_for
from core.models.userrole import UserRole
from core.models.user import create_user as create, read_user_by_email, read_users_by
from core.models.user import update_user, delete_user, list_all_users
from core.services.auth_roles import require_permission
from web.decorators.loginrequired import login_required
from web.decorators.permissionrequired import role_required
from flask import session

adminpanel_bp = Blueprint("adminpanel", "adminpanel", url_prefix="/panel-de-admin", template_folder="../templates")

@adminpanel_bp.route("/", methods=["GET"])
@require_permission("users.manage")
def admin_panel():
    '''Renderiza la página principal del panel de administración'''
    return render_template("adminpanel.html")

def validate_user_data(form_data: dict, is_update=False) -> dict:
    '''Valida y procesa los datos del formulario para crear o actualizar un usuario'''
    form_data["active"] = True
    errors = []
    data = {}

    required_fields = ["email", "name", "last_name", "password", "role"]
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"El campo {field} es obligatorio")
    
    if errors:
        raise Exception("; ".join(errors))

    try:
        data["email"] = form_data["email"].strip()
        data["name"] = form_data["name"].strip()
        data["last_name"] = form_data["last_name"].strip()
        data["password"] = form_data["password"]
        data["active"] = form_data["active"]
        data["role"] = UserRole[form_data["role"]]
    except Exception as e:
        raise Exception(f"Error en el formato de los datos: {str(e)}")
    
    return data

@adminpanel_bp.route("/buscar-usuarios", methods=["GET", "POST"])
@require_permission("users.manage")
def list_users() -> str:
    '''Lista y busca usuarios en el panel de administración'''
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        per_page = 25
        users, total = list_all_users(page=page, per_page=per_page)

        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next,
            "prev_num": prev_num,
            "next_num": next_num
        }
        return render_template("searchuser.html", users=users if users else None)
    else: #request.method == POST
        users = []
        search_option = request.form.keys()
        print(search_option)
        if "email" in search_option:
            email = request.form.get("email")
            result = read_user_by_email(email)
            if result:
                users.append(result)

        elif "actividad" or "rol" in search_option:
            act = request.form.get("actividad")
            match act:
                case "activo":
                    act = True
                case "inactivo":
                    act = False
                case "any":
                    act = None

            role = request.form.get("rol")
            match role:
                case "public":
                    role = UserRole.PUBLIC
                case "editor":
                    role = UserRole.EDITOR
                case "admin":
                    role = UserRole.ADMIN
                case "any":
                    role = None
            if (act is None and role is None):
                users = list_all_users()[0]
            else:
                users = read_users_by(role, act)

        if not users:
            users = None

        return render_template("searchuser.html", users=users)

@adminpanel_bp.route("/crear-usuario", methods=["GET", "POST"])
@require_permission("users.manage")
def create_user() -> str:
    '''Crea un nuevo usuario desde el panel de administración'''
    if request.method == "POST":
        try:
            data = validate_user_data(request.form.to_dict())
            create(**data)
            print("El usuario fue creado correctamente", "success")
            return redirect(url_for("adminpanel.list_users"))
        except Exception as e:
            print(f"Error al crear el usuario: {str(e)}", "error")

    return render_template("createuser.html")

@adminpanel_bp.route("/editar-usuario/<int:id>", methods=["GET", "POST"])
@require_permission("users.manage")
def edit_user(id):    
    '''Edita un usuario existente desde el panel de administración'''
    if request.method == "POST":
        try:
            data = validate_user_data(request.form)
            updated_user = update_user(id, **data)
            flash("Usuario editado correctamente.", "success")
            return redirect(url_for("panel-de-admin"))
        except ValueError as e:
            flash(str(e), "error")

    return render_template("edituser.html", logged_user=session['user_id'] if 'user_id' in session else None)

@adminpanel_bp.route("/eliminar-usuario/<int:id>", methods=["POST"])
@require_permission("users.manage")
def del_user(id: int):
    '''Elimina un usuario desde el panel de administración'''
    delete_user(id)
    return redirect(url_for("adminpanel.list_users"))
