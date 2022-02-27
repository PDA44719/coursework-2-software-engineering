from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/')
def index():
    return "This is the authentication section of the web app"
