import math
from app.core.event_engine.field.queries import ValueQuery
from app.core.models import User, Alert, Device, SensorData
from unittest.mock import MagicMock
import pytest

class TestValueQuery:
	@pytest.mark.parametrize('table', [(User, Alert, Device)])
	def test_ctor(self, table):
		"""Assert constructor properly raises exceptions"""
		mock_value = MagicMock()
		with pytest.raises(ValueError):
			score_function = ValueQuery(mock_value, mock_value, mock_value, table)

	@pytest.mark.parametrize('table, id_col, time_col, col, expected', [(SensorData, SensorData.plant_id, SensorData.time, SensorData.temperature, 10.85)])
	def test_query(self, session, table, id_col, time_col, col, expected):
		"""Assert query properly returns latest value"""
		query = ValueQuery(table, id_col, time_col, col)

		value = query.execute(1, session)
		assert math.isclose(value, expected, rel_tol=1e-2)
