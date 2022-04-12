from datetime import datetime, timedelta
from unittest import mock
from app.common.schemas.dynamic_schema import DynamicSchema
from app.core.event_engine import Field
from app.core.event_engine.events import SensorDataEvent
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger
from app.core.models import Plant, SensorData, SeverityLevelEnum, Alert, PlantType
from app.core.models.event_engine import EventHandlerInformation
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm.scoping import ScopedSession
from freezegun import freeze_time


class TestSensorDataEventHandler:
	def test_from_event_handler(self, default_handler):
		res = EventHandlerInformation.from_event_handler(default_handler)

		assert res.config == {
			"triggers": [
				{
					"AndTrigger": {
						"triggers": [
							{
								"EqualsTrigger": {
									"value": {
										"ValueRating": "TooLow"
									},
									"field": "value",
									"actions": []
								}
							},
							{
								"LessThanTrigger": {
									"value": {
										"int": 0
									},
									"field": "slope",
									"actions": []
								}
							}
						],
						"field": None,
						"actions": [
							1
						]
					}
				},
				{
					"AndTrigger": {
						"triggers": [
							{
								"EqualsTrigger": {
									"value": {
										"ValueRating": "Low"
									},
									"field": "value",
									"actions": []
								}
							}
						],
						"field": None,
						"actions": [
							2
						]
					}
				},
				{
					"AndTrigger": {
						"triggers": [
							{
								"EqualsTrigger": {
									"value": {
										"ValueRating": "High"
									},
									"field": "value",
									"actions": []
								}
							}
						],
						"field": None,
						"actions": [
							3
						]
					}
				},
				{
					"AndTrigger": {
						"triggers": [
							{
								"EqualsTrigger": {
									"value": {
										"ValueRating": "TooHigh"
									},
									"field": "value",
									"actions": []
								}
							}
						],
						"field": None,
						"actions": [
							4
						]
					}
				}
			],
			"field": {
				"Field": {
					"queries": {
						"value": {
							"ValueQuery": {
								"post_processor": {
									"PlantValueScore": {
										"max_col": {
											"column": "maximum_temperature",
											"table": "app.core.models.plant_type.PlantType"
										},
										"min_col": {
											"column": "minimum_temperature",
											"table": "app.core.models.plant_type.PlantType"
										}
									}
								},
								"order_column": {
									"column": "time",
									"table": "app.core.models.sensor_data.SensorData"
								},
								"id_column": {
									"column": "plant_id",
									"table": "app.core.models.sensor_data.SensorData"
								},
								"table": "SensorData"
							}
						},
						"slope": {
							"SlopeQuery": {
								"time_start": 10800,
								"post_processor": None,
								"time_end": None,
								"id_column": {
									"column": "plant_id",
									"table": "app.core.models.sensor_data.SensorData"
								},
								"table": "SensorData"
							}
						}
					},
					"field": {
						"column": "temperature",
						"table": "app.core.models.sensor_data.SensorData"
					}
				}
			},
			"type": "SensorDataEventHandler"
		}