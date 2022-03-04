from flask import Blueprint, render_template
from my_app.auth.forms import SignupForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


'''@auth_bp.route('/')
def index():
    return render_template('authorization_page.html', )'''


@auth_bp.route('/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.first_name.data
        return f"Hello, {name}. You are signed up."
    print(form)
    return render_template('authorization_page.html', form=form)
