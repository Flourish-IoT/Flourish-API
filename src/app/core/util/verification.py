import random
import math

def verify_code():
  ## storing strings in a list
  digits = [i for i in range(0, 10)]
  random_str = ""

  ## generating a random index
  ## multiply with 10 to generate a number between 0 and 10 not including 10
  for i in range(4):
    index = math.floor(random.random()*10)
    random_str += str(digits[index])

  ## displaying the random string
  return random_str