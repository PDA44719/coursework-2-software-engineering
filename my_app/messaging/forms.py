from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    """Form to get the text to be contained in a message."""
    text = TextAreaField(label='Message', validators=[DataRequired()])


class LookForUser(FlaskForm):
    """Form used to get the email address of the user with whom the current user would like to chat."""
    user = SelectField(label="Find User", validators=[DataRequired()])

    def __init__(self, user_choices):
        """Set the user options available."""
        super().__init__()
        self.user.choices = user_choices
