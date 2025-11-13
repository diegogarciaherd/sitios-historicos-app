# admin/src/web/controllers/validators/review_validator.py

def validate_review_data(data: dict) -> list[str]:
    """
    Valida los datos enviados para crear una reseña pública.

    Reglas:
      - rating: obligatorio, entero entre 1 y 5.
      - title: obligatorio, máx 120 caracteres.
      - body: obligatorio.
    """
    errors: list[str] = []

    rating = data.get("rating")
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()

    # Rating
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            errors.append("La puntuación debe estar entre 1 y 5.")
    except (TypeError, ValueError):
        errors.append("La puntuación es obligatoria y debe ser un número entre 1 y 5.")

    # Título
    if not title:
        errors.append("El título es obligatorio.")
    elif len(title) > 120:
        errors.append("El título no puede superar los 120 caracteres.")

    # Comentario
    if not body:
        errors.append("El comentario es obligatorio.")

    return errors
