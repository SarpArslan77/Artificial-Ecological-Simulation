from general import General
import numpy as np

class Corpse():

    all_corpses_list: list = []

    def __init__(self, position_x:int, position_y:int):
        self.position_x, self.position_y = position_x, position_y

        self.decomposition_rate = round(np.random.uniform(0.002, 0.005), 4)
        self.prolificacy = round(np.random.uniform(0.75, 1.0), 4)
        self.color = General.colors["black"]

        Corpse.all_corpses_list.append(self)
        General.all_utility_matrix[self.position_y//10, self.position_x//10] = self

    def decompose(self) -> None:
        self.prolificacy -= self.decomposition_rate

    def corpse_main_loop(self) -> None:
        if self.prolificacy < 0.2:
            self.color = General.colors["gray"]
        if self.prolificacy > 0:
            self.decompose()
        else:
            General.all_utility_matrix[self.position_y//10, self.position_x//10] = None
            Corpse.all_corpses_list.remove(self)

        

class Food():

    all_foods_list: list = []

    def __init__(self, position_x: int, position_y: int):
        self.position_x, self.position_y = position_x, position_y

        self.decomposition_rate = round(np.random.uniform(0.004, 0.010), 4)
        self.prolificacy = round(np.random.uniform(0.55, 0.9), 4)
        self.color = General.colors["orange"]

        Food.all_foods_list.append(self)
        General.all_utility_matrix[self.position_y//10, self.position_x//10] = self

    def decompose(self) -> None:
        self.prolificacy -= self.decomposition_rate

    def food_main_loop(self) -> None:
        if self.prolificacy < 0.2: 
            self.color = General.colors["brown"]
        if self.prolificacy > 0:
            self.decompose()
        else:
            General.all_utility_matrix[self.position_y//10, self.position_x//10] = None
            Food.all_foods_list.remove(self)



class Pollen():

    all_pollen_list: list = []

    # attributes to be inherited from the producer_cell
    def __init__(self, position_x: int, position_y: int,
                 energy_capacity: float, energy_production_rate: float, resilience: float,
                 lifespan: float, aging_speed: float, reproduction_rate: float, offspring_count: int,
                 evolution_rate: float, pollen_production_rate: float, ideal_pollen_production_temperature: float,
                 dropped_by = None) -> None:
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
        self.pollen_production_rate = pollen_production_rate
        self.ideal_pollen_production_temperature = ideal_pollen_production_temperature
        self.dropped_by = dropped_by

        self.decomposition_rate = round(np.random.uniform(0.008, 0.020), 4)
        self.prolificacy = round(np.random.uniform(0.5, 0.85), 4)
        self.color = General.colors["yellow"]

        Pollen.all_pollen_list.append(self)
        General.all_utility_matrix[self.position_y//10, self.position_x//10] = self

    def decompose(self) -> None:
        self.prolificacy -= self.decomposition_rate

    def pollen_main_loop(self) -> None:
        # if the pollen is picked, it will not decompose
        if self.prolificacy > 0:
            self.decompose()
        else:
            General.all_utility_matrix[self.position_y//10, self.position_x//10] = None
            Pollen.all_pollen_list.remove(self)
            print("pollen died")