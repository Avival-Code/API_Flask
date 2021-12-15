from .. import database
from ..extensions import guard, limiter
from ..models import *
from .parsers import *
from .fields import *
from .string_validation import *
from copy import Error
from datetime import datetime
from flask import jsonify
from flask_restful import Resource, marshal_with, abort
from flask_praetorian import auth_required
from flask_cors import cross_origin

class Login( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    def post( self ):
        login_args = login_put_args.parse_args()
        if not login_input_validation( login_args ):
            abort( 400, message="Información inválida." )

        user = guard.authenticate( login_args[ 'username' ], login_args[ 'password' ] )
        token = guard.encode_jwt_token( user )
        return jsonify( { 'clave_usuario': user.clave_usuario, 'access_token': token } )

class Usuarios( Resource ):
    decorators = [ 
        limiter.limit( "1 per second", methods=[ 'GET' ] ),
        limiter.limit( "5 per day", methods=[ 'POST' ] )
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
        if not id_validation( clave_usuario ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        return usuario, 200

    @auth_required
    @marshal_with( usuario_fields )
    def put( self, clave_usuario ):
        if not id_validation( clave_usuario ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message = "No se encontró el usuario especificado." )

        args = usuario_put_args.parse_args()
        if not user_input_validation( args ):
            abort( 400, message="Información inválida." )

        nombre_usuario_existente = Usuario.query.filter_by( nombre_usuario=args[ "nombre_usuario" ] ).one_or_none()
        if nombre_usuario_existente:
            abort( 409, message="El nombre de usuario ya se esta utilizando." )

        usuario.nombres = args[ "nombres" ]
        usuario.apellidos = args[ "apellidos" ]
        usuario.nombre_usuario = args[ "nombre_usuario" ]
        usuario.contrasena = guard.hash_password( args[ "contrasena" ] )
        usuario.correo_electronico = args[ "correo_electronico" ]
        usuario.foto_perfil = args[ "foto_perfil" ]
        database.session.commit()
        return 200

    @auth_required
    def delete( self, clave_usuario ):
        if not id_validation( clave_usuario ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).first()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        database.session.delete( usuario )
        database.session.commit()
        return {}, 200

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
        if not id_validation( clave_usuario_in ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario_in ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        try:
            publicaciones = database.session.query( Publicacion ).join( UsuarioPublicacion, UsuarioPublicacion.clave_publicacion==Publicacion.clave_publicacion ).join( Multimedia, Multimedia.clave_publicacion==Publicacion.clave_publicacion ).filter( UsuarioPublicacion.clave_usuario==clave_usuario_in ).all()
            return publicaciones, 200
        except Error:
            return 404

    @auth_required
    @marshal_with( publicacion_fields )
    def post( self, clave_usuario_in ):
        if not id_validation( clave_usuario_in ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario_in ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

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
        if not id_validation( clave_publicacion ):
            abort( 400, message="Clave de publicación inválida." )

        try:
            publicacionEncontrada = database.session.query( Publicacion ).join( Multimedia, Multimedia.clave_publicacion==Publicacion.clave_publicacion ).join( UsuarioPublicacion, UsuarioPublicacion.clave_publicacion==Publicacion.clave_publicacion ).filter( Publicacion.clave_publicacion==clave_publicacion ).one_or_none()
            if not publicacionEncontrada:
                abort( 404, message="No se encontró la publicación especificada" )

            return publicacionEncontrada, 200
        except Error:
            return 404

    @auth_required
    def delete( self, clave_publicacion ):
        if not id_validation( clave_publicacion ):
            abort( 400, message="Clave de publicación inválida." )

        register = UsuarioPublicacion.query.filter_by( clave_publicacion=clave_publicacion ).one_or_none()
        if not register:
            abort( 404, message= "No se encontro la publicacion especificada" )

        multimedia = Multimedia.query.filter_by( clave_publicacion=clave_publicacion ).one_or_none()    
        publicacion = Publicacion.query.filter_by( clave_publicacion=clave_publicacion ).one_or_none()

        database.session.delete( register )
        database.session.delete( multimedia )
        database.session.delete( publicacion )
        database.session.commit()
        return 200

class SearchPublicaciones( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( publicacion_fields )
    def get( self, search_query ):
        if not search_input_validation( search_query ):
            abort( 400, message="Información inválida." )

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
        if not search_input_validation( search_query ):
            abort( 400, message="Información inválida." )

        usuarios = Usuario.query.filter( Usuario.nombre_usuario.contains( search_query ) ).all()
        if not usuarios:
            abort( 404, message="No se encontraron usuarios" )

        resultado = []
        for usuario in usuarios:
            resultado.append( { 'clave_usuario': usuario.clave_usuario, 'nombre_usuario': usuario.nombre_usuario } )

        return resultado, 200

class MultimediaGeneral( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( multimedia_fields )
    def get( self ):
        multimedia = Multimedia.query.all()
        return multimedia, 200

class MultimediaUsuario( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( multimedia_fields )
    def get( self, clave_usuario ):
        if not id_validation( clave_usuario ):
            abort( 400, message="Clave de usuario inválida." )

        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        registros = UsuarioPublicacion.query.filter_by( clave_usuario=clave_usuario ).all()
        if not registros:
            abort( 404, message="El usuario no tiene publicaciones." )

        imagenes = []
        for registro in registros:
            multimedia_especifica = Multimedia.query.filter_by( clave_publicacion=registro.clave_publicacion ).one_or_none()
            imagenes.append( { 'clave_multimedia': multimedia_especifica.clave_multimedia, 'clave_publicacion': multimedia_especifica.clave_publicacion, 'multimedia': multimedia_especifica.multimedia } )
        
        return imagenes, 200

class MultimediaEspecifica( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( multimedia_fields )
    def get( self, clave_publicacion_in ):
        if not id_validation( clave_publicacion_in ):
            abort( 400, message="Clave de usuario inválida." )

        publicacion = Publicacion.query.filter_by( clave_publicacion=clave_publicacion_in ).one_or_none()
        if not publicacion:
            abort( 404, message="No se encontró la publicación especificada." )
            
        multimedia = Multimedia.query.filter_by( clave_publicacion=clave_publicacion_in ).one_or_none()
        if not multimedia:
            abort( 404, message="No hay multimedia para esta publicacion" )

        return multimedia, 200 

class Comentarios( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @auth_required
    @cross_origin( allow_headers=[ 'Content-Type' ] )
    @marshal_with( comentario_usuario_fields )
    def post( self ):
        try:
            comentarioSubir = comentario_usuario_put_args.parse_args()
            if not comment_input_validation( comentarioSubir ):
                abort( 400, message="Información inválida" )

            publicacion = Publicacion.query.filter_by( clave_publicacion=comentarioSubir[ 'clave_publicacion' ] ).one_or_none()
            if not publicacion:
                abort( 404, message="No se encontró la publicación especificada." )

            usuario = Usuario.query.filter_by( clave_usuario=comentarioSubir[ 'clave_usuario' ] ).one_or_none()
            if not usuario:
                abort( 404, message="No se encontró el usuario especificado." )

            comentarioNuevo = ComentarioUsuario( clave_publicacion = comentarioSubir[ 'clave_publicacion' ], clave_usuario=comentarioSubir[ 'clave_usuario' ], comentario=comentarioSubir[ 'comentario' ] )
            database.session.add( comentarioNuevo )
            database.session.commit()
            return comentarioNuevo, 201
        except Error:
            return 404

class ComentariosEspecificos( Resource ):
    decorators = [ limiter.limit( "1 per second" ) ]
    @marshal_with( comentario_usuario_fields )    
    def get( self, clave_publicacion_in ):
        try:
            if not id_validation(  clave_publicacion_in ):
                abort( 400, message="Clave de publicacion inválida" )

            publicacion = Publicacion.query.filter_by( clave_publicacion=clave_publicacion_in ).one_or_none()
            if not publicacion:
                abort( 404, message="No se encontró la publicación especificada." )

            comentarioPublicacion = ComentarioUsuario.query.filter_by( clave_publicacion=clave_publicacion_in ).all()
            if not comentarioPublicacion:
                abort( 404, message="No hay comentarios" )

            return comentarioPublicacion, 200 
        except Error:
            return "Exepcion Encontrada",404