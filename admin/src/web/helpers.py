from flask import current_app


def image_url(object_name: str) -> str:
    """Genera la URL completa para acceder a una imagen almacenada en Minio.

    Args:
        object_name (str): Nombre del objeto en Minio.

    Returns:
        str: URL completa de la imagen.
    """
    protocol = "https" if current_app.config.get("MINIO_SECURE") else "http"

    return f"{protocol}://{current_app.config.get("MINIO_SERVER")}/{current_app.config.get("MINIO_BUCKET")}/{object_name}"
