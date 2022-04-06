import pathlib


class Config(object):
    """Base configuration class."""
    SECRET_KEY = b'gjyMT4Ju-ek9u4MDeOhpHQ'
    WTF_CSRF_SECRET_KEY = "crFAuXFCPKbKWw8JAKfnSA"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_PATH = pathlib.Path(__file__).parent.parent.joinpath("my_app")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(DATA_PATH.joinpath('example.sqlite'))


class ProductionConfig(Config):
    """Production configuration class."""
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration class."""
    TESTING = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration class."""
    TESTING = True
    SQLALCHEMY_ECHO = True
