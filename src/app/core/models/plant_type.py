from email.mime import image
from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET

class PlantType(BaseModel):
    __tablename__ = 'plant_types'

    plant_type_id = cast(int, Column(
        Integer,
        primary_key = True
    ))

    scientific_name = cast(str, Column(
        String
    ))

    minimum_light = cast(int, Column(
        Integer
    ))

    maximum_light = cast(int, Column(
        Integer
    ))

    minimum_temperature = cast(float, Column(
        Float
    ))

    maximum_temperature = cast(float, Column(
        Float
    ))

    minimum_humidity = cast(float, Column(
        Float
    ))

    maximum_humidity = cast(float, Column(
        Float
    ))

    minimum_soil_moisture = cast(float, Column(
        Float
    ))

    maximum_soil_moisture = cast(float, Column(
        Float
    ))

    image = cast(str, Column(
        String
    ))
