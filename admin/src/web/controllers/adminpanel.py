from flask import Blueprint, request, render_template, flash, redirect, url_for, abort
from core.models.userrole import UserRole
from core.models.user import create_user, read_user_by_email, read_users_by_activeness
from core.models.user import read_users_by_role, update_user, delete_user, get_user_by_id, list_all_users

adminpanel_bp = Blueprint("panel-de-admin", "panel-de-admin")

@adminpanel_bp.route("/", methods=["GET"])
def admin_panel():
    pass

def validate_user_data(form_data: dict, is_update=False) -> dict:
    errors = []
    data = {}

    required_fields = ["email", "name", "last_name", "password", "active", "role"]
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"El campo {field} es obligatorio")
    
    if errors:
        raise ValueError("; ".join(errors))

    try:
        data["email"] = form_data["email"].strip()
        data["name"] = form_data["name"].strip()
        data["last_name"] = form_data["last_name"].strip()
        data["password"] = form_data["password"]
        data["active"] = form_data["active"]
        data["role"] = UserRole[form_data["role"]]
    except (ValueError, KeyError) as e:
        raise ValueError(f"Error en el formato de los datos: {str(e)}")
    
    return data

@adminpanel_bp.route("/listar-usuarios")
def list_users() -> str:
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
    return render_template("adminpanel.html", pagination=pagination, users=users)

@adminpanel_bp.route("/crear-usuario", methods=["GET", "POST"])
def create_user() -> str:
    if request.method == "POST":
        try:
            data = validate_user_data(request.form)
            create_user(**data)
            flash("El usuario fue creado correctamente", "success")
            return redirect(url_for("panel-de-admin"))
        except ValueError as e:
            flash(f"Error de validación: {str(e)}", "error")
        except Exception as e:
            flash(f"Error al crear el sitio: {str(e)}", "error")

    return render_template("form.html")

@adminpanel_bp.route("/editar-usuario/<int:id>", methods=["GET", "POST"])
def edit_user(id: int) -> str:
    user = get_user_by_id(id)
    if not user:
        abort(404)
    
    if request.method == "POST":
        try:
            data = validate_user_data(request.form)
            updated_user = update_user(id, **data)
            flash("Usuario editado correctamente.", "success")
            return redirect(url_for("panel-de-admin"))
        except ValueError as e:
            flash(str(e), "error")
    
    return render_template("form.html", user=user)

@adminpanel_bp.route("/eliminar-usuario/<int:id>", methods=["POST"])
def del_user(id: int):
    delete_user(id)
    return redirect(url_for("panel-de-admin"))

@adminpanel_bp.route("/ver-usuario/<int:id>", methods=["GET"])
def view_user(id: int) -> str:
    user = get_user_by_id(id)
    return render_template("viewuser.html", user=user)
