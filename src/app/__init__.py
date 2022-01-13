from enum import Enum
from flask import Flask

class Environment(Enum):
	dev = 'dev', 'config.DevConfig'
	prod = 'prod', 'config.ProdConfig'

	def __init__(self, env, config) -> None:
			self.env = env
			self.config = config

	@classmethod
	def get_environments(self):
		"""
		Returns all valid environment names
		"""
		# extract environment name from each entry
		return list(map(lambda x: x.env, list(self)))

def create_app(env: Environment = Environment.dev) -> Flask:
	"""
	Create Flask application for a specific environment
	"""
	print(f'Creating application with environment "{env.env}", config: "{env.config}"')
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object(env.config)

	with app.app_context():
		# Mount versioned endpoints
		from .v1 import blueprint as v1
		app.register_blueprint(v1)

		return app