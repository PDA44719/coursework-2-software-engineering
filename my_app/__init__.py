from flask import Flask


def create_app(config_class_name):
    """
    Initialise the Flask application.
    :rtype: Returns a configured Flask object
    """
    app = Flask(__name__)
    app.config.from_object(config_class_name)

    from my_app.auth import auth_bp
    from my_app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        # Import Dash application
        from dash_app.dash import init_dashboard
        app = init_dashboard(app)
    return app
