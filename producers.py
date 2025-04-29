
from general import General
from utility import Corpse, Food, Pollen
from cells import Cells
import numpy as np
import sys

class Producers(Cells):

    # energy storage capacity
    # energy production rate
    # resilience
    # lifespan
    # aging speed
    # reproduction rate
    # offspring count
    # adaptation and evolution rate
    # energy consumption rate

    # behavioural complexity - migration, territoriality, 
    #       competition, symbiosis/mutualism or social hierarchy
    # reactions to  environmental dynamics - seasonal behaviour

    # class variables to be accesed by all the instances of Producers class
    all_producer_cells_list: list = []

    def __init__(self, position_x: int, position_y, energy_capacity: float, energy_production_rate: float, resilience: float, lifespan: float, 
                 aging_speed: float, reproduction_rate: float, offspring_count: float, evolution_rate: float, current_energy: float, age: float,
                 pollen_production_rate: float, ideal_pollen_production_temperature: float,
                 temperature_level: int, elevation_level: int, humidity_level: int, radioactivity_level: int, productivity_level: int):
        ### DEBUGGING
        """start_time = time.perf_counter()"""
        # inputted parameters + starting parameters are inheritted
        super().__init__(position_x, position_y, energy_capacity, energy_production_rate,
                         resilience, lifespan, aging_speed, reproduction_rate, offspring_count,
                         evolution_rate, current_energy, age, temperature_level)
        self.pollen_production_rate = pollen_production_rate
        self.ideal_pollen_production_temperature = ideal_pollen_production_temperature
        # map based parameters
        self.elevation_level = elevation_level
        self.temperature_level = temperature_level
        self.humidity_level = humidity_level
        self.radioactivity_level = radioactivity_level
        self.productivity_level = productivity_level
        self.name = f"PD-{elevation_level}{temperature_level}{humidity_level}"
        # derivated parameters from inputted parameters
        self.color: tuple[int, int, int] = (int(elevation_level*255), abs(int(temperature_level*255)), int(humidity_level*255))
        self.energy_consumption_rate = round((self.aging_speed*(1+(1-self.resilience))*
                                        (1+0.15*self.elevation_level)*
                                        (1+0.25*abs(self.temperature_level-2)**1.5)*
                                        (1+0.2*abs(self.humidity_level-2)**1.5)), 4)
        #self.energy_consumption_rate = round(1/(1+np.exp(-self.energy_consumption_rate))/100, 4) # normalized with sigmoid function
        self.psychological_stress = round((1/(1+np.exp(-((self.energy_capacity-self.current_energy)-0.5))) + 
                                     (self.age/self.lifespan)**2 + 
                                     0.3*self.resilience + 
                                     0.1*self.elevation_level/4 + 
                                     0.2*(abs(self.temperature_level-2)/4) + 
                                     0.15*(abs(self.humidity_level-2)/4)), 4)
        #self.psychological_stress = round(1/(np.exp(-self.psychological_stress)), 4) # normalized
        # if panic_mode > 3 then it can no longer increase its metabolism in the area [-3, 3]
        self.panic_mode: int = 0


        ### DEBUGGING
        """end_time = time.perf_counter()
        print(f"__init__ took {end_time - start_time:.6f} seconds")"""


    def __repr__(self):
        return self.name
    
    @classmethod
    def generate_starting_producer_cells(cls, producer_cell_count: int) -> None:
        """
        1) position_x, position_y [0, 2500]
        2) energy_capacity [0.5, 1.0]
        3) energy_production_rate [0.02, 0.1]
        4) resilience [0.001, 1.0]
        5) lifespan [0.5, 1.0]
        6) aging_speed [0.002, 0.005]
        7) reproduction_rate [0.001, 0.02]
        8) offspring_count [1, 4]
        9) evolution_rate [0.001, 1.0]
        10) pollen_production_rate [0, 1.0]
        11) current_energy = energy_capacity met
        12) age 0.0
        13) elevation_level, temperature_level, humidity_level, radioactivity_level, productivity_level [0, 4]
        """
        ### DEBUGGING
        """start_time = time.perf_counter()"""

        grid_size: int = General.world_size//10
        if producer_cell_count > General.total_grid_cells:
            raise ValueError("producer_cell_count exceeds available cells")
            
        linear_indices = np.random.choice(General.total_grid_cells, size=producer_cell_count, replace=False)
        x_indices, y_indices = np.unravel_index(linear_indices, (grid_size, grid_size))
        for i in range(producer_cell_count):
            x_idx, y_idx = x_indices[i], y_indices[i]
            pos_x, pos_y = x_idx * 10, y_idx * 10
            ### DEBUGGING
            energy_capacity = round(np.random.uniform(0.5, 1.0), 4)
            energy_production_rate = round(np.random.uniform(0.02, 0.1), 4)
            resilience = round(np.random.uniform(0.001, 1.0), 4)
            lifespan = round(np.random.uniform(0.5, 1.0), 4)
            aging_speed = round(np.random.uniform(0.002, 0.005), 4)
            reproduction_rate = round(np.random.uniform(0.001, 0.02), 4)
            offspring_count = np.random.randint(1, 4)
            evolution_rate = round(np.random.uniform(0.001, 1.0), 4)
            pollen_production_rate = round(np.random.uniform(0.001, 1.0), 4)
            ideal_pollen_production_temperature = round(np.random.uniform(-1.0, 1.0), 4)
            new_producer_cell = Producers(
                pos_x, pos_y,
                energy_capacity,
                energy_production_rate,
                resilience,
                lifespan,
                aging_speed,
                reproduction_rate,
                offspring_count,
                evolution_rate,
                energy_capacity/2, # current enery is equal to half of energy_capacity
                0.0,
                pollen_production_rate,
                ideal_pollen_production_temperature,
                General.temperature_matrix[y_idx, x_idx],
                General.elevation_matrix[y_idx, x_idx],
                General.humidity_matrix[y_idx, x_idx],
                General.radioactivity_matrix[y_idx, x_idx],
                General.productivity_matrix[y_idx, x_idx],
            )
            # add the producers to the matrixes / lists
            General.all_cells_matrix[y_idx, x_idx] = new_producer_cell
            Producers.all_producer_cells_list.append(new_producer_cell)
            Cells.all_cells_list.append(new_producer_cell)


        ### DEBUGGING
        """end_time = time.perf_counter()
        print(f"generate_starting_producer_cells took {end_time - start_time:.6f} seconds")"""

    def die(self) -> None:
        Producers.all_producer_cells_list.remove(self)
        Cells.all_cells_list.remove(self)
        General.all_cells_matrix[int(self.position_y//10), int(self.position_x//10)] = None
        General.all_utility_matrix[int(self.position_y//10), int(self.position_x//10)] = Corpse(self.position_x, self.position_y)

    def produce_energy_and_food(self) -> None:
        possible_food_positions = General.area_3x3[:]
        np.random.shuffle(possible_food_positions)
        for dx, dy in possible_food_positions:
            if (0 <= self.position_x+dx < General.world_size) and (0 <= self.position_y+dy < General.world_size):
                # check if the cell is empty
                if not(General.all_utility_matrix[(self.position_y+dy)//10, (self.position_x+dx)//10]):
                    # create food
                    General.all_utility_matrix[(self.position_y+dy)//10, (self.position_x+dx)//10] = Food(self.position_x+dx, self.position_y+dy)
                    self.current_energy = round(min(self.energy_capacity, self.energy_production_rate + self.current_energy), 4)
                    break

    def produce_pollen(self) -> None:
        # Initialize parameters with current traits to pass to Pollen
        params = {
            'energy_capacity': self.energy_capacity,
            'energy_production_rate': self.energy_production_rate,
            'resilience': self.resilience,
            'lifespan': self.lifespan,
            'aging_speed': self.aging_speed,
            'reproduction_rate': self.reproduction_rate,
            'offspring_count': self.offspring_count,
            'pollen_production_rate': self.pollen_production_rate,
            'ideal_pollen_production_temperature': self.ideal_pollen_production_temperature,
            'evolution_rate': self.evolution_rate,
        }
        # Define mutation parameters for each trait
        traits = [
            {
                'name': 'energy_capacity',
                'min': 0.5,
                'max': 1.0,
                'delta_std': 0.05,  # Biologically plausible mutation step (normal distribution)
                'round': 4,
            },
            {
                'name': 'energy_production_rate',
                'min': 0.02,
                'max': 0.1,
                'delta_std': 0.005,
                'round': 4,
            },
            {
                'name': 'resilience',
                'min': 0.001,
                'max': 1.0,
                'delta_std': 0.05,
                'round': 4,
            },
            {
                'name': 'lifespan',
                'min': 0.5,
                'max': 1.0,
                'delta_std': 0.05,
                'round': 4,
            },
            {
                'name': 'aging_speed',
                'min': 0.002,
                'max': 0.005,
                'delta_std': 0.0002,
                'round': 4,
            },
            {
                'name': 'reproduction_rate',
                'min': 0.001,
                'max': 0.02,
                'delta_std': 0.002,
                'round': 4,
            },
            {
                'name': 'offspring_count',
                'min': 1,
                'max': 4,
                'delta_std': 0.5,  # Simulate discrete changes
                'round': 0,
            },
            {
                'name': 'pollen_production_rate',
                'min': 0.001,
                'max': 1.0,
                'delta_std': 0.05,
                'round': 4,
            },
            {
                'name': 'ideal_pollen_production_temperature',
                'min': -1.0,
                'max': 1.0,
                'delta_std': 0.1,
                'round': 4,
            },
            {
                'name': 'evolution_rate',
                'min': 0.001,
                'max': 1.0,
                'delta_std': 0.05,
                'round': 4,
            },
        ]
        # Vectorized mutation checks and computations
        num_traits = len(traits)
        mutation_probs = self.evolution_rate / 10  # Same as original 
        # Generate all mutation flags in one call
        mutation_mask = np.random.rand(num_traits) < mutation_probs  
        if np.any(mutation_mask):
            # Generate normally distributed deltas (smaller changes more likely)
            deltas = np.random.normal(loc=0, scale=[t['delta_std'] for t in traits], size=num_traits)
            deltas *= self.evolution_rate  # Scale by evolution rate
            # Apply mutations only where mask is True
            for i, trait in enumerate(traits):
                if mutation_mask[i]:
                    new_val = params[trait['name']] + deltas[i]
                    new_val = np.clip(new_val, trait['min'], trait['max'])
                    if trait['round'] is not None:
                        new_val = round(new_val, trait['round'])
                    params[trait['name']] = new_val
        # Find pollen position (original logic optimized)
        pollen_position_candidates = []
        for dx, dy in General.area_2x2:
            if 0 <= self.position_x+dx < General.world_size and 0 <= self.position_y+dy < General.world_size:
                pollen_position_candidates.append((self.position_x + dx, self.position_y + dy))
        available_pollen_positions = [(x, y) for x, y in pollen_position_candidates if not General.all_utility_matrix[y // 10, x // 10]]  
        if available_pollen_positions:
            x, y = available_pollen_positions[np.random.choice(len(available_pollen_positions))]
            General.all_utility_matrix[y // 10, x // 10] = Pollen(
                x, y, 
                params['energy_capacity'],
                params['energy_production_rate'],
                params['resilience'],
                params['lifespan'],
                params['aging_speed'],
                params['reproduction_rate'],
                params['offspring_count'],
                params['evolution_rate'],
                params['pollen_production_rate'],
                params['ideal_pollen_production_temperature']
            )

    def reproduce(self, to_be_used_pollen: Pollen) -> None:
        # create a new producer cell with the same parameters as the pollen with mutation effects
        for _ in range(self.offspring_count):
            # Find available positions for offspring
            offspring_position_candidates = [(self.position_x + dx, self.position_y + dy) for dx, dy in General.area_3x3]
            available_offspring_positions = [(x, y) for x, y in offspring_position_candidates if ((0 <= x < General.world_size) and (0 <= y < General.world_size)) and 
                                                                                                    (not General.all_utility_matrix[y // 10, x // 10])]
            if available_offspring_positions:
                x, y = available_offspring_positions[np.random.randint(0, len(available_offspring_positions))]
                new_producer_cell_energy_capacity = round(((self.energy_capacity + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10))+to_be_used_pollen.energy_capacity)/2, 4)
                new_producer_cell_energy_production_rate = round((self.energy_production_rate + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.energy_production_rate)/2, 4)
                new_producer_cell_resilience = round((self.resilience + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.resilience)/2, 4)
                new_producer_cell_lifespan = round((self.lifespan + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.lifespan)/2, 4)
                new_producer_cell_aging_speed = round((self.aging_speed + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.aging_speed)/2, 4)
                new_producer_cell_reproduction_rate = round((self.reproduction_rate + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.reproduction_rate)/2, 4)
                new_producer_cell_offspring_count = round((self.offspring_count + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.offspring_count)/2)
                new_producer_cell_pollen_production_rate = round((self.pollen_production_rate + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.pollen_production_rate)/2, 4)
                new_producer_cell_ideal_pollen_production_temperature = min(1.0, max(-1.0, round((self.ideal_pollen_production_temperature + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.ideal_pollen_production_temperature)/2, 4)))
                new_producer_cell_evolution_rate = round((self.evolution_rate + np.random.choice([-1, 1])*(self.evolution_rate/10+self.radioactivity_level/10)+to_be_used_pollen.evolution_rate)/2, 4)
                # Create a new producer cell with the same parameters as the pollen with mutation effects
                new_producer_cell = Producers(
                    x, y,
                    new_producer_cell_energy_capacity,
                    new_producer_cell_energy_production_rate,
                    new_producer_cell_resilience,
                    new_producer_cell_lifespan,
                    new_producer_cell_aging_speed,
                    new_producer_cell_reproduction_rate,
                    new_producer_cell_offspring_count,
                    new_producer_cell_evolution_rate,
                    self.energy_capacity / 2,  # current energy is equal to half of energy_capacity
                    0.0,
                    new_producer_cell_pollen_production_rate,
                    new_producer_cell_ideal_pollen_production_temperature,
                    General.temperature_matrix[int(y // 10), int(x // 10)],
                    General.elevation_matrix[int(y // 10), int(x // 10)],
                    General.humidity_matrix[int(y // 10), int(x // 10)],
                    General.radioactivity_matrix[int(y // 10), int(x // 10)],
                    General.productivity_matrix[int(y // 10), int(x // 10)]
                )
                # Add the new producer cell to the matrixes / lists
                General.all_cells_matrix[int(y // 10), int(x // 10)] = new_producer_cell
                Producers.all_producer_cells_list.append(new_producer_cell)
                Cells.all_cells_list.append(new_producer_cell)
                print(f"new producer cell created at {x//10}, {y//10}")

    def main_loop_producer_cells(self) -> None:
        # if age > lifespan high chance, elif age < lifespan low chance, else get old
        if (self.age > self.lifespan + np.random.uniform(0, 0.25)*(1+self.resilience)):
            self.die()
            return
        else:
            self.age += self.aging_speed
            self.current_energy = round(self.current_energy - self.energy_consumption_rate, 4)
        
        # increase metabolism if energy production rate is not enough with its negative consequences
        if (self.energy_production_rate < self.energy_consumption_rate) or (self.current_energy < 0.4) and (self.panic_mode < 3):
            adjustment = abs(self.energy_production_rate-self.energy_consumption_rate)
            # Increase energy production to match consumption
            self.energy_production_rate = round(min(0.1, self.energy_production_rate + adjustment), 4)
            # Negative consequences of increased metabolism
            self.resilience = round(max(0.001, self.resilience - adjustment), 4)
            self.lifespan = round(max(0.5, self.lifespan - adjustment), 4)
            self.aging_speed = round(min(0.005, self.aging_speed + adjustment/200), 4)
            self.reproduction_rate = round(max(0.001, self.reproduction_rate - adjustment/200), 4)
            self.offspring_count = max(1, self.offspring_count - 1)
            self.evolution_rate = round(max(0.001, self.evolution_rate - adjustment), 4)
            self.psychological_stress = round(min(1.0, self.psychological_stress + adjustment), 4)
            # change the panic mode
            self.panic_mode += 1
            self.produce_energy_and_food()
        # decrease the metabolism with its positive consequences
        elif (self.energy_production_rate > self.energy_consumption_rate) and (self.current_energy > 0.9) and (self.panic_mode > -3):
            adjustment = (self.energy_production_rate-self.energy_consumption_rate) / 4  # Smaller adjustments for optimization
            # Decrease energy production to conserve resources
            self.energy_production_rate = round(max(0.02, self.energy_production_rate - adjustment), 4)
            # Positive consequences of decreased metabolism
            self.resilience = round(min(1.0, self.resilience + adjustment), 4)
            self.lifespan = round(min(1.0, self.lifespan + adjustment), 4)
            self.aging_speed = round(max(0.002, self.aging_speed - adjustment/200), 4)
            self.reproduction_rate = round(min(0.02, self.reproduction_rate + adjustment/200), 4)
            self.offspring_count = min(4, self.offspring_count + 1)
            self.evolution_rate = round(min(1.0, self.evolution_rate + adjustment), 4)
            self.psychological_stress = round(max(0.0, self.psychological_stress - adjustment), 4)
            self.panic_mode -= 1
        # if the energy is too low, go bankrupt and produce energy forcefully
        elif (self.current_energy < 0.1) and (self.panic_mode < 3):
            adjustment = abs(self.energy_production_rate-self.energy_consumption_rate)*3
            # Increase energy production to match consumption
            self.energy_production_rate = round(min(0.1, self.energy_production_rate + adjustment), 4)
            # Negative consequences of increased metabolism
            self.resilience = round(max(0.001, self.resilience - adjustment), 4)
            self.lifespan = round(max(0.5, self.lifespan - adjustment), 4)
            self.aging_speed = round(min(0.005, self.aging_speed + adjustment/200), 4)
            self.reproduction_rate = round(max(0.001, self.reproduction_rate - adjustment/200), 4)
            self.offspring_count = max(1, self.offspring_count - 1)
            self.evolution_rate = round(max(0.001, self.evolution_rate - adjustment), 4)
            self.psychological_stress = round(min(1.0, self.psychological_stress + adjustment), 4)
            # produce the food after the adjustmens, so that the changes to the production rate are immediately applicable
            # it can drastically increase its metabolism only one time
            self.panic_mode += 3
            self.produce_energy_and_food()

        # produce food if by chance and energy capacity not met
        if (np.random.random() < self.productivity_level/7) and (self.energy_capacity-self.current_energy):
            self.produce_energy_and_food()
        # produce pollen if by chance and the temperature (with the effect of evolution rate) is suitable
        if (np.random.random() < self.pollen_production_rate/7): #and (max(-1.0, self.ideal_pollen_production_temperature-self.evolution_rate) < self.temperature_level < min(1.0, self.ideal_pollen_production_temperature+self.evolution_rate)):
            self.produce_pollen()

        # if the pollen is on the producer_cell, there is a chance to reproduction
        if isinstance(General.all_utility_matrix[int(self.position_y//10), int(self.position_x//10)], Pollen):
            to_be_used_pollen: Pollen = General.all_utility_matrix[int(self.position_y//10), int(self.position_x//10)]
            Pollen.all_pollen_list.remove(to_be_used_pollen)
            General.all_utility_matrix[int(to_be_used_pollen.position_y//10), int(to_be_used_pollen.position_x//10)] = None
            # if by chance can reproduce
            if np.random.random() < self.reproduction_rate:
                self.reproduce(to_be_used_pollen)
            print(f"Reproduced at {self.position_x}, {self.position_y}")

# TEST TEST TEST
if __name__ == "__main__":
    # our geana pig
    Producers.generate_starting_producer_cells(250)
    for cell in Producers.all_producer_cells_list:
        cell: Producers
        
    sys.exit()

    

    


