"""
agent.py

Contains the AI code which controls critters.

Currently contains basic heuristic behaviour, but could forseeably
be replaced with something more advanced.

Michael Davies and David Shorten
CSC3003S Capstone Project

All graphics used in this program are open content and 
were provided for by REFMAP(http://www.tekepon.net/fsm)
"""

from objects import *
import random
from math import *

def bound(x, a, b):
    if x < a: return a
    if x > b: return b
    return x

class Agent(object):
    """ The "brain" of a single critter, which controls its actions.
    Not to be confused with Critter, which is more like a critter's
    "physical body" which itself contains an agent. """
    
    # The current heuristic behaviour is to some extent controlled
    # by these four floating-point valued "traits", which differ between
    # critters and are "inherited" from parents.
    trait_names = [
        "reproduction_period",
        "reproduction_energy_threshold",
        "mean_turn_interval",
        "agent_move_speed"
    ]
    
    def __init__(self, config, parent1=None, parent2=None):
        """ Create a new Agent.

        parent1, parent2 - the Agents of the two parents, or
                           None if this agent belongs to one of the initial critters. """
        self.config = config
        self.clock = 0
        self.avoidance_countdown = 0

        # Map from trait name to value
        self.traits = {}
        
        # If we have no parents (i.e. we're one of the critters
        # at the initial state), then use the initial trait values from the config
        if parent1 == None or config.agent_trait_variance == 0:
            for t in Agent.trait_names:
                self.traits[t] = config[t]

        # Otherwise we get our traits by averaging our two parents'
        # settings and adding some randomness (that's how genetics
        # works, right?)
        else:
            for t in Agent.trait_names:
                value = (parent1.traits[t] + parent2.traits[t])/2
                value += (2*random.random() - 1)*config.agent_trait_variance*config[t]
                value = bound(value, config[t + "_min"], config[t + "_max"])
                self.traits[t] = value
        
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

        # Think about reproduction
        reproduction_target = None
        if critter.is_mature() and critter.energy > self.traits["reproduction_energy_threshold"] \
              and self.clock > self.traits["reproduction_period"]:
            
            # Try to find another critter to reproduce with  
            for (obj, dx, dy) in visible_objects:
                if obj.get_type() == "Critter" \
                     and dx**2 + dy**2 <= self.config.reproduction_radius_sq \
                     and obj.gender != critter.gender \
                     and obj.is_mature():
                    
                    reproduction_target = obj
                    self.clock = 0
                    break
                
        # check whether he is currently avoiding
        if self.avoidance_countdown > 0:
            self.avoidance_countdown -= 1
            return (0, self.traits["agent_move_speed"], reproduction_target)

        # object avoidance
        avoidable_things = [(obj, dx, dy) for (obj, dx, dy) in visible_objects
                                  if obj.get_type() == "Critter" 
                                  or obj.get_type() == "Scenery"]
        for thing in avoidable_things:
            if thing[0].get_type() == "Critter" and \
                    thing[1]**2 + thing[2]**2 <= self.config.critter_avoidance_radius**2:
                angle = atan2(-thing[2], -thing[1])
                self.avoidance_countdown = self.config.avoidance_time*self.config.framerate
                return (angle - critter.direction, 
                        self.traits["agent_move_speed"], reproduction_target)
            
            elif thing[0].get_type() == "Scenery" and \
                    thing[1]**2 + thing[2]**2 <= self.config.scenery_avoidance_radius**2:
                angle = atan2(-thing[2], -thing[1])
                self.avoidance_countdown = self.config.avoidance_time*self.config.framerate
                return (angle - critter.direction, 
                        self.traits["agent_move_speed"], reproduction_target)
        

        # Look for food
        visible_food_positions = [(dx, dy) for (obj, dx, dy) in visible_objects
                                  if obj.get_type() == "Food"]
        
        if visible_food_positions != []:
            # Move towards the closest food
            (closest_food_dx, closest_food_dy) = min(visible_food_positions,
                                                     key = lambda (dx, dy): dx**2 + dy**2)
            
            angle = atan2(closest_food_dy, closest_food_dx)
            return (angle - critter.direction, self.traits["agent_move_speed"], reproduction_target)
        else:
            # Can't see any food; walk around randomly
            turn_angle = 0
            if random.randint(0, int(self.config.framerate*self.traits["mean_turn_interval"])) == 5:
                turn_angle = (random.randint(0, 4)*pi)/2
            return (turn_angle, self.traits["agent_move_speed"], reproduction_target)
