"""
images.py

Loads images and stores them in a single, localised location.
This prevents multiple copies of the same image from being loaded
unnecessarily.

The first time a function from this module is called, the image is
loaded and returned; on subsequent calls, a reference to that same image
is returned.

All graphics used in this program are open content and 
were provided for by REFMAP(http://www.tekepon.net/fsm)
"""

import pygame

male_images = None

def get_male_images():
    """ Get the sprites for the male critter.

    Returns a three-dimensional list where:
    * the first dimension (from 0 to 3) gives the critter's "life stage"
      (0=child, 1=teenager, 2=adult, 3=elder)
    * the second dimension (from 0 to 4) gives the direction the critter
      is facing (0=east, 1=south, 2=west, 3=north)
    * the third dimension gives the animation frame. """

    global male_images
    
    if male_images == None:
        male_images = [
            # child
            [
                # east
                [
                    pygame.image.load('images/boy_east1.png').convert(),
                    pygame.image.load('images/boy_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/boy_south1.png').convert(),
                    pygame.image.load('images/boy_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/boy_west1.png').convert(),
                    pygame.image.load('images/boy_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/boy_north1.png').convert(),
                    pygame.image.load('images/boy_north2.png').convert()
                ]
            ],
            # teen
            [
                # east
                [
                    pygame.image.load('images/teen_east1.png').convert(),
                    pygame.image.load('images/teen_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/teen_south1.png').convert(),
                    pygame.image.load('images/teen_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/teen_west1.png').convert(),
                    pygame.image.load('images/teen_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/teen_north1.png').convert(),
                    pygame.image.load('images/teen_north2.png').convert()
                ]
            ],
            # adult
            [
                # east
                [
                    pygame.image.load('images/man_east1.png').convert(),
                    pygame.image.load('images/man_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/man_south1.png').convert(),
                    pygame.image.load('images/man_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/man_west1.png').convert(),
                    pygame.image.load('images/man_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/man_north1.png').convert(),
                    pygame.image.load('images/man_north2.png').convert()
                ]
            ],
            # elder
            [
                # east
                [
                    pygame.image.load('images/grandpa_east1.png').convert(),
                    pygame.image.load('images/grandpa_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/grandpa_south1.png').convert(),
                    pygame.image.load('images/grandpa_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/grandpa_west1.png').convert(),
                    pygame.image.load('images/grandpa_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/grandpa_north1.png').convert(),
                    pygame.image.load('images/grandpa_north2.png').convert()
                ]
            ]
        ]
        
    return male_images

female_images = None

def get_female_images():
    """ Get the sprites for the female critter. Return value
    is in the same format as get_male_images. """

    global female_images
    
    if female_images == None:
        female_images = [
            # child
            [
                # east
                [
                    pygame.image.load('images/girl_east1.png').convert(),
                    pygame.image.load('images/girl_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/girl_south1.png').convert(),
                    pygame.image.load('images/girl_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/girl_west1.png').convert(),
                    pygame.image.load('images/girl_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/girl_north1.png').convert(),
                    pygame.image.load('images/girl_north2.png').convert()
                ]
            ],
            # teen
            [
                # east
                [
                    pygame.image.load('images/teeng_east1.png').convert(),
                    pygame.image.load('images/teeng_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/teeng_south1.png').convert(),
                    pygame.image.load('images/teeng_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/teeng_west1.png').convert(),
                    pygame.image.load('images/teeng_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/teeng_north1.png').convert(),
                    pygame.image.load('images/teeng_north2.png').convert()
                ]
            ],
            # adult
            [
                # east
                [
                    pygame.image.load('images/woman_east1.png').convert(),
                    pygame.image.load('images/woman_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/woman_south1.png').convert(),
                    pygame.image.load('images/woman_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/woman_west1.png').convert(),
                    pygame.image.load('images/woman_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/woman_north1.png').convert(),
                    pygame.image.load('images/woman_north2.png').convert()
                ]
            ],
            # elder
            [
                # east
                [
                    pygame.image.load('images/grandma_east1.png').convert(),
                    pygame.image.load('images/grandma_east2.png').convert()
                ],
                # south
                [
                    pygame.image.load('images/grandma_south1.png').convert(),
                    pygame.image.load('images/grandma_south2.png').convert()
                ],
                # west
                [
                    pygame.image.load('images/grandma_west1.png').convert(),
                    pygame.image.load('images/grandma_west2.png').convert()
                ],
                # north
                [
                    pygame.image.load('images/grandma_north1.png').convert(),
                    pygame.image.load('images/grandma_north2.png').convert()
                ]
            ]
        ]
        
    return female_images

eagle = None

def get_eagle():
    """ Get the eagle sprites. Returns a list containing the
    animation frames. """
    global eagle

    if eagle == None:
        eagle = [
            pygame.image.load('images/eagle1.png').convert_alpha(),
            pygame.image.load('images/eagle2.png').convert_alpha()
        ]

    return eagle

dove = None

def get_dove():
    """ Get the dove sprites. Returns a list containing the
    animation frames. """
    global dove

    if dove == None:
        dove = [
            pygame.image.load('images/dove1.png').convert_alpha(),
            pygame.image.load('images/dove2.png').convert_alpha()
        ]

    return dove

skeleton = None

def get_skeleton():
    global skeleton

    if skeleton == None:
        skeleton = pygame.image.load('images/bones.png').convert_alpha()

    return skeleton

food_image = None

def get_food_image():
    global food_image

    if food_image == None:
        food_image = pygame.image.load('images/goat.png').convert_alpha()

    return food_image

tile_grass = None

def get_tile_grass():
    global tile_grass

    if tile_grass == None:
        tile_grass = pygame.image.load('images/tile_grass.png').convert()

    return tile_grass

tile_daisies = None

def get_tile_daisies():
    global tile_daisies

    if tile_daisies == None:
        tile_daisies = pygame.image.load('images/tile_daisies.png').convert()

    return tile_daisies

tile_dirt = None

def get_tile_dirt():
    global tile_dirt

    if tile_dirt == None:
        tile_dirt = pygame.image.load('images/tile_dirt.png').convert()

    return tile_dirt

tile_hill = None

def get_tile_hill():
    global tile_hill

    if tile_hill == None:
        tile_hill = pygame.image.load('images/tile_hill.png').convert()

    return tile_hill

tile_long_grass = None

def get_tile_long_grass():
    global tile_long_grass

    if tile_long_grass == None:
        tile_long_grass = pygame.image.load('images/tile_long_grass.png').convert()

    return tile_long_grass

tile_pit = None

def get_tile_pit():
    global tile_pit

    if tile_pit == None:
        tile_pit = pygame.image.load('images/tile_pit.png').convert()

    return tile_pit

tile_sand = None

def get_tile_sand():
    global tile_sand

    if tile_sand == None:
        tile_sand = pygame.image.load('images/tile_sand.png').convert()

    return tile_sand

palm = None

def get_palm():
    global palm

    if palm == None:
        palm = pygame.image.load('images/palm.png').convert_alpha()

    return palm

pine = None

def get_pine():
    global pine

    if pine == None:
        pine = pygame.image.load('images/pine.png').convert_alpha()

    return pine

oak = None

def get_oak():
    global oak

    if oak == None:
        oak = pygame.image.load('images/oak.png').convert_alpha()

    return oak

dead_tree = None

def get_dead_tree():
    global dead_tree

    if dead_tree == None:
        dead_tree = pygame.image.load('images/dead_tree.png').convert_alpha()

    return dead_tree

heart = None

def get_heart():
    global heart

    if heart == None:
        heart = pygame.image.load('images/heart2.png').convert_alpha()

    return heart

fern = None

def get_fern():
    global fern

    if fern == None:
        fern = pygame.image.load('images/fern.png').convert_alpha()

    return fern

pink_flowers = None

def get_pink_flowers():
    global pink_flowers

    if pink_flowers == None:
        pink_flowers = pygame.image.load('images/pink_flowers.png').convert_alpha()

    return pink_flowers

yellow_flowers = None

def get_yellow_flowers():
    global yellow_flowers

    if yellow_flowers == None:
        yellow_flowers = pygame.image.load('images/yellow_flowers.png').convert_alpha()

    return yellow_flowers

rocks = None

def get_rocks():
    global rocks

    if rocks == None:
        rocks = pygame.image.load('images/rocks.png').convert_alpha()

    return rocks

stump = None

def get_stump():
    global stump

    if stump == None:
        stump = pygame.image.load('images/stump.png').convert_alpha()

    return stump

