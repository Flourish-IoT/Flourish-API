from abc import ABC, abstractmethod
import logging
from typing import Any, List, TypeVar, Generic
from .actions import Action

T = TypeVar('T')

class Trigger(ABC, Generic[T]):
	actions: List[Action]

	def __init__(self, actions: List[Action]) -> None:
		self.actions = actions

	@abstractmethod
	def execute(self, value: T):
		raise NotImplementedError

	def _execute_actions(self):
		for action in self.actions:
			action.execute()