import random

NUM_TREES = 100
NUM_FLOWERS = 6
RADIUS = 200
CENTER_X = 400
CENTER_Y = 100
TYPES = ["pine", "dead_tree", "oak", "fern", "stump"]
FLOWERS = ["yellow_flowers", "pink_flowers"]
a = 10
PALMS = 5
ROCKS = 12
STUMPS = 12
OTHER_TILES = 20
tiles = ["sand", "dirt", "long_grass", "daisies", "hill"]



file = open("large_world_spec", "w")

file.write("10 12 \n")

for i in xrange(0, OTHER_TILES):
    file.write(tiles[random.randint(0, 4)])
    file.write(" : ")
    file.write(str(random.randint(0, 11)))
    file.write(" ")
    file.write(str(random.randint(0, 9)))
    file.write("\n")

for i in xrange(0, PALMS):
    file.write("palm")
    file.write(" : ")
    file.write(str(random.randint(0, 640)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, 768)))
    file.write("\n")
    
for i in xrange(0, ROCKS):
    file.write("rocks")
    file.write(" : ")
    file.write(str(random.randint(0, 640)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, 768)))
    file.write("\n")
    
for i in xrange(0, STUMPS):
    file.write("stump")
    file.write(" : ")
    file.write(str(random.randint(0, 640)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, 768)))
    file.write("\n")

for i in xrange(0, NUM_TREES):
    file.write(TYPES[random.randint(0, 4)])
    file.write(" : ")
    file.write(str(CENTER_X + random.randint(0, RADIUS)))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, RADIUS)))
    file.write("\n")

for i in xrange(0 , NUM_FLOWERS):
    file.write(FLOWERS[random.randint(0, 1)])
    file.write(" : ")
    file.write(str(CENTER_X + RADIUS + a))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, RADIUS)))
    file.write("\n")
    
for i in xrange(0 , NUM_FLOWERS):
    file.write(FLOWERS[random.randint(0, 1)])
    file.write(" : ")
    file.write(str(CENTER_X - a))
    file.write(" ")
    file.write(str(CENTER_Y + random.randint(0, RADIUS)))
    file.write("\n")
    
for i in xrange(0 , NUM_FLOWERS):
    file.write(FLOWERS[random.randint(0, 1)])
    file.write(" : ")
    file.write(str(CENTER_X + random.randint(0, RADIUS)))
    file.write(" ")
    file.write(str(CENTER_Y + RADIUS + a))
    file.write("\n")
    
for i in xrange(0 , NUM_FLOWERS):
    file.write(FLOWERS[random.randint(0, 1)])
    file.write(" : ")
    file.write(str(CENTER_X + random.randint(0, RADIUS)))
    file.write(" ")
    file.write(str(CENTER_Y - a))
    file.write("\n")
     