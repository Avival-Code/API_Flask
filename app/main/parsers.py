from datetime import date
from typing import Text
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

publicaciones_favoritas_put_args = reqparse.RequestParser()
publicaciones_favoritas_put_args.add_argument( "clave_usuario", type=int, help="Se requiere la clave del usuario", required=True )
publicaciones_favoritas_put_args.add_argument( "clave_publicacion", type=int, help="Se requiere la clave de la publicación", required=True )

usuarios_favoritos_put_args = reqparse.RequestParser()
usuarios_favoritos_put_args.add_argument( "clave_usuario", type=int, help="Se requiere la clave del usuario", required=True )
usuarios_favoritos_put_args.add_argument( "clave_usuario_favorito", type=int, help="Se requiere la clave del usuario favorito", required=True )

comentario_usuario_put_args = reqparse.RequestParser()
comentario_usuario_put_args.add_argument("clave_publicacion", type=int,help="Es necesaria la clave de la publicacion", required=True )
comentario_usuario_put_args.add_argument("clave_usuario", type=int,help="Es necesaria la clave del usuario", required=True )
comentario_usuario_put_args.add_argument("comentario", type=str,help="Es necesario el comentario", required=True )

publicacion_put_args = reqparse.RequestParser()
publicacion_put_args.add_argument( "nombre_publicacion", type=str, help="Es necesario el nombre de la publicacion", required=True )
publicacion_put_args.add_argument( "descripcion",type=str,help="Es necesaria la descripcion de la publicacion", required=True )
publicacion_put_args.add_argument( "calificacion_general", type=float, help="En nesesaria la calificacion de la publicacion", required=False )
publicacion_put_args.add_argument( "categoria", type=int, help="Es necesaria la categoria de la publicacion", required=True )
publicacion_put_args.add_argument( "fecha_publicacion", type=date, help="Es necesaria la fecha de la publicacion", required=False )
publicacion_put_args.add_argument( "multimedia", type=Text, help="Es necesario el archivo", required=True )

calificacion_publicacion_put_args = reqparse.RequestParser()
calificacion_publicacion_put_args.add_argument( "clave_publicacion", type=int,help="Es necesaria la clave de publicacion", required=True )
calificacion_publicacion_put_args.add_argument( "clave_usuario", type=int, help= "Es necesaria la clave del usuario", required=True )
calificacion_publicacion_put_args.add_argument( "calificacion", type=float, help="Es necesaria la calificacion",required=True )

multimedia_put_args = reqparse.RequestParser()
multimedia_put_args.add_argument( "clave_publicacion", type= int, help="Es necesaria la clave de la publicacion", required=True )
multimedia_put_args.add_argument( "multimedia", type=Text, help="Es necesario el archivo", required=True )



