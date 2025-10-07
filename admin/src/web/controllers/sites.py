from flask import Blueprint
from flask import render_template, flash, abort
from src.core.models.sites import SitioHistorico, EstadoConservacion
from src.core.models.sites import (
    list_sites,
    list_sites_with_filters,
    create_sites,
    update_site,
    get_site,
    delete_site,
    get_all_cities,
    get_all_provinces,
)
from src.core.database import db
from flask import request, redirect, url_for

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)  # Define el blueprint para las rutas de sitios


def validate_site_data(form_data, is_update=False):
    """Valida los datos del formulario de sitios"""
    errors = []
    data = {}

    # Validar campos obligatorios
    required_fields = ["nombre", "ciudad", "provincia", "latitud", "longitud", "estado"]
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"El campo {field} es obligatorio")

    if errors:
        raise ValueError("; ".join(errors))

    # Validar y convertir datos
    try:
        data["nombre"] = form_data["nombre"].strip()
        data["ciudad"] = form_data["ciudad"].strip()
        data["provincia"] = form_data["provincia"].strip()
        data["latitud"] = float(form_data["latitud"])
        data["longitud"] = float(form_data["longitud"])
        data["estado"] = EstadoConservacion[form_data["estado"]]
    except (ValueError, KeyError) as e:
        raise ValueError(f"Error en el formato de los datos: {str(e)}")

    # Validar coordenadas
    if not (-90 <= data["latitud"] <= 90):
        raise ValueError("La latitud debe estar entre -90 y 90")
    if not (-180 <= data["longitud"] <= 180):
        raise ValueError("La longitud debe estar entre -180 y 180")

    # Campos opcionales
    data["descripcionBreve"] = form_data.get("descripcionBreve", "").strip() or None
    data["descripcionCompleta"] = (
        form_data.get("descripcionCompleta", "").strip() or None
    )
    data["categoria"] = form_data.get("categoria_nombre", "").strip() or None
    data["visible"] = "visible" in form_data

    # Validar año de inauguración si se proporciona
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

    return data


@sites_bp.route("/")
def list_all_sites():
    query_params = request.args.to_dict()

    page = request.args.get("page", 1, type=int)
    per_page = 25
    # sites, total = list_sites(page=page, per_page=per_page)
    sites, total = list_sites_with_filters(query_params, page=page, per_page=per_page)

    # Ordenar los resultaos por fecha de registro, nombre o ciudad (asc/desc).
    # Primero por fecha de registro descendente (los más recientes primero)
    # En caso de empate, por nombre ascendente (A-Z)
    # En caso de nuevo empate, por ciudad ascendente (A-Z)
    sites.sort(
        key=lambda s: (s.fechaRegistro, s.nombre.lower(), s.ciudad.lower()),
        reverse=True,
    )

    # Calcular información de paginación
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
        "next_num": next_num,
    }

    cities = [c[0] for c in get_all_cities()]
    provinces = [p[0] for p in get_all_provinces()]

    return render_template(
        "sites.html",
        pagination=pagination,
        sites=sites,
        cities=cities,
        provinces=provinces,
    )


@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
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
# Mejorada con validación y manejo de errores
def edit_site(id):
    site = get_site(id)
    if not site:
        abort(404)

    if request.method == "POST":
        try:
            # Validar datos
            data = validate_site_data(request.form)
            # Actualizar
            updated_site = update_site(id, **data)
            flash("Sitio actualizado correctamente", "success")
            return redirect(url_for("sites.list_all_sites"))
        except ValidationError as e:
            flash(str(e), "error")

    return render_template("form.html", site=site)


@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
def delete_site(id):
    delete_site(id)
    return redirect(url_for("sites.list_all_sites"))


@sites_bp.route("/ver_sitio/<int:id>", methods=["GET"])
def view_site(id):
    site = get_site(id)
    return render_template("view.html", site=site)
