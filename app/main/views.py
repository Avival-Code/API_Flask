from flask import make_response, render_template, jsonify
from flask_restful import Resource, marshal_with, abort
from flask_praetorian import auth_required
from .. import database
from ..extensions import guard, limiter
from ..models import *
from .parsers import *
from .fields import *

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