import logging
from flask.app import Flask
from app import create_rest_app, Environment
from argparse import ArgumentParser


def configure_app():
	parser = ArgumentParser(description='Flourish Backend API')
	parser.add_argument('-c', '--config', type=str, choices=Environment.get_environments(), default=Environment.local.env, dest='config', help='Config file to use')
	parser.add_argument('-p', '--port', type=int, default=5000, dest='port', help='Port to run on. This can only be used when running Flask directly.')
	args, _ = parser.parse_known_args()

	env = Environment[ args.config ]
	app = create_rest_app(env)

	return app, args

# gunicorn entrypoint
def create_gunicorn(*args, **kwargs):
	# parse arguments passed in through kwargs, gunicorn CLI args are useless
	import sys
	for k, v in kwargs.items():
		# if single letter, assume short form argument
		sys.argv.append(f'{"-" if len(k) == 1 else "--"}{k}')
		sys.argv.append(v)

	app, _ = configure_app()

	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	return app

if __name__ == '__main__':
	app, args = configure_app()
	app.run(host='0.0.0.0', port=args.port)