from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app import db
from flask_login import current_user
from my_app.models import User, Message, Chat, LastTimeChecked


class MessageForm(FlaskForm):
    text = TextAreaField(label='Message', validators=[DataRequired()])


class LookForUser(FlaskForm):
    user = SelectField(label="Find User", validators=[DataRequired()])

    def __init__(self, user_choices):
        super().__init__()
        self.user.choices = user_choices
