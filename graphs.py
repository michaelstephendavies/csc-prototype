from __future__ import division

import pygame
from pygame.locals import *

#imports from our own files
from main import *

text_font = None
def get_text_font():
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

class Graph(object):
    def __init__(self, x, y, width, height, title,
                 bg_color=Color(255, 255, 255), out_file=None):
        self.rect = Rect(x, y, width, height)
        self.title_image = get_text_font().render(title, True, Color(0, 0, 0), bg_color)
        self.bg_color = bg_color
        
        if out_file != None:
            self.out = open(out_file, "w")
        else:
            self.out = None

    def finish(self):
        self.out.close()
    
    def render(self, screen):
        screen.fill(self.bg_color, self.rect)
        self.render_foreground(screen)
        screen.blit(self.title_image, self.rect)

    def render_foreground(self, screen):
        raise NotImplementedError("Override in your subclass")


class LineGraph(Graph):
    def __init__(self, x, y, width, height, title, high, scale_division,
                 bg_color=Color(255, 255, 255),
                 fg_color=Color(50, 50, 50), out_file=None):
        
        Graph.__init__(self, x, y, width, height, title, bg_color, out_file)

        self.zero_surface = get_text_font().render("0", True, Color(0, 0, 0), bg_color)
        self.high_surface = get_text_font().render(str(high), True, Color(0, 0, 0), bg_color)
        axis_size = max(self.high_surface.get_width(), self.zero_surface.get_width()) + 10
        
        self.graph_area_rect = Rect(x+axis_size, y+20, width-axis_size - 5, height-25)
        self.high = float(high)
        self.fg_color = fg_color
        self.scale_division = float(scale_division)
        
        self.graph_surface = pygame.Surface((self.graph_area_rect.width, self.graph_area_rect.height))
        self.graph_surface.fill(bg_color)

    def add_data_point(self, new_point):
        new_data_point_scaled = int((1 - new_point/self.high) * self.graph_area_rect.height)

        self.graph_surface.scroll(dx=-1)
        pygame.draw.line(self.graph_surface, self.bg_color,
                         (self.graph_area_rect.width-1, 0),
                         (self.graph_area_rect.width-1, self.graph_area_rect.height))
        pygame.draw.line(self.graph_surface, self.fg_color,
                         (self.graph_area_rect.width-1, self.graph_area_rect.height),
                         (self.graph_area_rect.width-1, new_data_point_scaled))

        self.last_data_point_scaled = new_data_point_scaled
    
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
            
