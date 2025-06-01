import pygame
from random import randint
from objects import *
pygame.init()

# Conversion factor
pixels_per_meter = 50 # 50 pixels = 1 meter (arbitrary choice)

# Simple Slider Class
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.initial_val = initial_val
        self.value = initial_val
        self.grabbed = False
        
        # Calculate the initial position of the handle
        self.handle_w = h
        self.handle_h = h
        self._update_handle_pos()

    def _update_handle_pos(self):
        # Calculate handle position based on current value
        range_span = self.max_val - self.min_val
        value_ratio = (self.value - self.min_val) / range_span if range_span > 0 else 0
        handle_x = self.rect.x + (self.rect.width - self.handle_w) * value_ratio
        self.handle_rect = pygame.Rect(handle_x, self.rect.y, self.handle_w, self.handle_h)

    def draw(self, surface):
        # Draw slider bar
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        # Draw slider handle
        pygame.draw.rect(surface, (100, 100, 100), self.handle_rect)

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

class main:
    def __init__(self):
        # Window Config #
        self.surface = pygame.display.set_mode((1280, 720))
        self.caption = pygame.display.set_caption("Comphy")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.__running = True
        
        # Tube Config (in meters)
        self.l_tube_height_m = 200 / pixels_per_meter
        self.base_r_tube_height_m = 100 / pixels_per_meter
        self.current_r_tube_height_m = self.base_r_tube_height_m
        self.tube_width_m = (self.surface.get_width() // 2 - 50) / pixels_per_meter
        self.tube_center_y_m = (self.surface.get_rect().centery - 100) / pixels_per_meter
        
        self.l_tube = Tube(self.surface, int(self.tube_width_m * pixels_per_meter), int(self.l_tube_height_m * pixels_per_meter))
        self.l_tube.rect.left = 0
        self.l_tube.rect.centery = int(self.tube_center_y_m * pixels_per_meter)
        
        self.r_tube = Tube(self.surface, int(self.tube_width_m * pixels_per_meter), int(self.current_r_tube_height_m * pixels_per_meter))
        self.r_tube.rect.right = self.surface.get_width()
        self.r_tube.rect.centery = int(self.tube_center_y_m * pixels_per_meter)
        
        # Transition zone (in meters)
        self.transition_start_m = (self.surface.get_width() // 2 - 100) / pixels_per_meter  # Start of transition
        self.transition_end_m = (self.surface.get_width() // 2 + 100) / pixels_per_meter    # End of transition
        
        # Particle Config
        self.particle_size_m = 10 / pixels_per_meter
        self.base_speed_mps = 2 # meters per second
        self.particle_speed_mps = self.base_speed_mps
        self.particle_cols = []
        self.spawn_interval = 0.5 # seconds
        self.max_particles = 20  # Maximum number of particle columns
        self.particles_per_column = 8  # Number of particles in each column
        self.pressure = 1.0  # Pressure multiplier (still abstract)
        self.compression_started = False
        self.compression_timer = 0 # frames
        
        self.spawn_timer = Timer(self.spawn_interval, True)
        
        # Slider for Right Tube Height (controls height in meters)
        slider_w = 200
        slider_h = 20
        padding = 20
        slider_x = self.surface.get_width() - slider_w - padding
        slider_y = self.surface.get_height() - slider_h - padding
        slider_min_h_m = self.particle_size_m * 2
        slider_max_h_m = self.l_tube_height_m
        self.right_tube_slider = Slider(slider_x, slider_y, slider_w, slider_h, slider_min_h_m, slider_max_h_m, self.current_r_tube_height_m)

        # Initial fill
        self._initialFill()

    def _updateTubeSize(self):
        # Update the right tube object's dimensions and position (using pixels)
        self.r_tube.rect.height = int(self.current_r_tube_height_m * pixels_per_meter)
        self.r_tube.backborder.height = int(self.current_r_tube_height_m * pixels_per_meter + 10) # Keep border thickness in pixels
        self.r_tube.rect.centery = int(self.tube_center_y_m * pixels_per_meter)
        self.r_tube.backborder.center = self.r_tube.rect.center

    def _initialFill(self):
        # Generate particles in the left tube (using pixel coordinates for spawning range)
        generation_range_top_px = self.l_tube.rect.top
        generation_range_bot_px = self.l_tube.rect.bottom
        
        # Fill the tube with particles
        for _ in range(self.max_particles):
            # ParticleColumn expects speed in its own unit (which was pixels/frame), let's keep it that way internally for now
            # The speed calculation will be done in meters/s and then converted for the ParticleColumn
            newCol = ParticleColumn(self.surface, int(self.particle_size_m * pixels_per_meter), self.particles_per_column, self.base_speed_mps * pixels_per_meter / self.FPS, (generation_range_top_px, generation_range_bot_px))
            newCol.rect.x = randint(0, self.surface.get_width() // 2)  # Distribute particles in the left tube (in pixels)
            self.particle_cols.append(newCol)
            
    def _getTubeHeightAtX_m(self, x_pos_px):
        x_pos_m = x_pos_px / pixels_per_meter
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
        x_pos_m = x_pos_px / pixels_per_meter
        
        # Calculate target velocity in the narrow tube using continuity equation
        # v2 = v1 * (A1 / A2) -> v2 = v1 * (H1 / H2) in 2D
        target_speed_narrow_mps = self.base_speed_mps * (self.l_tube_height_m / self.current_r_tube_height_m) if self.current_r_tube_height_m > 0 else self.base_speed_mps

        if x_pos_m < self.transition_start_m:
            return self.base_speed_mps
        elif x_pos_m > self.transition_end_m:
             # Apply calculated speed in narrow tube, potentially scaled by abstract pressure
            return target_speed_narrow_mps # * self.pressure # Decide if pressure still scales speed here
        else:
            # Calculate how far through the transition zone the particle is (0 to 1) in meters
            transition_progress = (x_pos_m - self.transition_start_m) / (self.transition_end_m - self.transition_start_m)
            # Smooth the transition using a quadratic function
            transition_progress = transition_progress * transition_progress
            
             # Interpolate between base speed and target speed in narrow tube
            interpolated_speed_mps = self.base_speed_mps + (target_speed_narrow_mps - self.base_speed_mps) * transition_progress
            return interpolated_speed_mps # * self.pressure # Decide if pressure still scales speed here
    
    def _updatePhysics(self):
        # Calculate pressure based on the ratio of the left tube height to the current right tube height
        compression_ratio = self.l_tube_height_m / self.current_r_tube_height_m if self.current_r_tube_height_m > 0 else 1.0
        # Base pressure is 1.0, it increases as the tube gets narrower (this is still an abstract pressure value)
        self.pressure = 1.0 + (compression_ratio - 1.0) * (len(self.particle_cols) / self.max_particles)
        
        # Update particle speeds and positions based on their location
        for col in self.particle_cols:
            # Calculate speed in meters/s based on position
            speed_mps = self._calculateSpeedAtX_mps(col.rect.centerx)
            # Convert speed to pixels per frame for the ParticleColumn
            col.travel_speed = speed_mps * pixels_per_meter / self.FPS
            
            # Calculate current tube height at particle's x position (in meters)
            current_tube_height_m = self._getTubeHeightAtX_m(col.rect.centerx)
            
            # Calculate vertical spacing based on current tube height (in meters)
            # Ensure spacing is not zero if current_tube_height_m is very small
            spacing_m = current_tube_height_m / (self.particles_per_column + 1) if self.particles_per_column + 1 > 0 else current_tube_height_m
            
            # Update particle positions to be centered vertically within the current tube height (using pixels)
            tube_top_y_m = self.tube_center_y_m - current_tube_height_m / 2
            tube_top_y_px = int(tube_top_y_m * pixels_per_meter)
            
            for i, particle in enumerate(col.particles):
                target_y_m = tube_top_y_m + spacing_m * (i + 1)
                target_y_px = int(target_y_m * pixels_per_meter)
                
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
                initial_speed_px_per_frame = self.base_speed_mps * pixels_per_meter / self.FPS
                newCol = ParticleColumn(self.surface, int(self.particle_size_m * pixels_per_meter), self.particles_per_column, initial_speed_px_per_frame, (generation_range_top_px, generation_range_bot_px))
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
        l_tube_bottomright = (self.l_tube.rect.right, int(self.tube_center_y_m * pixels_per_meter + self.l_tube_height_m * pixels_per_meter / 2))
        r_tube_topleft = self.r_tube.rect.topleft
        r_tube_bottomleft = (self.r_tube.rect.left, int(self.tube_center_y_m * pixels_per_meter + self.current_r_tube_height_m * pixels_per_meter / 2))
        
        tube_connector_points = [l_tube_topright, l_tube_bottomright, r_tube_bottomleft, r_tube_topleft]
        # Draw in pixels
        pygame.draw.polygon(self.surface, self.l_tube.bb_col, tube_connector_points, 12)
        pygame.draw.polygon(self.surface, self.l_tube.tube_col, tube_connector_points)
        
    def __event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
            
            # Handle slider events (slider value is in meters)
            if self.right_tube_slider.handle_event(e):
                self.current_r_tube_height_m = self.right_tube_slider.value
                self._updateTubeSize()

    
    def __update(self):
        self.surface.fill((255,255,255))
        
        self._updatePhysics()
        self._generateParticles()
        
        self._drawConnector()
        self.l_tube.draw()
        self.r_tube.draw()
        
        self._drawParticles()
        
        # Draw the slider
        self.right_tube_slider.draw(self.surface)
        
        # Display information
        font = pygame.font.Font(None, 36)
        
        # Display initial velocity, current velocity in narrow tube, and right tube height in meters
        initial_vel_text = font.render(f"Initial Velocity: {self.base_speed_mps:.2f} m/s", True, (0, 0, 0))
        
        # Calculate and display current velocity in the narrow tube based on continuity
        current_vel_narrow_mps = self.base_speed_mps * (self.l_tube_height_m / self.current_r_tube_height_m) if self.current_r_tube_height_m > 0 else self.base_speed_mps
        current_vel_text = font.render(f"Velocity in Narrow Tube: {current_vel_narrow_mps:.2f} m/s", True, (0, 0, 0))
        
        tube_size_text = font.render(f"Right Tube Height: {self.current_r_tube_height_m:.2f} m", True, (0, 0, 0))
        
        # Display abstract pressure
        pressure_text = font.render(f"Abstract Pressure: {self.pressure:.2f}x", True, (0, 0, 0))
        
        # Calculate positions for bottom right text and slider
        padding = 20
        text_v_spacing = 30 # Vertical space between text lines
        
        # Position tube size text above the slider
        tube_size_text_rect = tube_size_text.get_rect()
        tube_size_text_x = self.surface.get_width() - tube_size_text_rect.width - padding
        tube_size_text_y = self.right_tube_slider.rect.y - tube_size_text_rect.height - 5 # 5 pixels padding above slider

        self.surface.blit(initial_vel_text, (10, 10))
        self.surface.blit(current_vel_text, (10, 50))
        self.surface.blit(pressure_text, (10, 130))
        
        # Blit tube size text at new bottom right position
        self.surface.blit(tube_size_text, (tube_size_text_x, tube_size_text_y))
        
        pygame.display.update()
    
    def run(self):
        while self.__running:
            self.__event()
            self.__update()
            self.clock.tick(self.FPS)
    
if __name__ == '__main__': main().run()
