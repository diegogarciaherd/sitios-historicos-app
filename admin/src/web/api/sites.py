from flask import Blueprint, jsonify, request
from core.models.sites import list_sites_with_filters
from core.models.sites import create_sites, get_site
from flask_jwt_extended import jwt_required
from core.models.tags import get_tags_by_ids, assign_tags

sites_api_bp = Blueprint("sites_api", __name__, url_prefix="/api/sites")

def check_filters(filters: dict):
    errors = {}
    if "order_by" in filters and filters["order_by"]:
        if filters["order_by"] != "rating-5-1" or "rating-1-5" or "latest" or "oldest":
            errors["order_by"] = "Criterio de orden invalido."
    if "lat" in filters and filters["lat"]:
        if int(filters["lat"]) < -90 or int(filters["lat"]) > 90:
            errors["lat"] = "Fuera de rango."
    if "long" in filters and filters["long"]:
        if int(filters["long"]) < -180 or int(filters["long"]) > 180:
            errors["long"] = "Fuera de rango."
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
            int(filters["per_page"])
        except ValueError:
            errors["per_page"] = "No es un numero."

        if int(filters["per_page"]) > 100:
            errors["per_page"] = "Debe ser entre 1 y 100."
    
    return errors

def validate_post_data(data: dict):
    errors = []
    required_fields = ["nombre", "estado", "tags", "lat", "lng"]

    for rf in required_fields:
        value = data.get(rf)
        if value is None or (isinstance(value, str)) and not value.strip():
                errors.append(f"El campo {rf} es requerido.")

    return errors


@sites_api_bp.get("/")
def get_sites_by_criteria():
    filters = request.args.to_dict()
    print(filters)
    errors = check_filters(filters)

    if not errors:
        sites = list_sites_with_filters(filters)[0]
        sites_data = [site.to_dict() for site in sites]
        return jsonify(sites_data), 200
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

@sites_api_bp.post("/")
@jwt_required()
def create_site():
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
