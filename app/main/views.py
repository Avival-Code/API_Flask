from copy import Error
from datetime import datetime
from logging import error
import re
from flask import make_response, render_template, jsonify, send_from_directory
from flask.globals import session
from flask.helpers import send_file, send_from_directory
from werkzeug.utils import secure_filename
from flask_restful import Resource, marshal_with, abort,Api, reqparse, request, MethodNotAllowed
from flask_praetorian import auth_required
from werkzeug.wrappers import Response
from .. import database
from ..extensions import guard, limiter
from ..models import *
from .parsers import *
from .fields import *
import os
import app

class MainPage( Resource ):
    def get( self ):
        headers = { 'Content-Type': 'Text/html' }
        return make_response( render_template( 'main_page.html' ), 200, headers )

class Login( Resource ):
    def post( self ):
        login_args = login_put_args.parse_args()
        user = guard.authenticate( login_args[ 'username' ], login_args[ 'password' ] )
        token = guard.encode_jwt_token( user )
        return jsonify( { 'clave_usuario': user.clave_usuario, 'access_token': token } )

class Usuarios( Resource ):
    @marshal_with( usuario_fields )
    def get( self ):
        usuarios = Usuario.query.all()
        return usuarios, 200

    decorators = [ limiter.limit( "2 per day" ) ]
    @marshal_with( usuario_fields )
    def post( self ):
        usuario_args = usuario_put_args.parse_args()
        usuario_existe = Usuario.query.filter_by( nombre_usuario=usuario_args[ 'nombre_usuario' ] ).one_or_none()
        if usuario_existe:
            abort( 409, message="El nombre de usuario ya se esta utilizando." )

        usuario = Usuario( nombres=usuario_args[ 'nombres' ], apellidos=usuario_args[ 'apellidos' ], correo_electronico=usuario_args[ 'correo_electronico' ], nombre_usuario=usuario_args[ 'nombre_usuario' ], contrasena=guard.hash_password( usuario_args[ 'contrasena' ] ) )
        database.session.add( usuario )
        database.session.commit()
        return usuario, 201

class UsuarioEspecifico( Resource ):
    @marshal_with( usuario_fields )
    def get( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        return usuario, 200

    decorators = [ limiter.limit( "10 per day" ) ]
    @auth_required
    @marshal_with( usuario_fields )
    def put( self, clave_usuario ):
        args = usuario_put_args.parse_args()
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message = "No se encontró el usuario especificado." )

        usuario.nombres = args[ "nombres" ]
        usuario.apellidos = args[ "apellidos" ]
        usuario.nombre_usuario = args[ "nombre_usuario" ]
        usuario.contrasena = guard.hash_password( args[ "contrasena" ] )
        usuario.correo_electronico = args[ "correo_electronico" ]
        database.session.commit()
        return usuario, 200

    decorators = [ limiter.limit( "1 per day" ) ]
    @auth_required
    def delete( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).first()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        database.session.delete( usuario )
        database.session.commit()
        return {}, 200

class PublicacionesFavoritas( Resource ):
    @auth_required
    def get( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario=clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )
        
        publicaciones_favoritas = database.session.query( Publicacion ).join( PublicacionesFavoritas, PublicacionesFavoritas.clave_publicacion==Publicacion.clave_publicacion ).filter( PublicacionesFavoritas.clave_usuario==clave_usuario ).all()
        if not publicaciones_favoritas:
            abort( 404, message="No hay publicaciones favoritas." )
        return publicaciones_favoritas, 200

    def post( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = publicaciones_favoritas_put_args.parse_args()
        favorito_existe = PublicacionesFavoritas.query.filter_by( clave_usuario==clave_usuario).filter_by( PublicacionesFavoritas.clave_publicacion==args[ 'clave_publicacion' ] ).first()
        if favorito_existe:
            abort( 409, message="El favorito ya esta agregado a la lista." )

        publicacion_favorita = PublicacionesFavoritas( clave_usuario=clave_usuario, clave_publicacion=args[ 'clave_publicacion' ] )
        database.session.add( publicacion_favorita )
        database.session.commit()
        return {}, 201

    decorators = [ limiter.limit( "1 per minute" ) ]
    @auth_required
    def delete( self, clave_usuario ):
        usuario = Usuario.query.filter_by( clave_usuario==clave_usuario ).one_or_none()
        if not usuario:
            abort( 404, message="No se encontró el usuario especificado." )

        args = publicaciones_favoritas_put_args.parse_args()
        favorito = PublicacionesFavoritas.query.filter_by( clave_usuario==clave_usuario).filter_by( PublicacionesFavoritas.clave_publicacion==args[ 'clave_publicacion' ] ).first()
        if not favorito:
            abort( 409, message="No se encontró el favorito especificado." )

        database.session.delete( favorito )
        database.session.commit()
        return {}, 200

class UsuariosFavoritos( Resource ):
    def get( self, clave_usuario ):
        return 200

    def post( self, clave_usuario ):
        return 200


class UploadImagen( Resource ):

    def post(self):
        foto = request.files['file']
        if not foto:
            return "No se a seleccionado ningun archivo", 404
        try:
            foto.save(os.path.join("Imagenes", secure_filename(foto.filename)))
            return "se guardo con exito", 201
        except IOError:
            return "No se puede guardar ahora mismo", 403



class RecuperarImagen( Resource ):
   

    def post(self):
            foto = request.get_json()
            nombreFoto = foto['NombreFoto']
            if not nombreFoto:
                return "No se especifica que foto decea recuperar", 403
            try:
                return send_file(os.path.join("Imagenes"),nombreFoto, as_attachment=False) , 201
            except Error:
                    return "no se puede recuperar la foto", 404
            

class DescargarImagen( Resource ):
    
    def get(self):
            foto = request.get_json()
            nombreFoto = foto['NombreFoto']
            if not nombreFoto:
                return "No se especifica que foto decea recuperar", 403
            try:
                
                return send_file(os.path.join("Imagenes"),nombreFoto, as_attachment=False) , 201
            except Error :
                    return "no se puede recuperar la foto", 404



class Publicaciones (Resource):
    def post(self):
        try: 
            publicacionaSubir = request.get_json()
            publicacionNueva = Publicacion(nombre_publicacion = publicacionaSubir['nombre_publicacion'],descripcion=publicacionaSubir['descripcion'],calificacion_general = publicacionaSubir['calificacion_general'], categoria = publicacionaSubir['categoria'],fecha_publicacion= datetime.now() )
            database.session.add(publicacionNueva)
            database.session.commit()
            return publicacionNueva, 201
        except Error:
            return 404


    def get (self):
        try:
            publicaciones = database.session.query(Publicacion)
            return publicaciones, 201
        except: Error
        return 404
    


    def get(self):
        try:
            publicacionBuscar =request.get_json()
            idpublicacion = publicacionBuscar['clave_publicacion']
            publicacionEncontrada = database.session.query(Publicacion).filter_by(clave_publicacion = idpublicacion)

            if not publicacionEncontrada:
                return publicacionEncontrada, 201
                
            return "No se encontro la publicacion", 404
        except: Error

        return "Excepcion encontrada", 404
        

    



class Comentarios(Resource):
    def post(self):
        try:

            comentarioSubir = request.get_json()
            comentarioNuevo = ComentarioUsuario(clave_publicacion = comentarioSubir['clave_publicacion'],clave_usuario = comentarioSubir['clave_usuario'], comentario = comentarioSubir['comentario'])
            database.session.add(comentarioNuevo)
            database.session.commit()
            return comentarioNuevo, 201
        except Error:
            return 404
          
    def get (self):
        try:
            publicacion = request.get_json()
            idpublicacion = publicacion['clave_publicacion']
            comentarioPublicacion = database.session.query(ComentarioUsuario).filter_by(clave_publicacion= idpublicacion)
            if not comentarioPublicacion:
                return comentarioPublicacion, 201

            return "No hay comentarios", 404 
        except Error:
            return "Exepcion Encontrada",404
          
class AgregarCalificacionPublicacion(Resource):
    def post(self):
        return 404