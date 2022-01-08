from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('plants', description='Plant related operations', path='/plants')