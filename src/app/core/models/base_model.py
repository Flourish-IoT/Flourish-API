from typing import Any
from sqlalchemy import Column
from sqlalchemy.orm import registry
from sqlalchemy import MetaData
from sqlalchemy.orm.decl_api import DeclarativeMeta
from copy import deepcopy
from app.common.schemas import SerializableType

from app.core.util import PrettyPrint

meta = MetaData(naming_convention={
    "ix": "%(column_0_label)s_idx", # matches TimescaleDB naming scheme and avoids conflicts
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})
mapper_registry = registry(metadata=meta)

class BaseModel(PrettyPrint, SerializableType, metaclass=DeclarativeMeta):
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