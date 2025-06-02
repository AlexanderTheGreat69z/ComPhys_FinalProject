import pygame
from random import randint
from numpy import sqrt

from objects import *
from utils import *
from settings import *

pygame.init()


class main:
    def __init__(self):
        # Window Config #
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        self.caption = pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
        self.FPS = FPS
        self.__running = True
        self.px_per_mtr = PIXELS_PER_METER
        
        # Tube Config (in meters)
        self.l_tube_height_m = 200 / self.px_per_mtr
        self.base_r_tube_height_m = 100 / self.px_per_mtr
        self.current_r_tube_height_m = self.base_r_tube_height_m
        self.tube_width_m = (self.surface.get_width() // 2 - 50) / self.px_per_mtr
        self.tube_center_y_m = (self.surface.get_rect().centery - 100) / self.px_per_mtr
        
        self.l_tube = Tube(self.surface, int(self.tube_width_m * self.px_per_mtr), int(self.l_tube_height_m * self.px_per_mtr))
        self.l_tube.rect.left = 0
        self.l_tube.rect.centery = int(self.tube_center_y_m * self.px_per_mtr)
        
        self.r_tube = Tube(self.surface, int(self.tube_width_m * self.px_per_mtr), int(self.current_r_tube_height_m * self.px_per_mtr))
        self.r_tube.rect.right = self.surface.get_width()
        self.r_tube.rect.centery = int(self.tube_center_y_m * self.px_per_mtr)
        
        # Transition zone (in meters)
        self.transition_start_m = (self.surface.get_width() // 2 - 100) / self.px_per_mtr  # Start of transition
        self.transition_end_m = (self.surface.get_width() // 2 + 100) / self.px_per_mtr    # End of transition
        
        # Particle Config
        self.particle_size_m = 10 / self.px_per_mtr
        self.base_speed_mps = 2 # meters per second
        self.aftermath_speed = 0 
        self.particle_speed_mps = self.base_speed_mps
        self.particle_cols = []
        self.spawn_interval = 0.5 # seconds
        self.max_particles = 20  # Maximum number of particle columns
        self.particles_per_column = 8  # Density
        self.pressure = DEFAULT_ENVIRONMENTAL_PRESSURE  # Pressure multiplier (still abstract)
        self.compression_started = False
        self.compression_timer = 0 # frames
        
        self.spawn_timer = Timer(self.spawn_interval, True)
        
        # Slider for Right Tube Height (controls height in meters)
        padding = 20
        self.slider_min_val = self.l_tube_height_m * 0.125
        self.slider_max_val = self.l_tube_height_m * 2
        self.right_tube_slider = Slider(self.surface, self.slider_min_val, self.slider_max_val, self.current_r_tube_height_m)
        self.right_tube_slider.rect.right = self.surface.get_rect().right - padding
        self.right_tube_slider.rect.bottom = self.surface.get_rect().bottom - padding
        
        self.density_slider = Slider(self.surface, 5, 20, self.particles_per_column)
        self.density_slider.rect.left = self.surface.get_rect().left + padding
        self.density_slider.rect.bottom = self.surface.get_rect().bottom - padding

        # Initial fill
        # self._initialFill()

    def _updateTubeSize(self):
        # Update the right tube object's dimensions and position (using pixels)
        self.r_tube.rect.height = int(self.current_r_tube_height_m * self.px_per_mtr)
        self.r_tube.backborder.height = int(self.current_r_tube_height_m * self.px_per_mtr + 10) # Keep border thickness in pixels
        self.r_tube.rect.centery = int(self.tube_center_y_m * self.px_per_mtr)
        self.r_tube.backborder.center = self.r_tube.rect.center

    # def _initialFill(self):
    #     # Generate particles in the left tube (using pixel coordinates for spawning range)
    #     generation_range_top_px = self.l_tube.rect.top
    #     generation_range_bot_px = self.l_tube.rect.bottom
        
    #     # Fill the tube with particles
    #     for _ in range(self.max_particles):
    #         # ParticleColumn expects speed in its own unit (which was pixels/frame), let's keep it that way internally for now
    #         # The speed calculation will be done in meters/s and then converted for the ParticleColumn
    #         newCol = ParticleColumn(self.surface, int(self.particle_size_m * self.px_per_mtr), self.particles_per_column, self.base_speed_mps * self.px_per_mtr / self.FPS, (generation_range_top_px, generation_range_bot_px))
    #         newCol.rect.x = randint(0, self.surface.get_width() // 2)  # Distribute particles in the left tube (in pixels)
    #         self.particle_cols.append(newCol)
            
    def _getTubeHeightAtX_m(self, x_pos_px):
        x_pos_m = x_pos_px / self.px_per_mtr
        if x_pos_m < self.transition_start_m:
            return self.l_tube_height_m
        elif x_pos_m > self.transition_end_m:
            return self.current_r_tube_height_m
        else:
            # Calculate progress through transition (in meters)
            progress = (x_pos_m - self.transition_start_m) / (self.transition_end_m - self.transition_start_m)
            # Linearly interpolate height (can change easing if needed)
            return self.l_tube_height_m + (self.current_r_tube_height_m - self.l_tube_height_m) * progress
            
    def _calculateSpeedAtX_mps(self, x_pos_px):
        x_pos_m = x_pos_px / self.px_per_mtr
        
        # Calculate target velocity in the narrow tube using continuity equation
        # v2 = v1 * (A1 / A2) -> v2 = v1 * (H1 / H2) in 2D
        self.aftermath_speed = self.base_speed_mps * (self.l_tube_height_m / self.current_r_tube_height_m) if self.current_r_tube_height_m > 0 else self.base_speed_mps
        
        print(f"Base: {self.base_speed_mps} | After: {self.aftermath_speed}")
        if x_pos_m < self.transition_start_m:
            return self.base_speed_mps
        elif x_pos_m > self.transition_end_m:
            # Apply calculated speed in narrow tube, potentially scaled by abstract pressure
            return self.aftermath_speed # * self.pressure # Decide if pressure still scales speed here
        else:
            # Calculate how far through the transition zone the particle is (0 to 1) in meters
            transition_progress = (x_pos_m - self.transition_start_m) / (self.transition_end_m - self.transition_start_m)
            # Smooth the transition using a quadratic function
            transition_progress = transition_progress * transition_progress
            
            # Interpolate between base speed and target speed in narrow tube
            interpolated_speed_mps = self.base_speed_mps + (self.aftermath_speed - self.base_speed_mps) * transition_progress
            return interpolated_speed_mps # * self.pressure # Decide if pressure still scales speed here
        
    def _updatePhysics(self):
        # Calculate pressure based on the ratio of the left tube height to the current right tube height
        # compression_ratio = self.l_tube_height_m / self.current_r_tube_height_m if self.current_r_tube_height_m > 0 else 1.0
        # Base pressure is 1.0, it increases as the tube gets narrower (this is still an abstract pressure value)
        # self.pressure = DEFAULT_ENVIRONMENTAL_PRESSURE + (compression_ratio - 1.0) * (len(self.particle_cols) / self.max_particles)
        self.pressure = DEFAULT_ENVIRONMENTAL_PRESSURE + ((self.particles_per_column*125)*(self.base_speed_mps**2 - self.aftermath_speed**2))/2
        self.pressure /= DEFAULT_ENVIRONMENTAL_PRESSURE
        
        # Update particle speeds and positions based on their location
        for col in self.particle_cols:
            # Calculate speed in meters/s based on position
            speed_mps = self._calculateSpeedAtX_mps(col.rect.centerx)
            # Convert speed to pixels per frame for the ParticleColumn
            col.travel_speed = speed_mps * self.px_per_mtr / self.FPS
            
            # Calculate current tube height at particle's x position (in meters)
            current_tube_height_m = self._getTubeHeightAtX_m(col.rect.centerx)
            
            # Calculate vertical spacing based on current tube height (in meters)
            # Ensure spacing is not zero if current_tube_height_m is very small
            spacing_m = current_tube_height_m / (self.particles_per_column + 1) if self.particles_per_column + 1 > 0 else current_tube_height_m
            
            # Update particle positions to be centered vertically within the current tube height (using pixels)
            tube_top_y_m = self.tube_center_y_m - current_tube_height_m / 2
            tube_top_y_px = int(tube_top_y_m * self.px_per_mtr)
            
            for i, particle in enumerate(col.particles):
                target_y_m = tube_top_y_m + spacing_m * (i + 1)
                target_y_px = int(target_y_m * self.px_per_mtr)
                
                # Directly set particle position for immediate compression
                particle.rect.centery = target_y_px

    
    def _generateParticles(self):
        if len(self.particle_cols) < self.max_particles:
            # Generation range in pixels
            generation_range_top_px = self.l_tube.rect.top
            generation_range_bot_px = self.l_tube.rect.bottom
            
            self.spawn_timer.countdown() # Timer works in seconds
            if self.spawn_timer.triggered():
                # Initial speed for new particles (base speed in meters/s converted to pixels/frame)
                initial_speed_px_per_frame = self.base_speed_mps * self.px_per_mtr / self.FPS
                newCol = ParticleColumn(self.surface, int(self.particle_size_m * self.px_per_mtr), self.particles_per_column, initial_speed_px_per_frame, (generation_range_top_px, generation_range_bot_px))
                self.particle_cols.append(newCol)
        
    def _drawParticles(self):
        # Drawing is done in pixels by the ParticleColumn class
        for col in self.particle_cols:
            col.draw()
            # Remove particle columns that have moved off screen to the right (check in pixels)
            if col.rect.left > self.surface.get_width():
                self.particle_cols.remove(col)
                
    def _drawConnector(self):
        # Calculate the connector points based on current tube heights and positions (in pixels)
        l_tube_topright = self.l_tube.rect.topright
        l_tube_bottomright = (self.l_tube.rect.right, int(self.tube_center_y_m * self.px_per_mtr + self.l_tube_height_m * self.px_per_mtr / 2))
        r_tube_topleft = self.r_tube.rect.topleft
        r_tube_bottomleft = (self.r_tube.rect.left, int(self.tube_center_y_m * self.px_per_mtr + self.current_r_tube_height_m * self.px_per_mtr / 2))
        
        tube_connector_points = [l_tube_topright, l_tube_bottomright, r_tube_bottomleft, r_tube_topleft]
        # Draw in pixels
        pygame.draw.polygon(self.surface, self.l_tube.bb_col, tube_connector_points, 12)
        pygame.draw.polygon(self.surface, self.l_tube.tube_col, tube_connector_points)
        
    def _drawTexts(self):
        # Display initial velocity, current velocity in narrow tube, and right tube height in meters
        initial_vel_text = self.font.render(f"Initial Velocity: {self.base_speed_mps:.2f} m/s", True, (0, 0, 0))
        current_vel_text = self.font.render(f"Velocity in Narrow Tube: {self.aftermath_speed:.2f} m/s", True, (0, 0, 0))
        tube_size_text = self.font.render(f"Right Tube Height: {self.current_r_tube_height_m:.2f} m", True, (0, 0, 0))
        pressure_text = self.font.render(f"Abstract Pressure: {self.pressure:5f} atm", True, (0, 0, 0))
        
        
        padding = 20
        
        # Position tube size text above the slider
        tube_size_text_rect = tube_size_text.get_rect()
        tube_size_text_x = self.surface.get_width() - tube_size_text_rect.width - padding
        tube_size_text_y = self.right_tube_slider.rect.y - tube_size_text_rect.height - 5 # 5 pixels padding above slider

        self.surface.blit(initial_vel_text, (10, 10))
        self.surface.blit(current_vel_text, (10, 50))
        self.surface.blit(pressure_text, (10, 130))
        
        # Blit tube size text at new bottom right position
        self.surface.blit(tube_size_text, (tube_size_text_x, tube_size_text_y))
        
    def __event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
            
            # Handle slider events (slider value is in meters)
            if self.right_tube_slider.handle_event(e):
                self.current_r_tube_height_m = self.right_tube_slider.value
                self._updateTubeSize()
            
            if self.density_slider.handle_event(e):
                self.particles_per_column = self.density_slider.value
    
    def __update(self):
        self.surface.fill((255,255,255))
        
        self._updatePhysics()
        self._generateParticles()
        
        self._drawConnector()
        self.l_tube.draw()
        self.r_tube.draw()
        
        self._drawParticles()
        self._drawTexts()
        
        # Draw the slider
        self.right_tube_slider.draw()
        self.density_slider.draw()
        
        pygame.display.update()
    
    def run(self):
        while self.__running:
            self.__event()
            self.__update()
            self.clock.tick(self.FPS)
    
if __name__ == '__main__': main().run()
