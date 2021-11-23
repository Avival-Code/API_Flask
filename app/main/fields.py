from flask_restful import fields

usuario_fields = {
    'clave_usuario': fields.Integer,
    'nombres': fields.String,
    'apellidos': fields.String,
    'nombre_usuario': fields.String,
    'constrasena': fields.String,
    'correo_electronico': fields.String
}

publicacion_fields = {
    'clave_publicacion': fields.Integer,
    'nombre_publicacion': fields.String,
    'descripcion': fields.String,
    'calificacion_general': fields.Float,
    'categoria': fields.Integer,
    'fecha_publicacion': fields.DateTime
}