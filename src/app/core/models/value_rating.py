from enum import IntEnum

class ValueRating(IntEnum):
	NoRating = -1
	TooLow = 1,
	Low = 2,
	Nominal = 3
	High = 4,
	TooHigh = 5,