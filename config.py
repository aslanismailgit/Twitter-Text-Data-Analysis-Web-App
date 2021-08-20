class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/twan.db'
    #  this is a connection to a dead google cloud mysql db
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:<your_db_password>@34.135.124.147:3306/twandb"

    # this is a sample connection to mongodb atlas
    # MONGO_URI = "mongodb+srv://twanuser1:<your_db_password>@cluster0.d89gm.mongodb.net/twan_db?retryWrites=true&w=majority"

    SECRET_KEY = 'ec9439cfc6c796ae2029594d'
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = <your_mail_address>
    MAIL_PASSWORD = <your_mail_password>
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True


