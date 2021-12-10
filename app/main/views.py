from copy import Error
from datetime import datetime
from logging import error
from flask import make_response, render_template, jsonify, send_from_directory
from flask.globals import session
from flask.helpers import send_file, send_from_directory
from werkzeug.exceptions import default_exceptions
from werkzeug.utils import secure_filename
from flask_restful import Resource, marshal, marshal_with, abort,Api, reqparse, request, MethodNotAllowed
from flask_praetorian import auth_required
from flask_cors import cross_origin
from werkzeug.wrappers import Response
from .. import database
from ..extensions import guard, limiter
from ..models import *
from .parsers import *
from .fields import *
from .string_validation import *

class Login( Resource ):
    def post( self ):
        login_args = login_put_args.parse_args()
        user = guard.authenticate( login_args[ 'username' ], login_args[ 'password' ] )
        token = guard.encode_jwt_token( user )
        return jsonify( { 'clave_usuario': user.clave_usuario, 'access_token': token } )

class Usuarios( Resource ):
    decorators = [ 
        limiter.limit( "1 per second", methods=[ 'GET' ] ),
        limiter.limit( "2 per day", methods=[ 'POST' ] )
    ]

    @marshal_with( usuario_fields )
    def get( self ):
        usuarios = Usuario.query.all()
        return usuarios, 200

    @cross_origin( allow_headers=[ 'Content-Type' ] )
    @marshal_with( usuario_fields )
    def post( self ):
        usuario_args = usuario_put_args.parse_args()
        if not user_input_validation( usuario_args ):
            abort( 400, message="Información inválida." )

        usuario_existe = Usuario.query.filter_by( nombre_usuario=usuario_args[ 'nombre_usuario' ] ).one_or_none()
        if usuario_existe:
            abort( 409, message="El nombre de usuario ya se esta utilizando." )

        usuario = Usuario( nombres=usuario_args[ 'nombres' ], apellidos=usuario_args[ 'apellidos' ], correo_electronico=usuario_args[ 'correo_electronico' ], nombre_usuario=usuario_args[ 'nombre_usuario' ], contrasena=guard.hash_password( usuario_args[ 'contrasena' ] ), fecha_union=datetime.now(), foto_perfil='' )
        database.session.add( usuario )
        database.session.commit()
        return 201

class UsuarioEspecifico( Resource ):
    decorators = [ 
        limiter.limit( "1 per second", methods=[ 'GET' ] ),
        limiter.limit( "10 per day", methods=[ 'PUT' ] ),
        limiter.limit( "1 per day", methods=[ 'DELETE' ] )
    ]

    @marshal_with( usuario_fields )
    def get( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        return usuario, 200

    @auth_required
    @marshal_with( usuario_fields )
    def put( self, clave_usuario ):
        args = usuario_put_args.parse_args()
        if not user_input_validation( args ):
            abort( 400, message="Información inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message = "No se encontró el usuario especificado." )

        usuario.nombres = args[ "nombres" ]
        usuario.apellidos = args[ "apellidos" ]
        usuario.nombre_usuario = args[ "nombre_usuario" ]
        usuario.contrasena = guard.hash_password( args[ "contrasena" ] )
        usuario.correo_electronico = args[ "correo_electronico" ]
        database.session.commit()
        return 200

    @auth_required
    def delete( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).first()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        database.session.delete( usuario )
        database.session.commit()
        return {}, 200

class PublicacionesFavoritas( Resource ):
    decorators = [ limiter.limit( "1 per second", methods=[ 'GET', 'POST', 'DELETE' ] ) ]

    @auth_required
    @marshal_with( publicacion_fields )
    def get( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )
        
        publicaciones_favoritas = database.session.query( Publicacion ).join( PublicacionesFavoritas, PublicacionesFavoritas.clave_publicacion==Publicacion.clave_publicacion ).filter( PublicacionesFavoritas.clave_usuario==clave_usuario ).all()
        if not publicaciones_favoritas:
            abort( 404, message="No hay publicaciones favoritas." )
        return publicaciones_favoritas, 200

    @auth_required
    def post( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = publicaciones_favoritas_put_args.parse_args()
        favorito_existe = PublicacionesFavoritas.query.filter_by( clave_usuario==clave_usuario).filter_by( PublicacionesFavoritas.clave_publicacion==args[ 'clave_publicacion' ] ).first()
        if favorito_existe:
            abort( 409, message="La publicación ya esta en la lista de favoritos." )

        publicacion_favorita = PublicacionesFavoritas( clave_usuario=clave_usuario, clave_publicacion=args[ 'clave_publicacion' ] )
        database.session.add( publicacion_favorita )
        database.session.commit()
        return {}, 201

    @auth_required
    def delete( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = publicaciones_favoritas_put_args.parse_args()
        publicacion_favorita = PublicacionesFavoritas.query.filter_by( clave_usuario==clave_usuario).filter_by( PublicacionesFavoritas.clave_publicacion==args[ 'clave_publicacion' ] ).first()
        if not publicacion_favorita:
            abort( 409, message="No se encontró la publicación favorita especificada." )

        database.session.delete( publicacion_favorita )
        database.session.commit()
        return {}, 200

class UsuariosFavoritos( Resource ):
    decorators = [ limiter.limit( "1 per second", methods=[ 'GET', 'POST', 'DELETE' ] ) ]

    @auth_required
    @marshal_with( usuario_fields )
    def get( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        usuarios = database.session.query( Usuario ).join( UsuariosFavoritos, UsuariosFavoritos.clave_usuario_favorito==Usuario.clave_usuario ).filter_by( UsuariosFavoritos.clave_usuario==clave_usuario ).all()
        if not usuarios:
            abort( 404, message="No hay usuarios favoritos." )
        return usuarios, 200

    @auth_required
    def post( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = usuarios_favoritos_put_args.parse_args()
        favorito_existe = UsuariosFavoritos.query.filter_by( clave_usuario==clave_usuario ).filter_by( UsuariosFavoritos.clave_usuario_favorito==args[ "clave_usuario_favorito" ] ).first()
        if favorito_existe:
            abort( 404, message="El usuario ya esta en la lista de favoritos." )

        favorito = UsuariosFavoritos( clave_usuario=clave_usuario, clave_usuario_favorito=args[ "clave_usuario_favorito" ] )
        database.session.add( favorito )
        database.session.commit()
        return {}, 201

    @auth_required
    def delete( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = usuarios_favoritos_put_args.parse_args()
        usuario_favorito = UsuariosFavoritos.query.filter_by( clave_usuario==clave_usuario ).filter_by( UsuariosFavoritos.clave_usuario_favorito==args[ "clave_usuario_favorito" ] ).first()
        if not usuario_favorito:
            abort( 404, message="No se encontró el usuario favorito especificado." )

        database.session.delete( usuario_favorito )
        database.session.commit()
        return 200

class PublicacionesGeneral( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( publicacion_fields )
    def get( self ):
        publicaciones = database.session.query( Publicacion ).join( Multimedia, Multimedia.clave_publicacion==Publicacion.clave_publicacion ).all()
        return publicaciones, 200

class PublicacionesUsuario( Resource ):
    decorators = [ 
        limiter.limit( "1 per second", methods=[ 'GET' ] ),
        limiter.limit( "50 per day", methods=[ 'POST' ] )
    ]

    @marshal_with( publicacion_fields )
    def get ( self, clave_usuario_in ):
        try:
            publicaciones = database.session.query( Publicacion ).join( UsuarioPublicacion, UsuarioPublicacion.clave_publicacion==Publicacion.clave_publicacion ).join( Multimedia, Multimedia.clave_publicacion==Publicacion.clave_publicacion ).filter( UsuarioPublicacion.clave_usuario==clave_usuario_in ).all()
            return publicaciones, 200
        except Error:
            return 404

    @auth_required
    @marshal_with( publicacion_fields )
    def post( self, clave_usuario_in ):
        try: 
            publicacionArgs = publicacion_put_args.parse_args()
            if not publication_input_validation( publicacionArgs ):
                abort( 400, message="Información inválida." )
                
            publicacionExiste = Publicacion.query.filter_by( nombre_publicacion=publicacionArgs[ 'nombre_publicacion' ] ).one_or_none()
            if publicacionExiste:
                abort( 409, message="Ya existe una publicación con ese nombre." ) 
            
            publicacionNueva = Publicacion( nombre_publicacion = publicacionArgs[ 'nombre_publicacion' ],descripcion=publicacionArgs[ 'descripcion' ],calificacion_general = 0.0, categoria = publicacionArgs[ 'categoria' ],fecha_publicacion= datetime.now() )
            database.session.add( publicacionNueva )
            database.session.commit()

            registro = UsuarioPublicacion( clave_usuario=clave_usuario_in, clave_publicacion=publicacionNueva.clave_publicacion )
            database.session.add( registro )
            database.session.commit()

            multimedia = Multimedia( clave_publicacion=publicacionNueva.clave_publicacion ,multimedia=publicacionArgs[ 'multimedia' ] )
            database.session.add( multimedia )
            database.session.commit()
            return 201
        except Error:
            return 404

class PublicacionesExpecificas( Resource ):
    decorators = [ 
        limiter.limit( "1 per second", methods=[ 'GET' ] ),
        limiter.limit( "50 per day", methods=[ 'DELETE' ] ) 
    ]
    
    @marshal_with( publicacion_fields )
    def get( self, clave_publicacion ):
        try:
            publicacionEncontrada = database.session.query( Publicacion ).join( Multimedia, Multimedia.clave_publicacion==Publicacion.clave_publicacion ).join( UsuarioPublicacion, UsuarioPublicacion.clave_publicacion==Publicacion.clave_publicacion ).filter( Publicacion.clave_publicacion==clave_publicacion ).one_or_none()
            if not publicacionEncontrada:
                abort( 404, message="No se encontró la publicación especificada" )
            return publicacionEncontrada, 200
        except Error:
            return 404

    @auth_required
    def delete( self, clave_publicacion ):
        register = UsuarioPublicacion.query.filter_by( clave_publicacion==clave_publicacion ).one_or_none()
        if not register:
            abort (404, message= "No se encontro la publicacion especificada")

        multimedia = Multimedia.query.filter_by( clave_publicacion==clave_publicacion ).one_or_none()    
        publicacion = Publicacion.query.filter_by( clave_publicacion == clave_publicacion ).one_or_none()

        database.session.delete( register )
        database.session.delete( multimedia )
        database.session.delete( publicacion )
        database.session.commit()
        return 200

class SearchPublicaciones( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( publicacion_fields )
    def get( self, search_query ):
        publicaciones = Publicacion.query.filter( Publicacion.nombre_publicacion.contains( search_query ) ).all()
        if not publicaciones:
            abort( 404, message="No se encontraron publicaciones" )

        resultado = []
        for publicacion in publicaciones:
            register = UsuarioPublicacion.query.filter_by( clave_publicacion=publicacion.clave_publicacion ).one_or_none()
            multimedia = Multimedia.query.filter_by( clave_publicacion=publicacion.clave_publicacion ).one_or_none()
            resultado.append( { 'clave_publicacion': publicacion.clave_publicacion, 'clave_usuario': register.clave_usuario, 'nombre_publicacion': publicacion.nombre_publicacion, 'descripcion': publicacion.descripcion, 'calificacion_general': publicacion.calificacion_general, 'categoria': publicacion.categoria, 'fecha_publicacion': publicacion.fecha_publicacion, 'multimedia': multimedia.multimedia } )
        
        return resultado, 200

class SearchUsuarios( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( usuario_fields )
    def get( self, search_query ):
        usuarios = Usuario.query.filter( Usuario.nombre_usuario.contains( search_query ) ).all()
        if not usuarios:
            abort( 404, message="No se encontraron usuarios" )

        resultado = []
        for usuario in usuarios:
            resultado.append( { 'clave_usuario': usuario.clave_usuario, 'nombre_usuario': usuario.nombre_usuario } )

        return resultado, 200
            

class Comentarios(Resource):
    def post(self):
        try:

            comentarioSubir = comentario_usuario_put_args.parse_args()
            comentarioNuevo = ComentarioUsuario(clave_publicacion = comentarioSubir['clave_publicacion'],clave_usuario = comentarioSubir['clave_usuario'], comentario = comentarioSubir['comentario'])
            database.session.add(comentarioNuevo)
            database.session.commit()
            return comentarioNuevo, 201
        except Error:
            return 404
          
    def get (self, clave_publicacion):
        try:
            
            comentarioPublicacion = ComentarioUsuario.query.filter_by(clave_publicacion == clave_publicacion).one_or_none()
            if not comentarioPublicacion:
                return "No hay comentarios", 404
            return comentarioPublicacion, 201 
        except Error:
            return "Exepcion Encontrada",404

    def delete(self):
            clave_comentario = comentario_usuario_put_args.parse_args()
            comentarioEncontrado = ComentarioUsuario.query.filter_by(clave_comentario == clave_comentario['clave_comentario']).one_or_none()
            if not comentarioEncontrado:
              abort (404, message= "No se encontro la publicacion especifica")

            database.session.delete(comentarioEncontrado)
            database.session.commit()
            return 200


class multimedia( Resource ):

    def post(self):
        
        try: 
            multimediaSubir = multimedia_put_args.parse_args()
            multimediaNueva = Multimedia(clave_publicacion=multimediaSubir['clave_publicacion'], multimedia= ['multimedia'])
            database.session.add(multimediaNueva)
            database.session.commit()
            return multimediaNueva, 201
        except Error:
            return 404

    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( multimedia_fields )
    def get( self ):
        multimedia = database.session.query( Multimedia ).all()
        return multimedia, 200

class MultimediaUsuario( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( multimedia_fields )
    def get( self, clave_usuario ):
        registros = UsuarioPublicacion.query.filter_by( clave_usuario=clave_usuario ).all()
        if not registros:
            abort( 404, message="El usuario no tiene publicaciones." )

        imagenes = []
        for registro in registros:
            multimedia_especifica = Multimedia.query.filter_by( clave_publicacion=registro.clave_publicacion ).one_or_none()
            imagenes.append( { 'clave_multimedia': multimedia_especifica.clave_multimedia, 'clave_publicacion': multimedia_especifica.clave_publicacion, 'multimedia': multimedia_especifica.multimedia } )
        
        return imagenes, 200
    

    

class multimediaExpecifica(Resource):
    
    @marshal_with( multimedia_fields )
    def get (self, clave_publicacion_in):
       
            
            multimedia = Multimedia.query.filter_by(clave_publicacion = clave_publicacion_in).one_or_none()
            if not multimedia:
                return "No hay multimedia para esta publicacion", 404
            return multimedia, 201 
      

    def put (self, clave_publicacion_in):
        try:
            multimediaNueva = multimedia_put_args.parse_args()
            multimedia = Multimedia.query.filter_by(clave_publicacion = clave_publicacion_in).one_or_none().update(dict(multimedia = multimediaNueva["multimedia"]))
            return 200
        except Error:
            return 400
            
class calificacionPublicacion(Resource):
    def post(self):
        try:
            calificacionSubir = calificacion_publicacion_put_args.parse_args()
            calificacionNueva = CalificacionPublicacion(clave_publicacion = calificacionSubir['clave_publicacion'], clave_usuario= calificacionSubir['clave_usuario'], calificacion=['calificacion'])
            database.session.add(calificacionNueva)
            database.session.commit()
            return {}, 201
        except Error:
            return 404

class calificacionPublicacionEspecifica(Resource):
    def get(self,clave_publicacion):
        calificaciones = CalificacionPublicacion.query.filter_by(clave_publicacion = clave_publicacion)
        if not calificaciones:
            return "No existe calificaciones para la publicacion", 404
        return calificaciones, 201