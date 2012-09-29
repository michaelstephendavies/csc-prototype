import random

NUM_TREES = 10
RADIUS = 250
CENTER_X = 100
CENTER_Y = 100
TYPES = ["pine", "dead_tree", "oak"]

file = open("cool_large", "w")

for i in xrange(0, NUM_TREES):
    file.write(TYPES[random.randint(0, 2)])
    file.write(" : ")
    file.write(str(CENTER_X + random.randint(0, RADIUS)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, RADIUS)))
    file.write("\n")
     