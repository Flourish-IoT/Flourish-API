from app.core.event_engine.post_process_functions import ValueRating, target_value_score, score
from app.core.event_engine.post_process_functions.target_value_score import _get_plant_min_max
from unittest.mock import MagicMock
import pytest

from app.core.models import Plant, PlantType

class TestTargetValueScore:
	@pytest.mark.parametrize('min, max, value, expected', [
		( 1, 3, 2, ValueRating.Nominal ),
		(1.2, 1.4, 1.5, ValueRating.TooHigh),
		(1, 5, -2, ValueRating.TooLow),
		(None, None, -2, ValueRating.NoRating)
		]
	)
	def test_score(self, min, max, value, expected):
		# TODO: expand this
		"""Assert score function properly scores values"""
		rating = score(value, min, max)
		assert rating == expected

class TestPlantValueScore:
	@pytest.mark.parametrize('plant_type, min_col, max_col, expected', [
			(PlantType(minimum_light = 20, maximum_light = 40), PlantType.minimum_light, PlantType.maximum_light, (20, 40)),
			(PlantType(minimum_temperature = 60, maximum_temperature = 80), PlantType.minimum_temperature, PlantType.maximum_temperature, (60, 80)),
			(PlantType(minimum_humidity = 20, maximum_humidity = 70), PlantType.minimum_humidity, PlantType.maximum_humidity, (20, 70)),
			(PlantType(minimum_soil_moisture = 10, maximum_soil_moisture = 90), PlantType.minimum_soil_moisture, PlantType.maximum_soil_moisture, (10, 90)),
		]
	)
	def test_get_min_max(self, plant_type, min_col, max_col, expected):
		"""Test that get_min_max returns the correct values"""
		plant = Plant(plant_type=plant_type)
		min_max = _get_plant_min_max(plant, min_col, max_col)

		assert min_max == expected

	@pytest.mark.parametrize('min_col, max_col', [
			(PlantType.minimum_light, PlantType.maximum_light),
			(PlantType.minimum_temperature, PlantType.maximum_temperature),
			(PlantType.minimum_humidity, PlantType.maximum_humidity),
			(PlantType.minimum_soil_moisture, PlantType.maximum_soil_moisture),
		]
	)
	def test_get_min_max_no_plant_type(self, min_col, max_col):
		"""Test that get_min_max returns ( None, None ) if no plant_type is associated with plant"""
		plant = Plant(plant_type=None)
		min_max = _get_plant_min_max(plant, min_col, max_col)

		assert min_max == (None, None)