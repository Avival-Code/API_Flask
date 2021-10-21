import os
from os.path import join, dirname
from dotenv import load_dotenv
basedir = os.path.abspath( os.path.dirname( __file__ ) )

dotenv_path = join( dirname( __file__ ), '.env' )
load_dotenv( dotenv_path )

class BaseConfig:
    SECRET_KEY = os.environ.get( "SECRET_KEY" )
    JWT_ACCESS_LIFESPAN = { "hours" : 12 }
    JWT_REFRESH_LIFESPAN = { "days" : 10 }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app( app ):
        pass

class DevelopmentConfig( BaseConfig ):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get( "DEVELOPMENT_DATABASE_URL" )

class TestingConfig( BaseConfig ):
    DEBUG = False
    TESTING = True
    JWT_ACCESS_LIFESPAN = { "minutes" : 20 }
    JWT_REFRESH_LIFESPAN = { "days" : 0 }
    SQLALCHEMY_DATABASE_URI = os.environ.get( "TESTING_DATABASE_URL" )

class ProductionConfig( BaseConfig ):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get( "PRODUCTION_DATABASE_URL" )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}