from flask import Blueprint, jsonify
from core.models.tags import get_all_tags

tags_api_bp = Blueprint("tags_api", __name__, url_prefix="/api/tags")

@tags_api_bp.get("")
def get_all_tags_public():
    """
    Endpoint para obtener todos los tags.
    """
    try:
        tags = get_all_tags()
        tags_data = [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in tags]
        return jsonify({
            "results": tags_data,
            "total": len(tags_data)
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred.",
                "details": str(e)
            }
        }), 500

