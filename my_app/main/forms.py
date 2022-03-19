from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app import photos
from my_app.models import Profile


class ProfileForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    photo = FileField(label='Profile Picture', validators=[FileAllowed(photos, 'Images only!')])

    def validate_username(self, username):
        profile = Profile.query.filter_by(username=username.data).first()
        if profile is not None:
            raise ValidationError('An account is already registered with that username')
