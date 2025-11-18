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
)
from .validators.site_validator import validate_site_data
import tempfile

# Importá helpers/modelos de sitios
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
from core.models import tags
from datetime import datetime
from flask import Blueprint, session
import json
import csv
from core.database import db
from core.models.site_history import SiteChange
from core.services.site_history import log_site_change, diff_site, diff_tags
from flask import current_app
from os import fstat
import uuid
from core.models.site_images import (
    create_site_image,
    get_images_by_site,
    get_image_cover_by_site,
    validate_site_images,
)


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
    per_page = 10
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
        # Manejar checkbox visible
        data["visible"] = "visible" in request.form

        tag_ids = request.form.getlist("tags[]")
        data.pop("tags[]", None)

        # Validar datos
        errors = validate_site_data(data)

        # Si hay errores, mostrar el formulario con los errores
        if errors:
            # Mostrar cada error individualmente
            for error in errors:
                flash(error, "error")
            return render_template(
                "form.html",
                site=None,
                tags=all_tags,
                selected_tag_ids=tag_ids,
                form_data=data,  # Mantener datos del formulario
            )

        # SOLO crear el sitio si NO hay errores
        try:
            site = create_sites(**data)

            if tag_ids:
                selected_tags = tags.get_tags_by_ids(tag_ids)
                tags.assign_tags(site, selected_tags)

            log_site_change(
                site_id=site.id, user_id=session.get("user_id"), action="create"
            )
            db.session.commit()  # persistimos el historial

            # IMPORTANTE: Flash ANTES de redirect
            flash("Sitio creado correctamente", "success")
            return redirect(url_for("sites.list_all_sites"))  # ← Redirigir a la lista

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


# Editar
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
        # --- SNAPSHOT ANTES (desvinculado para que el diff vea cambios reales) ---
        before = get_site(id)
        _ = list(getattr(before, "tags", []))  # (opcional) fuerza precarga de tags
        db.session.expunge(before)  # clave para “congelar” el snapshot

        data = request.form.to_dict()

        data["visible"] = "visible" in request.form
        # Los nombres de los campos permanecen como están en tu capa de modelos
        data["latitud"] = request.form.get("lat")
        data["longitud"] = request.form.get("lng")

        tag_ids = request.form.getlist("tags[]")
        data.pop("tags[]", None)

        errors = validate_site_data(data)
        # Si hay errores, mostrar el formulario con los errores
        if errors:
            # Mostrar cada error individualmente
            for error in errors:
                flash(error, "error")
            return render_template(
                "form.html",
                site=None,
                tags=all_tags,
                selected_tag_ids=tag_ids,
                form_data=data,  # Mantener datos del formulario
            )

        try:
            upload_images(request, id)
        except Exception as e:
            flash(f"Error al subir las imágenes: {str(e)}", "error")
            return render_template(
                "form.html",
                site=site,
                tags=all_tags,
                selected_tag_ids=selected_tag_ids,
                site_images=site_images,
            )

        # --- UPDATE CAMPOS ---
        try:
            update_site(id, **data)
        except Exception as e:
            flash(f"Error al actualizar el sitio: {str(e)}", "error")
            return render_template(
                "form.html",
                site=site,
                tags=all_tags,
                selected_tag_ids=selected_tag_ids,
                site_images=site_images,
            )

        # --- TAGS ---
        selected_tags = tags.get_tags_by_ids(tag_ids)
        tags.assign_tags(site, selected_tags)

        # --- SNAPSHOT DESPUÉS ---
        after = get_site(id)

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
        # registrar el historial ANTES de eliminar, para guardar quién lo borró
        log_site_change(site_id=id, user_id=session.get("user_id"), action="delete")
        db.session.commit()  # confirma el registro en la tabla sites_history

        # Llama a la función existente que elimina el sitio
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
    """Muestra los detalles de un sitio histórico"""
    site = get_site(id)
    site_lat = site.lat
    site_lng = site.lng

    site_images = get_images_by_site(site.id)
    return render_template(
        "show_site.html",
        site=site,
        site_lat=site_lat,
        site_lng=site_lng,
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

    # Nombre del archivo: sitios_<YYYYMMDD_HHMM>.csv
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
    Lista el historial con filtros y paginación (25 por página).
    Filtros:
      - user: texto a buscar en nombre o apellido (icontains)
      - action: create|update|delete
      - from: YYYY-MM-DD
      - to:   YYYY-MM-DD
    """
    from core.models.user import User  # import local para evitar circulares

    q = (
        db.session.query(SiteChange, User)
        .outerjoin(User, User.id == SiteChange.user_id)
        .filter(SiteChange.site_id == id)
    )

    # --- Filtros ---
    user_txt = request.args.get("user", "", type=str).strip()
    if user_txt:
        like = f"%{user_txt.lower()}%"
        q = q.filter(
            db.or_(
                db.func.lower(User.name).like(like),
                db.func.lower(User.last_name).like(like),
            )
        )

    action = request.args.get("action", "", type=str).strip()
    if action in ("create", "update", "delete"):
        q = q.filter(SiteChange.action == action)

    def _parse_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None

    d_from = _parse_date(request.args.get("from", request.args.get("start", "")))
    d_to = _parse_date(request.args.get("to", request.args.get("end", "")))
    if d_from:
        q = q.filter(SiteChange.changed_at >= d_from)
    if d_to:
        # inclusive hasta fin de día
        q = q.filter(
            SiteChange.changed_at < (d_to.replace(hour=23, minute=59, second=59))
        )

    # --- Orden + paginación ---
    q = q.order_by(SiteChange.changed_at.desc())
    page = max(1, request.args.get("page", 1, type=int))
    per_page = 25
    total = q.count()
    rows = q.limit(per_page).offset((page - 1) * per_page).all()

    # Adaptamos a estructura simple para el template
    cambios = []
    for schange, u in rows:
        cambios.append(
            {
                "changed_at": schange.changed_at,
                "user_name": (
                    f"{u.name} {u.last_name} ({u.email})".strip() if u else "—"
                ),
                "action": schange.action,
                "field": schange.field or "—",
                "old_value": schange.old_value or "—",
                "new_value": schange.new_value or "—",
            }
        )

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

    # Para conservar filtros en los links de paginación
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


def upload_images(req, site_id):
    """Función para manejar la subida de imágenes asociadas a un sitio histórico."""

    images = req.files.getlist("images")

    if images and len(images) > 0:
        if images[0].filename != "":

            # En este punto, hay imágenes para subir.
            # Armamos los datos para validar las images a subir

            images_data_to_validate = []
            images_data_to_upload = []

            for img in images:
                order = req.form.get(f"order-{img.filename}", 0)
                is_cover = req.form.get(f"is-cover-{img.filename}", "off") == "on"
                size = fstat(img.fileno()).st_size
                format = img.content_type
                images_data_to_validate.append(
                    {
                        "size": size,
                        "format": format,
                        "order": order,
                        "is_cover": is_cover,
                        "filename": img.filename,
                    }
                )
                images_data_to_upload.append(
                    {
                        "object_name": f"public/sites/{site_id}/{uuid.uuid4()}{img.filename}",
                        "data": img,
                        "length": size,
                        "content_type": img.content_type,
                        "alt_text": req.form.get(f"alt-text-{img.filename}", ""),
                        "description": req.form.get(f"description-{img.filename}", ""),
                        "order": order,
                        "is_cover": is_cover,
                    }
                )

            # Validar las imágenes antes de subirlas
            validation_result = validate_site_images(site_id, images_data_to_validate)

            if validation_result is not True:
                raise ValueError("Error al validar las imágenes")

            # En este punto, las imágenes son válidas y podemos proceder a subirlas.

            client_storage = current_app.storage
            bucket_name = current_app.config.get("MINIO_BUCKET")

            for img in images_data_to_upload:
                client_storage.put_object(
                    bucket_name=bucket_name,
                    object_name=img["object_name"],
                    data=img["data"],
                    length=img["length"],
                    content_type=img["content_type"],
                )

                create_site_image(
                    site_id=site_id,
                    object_name=img["object_name"],
                    alt_text=img["alt_text"],
                    description=img["description"],
                    order=img["order"],
                    is_cover=img["is_cover"],
                )
