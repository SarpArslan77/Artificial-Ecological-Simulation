import pygame
import sys
from opensimplex import OpenSimplex
import numpy as np
from scipy.signal import convolve2d
import random

# Initialize noise generator
noise_elev = OpenSimplex(seed=1)
noise_temp = OpenSimplex(seed=67)
noise_hum = OpenSimplex(seed=250)
noise_prod = OpenSimplex(seed=700)

# Map parameters
WIDTH, HEIGHT = 250, 250
SCALE = 0.02

# Biome color map
ELEVATION_COLORS = {
    0: (46, 34, 22),    # Dark brown (lowest elevation)
    1: (69, 50, 27),    # Medium brown
    2: (92, 66, 32),    # Light brown
    3: (115, 82, 37),   # Tan
    4: (138, 98, 42),   # Light tan
    5: (161, 114, 47),  # Sandy yellow
    6: (100, 150, 50),  # Light green
    7: (50, 120, 100),  # Teal (transition to blue)
    8: (30, 90, 150),   # Bright blue
    9: (10, 50, 100)   # Dark blue (hig
}

TEMPERATURE_COLORS = {
    9: (0, 0, 100),       # Dark blue (coldest)
    8: (0, 0, 150),       # Medium dark blue
    7: (0, 0, 200),       # Bright blue
    6: (100, 150, 255),   # Very light blue
    5: (200, 200, 100),   # Pale yellow
    4: (255, 200, 50),    # Yellow
    3: (255, 175, 25),    # Bright Orange
    2: (255, 150, 0),     # Orange
    1: (255, 100, 0),     # Bright orange
    0: (255, 0, 0)       # Red (hottest)
}

HUMIDITY_COLORS = {
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

RADIOACTIVITY_COLORS = {
    0: (255, 255, 255),  # White (lowest)
    1: (230, 255, 230),  # Very light green
    2: (200, 255, 200),  # Light green
    3: (150, 255, 150),  # Pale green
    4: (100, 255, 100),  # Soft green
    5: (50, 255, 50),    # Medium green
    6: (0, 255, 0),      # Bright green
    7: (0, 200, 0),      # Strong green
    8: (0, 150, 0),      # Dark green
    9: (0, 100, 0)      # Very dark green (maximum)
}

PRODUCTIVITY_COLORS = {
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

def get_elevation(x, y):
    e = 1 * noise_elev.noise2(x * SCALE * 1, y * SCALE * 1)
    e += 0.5 * noise_elev.noise2(x * SCALE * 2, y * SCALE * 2)
    e += 0.25 * noise_elev.noise2(x * SCALE * 4, y * SCALE * 4)
    return (e + 1) / 2

def determine_elevation_color(elev):
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

def get_temperature(x, y, elevation):
    # Base temperature from elevation
    base_temp = (1.0 - 2*elevation) * 0.7
    
    # Fractal noise for variation
    noise_scale = 0.05
    noise = (
        1.0 * noise_temp.noise2(x * noise_scale * 1, y * noise_scale * 1) +
        0.5 * noise_temp.noise2(x * noise_scale * 2, y * noise_scale * 2) +
        0.25 * noise_temp.noise2(x * noise_scale * 4, y * noise_scale * 4)
    ) / 1.75  # Normalize
    noise *= 0.3  # Limit noise strength
    
    # Combine and clamp
    temperature = base_temp + noise 

    # adjust temperature for lakes
    if elevation <= 0.2:
        lake_effect = elevation*0.2
        temperature += lake_effect

    return max(-1.0, min(1.0, temperature))

def determine_temperature_color(temperature):
    if temperature <= -0.9: return 9
    elif temperature <= -0.7: return 8
    elif temperature <= -0.5: return 7
    elif temperature <= -0.3: return 6
    elif temperature <= -0.1: return 5
    elif temperature <= 0.3: return 4
    elif temperature <= 0.5: return 3
    elif temperature <= 0.6: return 2
    elif temperature <= 0.9: return 1
    else: return 0

def get_humidity(x, y, elevation):
    base_hum = (1.0 - elevation)*0.9

    noise_scale = 0.05
    noise = (
        1.0*noise_hum.noise2(x*noise_scale*1, y*noise_scale*1)+
        0.5*noise_hum.noise2(x*noise_scale*2, y*noise_scale*2)+
        0.25*noise_hum.noise2(x*noise_scale*4, y*noise_scale*4)
    )/1.75
    noise *= 0.10

    humidity = base_hum + noise

    return max(0, min(1.0, humidity))

def determine_humidity_color(humidity):
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

def get_radioactivity(zone_count):
    all_source_positions = []
    all_drain_value = []
    all_drain_positions = []
    for _ in range(zone_count):
        source_x = random.randint(0, WIDTH-1)
        source_y = random.randint(0, HEIGHT-1)
        while (source_x, source_y) in all_source_positions:
            source_x = random.randint(0, WIDTH-1)
            source_y = random.randint(0, HEIGHT-1)
        all_source_positions.append((source_y, source_x,))
        for _ in range(500):
            drain_x_position = max(min(source_x - random.randint(-25, 25), WIDTH-1), 0)
            drain_y_position = max(min(source_y - random.randint(-25, 25), HEIGHT-1), 0)
            drain_value = 1 - random.uniform(0, 0.5)
            while (drain_x_position, drain_y_position) in all_drain_positions:
                drain_x_position = max(min(source_x - random.randint(-25, 25), WIDTH-1), 0)
                drain_y_position = max(min(source_y - random.randint(-25, 25), HEIGHT-1), 0)
            all_drain_positions.append((drain_y_position, drain_x_position)) 
            all_drain_value.append(drain_value)

    return (all_source_positions, all_drain_positions, all_drain_value)
    
def determine_radioactivity_color(radioactivity):
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

def get_productivity(x, y, humidity, radioactivity):

    productivity = 1 * noise_prod.noise2(x * SCALE * 1, y * SCALE * 1)
    productivity += 0.5 * noise_prod.noise2(x * SCALE * 2, y * SCALE * 2)
    productivity += 0.25 * noise_prod.noise2(x * SCALE * 4, y * SCALE * 4)
    productivity = (productivity + 1) * humidity

    if radioactivity > 0.7:
        productivity = 1
    elif radioactivity > 0.3:
        productivity *= radioactivity * 2

    return productivity
    
def determine_productivity_color(productivity):
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

def smooth_the_map(matrix: list[list[float]], smoothing_factor: int) -> list[list[float]]:
    """Convert 100x100 matrix to 1000x1000 by repeating values 10x10 times"""
    smoothed = []
    # For each row in original matrix
    for row in matrix:
        # Repeat the row vertically 10 times
        for _ in range(smoothing_factor):
            new_row = []
            # Repeat each value horizontally 10 times
            for value in row:
                new_row.extend([value] * smoothing_factor)
            smoothed.append(new_row)
    return smoothed


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH*3, HEIGHT))  # Double width for side-by-side
pygame.display.set_caption("Original (Left) vs Smoothed (Right)")

print("starting_with_the_procedure")
# Generate original matrix
kernel_size = 21
square_kernel = np.ones((kernel_size, kernel_size))

elevation_matrix = [[get_elevation(x, y) for x in range(WIDTH)] for y in range(HEIGHT)]
elevation_matrix_np = np.array(elevation_matrix)
elevation_sum = convolve2d(elevation_matrix_np, square_kernel, mode="same", boundary="fill")
elevation_counts = convolve2d(np.ones_like(elevation_matrix_np), square_kernel, mode="same", boundary="fill")
elevation_smoothed_matrix = smooth_the_map(elevation_sum / elevation_counts, 10) # np array matrix
#print(len(elevation_smoothed_matrix))
print("elevation_matrix is done")
print()

temperature_matrix = [[get_temperature(x, y, elevation_matrix[y][x]) for x in range(WIDTH)] for y in range(HEIGHT)]
temperature_matrix_np = np.array(temperature_matrix)
temperature_sum = convolve2d(temperature_matrix_np, square_kernel, mode="same", boundary="fill")
temperature_counts = convolve2d(np.ones_like(temperature_matrix_np), square_kernel, mode="same", boundary="fill")
temperature_smoothed_matrix = smooth_the_map(temperature_sum / temperature_counts, 10) # np array matrix
print("temperature_matrix is done")
print()

humidity_matrix = [[get_humidity(x, y, elevation_matrix[y][x]) for x in range(WIDTH)] for y in range(HEIGHT)]
humidity_matrix_np = np.array(humidity_matrix)
humidity_sum = convolve2d(humidity_matrix_np, square_kernel, mode="same", boundary="fill")
humidity_counts = convolve2d(np.ones_like(humidity_matrix_np), square_kernel, mode="same", boundary="fill")
humidity_smoothed_matrix = smooth_the_map(humidity_sum / humidity_counts, 10) # np array matrix
print("humidity_matrix is done")
print()

radius = 5
diameter = 2*radius+1
circle_kernel = np.zeros((diameter, diameter))
y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
distance = np.sqrt(x**2+y**2)
circle_kernel[distance<=radius]=1
circle_kernel=circle_kernel/np.sum(circle_kernel)

radioactive_sources, radioactive_drain_positions, radioactive_drain_values = get_radioactivity(4)
radioactivity_matrix = np.zeros((HEIGHT, WIDTH))
for source_y, source_x  in radioactive_sources:
    radioactivity_matrix[source_y][source_x] = 1
for i in range(len(radioactive_drain_values)):
    drain_y, drain_x = radioactive_drain_positions[i]
    radioactivity_matrix[drain_y][drain_x] = radioactive_drain_values[i]
radioactivity_matrix_np = np.array(radioactivity_matrix)
radioactivity_sum = convolve2d(radioactivity_matrix_np, circle_kernel, mode="same", boundary="fill")
radioactivity_counts = convolve2d(np.ones_like(radioactivity_matrix_np), circle_kernel, mode="same", boundary="fill")
radioactivity_smoothed_matrix = smooth_the_map((radioactivity_sum*10) / radioactivity_counts, 10)
print("radioactivity_matrix is done")
print()

productivity_matrix = [[get_productivity(x, y, humidity_matrix[y][x], radioactivity_smoothed_matrix[y][x]) for x in range(WIDTH)] for y in range(HEIGHT)]
productivity_matrix_np = np.array(productivity_matrix)
productivity_sum = convolve2d(productivity_matrix_np, square_kernel, mode="same", boundary="fill")
productivity_counts = convolve2d(np.ones_like(productivity_matrix_np), square_kernel, mode="same", boundary="fill")
productivity_smoothed_matrix = smooth_the_map(productivity_sum / productivity_counts, 10)
print("productivity_matrix is done")
print()

"""all_smoothed_matrices = np.load("map_1234.npz")
elevation_smoothed_matrix = all_smoothed_matrices["elevation_smoothed_matrix"]
temperature_smoothed_matrix = all_smoothed_matrices["temperature_smoothed_matrix"]
humidity_smoothed_matrix = all_smoothed_matrices["humidity_smoothed_matrix"]
radioactivity_smoothed_matrix = all_smoothed_matrices["radioactivity_smoothed_matrix"]
productivity_smoothed_matrix = all_smoothed_matrices["productivity_smoothed_matrix"]"""

# Draw both maps side-by-side
for y in range(HEIGHT):
    for x in range(WIDTH):
        ### Original map (left side)
        #elevation_map = determine_elevation_color(elevation_matrix[y][x])
        #temperature_map = determine_temperature_color(temperature_matrix[y][x])
        #radioactivity_map = determine_radioactivity_color(radioactivity_matrix[y][x])

        ### Smoothed map (right side)
        elevation_smoothed_map = determine_elevation_color(elevation_smoothed_matrix[y][x])
        temperature_smoothed_map = determine_temperature_color(temperature_smoothed_matrix[y][x])
        humidity_smoothed_map = determine_humidity_color(humidity_smoothed_matrix[y][x])
        radioactivity_smoothed_map = determine_radioactivity_color(radioactivity_smoothed_matrix[y][x])
        productivity_smoothed_map = determine_productivity_color(productivity_smoothed_matrix[y][x])

        left_side_map = temperature_smoothed_map
        middle_side_map = humidity_smoothed_map
        right_side_map = productivity_smoothed_map

        screen.set_at((x, y), TEMPERATURE_COLORS[left_side_map])
        screen.set_at((x + WIDTH, y), HUMIDITY_COLORS[middle_side_map])
        screen.set_at((x+WIDTH*2, y), PRODUCTIVITY_COLORS[right_side_map])
    
    # Update progress every 50 rows
    if y % 50 == 0:
        pygame.display.flip()
        pygame.event.pump()


# Final update
pygame.display.flip()


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()

np.savez("map_1234.npz", elevation_smoothed_matrix=elevation_smoothed_matrix, 
         temperature_smoothed_matrix=temperature_smoothed_matrix, 
         humidity_smoothed_matrix=humidity_smoothed_matrix,
         radioactivity_smoothed_matrix=radioactivity_smoothed_matrix,
         productivity_smoothed_matrix=productivity_smoothed_matrix)

sys.exit()