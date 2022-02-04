from .base_model import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String

class Plant(BaseModel):
	__tablename__ = 'plants'

	plant_id = Column(
		Integer,
		primary_key = True
	)
	user_id = Column(
		Integer,
		ForeignKey("users.user_id") 
	)