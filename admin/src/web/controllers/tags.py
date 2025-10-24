from flask import render_template, Blueprint, request, jsonify
from core.models.tags import Tag
from core.models.sites import SitioHistorico
from core.database import db
from flask import flash, redirect, url_for
from core.models import tags
from core.services.auth_roles import require_permission

tags_bp = Blueprint("tags", __name__, url_prefix="/tags", template_folder="../templates/tags")

# Página HTML
@tags_bp.route("/", methods=["GET"])
@require_permission("tags.manage")
def tags_list():
    '''Lista todos los tags con paginación, búsqueda y ordenamiento'''
    search = request.args.get("search", "")
    order_by = request.args.get("order_by", "name_asc")
    page = request.args.get("page", 1, type=int)

    tagsI, total, total_pages = tags.get_tags(search=search, order_by=order_by, page=page)

    return render_template(
        "list.html",
        tags=tagsI,
        page=page,
        total_pages=total_pages,
        search=search,
        order_by=order_by
    )


# API JSON
@tags_bp.route("/api", methods=["GET"])
@require_permission("tags.manage")
def get_tags():
    '''API para obtener tags con paginación y búsqueda'''
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 25

    pagination = tags.list_tags(search, page, per_page)
    data = [{"id": t.id, "name": t.name, "slug": t.slug} for t in pagination.items]

    return jsonify({
        "results": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })


# Crear tag
@tags_bp.route("/create", methods=["GET", "POST"])
@require_permission("tags.manage")
def create_tag():
    '''Crea un nuevo tag'''
    if request.method == "POST":
        try:
            tags.create_tag(request.form["name"])
            flash("Tag creado correctamente.", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("tags.tags_list"))

    return render_template("create.html")


# Editar tag
@tags_bp.route("/edit/<int:tag_id>", methods=["GET", "POST"])
@require_permission("tags.manage")
def edit_tag_view(tag_id):
    '''Edita un tag existente'''
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.tags_list"))

    if request.method == "POST":
        try:
            tags.update_tag(tag_id, request.form["name"])
            flash("Tag actualizado correctamente.", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("tags.tags_list"))

    return render_template("edit.html", tag=tag)


# Eliminar tag
@tags_bp.route("/delete/<int:tag_id>", methods=["POST"])
@require_permission("tags.manage")
def delete_tag_view(tag_id):
    '''Elimina un tag existente'''
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.tags_list"))

    # Validación de sitios asociados en la vista
    sitios_asociados = db.session.query(SitioHistorico).filter(
        SitioHistorico.tags.any(id=tag.id)
    ).all()
    if sitios_asociados:
        flash("No se puede eliminar un tag asignado a algún sitio.", "error")
        return redirect(url_for("tags.tags_list"))

    # Eliminar usando el servicio
    tags.delete_tag(tag_id)
    flash("Tag eliminado correctamente.", "success")
    return redirect(url_for("tags.tags_list"))