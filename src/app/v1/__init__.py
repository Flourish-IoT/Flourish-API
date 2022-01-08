from flask import Blueprint, blueprints
from .users.routes import api as user_api
from flask_restx import Api

# create v1 api
blueprint = Blueprint('api', __name__, url_prefix='/v1')
api = Api(blueprint, title='Flourish API', version='1.0', description='API to interact with the Flourish backend')

# mount v1 endpoints
api.add_namespace(user_api)