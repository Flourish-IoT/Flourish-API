# from app.core.event_engine.queries import Query
# from unittest.mock import MagicMock
# import pytest
# from sqlalchemy import Column
# from sqlalchemy.orm import Session


# def _get_mock_query(v):
# 	mock =  MagicMock(Query)
# 	mock.execute.return_value = v
# 	return mock

# class TestEventEngine:
# 	# @pytest.mark.parametrize('expected, queries', [
# 	# 	({'foo': 5}, { 'foo': _get_mock_query(5) }),
# 	# 	({'foo': 5, 'bar': 20}, { 'foo': _get_mock_query(5), 'bar': _get_mock_query(20) }),
# 	# 	({'foo': 20}, { 'foo': _get_mock_query(5), 'foo': _get_mock_query(20) }),
# 	# ])
# 	def test_handle(self):
# 		"""Ensure get_value returns the proper response"""
# 		pass
# 		# mock_col = MagicMock(Column)

# 		# field = Field(mock_col, queries)
# 		# mock_session = MagicMock(Session)
# 		# value = field.get_value(1, mock_session)

# 		# # make sure queries are called with correct values
# 		# for query in queries.values():
# 		# 	query.execute.assert_called_once_with(1, mock_col, mock_session)

# 		# # make sure returned value is correct
# 		# assert value == expected

