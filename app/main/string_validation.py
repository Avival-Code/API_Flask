import re

def user_input_validation( user_input ):
    matches = True
    print( matches )
    matches = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", user_input[ 'nombres' ] ) )
    matches = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", user_input[ 'apellidos' ] ) )
    matches = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,25}$)", user_input[ 'nombre_usuario' ] ) )
    matches = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,20}$)", user_input[ 'contrasena' ] ) )
    matches = bool( re.fullmatch( r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", user_input[ 'correo_electronico' ] ) )
    return matches

def publication_input_validation( publication_input ):
    matches = True
    matches = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s]{3,40}$)", publication_input[ 'nombre_publicacion' ] ) )
    matches = bool( re.fullmatch( r"(^[a-zA-ZÀ-ÿ\s\.]{3,200}$)", publication_input[ 'descripcion' ] ) )
    return matches

def search_input_validation( busqueda ):
    matches = bool( re.fullmatch( r"(^[a-zA-Z0-9\_\-]{4,25}$)", busqueda ) )
    return matches