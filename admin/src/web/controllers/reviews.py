# admin/src/web/controllers/reviews.py

from __future__ import annotations
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, abort
from core.database import db
from core.services.auth_roles import require_permission
from core.models.reviews import Review, ReviewStatus
from core.models.sites import get_site
from .validators.review_validator import validate_review_data

reviews_bp = Blueprint(
    "reviews",
    __name__,
    url_prefix="/reseñas",
    template_folder="../templates/reviews"
)

# --- Público / usuarios logueados: crear reseña (queda en PENDING)
@reviews_bp.route("/nuevo/<int:site_id>", methods=["POST"])
def create_public(site_id: int):
    """Crea una reseña para un sitio y la deja en estado PENDING."""
    site = get_site(site_id)
    if not site:
        abort(404)

    data = request.form.to_dict()
    errors = validate_review_data(data)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("sites.view_site", id=site_id))

    r = Review(
        site_id=site_id,
        user_id=session.get("user_id"),  # puede ser None si se permite anónimo
        rating=int(data["rating"]),
        title=data["title"].strip(),
        body=data["body"].strip(),
        status=ReviewStatus.PENDING,
    )
    db.session.add(r)
    db.session.commit()

    flash("¡Gracias! Tu reseña quedó en revisión.", "success")
    return redirect(url_for("sites.view_site", id=site_id))


# --- Moderación: listado con filtros + paginación
@reviews_bp.route("/moderar", methods=["GET"])
@require_permission("reviews.queue_view")
def moderate_list():
    """Lista de reseñas a moderar (permiso reviews.queue_view)."""
    page = request.args.get("page", 1, type=int)
    per_page = 25

    q = db.session.query(Review).order_by(Review.created_at.desc())

    status = request.args.get("status", "").strip()
    if status in ("pending", "approved", "rejected"):
        q = q.filter(Review.status == ReviewStatus(status))

    site_id = request.args.get("site_id", type=int)
    if site_id:
        q = q.filter(Review.site_id == site_id)

    rating = request.args.get("rating", type=int)
    if rating:
        q = q.filter(Review.rating == rating)

    total = q.count()
    pages = (total + per_page - 1) // per_page
    rows = q.limit(per_page).offset((page - 1) * per_page).all()

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
        "status": status,
        "site_id": site_id or "",
        "rating": rating or "",
    }

    return render_template(
        "reviews/moderation.html",
        items=rows,
        pagination=pagination,
        current_filters=current_filters,
    )


# --- Aprobar reseña
@reviews_bp.route("/aprobar/<int:id>", methods=["POST"])
@require_permission("reviews.moderate")
def approve(id: int):
    r = db.session.get(Review, id) or abort(404)
    r.status = ReviewStatus.APPROVED
    r.moderated_by = session.get("user_id")
    r.moderated_at = datetime.utcnow()
    r.reject_reason = None
    db.session.commit()

    flash("Reseña aprobada.", "success")
    return redirect(request.referrer or url_for("reviews.moderate_list"))


# --- Rechazar reseña
@reviews_bp.route("/rechazar/<int:id>", methods=["POST"])
@require_permission("reviews.moderate")
def reject(id: int):
    r = db.session.get(Review, id) or abort(404)
    r.status = ReviewStatus.REJECTED
    r.moderated_by = session.get("user_id")
    r.moderated_at = datetime.utcnow()
    r.reject_reason = request.form.get("reason", "").strip() or None
    db.session.commit()

    flash("Reseña rechazada.", "success")
    return redirect(request.referrer or url_for("reviews.moderate_list"))


# --- Eliminar reseña (quien tenga delete_any)
@reviews_bp.route("/eliminar/<int:id>", methods=["POST"])
@require_permission("reviews.delete_any")
def delete(id: int):
    r = db.session.get(Review, id) or abort(404)
    db.session.delete(r)
    db.session.commit()

    flash("Reseña eliminada.", "success")
    return redirect(request.referrer or url_for("reviews.moderate_list"))
