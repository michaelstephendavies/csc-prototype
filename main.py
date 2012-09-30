"""
main.py

Contains the central World object which runs the main
simulation loop.

Usage: python main.py config_file world_spec_file

Michael Davies and David Shorten
CSC3003S Capstone Project

All graphics used in this program are open content and 
were provided for by REFMAP(http://www.tekepon.net/fsm)
"""

from __future__ import division

import os, sys
from os import path
import pygame
from pygame.locals import *
from math import *
import random
random.seed()

#imports from our own files
from images import *
from objects import *
from graphs import *
from config import *

class World(object):
    """ Stores all the simulation objects and runs the main
    simulation loop.

    Publically accessible attributes (read-only):
    self.objects - List containing all Objects, excluding skeletons.
    self.object_count - Map from object type string ("Critter" or "Food")
                        to the current number of objects of that type.
                        (Scenery is not tracked.)"""
    
    def __init__(self, screen, config):
        """ Create a new World, given the Pygame Surface to draw to and
        the configuration settings (a Config object). Call run to actually
        start the simulation. """
        
        # The simulation model has a toroidal topology (x and y co-ordinates
        # "wrap around"); we keep all x values in [0, width) and y values in
        # [0, height).
        
        # (0, 0) in the simulation model maps to the top-left corner,
        # positive y is down. Directions are given with positive being clockwise.
        
        self.screen = screen
        self.config = config
        self.skeletons = []
        self.objects = []

        # Map from object type string (return value from Object.get_type)
        # to number of objects of that type
        self.object_count = {"Critter": 0, "Food": 0}
        
        # Initialise graphs
        self.graphs = []
        if config.enable_graphs:
            self.sidebar_rect = Rect(self.config.world_width, 0,
                                     self.config.graph_width, self.config.world_height)
            self.sidebar_color = Color(200, 200, 200)
            
            num_graphs = 0
            if config.population_graph: num_graphs += 1
            if config.food_graph: num_graphs += 1
            if config.agent_move_speed_graph: num_graphs += 1

            # Allocate vertical space to each graph.
            # In total, one padding is needed for each graph, plus one extra
            # padding at the top. The rest of the space is divided equally
            # between the graphs.
            if num_graphs > 0:
                padding = 5
                vertical_space_per_graph = (config.world_height - (num_graphs+1)*padding)/num_graphs
                current_y = padding
                
                if config.population_graph:
                    self.graphs.append(PopulationGraph(self, config.world_width, current_y, config.graph_width,
                                                       vertical_space_per_graph, config.population_graph_high,
                                                       config.population_graph_scale_division,
                                                       config.population_graph_update_period,
                                                       config.population_graph_export_path))
                    current_y += vertical_space_per_graph + padding

                if config.food_graph:
                    self.graphs.append(FoodGraph(self, config.world_width, current_y, config.graph_width,
                                                 vertical_space_per_graph, config.food_graph_high,
                                                 config.food_graph_scale_division,
                                                 config.food_graph_update_period,
                                                 config.food_graph_export_path))
                    current_y += vertical_space_per_graph + padding

                if config.agent_move_speed_graph:
                    self.graphs.append(AgentTraitGraph(self, "agent_move_speed",
                                                       config.world_width, current_y, config.graph_width,
                                                       vertical_space_per_graph, "Average move speed vs Time",
                                                       config.agent_move_speed_graph_high,
                                                       config.agent_move_speed_graph_scale_division,
                                                       config.agent_move_speed_graph_update_period,
                                                       config.agent_move_speed_graph_export_path))
                    current_y += vertical_space_per_graph + padding
                
        
        # Add scenery from the world specification to the list of objects
        for item in self.config.scenery:
            if item[0] == "palm":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_palm(), self.config.tree_horizontal_offset, 
                                    self.config.palm_vertical_offset))
            elif item[0] == "oak":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_oak(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "dead_tree":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_dead_tree(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "pine":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_pine(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "fern":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_fern(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "rocks":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_rocks(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "stump":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_stump(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "yellow_flowers":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_yellow_flowers(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "pink_flowers":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_pink_flowers(), self.config.small_object_offset, 
                                    self.config.small_object_offset))

        # Create the initial critters and food
        for i in xrange(self.config.starting_males):
            self.add(Critter(config, self, len(self.objects),
                random.random()*self.config.world_width, random.random()
                    *self.config.world_height, random.randint(0, 5), 
                            random.randint(0, 5), 2*self.config.ageing_interval, get_male_images(), "m"))
        
        for i in xrange(self.config.starting_females):
            self.add(Critter(config, self, len(self.objects),
                random.random()*self.config.world_width, random.random()
                    *self.config.world_height, random.randint(0, 5), 
                            random.randint(0, 5), 2*self.config.ageing_interval, get_female_images(), "f"))
        
        for i in xrange(10):
            self.add(Food(config, self, len(self.objects), random.random()*self.config.world_width,
                random.random()*self.config.world_height, self.config.food_energy))
    
    def delete(self, obj):
        """ Remove an object (other than a skeleton) from the world. """
        obj.kill()
        self.objects.remove(obj)

        if obj.get_type() in self.object_count:
            self.object_count[obj.get_type()] -= 1

    def add(self, new_obj):
        """ Add an object (other than a skeleton) to the world; if the
        new object is too close to an existing object, it will be placed
        randomly onto the world. """
        
        # make sure the food is not too close to scenery, this messes
        # with the collision avoidance
        can_add = True
        for obj in self.objects:
            if new_obj.distance_sq(obj) < 1.5*self.config.scenery_avoidance_radius_sq:
                new_obj.x += random.random()*self.config.world_width
                new_obj.x %= self.config.world_width
                new_obj.y += random.random()*self.config.world_height
                new_obj.y %= self.config.world_height
                self.add(new_obj)
                return
        self.objects.append(new_obj)
        
        if new_obj.get_type() in self.object_count:
            self.object_count[new_obj.get_type()] += 1
         
    def add_here(self, new_obj):
        """ Add an object (other than a skeleton) to the world, without
        repositioning it if it is too close to an existing object. """
        self.objects.append(new_obj)

        if new_obj.get_type() in self.object_count:
            self.object_count[new_obj.get_type()] += 1
        
    def add_skeleton(self, new_skeleton):
        """ Add a skeleton to the world. """
        self.skeletons.append(new_skeleton)
        
    def delete_skeleton(self, skeleton):
        """ Remove a skeleton from the world. """
        self.skeletons.remove(skeleton)
    
    def run(self):
        """ Run the simulation. Only returns when the user closes
        the Pygame window. """
        counter = 0
        
        tiles = {    
            "g" : get_tile_grass(),
            "d" : get_tile_daisies(),
            "h" : get_tile_hill(),
            "l" : get_tile_long_grass(),
            "p" : get_tile_pit(),
            "s" : get_tile_sand(),
            "i" : get_tile_dirt()
        }
        
        # variables to help the eagle and dove only sometimes
        # fly accross 
        eagle_on = True
        eagle_x = 0
        eagle_y = 0.1*self.config.world_height # first y channel
        eagle_start = 0
        dove_on = True
        dove_x = 0.1*self.config.world_width # first x channel
        dove_y = 0
        dove_start = 0        

        # Main simulation loop
        while True:
            
            # Keep a steady framerate
            clock = pygame.time.Clock()
            clock.tick(self.config.framerate)

            # Check if the user quitted
            for event in pygame.event.get():
                if event.type == QUIT:
                    # Allow the graphs to close their output streams
                    # if necessary
                    for graph in self.graphs:
                        graph.finish()
                    return

            # Update the simulation
            # ---------------------
            
            # Update each object; Iterate over a copy of the object list
            # since modifying a list while iterating over it is verboten
            for obj in self.objects[:]:
                obj.update()

            for obj in self.skeletons[:]:
                obj.update()

            # Maybe spawn some food
            if counter % self.config.food_spawn_period == 0:
                self.add(Food(config, self, 0, random.random()*self.config.world_width,
                              random.random()*self.config.world_height, self.config.food_energy))

            # Update the graphs
            for graph in self.graphs:
                graph.update()

            # Render the simulation
            # ---------------------
            
            # Sort the objects in order of y-coordinates so that they are
            # rendered in the correct order: If A is behind B, we have render
            # A first so that B appears in front.
            self.objects.sort(key = lambda obj: obj.y)

            # Draw the tiles
            for x in xrange(self.config.cols):
                for y in xrange(self.config.rows):
                       self.screen.blit(tiles[self.config.tile_spec[x][y]], 
                                        (x*self.config.tile_size, y*self.config.tile_size))

            # Draw the objects; draw all the skeletons first so they appear
            # underneath all the other objects.
            for skeleton in self.skeletons:
                skeleton.render(self.screen)

            for obj in self.objects:
                obj.render(self.screen)
            
            # Update and render the eagle and dove
            # Since we draw these after all the other objects, they appear
            # on top.
            frame_choice = int(floor((counter / self.config.framerate)*5) % 2)
            if(eagle_on):
                if eagle_x > self.config.world_width:
                    eagle_on = False   
                eagle_x = (counter - eagle_start)
                screen.blit(get_eagle()[frame_choice], (eagle_x, eagle_y))
            if (not eagle_on) and \
                random.randint(0, 2*self.config.framerate - 1) == \
                (counter % 2*self.config.framerate):
                eagle_on = True
                eagle_x = 0
                eagle_start = counter
                eagle_y = (random.randint(1, 9)/10)*self.config.world_height
            if(dove_on):
                if dove_y < 0:
                    dove_on = False   
                dove_y = (self.config.world_height - (counter - dove_start))
                screen.blit(get_dove()[frame_choice], (dove_x, dove_y))
            if (not dove_on) and \
                random.randint(0, 2*self.config.framerate - 1) == \
                (counter % 2*self.config.framerate):
                dove_on = True
                dove_y = 0
                dove_start = counter
                dove_x = (random.randint(1, 9)/10)*self.config.world_width

            # Draw the graph sidebar
            if self.config.enable_graphs:
                self.screen.fill(self.sidebar_color, self.sidebar_rect)
                for graph in self.graphs:
                    graph.render(self.screen)
            
            counter += 1    
            
            pygame.display.flip()
            

if __name__ == '__main__':
    # Parse the configuration and world specification
    try:
        config = Config(sys.argv[1], sys.argv[2])
    except ConfigParseException as ex:
        print ex
        sys.exit(1)
    except IndexError:
        # User left out a command-line parameter
        print "USAGE: python main.py config_file world_spec_file"
        sys.exit(1)

    # Seed the random number generator
    if config.random_seed == "":
        random.seed() # using the OS-specific randomness source
    else:
        random.seed(hash(config.random_seed))

    # Initialise the Pygame library
    pygame.init()
    pygame.font.init()

    # Create the Pygame window to draw onto
    if config.enable_graphs:
        # Leave some space on the right of the world to show graphs
        screen = pygame.display.set_mode((config.world_width + config.graph_width, config.world_height))
    else:
        screen = pygame.display.set_mode((config.world_width, config.world_height))

    # Run the simulation
    World(screen, config).run()
