from flask import Blueprint
from flask import render_template, flash, abort, session
from core.models.sites import (
    list_sites,
    list_sites_with_filters,
    create_sites,
    update_site,
    get_site,
    delete_site_by_id,
    get_all_cities,
    get_all_provinces,
    SitioHistorico,
    EstadoConservacion
)
from core.database import db
from flask import request, redirect, url_for
from .validators.site_validator import validate_site_data
from core.models import tags
from core.models.tags import Tag

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)  # Define el blueprint para las rutas de sitios

@sites_bp.route('/')
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

@sites_bp.route('/crear_sitio', methods=['GET', 'POST'])
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
