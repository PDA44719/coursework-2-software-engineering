from flask import flash, redirect, url_for, request
from urllib.parse import urlparse, urljoin
from my_app import login_manager
from my_app.models import User


@login_manager.user_loader
def load_user(user_id):
    """ Takes a user ID and returns a user object or None if the user does not exist."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))


def is_safe_url(target):
    """Determine if the target url is safe"""
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc
