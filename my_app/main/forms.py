from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app import photos
from my_app.models import Profile
from flask_login import current_user


class ProfileForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    photo = FileField(label='Profile Picture', validators=[FileAllowed(photos, 'Images only!')])

    def validate_username(self, username):
        profile = Profile.query.filter_by(username=username.data).first()
        # If that username is already being used by someone who is not the current user
        if profile is not None and profile.user != current_user:
            raise ValidationError('An account is already registered with that username')


class ProposalForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    plot = TextAreaField(label='Plot', validators=[DataRequired()])
