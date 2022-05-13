from datetime import datetime, timedelta
from unittest import mock
from app.common.schemas.dynamic_schema import DynamicSchema
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
		handler_info = EventHandlerInformation()
		handler_info.update_config(default_handler)

		assert handler_info.config == {
			'queries': {'value': {'ValueQuery': {'order_column': {'column': 'time', 'table': 'app.core.models.sensor_data.SensorData'
				}, 'table': 'SensorData', 'column': {'column': 'temperature', 'table': 'app.core.models.sensor_data.SensorData'
				}, 'post_processor': {'PlantValueScore': {'min_col': {'column': 'minimum_temperature', 'table': 'app.core.models.plant_type.PlantType'
						}, 'max_col': {'column': 'maximum_temperature', 'table': 'app.core.models.plant_type.PlantType'
						}
					}
				}, 'id_column': {'column': 'plant_id', 'table': 'app.core.models.sensor_data.SensorData'
				}
			}
		}, 'slope': {'SlopeQuery': {'table': 'SensorData', 'column': {'column': 'temperature', 'table': 'app.core.models.sensor_data.SensorData'
				}, 'post_processor': None, 'time_end': None, 'time_start': 10800, 'id_column': {'column': 'plant_id', 'table': 'app.core.models.sensor_data.SensorData'
				}
			}
		}
	}, 'triggers': [
		{'AndTrigger': {'triggers': [
					{'EqualsTrigger': {'actions': [], 'field': 'value', 'value': {'ValueRating': 'TooLow'
							}
						}
					},
					{'LessThanTrigger': {'actions': [], 'field': 'slope', 'value': {'int': 0
							}
						}
					}
				], 'actions': [
					1
				]
			}
		},
		{'AndTrigger': {'triggers': [
					{'EqualsTrigger': {'actions': [], 'field': 'value', 'value': {'ValueRating': 'Low'
							}
						}
					}
				], 'actions': [
					2
				]
			}
		},
		{'AndTrigger': {'triggers': [
					{'EqualsTrigger': {'actions': [], 'field': 'value', 'value': {'ValueRating': 'High'
							}
						}
					}
				], 'actions': [
					3
				]
			}
		},
		{'AndTrigger': {'triggers': [
					{'EqualsTrigger': {'actions': [], 'field': 'value', 'value': {'ValueRating': 'TooHigh'
							}
						}
					}
				], 'actions': [
					4
				]
			}
		}
	], 'type': 'SensorDataEventHandler'
}
