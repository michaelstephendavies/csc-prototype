from objects import *
import random
from math import *

def bound(x, a, b):
    if x < a: return a
    if x > b: return b
    return x

class Agent(object):
    def __init__(self, config, parent1=None, parent2=None):
        self.config = config
        self.clock = 0

        # If we have no parents (i.e. we're one of the critters
        # at the initial state), then use the initial settings
        if parent1 == None or config.agent_setting_variance == 0:
            self.reproduction_period = config.reproduction_period
            self.reproduction_energy_threshold = config.reproduction_energy_threshold
            self.mean_turn_interval = config.mean_turn_interval
            self.agent_move_speed = config.agent_move_speed

        # Otherwise we get our settings by averaging our two parents'
        # settings and adding some randomness (that's how genetics
        # works, right?)
        else:
            # needs refactoring
            
            self.reproduction_period = \
              (parent1.reproduction_period + parent2.reproduction_period)/2
            
            self.reproduction_energy_threshold = \
              (parent1.reproduction_energy_threshold + parent2.reproduction_energy_threshold)/2
            
            self.mean_turn_interval = \
              (parent1.mean_turn_interval + parent2.mean_turn_interval)/2
            
            self.agent_move_speed = \
              (parent1.agent_move_speed + parent2.agent_move_speed)/2


            self.reproduction_period += \
              (2*random.random() - 1)*config.agent_setting_variance*self.reproduction_period
            
            self.reproduction_energy_threshold += \
              (2*random.random() - 1)*config.agent_setting_variance*self.reproduction_energy_threshold
            
            self.mean_turn_interval += \
              (2*random.random() - 1)*config.agent_setting_variance*self.mean_turn_interval
            
            self.agent_move_speed += \
              (2*random.random() - 1)*config.agent_setting_variance*self.agent_move_speed


            self.reproduction_period = \
                bound(self.reproduction_period,
                      config.reproduction_period_min,
                      config.reproduction_period_max)

            self.reproduction_energy_threshold = \
                bound(self.reproduction_energy_threshold,
                      config.reproduction_energy_threshold_min,
                      config.reproduction_energy_threshold_max)

            self.mean_turn_interval = \
                bound(self.mean_turn_interval,
                      config.mean_turn_interval_min,
                      config.mean_turn_interval_max)

            self.agent_move_speed = \
                bound(self.agent_move_speed,
                      config.agent_move_speed_min,
                      config.agent_move_speed_max)
        
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
        if critter.is_mature() and critter.energy > self.reproduction_energy_threshold \
              and self.clock > self.reproduction_period:
            
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
            return (angle - critter.direction, self.agent_move_speed, reproduction_target)
        else:
            # Can't see any food; walk around randomly
            turn_angle = 0
            if random.randint(0, int(self.config.framerate*self.mean_turn_interval)) == 5:
                turn_angle = (random.randint(0, 4)*pi)/2
            return (turn_angle, self.agent_move_speed, reproduction_target)
