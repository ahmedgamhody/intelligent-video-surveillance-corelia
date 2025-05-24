from config import db_settings as dbs
from .db_control import DBControl


db_controller = DBControl(dbs)
