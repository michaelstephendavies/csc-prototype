"""
graphs.py

Displays and exports various graphs.

Michael Davies and David Shorten
CSC3003S Capstone Project
"""

from __future__ import division

import pygame
from pygame.locals import *

#imports from our own files
from main import *

text_font = None
def get_text_font():
    """ Get the Pygame font used to render text. """
    global text_font
    if text_font == None:
        text_font = pygame.font.Font(None, 16)
    return text_font

def float_xrange(start, stop, step):
    """ Like xrange, but supports float arguments. """
    x = start
    while x <= stop:
        yield x
        x += step

def mean(iterable):
    """ Calculate the mean value in an iterable of numbers. """
    total = 0
    length = 0
    
    for value in iterable:
        total += value
        length += 1

    if length == 0: return 0
    return total/length


class Graph(object):
    """ Abstract base class for graphs. Takes care of drawing the
    background and graph title, takes care of the update_period
    parameter, and provides an output stream for the CSV export. """
    
    def __init__(self, x, y, width, height, title, update_period,
                 bg_color=Color(255, 255, 255), out_file=None):
        """ Create a new Graph. Remember to call this in your subclass' constructor.
        x, y - screen coordinates of the graph rectangle
        update_period - number of frames between subsequent update_inner calls
        out_file - filename of file to write to; if empty string or None, do not
                   export to file """
        
        self.rect = Rect(x, y, width, height)

        # Render the title text once to an image, which we will then blit to the
        # screen when we need to. (Pygame doesn't allow you to draw text directly
        # to the screen.)
        self.title_image = get_text_font().render(title, True, Color(0, 0, 0), bg_color)
        
        self.bg_color = bg_color
        self.update_period = update_period
        self.counter = 0

        # Create the output stream if necessary
        if out_file != None and out_file != "":
            self.out = open(out_file, "w")
        else:
            self.out = None

    def update(self):
        """ Called once every frame by the World's main simulation loop. """
        self.counter += 1
        if self.counter % self.update_period == 0:
            self.update_inner()

    def update_inner(self):
        """ Called once per update_period. """
        raise NotImplementedError("Override in your subclass")

    def write_to_output(self, string):
        """ Write some text to the output file; does nothing if out_file
        was empty string or None. """
        if self.out != None:
            self.out.write(string)
    
    def finish(self):
        """ Called when the application closes, so that the output stream
        can be closed. """
        if self.out != None:
            self.out.close()
    
    def render(self, screen):
        """ Draw the graph to the screen. """
        screen.fill(self.bg_color, self.rect)
        self.render_foreground(screen)
        screen.blit(self.title_image, self.rect)

    def render_foreground(self, screen):
        """ Draw the foreground of the graph (i.e. all of the graph, but
        excluding the background and title). """
        raise NotImplementedError("Override in your subclass")


class LineGraph(Graph):
    """ Abstract base class for a line graph, which displays how some
    value varies over time, and scrolls to the left as the simulation
    progresses. """
    
    def __init__(self, x, y, width, height, title, update_period, high, scale_division,
                 bg_color=Color(255, 255, 255),
                 fg_color=Color(50, 50, 50), out_file=None):
        """ Create a new LineGraph. Remember to call this in your subclass' constructor.

        high - the highest possible y-value the graph can display (the lowest possible
               value currently has to be 0); determines the vertical scale
        scale_division - spacing between each scale mark on the y-axis """
        
        Graph.__init__(self, x, y, width, height, title, update_period, bg_color, out_file)

        # Render the y-axis markings (0 and the high value) once each to two images
        # which we will then blit to the screen
        self.zero_surface = get_text_font().render("0", True, Color(0, 0, 0), bg_color)
        self.high_surface = get_text_font().render(str(high), True, Color(0, 0, 0), bg_color)

        # Amount of space allocated to the x-axis
        axis_size = max(self.high_surface.get_width(), self.zero_surface.get_width()) + 10

        # Rectangle defining the screen coordinates of the main graph region (excluding
        # axes and padding)
        self.graph_area_rect = Rect(x+axis_size, y+20, width-axis_size - 5, height-25)
        
        self.high = float(high)
        self.fg_color = fg_color
        self.scale_division = float(scale_division)

        # Create a single surface which we draw the graph area to. Each time
        # we add a new data point, we scroll this surface one pixel to the left,
        # and fill in the rightmost edge with the new data point. This surface
        # is then blitted to the screen.
        # This way, we do not need to
        self.graph_surface = pygame.Surface((self.graph_area_rect.width, self.graph_area_rect.height))
        self.graph_surface.fill(bg_color)

        self.write_to_output(title+"\n")
        self.write_to_output("Frame,Value\n")
    
    def add_data_point(self, new_point):
        """ Add a new data point to the graph. Your subclass should call this
        once in update_inner. """
        # Convert the given y-value into a coordinate in graph_surface
        new_data_point_scaled = int((1 - new_point/self.high) * self.graph_area_rect.height)

        # Scroll graph_surface to the left by one pixel, then fill in the leftmost
        # edge with the new data point
        self.graph_surface.scroll(dx=-1)
        pygame.draw.line(self.graph_surface, self.bg_color,
                         (self.graph_area_rect.width-1, 0),
                         (self.graph_area_rect.width-1, self.graph_area_rect.height))
        pygame.draw.line(self.graph_surface, self.fg_color,
                         (self.graph_area_rect.width-1, self.graph_area_rect.height),
                         (self.graph_area_rect.width-1, new_data_point_scaled))

        # Write the data point to the CSV file if necessary
        self.write_to_output("{0},{1}\n".format(self.counter, new_point))
    
    def render_foreground(self, screen):
        screen.blit(self.graph_surface, self.graph_area_rect)

        # Draw axes
        pygame.draw.line(screen, (0, 0, 0),
                         self.graph_area_rect.topleft, self.graph_area_rect.bottomleft)
        pygame.draw.line(screen, (0, 0, 0),
                         self.graph_area_rect.bottomleft, self.graph_area_rect.bottomright)

        # Draw scale marks
        for y in float_xrange(0.0, self.high, self.scale_division):
            scaled_y = self.graph_area_rect.bottom - int((1 - y/self.high) * self.graph_area_rect.height)
            pygame.draw.line(screen, (0, 0, 0),
                             (self.graph_area_rect.left, scaled_y),
                             (self.graph_area_rect.left - 5, scaled_y))

        # Draw text labels on the scale for 0 and high
        screen.blit(self.zero_surface,
                    (self.graph_area_rect.left - self.zero_surface.get_width() - 6,
                     self.graph_area_rect.bottom - self.zero_surface.get_height() + 4))
        screen.blit(self.high_surface,
                    (self.graph_area_rect.left - self.high_surface.get_width() - 6,
                     self.graph_area_rect.top))
            

class PopulationGraph(LineGraph):
    """ Graph tracking critter population levels over time. """
    
    def __init__(self, world, x, y, width, height, high,
                 scale_division, update_period, out_file=None):
        
        LineGraph.__init__(self, x, y, width, height, "Population vs Time",
                           update_period, high, scale_division,
                           Color(200, 200, 200), Color(80, 80, 150), out_file)
        
        self.world = world

    def update_inner(self):
        self.add_data_point(self.world.object_count["Critter"])


class FoodGraph(LineGraph):
    """ Graph tracking food levels over time. """
    
    def __init__(self, world, x, y, width, height, high,
                 scale_division, update_period, out_file=None):
        
        LineGraph.__init__(self, x, y, width, height, "Food level vs Time",
                           update_period, high, scale_division,
                           Color(200, 200, 200), Color(80, 150, 80), out_file)

        self.world = world

    def update_inner(self):
        self.add_data_point(self.world.object_count["Food"])


class AgentTraitGraph(LineGraph):
    """ Graph tracking the average value of some Agent trait across
    all critters over time. """
    
    def __init__(self, world, trait, x, y, width, height, title,
                 high, scale_division, update_period, out_file=None):

        LineGraph.__init__(self, x, y, width, height, title, update_period,
                           high, scale_division, Color(200, 200, 200), Color(150, 80, 80), out_file)

        self.trait = trait
        self.world = world

    def update_inner(self):
        self.add_data_point(mean(obj.agent.traits[self.trait]
                                 for obj in self.world.objects
                                 if obj.get_type() == "Critter"))

    
