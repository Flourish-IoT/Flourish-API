# hack to make pytest import correctly
from datetime import datetime
from unittest.mock import MagicMock
import pytest
from app import Environment, db, create_app

@pytest.fixture(scope='session')
def app():
	# TODO: this should be Environment.test when we figure out how it will work
	a = create_app(Environment.local)
	with a.app_context():
		yield

	return

@pytest.fixture
def session(app):
	return db.session

def pytest_addoption(parser):
	parser.addoption('--db', action="store_true", default=False, help='Run tests against database')

def pytest_configure(config):
	config.addinivalue_line("markers", "db: Mark tests as db to run")

def pytest_collection_modifyitems(config, items):
	if config.getoption('--db'):
		# --db passed, do not skip tests that require the database
		return

	skip_db = pytest.mark.skip(reason='Need --db option to run')
	for item in items:
		if 'db' in item.keywords:
			item.add_marker(skip_db)