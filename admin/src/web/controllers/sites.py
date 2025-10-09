# admin/src/web/controllers/sites.py
from __future__ import annotations

from core.services.auth_roles import require_permission  # (tu cambio)

from core.database import db
from flask import request, redirect, url_for, render_template
from .validators.site_validator import validate_site_data
import tempfile

# Importá helpers/modelos que ya existían en development
from core.models.sites import (
    list_sites,
    # create_site, update_site, get_site, delete_site as delete_site_model,  # si existen
    get_all_cities,
    get_all_provinces,
)
from core.models.tags import get_all_tags  # ya estaba en development

from datetime import datetime
from flask import Blueprint

sites_bp = Blueprint(
    "sites",
    __name__,
    url_prefix="/sitios",
    template_folder="../templates/sites"
)


# --------------------------------------------------------------------
# Listado con permisos + validación de fechas (tu rama) + paginación
# + render completo (development)
# --------------------------------------------------------------------
@require_permission("sites.view")
def list_all_sites():
    query_params = request.args.to_dict()

    # Validación de fechas si vienen ambas (tu cambio)
    if "startDate" in query_params and "endDate" in query_params:
        try:
            start_date = datetime.strptime(query_params["startDate"], "%Y-%m-%d")
            end_date = datetime.strptime(query_params["endDate"], "%Y-%m-%d")
            if start_date > end_date:
                return "La fecha de inicio no puede ser mayor a la fecha de fin.", 400
        except ValueError:
            return "Formato de fecha inválido. Use YYYY-MM-DD.", 400

    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Pasamos filtros al listado (manteniendo API de development)
    sites, total = list_sites(page=page, per_page=per_page, filters=query_params)

    pagination = {
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page * per_page < total else None,
        "page": page,
        "per_page": per_page,
        "total": total,
    }

    # Catálogos (mantiene lo de tus compas)
    cities = [c[0] for c in get_all_cities()]
    provinces = [p[0] for p in get_all_provinces()]
    tags = [t.name for t in get_all_tags()]

    return render_template(
        "sites.html",
        pagination=pagination,
        sites=sites,
        cities=cities,
        provinces=provinces,
        tags=tags,
    )


# Si tu blueprint lo registra con rutas, mantené estas decoraciones:
@sites_bp.route("/", methods=["GET"])
def route_list_all_sites():
    return list_all_sites()


# --------------------------------------------------------------------
# Ejemplo de endpoint protegido para creación (dejado listo por si ya existe)
# --------------------------------------------------------------------
@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
@require_permission("sites.create")
def route_create_site():
    if request.method == "GET":
        return render_template("create_site.html")

    form_data = request.form.to_dict()
    errors = validate_site_data(form_data)
    if errors:
        return render_template("create_site.html", errors=errors, data=form_data), 400

    # Si usás servicio/modelo create_site, descomentá la línea:
    # new_id = create_site(form_data)
    # return redirect(url_for("sites.route_get_site", site_id=new_id))

    return redirect(url_for("sites.route_list_all_sites"))
