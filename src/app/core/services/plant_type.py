from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, select
from typing import List
import logging

from app.core.models.plant_type import PlantType

def get_plant_type(plant_type_id: int, session: ScopedSession):
    plant_type= session.get(PlantType, plant_type_id)

    if plant_type is None:
        raise NotFoundError(f'Could not find plant type with id: {plant_type_id}')

    return plant_type

def get_all_plant_types(session: ScopedSession):
    query = select(PlantType)

    try:
        plant_types: List[PlantType] = session.execute(query).scalars().all()
    except Exception as e:
        logging.error(f'Failed to get plant types for user')
        logging.exception(e)
        raise e

    return plant_types



