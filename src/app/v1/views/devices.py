from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('devices', description='Device related operations', path='/devices')