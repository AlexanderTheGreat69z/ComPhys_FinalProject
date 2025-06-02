import pygame
from settings import *

class Timer:
    def __init__(self, t:int, loop:bool=False):
        self.interval = t * 1000
        self.start = pygame.time.get_ticks()
        self.loop = loop
        self.__triggered = False
        
    def countdown(self):
        current = pygame.time.get_ticks()
        if current - self.start >= self.interval:
            self.__triggered = True
            if self.loop: self.start = current  # Reset the timer
        else:
            self.__triggered = False
    
    def triggered(self):
        return self.__triggered

class Slider:
    def __init__(self, surface:pygame.Surface, min_val:int, max_val:int, initial_val:int):
        self.surface = surface
        self.rect = pygame.Rect(0, 0, SLIDER_WIDTH, SLIDER_HEIGHT)
        self.min_val = min_val
        self.max_val = max_val
        self.initial_val = initial_val
        self.value = initial_val
        self.grabbed = False
        
        # Calculate the initial position of the handle
        self.handle_w = self.rect.height
        self.handle_h = self.rect.height
        self.handle_rect = pygame.Rect(0, 0, self.handle_w, self.handle_h)

    def _update_handle_pos(self):
        # Calculate handle position based on current value
        range_span = self.max_val - self.min_val
        value_ratio = (self.value - self.min_val) / range_span if range_span > 0 else 0
        handle_x = self.rect.x + (self.rect.width - self.handle_w) * value_ratio
        self.handle_rect = pygame.Rect(handle_x, self.rect.y, self.handle_w, self.handle_h)

    def draw(self):
        # Draw slider bar
        pygame.draw.rect(self.surface, (200, 200, 200), self.rect)
        # Draw slider handle
        pygame.draw.rect(self.surface, (100, 100, 100), self.handle_rect)
        self._update_handle_pos()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.grabbed = True
                self.grab_offset_x = event.pos[0] - self.handle_rect.x
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION:
            if self.grabbed:
                # Move handle with mouse, clamp within slider bounds
                new_handle_x = event.pos[0] - self.grab_offset_x
                new_handle_x = max(self.rect.x, new_handle_x)
                new_handle_x = min(self.rect.right - self.handle_w, new_handle_x)
                self.handle_rect.x = new_handle_x
                
                # Update value based on handle position
                slider_range = self.rect.width - self.handle_w
                handle_pos_in_range = self.handle_rect.x - self.rect.x
                value_ratio = handle_pos_in_range / slider_range if slider_range > 0 else 0
                self.value = self.min_val + (self.max_val - self.min_val) * value_ratio
                return True # Indicate that the value has changed
        return False # Indicate that the value has not changed
