from flask_restful import fields

from app.models import ComentarioUsuario

usuario_fields = {
    'clave_usuario': fields.Integer,
    'nombres': fields.String,
    'apellidos': fields.String,
    'nombre_usuario': fields.String,
    'correo_electronico': fields.String,
    'fecha_union': fields.DateTime,
    'foto_perfil': fields.String
}

publicacion_fields = {
    'clave_publicacion': fields.Integer,
    'clave_usuario': fields.Integer,
    'nombre_publicacion': fields.String,
    'descripcion': fields.String,
    'calificacion_general': fields.Float,
    'categoria': fields.Integer,
    'fecha_publicacion': fields.DateTime,
    'multimedia': fields.String
}

comentario_usuario_fields = {
    'clave_comentario': fields.Integer,
    'clave_publicacion': fields.Integer,
    'clave_usuario': fields.Integer,
    'comentario' : fields.String

}

calificacion_publicacion_fields = {
    'clave_calificacion': fields.Integer,
    'clave_publicacion': fields.Integer,
    'clave_usuarios': fields.Integer,
    'calificacion': fields.Float
}

multimedia_fields = {
    'clave_multimedia': fields.Integer,
    'clave_publicacion': fields.Integer,
    'multimedia': fields.String
}