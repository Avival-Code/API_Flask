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

api.add_resource( Login, "/login" )
api.add_resource( Usuarios, "/usuarios" )
api.add_resource( UsuarioEspecifico, "/usuarios/<int:clave_usuario>" )
api.add_resource( PublicacionesGeneral, "/publicaciones" )
api.add_resource( PublicacionesUsuario, "/publicacionesusuario/<int:clave_usuario_in>" )
api.add_resource( PublicacionesEspecificas, "/publicaciones/<int:clave_publicacion>" )
api.add_resource( SearchPublicaciones, "/publicaciones/search/<string:search_query>" )
api.add_resource( SearchUsuarios, "/usuarios/search/<string:search_query>" )
api.add_resource( MultimediaGeneral, "/multimedia" )
api.add_resource( MultimediaUsuario, "/multimedia/<int:clave_usuario>" )
api.add_resource( MultimediaEspecifica, "/multimedia/<int:clave_publicacion_in>/obtenermultimedia" )
api.add_resource( Comentarios, "/comentarios" )
api.add_resource( ComentariosEspecificos, "/comentarios/<int:clave_publicacion_in>" )

app.app_context().push()
database.create_all()

if __name__ == "__main__":
    app.run( host='0.0.0.0' )