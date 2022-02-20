# hack to make pytest import correctly
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