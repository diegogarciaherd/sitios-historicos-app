from src.core.models import sites
from src.core.database import db
from geoalchemy2.elements import WKTElement

def run(): 

    site1 = sites.create_sites(
        nombre="Catedral de La Plata",
        descripcionBreve="Imponente catedral neogótica en La Plata.",
        descripcionCompleta="La Catedral de La Plata es una de las iglesias más grandes de Argentina y un ejemplo destacado de la arquitectura neogótica. Su construcción comenzó en 1884 y se completó en 1932. La catedral cuenta con impresionantes vitrales, torres altas y una nave central majestuosa.",
        ciudad="La Plata",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1932,
        categoria="Histórico",
        localizacion=WKTElement('POINT(-34.9214 -57.9544)', srid=4326)
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
        localizacion=WKTElement('POINT(-34.6015 -58.3816)', srid=4326)
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
        localizacion=WKTElement('POINT(-34.6083 -58.3712)', srid=4326)
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
        localizacion=WKTElement('POINT(-26.8083 -65.2175)', srid=4326)
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
        localizacion=WKTElement('POINT(-34.6083 -58.3750)', srid=4326)
    )

    site6 = sites.create_sites(
        nombre="Museo Histórico Nacional",
        descripcionBreve="Museo que preserva la historia argentina.",
        descripcionCompleta="El Museo Histórico Nacional es uno de los museos más importantes de Argentina, dedicado a preservar y exhibir objetos relacionados con la historia del país. Inaugurado en 1889, cuenta con una vasta colección que incluye documentos, pinturas, armas y objetos personales de próceres argentinos.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1889,
        categoria="Museo",
        localizacion=WKTElement('POINT(-34.6083 -58.3750)', srid=4326)
    )

    site7 = sites.create_sites(
        nombre="Basílica de Luján",
        descripcionBreve="Importante santuario mariano de Argentina.",
        descripcionCompleta="La Basílica de Nuestra Señora de Luján es el santuario mariano más importante de Argentina. Su construcción comenzó en 1890 y se completó en 1935. La basílica alberga la imagen de la Virgen de Luján, patrona de Argentina, y recibe millones de peregrinos cada año.",
        ciudad="Luján",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1935,
        categoria="Religioso",
        localizacion=WKTElement('POINT(-34.5667 -59.1167)',srid=4326)
    )

    site8 = sites.create_sites(
        nombre="Palacio San José",
        descripcionBreve="Residencia del General Urquiza en Entre Ríos.",
        descripcionCompleta="El Palacio San José fue la residencia del General Justo José de Urquiza, primer presidente constitucional de Argentina. Construido entre 1848 y 1857, este palacio de estilo italiano es un ejemplo único de la arquitectura del siglo XIX en el interior del país.",
        ciudad="Concepción del Uruguay",
        provincia="Entre Ríos",
        estado=sites.EstadoConservacion.REGULAR,
        añoInauguracion=1857,
        categoria="Histórico",
        localizacion=WKTElement('POINT(-32.4833 -58.2333)', srid=4326)
    )

    site9 = sites.create_sites(
        nombre="Casa Natal de Sarmiento",
        descripcionBreve="Casa donde nació Domingo Faustino Sarmiento.",
        descripcionCompleta="La Casa Natal de Sarmiento es el lugar donde nació Domingo Faustino Sarmiento, presidente de Argentina entre 1868 y 1874. Esta casa museo preserva objetos personales y documentos del prócer, siendo un importante centro de estudio de la historia argentina del siglo XIX.",
        ciudad="San Juan",
        provincia="San Juan",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1811,
        categoria="Histórico",
        localizacion=WKTElement('POINT(-31.5375 -68.5364)', srid=4326)
    )

    site10 = sites.create_sites(
        nombre="Estancia Jesuítica de Alta Gracia",
        descripcionBreve="Complejo jesuítico declarado Patrimonio de la Humanidad.",
        descripcionCompleta="La Estancia Jesuítica de Alta Gracia forma parte del conjunto de estancias jesuíticas de Córdoba, declaradas Patrimonio de la Humanidad por la UNESCO. Construida en el siglo XVII, incluye la iglesia, la residencia, el obraje y la ranchería, siendo un ejemplo excepcional de la arquitectura colonial.",
        ciudad="Alta Gracia",
        provincia="Córdoba",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1643,
        categoria="Patrimonio UNESCO",
        localizacion=WKTElement('POINT(-31.6667 -64.4333)', srid=4326)
    )

    site11 = sites.create_sites(
        nombre="Casa de Gobierno de Córdoba",
        descripcionBreve="Sede del gobierno provincial de Córdoba.",
        descripcionCompleta="La Casa de Gobierno de Córdoba es un edificio histórico que data del siglo XIX. Su arquitectura de estilo neoclásico la convierte en uno de los edificios más representativos de la ciudad. Ha sido sede del gobierno provincial desde su construcción.",
        ciudad="Córdoba",
        provincia="Córdoba",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1890,
        categoria="Gobierno",
        localizacion=WKTElement('POINT(-31.4201 -64.1888)', srid=4326)
    )

    site12 = sites.create_sites(
        nombre="Monumento a la Bandera",
        descripcionBreve="Monumento nacional en Rosario.",
        descripcionCompleta="El Monumento a la Bandera es un complejo escultórico ubicado en Rosario, ciudad donde se izó por primera vez la bandera argentina. Inaugurado en 1957, el monumento incluye la Torre Central, el Propileo y la Galería de Honor de las Banderas de América.",
        ciudad="Rosario",
        provincia="Santa Fe",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1957,
        categoria="Monumento",
        localizacion=WKTElement('POINT(-32.9442 -60.6505)', srid=4326)
    )

    site13 = sites.create_sites(
        nombre="Casa de la Independencia",
        descripcionBreve="Museo histórico en San Miguel de Tucumán.",
        descripcionCompleta="La Casa de la Independencia es un museo histórico que preserva la casa donde se declaró la independencia de Argentina. El edificio original fue reconstruido y convertido en museo, exhibiendo objetos y documentos relacionados con el Congreso de Tucumán de 1816.",
        ciudad="San Miguel de Tucumán",
        provincia="Tucumán",
        estado=sites.EstadoConservacion.REGULAR,
        añoInauguracion=1941,
        categoria="Museo",
        localizacion=WKTElement('POINT(-26.8083 -65.2175)', srid=4326)
    )

    site14 = sites.create_sites(
        nombre="Catedral de Córdoba",
        descripcionBreve="Catedral más antigua de Argentina.",
        descripcionCompleta="La Catedral de Córdoba es la catedral más antigua de Argentina, construida entre 1577 y 1914. Su arquitectura combina estilos barroco y neoclásico, siendo un ejemplo excepcional de la arquitectura colonial española en América del Sur.",
        ciudad="Córdoba",
        provincia="Córdoba",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1914,
        categoria="Religioso",
        localizacion=WKTElement('POINT(-31.4201 -64.1888)', srid=4326)
    )

    site15 = sites.create_sites(
        nombre="Puerto Madero",
        descripcionBreve="Barrio moderno con arquitectura histórica renovada.",
        descripcionCompleta="Puerto Madero es un barrio de Buenos Aires que combina arquitectura histórica renovada con modernos rascacielos. Los antiguos depósitos portuarios fueron convertidos en oficinas, restaurantes y viviendas, creando un ejemplo único de renovación urbana en Argentina.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1990,
        categoria="Renovación Urbana",
        localizacion=WKTElement('POINT(-34.6103 -58.3636)', srid=4326)
    )

    site16 = sites.create_sites(
        nombre="Museo de la Memoria",
        descripcionBreve="Museo dedicado a la memoria de los desaparecidos.",
        descripcionCompleta="El Museo de la Memoria de Rosario es un espacio dedicado a preservar la memoria de las víctimas del terrorismo de estado durante la última dictadura militar. Inaugurado en 2010, el museo incluye exposiciones permanentes y temporales sobre derechos humanos.",
        ciudad="Rosario",
        provincia="Santa Fe",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=2010,
        categoria="Memoria",
        localizacion=WKTElement('POINT(-32.9442 -60.6505)', srid=4326)
    )

    site17 = sites.create_sites(
        nombre="Casa de la Cultura",
        descripcionBreve="Centro cultural en La Plata.",
        descripcionCompleta="La Casa de la Cultura de La Plata es un centro cultural ubicado en un edificio histórico de principios del siglo XX. Actualmente alberga exposiciones, conciertos y eventos culturales, siendo uno de los espacios culturales más importantes de la ciudad.",
        ciudad="La Plata",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.REGULAR,
        añoInauguracion=1920,
        categoria="Cultural",
        localizacion=WKTElement('POINT(-34.9214 -57.9544)', srid=4326)
    )

    site18 = sites.create_sites(
        nombre="Plaza de Mayo",
        descripcionBreve="Plaza histórica de Buenos Aires.",
        descripcionCompleta="La Plaza de Mayo es la plaza más importante de Buenos Aires y ha sido escenario de numerosos acontecimientos históricos. Rodeada por edificios históricos como la Casa Rosada y la Catedral Metropolitana, es el corazón político y social de la ciudad.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=1580,
        categoria="Plaza Histórica",
        localizacion=WKTElement('POINT(-34.6083 -58.3712)', srid=4326)
    )

    site19 = sites.create_sites(
        nombre="Casa de la Cultura de Salta",
        descripcionBreve="Centro cultural en edificio histórico de Salta.",
        descripcionCompleta="La Casa de la Cultura de Salta está ubicada en un edificio histórico del siglo XIX que combina arquitectura colonial y republicana. Actualmente funciona como centro cultural, albergando exposiciones, talleres y eventos que promueven la cultura local y regional.",
        ciudad="Salta",
        provincia="Salta",
        estado=sites.EstadoConservacion.MALO,
        añoInauguracion=1850,
        categoria="Cultural",
        localizacion=WKTElement('POINT(-24.7821 -65.4232)', srid=4326)
    )

    site20 = sites.create_sites(
        nombre="Museo Evita",
        descripcionBreve="Museo dedicado a Eva Perón.",
        descripcionCompleta="El Museo Evita está dedicado a la vida y obra de Eva Perón, una de las figuras más importantes de la historia argentina del siglo XX. El museo exhibe objetos personales, documentos, fotografías y vestidos de Evita, ofreciendo una perspectiva completa de su vida y legado.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        estado=sites.EstadoConservacion.BUENO,
        añoInauguracion=2002,
        categoria="Museo",
        localizacion=WKTElement('POINT(-34.6083 -58.3750)', srid=4326)
        )

    sites_created = [site1, site2, site3, site4, site5, site6, site7, site8, site9, site10, 
                    site11, site12, site13, site14, site15, site16, site17, site18, site19, site20]
    
    print(f"Created {len(sites_created)} sites:")
    for i, site in enumerate(sites_created, 1):
        print(f"{i}. {site.nombre} - {site.ciudad}, {site.provincia}")
