from flask_restful import reqparse

login_put_args = reqparse.RequestParser()
login_put_args.add_argument( "username", type=str, help="Se requiere un nombre de usuario", required=True )
login_put_args.add_argument( "password", type=str, help="Se requiere de una contraseña", required= True )

usuario_put_args = reqparse.RequestParser()
usuario_put_args.add_argument( "nombres", type=str, help="Los nombres son requeridos", required=True )
usuario_put_args.add_argument( "apellidos", type=str, help="Los apellidos son requeridos", required=True )
usuario_put_args.add_argument( "nombre_usuario", type=str, help="El nombre de usuario es requerido", required=True )
usuario_put_args.add_argument( "contrasena", type=str, help="La contraseña es requerida", required=True )
usuario_put_args.add_argument( "correo_electronico", type=str, help="El correo es requerido", required=True )