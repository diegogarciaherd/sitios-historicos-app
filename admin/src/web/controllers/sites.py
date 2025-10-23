# admin/src/web/controllers/sites.py
from __future__ import annotations

from core.services.auth_roles import require_permission  # (tu cambio)

from core.database import db
from flask import (
    abort,
    flash,
    jsonify,
    request,
    redirect,
    send_file,
    url_for,
    render_template,
)
from .validators.site_validator import validate_site_data
import tempfile

# Importá helpers/modelos que ya existían en development
from core.models.sites import (
    list_sites,
    create_sites,
    list_sites_with_filters,
    update_site,
    get_site,
    delete_site_by_id,  # si existen
    get_all_cities,
    get_all_provinces,
)
from core.database import db
from flask import request, redirect, url_for
from .validators.site_validator import validate_site_data
from core.models import tags
from core.models.tags import Tag
from core.models.tags import get_all_tags  # ya estaba en development

from datetime import datetime
from flask import Blueprint
import json
import csv

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)


@sites_bp.route("/")
@require_permission("sites.view")
def home():
    return render_template("sites_home.html")


@sites_bp.route("/listar")
@require_permission("sites.view")
def list_all_sites():
    query_params = request.args.to_dict()

    # Si en los query params estan los filtros de startDate y endDate (ambos), verificar que
    # startDate <= endDate. Si no, devolver error 400.
    if "startDate" in query_params and "endDate" in query_params:
        try:
            start_date = datetime.strptime(query_params["startDate"], "%Y-%m-%d")
            end_date = datetime.strptime(query_params["endDate"], "%Y-%m-%d")
            if start_date > end_date:
                return "La fecha de inicio no puede ser mayor a la fecha de fin.", 400
        except ValueError:
            return "Formato de fecha inválido. Use YYYY-MM-DD.", 400

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
    tags = [t.name for t in get_all_tags()]

    sitesJson = [
        site.to_dict() for site in sites
    ]  # Sitios en formato JSON para guardar en el frontend, para luego poder exportarlos a CSV

    return render_template(
        "sites.html",
        pagination=pagination,
        sites=sites,
        sitesJson=json.dumps(sitesJson),
        cities=cities,
        provinces=provinces,
        tags=tags,
    )


@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
@require_permission("sites.create")
def create_site():
    all_tags = db.session.query(Tag).all()
    selected_tag_ids = []

    if request.method == "POST":
        data = request.form.to_dict()
        # Manejar checkbox visible
        data["visible"] = "visible" in request.form

        tag_ids = request.form.getlist("tags[]")  # Lista de ids seleccionados
        data.pop("tags[]", None)

        site = create_sites(**data)

        if tag_ids:
            selected_tags = db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            tags.assign_tags(site, selected_tags)

        flash("Sitio creado correctamente", "success")
        return redirect(url_for("sites.list_all_sites"))

    return render_template(
        "form.html", site=None, tags=all_tags, selected_tag_ids=selected_tag_ids
    )


@sites_bp.route("/editar_sitio/<int:id>", methods=["GET", "POST"])
@require_permission("sites.create")
def edit_site(id):
    site = get_site(id)
    if not site:
        abort(404)

    all_tags = db.session.query(Tag).all()
    selected_tag_ids = [str(tag.id) for tag in site.tags]

    if request.method == "POST":
        data = request.form.to_dict()
        data["visible"] = "visible" in request.form

        tag_ids = request.form.getlist("tags[]")
        data.pop("tags[]", None)

        update_site(id, **data)

        # Actualizar tags
        selected_tags = db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        tags.assign_tags(site, selected_tags)

        flash("Sitio actualizado correctamente", "success")
        return redirect(url_for("sites.list_all_sites"))

    return render_template(
        "form.html", site=site, tags=all_tags, selected_tag_ids=selected_tag_ids
    )


@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
@require_permission("sites.create")
def delete_site(id):
    try:
        # Llama a la función existente
        delete_site_by_id(id)
        site = get_site(id)  # Verifica si el sitio aún existe
        if not site:
            flash("Sitio eliminado correctamente", "success")
        else:
            flash("Sitio no encontrado", "error")
    except Exception as e:
        flash(f"Error al eliminar el sitio: {str(e)}", "error")
    return redirect(url_for("sites.list_all_sites"))


@sites_bp.route("/ver_sitio/<int:id>", methods=["GET"])
@require_permission("sites.view")
def view_site(id):
    site = get_site(id)
    site_lat = site.lat
    site_lng = site.lng
    return render_template("show_site.html", site=site, site_lat=site_lat, site_lng=site_lng)



@sites_bp.route("/exportar_csv", methods=["POST"])
@require_permission("sites.export")
def export_csv():
    """Función para exportar los sitios a un archivo CSV."""

    sitesToExport = request.get_json().get("sites", [])

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "ID",
                "Nombre",
                "Descripción",
                "Ciudad",
                "Provincia",
                "Estado de conservación",
                "Fecha de registro",
                "Coordenadas (Lat, Lng)",
                "Tags",
            ]
        )
        for site in sitesToExport:
            fechaRegistro = datetime.fromisoformat(site["fechaRegistro"])
            fechaRegistro = fechaRegistro.strftime("%d/%m/%Y %H:%M")

            writer.writerow(
                [
                    site["id"],
                    site["nombre"],
                    site["descripcionBreve"],
                    site["ciudad"],
                    site["provincia"],
                    site["estado"],
                    fechaRegistro,
                    f"{site['lat']}, {site['lng']}",
                    ", ".join(
                        tag["name"] for tag in site["tags"]
                    ),  # Esto crea una cadena con los nombres de los tags separados por comas
                ]
            )
        file.flush()
        file.seek(0)

    # Nombre del archivo: sitios_<YYYYMMDD_HHMM>.csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"sitios_{timestamp}.csv"

    return send_file(
        file.name,  # Ruta absoluta del archivo que creamos antes con tempfile
        as_attachment=True,  # Indica al navegador que lo descargue
        download_name=filename,
        mimetype="text/csv",
    )
