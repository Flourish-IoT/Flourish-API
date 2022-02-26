from typing import Any
from sqlalchemy import Column
from sqlalchemy.orm import registry
from sqlalchemy.orm.decl_api import DeclarativeMeta
from copy import deepcopy

from app.core.util import PrettyPrint

mapper_registry = registry()

class BaseModel(PrettyPrint, metaclass=DeclarativeMeta):
    __abstract__ = True

    # these are supplied by the sqlalchemy2-stubs, so may be omitted
    # when they are installed
    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor

    def get_column_value(self, column: Column | Any) -> Any:
        """Dynamically get a value using a reference to a column
        Usage::

            class Foo(BaseModel):
                bar = cast(int, Column(Integer))

            foo = Foo(bar=2)
            print(foo.get_column_value(Foo.bar))
            2

        Args:
                column (Column | Any): Column to get value from

        Returns:
                Any: Value of column
        """
        return getattr(self, column.property.key)

    def __eq__(self, other):
        # from https://stackoverflow.com/q/39043003
        classes_match = isinstance(other, self.__class__)
        a, b = deepcopy(self.__dict__), deepcopy(other.__dict__)
        #compare based on equality our attributes, ignoring SQLAlchemy internal stuff
        a.pop('_sa_instance_state', None)
        b.pop('_sa_instance_state', None)
        attrs_match = (a == b)
        return classes_match and attrs_match

    def __ne__(self, other):
        return not self.__eq__(other)