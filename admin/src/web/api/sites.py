# admin/src/web/api/sites.py

"""
API de Sitios
-------------
Contiene los endpoints relacionados con sitios históricos, incluyendo:
- Listado y filtros.
- Creación de sitios.
- Obtención por ID.
- Gestión de favoritos (toggle y listado del usuario).
- Gestión de reseñas (reviews).

Este módulo es utilizado por la aplicación pública mediante JWT.
"""

from core.database import db
from core.models.favorites import Favorite
from core.models.sites import SitioHistorico
from core.services.favorite_service import toggle_favorite

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models.sites import (
    list_sites_with_filters,
    create_sites,
    get_site,
    increment_site_visit_count,
    get_sites_by_visits,
)
from core.models.tags import get_tags_by_ids, assign_tags
from core.models.reviews import (
    get_reviews_by_site_id,
    create_review,
    get_review_by_id,
    delete_review,
    ReviewStatus,
)

# Nota: la lógica espacial ahora se maneja en `list_sites_with_filters` (PostGIS/ST_DWithin)

# Blueprint principal con prefijo único
sites_api_bp = Blueprint("sites_api", __name__, url_prefix="/api/sites")


# ----------------------------------------------------------------------
#                           VALIDACIONES BÁSICAS
# ----------------------------------------------------------------------
def check_filters(filters: dict) -> dict:
    """
    Valida los filtros de búsqueda enviados en el querystring.
    Verifica tipos, rangos y valores permitidos.

    Args:
        filters (dict): Diccionario con los parámetros recibidos.

    Returns:
        dict: Diccionario con errores, vacío si no hay problemas.
    """
    errors: dict[str, str] = {}
    valid_orders = {
        "rating-5-1",
        "rating-1-5",
        "latest",
        "oldest",
        "name-asc",
        "name-desc",
    }

    if "order_by" in filters and filters["order_by"]:
        if filters["order_by"] not in valid_orders:
            errors["order_by"] = "Criterio de orden inválido."

    if "lat" in filters and filters["lat"]:
        try:
            lat_val = float(filters["lat"])
            if lat_val < -90 or lat_val > 90:
                errors["lat"] = "Fuera de rango."
        except ValueError:
            errors["lat"] = "No es un número."

    if "lng" in filters and filters["lng"]:
        try:
            lng_val = float(filters["lng"])
            if lng_val < -180 or lng_val > 180:
                errors["lng"] = "Fuera de rango."
        except ValueError:
            errors["lng"] = "No es un número."

    if "radius" in filters and filters["radius"]:
        try:
            float(filters["radius"])
        except ValueError:
            errors["radius"] = "No es un número."

    return errors


# ----------------------------------------------------------------------
#                           LISTADO Y FILTROS DE SITIOS
# ----------------------------------------------------------------------
@sites_api_bp.get("")
def list_sites():
    """
    Lista sitios históricos con filtros opcionales:
    - Tags
    - Orden
    - Nombre
    - Radio (lat, lng, radius)

    Los filtros llegan vía querystring.
    """
    filters = request.args.to_dict(flat=True)
    errors = check_filters(filters)

    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_filters",
                        "message": "Invalid filter parameters",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    # Filtro por tags si vienen
    tag_ids = filters.get("tags")
    tags = None
    if tag_ids:
        try:
            tag_ids_list = [int(t) for t in tag_ids.split(",")]
        except ValueError:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_filters",
                            "message": "Tag IDs must be integers",
                        }
                    }
                ),
                400,
            )
        tags = get_tags_by_ids(tag_ids_list)

    # Toda la lógica (incluyendo lat/lng/radius) la resuelve list_sites_with_filters
    sites = list_sites_with_filters(filters, tags)

    data = [site.to_dict() for site in sites[0]]

    return jsonify({"data": data}), 200


# ----------------------------------------------------------------------
#                           CREACIÓN DE SITIOS
# ----------------------------------------------------------------------
@sites_api_bp.post("/")
@jwt_required()
def create_site():
    """
    Crea uno o varios sitios históricos a partir de un JSON.
    Este endpoint está pensado principalmente para la app privada.
    """
    payload = request.get_json() or {}

    if isinstance(payload, list):
        created_sites = create_sites(payload)
    elif isinstance(payload, dict):
        created_sites = [create_sites([payload])[0]]
    else:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_payload",
                        "message": "Payload must be a list or dict",
                    }
                }
            ),
            400,
        )

    return jsonify([site.to_dict() for site in created_sites]), 201


# ----------------------------------------------------------------------
#                           OBTENCIÓN POR ID
# ----------------------------------------------------------------------
@sites_api_bp.get("/<int:id>")
def get_site_by_id(id: int):
    """
    Devuelve un sitio histórico por su ID.
    Además incrementa el contador de visitas.
    """
    site = get_site(id)
    if not site:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "No existe un sitio con ese id.",
                    }
                }
            ),
            404,
        )

    # Contabilizamos la visita
    increment_site_visit_count(id)

    return jsonify(site.to_dict()), 200


# ----------------------------------------------------------------------
#                           FAVORITOS
# ----------------------------------------------------------------------
@sites_api_bp.post("/<int:site_id>/favorite")
@jwt_required()
def toggle_favorite_api(site_id: int):
    """
    Crea o elimina un favorito según el estado actual.

    La acción se determina automáticamente:
    - Si el usuario ya marcó el sitio → se elimina.
    - Si no lo marcó → se crea.

    Requiere JWT.
    """
    # JWT guarda el id como string → lo convertimos a int
    user_id = int(get_jwt_identity())

    site = db.session.get(SitioHistorico, site_id)
    if not site:
        return jsonify({"error": "Sitio no encontrado"}), 404

    created = toggle_favorite(user_id, site_id)

    return jsonify({"favorite": created, "site_id": site_id}), 200


@sites_api_bp.get("/users/me/favorites")
@jwt_required()
def get_my_favorites():
    """
    Devuelve la lista de todos los sitios marcados como favoritos
    por el usuario autenticado.
    """
    user_id = int(get_jwt_identity())
    favorites = db.session.query(Favorite).filter_by(user_id=user_id).all()

    return (
        jsonify(
            [
                {
                    "site_id": fav.site.id,
                    "site_name": fav.site.nombre,
                    "created_at": fav.created_at.isoformat(),
                }
                for fav in favorites
            ]
        ),
        200,
    )


# ----------------------------------------------------------------------
#                               REVIEWS
# ----------------------------------------------------------------------
def check_pagination_params(params: dict) -> dict:
    """
    Chequea y sanitiza los parámetros de paginación para un GET
    sobre las reseñas de un sitio.

    Args:
        params (dict): Los datos de paginación (page y per_page)

    Returns:
        dict: errores si se produjeron.
    """
    errors: dict[str, str] = {}

    if "per_page" in params:
        try:
            per_page = int(params["per_page"])
            if per_page > 100:
                params["per_page"] = 100
        except ValueError:
            errors["per_page"] = "No es un número."

    if "page" in params and params["page"]:
        try:
            int(params["page"])
        except ValueError:
            errors["page"] = "No es un número."

    return errors


def check_review_post_params(params: dict) -> dict:
    """
    Chequea y sanitiza los parámetros de un POST para la creación de
    una nueva reseña.

    Args:
        params (dict): Los datos de la nueva reseña.

    Returns:
        dict: errores si se produjeron.
    """
    errors: dict[str, str] = {}

    if "rating" in params:
        try:
            rating = int(params["rating"])
            if rating > 5:
                params["rating"] = 5
        except (TypeError, ValueError):
            errors["rating"] = "El puntaje debe ser numérico."
    else:
        errors["rating"] = "El puntaje es obligatorio."

    if "title" in params and not params["title"]:
        errors["title"] = "El título es obligatorio."

    if "body" in params and not params["body"]:
        errors["body"] = "La descripción es obligatoria."

    if "status" in params:
        match params["status"]:
            case "pending":
                params["status"] = ReviewStatus.PENDING
            case "approved":
                params["status"] = ReviewStatus.APPROVED
            case "rejected":
                params["status"] = ReviewStatus.REJECTED

    return errors


@sites_api_bp.get("/<int:id>/reviews")
def get_site_reviews(id: int):
    """
    Devuelve todas las reseñas asociadas a un sitio histórico identificado
    por la id ingresada en la URL.

    Lectura pública (no requiere JWT), como pide la consigna.
    """
    # Si el sitio no existe, 404
    site = get_site(id)
    if not site:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"El sitio {id} no existe.",
                    }
                }
            ),
            404,
        )

    pagination = request.args.to_dict(flat=True)
    errors = check_pagination_params(pagination)

    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    page = int(pagination.get("page", 1) or 1)
    per_page = int(pagination.get("per_page", 10) or 10)

    reviews, total = get_reviews_by_site_id(id, page, per_page)
    reviews_data = [review.to_dict() for review in reviews]

    return (
        jsonify(
            {
                "data": reviews_data,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                },
            }
        ),
        200,
    )


@sites_api_bp.post("/<int:site_id>/reviews")
@jwt_required()
def create_site_review(site_id: int):
    """
    Crea una nueva reseña para el sitio histórico especificado.
    Requiere usuario autenticado (JWT).
    """
    site = get_site(site_id)
    if not site:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"El sitio {site_id} no existe.",
                    }
                }
            ),
            404,
        )

    user_id = int(get_jwt_identity())
    params = request.get_json() or {}
    params["site_id"] = site_id
    params["user_id"] = user_id

    errors = check_review_post_params(params)
    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    review = create_review(**params)
    return jsonify(review.to_dict()), 201


@sites_api_bp.get("/<int:site_id>/reviews/<int:review_id>")
def get_site_review_by_id(site_id: int, review_id: int):
    """
    Devuelve la reseña especificada para el sitio histórico especificado.

    ATENCIÓN:
    Cada sitio histórico puede tener ninguna o más reseñas asociadas.
    """
    site = get_site(site_id)
    if not site:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"El sitio {site_id} no existe.",
                    }
                }
            ),
            404,
        )

    reviews, total = get_reviews_by_site_id(site_id)
    if review_id > total:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"La reseña {review_id} no existe.",
                    }
                }
            ),
            404,
        )

    if not reviews:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred.",
                    }
                }
            ),
            500,
        )

    review = reviews[review_id - 1]
    return jsonify(review.to_dict()), 200


@sites_api_bp.delete("/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def delete_site_review_by_id(site_id: int, review_id: int):
    """
    Elimina (física) una reseña del sitio histórico especificado.

    ATENCIÓN: Utiliza el mismo mecanismo que get_site_review_by_id().
    """
    site = get_site(site_id)
    if not site:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"El sitio {site_id} no existe.",
                    }
                }
            ),
            404,
        )

    reviews, total = get_reviews_by_site_id(site_id)
    if review_id > total:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"La reseña {review_id} no existe.",
                    }
                }
            ),
            404,
        )

    if not reviews:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred.",
                    }
                }
            ),
            500,
        )

    delete_review(reviews[review_id - 1].id)
    # 204: sin body
    return ("", 204)


@sites_api_bp.get("/most_visited")
def get_most_visited_sites():
    """
    Devuelve una lista de los sitios más visitados.

    Returns:
        JSON con lista de sitios.
    """

    most_visited_sites = get_sites_by_visits()
    sites_data = [site.to_dict() for site in most_visited_sites]

    return jsonify({"data": sites_data}), 200
