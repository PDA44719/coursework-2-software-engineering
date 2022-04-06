from my_app.auth.helper_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required
from datetime import timedelta
from my_app.auth.forms import SignupForm, LoginForm
from my_app.models import User
from my_app import db
from sqlalchemy.exc import IntegrityError


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['GET', 'POST'])
def signup():
    """Route used to register users that do not have an account."""
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():  # Form was completed & validated
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)

        # Try to add and commit the user. If not possible, redirect to the signup page and display an error
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(f'Unable to register {form.email.data}.', 'error')
            return redirect(url_for('auth.signup'))

        flash(f"Hello, {user.first_name} {user.last_name}. You are signed up.")  # Successful signup
        return redirect(url_for('auth.login'))

    return render_template('authorization_page.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route utilized to provide the login functionality."""
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate_on_submit():  # Form was completed & validated
        # Get the user corresponding to the email address and login
        user = User.query.filter_by(email=login_form.email.data).first()
        login_user(user, remember=login_form.remember.data, duration=timedelta(minutes=1))

        # If the next url is not safe, abort
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('main.index'))
    return render_template('login.html', form=login_form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Route used to allow users to logout."""
    logout_user()
    return redirect(url_for('auth.login'))
