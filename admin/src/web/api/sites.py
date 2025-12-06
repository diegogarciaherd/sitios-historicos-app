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

# admin/src/web/api/sites.py
import enum
from core.database import db
from core.models.favorites import Favorite
from core.models.sites import SitioHistorico
from core.services.favorite_service import toggle_favorite
from core.models.reviews import create_review, Review
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models.sites import (
    list_sites_with_filters,
    get_site,
    increment_site_visit_count,
)
from core.models.tags import get_tags_by_ids, assign_tags
from core.models.reviews import (
    get_reviews_by_site_id,
    create_review,
    get_review_by_id,
    delete_review,
    ReviewStatus,
    get_reviews_by_user_id,
    update_review,
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
        "latest",  # muestra los más nuevos primero
        "oldest",  # muestra los más antiguos primero
        "name-asc",
        "name-desc",
        "most-visited",
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


# ----------------------------------------------------------------------
#                           LISTADO Y FILTROS DE SITIOS
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

    print("--- filters: ", filters)

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
    Devuelve los sitios marcados como favoritos por el usuario autenticado.

    Compatibilidad:
    - Si NO se envían parámetros de paginación/orden → devuelve una lista simple
      (comportamiento anterior, usado por FavoritesView).
    - Si se envían page/per_page/order o 'paginated' → devuelve { data, meta }.
    """
    user_id = int(get_jwt_identity())
    params = request.args.to_dict(flat=True)

    # ¿El caller quiere paginación?
    wants_pagination = any(
        key in params for key in ("page", "per_page", "order", "paginated")
    )

    base_query = db.session.query(Favorite).filter_by(user_id=user_id)

    if not wants_pagination:
        favorites = base_query.all()
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

    # Con paginación
    errors = check_pagination_params(params)
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

    page = int(params.get("page", 1) or 1)
    per_page = int(params.get("per_page", 25) or 25)
    order = params.get("order", "desc")

    query = base_query
    if order == "asc":
        query = query.order_by(Favorite.created_at.asc())
    else:
        query = query.order_by(Favorite.created_at.desc())

    total = query.count()
    favorites = query.offset((page - 1) * per_page).limit(per_page).all()

    data = [
        {
            "site_id": fav.site.id,
            "site_name": fav.site.nombre,
            "created_at": fav.created_at.isoformat(),
        }
        for fav in favorites
    ]

    return (
        jsonify(
            {
                "data": data,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                },
            }
        ),
        200,
    )


@sites_api_bp.get("/favorites")
@jwt_required()
def get_favorites():
    """
    Devuelve los sitios marcados como favoritos por el usuario autenticado.

    Compatibilidad:
    - Si NO se envían parámetros de paginación/orden → devuelve una lista simple
      (comportamiento anterior, usado por FavoritesView).
    - Si se envían page/per_page/order o 'paginated' → devuelve { data, meta }.
    """
    user_id = int(get_jwt_identity())
    params = request.args.to_dict(flat=True)

    # ¿El caller quiere paginación?
    wants_pagination = any(
        key in params for key in ("page", "per_page", "order", "paginated")
    )

    base_query = db.session.query(Favorite).filter_by(user_id=user_id)

    if not wants_pagination:
        favorites = base_query.all()
        return (
            jsonify(
                [
                    fav.site.to_dict()
                    for fav in favorites
                ]
            ),
            200,
        )

    # Con paginación
    errors = check_pagination_params(params)
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

    page = int(params.get("page", 1) or 1)
    per_page = int(params.get("per_page", 25) or 25)
    order = params.get("order", "desc")

    query = base_query
    if order == "asc":
        query = query.order_by(Favorite.created_at.asc())
    else:
        query = query.order_by(Favorite.created_at.desc())

    total = query.count()
    favorites = (
        query.offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    data = [
        fav.site.to_dict()
        for fav in favorites
    ]

    return (
        jsonify(
            {
                "data": data,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                },
            }
        ),
        200,
    )


# ----------------------------------------------------------------------
#                               REVIEWS
# ----------------------------------------------------------------------

# Reglas de validación de reseñas
MIN_REVIEW_BODY_LEN = 20
MAX_REVIEW_BODY_LEN = 1000
MAX_REVIEW_TITLE_LEN = 120


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
    Chequea y sanitiza los parámetros de un POST/POST para la creación o
    actualización de una reseña.

    Validaciones:
    - rating obligatorio, entero entre 1 y 5.
    - title obligatorio, sin espacios sobrantes, máx. 120 caracteres.
    - body obligatorio, entre 20 y 1000 caracteres.
    - status (opcional) mapeado a ReviewStatus.
    """
    errors: dict[str, str] = {}

    # -------- rating --------
    rating_raw = params.get("rating")
    if rating_raw is None:
        errors["rating"] = "El puntaje es obligatorio."
    else:
        try:
            rating_int = int(rating_raw)
        except (TypeError, ValueError):
            errors["rating"] = "El puntaje debe ser numérico."
        else:
            if rating_int < 1 or rating_int > 5:
                errors["rating"] = "El puntaje debe estar entre 1 y 5."
            else:
                # guardamos el entero "limpio"
                params["rating"] = rating_int

    # -------- title --------
    title_raw = (params.get("title") or "").strip()
    if not title_raw:
        errors["title"] = "El título es obligatorio."
    elif len(title_raw) > MAX_REVIEW_TITLE_LEN:
        errors["title"] = (
            f"El título no puede superar los {MAX_REVIEW_TITLE_LEN} caracteres."
        )
    else:
        params["title"] = title_raw

    # -------- body --------
    body_raw = (params.get("body") or "").strip()
    if not body_raw:
        errors["body"] = "La descripción es obligatoria."
    else:
        length = len(body_raw)
        if length < MIN_REVIEW_BODY_LEN:
            errors["body"] = (
                f"La descripción debe tener al menos {MIN_REVIEW_BODY_LEN} caracteres."
            )
        elif length > MAX_REVIEW_BODY_LEN:
            errors["body"] = (
                f"La descripción no puede superar los {MAX_REVIEW_BODY_LEN} caracteres."
            )
        else:
            params["body"] = body_raw

    # -------- status (opcional) --------
    if "status" in params and params["status"]:
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
def create_review_route(site_id):  
    """
    Crea una nueva reseña para un sitio específico.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['rating', 'title', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Validar que el usuario no tenga ya una reseña para este sitio
        existing_review = (
            db.session.query(Review)
            .filter(
                Review.user_id == current_user_id,
                Review.site_id == site_id
            )
            .first()
        )
        
        if existing_review:
            return jsonify({
                'success': False,
                'error': 'Ya tienes una reseña para este sitio. Solo se permite una reseña por usuario.'
            }), 400
        
        # Crear la reseña
        review, message = create_review(
            user_id=current_user_id,
            site_id=site_id,
            rating=data['rating'],
            title=data['title'],
            body=data['body']
        )
        
        if not review:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
        return jsonify({
            'success': True,
            'message': '¡Reseña enviada exitosamente! Gracias por tu aporte.',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Error creando reseña: {str(e)}")  
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }), 500

@sites_api_bp.get("/users/me/reviews")
@jwt_required()
def get_my_reviews():
    """
    Devuelve las reseñas del usuario autenticado, con paginación
    y orden por fecha (asc/desc). Pensado para el Perfil del Usuario.
    """
    user_id = int(get_jwt_identity())
    params = request.args.to_dict(flat=True)

    errors = check_pagination_params(params)
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

    page = int(params.get("page", 1) or 1)
    per_page = int(params.get("per_page", 25) or 25)
    order = params.get("order", "desc")
    status = params.get("status", "all")  # Nuevo parámetro

    # Validar que el status sea válido
    valid_statuses = ["all", "approved", "pending", "rejected"]
    if status not in valid_statuses:
        status = "all"

    reviews, total = get_reviews_by_user_id(user_id, page, per_page, order, status)

    data = []
    for review in reviews:
        body = review.body or ""
        data.append(
            {
                "id": review.id,
                "site_id": review.site_id,
                "site_name": getattr(review.site, "nombre", None),
                "rating": review.rating,
                "created_at": review.created_at.isoformat(),
                "body": body[:160],
                "title": review.title,
                "status": review.status.value if isinstance(review.status, enum.Enum) else review.status,
            }
        )

    return (
        jsonify(
            {
                "data": data,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "status": status,  # Incluir el estado actual en la respuesta
                    "order": order,
                },
            }
        ),
        200,
    )


@sites_api_bp.post("/users/me/reviews/<int:review_id>")
@jwt_required()
def update_my_review(review_id: int):
    """
    Actualiza la reseña especificada del usuario autenticado.
    """
    user_id = int(get_jwt_identity())
    params = request.get_json() or {}

    review = get_review_by_id(review_id)
    if not review or review.user_id != user_id:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": f"La reseña {review_id} no existe o no pertenece al usuario.",
                    }
                }
            ),
            404,
        )

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

    message = update_review(review_id, **params)
    return jsonify({"message": message}), 200


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
    Elimina una reseña del sitio histórico especificado.

    - Requiere JWT.
    - Solo permite borrar la reseña si pertenece al usuario autenticado
      y al sitio indicado.
    """
    user_id = int(get_jwt_identity())

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

    review = get_review_by_id(review_id)
    if not review:
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

    # Validar que la reseña sea del sitio hecha por el usuario logueado
    if review.site_id != site_id or review.user_id != user_id:
        return (
            jsonify(
                {
                    "error": {
                        "code": "forbidden",
                        "message": "No tenés permiso para eliminar esta reseña.",
                    }
                }
            ),
            403,
        )

    delete_review(review.id)
    # 204: sin body
    return ("", 204)
