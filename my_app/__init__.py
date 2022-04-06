from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required


csrf = CSRFProtect()
csrf._exempt_views.add('dash.dash.dispatch')  # Exclude dash from CSRFProtect
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class_name):
    """
    Initialise the Flask application.

    Arguments
    ---------
    config_class_name : my_app.config.py
        The app configuration desired by the user.

    Returns
    -------
    flask.app.Flask
        Configured Flask object.

    """
    app = Flask(__name__)
    app.config.from_object(config_class_name)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        # Import Dash application
        from dash_app.dash import init_dashboard
        d_app = init_dashboard(app)
        _protect_dash_views(d_app)

        from my_app.models import User
        db.create_all()

    from my_app.auth.routes import auth_bp
    from my_app.main.routes import main_bp
    from my_app.messaging.routes import messaging_bp
    from my_app.forum.routes import forum_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(forum_bp)

    return app


def _protect_dash_views(dash_app):
    """Protect the dash app from being viewed without being logged in."""
    for view_func in dash_app.server.view_functions:
        if view_func.startswith(dash_app.config.routes_pathname_prefix):
            dash_app.server.view_functions[view_func] = login_required(dash_app.server.view_functions[view_func])
