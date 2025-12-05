# src/core/validation/reviews.py
from typing import Dict, Any

MIN_TEXT_LEN = 20
MAX_TEXT_LEN = 1000

def validate_review_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Valida los datos de una reseña.
    Devuelve un dict field -> mensaje_de_error.
    Si no hay errores, devuelve {}.
    """
    errors: Dict[str, str] = {}

    # puntuación obligatoria y entre 1 y 5
    rating = data.get("rating")
    if rating is None:
        errors["rating"] = "La puntuación es obligatoria."
    else:
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            errors["rating"] = "La puntuación debe ser un número entero."
        else:
            if rating < 1 or rating > 5:
                errors["rating"] = "La puntuación debe estar entre 1 y 5."

    # texto obligatorio, largo 20–1000
    text = (data.get("text") or "").strip()
    if not text:
        errors["text"] = "El texto de la reseña es obligatorio."
    else:
        length = len(text)
        if length < MIN_TEXT_LEN:
            errors["text"] = (
                f"La reseña debe tener al menos {MIN_TEXT_LEN} caracteres."
            )
        elif length > MAX_TEXT_LEN:
            errors["text"] = (
                f"La reseña no puede superar los {MAX_TEXT_LEN} caracteres."
            )

    return errors
