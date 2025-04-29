import numpy as np

class General():

    world_size: int = 2500

    colors = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (125, 125, 125),
        "red": (255, 0, 0),
        "green" : (0, 255, 0),
        "blue" : (0, 0, 255),
        "purple" : (128, 0, 128),
        "yellow" : (255, 255, 0),
        "brown" : (90, 50, 10),
        "orange" : (255, 165, 0),
    }

    total_grid_cells: int = (world_size//10)**2

    area_1x1: list[tuple[int, int]] = [
        (-10, -10), (-10, 0), (-10, 10),
        (0, -10), (0, 10),
        (10, -10), (10, 0), (10, 10)
    ]

    area_1x1: list[tuple[int, int]] = [(x, y) for x in range(-10, 20, 10) for y in range(-10, 20, 10)]
    area_2x2: list[tuple[int, int]] = [(x, y) for x in range(-20, 30, 10) for y in range(-20, 30, 10)]
    area_3x3: list[tuple[int, int]] = [(x, y) for x in range(-30, 40, 10) for y in range(-30, 40, 10)]
    area_10x10: list[tuple[int, int]] = [(x, y) for x in range(-100, 110, 10) for y in range(-100, 110, 10)]


    # lists for the cells 
    all_matrices = np.load("map_1234.npz")
    elevation_matrix = all_matrices["elevation_smoothed_matrix"]
    temperature_matrix = all_matrices["temperature_smoothed_matrix"]
    humidity_matrix = all_matrices["humidity_smoothed_matrix"]
    radioactivity_matrix = all_matrices["radioactivity_smoothed_matrix"]
    productivity_matrix = all_matrices["productivity_smoothed_matrix"]

    all_utility_matrix = np.empty((world_size//10, world_size//10), dtype=object)
    all_cells_matrix = np.empty((world_size//10, world_size//10), dtype=object)

