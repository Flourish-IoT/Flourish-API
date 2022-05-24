from unittest.mock import MagicMock
import pytest
import app.core.models as models
from flask.testing import FlaskClient

class TestUserViews:
	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user(self, client: FlaskClient, user, version):
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

	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user_nonexistant(self, client: FlaskClient, version):
		# user with ID 0 can never exist
		response = client.get(f'/{version}/users/0')

		assert response.status_code == 404
		assert response.json == {'message': 'Could not find user with ID: 0'}

	# TODO: test query params
	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user_devices(self, client: FlaskClient, user, device, version):
		response = client.get(f'/{version}/users/{user.user_id}/devices')

		assert response.status_code == 200
		assert response.json == [{
			'id': device.device_id,
			'deviceType': device.device_type.name,
			'deviceState': device.device_state.name,
			'model': device.model,
			'name': device.name
		}]

	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user_no_devices(self, client: FlaskClient, user, version):
		response = client.get(f'/{version}/users/{user.user_id}/devices')

		assert response.status_code == 200
		assert response.json == []

	# TODO: test query params
	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user_plants(self, client: FlaskClient, user, plant, version):
		response = client.get(f'/{version}/users/{user.user_id}/plants')

		assert response.status_code == 200
		assert response.json == [{
			'id': plant.plant_id,
			'name': plant.name,
			'image': plant.image,
			'gaugeRatings': plant.gauge_ratings,
			'sensorData': plant.sensor_data,
			'deviceId': plant.device_id,
			'plantType': plant.plant_type
		}]

	@pytest.mark.parametrize('version', ['v1'])
	def test_get_user_no_plants(self, client: FlaskClient, user, version):
		response = client.get(f'/{version}/users/{user.user_id}/plants')

		assert response.status_code == 200
		assert response.json == []
