
from objects import *
import random
from math import *

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

class Agent(object):
    def __init__(self):
        self.clock = 0

    def compute_next_action(self, critter, visible_objects):
        """ Given the current state of the critter and a list of visible
        objects, returns the next set of actions for this agent's critter.

        critter is just the Critter instance
        visible_objects is a list of triples (obj, dx, dy) where:
        * obj is an Object instance
        * dx is the "delta-x" of the object relative to the critter
        * dy is the "delta-y" of the object relative to the critter
        Note that dx and dy have already taken into account the fact
        that the world wraps around.
        
        Returns a tuple (turn_angle, move_distance, reproduce)
        where reproduce is a boolean, which tells the given critter
        what to do. """
        self.clock += 1
        
        visible_food_positions = [(dx, dy) for (obj, dx, dy) in visible_objects
                                  if obj.get_type() == "Food"]
        
        if visible_food_positions != []:
            (closest_food_dx, closest_food_dy) = min(visible_food_positions,
                                                     key = lambda (dx, dy): dx**2 + dy**2)
            
            angle = atan2(closest_food_dy, closest_food_dx)
            return (angle - critter.direction, CRITTER_MAX_MOVE_SPEED, False)
        else:
            reproduce = False
            if critter.energy > REPRODUCTION_ENERGY_THRESHOLD:
                if self.clock > REPRODUCTION_PERIOD:
                    reproduce = True
                    self.clock = 0
            turn_angle = 0
            if random.randint(0, FRAMERATE*MEAN_TURN_INTERVAL) == 5:
                turn_angle = (random.randint(0, 4)*pi)/2
            return (turn_angle, CRITTER_MAX_MOVE_SPEED, reproduce)