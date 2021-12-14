import re

def login_input_validation( login_input ):
    username = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,25}$)", login_input[ 'username' ] ) )
    password = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,20}$)", login_input[ 'password' ] ) )
    return ( username and password )

def user_input_validation( user_input ):
    nombres = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", user_input[ 'nombres' ] ) )
    apellidos = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", user_input[ 'apellidos' ] ) )
    usuario = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,25}$)", user_input[ 'nombre_usuario' ] ) )
    contrasena = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,20}$)", user_input[ 'contrasena' ] ) )
    correo = bool( re.fullmatch( r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", user_input[ 'correo_electronico' ] ) )
    return ( nombres and apellidos and usuario and contrasena and correo )

def publication_input_validation( publication_input ):
    nombre = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", publication_input[ 'nombre_publicacion' ] ) )
    descripcion = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s\.]{3,200}$)", publication_input[ 'descripcion' ] ) )
    categoria = bool( re.fullmatch( r"(^[0-9]{1,2}$)", str( publication_input[ 'categoria' ] ) ) )
    return ( nombre and descripcion and categoria )

def search_input_validation( busqueda ):
    return bool( re.fullmatch( r"(^[a-zA-Z0-9\s\_\-]{4,25}$)", busqueda ) )

def id_validation( id ):
    return bool( re.fullmatch( r"(^[0-9]{1,4}$)", str( id ) ) )

def comment_input_validation( comentario_input ):
    clave_publicacion = id_validation( comentario_input[ 'clave_publicacion' ] )
    clave_usuario = id_validation( comentario_input[ 'clave_usuario' ] )
    comentario = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{10,100}$)", comentario_input[ 'comentario' ] ) )
    return ( clave_publicacion and clave_usuario and comentario )
