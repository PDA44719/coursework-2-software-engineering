from flask import Blueprint, render_template, flash, redirect, url_for, request
from sqlalchemy.exc import IntegrityError

from my_app import db
from my_app.auth.forms import SignupForm, LoginForm
from my_app.models import User

auth_bp = Blueprint('auth', __name__)


'''@auth_bp.route('/')
def index():
    return render_template('authorization_page.html', )'''


@auth_bp.route('/auth/', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Hello, {user.first_name} {user.last_name}. You are signed up.")
        except IntegrityError:
            db.session.rollback()
            flash(f'Unable to register {form.email.data}.', 'error')
            return redirect(url_for('auth.signup'))
        return redirect(url_for('main.index'))
    return render_template('authorization_page.html', form=form)
