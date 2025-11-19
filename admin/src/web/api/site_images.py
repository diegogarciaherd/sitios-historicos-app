from core.models.site_images import get_image_cover_by_site, get_images_by_site
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from web.helpers import image_url


# Blueprint principal con prefijo único
site_images_api_bp = Blueprint("site_images_api", __name__, url_prefix="/api/site_images")

@site_images_api_bp.route("/<int:site_id>/cover", methods=["GET"])
def get_cover_image(site_id: int):
    """
    Devuelve los datos de un sitio histórico según su ID.

    Args:
        id (int): ID del sitio.

    Returns:
        JSON con el sitio o error 404 si no existe.
    """

    cover_image = get_image_cover_by_site(site_id)
    if cover_image:
        cover_image = image_url(cover_image.object_name)
        return jsonify(cover_image), 200

    return (
        jsonify(
            None
        ),
        200,
    )

@site_images_api_bp.route("/<int:site_id>", methods=["GET"])
def get_site_images(site_id: int):
    """
    Devuelve las imágenes asociadas a un sitio histórico según su ID.

    Args:
        site_id (int): ID del sitio.

    Returns:
        JSON con las imágenes del sitio o error 404 si no existe.
    """

    images = get_images_by_site(site_id)
    if images:
        for image in images:
            image.object_name = image_url(image.object_name)
        images_data = [image.to_dict() for image in images]
        return jsonify(images_data), 200

    return (
        jsonify(
            {
                "error": {
                    "code": "not_found",
                    "message": "No existen imágenes para el sitio con ese id.",
                }
            }
        ),
        404,
    )