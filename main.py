import pygame
from random import randint
from objects import *
pygame.init()

class main:
    def __init__(self):
        # Window Config #
        self.surface = pygame.display.set_mode((1280, 720))
        self.caption = pygame.display.set_caption("Comphy")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.__running = True
        
        # Tube Config #
        self.tube_sizes = (200, 100)
        
        self.l_tube = Tube(self.surface, self.surface.get_width() // 2 - 50, self.tube_sizes[0])
        self.l_tube.rect.left = self.surface.get_rect().left
        
        self.r_tube = Tube(self.surface, self.surface.get_width() // 2 - 50, self.tube_sizes[1])
        self.r_tube.rect.right = self.surface.get_rect().right
        
        self.l_tube.rect.y -= 100
        self.r_tube.rect.y -= 100
        
        # Particle Config #
        self.particle_size = 10
        self.particle_speed = 2
        self.particle_cols = []
        self.spawn_interval = 0.5
        
        self.spawn_timer = Timer(self.spawn_interval, True)
    
    def _generateParticles(self):
        generation_range_top = max(self.l_tube.rect.top, self.r_tube.rect.top)
        generation_range_bot = min(self.l_tube.rect.bottom, self.r_tube.rect.bottom)
        self.spawn_timer.countdown()
        if self.spawn_timer.triggered():
            newCol = ParticleColumn(self.surface, self.particle_size, 5, self.particle_speed, (generation_range_top, generation_range_bot))
            self.particle_cols.append(newCol)
        
    def _drawParticles(self):
        for col in self.particle_cols:
            col.draw()
            if col.rect.x > self.surface.get_width():
                self.particle_cols.remove(col)
                
    def _drawConnector(self):
        tube_connector_points = [self.l_tube.rect.topright, self.l_tube.rect.bottomright, self.r_tube.rect.bottomleft, self.r_tube.rect.topleft]
        pygame.draw.polygon(self.surface, self.l_tube.bb_col, tube_connector_points, 12)
        pygame.draw.polygon(self.surface, self.l_tube.tube_col, tube_connector_points)
        
    def __event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
            # if e.type == pygame.KEYDOWN:
            #     if e.key == pygame.K_UP and self.spawn_interval > 0.1:
            #         self.particle_speed += 0.5
            #         self.spawn_interval -= 0.1
            #     if e.key == pygame.K_DOWN and self.particle_speed > 0.5:
            #         self.particle_speed -= 0.5
            #         self.spawn_interval += 0.1
                
            #     self.particle_speed = round(self.particle_speed, 2)
            #     self.spawn_timer = Timer(round(self.spawn_interval, 2), True)
    
    def __update(self):
        self.surface.fill((255,255,255))
        self._drawConnector()
        self.l_tube.draw()
        self.r_tube.draw()
        
        self._generateParticles()
        self._drawParticles()
        
        print(len(self.particle_cols), f"P.Speed: {self.particle_speed} | Interval: {self.spawn_interval}")
        pygame.display.update()
    
    def run(self):
        while self.__running:
            self.__event()
            self.__update()
            self.clock.tick(self.FPS)
    
if __name__ == '__main__': main().run()
