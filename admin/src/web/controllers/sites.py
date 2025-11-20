# admin/src/web/controllers/sites.py

from __future__ import annotations

from core.services.auth_roles import require_permission
from flask import (
    abort,
    flash,
    request,
    redirect,
    send_file,
    url_for,
    render_template,
    session,
)
from .validators.site_validator import validate_site_data
import tempfile
import json
import csv
from datetime import datetime

from flask import Blueprint

from core.database import db
from core.models.sites import (
    list_sites,
    create_sites,
    list_sites_with_filters,
    update_site,
    get_site,
    delete_site_by_id,
    get_all_cities,
    get_all_provinces,
    SitioHistorico,
)
from core.models import tags
from core.models.site_history import SiteChange
from core.services.site_history import log_site_change, diff_site, diff_tags
from core.models.site_images import (
    create_site_image,
    get_images_by_site,
    get_image_cover_by_site,
    update_image_data,
    validate_site_images_data,
    generate_data_for_update,
    generate_data_for_create,
    delete_image_by_object_name,
    valdiate_images_to_replace,
    replace_site_image,
)
from core.models.reviews import Review, ReviewStatus
from sqlalchemy import func, or_

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)


@sites_bp.route("/")
@require_permission("sites.view")
def home():
    """Renderiza la página de inicio de sitios históricos"""
    return render_template("sites_home.html")


@sites_bp.route("/listar")
@require_permission("sites.view")
def list_all_sites():
    """Lista todos los sitios históricos con paginación y filtros"""
    query_params = request.args.to_dict()

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

    sites, total = list_sites_with_filters(query_params, page=page, per_page=per_page)

    """ sites.sort(
        key=lambda s: (s.fechaRegistro, s.nombre.lower(), s.ciudad.lower()),
        reverse=False,
    ) """

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

    cities = [c[0] for c in get_all_cities()]
    provinces = [p[0] for p in get_all_provinces()]
    tags_list = [t.name for t in tags.get_all_tags()]

    # Agregamos la imagen de portada al objeto de sitio
    for site in sites:
        cover_image = get_image_cover_by_site(site.id)
        site.cover_image = cover_image

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
        tags=tags_list,
    )


@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
@require_permission("sites.create")
def create_site():
    """Crea un nuevo sitio histórico"""
    all_tags = tags.get_all_tags()

    if request.method == "POST":
        data = request.form.to_dict()
        data["visible"] = "visible" in request.form

        tag_ids = request.form.getlist("tags[]")
        data.pop("tags[]", None)

        errors = validate_site_data(data)
        imagesErrors = validate_site_images_data(request, None)

        # Si hay errores, mostrar el formulario con los errores
        if errors or imagesErrors:
            # Mostrar cada error individualmente

            for error in errors:
                flash(error, "error")

            for error in imagesErrors:
                flash(error, "error")

            return render_template(
                "form.html",
                site=None,
                tags=all_tags,
                selected_tag_ids=tag_ids,
                form_data=data,  # Mantener datos del formulario
            )

        try:
            site = create_sites(**data)

            images_data_create = generate_data_for_create(request, site.id)
            for new_img_data in images_data_create:
                create_site_image(site.id, **new_img_data)

            if tag_ids:
                selected_tags = tags.get_tags_by_ids(tag_ids)
                tags.assign_tags(site, selected_tags)

            log_site_change(
                site_id=site.id, user_id=session.get("user_id"), action="create"
            )
            db.session.commit()  # persistimos el historial

            flash("Sitio creado correctamente", "success")
            return redirect(url_for("sites.list_all_sites"))
        except Exception as e:
            flash(f"Error al crear el sitio: {str(e)}", "error")
            return render_template(
                "form.html",
                site=None,
                tags=all_tags,
                selected_tag_ids=tag_ids,
                form_data=data,
            )

    # GET request
    return render_template("form.html", site=None, tags=all_tags, selected_tag_ids=[])


@sites_bp.route("/editar_sitio/<int:id>", methods=["GET", "POST"])
@require_permission("sites.edit")
def edit_site(id):
    """Edita un sitio histórico existente"""
    site = get_site(id)
    if not site:
        abort(404)

    all_tags = tags.get_all_tags()
    selected_tag_ids = [str(tag.id) for tag in site.tags]
    site_images = get_images_by_site(site.id)

    if request.method == "POST":
        before = get_site(id).to_dict()

        data = request.form.to_dict()

        data["visible"] = "visible" in request.form
        data["lat"] = request.form.get("lat")
        data["lng"] = request.form.get("lng")

        tag_ids = request.form.getlist("tags[]")
        data.pop("tags[]", None)

        imagesToReplace = request.form.getlist("imagesToReplace[]")
        data.pop("imagesToReplace[]", None)

        images_to_replace_errors = valdiate_images_to_replace(request, imagesToReplace)

        images_to_delete = request.form.getlist("imagesToDelete[]")
        data.pop("imagesToDelete[]", None)

        errors = validate_site_data(data)
        imagesErrors = validate_site_images_data(request, id, images_to_delete)

        # Si hay errores, mostrar el formulario con los errores
        if errors or len(imagesErrors) > 0 or len(images_to_replace_errors) > 0:
            # Mostrar cada error individualmente
            for error in errors:
                flash(error, "error")

            for error in imagesErrors:
                flash(error, "error")

            for error in images_to_replace_errors:
                flash(error, "error")

            return render_template(
                "form.html",
                site=site,
                tags=all_tags,
                selected_tag_ids=selected_tag_ids,
                site_images=site_images,
            )

        # --- UPDATE CAMPOS ---
        update_site(id, **data)

        images_data_update = generate_data_for_update(
            request, site.id, images_to_delete
        )
        images_data_create = generate_data_for_create(request, site.id)

        for img_data in images_data_update:
            update_image_data(img_data.pop("id"), **img_data)

        for new_img_data in images_data_create:
            create_site_image(site.id, **new_img_data)

        if len(images_to_delete) > 0:
            for object_name in images_to_delete:
                delete_image_by_object_name(object_name)

        if len(imagesToReplace) > 0:
            for object_name in imagesToReplace:
                replace_site_image(object_name, request)

        # --- TAGS ---
        selected_tags = tags.get_tags_by_ids(tag_ids)
        tags.assign_tags(site, selected_tags)

        after = get_site(id).to_dict()

        # --- DIFFS ---
        changes = diff_site(before, after)  # campos simples + coords + visible
        tag_changes = diff_tags(before, after)  # cambios de set de tags
        changes.update(tag_changes)

        # --- HISTORIAL + COMMIT ---
        log_site_change(
            site_id=id, user_id=session.get("user_id"), action="update", changes=changes
        )
        db.session.commit()

        flash("Sitio actualizado correctamente", "success")
        return redirect(url_for("sites.list_all_sites"))

    return render_template(
        "form.html",
        site=site,
        tags=all_tags,
        selected_tag_ids=selected_tag_ids,
        site_images=site_images,
    )


@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
@require_permission("sites.delete")
def delete_site(id):
    """Elimina un sitio histórico existente"""
    try:
        log_site_change(
            site_id=id,
            user_id=session.get("user_id"),
            action="delete",
        )
        db.session.commit()

        delete_site_by_id(id)
        site = get_site(id)

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
    """Muestra los detalles de un sitio histórico + reseñas aprobadas."""
    site = get_site(id)
    if not site:
        abort(404)

    # Reseñas aprobadas del sitio
    approved_reviews = (
        db.session.query(Review)
        .filter(Review.site_id == id, Review.status == ReviewStatus.APPROVED)
        .order_by(Review.created_at.desc())
        .all()
    )

    # Promedio de rating (solo aprobadas)
    avg_rating, total_reviews = (
        db.session.query(
            func.coalesce(func.avg(Review.rating), 0),
            func.count(Review.id),
        )
        .filter(
            Review.site_id == id,
            Review.status == ReviewStatus.APPROVED,
        )
        .one()
    )

    total_reviews = int(total_reviews)
    # Si no hay reseñas, dejamos avg_rating en None para que el template
    # muestre el mensaje "Todavía no hay reseñas..."
    if total_reviews == 0:
        avg_rating = None
    else:
        avg_rating = round(float(avg_rating), 1)

    site_images = get_images_by_site(site.id)

    return render_template(
        "show_site.html",
        site=site,
        site_lat=site.lat,
        site_lng=site.lng,
        reviews=approved_reviews,
        avg_rating=avg_rating,
        total_reviews=total_reviews,
        site_images=site_images,
    )


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
                    ", ".join(tag["name"] for tag in site["tags"]),
                ]
            )
        file.flush()
        file.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"sitios_{timestamp}.csv"

    return send_file(
        file.name,
        as_attachment=True,
        download_name=filename,
        mimetype="text/csv",
    )


@sites_bp.route("/ver_historial/<int:id>", methods=["GET"])
@require_permission("sites.history_view")
def view_history(id):
    """
    Historial de cambios de un sitio con filtros + paginación.
    """
    from core.models.user import User  # import local para evitar circulares

    q = (
        db.session.query(SiteChange, User)
        .outerjoin(User, User.id == SiteChange.user_id)
        .filter(SiteChange.site_id == id)
    )

    user_txt = request.args.get("user", "", type=str).strip()
    if user_txt:
        like = f"%{user_txt.lower()}%"
        q = q.filter(
            or_(
                func.lower(User.name).like(like),
                func.lower(User.last_name).like(like),
                func.lower(User.email).like(like),
            )
        )

    action = request.args.get("action", "", type=str).strip()
    if action in ("create", "update", "delete"):
        q = q.filter(SiteChange.action == action)

    def _parse_date(val: str):
        try:
            return datetime.strptime(val, "%Y-%m-%d")
        except Exception:
            return None

    d_from = _parse_date(request.args.get("from", "") or request.args.get("start", ""))
    d_to = _parse_date(request.args.get("to", "") or request.args.get("end", ""))

    if d_from:
        q = q.filter(SiteChange.changed_at >= d_from)
    if d_to:
        q = q.filter(
            SiteChange.changed_at < d_to.replace(hour=23, minute=59, second=59)
        )

    q = q.order_by(SiteChange.changed_at.desc())

    page = max(1, request.args.get("page", 1, type=int))
    per_page = 25
    total = q.count()
    rows = q.limit(per_page).offset((page - 1) * per_page).all()

    cambios = []
    for schange, u in rows:
        cambios.append(
            {
                "changed_at": schange.changed_at,
                "user_name": f"{u.name} {u.last_name} ({u.email})" if u else "—",
                "action": schange.action,
                "field": schange.field or "—",
                "old_value": schange.old_value or "—",
                "new_value": schange.new_value or "—",
            }
        )

    pages = (total + per_page - 1) // per_page
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_prev": page > 1,
        "has_next": page < pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < pages else None,
    }

    current_filters = {
        "user": user_txt,
        "action": action,
        "from": request.args.get("from", ""),
        "to": request.args.get("to", ""),
    }

    return render_template(
        "sites/sites_history.html",
        site_id=id,
        cambios=cambios,
        pagination=pagination,
        current_filters=current_filters,
    )


@sites_bp.route("/api/historial/<int:id>", methods=["GET"])
@require_permission("sites.history_view")
def api_history(id):
    cambios = (
        db.session.query(SiteChange)
        .filter_by(site_id=id)
        .order_by(SiteChange.changed_at.desc())
        .all()
    )

    data = [
        {
            "id": c.id,
            "site_id": c.site_id,
            "user_id": c.user_id,
            "action": c.action,
            "field": c.field,
            "old_value": c.old_value,
            "new_value": c.new_value,
            "changed_at": c.changed_at.isoformat(),
        }
        for c in cambios
    ]
    return json.dumps(data), 200, {"Content-Type": "application/json"}
