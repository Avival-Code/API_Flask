from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

database = SQLAlchemy()
guard = Praetorian()
limiter = Limiter( key_func=get_remote_address, default_limits=[ "200 per day", "50 per hour" ] )