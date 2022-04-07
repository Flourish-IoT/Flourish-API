from datetime import datetime, timedelta
from unittest import mock
from app.common.utils.polymorphic_schema import PolymorphicSchema
from app.core.event_engine import Field
from app.core.event_engine.events import SensorDataEvent
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, plant_value_score
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
		print(res)
