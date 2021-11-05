from . import database

class Usuario( database.Model ):
    clave_usuario = database.Column( database.Integer, primary_key=True, autoincrement=True )
    nombres = database.Column( database.String( 25 ), nullable=False )
    apellidos = database.Column( database.String( 50 ), nullable=False )
    nombre_usuario = database.Column( database.String( 50 ), nullable=False, unique=True )
    constrasena = database.Column( database.Text, nullable=False )
    correo_electronico = database.Column( database.String( 50 ), nullable=False )

    @property
    def identity( self ):
        return self.clave_usuario

    @property
    def rolenames( self ):
        return []

    @property
    def password( self ):
        return self.constrasena

    @classmethod
    def lookup( cls, username ):
        return cls.query.filter_by( clave_usuario=username ).one_or_none()

    @classmethod
    def identify( cls, id ):
        return cls.query.filter_by( clave_usuario=id ).one_or_none()

    def __repr__( self ):
        return f"Usuario( nombre_usuario = { self.nombre_usuario }, contrasena = { self.constrasena } )"