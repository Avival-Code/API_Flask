from flask import Flask
from .extensions import database, guard, limiter
from .models import Usuario
from config import config

def create_app( config_name ):
    app = Flask( __name__ )

    app.config.from_object( config[ config_name ] )
    config[ config_name ].init_app( app )

    database.init_app( app )
    guard.init_app( app, Usuario )
    limiter.init_app( app )

    return app