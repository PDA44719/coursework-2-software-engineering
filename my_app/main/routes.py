from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required
from my_app.messaging.routes import check_if_unread


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home route, which provides information to the user about the functionality of the app."""
    if not current_user.is_anonymous:  # If the user has logged in
        name = current_user.first_name
        return render_template('main_page.html', unread_messages=check_if_unread(), user_name=name)
    else:
        return render_template('main_page.html')


@main_bp.route('/dash_app/')
@login_required
def dash_app():
    """Route used to redirect to the dash app."""
    return redirect('/dash_app/')
