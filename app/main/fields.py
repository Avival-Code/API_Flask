from flask_restful import fields

usuario_fields = {
    'clave_usuario': fields.Integer,
    'nombres': fields.String,
    'apellidos': fields.String,
    'nombre_usuario': fields.String,
    'constrasena': fields.String,
    'correo_electronico': fields.String
}