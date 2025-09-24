from src.core import models
from src.core.database import db
from src.core.models.sitios import Categoria

def get_or_create_categoria(nombre: str) -> Categoria:
    categoria = db.session.query(Categoria).filter_by(nombre=nombre).first()
    if not categoria:
        categoria = Categoria(nombre=nombre)
        db.session.add(categoria)
        db.session.commit()
    return categoria


def run(): 
    categoria = get_or_create_categoria("Histórico")

    site1 = models.create_sites(
        nombre="Catedral de La Plata",
        descripcionBreve="Imponente catedral neogótica en La Plata.",
        descripcionCompleta="La Catedral de La Plata es una de las iglesias más grandes de Argentina y un ejemplo destacado de la arquitectura neogótica. Su construcción comenzó en 1884 y se completó en 1932. La catedral cuenta con impresionantes vitrales, torres altas y una nave central majestuosa.",
        ciudad="La Plata",
        provincia="Buenos Aires",
        latitud=-34.9214,
        longitud=-57.9544,
        estado=models.EstadoConservacion.BUENO,
        añoInauguracion=1932,
        categoria=categoria,
    )

    site2 = models.create_sites(
        nombre="Teatro Colón",
        descripcionBreve="Famoso teatro de ópera en Buenos Aires.",
        descripcionCompleta="El Teatro Colón es uno de los teatros de ópera más importantes del mundo, conocido por su acústica excepcional y su arquitectura impresionante. Inaugurado en 1908, el teatro ha sido sede de numerosas producciones de ópera, ballet y conciertos de renombre internacional.",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        latitud=-34.6015,
        longitud=-58.3816,
        estado=models.EstadoConservacion.BUENO,
        añoInauguracion=1908,
        categoria=categoria,
    )

    print(f"Created sites:\n {site1}\n {site2}")
