import pygame

man_images = None

def get_man_images():
    # Returns list of lists where:
    #  first list is the animation frames for walking east
    #  second list is the animation frames for walking south
    #  second list is the animation frames for walking west
    #  second list is the animation frames for walking north

    global man_images
    
    if man_images == None:
        man_images = [
            # east
            [
                pygame.image.load('man_east_walk1.png').convert(),
                pygame.image.load('man_east_walk2.png').convert()
            ],
            # south
            [
                pygame.image.load('man_south_walk1.png').convert(),
                pygame.image.load('man_south_walk2.png').convert()
            ],
            # west
            [
                pygame.image.load('man_west_walk1.png').convert(),
                pygame.image.load('man_west_walk2.png').convert()
            ],
            # north
            [
                pygame.image.load('man_north_walk1.png').convert(),
                pygame.image.load('man_north_walk2.png').convert()
            ],
        ]
        
    return man_images

food_image = None

def get_food_image():
    global food_image

    if food_image == None:
        food_image = pygame.image.load('small_food_bush.png').convert_alpha()

    return food_image

tile_grass = None

def get_tile_grass():
    global tile_grass

    if tile_grass == None:
        tile_grass = pygame.image.load('tile_grass.png').convert()

    return tile_grass

tile_daisies = None

def get_tile_daisies():
    global tile_daisies

    if tile_daisies == None:
        tile_daisies = pygame.image.load('tile_daisies.png').convert()

    return tile_daisies

tile_dirt = None

def get_tile_dirt():
    global tile_dirt

    if tile_dirt == None:
        tile_dirt = pygame.image.load('tile_dirt.png').convert()

    return tile_dirt

tile_hill = None

def get_tile_hill():
    global tile_hill

    if tile_hill == None:
        tile_hill = pygame.image.load('tile_hill.png').convert()

    return tile_hill

tile_long_grass = None

def get_tile_long_grass():
    global tile_long_grass

    if tile_long_grass == None:
        tile_long_grass = pygame.image.load('tile_long_grass.png').convert()

    return tile_long_grass

tile_pit = None

def get_tile_pit():
    global tile_pit

    if tile_pit == None:
        tile_pit = pygame.image.load('tile_pit.png').convert()

    return tile_pit

tile_sand = None

def get_tile_sand():
    global tile_sand

    if tile_sand == None:
        tile_sand = pygame.image.load('tile_sand.png').convert()

    return tile_sand
