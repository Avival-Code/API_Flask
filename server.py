import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask_restful import Api
from app.main.views import *
from app import create_app, database

dotenv_path = join( dirname( __file__ ), '.env' )
load_dotenv( dotenv_path )

app = create_app( os.environ.get( "CURRENT_CONFIG" ) or 'default' )

api = Api( app )

api.add_resource( MainPage, "/" )
api.add_resource( Login, "/login" )
api.add_resource( Usuarios, "/usuarios" )

app.app_context().push()
database.create_all()

if __name__ == "__main__":
    app.run( host='0.0.0.0' )