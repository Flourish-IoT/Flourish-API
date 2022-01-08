from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('collections', description='Collection related operations', path='/collections')