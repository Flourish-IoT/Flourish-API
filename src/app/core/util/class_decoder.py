from json import JSONDecoder, JSONDecodeError
import inspect
from typing import Generic, TypeVar
import importlib

# TODO: whitelist valid serializeable classes?
T = TypeVar('T')
class ClassDecoder(JSONDecoder, Generic[T]):
  def __init__(self):
    JSONDecoder.__init__(self, object_hook=self.obj_hook)

  def obj_hook(self, dict: dict) -> T | dict:
    if ("__class__" in dict):
      # pop metadata values so the dict is left with only object params
      class_name = dict.pop("__class__")
      module_name = dict.pop("__module__")

      # dynamically import module and class
      # module = __import__(module_name)
      module = importlib.import_module(module_name)
      class_ = getattr(module, class_name)

      # enums must be handled differently
      if ("__enum_value__" in dict):
        value = dict["__enum_value__"]
        return class_(value)

      # use reflection to get constructor parameter information
      parameters = inspect.signature(class_.__init__).parameters.keys()

      # remove any unneccesary params
      dictKeys = list(dict.keys())
      for key in dictKeys:
        if key not in parameters:
          del dict[key]

      return class_(**dict)
    else:
      return dict