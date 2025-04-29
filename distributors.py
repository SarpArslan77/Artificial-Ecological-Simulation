
from general import General
from utility import Corpse, Food, Pollen
from cells import Cells
import numpy as np
import sys

class Distributors(Cells):

    # energy storage capacity
    # energy production rate
    # resilience
    # lifespan
    # aging speed
    # reproduction rate
    # offspring count
    # adaptation and evolution rate
    # energy consumption rate

    # behavioural complexity - migration, territoriality, competition
    #   symbiosis/mutualism or social hierarchy
    # reactions to environmental dynamics

    all_distributor_cells_list: list = []
    all_distributor_cells_matrix = np.empty((General.world_size//10, General.world_size//10), dtype=object)

    def __init__(self, position_x: int, position_y: int, energy_capacity: float,
                 energy_production_rate: float, resilience: float, lifespan: float,
                 aging_speed: float, reproduction_rate: float, offspring_count: float,
                 evolution_rate: float, max_speed: float, polen_detection_range: int,
                 current_energy: float, age: float, temperature_level: float,
                 ):
        
        super().__init__(position_x, position_y, energy_capacity, energy_production_rate,
                    resilience, lifespan, aging_speed, reproduction_rate, offspring_count,
                    evolution_rate, current_energy, age, temperature_level)
        
        self.grid_x: int = int(position_x//10)
        self.grid_y: int = int(position_y//10)

        self.max_speed = max_speed
        # this value gets derived from the speed. since they are reverse
        self.max_pollen_carry_amount = max(1, min(5, round(8*max_speed-3)))
        self.polen_detection_range = polen_detection_range 
        self.current_polen_list: list = []
        self.real_sensed_area = np.empty((General.world_size//10, General.world_size//10), dtype=[('position', 'i,i'), ('cell', object), ('utility', object)])

        self.name: str = f"D-{self.max_pollen_carry_amount}"
        self.distributors_colors: dict = {
            5 : (255, 182, 193),
            4 : (255, 209, 220),
            3 : (255, 105, 180),
            2 : (255, 20, 147),
            1 : (199, 21, 133)
        } 
        self.color: tuple[int, int, int] = self.distributors_colors[self.max_pollen_carry_amount] 
        self.energy_consumption_rate: float = round((0.1*self.energy_capacity+ \
                                        self.max_speed**(1/1.5) * 0.2 + \
                                        self.max_pollen_carry_amount*0.15 + \
                                        abs(self.temperature_level-1.0)*0.8 + \
                                        self.polen_detection_range**(1/1.5) * 0.1) * \
                                        (1-self.resilience*0.02), 4)
        # normalize this value
        self.energy_consumption_rate = round((self.energy_consumption_rate - 2) / 6.5, 4)
        self.psychological_stress = round(((1-self.current_energy/self.energy_capacity)**(1/2) + \
                                    self.reproduction_rate*self.offspring_count/5 + \
                                    (self.age/self.lifespan)**(1/3) + \
                                    self.max_pollen_carry_amount*0.12) * \
                                    (1+self.evolution_rate*0.15) * \
                                    (1-self.resilience*0.3), 4)
        self.psychological_stress = round((self.psychological_stress-0.5)/1.1, 4)

        

    def __repr__(self):
        return self.name
    
    @classmethod
    def generate_starting_distributor_cells(cls, distributor_cell_count: int) -> None:
        """
        1) position_x, position_y [0, 2500]
        2) energy_capacity [0.25, 0.5]
        3) energy_production_rate [0.005, 0.0025]
        4) resilience [0.001, 1.0]
        5) lifespan [0.125, 0.25]
        6) aging_speed [0.0025, 0.00625]
        7) reproduction_rate [0.004, 0.008]
        8) offspring_count [2, 16]
        9) evolution_rate [0.001, 1.0]

        10) max_speed [0.5, 1.0]
        11) max_pollen_carry_amount [1, 5]
        12) polen_detection_range [50, 500]
        13) energy_consumption_rate [0.0, 1.0]
        14) psychological_stress [0.0, 1.0]

        15) current_energy = energy_capacity / 2
        16) age 0.0
        18) temperature_level
        """

        linear_indices = np.random.choice(General.total_grid_cells, size=distributor_cell_count, replace=False)
        x_indices, y_indices = np.unravel_index(linear_indices, (General.world_size//10, General.world_size//10))
        for i in range(distributor_cell_count):
            x_idx, y_idx = x_indices[i], y_indices[i]
            pos_x, pos_y = x_idx*10, y_idx*10
            energy_capacity = round(np.random.uniform(0.25, 0.5), 4)
            energy_production_rate = round(np.random.uniform(0.005, 0.0025), 4)
            resilience = round(np.random.uniform(0.001, 1.0), 4)
            lifespan = round(np.random.uniform(0.125, 0.25), 4)
            aging_speed = round(np.random.uniform(0.0025, 0.00625), 4)
            reproduction_rate = round(np.random.uniform(0.004, 0.008) ,4)
            offspring_count = np.random.randint(2, 16)
            evolution_rate = round(np.random.uniform(0.001, 1.0), 4)
            max_speed = round(np.random.uniform(0.5, 1.0), 4)
            pollen_detection_range = np.random.randint(50, 500)
            new_distributor_cell = Distributors(
                pos_x, pos_y,
                energy_capacity,
                energy_production_rate,
                resilience,
                lifespan,
                aging_speed,
                reproduction_rate, 
                offspring_count,
                evolution_rate,
                max_speed,
                pollen_detection_range,
                energy_capacity/2,
                0.0,
                General.temperature_matrix[y_idx, x_idx]
            )
            General.all_cells_matrix[y_idx, x_idx] = new_distributor_cell
            Distributors.all_distributor_cells_list.append(new_distributor_cell)
            Cells.all_cells_list.append(new_distributor_cell)

    def die(self) -> None:
        Distributors.all_distributor_cells_list.remove(self)
        Cells.all_cells_list.remove(self)
        General.all_cells_matrix[int(self.position_y//10), int(self.position_x//10)] = None
        General.all_utility_matrix[int(self.position_y//10), int(self.position_x//10)] = Corpse(self.position_x, self.position_y)

    def produce_energy(self) -> None:
        self.current_energy += self.energy_production_rate
    
    def pick_pollen(self, pollen: Pollen) -> None:
        pollen.dropped_by = None
        self.current_polen_list.append(pollen)
        General.all_utility_matrix[int(pollen.position_y//10), int(pollen.position_x//10)] = None
        Pollen.all_pollen_list.remove(pollen)

    def drop_pollen(self, pollen: Pollen, position_x = 0, position_y = 0) -> None:
        # when the pollen is dropped, its position gets updated
        if not(position_x or position_y): # if the position is not given, then it will be the current position of the distributor cell
            pollen.position_x, pollen.position_y = self.position_x, self.position_y
        else: # if the position is given, then it will be the given position for the producer cells
            pollen.position_x, pollen.position_y = position_x, position_y
        pollen.dropped_by = self
        self.current_polen_list.remove(pollen)
        General.all_utility_matrix[int(self.position_y//10), int(self.position_x//10)] = pollen
        Pollen.all_pollen_list.append(pollen)

    def move(self) -> None:
        candidate_sense_are = General.area_1x1[:]
        np.random.shuffle(candidate_sense_are)
        while True:
            if candidate_sense_are:
                move_x, move_y = candidate_sense_are.pop()
            else: # if not any possible move direction, that dont move
                return
            if (0 <= self.position_x + move_x < General.world_size) and (0 <= self.position_y+move_y < General.world_size) \
                and (General.all_cells_matrix[int((self.position_y+move_y)//10), int((self.position_x+move_x)//10)] is None):
                break
        General.all_cells_matrix[self.position_y//10, self.position_x//10] = None
        self.position_x += move_x
        self.position_y += move_y
        General.all_cells_matrix[self.position_y//10, self.position_x//10] = self

    def get_sensed_area(self) -> None:
        for dx, dy in General.area_10x10:
            if (0 <= self.position_x+dx < General.world_size) and (0 <= self.position_y+dy < General.world_size):
                corresponding_matrix_x, corresponding_matrix_y = int((self.position_x+dx)//10), int((self.position_y+dy)//10)
                possible_cell = General.all_cells_matrix[corresponding_matrix_y, corresponding_matrix_x]
                possible_utility = General.all_utility_matrix[corresponding_matrix_y, corresponding_matrix_x]
                if possible_cell:
                    if isinstance(possible_cell, (Distributors)) and (possible_cell is not self) or \
                        hasattr(possible_cell, "productivity_level"):
                        self.real_sensed_area[(corresponding_matrix_y, corresponding_matrix_x)]["cell"] = possible_cell
                if possible_utility:
                    if isinstance(possible_utility, (Food, Corpse, Pollen)):
                        self.real_sensed_area[(corresponding_matrix_y, corresponding_matrix_x)]["utility"] = possible_utility
                # if there is not cell or utility in the sensed area, then set it to None
                if not(possible_cell): self.real_sensed_area[(corresponding_matrix_y, corresponding_matrix_x)]["cell"] = None
                if not(possible_utility): self.real_sensed_area[(corresponding_matrix_y, corresponding_matrix_x)]["utility"] = None

    def main_loop_distributor_cells(self) -> None:
        # restart the sensed area for other cells and utilities 
        self.get_sensed_area()
        
        if (self.age > self.lifespan + np.random.uniform(0, 0.25) * (1+self.resilience)):
            self.die()
            return
        else:
            self.age += self.aging_speed
            self.current_energy = round(self.current_energy-self.energy_consumption_rate, 4)

        # movement logic
        if np.random.random() < self.max_speed:
            self.move()

        # find the locations of the utilities in the sensed area
        utility_types = np.array(
            [type(entry['utility']) if entry['utility'] is not None else None
            for entry in self.real_sensed_area.flatten()], dtype=object).reshape(General.world_size//10, General.world_size//10)
        sensed_pollen_locations_matrix = np.argwhere(utility_types == Pollen)
        #print(f"pollen locations: {sensed_pollen_locations_matrix}")
        sensed_food_locations = np.argwhere(utility_types == Food)
        sensed_corpse_locations = np.argwhere(utility_types == Corpse)
        # find the locations of the cells in the sensed area
        cell_types = np.array(
            [type(entry['cell']) if entry['cell'] is not None else None
            for entry in self.real_sensed_area.flatten()], 
            dtype=object
            ).reshape(General.world_size//10, General.world_size//10)
        is_producer = np.array(
            [hasattr(cell["cell"], 'main_loop_producer_cells') 
            for cell in self.real_sensed_area.flatten()],
            dtype=bool
        ).reshape(General.world_size//10, General.world_size//10)
        sensed_producer_cell_locations = np.argwhere(is_producer)  # Returns [[y1, x1], [y2, x2], ...]
        sensed_distributor_cell_locations = np.argwhere(cell_types == Distributors) 

        # polen logic
        # pick up pollen
        if (sensed_pollen_locations_matrix.any()) and (len(self.current_polen_list) < self.max_pollen_carry_amount):
            corresponding_matrix_x, corresponding_matrix_y = int(self.position_x//10), int(self.position_y//10)
            
            for (sensed_y, sensed_x) in sensed_pollen_locations_matrix:
                
                distance_to_pollen_matrix = abs(corresponding_matrix_x - sensed_x) + abs(corresponding_matrix_y - sensed_y)
                pollen_to_be_potentially_picked_up: Pollen = General.all_utility_matrix[sensed_y, sensed_x]
                # the pollen should be close enough and not already dropped by the same distributor cell
                if(distance_to_pollen_matrix <= 2) and (pollen_to_be_potentially_picked_up.dropped_by != self):
                    # Ensure this is actually a Pollen object
                    self.pick_pollen(pollen_to_be_potentially_picked_up)
                    print("pollen picked up")

        # drop pollen if near a producer cell
        if (sensed_producer_cell_locations.any()) and (self.current_polen_list):
            corresponding_matrix_x, corresponding_matrix_y = int(self.position_x//10), int(self.position_y//10)
            for (sensed_y, sensed_x) in sensed_producer_cell_locations:
                sensed_producer_cell = General.all_cells_matrix[sensed_y, sensed_x]
                #print(f"{General.all_cells_matrix[sensed_y, sensed_x]} at : {sensed_x}, {sensed_y} ")
                distance_to_producer_matrix = abs(corresponding_matrix_x - sensed_x) + abs(corresponding_matrix_y - sensed_y)
                if distance_to_producer_matrix <= 2:
                    pollen_to_be_dropped = np.random.choice(self.current_polen_list)
                    self.drop_pollen(pollen_to_be_dropped, sensed_producer_cell.position_x, sensed_producer_cell.position_y)
                    print(f"pollen dropped at {sensed_producer_cell.position_x}, {sensed_producer_cell.position_y}")
        # chance to drop a pollen in the environment randomly
        if (self.current_polen_list) and (np.random.random() < round(self.max_speed/10, 4)):
            pollen_to_be_dropped = np.random.choice(self.current_polen_list)
            self.drop_pollen(pollen_to_be_dropped)
            print(f"pollen dropped in the environment randomly at {self.position_x}, {self.position_y}")









        #print(self.sensed_area_for_other_cells)
        #print(self.sensed_area_for_utilities)
        






if __name__ == "__main__":
    Distributors.generate_starting_distributor_cells(25000)
    for cell in Distributors.all_distributor_cells_list:
        cell: Distributors
    print(f"max value is: {max(Distributors.all_distributor_cells_list, key=lambda x: x.psychological_stress).psychological_stress}")
    print(f"min value is: {min(Distributors.all_distributor_cells_list, key=lambda x: x.psychological_stress).psychological_stress}")





