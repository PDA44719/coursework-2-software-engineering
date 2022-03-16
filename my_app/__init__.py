from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class_name):
    """
    Initialise the Flask application.
    :rtype: Returns a configured Flask object
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
        app = init_dashboard(app)

        from my_app.models import User
        db.create_all()

    from my_app.auth.routes import auth_bp
    from my_app.main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
