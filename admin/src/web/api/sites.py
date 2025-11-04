from flask import Blueprint, jsonify, request
from core.models.sites import list_sites_with_filters, SitioHistorico as Site

sites_api_bp = Blueprint("sites_api", __name__, url_prefix="/api/sites")

@sites_api_bp.get("/")
def get_sites_by_criteria():
    print(request.args.to_dict())
    sites = list_sites_with_filters(request.args.to_dict())[0]
    sites_data = [site.to_dict() for site in sites]

    return jsonify(sites_data), 200
