# Flask configuration
class Config:
	SECRET_KEY = ''

class ProdConfig(Config):
	FLASK_ENV = 'production'
	DEBUG = False
	TESTING = False

class DevConfig(Config):
	FLASK_ENV = 'development'
	DEBUG = True
	TESTING = True