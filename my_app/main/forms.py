from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app import photos
from my_app.models import Profile
from flask_login import current_user

movie_genres = ['Science Fiction', 'Adventure', 'Action', 'Fantasy', 'Animation', 'Family', 'Music', 'Comedy', 'War',
                'Thriller', 'Crime', 'Romance', 'History', 'Horror', 'Mystery', 'Drama', 'Western', 'Documentary']

class ProfileForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    photo = FileField(label='Profile Picture', validators=[FileAllowed(photos, 'Images only!')])

    def validate_username(self, username):
        profile = Profile.query.filter_by(username=username.data).first()
        # If that username is already being used by someone who is not the current user
        if profile is not None and profile.user != current_user:
            raise ValidationError('An account is already registered with that username')


class CharacterForm(Form):
    character_name = StringField(label='Character Name', validators=[DataRequired()])
    character_description = TextAreaField(label='Character Description', validators=[DataRequired()])


class GenreForm(Form):
    genre = SelectField('Genre', choices=[(genre, genre) for genre in movie_genres])


class ProposalForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    plot = TextAreaField(label='Plot', validators=[DataRequired()])
    characters = FieldList(FormField(CharacterForm))
    genres = FieldList(FormField(GenreForm))

    def validate_characters(self, characters):
        number_of_characters = len(characters)
        if number_of_characters > 5:
            raise ValidationError('5 characters is the limit')
        elif number_of_characters == 0:
            raise ValidationError('At least 1 character needs to be defined')
