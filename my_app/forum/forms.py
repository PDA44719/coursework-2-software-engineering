from flask_wtf import FlaskForm, Form
from wtforms import StringField, TextAreaField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, ValidationError


movie_genres = ['Science Fiction', 'Adventure', 'Action', 'Fantasy', 'Animation', 'Family', 'Music', 'Comedy', 'War',
                'Thriller', 'Crime', 'Romance', 'History', 'Horror', 'Mystery', 'Drama', 'Western', 'Documentary']


class CharacterForm(Form):
    """Form that will get information about the character name and description."""
    character_name = StringField(label='Character Name', validators=[DataRequired()])
    character_description = TextAreaField(label='Character Description', validators=[DataRequired()])


class GenreForm(Form):
    """Form that will get the name of a genre."""
    genre = SelectField('Genre', choices=[(genre, genre) for genre in movie_genres])


class ProposalForm(FlaskForm):
    """Form that will get information about the title, plot, characters and genres of a film proposal."""
    title = StringField(label='Title', validators=[DataRequired()])
    plot = TextAreaField(label='Plot', validators=[DataRequired()])
    characters = FieldList(FormField(CharacterForm))
    genres = FieldList(FormField(GenreForm))

    def validate_characters(self, characters):
        """Only allow the user to input a number of characters between 1 and 5."""
        number_of_characters = len(characters)
        if number_of_characters > 5:
            raise ValidationError('5 characters per proposal is the limit.')
        elif number_of_characters == 0:
            raise ValidationError('At least 1 character needs to be defined.')

    def validate_genres(self, genres):
        """Only allow the user to input a number of genres between 1 and 3."""
        number_of_genres = len(genres)
        if number_of_genres > 3:
            raise ValidationError('3 genres per proposal is the limit.')
        elif number_of_genres == 0:
            raise ValidationError('At least 1 genre needs to be defined')
