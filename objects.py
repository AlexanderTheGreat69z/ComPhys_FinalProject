import pygame
from random import randint

class __RectObject:
    def __init__(self, surface:pygame.Surface, rect_val:tuple, color:tuple = (0,0,0), text:str = None):
        self.surface = surface
        self.rect = pygame.Rect(*rect_val)
        self.color = color
        
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.text = self.font.render(text, True, (0,0,0))
        self.text_rect = self.text.get_rect()
    
    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.rect)
        self.surface.blit(self.text, self.text_rect)
        
class Tube(__RectObject):
    def __init__(self, surface:pygame.Surface, w:int, h:int):
        self.surface = surface
        self.tube_col = (200,210,220)
        super().__init__(self.surface, (0,0, w, h), self.tube_col)
        self.backborder = pygame.Rect(0, 0, self.rect.width, h+10)
        
        self.bb_col = (150,150,150)
        self.rect.centery = self.surface.get_rect().centery
    
    def draw(self):
        self.backborder.center = self.rect.center
        pygame.draw.rect(self.surface, self.bb_col, self.backborder)
        pygame.draw.rect(self.surface, self.color, self.rect)
        
class Particle(__RectObject):
    def __init__(self, surface, size):
        self.size = size
        self.outline = (0,150, 200)
        super().__init__(surface, (0,0,size,size), (0,200,200))
    
    def draw(self):
        pygame.draw.circle(self.surface, self.color, self.rect.center, self.size//2)
        pygame.draw.circle(self.surface, self.outline, self.rect.center, self.size//2, self.size // 5)
        
class ParticleColumn:
    def __init__(self, surface:pygame.Surface, s, n, v, generation_range:tuple = None):
        self.surface = surface
        self.particle_size = s
        self.rect = pygame.Rect(0,0,s,self.surface.get_height())
        
        self.min_range, self.max_range = generation_range
        
        self.num_of_particles = n
        self.particles = []
        self.__generateParticles()
        
        self.travel_speed = v
    
    def __generateParticles(self):
        for i in range(self.num_of_particles):
            particle = Particle(self.surface, self.particle_size)
            x = self.rect.centerx
            y = randint(self.min_range + self.particle_size // 2, self.max_range - self.particle_size // 2)
            particle.rect.center = (x, y)
            self.particles.append(particle)
    
    def draw(self):
        for p in self.particles: 
            p.rect.centerx = self.rect.centerx
            p.draw()
        self.rect.x += self.travel_speed
        # pygame.draw.line(self.surface, (255,0,0), (self.rect.centerx, 0), (self.rect.centerx, self.surface.get_height()))

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