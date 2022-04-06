from my_app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """Database model that stores information about a user"""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    proposals = db.relationship("Proposal")  # One user to many proposals relationship
    time_checks = db.relationship("LastTimeChecked")  # One user to many time checks relationship

    def __repr__(self):
        """String representation of the user."""
        return f"{self.id} {self.first_name} {self.last_name} {self.email} {self.password}"

    def set_password(self, password):
        """Set a hashed password from the given password by the user."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the password input when logging in is the same as the hashed password."""
        return check_password_hash(self.password, password)


class Proposal(db.Model):
    """DataBase model that stores a film proposal's information."""
    __tablename__ = "proposal"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    plot = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # One proposal to many characters relationship, though the number of characters will be limited to 1-5
    characters = db.relationship("Character")
    # One proposal to many genres relationship, though the number of genres will be limited to 1-3
    genres = db.relationship("Genre")


class Character(db.Model):
    """DataBase model that stores information about a character from a film proposal."""
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.Text, nullable=False)
    character_description = db.Column(db.Text, nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey("proposal.id"))


class Genre(db.Model):
    """DataBase model that stores information about the genre of a film proposal."""
    __tablename__ = "genre"
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.Text, nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey("proposal.id"))


class Chat(db.Model):
    """DataBase model that stores information about a chat between two users."""
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_2_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    messages = db.relationship("Message")  # One chat to many messages relationship
    # One chat to many time checks relationship, though only one per user (per chat) is allowed
    time_checks = db.relationship("LastTimeChecked")


class Message(db.Model):
    """DataBase model that stores information about a message sent in a chat."""
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.DateTime, nullable=False)  # Time when the message was sent
    user_sender_id = db.Column(db.Integer, nullable=False)
    user_recipient_id = db.Column(db.Integer, nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"))


class LastTimeChecked(db.Model):
    """Database model that stores information about the last time a chat was checked by a specific user."""
    __tablename__ = "last_checked"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
