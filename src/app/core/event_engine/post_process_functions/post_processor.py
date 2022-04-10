from typing import Any
from app.common.schemas import SerializableClass
from app.core.event_engine.events import Event
from abc import ABC, abstractmethod
from marshmallow import Schema

class PostProcessorSchema(Schema):
	pass

class PostProcessor(ABC, SerializableClass):
	__schema__ = PostProcessorSchema

	@abstractmethod
	def process(self, value: Any, event: Event):
		raise NotImplementedError