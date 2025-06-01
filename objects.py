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
    def __init__(self, surface:pygame.Surface, a:int):
        self.surface = surface
        super().__init__(self.surface, (0,0,self.surface.get_width(), a), (200,200,200))
        self.backborder = pygame.Rect(0, 0, self.rect.width, a+10)
        
        self.bb_color = (150,150,150)
        self.rect.center = self.surface.get_rect().center
    
    def draw(self):
        self.backborder.center = self.rect.center
        pygame.draw.rect(self.surface, self.bb_color, self.backborder)
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
    def __init__(self, surface:pygame.Surface, s, n, generation_range:tuple = None):
        self.surface = surface
        self.particle_size = s
        self.rect = pygame.Rect(0,0,s,self.surface.get_height())
        
        self.min_range, self.max_range = generation_range
        
        self.num_of_particles = n
        self.particles = []
        self.__generateParticles()
    
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
        pygame.draw.line(self.surface, (255,0,0), (self.rect.centerx, 0), (self.rect.centerx, self.surface.get_height()))