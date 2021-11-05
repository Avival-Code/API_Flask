from flask_restful import reqparse

login_put_args = reqparse.RequestParser()
login_put_args.add_argument( "username", type=str, help="Se requiere un nombre de usuario", required=True )
login_put_args.add_argument( "password", type=str, help="Se requiere de una contraseña", required= True )
