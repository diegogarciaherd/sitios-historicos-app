from core.models import feature_flags
from core.database import db
from core.models.sites import SitioHistorico, EstadoConservacion
from core.models.tags import Tag
from core.database import db
from geoalchemy2.elements import WKTElement
from sqlalchemy import text


def run():
    """Seeding sitios históricos y tags ..."""
    print("Seeding database...")

    # 🔹 Limpiar relaciones y tablas
    """Elimina todos los datos existentes en las tablas de sitios y tags"""
    db.session.execute(text("DELETE FROM sites_tags"))
    db.session.query(SitioHistorico).delete()
    db.session.query(Tag).delete()
    db.session.commit()

    # 🔹 Crear tags
    tag_names = [
        "Histórico",
        "Cultural",
        "Religioso",
        "Gobierno",
        "Museo",
        "Monumento",
        "Natural",
        "Geológico",
        "Turismo",
    ]
    tags_objs = []
    for name in tag_names:
        tag = Tag(name=name)
        db.session.add(tag)
        tags_objs.append(tag)

    db.session.commit()  # commit para asignar IDs a los tags

    # 🔹 Función helper para coordenadas
    def make_point(lat, lon):
        """Crea un punto WKT a partir de latitud y longitud"""
        return WKTElement(f"POINT({lon} {lat})", srid=4326)

    # 🔹 Datos de sitios (todos en Buenos Aires)
    """Lista de diccionarios con datos de sitios históricos"""
    sitios_data = [
        {
            "nombre": "Catedral de La Plata",
            "ciudad": "La Plata",
            "descripcionBreve": "Imponente catedral neogótica.",
            "añoInauguracion": 1932,
            "categoria": "Religioso",
            "lat": -34.9214,
            "lng": -57.9544,
            "tags": ["Histórico", "Religioso"],
            "estado": EstadoConservacion.REGULAR,
            "cantVisitas": 100,
            "puntuacionTotal": 400,
            "cantidadResenas": 100,
        },
        {
            "nombre": "Café Tortoni",
            "ciudad": "Buenos Aires",
            "descripcionBreve": "Café histórico más antiguo.",
            "añoInauguracion": 1858,
            "categoria": "Cultural",
            "lat": -34.6083,
            "lng": -58.3700,
            "tags": ["Cultural", "Histórico"],
            "cantVisitas": 95,
            "puntuacionTotal": 450,
            "cantidadResenas": 100,
        },
        {
            "nombre": "Museo Nacional de Bellas Artes",
            "ciudad": "La Plata",
            "descripcionBreve": "Museo de arte argentino.",
            "añoInauguracion": 1895,
            "categoria": "Cultural",
            "lat": -34.5873,
            "lng": -58.3975,
            "tags": ["Museo", "Cultural"],
            "cantVisitas": 90,
            "puntuacionTotal": 420,
            "cantidadResenas": 100,
        },
        {
            "nombre": "Monumento a la Bandera",
            "ciudad": "Rosario",
            "descripcionBreve": "Hito histórico de la ciudad.",
            "añoInauguracion": 1957,
            "categoria": "Monumento",
            "lat": -34.6080,
            "lng": -58.3700,
            "tags": ["Monumento", "Histórico"],
            "cantVisitas": 85,
        },
        {
            "nombre": "Obelisco",
            "ciudad": "Buenos Aires",
            "descripcionBreve": "Símbolo de Buenos Aires.",
            "añoInauguracion": 1936,
            "categoria": "Monumento",
            "lat": -34.6037,
            "lng": -58.3816,
            "tags": ["Monumento", "Histórico"],
            "cantVisitas": 80,
        },
        {
            "nombre": "Jardín Japonés",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1967,
            "categoria": "Cultural",
            "descripcionBreve": "Parque temático japonés.",
            "lat": -34.5590,
            "lng": -58.4290,
            "tags": ["Cultural"],
            "cantVisitas": 75,
        },
        {
            "nombre": "Palacio Barolo",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1923,
            "categoria": "Histórico",
            "descripcionBreve": "Edificio histórico y arquitectónico.",
            "lat": -34.6080,
            "lng": -58.3810,
            "provincia": "Chubut",
            "tags": ["Histórico"],
            "cantVisitas": 70,
        },
        {
            "nombre": "Iglesia San Ignacio",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1722,
            "categoria": "Religioso",
            "descripcionBreve": "Antigua iglesia de Buenos Aires.",
            "lat": -34.6085,
            "lng": -58.3775,
            "tags": ["Religioso", "Histórico"],
            "cantVisitas": 65,
        },
        {
            "nombre": "Museo Evita",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 2002,
            "categoria": "Cultural",
            "descripcionBreve": "Museo dedicado a Eva Perón.",
            "lat": -34.6000,
            "lng": -58.4200,
            "tags": ["Museo", "Cultural"],
            "cantVisitas": 60,
        },
        {
            "nombre": "Palacio Legislativo",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1931,
            "categoria": "Gobierno",
            "descripcionBreve": "Sede de la Legislatura porteña.",
            "lat": -34.6117,
            "lng": -58.3844,
            "tags": ["Gobierno", "Histórico"],
            "cantVisitas": 55,
        },
        {
            "nombre": "Plaza de Mayo",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1884,
            "categoria": "Gobierno",
            "descripcionBreve": "Plaza histórica y centro político.",
            "lat": -34.6086,
            "lng": -58.3702,
            "tags": ["Histórico", "Gobierno"],
            "cantVisitas": 50,
        },
        {
            "nombre": "Cementerio Recoleta",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1822,
            "categoria": "Histórico",
            "descripcionBreve": "Lugar de descanso de grandes personalidades.",
            "lat": -34.5880,
            "lng": -58.3950,
            "tags": ["Histórico", "Cultural"],
            "cantVisitas": 45,
        },
        {
            "nombre": "Avenida Corrientes",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1930,
            "categoria": "Cultural",
            "descripcionBreve": "Avenida cultural y de teatros.",
            "lat": -34.6100,
            "lng": -58.3800,
            "tags": ["Cultural"],
            "cantVisitas": 40,
        },
        {
            "nombre": "Casa Rosada",
            "descripcionBreve": "Sede del Poder Ejecutivo Nacional",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1898,
            "categoria": "Gobierno",
            "provincia": "Buenos Aires",
            "estado": EstadoConservacion.BUENO,
            "lat": -34.6083,
            "lng": -58.3700,
            "tags": ["Gobierno", "Histórico"],
            "cantVisitas": 35,
        },
        {
            "nombre": "Catedral de Salta",
            "descripcionBreve": "Catedral de la ciudad de Salta",
            "ciudad": "Salta",
            "provincia": "Salta",
            "añoInauguracion": 1850,
            "categoria": "Religioso",
            "estado": EstadoConservacion.BUENO,
            "lat": -24.7821,
            "lng": -65.4232,
            "tags": ["Histórico", "Religioso"],
            "cantVisitas": 30,
        },
        {
            "nombre": "Parque General San Martín",
            "descripcionBreve": "Un hermoso parque en la ciudad de Mendoza",
            "ciudad": "Mendoza",
            "añoInauguracion": 1906,
            "categoria": "Natural",
            "provincia": "Mendoza",
            "estado": EstadoConservacion.REGULAR,
            "lat": -32.8908,
            "lng": -68.8272,
            "tags": ["Cultural"],
            "cantVisitas": 25,
        },
        {
            "nombre": "Casa Histórica de la Independencia",
            "descripcionBreve": "Lugar donde se declaró la independencia de Argentina",
            "ciudad": "San Miguel de Tucumán",
            "provincia": "Tucumán",
            "añoInauguracion": 1816,
            "categoria": "Histórico",
            "estado": EstadoConservacion.MALO,
            "lat": -26.8083,
            "lng": -65.2176,
            "tags": ["Histórico"],
            "cantVisitas": 20,
        },
        {
            "nombre": "Teatro Colón",
            "descripcionBreve": "Uno de los teatros de ópera más importantes del mundo",
            "ciudad": "Buenos Aires",
            "añoInauguracion": 1908,
            "categoria": "Cultural",
            "provincia": "Buenos Aires",
            "estado": EstadoConservacion.BUENO,
            "lat": -34.6014,
            "lng": -58.3836,
            "tags": ["Cultural", "Histórico"],
            "cantVisitas": 15,
        },
        {
            "nombre": "Ruinas de San Ignacio Miní",
            "descripcionBreve": "Antigua misión jesuítica en Misiones",
            "ciudad": "San Ignacio",
            "añoInauguracion": 1733,
            "categoria": "Histórico",
            "provincia": "Misiones",
            "estado": EstadoConservacion.REGULAR,
            "lat": -27.1833,
            "lng": -55.3333,
            "tags": ["Histórico"],
            "cantVisitas": 10,
        },
        {
            "nombre": "Cerro de los Siete Colores",
            "descripcionBreve": "Formación geológica única en Purmamarca",
            "ciudad": "Purmamarca",
            "añoInauguracion": 2000,
            "categoria": "Natural",
            "provincia": "Jujuy",
            "estado": EstadoConservacion.BUENO,
            "lat": -23.9875,
            "lng": -65.2625,
            "tags": ["Natural", "Geológico", "Turismo"],
            "cantVisitas": 9,
        },
        {
            "nombre": "Estancia Jesuítica de Alta Gracia",
            "descripcionBreve": "Patrimonio de la Humanidad en Córdoba",
            "ciudad": "Alta Gracia",
            "provincia": "Córdoba",
            "añoInauguracion": 1643,
            "categoria": "Histórico",
            "estado": EstadoConservacion.REGULAR,
            "lat": -31.6375,
            "lng": -64.4175,
            "tags": ["Histórico", "Cultural", "Religioso"],
            "cantVisitas": 8,
        },
        {
            "nombre": "Quebrada de Humahuaca",
            "descripcionBreve": "Valle montañoso en Jujuy",
            "ciudad": "Humahuaca",
            "provincia": "Jujuy",
            "añoInauguracion": 2003,
            "categoria": "Natural",
            "estado": EstadoConservacion.BUENO,
            "lat": -23.2061,
            "lng": -65.3472,
            "tags": ["Natural", "Cultural", "Turismo"],
            "cantVisitas": 7,
        },
        {
            "nombre": "Salto Alegre",
            "descripcionBreve": "Impresionante cascada en la provincia de Misiones",
            "ciudad": "Aristóbulo del Valle",
            "añoInauguracion": 1990,
            "categoria": "Natural",
            "provincia": "Misiones",
            "estado": EstadoConservacion.BUENO,
            "lat": -26.5833,
            "lng": -54.8667,
            "tags": ["Natural", "Turismo"],
            "cantVisitas": 6,
        },
    ]

    # 🔹 Crear sitios y asociar tags
    for s in sitios_data:
        """Crear sitio histórico y asociar tags"""
        sitio = SitioHistorico(
            nombre=s["nombre"],
            descripcionBreve=s["descripcionBreve"],
            ciudad=s["ciudad"] if "ciudad" in s else "Buenos Aires",
            provincia=s["provincia"] if "provincia" in s else "Buenos Aires",
            estado=s["estado"] if "estado" in s else EstadoConservacion.BUENO,
            localizacion=make_point(s["lat"], s["lng"]),
            añoInauguracion=s["añoInauguracion"],
            categoria=s["categoria"],
            cantVisitas=s["cantVisitas"] if "cantVisitas" in s else 0,
            puntuacionTotal=s["puntuacionTotal"] if "puntuacionTotal" in s else 0,
            cantidadResenas=s["cantidadResenas"] if "cantidadResenas" in s else 0,
        )
        sitio.tags = [t for t in tags_objs if t.name in s["tags"]]

        db.session.add(sitio)

    print(f"Seed completed: {len(sitios_data)} {len(tags_objs)} ")

    # Feature
    """Crea flags de características predeterminadas"""
    feature_flags.create_feature_flag(
        user_id=1,
        name="Sistema administrativo",
        activated=False,
        description="Deshabilita el sistema administrativo para los usuarios.",
        message="El sistema administrativo está en mantenimiento. Por favor, vuelva más tarde.",
    )
    feature_flags.create_feature_flag(
        user_id=1,
        name="Sitio público",
        activated=False,
        description="Deshabilita el acceso al sitio público.",
    )
    feature_flags.create_feature_flag(
        user_id=1,
        name="Reseñas",
        activated=False,
        description="Deshabilita el acceso a la creación de reseñas.",
    )

    db.session.commit()
