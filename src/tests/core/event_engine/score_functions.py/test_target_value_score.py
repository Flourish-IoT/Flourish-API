from app.core.event_engine.field.score_functions import ValueRating, TargetValueScoreFunction
from unittest.mock import MagicMock
import pytest

class TestTargetValueScore:
	@pytest.mark.parametrize('min, max', [(3, 1), (2, -2), (ValueRating.High, ValueRating.Low)])
	def test_ctor(self, min, max):
		"""Assert constructor properly raises exceptions"""
		with pytest.raises(ValueError):
			score_function = TargetValueScoreFunction(min, max)

	@pytest.mark.parametrize('min, max, value, expected', [( 1, 3, 2, ValueRating.Nominal ), (1.2, 1.4, 1.5, ValueRating.TooHigh), (1, 5, -2, ValueRating.TooLow)])
	def test_score(self, min, max, value, expected):
		# TODO: expand this
		"""Assert score function properly scores values"""
		score_function = TargetValueScoreFunction(min, max)
		rating = score_function.score(value)
		assert rating == expected