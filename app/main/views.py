from flask import make_response, render_template, jsonify
from flask_restful import Resource

class MainPage( Resource ):
    def get( self ):
        headers = { 'Content-Type': 'Text/html' }
        return make_response( render_template( 'main_page.html' ), 200, headers )

class Login( Resource ):
    def post( self ):
        login_args = login_put_args.parse_args()
        user = guard.authenticate( args[ 'username' ], args[ 'password' ] )
        token = guard.encode_jwt_token( user )
        return jsonify( { 'clave_usuario': user.clave_usuario, 'access_token': token } )