# Flask configuration
import os

class Config:
	SECRET_KEY = ''

	SQLALCHEMY_DATABASE_URI = ''
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ENGINE_OPTIONS = {
		'pool_size': 5,
		'future': True
	}

	RESTX_ERROR_404_HELP = False

class ProdConfig(Config):
	FLASK_ENV = 'production'
	DEBUG = False
	TESTING = False

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class DevConfig(Config):
	FLASK_ENV = 'development'
	DEBUG = True
	TESTING = True

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class LocalConfig(Config):
	FLASK_ENV = 'local'
	DEBUG = True
	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:password@localhost/postgres'
	SQLALCHEMY_ENGINE_OPTIONS = {
		'pool_size': 2,
		'future': True
	}

class TestConfig(Config):
	FLASK_ENV = 'test'
	DEBUG = True
	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'sqllite://postgres:password@localhost/postgres'