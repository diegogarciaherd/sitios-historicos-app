# admin/src/web/controllers/sites.py
from flask import Blueprint, render_template, flash, abort, request, redirect, url_for
from core.models.sites import (
    SitioHistorico, EstadoConservacion,
    list_sites, create_sites, update_site, get_site,
    delete_site as delete_site_model,
)
from core.services.auth_roles import require_permission

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)

def validate_site_data(form_data):
    errors = []
    data = {}

    required = ["nombre", "ciudad", "provincia", "latitud", "longitud", "estado"]
    for f in required:
        if not form_data.get(f):
            errors.append(f"El campo {f} es obligatorio")
    if errors:
        raise ValueError("; ".join(errors))

    try:
        data["nombre"] = form_data["nombre"].strip()
        data["ciudad"] = form_data["ciudad"].strip()
        data["provincia"] = form_data["provincia"].strip()
        data["latitud"] = float(form_data["latitud"])
        data["longitud"] = float(form_data["longitud"])
        data["estado"] = EstadoConservacion[form_data["estado"]]
    except (ValueError, KeyError) as e:
        raise ValueError(f"Error en el formato de los datos: {str(e)}")

    if not (-90 <= data["latitud"] <= 90):
        raise ValueError("La latitud debe estar entre -90 y 90")
    if not (-180 <= data["longitud"] <= 180):
        raise ValueError("La longitud debe estar entre -180 y 180")

    data["descripcionBreve"] = form_data.get("descripcionBreve", "").strip() or None
    data["descripcionCompleta"] = form_data.get("descripcionCompleta", "").strip() or None
    data["categoria"] = form_data.get("categoria_nombre", "").strip() or None
    data["visible"] = "visible" in form_data

    if form_data.get("añoInauguracion"):
        try:
            año = int(form_data["añoInauguracion"])
            if año < 1000 or año > 2024:
                raise ValueError("El año de inauguración debe estar entre 1000 y 2024")
            data["añoInauguracion"] = año
        except ValueError:
            raise ValueError("El año de inauguración debe ser un número válido")
    else:
        data["añoInauguracion"] = None

    # mapeo para create/update
    required = ["nombre", "ciudad", "provincia", "lat", "lng", "estado"]
    data["lat"] = float(form_data["lat"])
    data["lng"] = float(form_data["lng"])


@sites_bp.route("/")
@require_permission("sites.view")
def list_all_sites():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    sites, total = list_sites(page=page, per_page=per_page)

    total_pages = (total + per_page - 1) // per_page
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < total_pages else None,
    }
    return render_template("sites.html", pagination=pagination, sites=sites)

@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
@require_permission("sites.create")
def create_site():
    if request.method == "POST":
        try:
            data = validate_site_data(request.form)
            create_sites(**data)
            flash("Sitio histórico creado correctamente", "success")
            return redirect(url_for("sites.list_all_sites"))
        except ValueError as e:
            flash(f"Error de validación: {str(e)}", "error")
        except Exception as e:
            flash(f"Error al crear el sitio: {str(e)}", "error")
    return render_template("form.html")

@sites_bp.route("/editar_sitio/<int:id>", methods=["GET", "POST"])
@require_permission("sites.edit")
def edit_site(id):
    site = get_site(id)
    if not site:
        abort(404)
    if request.method == "POST":
        try:
            data = validate_site_data(request.form)
            update_site(id, **data)
            flash("Sitio actualizado correctamente", "success")
            return redirect(url_for("sites.list_all_sites"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("form.html", site=site)

@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
@require_permission("sites.delete")
def delete_site(id):
    delete_site_model(id)
    flash("Sitio eliminado correctamente", "success")
    return redirect(url_for("sites.list_all_sites"))

@sites_bp.route("/ver_sitio/<int:id>", methods=["GET"])
@require_permission("sites.view")
def view_site(id):
    site = get_site(id)
    return render_template("view.html", site=site)
