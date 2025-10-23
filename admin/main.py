from src.web import create_app
'''Punto de entrada para ejecutar la aplicación Flask'''
if __name__ == '__main__':
    app = create_app()
    app.run()