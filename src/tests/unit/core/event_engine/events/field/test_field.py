from app.core.event_engine.events.field import Field
from unittest.mock import MagicMock
import pytest
from app.core.event_engine.events.field.queries import Query
from sqlalchemy import Column
from sqlalchemy.orm import Session

from app.core.event_engine.events.field.score_functions import MinMaxSource, TargetValueScoreFunction, ValueRating

def _get_mock_min_max_source(min, max):
	mock =  MagicMock(MinMaxSource)
	mock.get_min_max.return_value = (min, max)
	return mock

class TestField:
	@pytest.mark.parametrize('value, expected, score_function', [
		(5, 5, None),
		(5, ValueRating.Nominal, TargetValueScoreFunction(_get_mock_min_max_source(0, 6))),
	])
	def test_field(self, value, expected, score_function):
		mock_col = MagicMock(Column)
		mock_query = MagicMock(Query)
		mock_query.execute.return_value = value
		field = Field(mock_col, mock_query, score_function)

		mock_session = MagicMock(Session)
		value = field.get_value(1, mock_session)

		assert value == expected
