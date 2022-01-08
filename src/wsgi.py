from ast import parse
from enum import Enum
from app import create_app, Environment
from argparse import ArgumentParser


if __name__ == '__main__':
	parser = ArgumentParser(description='Flourish Backend API')
	parser.add_argument('-c', type=str, choices=Environment.get_environments(), default=Environment.dev.env, dest='config', help='Config file to use')
	args = parser.parse_args()

	config = Environment[ args.config ]

	app = create_app(config)
	app.run()

else:
	# TODO: handle gunicorn
	app = create_app(Environment.dev)