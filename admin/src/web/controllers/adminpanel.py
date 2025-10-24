from flask import Blueprint, request, render_template, flash, redirect, url_for
from core.models.userrole import UserRole
from core.models.user import create_user as create, read_user_by_email, read_users_by
from core.models.user import update_user, delete_user, list_all_users, get_user_by_id
from core.services.auth_roles import require_permission
from flask import session

adminpanel_bp = Blueprint("adminpanel", "adminpanel", url_prefix="/panel-de-admin", template_folder="../templates")

@adminpanel_bp.route("/", methods=["GET"])
@require_permission("users.manage")
def admin_panel() -> str:
    """
    Puerta de entrada al panel de administrador.
    """
    return render_template("adminpanel.html")

def validate_user_data(form_data: dict) -> dict:
    """
    Sanitiza los datos recibidos del front-end, quitandoles los espacios
    en blanco y asegurandose de que los requeridos estan.

    Args:
        form_data (dict): Los datos a validar.

    Returns:
        dict: Los datos validados.
    """
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
    """
    Lista los usuarios existentes.
    """
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
    else:
        users = []
        search_option = request.form.keys()
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
    """
    Funcionalidad que permite crear un nuevo usuario.
    """
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
def edit_user(id: int) -> str:
    """
    Edita un usuario de la base de datos con los datos recibidos del
    front-end.

    Args:
        id (int): El id del usuario que se quiere editar.
    """
    if request.method == "POST":
        data, error = validate_edit_request_data(request.form.to_dict())
        if not error:
            error = update_user(id, **data)
        if not error:
            flash("Usuario editado correctamente.", "success")
        else:
            flash(error, "error")
        return render_template("edituser.html", user=data, edit=True, logged_user=session["user_id"] if "user_id" in session else None)
    else:
        user_to_edit = get_user_by_id(id)
        return render_template("edituser.html", user=user_to_edit, edit=True, logged_user=session['user_id'] if 'user_id' in session else None)

@adminpanel_bp.route("/eliminar-usuario/<int:id>", methods=["POST"])
@require_permission("users.manage")
def del_user(id: int):
    """
    Elimina un usuario de la base de datos.
    """
    delete_user(id)
    return redirect(url_for("adminpanel.list_users"))

def validate_edit_request_data(form_data: dict):
    """
    Helper que valida los datos recibidos en una peticion de edicion
    de usuario, de manera que tenga sentido con lo que espera la funcion
    del modelo.

    Args:
        form_data (dict): Los datos con los que se va a actualizar el usuario.
    """
    ret_data = {}
    ret_data["email"] = form_data["email"] if "email" in form_data else None
    ret_data["name"] = form_data["name"] if "name" in form_data else None
    ret_data["last_name"] = form_data["last_name"] if "last_name" in form_data else None
    ret_data["active"] = True if "active" in form_data else False
    
    match (form_data["role"]):
        case ("public"):
            ret_data["role"] = UserRole.PUBLIC
        case ("editor"):
            ret_data["role"] = UserRole.EDITOR
        case ("admin"):
            ret_data["role"] = UserRole.ADMIN

    if "password" in form_data:
        if form_data["password"] != form_data["repeat-password"]:
            return ret_data, "Las contraseñas deben coincidir en ambos campos."
        ret_data["password"] = form_data["password"]
        
    return ret_data, ""
