
class Cells():
    # energy storage capacity
    # energy production rate
    # resilience
    # lifespan
    # aging speed
    # reproduction rate
    # offspring count
    # adaptation and evolution rate
    # energy consumption rate

    all_cells_list: list = []

    def __init__(self, position_x: int, position_y: int, energy_capacity: float,
                 energy_production_rate: float, resilience: float, lifespan: float,
                 aging_speed: float, reproduction_rate: float, offspring_count: float,
                 evolution_rate: float, current_energy: float, age: float,
                 temperature_level: float):
        self.position_x = position_x
        self.position_y = position_y
        self.energy_capacity = energy_capacity
        self.energy_production_rate = energy_production_rate
        self.resilience = resilience
        self.lifespan = lifespan
        self.aging_speed = aging_speed
        self.reproduction_rate = reproduction_rate
        self.offspring_count = offspring_count
        self.evolution_rate = evolution_rate
        self.current_energy = current_energy
        self.age = age
        self.temperature_level = temperature_level