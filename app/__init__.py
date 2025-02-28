from flask import Flask
from app.routes import main
import os

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.abspath('templates'),
        static_folder=os.path.abspath('static')
    )

    # Enregistrer les routes
    app.register_blueprint(main)

    return app
