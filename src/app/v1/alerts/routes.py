from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('alerts', description='Alert related operations', path='/alerts')