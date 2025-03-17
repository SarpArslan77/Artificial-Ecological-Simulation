import math
import random

def apply_seasonal_effect(
    base_temp: float,  # Cell's baseline temperature (-1 to 1)
    elevation_effect: float,  # 0-1 (height-driven volatility)
    day_of_year: int,
    phase_shift: int = 0,
    randomness: float = 0.1
) -> float:
    """
    Transforms a cell's temperature using elevation-modulated seasonality.
    Preserves system boundaries (-1 to 1) while combining multiple effects.
    """
    # Seasonal component (elevation controls swing intensity)
    radians = (2 * math.pi / 365) * (day_of_year - phase_shift)
    seasonal_swing = math.sin(radians) * elevation_effect
    
    # Combine effects with noise
    modified_temp = base_temp + seasonal_swing
    #modified_temp += random.uniform(-randomness, randomness)
    
    # Enforce system constraints
    return max(-1.0, min(1.0, modified_temp))

elevation = [[1, 0.9, 0.8], [0.7, 0.6, 0.5], [0.4, 0.3, 0]]
a = [[-0.9, -0.6, -0.3], [0, 0.3, 0.6], [0.7, 0.8, 0.9]]
print(a)
print()
for y in range(len(a)):
    for x in range(len(a)):
        a[y][x] = apply_seasonal_effect(a[y][x], 0.5, 1)

print(a)