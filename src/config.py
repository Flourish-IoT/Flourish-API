# Flask configuration
import os

class Config:
	SQLALCHEMY_DATABASE_URI = ''
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	EMAIL_PASS = os.environ.get('EMAIL_PASS')
	SQLALCHEMY_ENGINE_OPTIONS = {
		'pool_size': 5,
		'future': True
	}

	RESTX_ERROR_404_HELP = False

class ProdConfig(Config):
	FLASK_ENV = 'production'
	DEBUG = False
	TESTING = False
	SECRET_KEY = os.environ.get('SECRET_KEY')

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class DevConfig(Config):
	FLASK_ENV = 'development'
	DEBUG = True
	TESTING = True
	SECRET_KEY = os.environ.get('SECRET_KEY')

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class LocalConfig(Config):
	FLASK_ENV = 'local'
	DEBUG = True
	TESTING = True
	SECRET_KEY='skbGoMfmaQzJTM'

	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:password@localhost/postgres'
	SQLALCHEMY_ENGINE_OPTIONS = {
		'pool_size': 2,
		'future': True,
		'echo': False
	}

class TestConfig(Config):
	FLASK_ENV = 'test'
	DEBUG = True
	TESTING = True
	SECRET_KEY='skbGoMfmaQzJTM'

	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'