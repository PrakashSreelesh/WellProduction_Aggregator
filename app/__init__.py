from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from .routes import initialize_routes
        initialize_routes(app)

    return app
