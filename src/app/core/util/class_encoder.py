from enum import Enum
from json import JSONEncoder

class ClassEncoder(JSONEncoder):
  def default(self, obj):
    """
    Takes in an object and returns a dictionary representation with object metadata
    """

    # add metadata
    obj_dict = {
      "__class__": obj.__class__.__name__,
      "__module__": obj.__module__
    }

    # add extra enum metadata
    if (isinstance(obj, Enum)):
      obj_dict["__enum_value__"] = obj.value
    else:
      # add object properties
      obj_dict.update(obj.__dict__)

    return obj_dict