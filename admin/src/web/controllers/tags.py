from flask import render_template, Blueprint, request, jsonify, session
from core.models.tags import Tag
from core.models.sites import SitioHistorico
from core.database import db
from sqlalchemy import func
from slugify import slugify
from flask import flash, redirect, url_for

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

# Ruta HTML: lista de tags
@tags_bp.route("/", methods=["GET"])
def tags_list():
    tags = db.session.query(Tag).order_by(Tag.name.asc()).all()
    return render_template(
        "tags/list.html",
        tags=tags,
        logged_user=session.get("user_id")
    )

#  Ruta API: búsqueda + paginación JSON
@tags_bp.route("/api", methods=["GET"])
def get_tags():
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 25

    query = db.session.query(Tag)
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))

    tags = query.order_by(Tag.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

    data = [{
        "id": tag.id,
        "name": tag.name,
        "slug": tag.slug
    } for tag in tags.items]

    return jsonify({
        "results": data,
        "total": tags.total,
        "page": tags.page,
        "pages": tags.pages
    })


@tags_bp.route("/create", methods=["GET", "POST"])
def create_tag():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        # Validaciones
        if len(name) < 3 or len(name) > 50:
            flash("El nombre debe tener entre 3 y 50 caracteres.", "error")
            return redirect(url_for("tags.create_tag"))

        existing = db.session.query(Tag).filter(func.lower(Tag.name) == name.lower()).first()
        if existing:
            flash("Ya existe un tag con ese nombre.", "error")
            return redirect(url_for("tags.create_tag"))

        slug = slugify(name)
        tag = Tag(name=name, slug=slug)
        db.session.add(tag)
        db.session.commit()
        flash("Tag creado correctamente.", "success")
        return redirect(url_for("tags.tags_list"))

    return render_template("tags/create.html")


@tags_bp.route("/edit/<int:tag_id>", methods=["GET", "POST"])
def edit_tag_view(tag_id):
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.tags_list"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if len(name) < 3 or len(name) > 50:
            flash("El nombre debe tener entre 3 y 50 caracteres.", "error")
            return redirect(url_for("tags.edit_tag_view", tag_id=tag_id))

        # Validar que no exista otro tag con el mismo nombre
        existing = db.session.query(Tag).filter(func.lower(Tag.name) == name.lower(), Tag.id != tag_id).first()
        if existing:
            flash("Ya existe un tag con ese nombre.", "error")
            return redirect(url_for("tags.edit_tag_view", tag_id=tag_id))

        tag.name = name
        tag.slug = slugify(name)
        db.session.commit()
        flash("Tag actualizado correctamente.", "success")
        return redirect(url_for("tags.tags_list"))

    return render_template("tags/edit.html", tag=tag)

# ❌ ELIMINAR TAG
@tags_bp.route("/delete/<int:tag_id>", methods=["POST"])
def delete_tag_view(tag_id):
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.tags_list"))

    # Validar que no esté asignado a sitios
    if tag.sitios and len(tag.sitios) > 0:
        flash("No se puede eliminar un tag asignado a algún sitio.", "error")
        return redirect(url_for("tags.tags_list"))

    db.session.delete(tag)
    db.session.commit()
    flash("Tag eliminado correctamente.", "success")
    return redirect(url_for("tags.tags_list"))