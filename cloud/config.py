

class Config:

    # General Flask Config
    SECRET_KEY = b'ergergergergegg/'
    USE_PROXYFIX = True

    APPLICATION_ROOT = '/'

    FLASK_APP = 'app.py'
    FLASK_RUN_HOST = 'localhost'
    FLASK_RUN_PORT = 8000

    FLASK_DEBUG = 0
    FLASK_ENV = "development"  # production

    DEBUG = False
    TESTING = False  # True

    SESSION_TYPE = 'sqlalchemy'  # 'redis'
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_COOKIE_NAME = 'my_cookieGetFace'
    SESSION_PERMANENT = True

    # Database

    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = "simple"  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 100
