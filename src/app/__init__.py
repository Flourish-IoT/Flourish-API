from enum import Enum
from flask import Flask
from flask_restx.api import Api

class Environment(Enum):
	dev = 'dev', 'config.DevConfig'
	prod = 'prod', 'config.ProdConfig'

	def __init__(self, env, config) -> None:
			self.env = env
			self.config = config

	@classmethod
	def get_environments(self):
		"""
		Returns all valid environments
		"""
		# extract environment name from each entry
		return list(map(lambda x: x.env, list(self)))

def create_app(env: Environment):
	"""
	Create Flask application
	"""
	print(f'Creating application with environment "{env.env}", config: "{env.config}"')
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object(env.config)

	with app.app_context():
		# Mount version endpoints
		from .v1 import blueprint as v1
		app.register_blueprint(v1)


		return app