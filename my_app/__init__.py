from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app(config_class_name):
    """
    Initialise the Flask application.
    :rtype: Returns a configured Flask object
    """
    app = Flask(__name__)
    app.config.from_object(config_class_name)
    csrf.init_app(app)

    from my_app.auth.routes import auth_bp
    from my_app.main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        # Import Dash application
        from dash_app.dash import init_dashboard
        app = init_dashboard(app)
    return app
