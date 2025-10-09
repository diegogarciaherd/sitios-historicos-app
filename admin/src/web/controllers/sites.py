# admin/src/web/controllers/sites.py
from __future__ import annotations

from core.services.auth_roles import require_permission  # (tu cambio)

from core.database import db
from flask import abort, flash, jsonify, request, redirect, send_file, url_for, render_template
from .validators.site_validator import validate_site_data
import tempfile

# Importá helpers/modelos que ya existían en development
from core.models.sites import (
    export_to_csv,
    list_sites,
    create_sites,
    list_sites_with_filters, update_site, get_site, delete_site_by_id,  # si existen
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
@sites_bp.route("/", methods=["GET"])
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

    return render_template(
        "sites.html",
        pagination=pagination,
        sites=sites,
        cities=cities,
        provinces=provinces,
        tags=tags,
    )


@sites_bp.route('/crear_sitio', methods=['GET', 'POST'])
@require_permission("sites.create")
def create_site():
    all_tags = db.session.query(Tag).all()
    selected_tag_ids = []

    if request.method == "POST":
        data = request.form.to_dict()
        # Manejar checkbox visible
        data['visible'] = 'visible' in request.form

        tag_ids = request.form.getlist('tags[]')  # Lista de ids seleccionados
        data.pop('tags[]', None)

        site = create_sites(**data)

        if tag_ids:
            selected_tags = db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            tags.assign_tags(site, selected_tags)

        flash("Sitio creado correctamente", "success")
        return redirect(url_for('sites.list_all_sites'))

    return render_template('form.html', site=None, tags=all_tags, selected_tag_ids=selected_tag_ids)


@sites_bp.route('/editar_sitio/<int:id>', methods=['GET', 'POST'])
@require_permission("sites.create")
def edit_site(id):
    site = get_site(id)
    if not site:
        abort(404)

    all_tags = db.session.query(Tag).all()
    selected_tag_ids = [str(tag.id) for tag in site.tags]

    if request.method == "POST":
        data = request.form.to_dict()
        data['visible'] = 'visible' in request.form

        tag_ids = request.form.getlist('tags[]')
        data.pop('tags[]', None)

        update_site(id, **data)

        # Actualizar tags
        selected_tags = db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        tags.assign_tags(site, selected_tags)

        flash("Sitio actualizado correctamente", "success")
        return redirect(url_for('sites.list_all_sites'))

    return render_template('form.html', site=site, tags=all_tags, selected_tag_ids=selected_tag_ids)



@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
@require_permission("sites.create")
def delete_site(id):
    try:
        # Llama a la función existente
        delete_site_by_id(id)
        site = get_site(id) # Verifica si el sitio aún existe
        if not site:
            flash('Sitio eliminado correctamente', 'success')
        else:
            flash('Sitio no encontrado', 'error')
    except Exception as e:
        flash(f'Error al eliminar el sitio: {str(e)}', 'error')
    return redirect(url_for('sites.list_all_sites'))

@sites_bp.route("/ver_sitio/<int:id>", methods=["GET"])
def view_site(id):
    site = get_site(id)
    return render_template('show_site.html', site=site)

@sites_bp.route("/exportar_csv", methods=["GET"])
def export_csv():
    """Función para exportar los sitios a un archivo CSV."""

    try:
        query_params = request.args.to_dict()

        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".csv"
        ) as temp_csv:
            export_to_csv(temp_csv.name, filters=query_params)
            temp_csv.flush()

        # Nombre del archivo: sitios_<YYYYMMDD_HHMM>.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        download_name = f"sitios_{timestamp}.csv"

        return send_file(
            temp_csv.name,
            as_attachment=True,
            download_name=download_name,
            mimetype="text/csv",
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al exportar CSV: {str(e)}"}), 500
