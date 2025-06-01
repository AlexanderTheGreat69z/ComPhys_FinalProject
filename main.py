import pygame
from random import randint
from objects import *
pygame.init()

class main:
    def __init__(self):
        self.surface = pygame.display.set_mode((1280, 720))
        self.caption = pygame.display.set_caption("Comphy")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.__running = True
        
        self.tube = Tube(self.surface, self.surface.get_height() // 2)
        self.tube.rect.y -= 100
        self.particle_size = 20
        self.particle_cols = []
        self._generateParticles(20)
    
    def _generateParticles(self, cols:int):
        space = self.surface.get_width() / (cols+1)
        for i in range(cols):
            col = ParticleColumn(self.surface, self.particle_size, 5, (self.tube.rect.top, self.tube.rect.bottom))
            col.rect.centerx = space * (i + 1)
            self.particle_cols.append(col)
        
    def _drawParticles(self):
        for col in self.particle_cols:
            col.draw()
        
    def __event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
    
    def __update(self):
        self.surface.fill((255,255,255))
        self.tube.draw()
        self._drawParticles()
        pygame.display.update()
    
    def run(self):
        while self.__running:
            self.__event()
            self.__update()
            self.clock.tick(self.FPS)
    
if __name__ == '__main__': main().run()
