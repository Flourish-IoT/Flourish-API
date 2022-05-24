from unittest.mock import MagicMock
import pytest
import app.core.models as models
from flask.testing import FlaskClient

class TestUserViews:
	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user(self, client: FlaskClient, user, version):
		"""Assert constructor properly raises exceptions"""
		response = client.get(f'/{version}/users/{user.user_id}')

		assert response.status_code == 200
		assert response.json == {
			'userId': user.user_id,
			'email': user.email,
			'username': user.username,
			# TODO: fix preferences
			# 'preferences': user.preferences
			'preferences': None
		}