from datetime import datetime, timedelta
from typing import cast
from unittest import mock
# from app.common.schemas.dynamic_schema import DynamicSchema
# from app.core.event_engine import Field
# from app.core.event_engine.events import SensorDataEvent
# from app.core.event_engine.queries import ValueQuery, SlopeQuery
# from app.core.event_engine.post_process_functions import ValueRating
# from app.core.event_engine.handlers import SensorDataEventHandler
# from app.core.event_engine.actions import GeneratePlantAlertAction
# from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger
# from app.core.models import Plant, SensorData, SeverityLevelEnum, Alert, PlantType
# from app.core.models.event_engine import EventHandlerInformation
# from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm.scoping import ScopedSession

from app.core.models.event_engine.event_handler_information import EventHandlerInformation
from app.core.services.event_handler_service import create_event_handler, delete_event_handler, get_event_handlers, delete_event_handler
from app.common.schemas.dynamic_field import DynamicField
from app.common.schemas.dynamic_schema import DynamicSchema
from app.common.schemas.type_field import TypeField
from app.core.event_engine import Field
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, PlantValueScore
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger, GreaterThanTrigger
from app.core.models import Plant, SensorData, SeverityLevelEnum, PlantType


class TestEventHandlerService:
	@pytest.fixture
	def unregistered_handler(self):
		return SensorDataEventHandler(
			Field(
				SensorData.temperature, {
					'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, PlantValueScore(PlantType.minimum_temperature, PlantType.maximum_temperature)),
					'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
				}
			),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						LessThanTrigger(field='slope', value=0)
					],
					[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						GreaterThanTrigger(field='slope', value=0)
					],
					[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				)
			]
		)

	# @pytest.mark.db
	def test_get_event_handlers(self, session, unregistered_handler):
		# create new event handler
		handler_id = create_event_handler(unregistered_handler, session, plant_id=1)
		assert handler_id is not None

		# ensure 1 handler is returned
		handlers = get_event_handlers(1, cast( Column[Integer], EventHandlerInformation ).plant_id, session)
		assert len(handlers) == 1

		# for handler in handlers:
		# 	handler.handle(event)

		# cleanup handler
		delete_event_handler(handler_id, session)

		# ensure handler is deleted
		handlers = get_event_handlers(1, cast( Column[Integer], EventHandlerInformation ).plant_id, session)
		assert len(handlers) == 0