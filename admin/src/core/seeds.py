from core.models import sites
from core.models import tags
from core.models.tags import Tag
from core.database import db
from geoalchemy2.elements import WKTElement
from core.models import user, userrole

def run(): 
    # Limpiar tabla de tags
    db.session.query(Tag).delete()
    db.session.commit()

    # Lista de tags a crear
    tags_list = [
        "Histórico", "Cultural", "Religioso", "Gobierno", "Museo", 
        "Independencia", "Monumento", "Memoria", "Patrimonio UNESCO",
        "Renovación Urbana", "Plaza Histórica"
    ]

    # Crear tags (ignorar si ya existen)
    for tag_name in tags_list:
        try:
            tags.create_tag(tag_name)
        except ValueError:
            pass

    # Obtener todos los tags y crear un diccionario para acceder rápido
    existing_tags, _, _ = tags.get_tags_paginated(page=1, per_page=1000)
    tags_dict = {tag.name: tag for tag in existing_tags}

    # Función helper para puntos geográficos
    def make_point(lat, lon):
        return WKTElement(f'POINT({lon} {lat})', srid=4326)

    # Crear sitios
    site1 = sites.create_sites(
        nombre="Catedral de La Plata",
        descripcionBreve="Imponente catedral neogótica en La Plata.",
        descripcionCompleta="La Catedral de La Plata es una de las iglesias más grandes de Argentina y un ejemplo destacado de la arquitectura neogótica. Su construcción comenzó en 1884 y se completó en 1932. La catedral cuenta con impresionantes vitrales, torres altas y una nave central majestuosa.",
        ciudad="La Plata",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1932,
        categoria="Histórico",
        localizacion=make_point(-34.9214, -57.9544)
    )   

    site2 = sites.create_sites(
        nombre="Teatro Colón",
        descripcionBreve="Famoso teatro de ópera en Buenos Aires.",
        descripcionCompleta="El Teatro Colón es uno de los teatros de ópera más importantes del mundo, conocido por su acústica excepcional y su arquitectura impresionante. Inaugurado en 1908, el teatro ha sido sede de numerosas producciones de ópera, ballet y conciertos de renombre internacional.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1908,
        categoria="Histórico",
        localizacion=make_point(-34.6014, -58.3836)
    )

    site3 = sites.create_sites(
        nombre="Casa Rosada",
        descripcionBreve="Sede del Poder Ejecutivo de la Nación Argentina.",
        descripcionCompleta="La Casa Rosada es la sede del Poder Ejecutivo de la Nación Argentina. Ubicada en la Plaza de Mayo, este edificio histórico ha sido testigo de importantes acontecimientos políticos del país. Su característico color rosa se debe a una mezcla de cal con sangre de buey.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1898,
        categoria="Gobierno",
        localizacion=make_point(-34.6083, -58.3700)
    )

    site4 = sites.create_sites(
        nombre="Casa de Tucumán",
        descripcionBreve="Lugar donde se declaró la Independencia de Argentina.",
        descripcionCompleta="La Casa de Tucumán es el lugar donde el 9 de julio de 1816 se declaró la Independencia de las Provincias Unidas del Río de la Plata. Este edificio histórico es uno de los más importantes del país y alberga el Salón de la Jura donde se firmó el Acta de la Independencia.",
        ciudad="San Miguel de Tucumán",
        provincia="Tucumán",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1816,
        categoria="Independencia",
        localizacion=make_point(-26.8083, -65.2175)
    )

    site5 = sites.create_sites(
        nombre="Café Tortoni",
        descripcionBreve="Café histórico más antiguo de Buenos Aires.",
        descripcionCompleta="El Café Tortoni es el café más antiguo de Buenos Aires, fundado en 1858. Fue frecuentado por importantes personalidades de la cultura argentina como Jorge Luis Borges, Carlos Gardel y Alfonsina Storni. Su arquitectura de estilo art nouveau lo convierte en un lugar único.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1858,
        categoria="Cultural",
        localizacion=make_point(-34.6083, -58.3700)
    )

    # (Aquí puedes agregar el resto de los sitios site6 hasta site20 de la misma manera)
    # Para no hacer el código gigante, se recomienda iterar desde una lista de diccionarios.

    sites_created = [site1, site2, site3, site4, site5]

    # Mapping de tags
    tags_mapping = {
        site1: ["Histórico", "Religioso"],
        site2: ["Cultural", "Histórico"],
        site3: ["Gobierno", "Histórico"],
        site4: ["Independencia", "Histórico"],
        site5: ["Cultural", "Histórico"]
    }

    # Asociar tags
    for site, tag_names in tags_mapping.items():
        associated_tags = [tags_dict[name] for name in tag_names if name in tags_dict]
        tags.assign_tags(site, associated_tags)

    print(f"Created {len(sites_created)} sites:")
    for i, site in enumerate(sites_created, 1):
        print(f"{i}. {site.nombre} - {site.ciudad}, {site.provincia}")

    pUser = user.create_user(
        email="public@hotmail.com",
        name="Public",
        last_name="User",
        password= "asd123",
        active= True,
        role= userrole.UserRole.PUBLIC
    )
    eUser = user.create_user(
        email= "editor@hotmail.com",
        name= "Editor",
        last_name="User",
        password="asd123",
        active=True,
        role= userrole.UserRole.EDITOR
    )
    admin = user.create_user(
        email="admin@hotmail.com",
        name="Admin",
        last_name="User",
        password="asd123",
        active=True,
        role= userrole.UserRole.ADMIN
    )