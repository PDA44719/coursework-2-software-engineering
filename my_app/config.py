import pathlib


class Config(object):
    SECRET_KEY = b'gjyMT4Ju-ek9u4MDeOhpHQ'
    WTF_CSRF_SECRET_KEY = "crFAuXFCPKbKWw8JAKfnSA"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_PATH = pathlib.Path(__file__).parent.parent.joinpath("my_app")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(DATA_PATH.joinpath('example.sqlite'))
    UPLOADED_PHOTOS_DEST = pathlib.Path(__file__).parent.joinpath("static/img")


class ProductionConfig(Config):
    TESTING = False


class DevelopmentConfig(Config):
    TESTING = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
