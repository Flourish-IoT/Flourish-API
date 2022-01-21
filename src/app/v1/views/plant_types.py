from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('plant_types', description='Plant Type related operations', path='/plant_types')