
import pygame
import sys
from general import General
from opensimplex import OpenSimplex
import random
import numpy as np
from scipy.signal import convolve2d
from datetime import datetime
import math

class Visual():

    def __init__(self, general: General):

        self.general = general
        
        pygame.init()
        self.fps: int = 60 # in terms of simulation: 1 second = 1 day, 30 secons = 1 month and 360 seconds(6 minutes) = 1 year
        self.seconds_till_start: int = 0
        self.day: int = 0
        self.month: int = 0
        self.year: int = 0

        screen_info = pygame.display.Info()
        self.max_screen_width = screen_info.current_w
        self.max_screen_height = screen_info.current_h

        self.screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
        self.screen_height: int = self.screen.get_height()
        self.screen_width: int = self.screen.get_width()
        self.display_caption = pygame.display.set_caption("Artificial Ecological Simulation")
        self.clock = pygame.time.Clock()

        self.world = pygame.Surface((self.general.world_size, self.general.world_size))

        self.camera_x: int = 0
        self.camera_y: int = 0
        self.scroll_speed: int = 10
        self.zoom_level: float = 1.0
        self.min_zoom: float = 0.2 # show x5 more area
        self.max_zoom: float= 2.0 # show x2 less area
        self.zoom_speed: float = 0.1

        self.noise_elev = OpenSimplex(seed=1)
        self.noise_temp = OpenSimplex(seed=2)
        self.noise_hum = OpenSimplex(seed=3)
        self.noise_prod = OpenSimplex(seed=4)
        self.noise_scale: float = 0.02
        self.elevation_colors = {
            0: (46, 34, 22),    # Dark brown (highest elevation- mountain)
            1: (69, 50, 27),    # Medium brown
            2: (92, 66, 32),    # Light brown
            3: (115, 82, 37),   # Tan
            4: (138, 98, 42),   # Light tan
            5: (161, 114, 47),  # Sandy yellow
            6: (100, 150, 50),  # Light green
            7: (50, 120, 100),  # Teal 
            8: (30, 90, 150),   # Bright blue
            9: (10, 50, 100)   # Dark blue (lowest elevation - lake)
        }
        self.temperature_colors = {
            9: (0, 0, 100),       # Dark blue (coldest)
            8: (0, 0, 150),       # Medium dark blue
            7: (0, 0, 200),       # Bright blue
            6: (100, 150, 255),   # Very light blue
            5: (200, 200, 100),   # Pale yellow
            4: (255, 200, 50),    # Yellow
            3: (255, 175, 25),    # Bright orange
            2: (255, 150, 0),     # Orange
            1: (255, 100, 0),     # Bright orange
            0: (255, 0, 0)       # Red (hottest)
        }
        self.humidity_colors = {
            9: (255, 0, 0),       # Red (driest)
            8: (255, 50, 50),     # Light red
            7: (255, 100, 100),   # Pale red
            6: (255, 150, 150),   # Pinkish red
            5: (255, 180, 180),   # Light pink
            4: (255, 200, 200),   # Pale pink
            3: (255, 220, 220),   # Very light pink
            2: (255, 230, 230),   # Almost white pink
            1: (255, 240, 240),   # White-pink
            0: (255, 255, 255)   # white
        }
        self.radioactivity_colors = {
            9: (255, 255, 255),  # White (lowest)
            8: (230, 255, 230),  # Very light green
            7: (200, 255, 200),  # Light green
            6: (150, 255, 150),  # Pale green
            5: (100, 255, 100),  # Soft green
            4: (50, 255, 50),    # Medium green
            3: (0, 255, 0),      # Bright green
            2: (0, 200, 0),      # Strong green
            1: (0, 150, 0),      # Dark green
            0: (0, 100, 0)      # Very dark green (maximum)
        }
        self.productivity_colors = {
            9: (128, 0, 128),    # Purple
            8: (113, 28, 113),
            7: (98, 56, 98),
            6: (83, 85, 83),
            5: (68, 113, 68),
            4: (53, 141, 53),
            3: (38, 170, 38),
            2: (23, 198, 23),
            1: (8, 226, 8),
            0: (0, 255, 0)       # Pure Green
        }
        self.square_kernel = np.ones((21, 21))
        # create the circle kernel
        self.circle_kernel = np.zeros((2*5+1, 2*5+1)) # 2*radius+1
        y, x = np.ogrid[-5:6, -5:6]
        distance = np.sqrt(x**2+y**2)
        self.circle_kernel[distance<=5]=1
        self.circle_kernel/=np.sum(self.circle_kernel)
        # load all the already created matrices
        self.all_matrices = np.load("map_1234.npz")
        self.elevation_matrix = self.all_matrices["elevation_smoothed_matrix"]
        print(type(self.elevation_matrix))
        self.temperature_matrix = self.all_matrices["temperature_smoothed_matrix"]
        self.humidity_matrix = self.all_matrices["humidity_smoothed_matrix"]
        self.radioactivity_matrix = self.all_matrices["radioactivity_smoothed_matrix"]
        self.productivity_matrix = self.all_matrices["productivity_smoothed_matrix"]

        self.running: bool = True
        self.choosen_map: int = 1 # shown map on the display, inputted from the user
        self.set_camera()
        self.show_simulation_info(self.day, self.month, self.year)

        self.simulation_start_time = datetime.now()



    # 1) general settings
    def handle_input(self) -> bool:
        keys = pygame.key.get_pressed()
        # camera movement
        if keys[pygame.K_LEFT]:
            self.camera_x -= self.scroll_speed/self.zoom_level
        if keys[pygame.K_RIGHT]:
            self.camera_x += self.scroll_speed/self.zoom_level
        if keys[pygame.K_UP]:
            self.camera_y -= self.scroll_speed/self.zoom_level
        if keys[pygame.K_DOWN]:
            self.camera_y += self.scroll_speed/self.zoom_level
        # zoom controls
        if keys[pygame.K_z]:
            self.zoom_level = min(self.zoom_level+self.zoom_speed, self.max_zoom)
        if self.zoom_level > 1.0:
            if keys[pygame.K_x]:
                self.zoom_level = max(self.zoom_level-self.zoom_speed, self.min_zoom)
        # keep the camera within bounds
        max_camera_x = self.general.world_size - (self.screen_width/self.zoom_level)
        max_camera_y = self.general.world_size - (self.screen_height/self.zoom_level)
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

        if sum(keys):
            return True
        else:
            return False

    def handle_resize(self, event) -> None:
        self.screen_width = event.w
        self.screen_height = event.h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

    def set_camera(self) -> None:
        self.screen.fill(self.general.colors["white"])

        view_height = int(self.screen_height/self.zoom_level)
        view_width = int(self.screen_width/self.zoom_level)

        visible_area = pygame.Surface((view_width, view_height))
        visible_area.blit(self.world, (0, 0), (self.camera_x, self.camera_y, view_width, view_height))

        scaled_surface = pygame.transform.scale(visible_area, (self.screen_width, self.screen_height))
        self.screen.blit(scaled_surface, (0, 0))

        # information on the screen
        font = pygame.font.Font(None, 20)
        settings_info: list[str] = [
            f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})",
            f"Zoom: {self.zoom_level:.2f}x",
            f"Screen: {self.screen_width}x{self.screen_height}",
            "Arrows: Move camera",
            "Z/X: Zoom in/out",
            "0: Blank Map",
            "1: Grid Map(default)",
            "2: Biome Map",
            "3: Elevation Map",
            "4: Temperature Map",
            "5: Humidity Map",
            "6: Radioactivity Map",
            "7: Productivity Map",
        ]
        for i, text in enumerate(settings_info):
            settings_text_surface = font.render(text, True, self.general.colors["red"])
            self.screen.blit(settings_text_surface, (10, 10+i*25))

    def show_simulation_info(self, day: int, month: int, year: int) -> None:
        pygame.draw.rect(self.screen, self.general.colors["purple"], (self.screen_width-105, 0, 105, 100))
        simulation_info: list[str] = [
            "Days Elapsed: ",
            f"Day: {self.seconds_till_start%30}",
            f"Month: {self.seconds_till_start//30}",
            f"Year: {self.seconds_till_start//360}"
        ]
        font = pygame.font.Font(None, 20)
        for i, text in enumerate(simulation_info):
            simulation_text_surface = font.render(text, True, self.general.colors["yellow"])
            self.screen.blit(simulation_text_surface, (self.screen_width-100, 10+i*25))

    # 2) code snippet for the map generation
    def draw_grid_map(self) -> None:
        for y in range(0, self.screen_width+30, 10):
            pygame.draw.line(self.world, self.general.colors["gray"], (self.camera_x+y-20, self.camera_y-20), (self.camera_x+y-20, self.camera_y+self.screen_height+20))
        for x in range(0, self.screen_height+30, 10):
            pygame.draw.line(self.world, self.general.colors["gray"], (self.camera_x-20, self.camera_y+x-20), (self.camera_x+self.screen_width+20, self.camera_y+x-20))

    def get_elevation(self, x: int, y: int) -> float:
        e: float = 1 * self.noise_elev.noise2(x * self.noise_scale * 1, y * self.noise_scale * 1)
        e += 0.5 * self.noise_elev.noise2(x * self.noise_scale * 2, y * self.noise_scale * 2)
        e += 0.25 * self.noise_elev.noise2(x * self.noise_scale * 4, y * self.noise_scale * 4)
        return (e + 1) / 2

    def determine_elevation_color(self, elev: float) -> int:
        # low elevation = 9,lake / high elevation = 0,mountain
        if elev <= 0.1: return 9
        elif elev <= 0.2: return 8
        elif elev <= 0.3: return 7
        elif elev <= 0.4: return 6
        elif elev <= 0.5: return 5
        elif elev <= 0.6: return 4
        elif elev <= 0.7: return 3
        elif elev <= 0.8: return 2
        elif elev <= 0.9: return 1
        else: return 0

    def get_temperature(self, x: int, y: int, elevation: float) -> float:
        # Base temperature from elevation
        base_temp: float = (1.0 - 2*elevation) * 0.7
        
        # Fractal noise for variation
        noise_scale: float = 0.05
        noise: float = (
            1.0 * self.noise_temp.noise2(x * noise_scale * 1, y * noise_scale * 1) +
            0.5 * self.noise_temp.noise2(x * noise_scale * 2, y * noise_scale * 2) +
            0.25 * self.noise_temp.noise2(x * noise_scale * 4, y * noise_scale * 4)
        ) / 1.75  # Normalize
        noise *= 0.3  # Limit noise strength
        
        # Combine and clamp
        temperature: float = base_temp + noise 

        # adjust temperature for lakes
        if elevation <= 0.2:
            lake_effect = elevation*0.2
            temperature += lake_effect

        return max(-1.0, min(1.0, temperature))
    
    def determine_temperature_color(self, temperature: float) -> int:
        if temperature <= -0.7: return 9
        elif temperature <= -0.6: return 8
        elif temperature <= -0.5: return 7
        elif temperature <= -0.3: return 6
        elif temperature <= -0.1: return 5
        elif temperature <= 0.3: return 4
        elif temperature <= 0.5: return 3
        elif temperature <= 0.6: return 2
        elif temperature <= 0.9: return 1
        else: return 0

    def get_humidity(self, x: int, y: int, elevation: float) -> float:
        base_hum: float = (1.0 - elevation)*0.9

        noise_scale: int = 0.05
        noise: float = (
            1.0*self.noise_hum.noise2(x*noise_scale*1, y*noise_scale*1)+
            0.5*self.noise_hum.noise2(x*noise_scale*2, y*noise_scale*2)+
            0.25*self.noise_hum.noise2(x*noise_scale*4, y*noise_scale*4)
        )/1.75
        noise *= 0.10

        humidity: float = base_hum + noise

        return max(0, min(1.0, humidity))

    def determine_humidity_color(self, humidity: float) -> int:
        if humidity <= 0.1: return 9
        elif humidity <= 0.2: return 8
        elif humidity <= 0.3: return 7
        elif humidity <= 0.4: return 6
        elif humidity <= 0.5: return 5
        elif humidity <= 0.6: return 4
        elif humidity <= 0.7: return 3
        elif humidity <= 0.8: return 2
        elif humidity <= 0.9: return 1
        else: return 0

    def get_radioactivity(self, zone_count: int = 4) -> tuple[list[int, int], list[int, int], list[int]]:
        all_source_positions = []
        all_drain_value = []
        all_drain_positions = []
        for _ in range(zone_count):
            source_x = random.randint(0, self.general.world_size-1)
            source_y = random.randint(0, self.general.world_size-1)
            while (source_x, source_y) in all_source_positions:
                source_x = random.randint(0, self.general.world_size-1)
                source_y = random.randint(0, self.general.world_size-1)
            all_source_positions.append((source_y, source_x,))
            for _ in range(500):
                drain_x_position = max(min(source_x - random.randint(-25, 25), self.general.world_size-1), 0)
                drain_y_position = max(min(source_y - random.randint(-25, 25), self.general.world_size-1), 0)
                drain_value = 1 - random.uniform(0, 0.5)
                while (drain_x_position, drain_y_position) in all_drain_positions:
                    drain_x_position = max(min(source_x - random.randint(-25, 25), self.general.world_size-1), 0)
                    drain_y_position = max(min(source_y - random.randint(-25, 25), self.general.world_size-1), 0)
                all_drain_positions.append((drain_y_position, drain_x_position)) 
                all_drain_value.append(drain_value)

        return (all_source_positions, all_drain_positions, all_drain_value)

    def determine_radioactivity_color(self, radioactivity: float) -> int:
        if radioactivity <= 0.1: return 0
        elif radioactivity <= 0.2: return 1
        elif radioactivity <= 0.3: return 2
        elif radioactivity <= 0.4: return 3
        elif radioactivity <= 0.5: return 4
        elif radioactivity <= 0.6: return 5
        elif radioactivity <= 0.7: return 6
        elif radioactivity <= 0.8: return 7
        elif radioactivity <= 0.9: return 8
        else: return 9

    def get_productivity(self, x: int, y, humidity: float, radioactivity: float) -> float:

        productivity: float = 1 * self.noise_prod.noise2(x * self.noise_scale * 1, y * self.noise_scale * 1)
        productivity += 0.5 * self.noise_prod.noise2(x * self.noise_scale * 2, y * self.noise_scale * 2)
        productivity += 0.25 * self.noise_prod.noise2(x * self.noise_scale * 4, y * self.noise_scale * 4)
        productivity = (productivity + 1) * humidity

        if radioactivity > 0.7:
            productivity = 1
        elif radioactivity > 0.3:
            productivity *= radioactivity * 2

        return productivity

    def determine_productivity_color(self, productivity: float) -> int:
        if productivity <= 0.1: return 9
        elif productivity <= 0.2: return 8
        elif productivity <= 0.3: return 7
        elif productivity <= 0.4: return 6
        elif productivity <= 0.5: return 5
        elif productivity <= 0.6: return 4
        elif productivity <= 0.7: return 3
        elif productivity <= 0.8: return 2
        elif productivity <= 0.9: return 1
        else: return 0

    def calculate_elevation_matrix(self) -> list[list[int]]:
        elevation_matrix = [[self.get_elevation(x, y) for x in range(self.general.world_size)] for y in range(self.general.world_size)]
        elevation_matrix_np = np.array(elevation_matrix)
        elevation_sum = convolve2d(elevation_matrix_np, self.square_kernel, mode="same", boundary="fill")
        elevation_counts = convolve2d(np.ones_like(elevation_matrix_np), self.square_kernel, mode="same", boundary="fill")
        elevation_smoothed_matrix = elevation_sum / elevation_counts # np array matrix
        return elevation_smoothed_matrix

    def calculate_temperature_matrix(self, elevation_matrix: list[list[int]]) -> list[list[int]]:
        temperature_matrix = [[self.get_temperature(x, y, elevation_matrix[y][x]) for x in range(self.general.world_size)] for y in range(self.general.world_size)]
        temperature_matrix_np = np.array(temperature_matrix)
        temperature_sum = convolve2d(temperature_matrix_np, self.square_kernel, mode="same", boundary="fill")
        temperature_counts = convolve2d(np.ones_like(temperature_matrix_np), self.square_kernel, mode="same", boundary="fill")
        temperature_smoothed_matrix = temperature_sum / temperature_counts # np array matrix
        return temperature_smoothed_matrix

    def calculate_humidity_matrix(self, elevation_matrix: list[list[int]]) -> list[list[int]]:
        humidity_matrix = [[self.get_humidity(x, y, elevation_matrix[y][x]) for x in range(self.general.world_size)] for y in range(self.general.world_size)]
        humidity_matrix_np = np.array(humidity_matrix)
        humidity_sum = convolve2d(humidity_matrix_np, self.square_kernel, mode="same", boundary="fill")
        humidity_counts = convolve2d(np.ones_like(humidity_matrix_np), self.square_kernel, mode="same", boundary="fill")
        humidity_smoothed_matrix = humidity_sum / humidity_counts # np array matrix
        return humidity_smoothed_matrix

    def calculate_radioactivity_matrix(self) -> list[list[int]]:
        radioactive_sources, radioactive_drain_positions, radioactive_drain_values = self.get_radioactivity()
        radioactivity_matrix = np.zeros((self.general.world_size, self.general.world_size))
        for source_y, source_x  in radioactive_sources:
            radioactivity_matrix[source_y][source_x] = 1
        for i in range(len(radioactive_drain_values)):
            drain_y, drain_x = radioactive_drain_positions[i]
            radioactivity_matrix[drain_y][drain_x] = radioactive_drain_values[i]
        radioactivity_matrix_np = np.array(radioactivity_matrix)
        radioactivity_sum = convolve2d(radioactivity_matrix_np, self.circle_kernel, mode="same", boundary="fill")
        radioactivity_counts = convolve2d(np.ones_like(radioactivity_matrix_np), self.circle_kernel, mode="same", boundary="fill")
        radioactivity_smoothed_matrix = (radioactivity_sum*10) / radioactivity_counts
        return radioactivity_smoothed_matrix

    def calculate_productivity_matrix(self, humidity_matrix: list[list[int]], radioactivity_smoothed_matrix: list[list[int]]) -> list[int]:
        productivity_matrix = [[self.get_productivity(x, y, humidity_matrix[y][x], radioactivity_smoothed_matrix[y][x]) for x in range(self.general.world_size)] for y in range(self.general.world_size)]
        productivity_matrix_np = np.array(productivity_matrix)
        productivity_sum = convolve2d(productivity_matrix_np, self.square_kernel, mode="same", boundary="fill")
        productivity_counts = convolve2d(np.ones_like(productivity_matrix_np), self.square_kernel, mode="same", boundary="fill")
        productivity_smoothed_matrix = productivity_sum / productivity_counts
        return productivity_smoothed_matrix

    def smooth_the_map(matrix: list[list[float]], smoothing_factor: int = 10) -> list[list[float]]:
        smoothed: list[list[float]] = []
        for row in matrix:
            for _ in range(smoothing_factor):
                new_row: list[float] = []
                for value in row:
                    new_row.extend([value] * smoothing_factor)
                smoothed.append(new_row)
        return smoothed

    def draw_elevation_map(self) -> None:
        for x in range(-30, self.screen_width+30, 10):
            for y in range(-30, self.screen_height+30, 10):
                elevation_color_no: int = self.determine_elevation_color(self.elevation_matrix[min(self.general.world_size-1, max(0, int(self.camera_y+y)))][min(self.general.world_size-1, max(0, int(self.camera_x+x)))])
                pygame.draw.rect(self.world, self.elevation_colors[elevation_color_no], ((min(self.general.world_size-1, max(0, int(self.camera_x+x))), min(self.general.world_size-1, max(0, int(self.camera_y+y))), 9, 9)))

    def draw_temperature_map(self) -> None:
        for x in range(-30, self.screen_width+30, 10):
            for y in range(-30, self.screen_height+30, 10):
                temperature_color_no: int = self.determine_temperature_color(self.temperature_matrix[min(self.general.world_size-1, max(0, int(self.camera_y+y)))][min(self.general.world_size-1, max(0, int(self.camera_x+x)))])
                pygame.draw.rect(self.world, self.temperature_colors[temperature_color_no], ((min(self.general.world_size-1, max(0, int(self.camera_x+x))), min(self.general.world_size-1, max(0, int(self.camera_y+y))), 9, 9)))

    def draw_humidity_map(self) -> None:
        for x in range(-30, self.screen_width+30, 10):
            for y in range(-30, self.screen_height+30, 10):
                humidity_color_no: int = self.determine_humidity_color(self.humidity_matrix[min(self.general.world_size-1, max(0, int(self.camera_y+y)))][min(self.general.world_size-1, max(0, int(self.camera_x+x)))])
                pygame.draw.rect(self.world, self.humidity_colors[humidity_color_no], ((min(self.general.world_size-1, max(0, int(self.camera_x+x))), min(self.general.world_size-1, max(0, int(self.camera_y+y))), 9, 9)))

    def draw_radioactivity_map(self) -> None:
        for x in range(-30, self.screen_width+30, 10):
            for y in range(-30, self.screen_height+30, 10):
                radioactivity_color_no: int = self.determine_temperature_color(self.radioactivity_matrix[min(self.general.world_size-1, max(0, int(self.camera_y+y)))][min(self.general.world_size-1, max(0, int(self.camera_x+x)))])
                pygame.draw.rect(self.world, self.radioactivity_colors[radioactivity_color_no], ((min(self.general.world_size-1, max(0, int(self.camera_x+x))), min(self.general.world_size-1, max(0, int(self.camera_y+y))), 9, 9)))

    def draw_productivity_map(self) -> None:
        for x in range(-30, self.screen_width+30, 10):
            for y in range(-30, self.screen_height+30, 10):
                productivity_color_no: int = self.determine_productivity_color(self.productivity_matrix[min(self.general.world_size-1, max(0, int(self.camera_y+y)))][min(self.general.world_size-1, max(0, int(self.camera_x+x)))])
                pygame.draw.rect(self.world, self.productivity_colors[productivity_color_no], ((min(self.general.world_size-1, max(0, int(self.camera_x+x))), min(self.general.world_size-1, max(0, int(self.camera_y+y))), 9, 9)))

    #3) code snippet for seasonal change
    def update_temperatures(self, phase_shift: int = 0, randomness: float = 0):
        """Vectorized monthly temperature update for entire matrix"""
        day_of_year: int = self.month * 30  
        
        # Single calculation for all cells
        radian = (2 * np.pi / 365) * (day_of_year - phase_shift)
        seasonal_swing = np.sin(radian) * self.elevation_matrix / 50
        
        # In-place operations for memory efficiency
        np.add(self.temperature_matrix, seasonal_swing, out=self.temperature_matrix)
        np.add(self.temperature_matrix, 
            np.random.uniform(-randomness, randomness, self.temperature_matrix.shape),
            out=self.temperature_matrix)
        # In-place clipping avoids creating new array
        np.clip(self.temperature_matrix, -1.0, 1.0, out=self.temperature_matrix)

    # main running function
    def run(self):

        while self.running:
            for event in pygame.event.get():
                # keyboard event handling
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_0:
                        self.choosen_map = 0
                    elif event.key == pygame.K_1:
                        self.choosen_map = 1
                    elif event.key == pygame.K_2:
                        self.choosen_map = 2
                    elif event.key == pygame.K_3:
                        self.choosen_map = 3
                    elif event.key == pygame.K_4:
                        self.choosen_map = 4
                    elif event.key == pygame.K_5:
                        self.choosen_map = 5
                    elif event.key == pygame.K_6:
                        self.choosen_map = 6
                    elif event.key == pygame.K_7:
                        self.choosen_map = 7
                # resizing the screen
                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)

            # show the simulation info regardless
            self.show_simulation_info(self.day, self.month, self.year)

            # start of real loop
            key_pressed: bool = self.handle_input()
            
            # change the map, according to user input
            if key_pressed:
                self.set_camera()
                self.show_simulation_info(self.day, self.month, self.year)
                if self.choosen_map == 0:
                    self.world.fill(self.general.colors["white"])
                elif self.choosen_map == 1:
                    self.world.fill(self.general.colors["white"])
                    self.draw_grid_map()
                elif self.choosen_map == 2:
                    pass
                elif self.choosen_map == 3:
                    self.world.fill(self.general.colors["white"])
                    self.draw_elevation_map()
                elif self.choosen_map == 4:
                    self.world.fill(self.general.colors["white"])
                    self.draw_temperature_map()
                elif self.choosen_map == 5:
                    self.world.fill(self.general.colors["white"])
                    self.draw_humidity_map()
                elif self.choosen_map == 6:
                    self.world.fill(self.general.colors["white"])
                    self.draw_radioactivity_map()
                elif self.choosen_map == 7:
                    self.world.fill(self.general.colors["white"])
                    self.draw_productivity_map()

            pygame.display.update()
            self.clock.tick(self.fps)

            self.seconds_till_start: int = int((datetime.now() - self.simulation_start_time).total_seconds())
            self.day = self.seconds_till_start%30
            self.month = (self.seconds_till_start//30)%12
            self.year = self.seconds_till_start//360
            # update the temperature matrix monthly to keep up with the seasonal changes
            if self.day//29 == 1:
                self.update_temperatures()

        pygame.quit()
        
if __name__ == "__main__":
    test_general = General()
    test_visual = Visual(test_general)
    test_visual.run()
    sys.exit()
