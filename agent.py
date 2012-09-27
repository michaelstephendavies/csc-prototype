from objects import *
import random
from math import *

class Agent(object):
    def __init__(self, config):
        self.config = config
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
        
        Returns a tuple (turn_angle, move_distance, reproduction_target)
        where reproduction_target is either None (meaning "do not reproduce on
        this frame") or another Critter (being the other critter to reproduce with). """
        self.clock += 1

        reproduction_target = None
        if critter.is_mature() and critter.energy > self.config.reproduction_energy_threshold \
              and self.clock > self.config.reproduction_period:
            
            # Try to find another critter to reproduce with  
            for (obj, dx, dy) in visible_objects:
                if obj.get_type() == "Critter" \
                     and dx**2 + dy**2 <= self.config.reproduction_radius_sq \
                     and obj.gender != critter.gender \
                     and obj.is_mature():
                    
                    reproduction_target = obj
                    self.clock = 0
                    break

        # Look for food
        visible_food_positions = [(dx, dy) for (obj, dx, dy) in visible_objects
                                  if obj.get_type() == "Food"]
        
        if visible_food_positions != []:
            # Move towards the closest food
            (closest_food_dx, closest_food_dy) = min(visible_food_positions,
                                                     key = lambda (dx, dy): dx**2 + dy**2)
            
            angle = atan2(closest_food_dy, closest_food_dx)
            return (angle - critter.direction, self.config.critter_max_move_speed, reproduction_target)
        else:
            # Can't see any food; walk around randomly
            turn_angle = 0
            if random.randint(0, self.config.framerate*self.config.mean_turn_interval) == 5:
                turn_angle = (random.randint(0, 4)*pi)/2
            return (turn_angle, self.config.critter_max_move_speed, reproduction_target)