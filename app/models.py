from . import database

class Usuario( database.Model ):
    clave_usuario = database.Column( database.Integer, primary_key=True, autoincrement=True )
    nombres = database.Column( database.String( 25 ), nullable=False )
    apellidos = database.Column( database.String( 50 ), nullable=False )
    nombre_usuario = database.Column( database.String( 50 ), nullable=False, unique=True )
    contrasena = database.Column( database.Text, nullable=False )
    correo_electronico = database.Column( database.String( 50 ), nullable=False )

    @property
    def identity( self ):
        return self.clave_usuario

    @property
    def rolenames( self ):
        return []

    @property
    def password( self ):
        return self.contrasena

    @classmethod
    def lookup( cls, username ):
        return cls.query.filter_by( clave_usuario=username ).one_or_none()

    @classmethod
    def identify( cls, id ):
        return cls.query.filter_by( clave_usuario=id ).one_or_none()

    def __repr__( self ):
        return f"Usuario( nombres = { self.nombres }, apellidos = { self.apellidos }, nombre_usuario = { self.nombre_usuario }, contrasena = { self.contrasena }, correo_electronico = { self.correo_electronico } )"

class Publicacion( database.Model ):
    clave_publicacion = database.Column( database.Integer, primary_key=True, autoincrement=True )
    nombre_publicacion = database.Column( database.String( 50 ), nullable=False )
    descripcion = database.Column( database.String( 200 ), nullable=False )
    calificacion_general = database.Column( database.Float )
    categoria = database.Column( database.Integer, nullable=False )
    fecha_publicacion = database.Column( database.Date )

    def __repr__( self ):
        return f"Publicacion( clave_publicacion = { self.clave_publicacion }, nombre_publicacion = { self.nombre_publicacion }, descripcion = { self.descripcion }, calificacion_general = { self.calificacion_general }, categoria = { self.categoria }, fecha_publicacion = { self.fecha_publicacion },  )"

class ComentarioUsuario( database.Model ):
    clave_comentario = database.Column( database.Integer, primary_key=True, autoincrement=True )
    clave_publicacion = database.Column( database.Integer, nullable=False )
    clave_usuario = database.Column( database.Integer, nullable=False )
    comentario = database.Column( database.String( 200 ), nullable=False )

    def __repr__( self ):
        return f"ComentarioUsuario( clave_comentario = { self.clave_comentario }, clave_publicacion = { self.clave_publicacion }, clave_usuario = { self.clave_usuario }, comentario = { self.comentario } )"

class CalificacionUsuario( database.Model ):
    clave_calificacion = database.Column( database.Integer, primary_key=True, autoincrement=True )
    clave_publicacion = database.Column( database.Integer )
    clave_usuario = database.Column( database.Integer )
    calificacion = database.Column( database.Float )

    def __repr__( self ):
        return f"CalificacionUsuario( clave_calificacion = { self.clave_calificacion }, clave_publicacion = { self.clave_publicacion }, clave_usuario = { self.clave_usuario }, calificacion = { self.calificacion } )"

