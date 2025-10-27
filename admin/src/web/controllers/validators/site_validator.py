
def validate_site_data(data):
    '''Valida los datos del sitio histórico proporcionados en el formulario.
    Devuelve una lista de mensajes de error si hay problemas, o una lista vacía si
    todo es correcto.'''
    errors = []

    # Validar nombre 
    if not data.get("nombre"):
        errors.append("El nombre del sitio es obligatorio.")
    elif len(data["nombre"]) > 100:
        errors.append("El nombre del sitio no puede exceder los 100 caracteres.")
    elif len(data["nombre"].strip()) == 0:
        errors.append("El nombre del sitio no puede estar vacío o contener solo espacios.")
    elif len(data["nombre"].strip()) < 3:
        errors.append("El nombre del sitio debe tener al menos 3 caracteres.")
    


    # Validar la descripción breve
    if not data.get("descripcionBreve"):
        errors.append("La descripción breve es obligatoria.")
    elif len(data["descripcionBreve"]) > 255:
        errors.append("La descripción breve no puede exceder los 255 caracteres.")
    elif len(data["descripcionBreve"].strip()) == 0:
        errors.append("La descripción breve no puede estar vacía o contener solo espacios.")

    # Validar estado de conservación
    
    if not data.get("estado"):
        errors.append("El estado de conservación es obligatorio.")
    elif data["estado"] not in ["EXCELENTE", "BUENO", "REGULAR", "MALO"]:
        errors.append("El estado de conservación no es válido.")
    
    # Validar coordenadas

    if not data.get("lat") or not data.get("lng"):
        errors.append("Las coordenadas (latitud y longitud) son obligatorias.")
    
    # Validar categoria
    if not data.get("categoria"):
        errors.append("La categoría es obligatoria.")
    elif len(data["categoria"].strip()) == 0:
        errors.append("La categoría no puede estar vacía o contener solo espacios.")
    elif len(data["categoria"]) > 50:
        errors.append("La categoría no puede exceder los 50 caracteres.")

    # Validar año de inauguración
    if not data.get("añoInauguracion"):
        errors.append("El año de inauguración es obligatorio.")
    else:
        try:
            año = int(data["añoInauguracion"])
            if año < 1000 or año > 2030:
                errors.append("El año de inauguración debe estar entre 1000 y 2100.")
        except ValueError:
            errors.append("El año de inauguración debe ser un número entero válido.")

    return errors
        
    
    