from images import *
from agent import *

#fix this later
INITIAL_ENERGY = 100
REPRODUCTION_ENERGY_THRESHOLD = 130
REPRODUCTION_COST = 30
CRITTER_ENERGY_DECAY_RATE = 0.2
FOOD_SPAWN_PERIOD = 50
FOOD_ENERGY = 50
CRITTER_VIEW_DISTANCE = 100
CRITTER_VIEW_DISTANCE_SQ = CRITTER_VIEW_DISTANCE**2
CRITTER_MAX_MOVE_SPEED = 0.5
REPRODUCTION_PERIOD = 120
COLLISION_RADIUS = 10
COLLISION_RADIUS_SQ = COLLISION_RADIUS**2
MEAN_TURN_INTERVAL = 10

WORLD_WIDTH = 640
WORLD_HEIGHT = 640
TILE_SIZE = 64

FRAMERATE = 50
ANIMATION_FRAME_INTERVAL = 8
CRITTER_VERTICAL_CENTER = 48
CRITTER_HORIZONTAL_CENTER = 16
FOOD_CENTER = 8

class Object(object):
    """ Abstract base class for simulation objects.
    
    In addition to overriding show, kill and update, all Objects
    must have the following attributes:
    object_ID - unique identifier for the object
    x, y - current simulation co-ordinates of the object
    world - reference to the containing World"""
    
    def __init__(self):
        raise NotImplementedError("Override in your subclass")
    
    def kill(self):
        """ Called when the object is destroyed. """
        pass
    
    def update(self):
        """ Called once every simulation step, to update the
        object's simulation model. """
        pass

    def render(self, screen):
        """ Called once every simulation step, to draw the
        object to the screen. """
        pass
    
    def distance_sq(self, other):
        """ Find the square of the distance between this Object and
        another Object. """

        # Since the world wraps around, it's not just a straight Euclidean
        # distance. We find the shorter x distance (either going across the
        # world in the normal way, or wrapping around the left/right edge).
        # Then we do the same for the y, then use these in the Euclidean
        # distance formula.
        dx = min(abs(self.x - other.x), WORLD_WIDTH - abs(self.x - other.x))
        dy = min(abs(self.y - other.y), WORLD_HEIGHT - abs(self.y - other.y))
        
        return dx**2 + dy**2  
    
    def get_type(self):
        raise NotImplementedError("Override in your subclass")

class Food(Object):
    def __init__(self, world, object_ID, x, y, contained_energy):
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.energy = contained_energy
        self.food_image = get_food_image()
    
    def render(self, screen):
        screen.blit(self.food_image, (self.x - FOOD_CENTER, self.y - FOOD_CENTER))
        
    def get_type(self):
        return "Food"


class Critter(Object):
        def __init__(self, world, object_ID, x, y, direction, 
                     counter_offset, images):            
            self.world = world
            self.object_ID = object_ID
            self.x = x
            self.y = y
            self.direction = direction
            self.energy = INITIAL_ENERGY
            self.agent = Agent()           
            self.images = images 
            # counter to know when to change the animation
            # given offset so that critters do not move in 
            # unison.
            self.iteration_counter = counter_offset
        
        def update(self):
            # Find all objects close enough to be visible to the agent;
            # tag each along with its delta-x and delta-y values relative
            # to this object
            visible_objects = []
            for obj in self.world.objects:
                if obj != self:
                    # There's two different ways to get from self.x to obj.x:
                    # directly, or around the left/right edge. We calculate
                    # both of these and get two possible "delta x" values
                    # Example: width=100, self.x=40, obj.x=80. Then
                    # dxDirect = +40 (40 units from left to right)
                    # and dxAround = -60 (60 units from right to left)
                    dxDirect = obj.x - self.x
                    if obj.x >= self.x:
                        dxAround = dxDirect - WORLD_WIDTH
                    else:
                        dxAround = dxDirect + WORLD_WIDTH

                    # Take the shorter one, i.e. the one with smaller
                    # absolute value
                    dx = min((dxDirect, dxAround), key = abs)
                    # And the same with the y values
                    dyDirect = obj.y - self.y
                    if obj.y >= self.y:
                        dyAround = dyDirect - WORLD_HEIGHT
                    else:
                        dyAround = dyDirect + WORLD_HEIGHT
                        
                    dy = min((dyDirect, dyAround), key = abs)

                    if dx**2 + dy**2 < CRITTER_VIEW_DISTANCE_SQ:
                        visible_objects.append((obj, dx, dy))

            # Ask the agent what to do
            (turn_angle, move_distance, reproduce) = \
                self.agent.compute_next_action(self, visible_objects)

            # Move
            if move_distance > CRITTER_MAX_MOVE_SPEED: move_distance = CRITTER_MAX_MOVE_SPEED
            self.direction += turn_angle
            self.direction %= 2*pi
            self.x += cos(self.direction) * move_distance
            self.y += sin(self.direction) * move_distance

            # Wrap around
            while self.x < 0: self.x += WORLD_WIDTH
            while self.x >= WORLD_WIDTH: self.x -= WORLD_WIDTH
            while self.y < 0: self.y += WORLD_HEIGHT
            while self.y >= WORLD_HEIGHT: self.y -= WORLD_HEIGHT

            self.direction %= 2*pi

            # Reproduce
            if reproduce:
                child = Critter(self.world, 0,
                                self.x, self.y, 
                                self.direction + pi, 0,
                                get_images())
                self.world.add(child)
                self.energy -= REPRODUCTION_COST

            # Eat food
            for obj in self.world.objects:
                if isinstance(obj, Food):
                    if self.distance_sq(obj) < COLLISION_RADIUS_SQ:
                        self.world.delete(obj)
                        self.energy += obj.energy

            # Energy decay + death
            self.energy -= CRITTER_ENERGY_DECAY_RATE
            if self.energy <= 0:
                self.world.delete(self)
                
            # update the counter
            self.iteration_counter += 1

        def render(self, screen):          
            direction_quadrant = int(((self.direction + pi/4)%(2*pi))/(pi/2))
            animation_frame = int(self.iteration_counter/ANIMATION_FRAME_INTERVAL) \
                                  % len(self.images[direction_quadrant])

            screen.blit(self.images[direction_quadrant][animation_frame],
                        (self.x - CRITTER_HORIZONTAL_CENTER, self.y - CRITTER_VERTICAL_CENTER))
            
        def get_type(self):
            return "Critter"