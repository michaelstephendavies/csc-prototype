import pygame

images = None

def get_man_images():
    # Returns list of lists where:
    #  first list is the animation frames for walking east
    #  second list is the animation frames for walking south
    #  second list is the animation frames for walking west
    #  second list is the animation frames for walking north

    global images
    
    if images == None:
        images = [
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
        
    return images

food_image = None

background_image = None


def get_food_image():
    global food_image

    if food_image == None:
        food_image = pygame.image.load('small_food_bush.png').convert_alpha()

    return food_image

def get_background_image():
    global background_image

    if background_image == None:
        background_image = pygame.image.load('tile_grass.png').convert()

    return background_image