from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

class Environment(Enum):
	test = 'test', 'config.TestConfig'
	local = 'local', 'config.LocalConfig'
	dev = 'dev', 'config.DevConfig'
	prod = 'prod', 'config.ProdConfig'

	def __init__(self, env, config) -> None:
			self.env = env
			self.config = config

	@classmethod
	def get_environments(cls):
		"""
		Returns all valid environment names
		"""
		# extract environment name from each entry
		return list(map(lambda x: x.env, list(cls)))

db = SQLAlchemy()
def create_rest_app(env: Environment = Environment.local) -> Flask:
	"""
	Create Flask application for a specific environment
	"""
	print(f'Creating application with environment "{env.env}", config: "{env.config}"')
	app = Flask(__name__, instance_relative_config=False)
	CORS(app)
	app.config.from_object(env.config)

	db.init_app(app)

	with app.app_context():
		# Mount versioned endpoints
		from .protocols.http.v1 import blueprint as v1
		app.register_blueprint(v1)

		return app
