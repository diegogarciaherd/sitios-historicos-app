from core.models import sites, feature_flags, feature_flags_history
from core.database import db
from core.models.sites import SitioHistorico, EstadoConservacion
from core.models import tags
from core.models.tags import Tag
from core.database import db
from geoalchemy2.elements import WKTElement
from core.models import user, userrole
from sqlalchemy import text
from datetime import datetime

def run():
    print("Seeding database...")

    
    # 🔹 Limpiar relaciones y tablas
    db.session.execute(text('DELETE FROM sites_tags'))
    db.session.query(SitioHistorico).delete()
    db.session.query(Tag).delete()
    db.session.commit()

    # 🔹 Crear tags
    tag_names = ["Histórico", "Cultural", "Religioso", "Gobierno", "Museo", "Monumento"]
    tags_objs = []
    for name in tag_names:
        tag = Tag(name=name)
        db.session.add(tag)
        tags_objs.append(tag)

    db.session.commit()  # commit para asignar IDs a los tags

    # 🔹 Función helper para coordenadas
    def make_point(lat, lon):
        return WKTElement(f'POINT({lon} {lat})', srid=4326)

    # 🔹 Datos de sitios (todos en Buenos Aires)
    sitios_data = [
        {"nombre": "Catedral de La Plata", "descripcionBreve": "Imponente catedral neogótica.", "lat": -34.9214, "lng": -57.9544, "tags": ["Histórico", "Religioso"]},
        {"nombre": "Teatro Colón", "descripcionBreve": "Famoso teatro de ópera.", "lat": -34.6014, "lng": -58.3836, "tags": ["Cultural", "Histórico"]},
        {"nombre": "Casa Rosada", "descripcionBreve": "Sede del Poder Ejecutivo.", "lat": -34.6083, "lng": -58.3700, "tags": ["Gobierno", "Histórico"]},
        {"nombre": "Café Tortoni", "descripcionBreve": "Café histórico más antiguo.", "lat": -34.6083, "lng": -58.3700, "tags": ["Cultural", "Histórico"]},
        {"nombre": "Museo Nacional de Bellas Artes", "descripcionBreve": "Museo de arte argentino.", "lat": -34.5873, "lng": -58.3975, "tags": ["Museo", "Cultural"]},
        {"nombre": "Monumento a la Bandera", "descripcionBreve": "Hito histórico de la ciudad.", "lat": -34.6080, "lng": -58.3700, "tags": ["Monumento", "Histórico"]},
        {"nombre": "Obelisco", "descripcionBreve": "Símbolo de Buenos Aires.", "lat": -34.6037, "lng": -58.3816, "tags": ["Monumento", "Histórico"]},
        {"nombre": "Jardín Japonés", "descripcionBreve": "Parque temático japonés.", "lat": -34.5590, "lng": -58.4290, "tags": ["Cultural"]},
        {"nombre": "Palacio Barolo", "descripcionBreve": "Edificio histórico y arquitectónico.", "lat": -34.6080, "lng": -58.3810, "tags": ["Histórico"]},
        {"nombre": "Iglesia San Ignacio", "descripcionBreve": "Antigua iglesia de Buenos Aires.", "lat": -34.6085, "lng": -58.3775, "tags": ["Religioso", "Histórico"]},
        {"nombre": "Museo Evita", "descripcionBreve": "Museo dedicado a Eva Perón.", "lat": -34.6000, "lng": -58.4200, "tags": ["Museo", "Cultural"]},
        {"nombre": "Palacio Legislativo", "descripcionBreve": "Sede de la Legislatura porteña.", "lat": -34.6117, "lng": -58.3844, "tags": ["Gobierno", "Histórico"]},
        {"nombre": "Plaza de Mayo", "descripcionBreve": "Plaza histórica y centro político.", "lat": -34.6086, "lng": -58.3702, "tags": ["Histórico", "Gobierno"]},
        {"nombre": "Cementerio Recoleta", "descripcionBreve": "Lugar de descanso de grandes personalidades.", "lat": -34.5880, "lng": -58.3950, "tags": ["Histórico", "Cultural"]},
        {"nombre": "Avenida Corrientes", "descripcionBreve": "Avenida cultural y de teatros.", "lat": -34.6100, "lng": -58.3800, "tags": ["Cultural"]}
    ]

    # 🔹 Crear sitios y asociar tags
    for s in sitios_data:
        sitio = SitioHistorico(
            nombre=s["nombre"],
            descripcionBreve=s["descripcionBreve"],
            ciudad="Buenos Aires",
            provincia="Buenos Aires",
            estado=EstadoConservacion.BUENO,
            localizacion=make_point(s["lat"], s["lng"])
        )
        sitio.tags = [t for t in tags_objs if t.name in s["tags"]]

        db.session.add(sitio)

    print(f"Seed completed: {len(sitios_data)} {len(tags_objs)} ")

    # Feature Flags
    feature_flags.create_feature_flag(user_id=1, name="Sistema administrativo", activated=False, description="Deshabilita el sistema administrativo para los usuarios.", message="El sistema administrativo está en mantenimiento. Por favor, vuelva más tarde.")
    feature_flags.create_feature_flag(user_id=1, name="Sitio público", activated=False, description="Deshabilita el acceso al sitio público.")
    feature_flags.create_feature_flag(user_id=1, name="Reseñas", activated=False, description="Deshabilita el acceso a la creación de reseñas.")

    db.session.commit()