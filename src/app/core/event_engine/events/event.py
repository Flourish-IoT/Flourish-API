from dataclasses import dataclass
from sqlalchemy.orm.scoping import ScopedSession

@dataclass
class Event:
	user_id: int
	session: ScopedSession