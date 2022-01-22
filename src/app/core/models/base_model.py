from app import db
from flask_sqlalchemy.model import Model

BaseModel = db.make_declarative_base(Model)