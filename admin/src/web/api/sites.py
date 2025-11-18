# admin/src/core/web/api/sites.py
from flask import Blueprint, jsonify, request
from core.models.sites import list_sites_with_filters
from core.models.sites import create_sites, get_site
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models.tags import get_tags_by_ids, assign_tags
from core.models.reviews import get_reviews_by_site_id, create_review, get_review_by_id
from core.models.reviews import delete_review, ReviewStatus
from core.services.favorite_service import toggle_favorite
from core.models.favorites import Favorite
from core.models.sites import SitioHistorico

sites_api_bp = Blueprint("sites_api", __name__, url_prefix="/api/sites")

def check_filters(filters: dict):
    """
    Revisa, corrige y notifica errores acerca de los filtros de busqueda.

    Args:
        filters (dict): Un diccionario con los filtro de busqueda.

    Returns:
        Errores si se produjeron.
    """
    errors = {}
    valid_orders = {"rating-5-1", "rating-1-5", "latest", "oldest", "name-asc", "name-desc"}

    if "order_by" in filters and filters["order_by"]:
        if filters["order_by"] not in valid_orders:
            errors["order_by"] = "Criterio de orden invalido."
    if "lat" in filters and filters["lat"]:
        try:
            lat_val = float(filters["lat"])
            if lat_val < -90 or lat_val > 90:
                errors["lat"] = "Fuera de rango."
        except ValueError:
            errors["lat"] = "No es un numero."
    if "long" in filters and filters["long"]:
        try:
            long_val = float(filters["long"])
            if long_val < -180 or long_val > 180:
                errors["long"] = "Fuera de rango."
        except ValueError:
            errors["long"] = "No es un numero."
    if "radius" in filters and filters["radius"]:
        try:
            int(filters["radius"])
        except ValueError:
            errors["radius"] = "No es un numero."
    if "page" in filters and filters["page"]:
        try:
            int(filters["page"])
        except ValueError:
            errors["page"] = "No es un numero."
    if "per_page" in filters and filters["per_page"]:
        try:
            per_page_int = int(filters["per_page"])
            if per_page_int > 100:
                filters["per_page"] = 100
            elif per_page_int < 1:
                errors["per_page"] = "Debe ser entre 1 y 100."
        except ValueError:
            errors["per_page"] = "No es un numero."
    
    return errors

def validate_post_data(data: dict):
    """
    Valida los datos de entrada en un post para crear un sitio.

    Args:
        data (dict): Los datos del nuevo sitio.

    Returns:
        Errores si se produjeron.
    """
    errors = []
    required_fields = ["nombre", "estado", "tags", "lat", "lng"]

    for rf in required_fields:
        value = data.get(rf)
        if value is None or (isinstance(value, str)) and not value.strip():
                errors.append(f"El campo {rf} es requerido.")

    return errors

@sites_api_bp.get("")
def get_sites_by_criteria():
    """
    Busca los sitios historicos de acuerdo a los criterios especificados.
    Los criterios son recibidos en la URL.
    """
    filters = request.args.to_dict()
    errors = check_filters(filters)

    if not errors:
        sites, total = list_sites_with_filters(filters, filters["page"] if "page" in filters else 1, filters["per_page"] if "per_page" in filters else 10)
        sites_data = [site.to_dict() for site in sites]
        return jsonify(sites_data, {
            "meta": {
                "page": filters["page"] if "page" in filters else 1,
                "per_page": filters["per_page"] if "per_page" in filters else total,
                "total": total
            }
        }), 200
    elif errors:
        return jsonify({
            "error" : {
                "code": "invalid_query",
                "message": "Parameter validation failed.",
                "details": errors
            }
        }), 400
    else:
        return jsonify({
            "error": {
            "code": "server_error",
            "message": "An unexpected error occurred."
            }
        }), 500

@sites_api_bp.post("")
@jwt_required()
def create_site():
    """
    Crea un nuevo sitio historico a partir de los datos recibidos en formato JSON.
    """
    data = request.get_json()
    errors = validate_post_data(data)
    if not errors:
        tags = data.pop("tags")
        site = create_sites(**data)
        selected_tags = get_tags_by_ids(tags)
        assign_tags(site, selected_tags)
        return jsonify(data), 201
    elif errors:
        return jsonify({
            "error" : {
                "code": "invalid_query",
                "message": "Parameter validation failed.",
                "details": errors
            }
        }), 400
    else:
        return jsonify({
            "error": {
            "code": "server_error",
            "message": "An unexpected error occurred"
            }
        }), 500

@sites_api_bp.get("/<int:id>")
def get_site_by_id(id):
    """
    Devuelve el sitio historico que corresponda con la id especificada
    en la URL.
    """
    site = get_site(id)
    if site:
        site_data = site.to_dict()
        return jsonify(site_data), 200
    elif not site:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": "No existe un sitio con ese id."
            }
        }), 404
    else:
        return jsonify({
            "error": {
            "code": "server_error",
            "message": "An unexpected error occurred"
            }
        }), 500
    

# marcar / desmarcar favorito
@api_bp.post("/sites/<int:site_id>/favorite")
@jwt_required()
def toggle_favorite_api(site_id):
    user_id = get_jwt_identity()

    exists = SitioHistorico.query.get(site_id)
    if not exists:
        return jsonify({"error": "Sitio no encontrado"}), 404

    created = toggle_favorite(user_id, site_id)

    return jsonify({
        "favorite": created,
        "site_id": site_id
    }), 200


# obtener favoritos de usuario
@api_bp.get("/users/me/favorites")
@jwt_required()
def get_my_favorites():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "site_id": fav.site.id,
            "site_name": fav.site.nombre,
            "created_at": fav.created_at.isoformat()
        }
        for fav in favorites
    ])

# --- Reviews ---
def check_pagination_params(params: dict):
    """
    Chequea y sanitiza los parametros de paginacion para un GET
    sobre las reseñas de un sitio.

    Args:
        params (dict): Los datos de paginacion (page y per_page)

    Returns:
        Errores si se produjeron.
    """
    errors = []
    if "per_page" in params:
        try:
            int(params["per_page"])
            if params["per_page"] > 100:
                params["per_page"] = 100
        except ValueError:
            errors["per_page"] = "No es un numero."
    if "page" in params and params["page"]:
        try:
            int(params["page"])
        except ValueError:
            errors["page"] = "No es un numero."
    return errors

def check_review_post_params(params: dict):
    """
    Chequea y sanitiza los parametros de un POST para la creacion de
    una nueva reseña.

    Args:
        params (dict): Los datos de la nueva reseña.

    Returns:
        Errores si se produjeron.
    """
    errors = []
    if "rating" in params:
        if params["rating"] > 5:
            params["rating"] = 5
    else:
        errors["rating"] = "El puntaje es obligatorio."
    
    if "title" in params:
        params["title"].strip()
    else:
        errors["title"] = "El titulo es obligatorio."
    
    if "body" in params:
        params["body"].strip()
    else:
        errors["body"] = "La descripcion es obligatoria."
    
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
    Devuelve todas las reseñas asociadas a un sitio historico identificado
    por la id ingresada en la URL.

    Args:
        id (int): La id del sitio historico.
    """
    site = get_site(id)
    if not site:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"El sitio {id} no existe."
            }
        }), 404
    
    pagination = request.args.to_dict()
    errors = check_pagination_params(pagination)
    reviews, total = get_reviews_by_site_id(id, pagination["page"] if "page" in pagination else 1, pagination["per_page"] if "per_page" in pagination else 10)
    if not errors and total > 0:
        reviews_data = [review.to_dict() for review in reviews]
        return jsonify(reviews_data, {
            "meta": {
                "page": pagination["page"] if "page" in pagination else 1,
                "per_page": pagination["per_page"] if "per_page" in pagination else total,
                "total": total
            }
        }), 200
    elif errors:
        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "Invalid input data",
                "details": errors
            }
        }), 400
    else:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error ocurred."
            }
        }), 500

@sites_api_bp.post("/<int:site_id>/reviews")
@jwt_required()
def create_site_review(site_id: int):
    """
    Crea una nueva reseña para el sitio historico recibido en la URL.
    La id del sitio historico se recibe por URL, y los datos de la
    reseña en el cuerpo tipo JSON.

    Args:
        site_id (int): La id del sitio historico.
    """
    int(site_id)
    site = get_site(site_id)
    if not site:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"El sitio {site_id} no existe."
            }
        }), 404
    params = request.get_json()
    params["site_id"] = site_id
    errors = check_review_post_params(params)

    if not errors:
        review = create_review(**params)
        return jsonify(review.to_dict()), 201
    elif errors:
        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "Invalid input data",
                "details": errors
            }
        }), 400
    else:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error ocurred."
            }
        }), 500

@sites_api_bp.get('/<int:site_id>/reviews/<int:review_id>')
@jwt_required()
def get_site_review_by_id(site_id: int, review_id: int):
    """
    Devuelve la reseña especificada para el sitio historico especificado.
    
    LEER BIEN:
    Cada sitio historico puede tener ninguna o mas reseñas asociadas.
    Cada reseña en la tabla tiene su PK que es la id, pero esta funcion
    primero trae TODAS las reseñas de un sitio historico, y en esa lista
    aplica el "review_id". Por ejemplo:

    El sitio historico 3 tiene las reseñas con PK 4, 6, 10.
    La funcion primero va a retornar una lista con las reseñas 4, 6 y 10,
    pero una vez que estan en dicha lista, esas reseñas pasaran a ser
    1, 2 y 3. O sea que un GET a .../api/sites/3/reviews/2 va a devolver
    la reseña con PK 6 del sitio historico 3. Se me ocurrio hacerlo asi
    porque sino quedaba medio raro/inconsistente, pero si no se entiende
    lo revierto.

    Args:
        site_id (int): La id del sitio historico.
        review_id (int): La id de la reseña (relativa a la lista).
    """
    int(site_id)
    int(review_id)
    site = get_site(site_id)
    reviews, total = get_reviews_by_site_id(site_id)
    if not site:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"El sitio {site_id} no existe."
            }
        }), 404
    elif review_id > total:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"La reseña {review_id} no existe."
            }
        }), 404
    elif reviews:
        return jsonify(reviews[review_id-1].to_dict()), 200
    else:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error ocurred."
            }
        }), 500

@sites_api_bp.delete("/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def delete_site_review_by_id(site_id: int, review_id: int):
    """
    Elimina (fisica) una reseña del sitio historico especificado.

    ATENCION: Utiliza el mismo mecanismo que get_site_review_by_id() (ver docstring).

    Args:
        site_id (int): La id del sitio historico.
        review_id (int): La id de la reseña (relativa a la lista).
    """
    int(site_id)
    int(review_id)
    site = get_site(site_id)
    reviews, total = get_reviews_by_site_id(site_id)
    if not site:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"El sitio {site_id} no existe."
            }
        }), 404
    elif review_id > total:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": f"La reseña {review_id} no existe."
            }
        }), 404
    elif reviews:
        delete_review(reviews[review_id-1].id)
        return jsonify({}), 204
    else:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error ocurred."
            }
        }), 500

# Metodos Correccion
def convert_and_validate_filters(filters: dict):
    """
    Convierte los valores de los filtros a enteros y valida los rangos.
    """
    errors = {}
    if "page" in filters and filters["page"]:
        try:
            filters["page"] = int(filters["page"])
            if filters["page"] < 1:
                errors["page"] = "Debe ser mayor a 0."
        except ValueError:
            errors["page"] = "No es un numero."

    if "per_page" in filters and filters["per_page"]:
        try:
            filters["per_page"] = int(filters["per_page"])
            if filters["per_page"] < 1:
                errors["per_page"] = "Debe ser mayor a 0."
            elif filters["per_page"] > 100:
                filters["per_page"] = 100
        except ValueError:
            errors["per_page"] = "No es un numero."
    return errors

@sites_api_bp.get("/fix")
def get_sites_by_criteria_fixed():
    """
    Busca los sitios historicos de acuerdo a los criterios especificados.
    Versión que usa convert_and_validate_filters para manejar tipos correctamente.
    Los criterios son recibidos en la URL.
    """
    filters = request.args.to_dict()
    errors = check_filters(filters)
    
    # Convertir tipos y validar rangos
    conversion_errors = convert_and_validate_filters(filters)
    errors.update(conversion_errors)

    if not errors:
        # Asegurar que page y per_page tengan valores por defecto correctos
        page = filters.get("page", 1)
        per_page = filters.get("per_page", 10)
        
        # Convertir a int si aún son strings (por si no pasaron por convert_and_validate_filters)
        if isinstance(page, str):
            try:
                page = int(page) if page else 1
            except ValueError:
                page = 1
        if isinstance(per_page, str):
            try:
                per_page = int(per_page) if per_page else 10
            except ValueError:
                per_page = 10
                
        sites, total = list_sites_with_filters(filters, page, per_page)
        sites_data = [site.to_dict() for site in sites]
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        return jsonify({
            "data": sites_data,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }), 200
    elif errors:
        return jsonify({
            "error" : {
                "code": "invalid_query",
                "message": "Parameter validation failed.",
                "details": errors
            }
        }), 400
    else:
        return jsonify({
            "error": {
            "code": "server_error",
            "message": "An unexpected error occurred."
            }
        }), 500