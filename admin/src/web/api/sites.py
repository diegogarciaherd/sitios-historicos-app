from flask import Blueprint, jsonify, request
from core.models.sites import list_sites_with_filters, SitioHistorico as Site
from core.models.sites import create_sites, EstadoConservacion
from flask_jwt_extended import jwt_required

sites_api_bp = Blueprint("sites_api", __name__, url_prefix="/api/sites")

#filters: search, city, province, tags, order_by, lat, long, radius, page, per_page
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
#nombre, descripcionbreve, desccompleta, ciudad, prov, yearinaugu
#categoria, fechareg, tags, lat, longitud
    if "id" in data and data["id"]:
        data.pop("id", None)
    if "visible" in data and data["visible"]:
        data["visible"] = True
    if "estado" in data and data["estado"]:
        data["estado"].upper()


@sites_api_bp.get("/")
def get_sites_by_criteria():
    filters = request.args.to_dict()
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
#@jwt_required()
def create_site():
    data = request.get_json()
    errors = validate_post_data(data)
    l = data.pop("tags")
    print(data)
    return "a"
    if not errors:
        create_sites(**data)
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
