# admin/src/web/api/sites.py

"""
API Sites
---------
Contiene los endpoints relacionados con sitios históricos, incluyendo:
- Listado y filtros.
- Creación de sitios.
- Obtención por ID.
- Gestión de favoritos (toggle y listado del usuario).
- Gestión de reseñas (reviews).

Este módulo es utilizado por la aplicación pública mediante JWT.
"""

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
from core.services.favorite_service import toggle_favorite
from core.models.favorites import Favorite
from core.models.sites import SitioHistorico

# del branch de tus compas: búsqueda por radio
from core.services.sites_services import get_sites_within_radius


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

    if "long" in filters and filters["long"]:
        try:
            long_val = float(filters["long"])
            if long_val < -180 or long_val > 180:
                errors["long"] = "Fuera de rango."
        except ValueError:
            errors["long"] = "No es un número."

    if "radius" in filters and filters["radius"]:
        try:
            int(filters["radius"])
        except ValueError:
            errors["radius"] = "No es un número."

    if "page" in filters and filters["page"]:
        try:
            int(filters["page"])
        except ValueError:
            errors["page"] = "No es un número."

    if "per_page" in filters and filters["per_page"]:
        try:
            per_page_int = int(filters["per_page"])
            if per_page_int > 100:
                filters["per_page"] = 100
            elif per_page_int < 1:
                errors["per_page"] = "Debe ser entre 1 y 100."
        except ValueError:
            errors["per_page"] = "No es un número."

    return errors


def validate_post_data(data: dict) -> list[str]:
    """
    Valida los datos necesarios para crear un sitio histórico.

    Args:
        data (dict): Datos enviados por JSON.

    Returns:
        list[str]: Lista de errores encontrados.
    """
    errors: list[str] = []
    required_fields = ["nombre", "estado", "tags", "lat", "lng"]

    for rf in required_fields:
        value = data.get(rf)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"El campo {rf} es requerido.")

    return errors


# ----------------------------------------------------------------------
#                           ENDPOINTS DE SITIOS
# ----------------------------------------------------------------------
@sites_api_bp.get("")
def get_sites_by_criteria():
    """
    Obtiene una lista de sitios filtrados por criterios opcionales.

    Los filtros posibles incluyen ordenamiento, latitud, longitud,
    radio, paginación, etc.

    Returns:
        JSON con la lista de sitios y metadata.
    """
    filters = request.args.to_dict()
    errors = check_filters(filters)

    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed.",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    page = int(filters.get("page", 1) or 1)
    per_page = int(filters.get("per_page", 10) or 10)

    sites, total = list_sites_with_filters(filters, page, per_page)
    sites_data = [site.to_dict() for site in sites]

    return (
        jsonify(
            {
                "data": sites_data,
                "meta": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                },
            }
        ),
        200,
    )


@sites_api_bp.post("")
@jwt_required()
def create_site():
    """
    Crea un nuevo sitio histórico.

    Requiere autenticación JWT.

    Returns:
        201 si se creó correctamente.
    """
    data = request.get_json() or {}
    errors = validate_post_data(data)

    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed.",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    tags = data.pop("tags")
    site = create_sites(**data)
    selected_tags = get_tags_by_ids(tags)
    assign_tags(site, selected_tags)

    return jsonify(site.to_dict()), 201


@sites_api_bp.get("/<int:id>")
def get_site_by_id(id: int):
    """
    Devuelve los datos de un sitio histórico según su ID.

    Args:
        id (int): ID del sitio.

    Returns:
        JSON con el sitio o error 404 si no existe.
    """
    site = get_site(id)
    if site:
        try:
            increment_site_visit_count(id)
        except ValueError:
            pass
        return jsonify(site.to_dict()), 200

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


# ----------------------------------------------------------------------
#                       BÚSQUEDA POR RADIO (branch compas)
# ----------------------------------------------------------------------
@sites_api_bp.get("/nearby")
def get_sites_nearby():
    """
    Devuelve sitios cercanos a una coordenada dada un radio en km.

    Espera query params:
        lat (float): latitud
        lng (float): longitud
        radius (int/float): radio en kilómetros
    """
    params = request.args.to_dict()
    errors = {}

    try:
        lat = float(params.get("lat", ""))
        long = float(params.get("lng", ""))
        radius = float(params.get("radius", ""))
    except ValueError:
        errors["coords"] = "lat, lng y radius deben ser numéricos."

    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parámetros inválidos.",
                        "details": errors,
                    }
                }
            ),
            400,
        )

    sites = get_sites_within_radius(lat, long, radius)
    data = [s.to_dict() for s in sites]
    return jsonify(data), 200


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

    Args:
        site_id (int): ID del sitio a marcar/desmarcar.

    Returns:
        JSON con estado actual del favorito.
    """
    user_id = get_jwt_identity()

    exists = SitioHistorico.query.get(site_id)
    if not exists:
        return jsonify({"error": "Sitio no encontrado"}), 404

    created = toggle_favorite(user_id, site_id)

    return jsonify({"favorite": created, "site_id": site_id}), 200


@sites_api_bp.get("/users/me/favorites")
@jwt_required()
def get_my_favorites():
    """
    Devuelve la lista de todos los sitios marcados como favoritos
    por el usuario autenticado.

    Returns:
        JSON con lista de favoritos.
    """
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()

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

    if "title" in params and isinstance(params["title"], str):
        params["title"] = params["title"].strip()
        if not params["title"]:
            errors["title"] = "El título es obligatorio."
    else:
        errors["title"] = "El título es obligatorio."

    if "body" in params and isinstance(params["body"], str):
        params["body"] = params["body"].strip()
        if not params["body"]:
            errors["body"] = "La descripción es obligatoria."
    else:
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
@jwt_required()
def get_site_reviews(id: int):
    """
    Devuelve todas las reseñas asociadas a un sitio histórico identificado
    por la id ingresada en la URL.

    Args:
        id (int): La id del sitio histórico.
    """
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

    pagination = request.args.to_dict()
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
                    "page": page,
                    "per_page": per_page if per_page else total,
                    "total": total,
                },
            }
        ),
        200,
    )


@sites_api_bp.post("/<int:site_id>/reviews")
@jwt_required()
def create_site_review(site_id: int):
    """
    Crea una nueva reseña para el sitio histórico recibido en la URL.
    La id del sitio histórico se recibe por URL, y los datos de la
    reseña en el cuerpo tipo JSON.

    Args:
        site_id (int): La id del sitio histórico.
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

    params = request.get_json() or {}
    params["site_id"] = site_id
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
@jwt_required()
def get_site_review_by_id(site_id: int, review_id: int):
    """
    Devuelve la reseña especificada para el sitio histórico especificado.

    ATENCIÓN:
    Cada sitio histórico puede tener ninguna o más reseñas asociadas.
    Esta función primero trae todas las reseñas del sitio y luego usa
    `review_id` como índice (1-based) dentro de esa lista.
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

    return jsonify(reviews[review_id - 1].to_dict()), 200


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
        JSON con la lista de sitios más visitados.
    """

    most_visited_sites = get_sites_by_visits()

    sites_data = [site.to_dict() for site in most_visited_sites]

    return (
        jsonify(
            {
                "data": sites_data,
            }
        ),
        200,
    )
