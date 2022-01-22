from flask import Blueprint, blueprints
from .views.users import api as user_api
from .views.plants import api as plant_api
from .views.plant_types import api as plant_type_api
from .views.devices import api as device_api
from .views.collections import api as collection_api
from .views.alerts import api as alert_api

from flask_restx import Api

# create v1 api
blueprint = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(blueprint, title='Flourish API', version='1.0', description='API to interact with the Flourish backend')

# mount v1 endpoints
api.add_namespace(user_api)
api.add_namespace(plant_api)
api.add_namespace(plant_type_api)
api.add_namespace(device_api)
api.add_namespace(collection_api)
api.add_namespace(alert_api)