from flask import Blueprint, blueprints
from .users.routes import api as user_api
from .plants.routes import api as plant_api
from .plant_types.routes import api as plant_type_api
from .devices.routes import api as device_api
from .collections.routes import api as collection_api
from .alerts.routes import api as alert_api
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