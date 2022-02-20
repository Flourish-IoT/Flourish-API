import math
from app.core.models import SensorData
from app.core.event_engine.events.field.queries import ValueQuery
from app.core.event_engine.events.field import Field
from unittest.mock import MagicMock
import pytest
import unittest.mock as mock

# TODO: create integration test
# class TestField:
# 	# @pytest.mark.parametrize('table', [(User, Alert, Device)])
# 	# def test_ctor(self, table):
# 	# 	"""Assert constructor properly raises exceptions"""
# 	# 	mock_value = MagicMock()
# 	# 	with pytest.raises(ValueError):
# 	# 		score_function = ValueQuery(mock_value, mock_value, mock_value, table)

# 	def test_field(self, session):
# 		query = ValueQuery(SensorData, SensorData.plant_id, SensorData.time)
# 		field = Field(SensorData.humidity, query)

# 		field.get_value(1, session)