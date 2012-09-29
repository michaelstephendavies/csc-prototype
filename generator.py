import random

NUM_TREES = 125
RADIUS = 325
CENTER_X = 600
CENTER_Y = 100
TYPES = ["pine", "dead_tree", "oak"]

file = open("large_world_spec", "w")

file.write("15 15\n")

for i in xrange(0, NUM_TREES):
    file.write(TYPES[random.randint(0, 2)])
    file.write(" : ")
    file.write(str(CENTER_X + random.randint(0, RADIUS)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, RADIUS)))
    file.write("\n")
     