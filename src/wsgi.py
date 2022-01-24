import logging
from flask.app import Flask
from app import create_app, Environment
from argparse import ArgumentParser


def configure_app():
	parser = ArgumentParser(description='Flourish Backend API')
	parser.add_argument('-c', type=str, choices=Environment.get_environments(), default=Environment.dev.env, dest='config', help='Config file to use')
	args, _ = parser.parse_known_args()

	env = Environment[ args.config ]
	app = create_app(env)

	return app

# gunicorn entrypoint
def create_gunicorn(*args, **kwargs):
	# parse arguments passed in through kwargs, gunicorn CLI args are useless
	import sys
	for k, v in kwargs.items():
		# if single letter, assume short form argument
		sys.argv.append(f'{"-" if len(k) == 1 else "--"}{k}')
		sys.argv.append(v)

	app = configure_app()

	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	return app

if __name__ == '__main__':
	app = configure_app()
	app.run(host='0.0.0.0')