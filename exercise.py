import random
import datetime

print(random.random())

print(random.randint(1,10))
random.seed(datetime.datetime.now())
print(random.random())