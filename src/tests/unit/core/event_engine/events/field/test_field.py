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

def _get_mock_query(v):
	mock =  MagicMock(Query)
	mock.execute.return_value = v
	return mock

class TestField:
	@pytest.mark.parametrize('expected, queries', [
		({'foo': 5}, { 'foo': _get_mock_query(5) }),
		({'foo': 5, 'bar': 20}, { 'foo': _get_mock_query(5), 'bar': _get_mock_query(20) }),
		({'foo': 20}, { 'foo': _get_mock_query(5), 'foo': _get_mock_query(20) }),
	])
	def test_field(self, expected, queries: dict):
		"""Ensure get_value returns the proper response"""
		mock_col = MagicMock(Column)

		field = Field(mock_col, queries)
		mock_session = MagicMock(Session)
		value = field.get_value(1, mock_session)

		# make sure queries are called with correct values
		for query in queries.values():
			query.execute.assert_called_once_with(1, mock_col, mock_session)

		# make sure returned value is correct
		assert value == expected
