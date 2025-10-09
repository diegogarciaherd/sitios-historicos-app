def validate_site_data(data):
    errors = {}

    # Validar campos obligatorios
    required_fields = ['nombre', 'ciudad', 'provincia', 'categoria', 'estado']
    for field in required_fields:
        value = data.get(field, '').strip()
    if not value:
        errors[field] = f"El campo {field} es obligatorio"

    # Validar coordenadas 
    lat = data.get('lat', '').strip()
    lng = data.get('lng', '').strip()

    if not lat or not lng:
        errors['localizacion'] = "Se debe seleccionar una ubicación en el mapa"

    # Validar longitud mínima del nombre
    nombre = data.get("nombre", "").strip()
    if nombre and len(nombre) < 3:
        errors["nombre"] = "Debe tener al menos 3 caracteres"

    # Validar año
    año_str = data.get("añoInauguracion", "").strip()
    if año_str:  # Es opcional, pero si se ingresa debe ser válido
        try:
            año = int(año_str)
            if año < 1500 or año > 2025:
                errors["añoInauguracion"] = "El año debe estar entre 1500 y 2025"
        except (ValueError, TypeError):
            errors["añoInauguracion"] = "El año debe ser un número válido"

    # Validar coordenadas
    lat_str = data.get("lat", "").strip()
    lng_str = data.get("lng", "").strip()
    
    if lat_str:
        try:
            lat = float(lat_str)
            if lat < -90 or lat > 90:
                errors["lat"] = "Latitud fuera de rango (-90 a 90)"
        except (ValueError, TypeError):
            errors["lat"] = "La latitud debe ser un número válido"

    if lng_str:
        try:
            lng = float(lng_str)
            if lng < -180 or lng > 180:
                errors["lng"] = "Longitud fuera de rango (-180 a 180)"
        except (ValueError, TypeError):
            errors["lng"] = "La longitud debe ser un número válido"

    return errors