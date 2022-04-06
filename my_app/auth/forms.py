from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app.models import User


class SignupForm(FlaskForm):
    """Form that gets information about a new user which is to be signed up."""
    first_name = StringField(label='First name', validators=[DataRequired()])
    last_name = StringField(label='Last name', validators=[DataRequired()])
    email = EmailField(label='Email address', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    password_repeat = PasswordField(label='Repeat Password',
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def validate_email(self, email):
        """Only allow the user to register with an email address that was not used by a previous user."""
        users = User.query.filter_by(email=email.data).first()
        if users is not None:
            raise ValidationError('An account is already registered for that email address')


class LoginForm(FlaskForm):
    """Form to get the login information of a user."""
    email = EmailField(label='Email address', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember me')

    def validate_email(self, email):
        """Only emails stored in the User database are valid."""
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('That email address is not registered')

    def validate_password(self, password):
        """Only validate the login process if the input password is the correct one."""
        user = User.query.filter_by(email=self.email.data).first()
        # Raise a ValidationError if the user exists and the password is incorrect.
        # If the user does not exist, the error is not necessary
        if user is not None and not user.check_password(password.data):
            raise ValidationError('Incorrect password.')
