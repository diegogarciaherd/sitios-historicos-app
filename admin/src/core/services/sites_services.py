import math
from core.database import db
from core.models.sites import SitioHistorico

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos usando Haversine.
    Devuelve la distancia en kilómetros.
    """
    R = 6371  # Radio de la Tierra en km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_sites_within_radius(lat, lng, radius_km):
    """
    Devuelve solo los sitios dentro del radio indicado.
    """
    lat = float(lat)
    lng = float(lng)
    radius_km = float(radius_km)

    all_sites = db.session.query(SitioHistorico).all()
    filtered = []

    for site in all_sites:
        if site.lat is None or site.lng is None:
            continue

        dist = haversine_distance(lat, lng, site.lat, site.lng)

        if dist <= radius_km:
            filtered.append(site)
        print("User:", lat, lng)

    return filtered