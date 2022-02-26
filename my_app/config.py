import pathlib


class Config(object):
    def __init__(self):
        self.SECRET_KEY = b'gjyMT4Ju-ek9u4MDeOhpHQ'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.DATA_PATH = pathlib.Path(__file__).parent.parent.joinpath("data")
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(self.DATA_PATH.joinpath('example.sqlite'))


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False
        self.SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_ECHO = True
